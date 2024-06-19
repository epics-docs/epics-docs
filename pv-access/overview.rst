PV Access repositories overview
===============================

.. tags:: developer, advanced

There are (at the time of writing) two generations of pvAccess C++ implementations available:

PVXS
----

PVXS <https://mdavidsaver.github.io/pvxs/> is a re-implementation of the pvAccess protocol support. 
This module provides a library (libpvxs.so or pvxs.dll) 
and a set of CLI utilities acting as PVAccess protocol client and/or server.

PVXS is functionally equivalent to the pvDataCPP and pvAccessCPP modules, 
and is foreseen to eventually supplant those. 

Inclusion in the EPICS release packages is foreseen from EPICS version 7.1.

PVA "classic"
-----------

These modules comprise the pvAccess implementation that was written in context of the "EPICS 4" project and integrated into
EPICS base distribution as separate modules beginning from version 7.0.


-   pvData <https://docs.epics-controls.org/projects/pvdata-cpp/en/latest>
-   pvAccess <https://docs.epics-controls.org/projects/pvaccess-cpp/en/latest>
-   pva2pva (QSRV / pvAccess Gateway) <https://docs.epics-controls.org/projects/pva2pva/en/latest>
-   Normative Types <https://docs.epics-controls.org/projects/normativetypes-cpp/en/latest>
-   pvaClient <https://docs.epics-controls.org/projects/pvaclient-cpp/en/latest>
-   pvDatabase <https://docs.epics-controls.org/projects/pvdatabase-cpp/en/latest>
