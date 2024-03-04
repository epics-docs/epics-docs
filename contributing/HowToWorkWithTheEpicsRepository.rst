How to Work with the EPICS Repository
=====================================

.. tags:: beginner, user, developer, advanced

This document aims to show to software developers how to get the current
EPICS Base code, modify it and publish the changes.

Organization of the EPICS Git Repository
----------------------------------------

The main EPICS repository is hosted on
`Launchpad <https://launchpad.net/epics-base>`__. The source code
repository is at https://git.launchpad.net/epics-base.

A mirror of the repository is available on Github:
https://github.com/epics-base/epics-base.git Depending on your location
one or the the other may be faster.

All current and past EPICS Base versions are in the same repository on
different branches.

EPICS 7
~~~~~~~

The current development branch is “core/master”. However this branch
only acts as a kind of envelope. The actual EPICS 7 code is divided into
modules each of which lives on a separate branch.

To get the latest version do this:

::

   git clone --recursive https://git.launchpad.net/epics-base
   cd epics-base
   git submodule update --remote

This requires at least git version 1.8. Older git versions may need a
different procedure. If ``git clone --recursive`` is not supported, do
this instead:

::

   git clone https://git.launchpad.net/epics-base
   cd epics-base
   git submodule update --init --reference .

If ``git submodule update --remote`` is not supported, look up the
branches of each module in the .gitmodule file, then go into each module
directory and check out the relevant branch manually.

Older EPICS Versions
~~~~~~~~~~~~~~~~~~~~

There is a separate branch for each of the older EPICS Base versions:
3.13, 3.14, 3.15, and 3.16. (However there is no 3.12 branch.)

Use these to check out the latest developments of one of the older
versions, for example to fix a bug in one of those versions.

::

   git clone --branch 3.14 https://git.launchpad.net/epics-base

Specific Releases
~~~~~~~~~~~~~~~~~

Individual releases as well as pre-releases and release candidates are
tagged like R3.16.1, R7.0.1-pre or R7.0.1-rc1. First clone the relevant
branch, then check out the tag, e.g.:

::

   git clone --branch 3.14 https://git.launchpad.net/epics-base
   cd epics-base
   git co R3.14.8

Making Changes
--------------

Changes should always be made against the head of the relevant branch,
not against the release tags.

For bug fixes check out the branch where the bug appears first. The fix
will be merged into newer EPICS versions by the core developer team.

For new features better announce your idea on the core-talk@aps.anl.gov
mailing list and ask which branch is most appropriate. For revolutionary
new features it is probably the EPICS 7 master branch respectively the
branch of the submodule as referenced in the .gitmodule file.

For each change create a new branch with a meaningful name.

::

   git checkout -b branch-name

Then start working on your change. Don’t forget to write a test!

Maintaining Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~

Build and test your changes on as many systems as possible. Important
operating systems are Linux, Windows, OS X, vxWorks and RTEMS.

Keep in mind that in particular vxWorks 5 uses old compiler versions. Do
not break working systems with dependencies on new compiler versions.
This means for example C++ 11 features.

EPICS up to 3.15 works with vxWorks 5.5 which uses gcc 3.3.2 with a
quite old C++ implementation and EPICS 3.16 works with vxWorks 6.3 using
gcc 3.4.4. Do not break that!

Testing
~~~~~~~

All new features must come with automated tests to prove their
functionality. This also helps to find out if future changes break
existing features.

There are several “test” directories. Choose the one appropriate for the
test. Keep in mind that some tests may run before all parts of Base are
built. Details vary depending on the EPICS Base version.

EPICS Base comes with a testing framework which allows to run IOCs, set
and read/compare values and more.

To add a test, you will typically create a xxxTest.c and probably some
records in a xxxTest.db file. (Choose a suitable name.) Also you need to
edit the Makefile in the test directory as well as a file with a name
like "epicsRun*Tests.c" to include your new test.

Here is a basic example of a test code (xxxTest.c):

.. code:: c

   #include "dbAccess.h"
   #include "dbUnitTest.h"
   #include "testMain.h"      
   MAIN(xxxTest) {
       epicsUInt32 value;
       
       /* Announce how many test will be done, see comments below. */
       testPlan(total_number_of_tests);

       testdbPrepare();

       /* Load your own IOC or one of the provided. */
       /* "dbTestIoc" or "recTestIoc" may be suitable. */
       testdbReadDatabase("recTestIoc.dbd", NULL, NULL);
       recTestIoc_registerRecordDeviceDriver(pdbbase);

       /* Load your records */
       testdbReadDatabase("xxxTest.db", NULL, "MACRO=VALUE");

       /* start up IOC */
       testIocInitOk();

       /* You may structure the test output with your own comments
        * (This does not count as a test.)
        */
       testDiag("##### This text goes to the test log #####");

       /* Set values and check for success. Counts as 1 test.
        * Make sure that DBF type matches your variable
        */
       testdbPutFieldOk("record.FIELD", DBF_ULONG, value);
     
       /* Get value and compare with expected result. Counts as 1 test.
        * Make sure that DBF type matches your variable
        */
       testdbGetFieldEqual("record.FIELD", DBF_ULONG, value);

       /* Do some arbitrary test. Counts as 1 test. */
       testOk(condition, formatstring, ...);
        
       /* The same without your own message. Counts as 1 test. */
       testOk1(condition);
        
       /* Finish */
       testIocShutdownOk();
       testdbCleanup();
       return testDone();
   }

Your test should run (and succeed) when you execute

::

   make runtests

Merging Your Work into EPICS Base
---------------------------------

When done with your development, do not push it to the main repository
(You probably do not have permission to do so anyway). Instead push it
to your personal repository on Launchpad.

Creating a Launchpad Account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you do not have a Launchpad account yet, got to
https://launchpad.net/ and click on “register”. With a Launchpad account
comes the possibility to have personal repositories. You will use these
to push your changes. Don’t forget to upload your public (*not
private!*) ssh key (found in $HOME/.ssh/id_rsa.pub or similar) in order
to be able to push to your repository using ssh.

Pushing Your Work to Launchpad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before pushing your work, you should first pull the latest version and
merge it with your changes if necessary.

In your git working directory, create a new “remote” referring to your
personal Launchpad repository. Launchpad will create a new repository if
necessary. You can use the same repository for multiple projects on
EPICS Base as long as you use different branch names.

::

   git remote add launchpad git+ssh://username@git.launchpad.net/~username/epics-base
   git push launchpad branch-name

After that you can go to the Launchpad web page related to that branch
(https://code.launchpad.net/~username/epics-base/+git/epics-base/+ref/branch-name)
and click the “Propose for merging” link. The core developer team will
review your changes any may either merge them or request fixes.

You can push updates on the same branch at any time, even after making a
merge request. The updates will automatically be part of the merge
request. Do **not** create a new merge request because of an update!
