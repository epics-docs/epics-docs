Setting the system environment
------------------------------
In order to run all EPICS commands anywhere by using their simple name and to build more EPICS modules using the same setup, you can set three environment variables for the current shell or user on the Windows system:

* EPICS_BASE
* EPICS_HOST_ARCH
* Path

Note that *running* IOCs only needs the Path to be set correctly (when using dynamic DLL builds).
*Building* IOC applications needs EPICS_HOST_ARCH and benefits from EPICS_BASE being set.

Required settings for Path
^^^^^^^^^^^^^^^^^^^^^^^^^^
The way you are building your binaries determines which paths have to be added to the Path variable.

* Static builds

  1. Add the EPICS Base binary directory for your target to be able to call the EPICS command line tools without specifying their fully qualified path.
  
  This setting is for convenience only and not mandatory. Your IOCs run without it.
  
* Dynamic (DLL) builds

  1. Add the EPICS Base binary directory for your target so that the EPICS DLLs are found and you can use the CLI tools without specifying the path.
  2. If you built your binaries using MinGW and want to use them under the Command Prompt or through a shortcut icon, add the MinGW binary directory ("C:\\msys64\\mingw64\\bin") so that the MinGW runtime system DLLs are found. Inside the MSYS2 Bash shell, this location is included by default.

  Both settings are mandatory; the former for all builds, the latter under the stated condition.

Set environment using a batch or script from EPICS Base
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
EPICS Base provides script and batch files to help setting the environment for running EPICS commands and doing EPICS builds.

The ``windows.bat`` batch file in the folder called ``startup`` sets the environment if you use the Windows command prompt and compiled your EPICS Base using Visual Studio compilers with the help of Strawberry Perl.
You probably will have to edit ``windows.bat`` to adapt it to your needs and ``call`` it from any Windows command prompt before doing EPICS commands or builds.
As ``windows.bat`` sets environment variables, it will not work properly if run from a ``powershell`` prompt via e.g. ``&``. You can either use a ``cmd`` command prompt for the EPICS build, or start the powershell session from a ``cmd`` session where you have already run the appropriate bat files. See https://stackoverflow.com/questions/49027851/setting-environment-variables-with-batch-file-lauched-by-powershell-script    

If you use the MSYS2 bash shell, you similarly need to adapt and run the ``unix.sh`` shell script from any bash shell prompt before doing EPICS commands or builds.

Set environment using the Windows settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This method requires less effort and does not need something special to be executed or called from the command prompt.

Go to Start Menu, Type "environment" and select "Edit environment variables for your account".
If you have Administrator rights and want to do it globally, you can also select ``Edit the system environment variables``.

1. Select ``Advance`` tab, navigate to ``Environment Variables`` button. That should open editable tables of settings for Windows Environment. 
2. Select ``User Variable for 'user'`` option, press NEW
3. Add EPICS BASE path here. In ``Variable Name``, put "EPICS_BASE". For ``Variable Value``, enter the location of your EPICS Base installation, e.g.,  "C:\\msys64\\home\\'user'\\base-7.0.9"
4. Set the host architecture. In ``Variable Name``, put "EPICS_HOST_ARCH". For ``Variable Value``, put "windows-x64-mingw" or "windows-x64" (depending on your selection of compilers).
5. Navigate to the variable called ``Path``. Press Edit. 
6. If you are using the MinGW compilers and dynamic (DLL) linking, add the path for the MinGW64 DLLs. Press NEW and enter "C:\\msys64\\mingw64\\bin". Press ok.
7. Add the path for the EPICS commands and DLLs. Press NEW and enter ``%EPICS_BASE%\bin\%EPICS_HOST_ARCH%``. Press ok twice and you are done.
8. Restart the Machine and check if EPICS commands like ``caget`` and ``camonitor`` are being recognised as valid commands in any location and work.

Note that by default the MSYS2 shell does not inherit the parent environment. To change that behavior, you need to start the shell with the argument ``-use-full-path``.
