EPICS Documentation
===================

This is the parent project for all EPICS related documentation on read-the-docs.

A good part of the EPICS documentation is dynamically created and hosted by
`read-the-docs <https://readthedocs.org>`_, which acts as a CI system, building
and hosting documentation from source or dedicated documentation repositories.

Read-the-docs offers valuable features that we use:

- Keeps complete frozen documentation trees of all released versions under a
  permalink with the release number.
- Keeps the documentation of the development tree (usually 'master') up-to-date
  and accessible using 'latest' as release number.
- Switching versions is available through the web browser.

This parent project page is not directly linked from the EPICS web site.
It creates the link to the canonical URL https://docs.epics-controls.org -
links from the EPICS web site to the documentation should point to the
subprojects using the canonical URL, e.g.,
'https://docs.epics-controls.org/projects/<project-slug>'

There are two kinds of subprojects:

1. Code repositories:
   The documentation is created from comments in the source code (Javadoc or
   Doxygen) and separate documents (PDF, Markdown, restructuredText).
   Documentation trees of released versions are kept for reference.

2. Documentation repositories:
   The repositories contain only documentation (like FAQs and How-To-Pages).
   Usually only one version exists ('latest').


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
