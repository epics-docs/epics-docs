What is EPICS?
--------------

.. image:: ../images/EPICS_black_blue_logo_rgb_small_v03.jpg


The **Experimental Physics and Industrial Control System** (**EPICS**) comprises
a set of software components and tools that can be used to create
distributed control systems. EPICS provides capabilities that are
typically expected from a distributed control system:

-  Remote control & monitoring of facility equipment

-  Automatic sequencing of operations

-  Facility mode and configuration control

-  Management of common time across the facility

-  Alarm detection, reporting and logging

-  Closed loop (feedback) control [1]

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

.. [1]
   Strictly speaking, each field of a record can also be considered as a
   process variable. However, for this discussion it is sufficient to
   take the simpler approach to equate a record with a PV.