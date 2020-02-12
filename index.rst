EPICS Documentation
===================

This is the parent project for all EPICS related documentation on read-the-docs.

A good part of the EPICS documentation is dynamically created and hosted by
`read-the-docs <readthedocs.org>`_, which acts as a CI system, building
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
   :caption: Guides

   Introduction to EPICS <guides/EPICS_Intro>
   guides/gettingstarted
   guides/EPICS_Process_Database_Concepts.rst
   How-To Pages <https://docs.epics-controls.org/projects/how-tos/en/latest>
   guides/faq

.. toctree::
   :maxdepth: 1
   :caption: Software

   specs/specs
   software/base
   software/modules
   Extensions <https://epics-controls.org/resources-and-support/extensions/>


.. toctree::
   :maxdepth: 1
   :caption: Training

   Training Material <https://epics-controls.org/resources-and-support/documents/training/>
