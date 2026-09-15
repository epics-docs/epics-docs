# Database Records

Database record instances are fundamentally different from the other database definitions.
A file containing record instances should never contain any of the other definitions and vice-versa.
Database record files typically use `.db` as the file extension.

## Format

```
record(record_type, record_name) {
    alias(alias_name)
    field(field_name, "field_value")
    info(info_name, "info_value")
    ...
}
alias(record_name, alias_name)
```

## General Rules

The general rules are the same as for the database definitions: {ref}`subsec:database-general-rules`.

The exception is that multiple record instances of the same name can be defined.

### Multiple Records of the Same Name

Multiple definitions of records using the same **record_name** is generally allowed,
as long as the record type is the same.
The last value given for each **field** is the value used.
The variable `dbRecordsOnceOnly` can be set to any non-zero value
using the iocsh `var` command to make loading duplicate record definitions into the IOC illegal.
:::{versionadded} 3.15.0.2
the record type has not to be repeated and instead `"*"` may be used.
:::

:::{versionadded} 7.0.8
using `"*"` allows to define multiple record entries even if `dbRecordsOnceOnly!=0` is set.
:::

Examples:

```
record(ai, "myrec") {field(VAL, "5")}
```

```
record("*", "myrec") {field(VAL, "10")}
```

`"myrec"` will therefore be initiliased with the value `10`.

With setting `dbRecordsOnceOnly!=0`, the behaviour is:

```
record("*", "myrec") {field(VAL, "10")} # allowed
record(ai, "myrec") {field(VAL, "10")} # error
```

:::{versionadded} 7.0.9
it is possible to use `"#"` to remove a previously defined record.
:::
Values for the fields are not required or advised,
just use an empty record body `{}`.
This is useful when a template defines records that are not wanted in some IOCs,
without having to split or duplicate the original template.

For example, this will remove the record named “unwanted”:

```
record("#", "unwanted") {}
```

## Definitions

**record_type**
:   The record type, `"*"` or `"#"` (see [Multiple Records of the Same Name](#multiple-records-of-the-same-name))

**record_name**
:   The record name. This must be composed out of only the following
    characters:

    ```
    a-z A-Z 0-9 _ - + : [ ] < > ;
    ```

    NOTE: If macro substitutions are used the name must be quoted.

**alias_name**
:   An alternate name for the record, following the same rules as the
    record name.

**field_name**
:   A field name.

**field_value**
:   A value for the named field, appropriate for its particular field
    type.
    When given inside double quotes the field value string may
    contain escaped characters which will be translated appropriately
    when loading the database.
    See section {ref}`subsec:database-escape-sequences`
    for the list of escaped characters supported.
    Permitted values for the various field types
    are as follows:

    -  **`DBF_STRING`** \
       Any ASCII string. If it exceeds the field length, it will be
       truncated.

    -  **`DBF_CHAR`, `DBF_UCHAR`, `DBF_SHORT`, `DBF_USHORT`, `DBF_LONG`, `DBF_ULONG`**  \
       A string that represents a valid integer.
       The standard C conventions are applied, i.e. a leading 0 means
       the value is given in octal and a leading 0x means that value
       is given in hex.

    -  **`DBF_FLOAT`, `DBF_DOUBLE`** \
       The string must represent a valid floating point number.
       Infinities or NaN are also allowed.

    -  **`DBF_MENU`** \
       The string must be one of the valid choices for the associated
       menu.

    -  **`DBF_DEVICE`** \
       The string must be one of the valid device choice strings.

    -  **`DBF_INLINK`, `DBF_OUTLINK`, `DBF_FWDLINK`** \
       NOTES:

       -  If the field name is `INP` or `OUT` then this field is
          associated with `DTYP`, and the permitted values are
          determined by the link type of the device support selected by
          the current `DTYP` choice string.
          Other `DBF_INLINK` and
          `DBF_OUTLINK` fields must be either `CONSTANT` or
          `PV_LINK`s.

       -  A device support that specifies a link type of `CONSTANT` can
          be given either a constant or a `PV_LINK`.

       The allowed values for the field depend on the device support's
       link type as follows:

       -  **`CONSTANT`** \
          A numeric literal, valid for the field type it is to be read
          into.

       -  **`PV_LINK`** \
          A value of the form:

          ```
          record.field process maximize
          ```

          `record` is the name of a record that exists in this or
          another IOC.

          The `.field`, `process`, and `maximize` parts are all
          optional.

          The default value for `.field` is `.VAL`.

          `process` can have one of the following values:

          -  `NPP` – No Process Passive (Default)

          -  `PP` – Process Passive

          -  `CA` – Force link to be a channel access link

          -  `CP` – CA and process on monitor

          -  `CPP` – CA and process on monitor if record is passive

             NOTES:

             `CP` and `CPP` are valid only for `DBF_INLINK` fields.

             `DBF_FWDLINK` fields can use `PP` or `CA`.
             If a
             `DBF_FWDLINK` is a channel access link it must reference
             the target record's `PROC` field.

          `maximize` can have one of the following values:

          -  `NMS` – No Maximize Severity (Default)

          -  `MS` – Maximize Severity

          -  `MSS` – Maximize Severity and Status

          -  `MSI` – Maximize Severity if Invalid

       -  **`VME_IO`** \
          `#Ccard Ssignal @parm`

          `card` – the card number of associated hardware module
          `signal` – signal on card
          `parm` – An arbitrary character string of up to 31
          characters.
          This field is optional and is device specific.

       -  **`CAMAC_IO`** \
          `#Bbranch Ccrate Nstation Asubaddress Ffunction @parm`

          `branch`, `crate`, `station`, `subaddress`, and
          `function` should be obvious to `camac` users.
          `subaddress` and `function` are optional (0 if not given).
          `parm` is also optional and is device specific (25 characters
          max).

       -  **`AB_IO`** \
          `#Llink Aadapter Ccard Ssignal @parm`

          `link` – Scanner, i.e. vme scanner number
          `adapter` – Adapter.
          Allen Bradley also calls this rack
          `card` – Card within Allen Bradley Chassis
          `signal` – signal on card
          `parm` – optional device-specific character string (27 char
          max)

       -  **`GPIB_IO`** \
          `#Llink Aaddr @parm`

          `link` – gpib link, i.e. interface
          `addr` – GPIB address
          `parm` – device-specific character string (31 char max)

       -  **`BITBUS_IO`** \
          `#Llink Nnode Pport Ssignal @parm`

          `link` – link, i.e. vme bitbus interface
          `node` – bitbus node
          `port` – port on the node
          `signal` – signal on port
          `parm` – device specific-character string (31 char max)

       -  **`INST_IO`** `@parm` \
          `parm` – Device dependent character string

       -  **`BBGPIB_IO`** \
          `#Llink Bbbaddr Ggpibaddr @parm`

          `link` – link, i.e. vme bitbus interface
          `bbadddr` – bitbus address
          `gpibaddr` – gpib address
          `parm` – optional device-specific character string (31 char
          max)

       -  **`RF_IO`** \
          `#Rcryo Mmicro Ddataset Eelement`

       -  **`VXI_IO`** \
          `#Vframe Cslot Ssignal @parm` (Dynamic addressing)
          or
          `#Vla Signal @parm` (Static Addressing)

          `frame` – VXI frame number
          `slot` – Slot within VXI frame
          `la` – Logical Address
          `signal` – Signal Number
          `parm` – device specific character string(25 char max)

**info_name**
:   The name of an Information Item related to this record.
    See section on Record Information Items below for more on
    Information Items.

**info_value**
:   Any ASCII string.
    IOC applications using this information item may
    place additional restrictions on the contents of the string.

## Examples

```
record(ai, "STS_AbAiMaS0") {
    field(SCAN, ".1 second")
    field(DTYP, "AB-1771IFE-4to20MA")
    field(INP, "#L0 A2 C0 S0 F0 @")
    field(PREC, "4")
    field(LINR, "LINEAR")
    field(EGUF, "20")
    field(EGUL, "4")
    field(EGU, "MilliAmps")
    field(HOPR, "20")
    field(LOPR, "4")
}
record(ao, "STS_AbAoMaC1S0") {
    field(DTYP, "AB-1771OFE")
    field(OUT, "#L0 A2 C1 S0 F0 @")
    field(LINR, "LINEAR")
    field(EGUF, "20")
    field(EGUL, "4")
    field(EGU, "MilliAmp")
    field(DRVH, "20")
    field(DRVL, "4")
    field(HOPR, "20")
    field(LOPR, "4")
    info(autosaveFields, "VAL")
}
record(bi, "STS_AbDiA0C0S0") {
    field(SCAN, "I/O Intr")
    field(DTYP, "AB-Binary Input")
    field(INP, "#L0 A0 C0 S0 F0 @")
    field(ZNAM, "Off")
    field(ONAM, "On")
}
```
