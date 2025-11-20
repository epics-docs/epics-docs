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

How this documentation is organized
-----------------------------------

Each page is labeled by the intended audience.
You may also directly use related links to see documents which match you the most.

.. toctree::
   :hidden:

   EPICS Website <https://epics-controls.org>

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   getting-started/EPICS_Intro

.. toctree::
   :caption: Site tags
   :maxdepth: 2
   :hidden:
   :titlesonly:

   _tags/tagsindex

.. toctree::
   :maxdepth: 1
   :caption: Installation

   getting-started/installation
   getting-started/installation-linux
   getting-started/installation-windows
   getting-started/installation-rtems
   getting-started/creating-ioc
   getting-started/os-specifics
   EPICS 7.0 Release Notes <https://docs.epics-controls.org/projects/base/en/latest/RELEASE_NOTES.html>


.. toctree::
   :maxdepth: 1
   :caption: Application Developer's Guide

   Getting Started <appdevguide/gettingStarted>
   EPICS Overview (Introduction to EPICS) <../getting-started/EPICS_Intro>
   Build Facility <build-system/specifications>
   EPICS Process Database Concepts <process-database/EPICS_Process_Database_Concepts>
   Database Locking, Scanning and Processing <appdevguide/lockScanProcess>
   Database Definition <appdevguide/databaseDefinition>
   IOC Initialization <appdevguide/IOCInit>
   appdevguide/AccessSecurity
   IOC Test Facilities <appdevguide/IOCTestFacilities>
   appdevguide/IOCErrorLogging
   appdevguide/deviceSupport
   appdevguide/IOCShell
   Application Developer's Guide (historical pdf, for 3.16.2) <https://epics.anl.gov/base/R3-16/2-docs/AppDevGuide.pdf>

.. toctree::
   :maxdepth: 1
   :caption: Use Cases and Design Patterns

   IOC Component Reference <https://docs.epics-controls.org/projects/base/en/latest/ComponentReference.html>
   process-database/common-database-patterns
   Database Examples (external link) <https://github.com/epics-docs/database-examples>
   process-database/how-to-avoid-copying-arrays-with-waveformrecord
   process-database/add-new-breakpoint-table.md
   getting-started/HowToUseStreamDevice
   build-system/how-to-port-epics-to-a-new-os-architecture

.. toctree::
   :maxdepth: 1
   :caption: EPICS Related Software

   software/epics-related-software

.. toctree::
   :maxdepth: 1
   :caption: PV Access details

   pv-access/overview
   PV Access Protocol Specification <pv-access/protocol>
   pv-access/Normative-Types-Specification
   pv-access/OverviewOfpvData

.. toctree::
   :maxdepth: 1
   :caption: Channel Access reference

   ca-ref/introduction
   ca-ref/configuration
   Command-line interface <https://docs.epics-controls.org/projects/base/en/latest/ca-cli.html>
   ca-ref/troubleshooting
   ca-ref/function-call-interface-general-guidelines

.. toctree::
   :maxdepth: 1
   :caption: System administration

   sys-admin/configure-ca
   sys-admin/how-to-find-which-ioc-provides-a-pv
   sys-admin/channel-access-reach-multiple-soft-iocs-linux
   sys-admin/setup-softioc-framework-linux
   sys-admin/console-logging-vme-softioc
   sys-admin/save-restore-tools.md
   build-system/posix-threads-priority-scheduling-linux

.. toctree::
   :maxdepth: 1
   :caption: Internal

   internal/ca_protocol
   internal/IOCInit
   Common Library C/C++ APIs <https://docs.epics-controls.org/projects/base/en/latest/libcom-api.html>
   IOC Database C/C++ APIs <https://docs.epics-controls.org/projects/base/en/latest/database-api.html>

.. toctree::
   :maxdepth: 1
   :caption: Contributing

   contributing/HowToWorkWithTheEpicsRepository
   CONTRIBUTING
   Installing EPICS on Raspberry PI (External) <https://cmd-response.readthedocs.io/en/latest/epics/rpi_epics.html>
   Area Detector: Installation Guide (External) <https://areadetector.github.io/areaDetector/install_guide.html>

.. toctree::
   :maxdepth: 1
   :caption: Training

   Training Material <https://epics-controls.org/resources-and-support/documents/training/>
   community/how-to-run-an-epics-collaboration-meeting.rst
