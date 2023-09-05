# How to Add a New Breakpoint Table

```{tags} developer, advanced
```

1. Copy `menuConvert.dbd` from `base/dbd` to the app's src directory.

2. In the src directory, create a breakpoint table file `<bpname>.dbd`. Look at `base/dbd/bpt*.dbd` for the proper format.

3. In `src/menuConvert.dbd`, add a line for your new breakpoint table, using the breaktable name from the first line of `<bpname>.dbd`. Look at the existing breakpoint table entries in `menuConvert.dbd` for the proper format.

4. Two options depending on the monotonicity and base version

    - If the breakpoint table is monotonic or epics base is \< 3.14.9, add `<bpname>.dbd` to `src/<appname>Support.dbd`:

    ``` c
    include <bpname>.dbd
    ```

    If Makefile is used instead of `<appname>Support.dbd`, add to `src/Makefile`:

    ``` makefile
    <appname>_DBD += <bpname>.dbd
    ```

    - If the breakpoint table is non-monotonic and epics base > 3.14.8, install `<bpname>.dbd` by itself in `src/Makefile`:

    ``` makefile
    DBD += <bpname>.dbd
    ```

5. Clean/build src.

6. Use the breaktable name in the record's LINR field. Make sure that the device support for the record supports conversion.

7. If the breakpoint table is non-monotonic and epics base > 3.14.8, change `st.cmd` to set the non-monotonic flag and load the breakpoint table:

``` c
dbBptNotMonotonic=1 (rtems, vxWorks)
```

or:

``` c
var dbBptNotMonotonic 1 (soft)
```

then:

``` c
dbLoadRecords("dbd/<bpname>.dbd")

```
