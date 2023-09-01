EPICS Documentation
===================

How this documentation is organized
-----------------------------------

Each page is labeled by the intended audienece.
You may also directly use related links to see documents which match you the most.

    +------------------------+----------------------------------------------------------------------+
    | **Beginner**           | :ref:`For beginners<beginner_docs>`                                  |
    +------------------------+----------------------------------------------------------------------+
    | **User**               | :ref:`For users<user_docs>`                                          |
    +------------------------+----------------------------------------------------------------------+
    | **Developer**          | :ref:`For developers<developer_docs>`                                |
    +------------------------+----------------------------------------------------------------------+
    | **Advanced**           | :ref:`For advanced<advanced_docs>`                                   |
    +------------------------+----------------------------------------------------------------------+


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

.. toctree::
   :maxdepth: 1
   :caption: Process database

   process-database/common-database-patterns
   process-database/how-to-avoid-copying-arrays-with-waveformrecord
   process-database/how-to-find-which-ioc-provides-a-pv
   Application Developer's Guide (pdf, 3.16.2) <https://epics.anl.gov/base/R3-16/2-docs/AppDevGuide.pdf>
   Application Developer's Guide (web version, preliminary) <appdevguide/AppDevGuide>
   process-database/EPICS_Process_Database_Concepts.rst

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
