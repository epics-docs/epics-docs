# PV Save and Restore Tools available


There are a number of different tools available within the EPICS community for saving and restoring values of PVs. This page gives somewhere for them to be briefly described, since they all have somewhat different characteristics. This page may be incomplete; if you know of a published tool that is not described here, please consider adding it

## IOC-based Tools

## [SynApps Autosave](https://epics.anl.gov/bcda/synApps/autosave/autosave.html)

Autosave automatically saves the values of EPICS process variables (PVs) to files on a server, and restores those values when the IOC is rebooted.


## Host-based Tools

### XAL 'score'

The XAL collection of high-level applications includes 'score': A Table of PV names, each with a current value and a saved value. One can see which PVs differ from their saved state, restore them etc.

Don't know a good web page, but try [this one](https://openxal.github.io/) .

### CSS 'PV Table'

Similar to 'score', but simpler and still unter development. Saves values to XML files, no connection to RDB.

For more on CSS (Control System Studio), see the [main page at DESY](http://css.desy.de).

### sddscasr

[**sddscasr**](https://ops.aps.anl.gov/manuals/EPICStoolkit/EPICStoolkit.html) is based off of casave, carestore, and sddssnapshot. It is used to save and restore snapshots of the PV values. The format of the request file and snapshot file is SDDS. It can be run in daemon mode where it maintains connections to PVs and when a trigger PV is activated it creates a new snapshot. This reduces the number of network calls to all the IOCs because it does not have to search for the PVs every time a snapshot it taken. This program is used at the APS for many different systems, including some with request files having over 17 thousand PVs.

It can also be used in conjunction with APS's SaveCompareRestore tool.
