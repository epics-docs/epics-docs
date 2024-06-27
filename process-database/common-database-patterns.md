Common Database patterns
========================

``` {tags}
developer
```

Pull Alarm Status w/o Data
--------------------------

This is useful to bring alarm status in without affecting the value
stored in a record. In the following example the alarm status of
**$(P):set** is fetched by **$(P):rbv** when it is processed, but the
value is read from a different record.

    record(bo, "$(P):set") {
        field(OSEV, "MAJOR")
        field(FLNK, "$(P):rbv")
    }

    record(bi, "$(P):rbv") {
        field(SDIS, "$(P):set NPP MS")
        field(DISV, "-1")
        field(INP , "$(P):some:other:record")   
    }

Combined Setting and Readback
-----------------------------

Use when a single PV is desired. Could be used to show the results of
rounding in a float to fixed precision conversion.

In the following example the value read from a 'bi' is inverted so that
the associated 'bo' acts as a toggle.

    record(bi, "$(P):rbv") {
        field(DTYP, "...")
        field(INP , "...")
        field(PINI, "YES")
        field(FLNK, "$(P):inv")
    }

    record(calcout, "$(P):inv")
        field(CALC, "!A")
        field(INPA, "$(P):rbv")
        field(OUT , "$(P) NPP")
    }

    record(bo, "$(P)") {
        field(DTYP, "...")
        field(OUT , "...")
        field(FLNK, "$(P):rbv")
    }

The important point is the NPP modifier on output link of the 'calcout'
record. This updates the VAL field of the 'bo' record (and posts
monitors) without processing it.
