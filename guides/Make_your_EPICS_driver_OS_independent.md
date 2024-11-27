# How to make your EPICS driver operating system independent

From EPICSWIKI

**W. Eric Norum et. al.**

## Introduction

The following table shows the changes made to some existing drivers to allow them to be used on systems other than vxWorks.
Note that it is a very preliminary start at a set of conversion instructions.
There's still no 'cookbook' document to guide you,
but many drivers can be converted without doing much more than applying the translations shown.
A technique that I've found works well is to first change all the `#include` statements that mention vxWorks header files to their OSI equivalents,
then enter a compile-edit cycle until all compile errors have been eliminated.

## Conversions

| **vxWorks** | **OSI** |
|---|---|
| `#include <vxWorks.h>` | `#include <epicsStdlib.h>` |
| `#include <stdlib.h>` | `#include <epicsStdioRedirect.h>` |
| `#include <iosLib.h>` |  |
| `#include <taskLib.h>` | `#include <epicsThread.h>` |
| `#include <memLib.h>` |  |
| `#include <rebootLib.h>` | `#include <epicsExit.h>` |
| `#include <intLib.h>` | `#include <epicsInterrupt.h>` |
| `#include <wdLib.h>` | `#include <epicsTimer.h>` |
| `#include <lstLib.h>` | `#include <ellLib.h>` |
| `#include <vme.h>` | `#include <devLib.h>` |
| `#include <sysLib.h>` |  |
| `#include <iv.h>` |  |
|  | `#include <epicsExport.h>`   `#include <iocsh.h>`  |
| `ERROR` | `-1` |
| `OK` | `0` |
| `#include <semLib.h>   SEM_ID flag = semBCreate(SEM_Q_PRIORITY, SEM_EMPTY); semGive(flag); semTake(flag, WAIT_FOREVER);`  | `#include <epicsEvent.h>   epicsEventId flag = epicsEventMustCreate(epicsEventEmpty); epicsEventSignal(flag); epicsEventMustWait(flag);`  |
| `#include <semLib.h>   SEM_ID Lock = semMCreate(SEM_Q_PRIORITY); semTake(Lock, WAIT_FOREVER); semGive(Lock);`  | `#include <epicsMutex.h>   epicsMutexId Lock = epicsMutexMustCreate(); epicsMutexLock(Lock); epicsMutexUnlock(Lock);`  |
| `taskDelay(1)` | To generate a 'short' delay:   `epicsThreadSleep(0.001)` This works because the operating system specific layer ensures a delay of at least one system clock tick for `epicsThreadSleep` arguments greater than 0.  |
| `taskDelay(30)` | Much old code assumes a 60 Hz vxWorks system clock. On such systems the equivalent for the command shown would be:   `epicsThreadSleep(0.5)` Of course, other code may assumes a 50 Hz or 100 Hz system clock rate. You can find out what your system clock rate is using `epicsThreadSleepQuantum()`, which returns the clock period in seconds.  |
| `taskSuspend(0)` | `epicsThreadSuspendSelf()` |
|  `intConnect(INUM_TO_IVEC(irqVector), irqHandler, pLink)`  |  `devConnectInterruptVME(irqVector, irqHandler, pLink)`  |
| `sysIntEnable(IrqLevel)` | `devEnableInterruptLevelVME(IrqLevel)` |
|  `sysBusToLocalAdrs(VME_AM_SUP_SHORT_IO, (char*)CardAddress, (char**)&ErLink[Card].pEr)`  |  `devRegisterAddress(“apsEr”, atVMEA16, CardAddress, 0x40, (void*)&ErLink[Card].pEr)`  |
| `vxMemProbe(pReg, READ, sizeof(short), &value)` | `devReadProbe(sizeof(short), pReg, &value)` |
| `vxMemProbe(pReg,WRITE,sizeof(short), &value)` | `devWriteProbe(sizeof(short), pReg, &value)` |
| `key = intLock()` | `key = epicsInterruptLock()` |
| `intUnlock(key)` | `epicsInterruptUnlock(key)` |
|  `#include <wdLib.h> #include <sysLib.h> WDOG_ID wd = wdCreate(); wdStart(wd, delay * sysClkRateGet(), (FUNCPTR) wdCallback, (int) arg);`  |  `#include <epicsTimer.h> #include <epicsThread.h> epicsTimerQueueId tq = epicsTimerQueueAllocate(1, epicsThreadPriorityScanLow); epicsTimerId wd = epicsTimerQueueCreateTimer(tq, wdCallback, (void *) arg); epicsTimerStartDelay(wd, delay);` If the watchdog timer is being used only to invoke timed callbacks it may be possible to eliminate the watchdog timer completely and just use `callbackRequestDelayed` instead. If the timed callbacks are being used only for invoking record processing things are even simpler - just use `callbackRequestProcessCallbackDelayed`.  |
| `rebootHookAdd((FUNCPTR)ErRebootFunc)` | `epicsAtExit(ErRebootFunc, NULL)` |
| ` #include <fast_lock.h> FAST_LOCK lock; FASTLOCKINIT(&mzconf[card].lock); FASTLOCKFREE(&mzconf[card].lock); FASTLOCK(&mzconf[card].lock); FASTUNLOCK(&mzconf[card].lock);`  | You'll have to use your judgement here. If the section of code being protected is quick (less than a few microseconds) it's reasonable to simply disable interrupts while the code is active. In this case you can remove the 'lock' variable and the init/free operations and then add a local ‘key’ variable and replace the lock/unlock operations with `epicsInterruptLock/Unlock` operations. If the section of code being protected is longer you'll have to convert the `FASTLOCK` to an EPICS mutex. |
| `taskSpawn(...)` | `epicsThreadCreate(...)`   You should consider rewriting the driver to use the "worker thread" environment provided by the ASYN package. This is likely to result in a shorter, simpler, and more robust driver.  |


## Some other changes

*   Some R3.13 record support database definitions explicitly mention all fields rather than including `dbCommon.dbd`.
This can cause problems with `FAST_LOCK`.
The solution is to add `include "dbCommon.dbd"` at the beginning of the file in question
and to remove all entries for the fields provided by `dbCommon.dbd`.
*   You should set up IOC shell command registrations for all 'configure' functions
and for any other commands you may need to call from the IOC shell.
Here's an example of a fairly complex configuration command:

```c
 /*
  * IOC shell command registration
  */
 #include <iocsh.h>
 static const iocshArg vtr10012ConfigArg0 = { "card",iocshArgInt};
 static const iocshArg vtr10012ConfigArg1 = { "VME A16 offset",iocshArgInt};
 static const iocshArg vtr10012ConfigArg2 = { "VME memory offset",iocshArgInt};
 static const iocshArg vtr10012ConfigArg3 = { "interrupt vector",iocshArgInt};
 static const iocshArg vtr10012ConfigArg4 = { "interrupt level",iocshArgInt};
 static const iocshArg vtr10012ConfigArg5 = { "use DMA",iocshArgInt};
 static const iocshArg vtr10012ConfigArg6 = { "nchannels",iocshArgInt};
 static const iocshArg vtr10012ConfigArg7 = { "kilosamplesPerChan",iocshArgInt};
 static const iocshArg *vtr10012ConfigArgs[] = {
     &vtr10012ConfigArg0, &vtr10012ConfigArg1, &vtr10012ConfigArg2,
     &vtr10012ConfigArg3, &vtr10012ConfigArg4, &vtr10012ConfigArg5,
     &vtr10012ConfigArg6,&vtr10012ConfigArg7};
 static const iocshFuncDef vtr10012ConfigFuncDef =
                       {"vtr10012Config",8,vtr10012ConfigArgs};
 static void vtr10012ConfigCallFunc(const iocshArgBuf *args)
 {
     vtr10012Config(args[0].ival, args[1].ival, args[2].ival,
                  args[3].ival, args[4].ival, args[5].ival,
                  args[6].ival, args[7].ival);
 }
 
 /*
  * This routine is called before multitasking has started, so there's
  * no race condition in the test/set of firstTime.
  */
 static void
 drvVtr10012RegisterCommands(void)
 {
     static int firstTime = 1;
     if (firstTime) {
         iocshRegister(&vtr10012ConfigFuncDef,vtr10012ConfigCallFunc);
         firstTime = 0;
     }
 }
 epicsExportRegistrar(drvVtr10012RegisterCommands);
```

You must also provide a corresponding registrar statement in a `.dbd` file:

```
registrar(drvVtr10012RegisterCommands)
```

*   If your driver provides functions that are referred to by name from database files you must:
    *   `#include <registryFunction.h>`
    *   Add an `epicsExportFunction()` statement for each such function.
    *   Add a corresponding `function` statement in a `.dbd` file.

## Additional Information

The procedure for converting a support module from R3.13 to R3.14 is described in the
[Converting R3.13 Apps to R3.14](https://epics.anl.gov/base/R3-14/8-docs/ConvertingR3.13AppsToR3.14.html)
document.
