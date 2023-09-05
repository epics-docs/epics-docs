Packages required for EPICS on Centos 8
=======================================

.. tags:: beginner
.. contents:: Contents


Overview
--------
This document describes the packages that must be installed in order to build EPICS base, 
synApps, and areaDetector on a new Centos 8 system.  
For other versions of Linux the package manager and package names may be different, 
but the requirements are likely to be the same.

Add the Extra Packages for Enterprise Linux (EPEL) site for the dnf package manager.  
This site has additional packages that are needed::

  sudo dnf install epel-release

Enable the powertools repository by running::
   
  sudo dnf config-manager --set-enabled powertools

Or on CentOS 9 Stream by running::

  sudo dnf config-manager --set-enabled crb


Packages required to build EPICS base
-------------------------------------

::

  sudo dnf install gcc gcc-c++ gcc-toolset-9-make readline-devel perl-ExtUtils-Install make


Packages required by the sequencer
----------------------------------

::

  sudo dnf install re2c

Packages required by epics-modules/asyn
---------------------------------------

::

  sudo dnf install rpcgen libtirpc-devel

Packages required by the Canberra and Amptek support in epics-modules/mca
-------------------------------------------------------------------------

::

  sudo dnf install libnet-devel libpcap-devel libusb-devel

Packages required by the Linux drivers in epics-modules/measComp
----------------------------------------------------------------

::

  sudo dnf install libnet-devel libpcap-devel libusb-devel

Packages required by areaDetector/ADSupport/GraphicsMagick
----------------------------------------------------------

::

  sudo dnf install xorg-x11-proto-devel libX11-devel libXext-devel


Packages required by areaDetector/ADEiger
-----------------------------------------

::

  sudo dnf install zeromq-devel


Packages required to build aravis 7.0.2 for areaDetector/ADAravis
-----------------------------------------------------------------

::

  sudo dnf install ninja-build meson glib2-devel libxml2-devel gtk3-devel gstreamer1 gstreamer1-devel gstreamer1-plugins-base-devel libnotify-devel gtk-doc gobject-introspection-devel


Packages required to build areaDetector/ADVimba
-----------------------------------------------

::

 sudo dnf install glibmm24-devel


Packages required to build EDM
------------------------------

::

  sudo dnf install giflib giflib-devel zlib-devel libpng-devel motif-devel libXtst-devel

Packages required to build MEDM
-------------------------------

::

  sudo dnf install libXt-devel motif-devel


