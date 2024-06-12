Welcome to the EPICS Documentation!
===================================

![image](./images/EPICS_black_blue_logo_rgb_small_v03.jpg)

The **Experimental Physics and Industrial Control System** (**EPICS**)
comprises a set of software components and tools that can be used to
create distributed control systems. EPICS provides capabilities that are
typically expected from a distributed control system:

-   Remote control & monitoring of facility equipment
-   Automatic sequencing of operations
-   Facility mode and configuration control
-   Management of common time across the facility
-   Alarm detection, reporting and logging
-   Closed loop (feedback) control
-   Modeling and simulation
-   Data conversions and filtering
-   Data acquisition including image data
-   Data trending, archiving, retrieval and plotting
-   Data analysis
-   Access security (basic protection against unintended manipulation)

EPICS can scale from very big to very small systems. Big systems have to
be able to transport and store large amounts of data, be robust and
reliable but also failure-tolerant. Failure of a single component should
not bring the system down. For small installations it has to be possible
to set up a control system without requiring complicated or expensive
infrastructure components.

For modern applications, management of data is becoming increasingly
important. It shall be possible to store acquired operational data for
the long term and to retrieve it in the original form. EPICS provides
the tools to achieve this and to tailor the data management to the needs
of the facility.

One of the most appreciated aspects of EPICS is the lively collaboration
that is spread around the globe. Members of the collaboration are happy
to help other users with their issues and to discuss new ideas.

How this documentation is organized
-----------------------------------

Each page is labeled by the intended audienece. You may also directly
use related links to see documents which match you the most.

::: {.toctree}
EPICS Website \<<https://epics-controls.org>\>
:::

::: {.toctree}
getting-started/EPICS\_Intro
:::

::: {.toctree}
\_tags/tagsindex
:::

::: {.toctree}
getting-started/installation getting-started/installation-linux
getting-started/installation-windows getting-started/linux-packages.rst
getting-started/cross-compile-to-old-x86-linux
getting-started/creating-ioc getting-started/epics-macosx-firewall
getting-started/configuring-vxworks-6\_x
getting-started/vxworks5\_tornado
:::

::: {.toctree}
process-database/common-database-patterns
process-database/how-to-avoid-copying-arrays-with-waveformrecord
Application Developer\'s Guide (pdf, 3.16.2)
\<<https://epics.anl.gov/base/R3-16/2-docs/AppDevGuide.pdf>\>
Application Developer\'s Guide (web version, preliminary)
\<appdevguide/AppDevGuide\>
process-database/EPICS\_Process\_Database\_Concepts.rst
process-database/add-new-breakpoint-table.md Database Examples (external
link) \<<https://github.com/epics-docs/database-examples>\>
:::

::: {.toctree}
software/epics-related-software
:::

::: {.toctree}
build-system/how-to-port-epics-to-a-new-os-architecture Getting Started
with EPICS on RTEMS 4
\<<https://epics.anl.gov/base/RTEMS/tutorial/tutorial.html>\>
build-system/specifications
:::

::: {.toctree}
pv-access/overview PV Access specifications
\<<https://github.com/epics-base/pvAccessCPP/wiki/protocol>\>
pv-access/Normative-Types-Specification pv-access/OverviewOfpvData
:::

::: {.toctree}
access-security/specifications
:::

::: {.toctree}
sys-admin/configure-ca sys-admin/how-to-find-which-ioc-provides-a-pv
sys-admin/channel-access-reach-multiple-soft-iocs-linux
sys-admin/setup-softioc-framework-linux
sys-admin/console-logging-vme-softioc sys-admin/save-restore-tools.md
:::

::: {.toctree}
internal/ca\_protocol internal/IOCInit
:::

::: {.toctree}
contributing/HowToWorkWithTheEpicsRepository CONTRIBUTING Installing
EPICS on Raspberry PI (External)
\<<https://prjemian.github.io/epicspi/>\> Area Detector: Installation
Guide (External)
\<<https://areadetector.github.io/master/install_guide.html>\>
:::

::: {.toctree}
Training Material
\<<https://epics-controls.org/resources-and-support/documents/training/>\>
community/how-to-run-an-epics-collaboration-meeting.rst
:::
