How to Avoid Copying Arrays with waveformRecord
===============================================

This page describes how to use the array field memory management feature that was introduced in EPICS 3.15.1.
This allows array data to be moved into and out of the value (aka BPTR) field of the waveform, aai, and aao types.

Making use of this feature involves replacing the pointer stored in the BPTR field with another (user allocated) pointer.
The basic rules are:

#. BPTR, and the memory it is currently pointing to, can only be accessed while the record is locked.
#. NELM may not be changed.
#. BPTR must always point to a piece of memory large enough to accommodate the maximum number of elements (as given by the NELM field).

Rule #1 means that it is only safe to read, write, or de-reference the BPTR field from a device support function, or after manually calling dbScanLock().
Rule #3 means that BPTR can never be set to NULL, and when replacing BPTR, the replacement must be allocated large enough for the worst case.
An external client may put an array of up to NELM elements to the field at almost any time.

Example
#######

::

    /* Demonstration of using custom allocation for waveformRecord buffers.
     *
     * Requires EPICS Base 3.15.1 or newer
     *
     * This example makes inefficient use of malloc() and
     * free().  This is done to make clear where new memory appears.
     * In reality a free list should be used.
     *
     * Also be aware that this example will use 100% of the time of one CPU core.
     * However, this will be spread across available cores.
     *
     * To use this example include the following in a DBD file:
     *
     * device(waveform,CONSTANT,devWfZeroCopy,"Zero Copy Demo")
     *
     * Also include a record instance
     *
     * record(waveform, "$(NAME)") {
     *  field(DTYP, "Zero Copy Demo")
     *  field(FTVL, "SHORT")
     *  field(NELM, "100")
     *  field(SCAN, "I/O Intr")
     * }
     */
    
    #include <errlog.h>
    #include <initHooks.h>
    #include <ellLib.h>
    #include <devSup.h>
    #include <dbDefs.h>
    #include <dbAccess.h>
    #include <cantProceed.h>
    #include <epicsTypes.h>
    #include <epicsMutex.h>
    #include <epicsEvent.h>
    #include <epicsThread.h>
    #include <menuFtype.h>
    #include <dbScan.h>
    
    #include <waveformRecord.h>
    
    static ELLLIST allPvt = ELLLIST_INIT;
    
    struct devicePvt {
        ELLNODE node;
    
        /* synchronize access to this structure */
        epicsMutexId lock;
        /* wakeup the worker when another update is needed */
        epicsEventId wakeup;
        /* notify the scanner thread when another update is available */
        IOSCANPVT scan;
    
        /* the next update */
        void *nextBuffer;
        epicsUInt32 maxbytes, numbytes;
    };
    
    static void startWorkers(initHookState);
    
    static long init(int phase)
    {
        if(phase!=0)
            return 0;
        initHookRegister(&startWorkers);
        return 0;
    }
    
    static long init_record(waveformRecord *prec)
    {
        struct devicePvt *priv;
        if(prec->ftvl!=menuFtypeSHORT) {
            errlogPrintf("%s.FTVL must be set to SHORT for this example\n", prec->name);
            return 0;
        }
    
        /* cleanup array allocated by record support.
            * Not necessary since we use calloc()/free(),
            * but needed when allocating in other ways.
            */
        free(prec->bptr);
        prec->bptr = callocMustSucceed(prec->nelm, dbValueSize(prec->ftvl), "first buf");
    
        priv = callocMustSucceed(1, sizeof(*priv), "init_record devWfZeroCopy");
        priv->lock = epicsMutexMustCreate();
        priv->wakeup = epicsEventMustCreate(epicsEventFull);
        scanIoInit(&priv->scan);
        priv->maxbytes = prec->nelm*dbValueSize(prec->ftvl);
    
        ellAdd(&allPvt, &priv->node);
    
        prec->dpvt = priv;
        return 0;
    }
    
    static void worker(void*);
    
    static void startWorkers(initHookState state)
    {
        ELLNODE *cur;
        /* Don't start worker threads until
            * it is safe to call scanIoRequest()
            */
        if(state!=initHookAfterInterruptAccept)
            return;
        for(cur=ellFirst(&allPvt); cur; cur=ellNext(cur))
        {
            struct devicePvt *priv = CONTAINER(cur, struct devicePvt, node);
            epicsThreadMustCreate("wfworker",
                                    epicsThreadPriorityHigh,
                                    epicsThreadGetStackSize(epicsThreadStackSmall),
                                    &worker, priv);
        }
    }
    
    static void worker(void* raw)
    {
        struct devicePvt *priv=raw;
        void *buf = NULL;
        epicsUInt32 nbytes = priv->maxbytes;
    
        while(1) {
    
            if(!buf) {
                /* allocate and initialize a new buffer for later (local) use */
                size_t i;
                epicsInt16 *ibuf;
                buf = callocMustSucceed(1, nbytes, "buffer");
                ibuf = (epicsInt16*)buf;
                for(i=0; i<nbytes/2; i++)
                {
                    ibuf[i] = rand();
                }
            }
    
            /* wait for Event signal when record is scanning 'I/O Intr',
                * and timeout when record is scanning periodic
                */
            if(epicsEventWaitWithTimeout(priv->wakeup, 1.0)==epicsEventError) {
                cantProceed("worker encountered an error waiting for wakeup\n");
            }
    
            epicsMutexMustLock(priv->lock);
    
            if(!priv->nextBuffer) {
                /* make the local buffer available to the read_wf function */
                priv->nextBuffer = buf;
                buf = NULL;
                priv->numbytes = priv->maxbytes;
                scanIoRequest(priv->scan);
            }
    
            epicsMutexUnlock(priv->lock);
        }
    }
    
    static long get_iointr_info(int dir, dbCommon *prec, IOSCANPVT *scan)
    {
        struct devicePvt *priv=prec->dpvt;
        if(!priv)
            return 0;
        *scan = priv->scan;
        /* wakeup the worker when this thread is placed in the I/O scan list */
        if(dir==0)
            epicsEventSignal(priv->wakeup);
        return 0;
    }
    
    static long read_wf(waveformRecord *prec)
    {
        struct devicePvt *priv=prec->dpvt;
        if(!priv)
            return 0;
    
        epicsMutexMustLock(priv->lock);
    
        if(priv->nextBuffer) {
            /* an update is available, so claim it. */
    
            if(prec->bptr)
                free(prec->bptr);
    
            prec->bptr = priv->nextBuffer; /* no memcpy! */
            priv->nextBuffer = NULL;
            prec->nord = priv->numbytes / dbValueSize(prec->ftvl);
    
            epicsEventSignal(priv->wakeup);
        }
    
        epicsMutexUnlock(priv->lock);
    
        assert(prec->bptr);
    
        return 0;
    }
    
    static
    struct dset5 {
        dset com;
        DEVSUPFUN read;
    } devWfZeroCopy = {
    {5, NULL,
        &init,
        &init_record,
        &get_iointr_info
    },
        &read_wf
    };
    
    #include <epicsExport.h>
    
    epicsExportAddress(dset, devWfZeroCopy);
