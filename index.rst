Welcome to the EPICS Documentation!
====================================


.. image:: ./images/EPICS_black_blue_logo_rgb_small_v03.jpg


The **Experimental Physics and Industrial Control System** (**EPICS**) comprises
a set of software components and tools that can be used to create
distributed control systems. EPICS provides capabilities that are
typically expected from a distributed control system:

-  Remote control & monitoring of facility equipment

-  Automatic sequencing of operations

-  Facility mode and configuration control

-  Management of common time across the facility

-  Alarm detection, reporting and logging

-  Closed loop (feedback) control

-  Modeling and simulation

-  Data conversions and filtering

-  Data acquisition including image data

-  Data trending, archiving, retrieval and plotting

-  Data analysis

-  Access security (basic protection against unintended manipulation)

EPICS can scale from very big to very small systems. Big systems have to
be able to transport and store large amounts of data, be robust and
reliable but also failure-tolerant. Failure of a single component should
not bring the system down. For small installations it has to be possible
to set up a control system without requiring complicated or expensive
infrastructure components.

For modern applications, management of data is becoming increasingly important.
It shall be possible to store acquired operational data for
the long term and to retrieve it in the original form. EPICS provides the
tools to achieve this and to tailor the data management to the needs of
the facility.

One of the most appreciated aspects of EPICS is the lively collaboration
that is spread around the globe. Members of the collaboration are happy
to help other users with their issues and to discuss new ideas.

.. toctree::
   :hidden:

   EPICS Website <https://epics-controls.org>

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   getting-started/EPICS_Intro
   getting-started/installation
   getting-started/linux-packages.rst
   getting-started/creating-ioc
   getting-started/installation-windows
   getting-started/epics-macosx-firewall
   getting-started/setup-softioc-framework-linux
   getting-started/console-logging-vme-softioc
   getting-started/save-restore-tools.md
   getting-started/configure-ca
   getting-started/channel-access-reach-multiple-soft-iocs-linux

.. toctree::
   :maxdepth: 1
   :caption: Process database

   process-database/common-database-patterns
   process-database/how-to-avoid-copying-arrays-with-waveformrecord
   process-database/how-to-find-which-ioc-provides-a-pv
   Application Developer's Guide (pdf, 3.16.2) <https://epics.anl.gov/base/R3-16/2-docs/AppDevGuide.pdf>
   Application Developer's Guide (web version, preliminary) <appdevguide/AppDevGuide>
   process-database/EPICS_Process_Database_Concepts.rst
   process-database/add-new-breakpoint-table.md
   Database Examples (external link) <https://github.com/epics-docs/database-examples>

.. toctree::
   :maxdepth: 1
   :caption: EPICS Related Software
   
   software/epics-related-software

.. toctree::
   :maxdepth: 1
   :caption: The build system

   build-system/how-to-port-epics-to-a-new-os-architecture
   build-system/cross-compile-epics-and-a-ioc-to-an-old-x86-linux.md
   Getting Started with EPICS on RTEMS 4 <https://epics.anl.gov/base/RTEMS/tutorial/tutorial.html>
   build-system/configuring-vxworks-6_x
   build-system/vxworks6_tornado
   build-system/specifications

.. toctree::
   :maxdepth: 1
   :caption: PV Access details

   pv-access/overview
   PV Access specifications <https://github.com/epics-base/pvAccessCPP/wiki/protocol>
   pv-access/Normative-Types-Specification
   pv-access/OverviewOfpvData

.. toctree::
   :maxdepth: 1
   :caption: Access security

   access-security/specifications

.. toctree::
   :maxdepth: 1
   :caption: Internal

   internal/ca_protocol
   internal/IOCInit

.. toctree::
   :maxdepth: 1
   :caption: Contributing

   contributing/HowToWorkWithTheEpicsRepository
   CONTRIBUTING
   Installing EPICS on Raspberry PI (External) <https://prjemian.github.io/epicspi/>
   Area Detector: Installation Guide (External) <https://areadetector.github.io/master/install_guide.html>

.. toctree::
   :maxdepth: 1
   :caption: Software

   specs/specs
   software/base

.. toctree::
   :maxdepth: 1
   :caption: Training

   Training Material <https://epics-controls.org/resources-and-support/documents/training/>
   community/how-to-run-an-epics-collaboration-meeting.rst
