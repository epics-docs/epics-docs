# "Best Practice" Guidelines

## "Best Practice" Guidelines for Developers

This document presents some guidelines that have been found useful. Please add your own suggestions!

### Support Modules

*   If your IOC application source directory contains '.c' files you should **definitely** consider moving them to a support module (either existing or new). A big problem in the past has been the proliferation of similar or identical '.c' files among multiple IOC applications. Help stamp out this practice now! To a lesser degree you should consider doing the same for any sequence programs in your application although these tend to be much more application-specific and thus impractical to move to a support module.
*   Use `$EPICS_BASE/bin/makeBaseApp.pl -t support` to create a new support module. If you're writing a new message-based instrument support module `<path to asyn bin>/makeSupport.pl -t streamSCPI` is a good place to start.
*   Nothing within the support 'modules' directory tree should be an 'App'. Nothing within the 'ioc' applications directory tree should be anything but an 'App'.

### Device Support

*   All message-based devices (with any expected lifetime) should be converted to use ASYN. If you are starting from existing devGpib support see [these guidelines for conversion](https://epics.anl.gov/modules/soft/asyn/R4-10/gpibCoreConversion/conversionNotes.html). If you are starting on brand-new support see [these notes](https://epics.anl.gov/modules/soft/asyn/R4-10/HowToDoSerial/tutorial.html) or have a look at the [stream device support](http://epics.web.psi.ch/software/streamdevice/).
*   Support for a particular device should be in its own support module.

### Database Files

*   Support modules and IOC applications should install all .db files into their <top>/db directory. When an application uses a .db file from a support module that file may be copied from the support module `<top>/db` directory to the IOC application `<top>/db` directory. This is done by adding lines like `DB_INSTALLS += $(ASYN)/db/asynRecord.db` to the application `<top>/_appName_/Db/Makefile`. This allows all the .db files needed by an application to be found in a single location.
*   Template files that are part of support modules do not need to be copied to your application Db source directory. The build system knows to look in support module db directories for template files.

### Application Makefile

*   Add support module .dbd files to your application using the Makefile `_xxxxxx_DBD += _yyyyy_.dbd` mechanism.

### st.cmd

*   Expansion of substitution/template files should be performed at build-time on the host rather than at application startup on the IOC.
*   **vxWorks only** — The **ld** command to load the application executable code must not use vxWorks shell redirection since this may break the commands later in the script. Change lines like

``` console
ld < libpm.munch  
into  
ld 0,0, "libpm.munch"
```

### Autosave/restore

*   The autosave/restore support module provides several diagnostic PVs. One of the most important of these is a PV which indicates the success or failure of autosave operations. An infrastructure monitoring system can check this PV and provide warnings about problems. All applications which use autosave/restore should include these PVs.

To add the PVs to an application:

1.  Add the following line to the `<top>/_appName_/Db/Makefile`:
``` makefile
DB_INSTALLS += $(AUTOSAVE)/asApp/Db/save_restoreStatus.db
```
2.  If you're using the IOC shell, add the following lines to the st.cmd script (before iocInit)
``` bash
save_restoreSet_status_prefix($(IOC))  
dbLoadRecords(db/save_restoreStatus.db,P=$(IOC))  
```
If you're using the vxWorks shell to read the startup script the command must either specify the IOC name explicitly
``` bash
save_restoreSet_status_prefix("iocxxxxx")  
dbLoadRecords("db/save_restoreStatus.db","P=iocxxxxx")

```
or use iocshCmd to parse the lines
``` bash
iocshCmd("save_restoreSet_status_prefix($(IOC))")
iocshCmd("dbLoadRecords(db/save_restoreStatus.db,P=$(IOC))")
```

