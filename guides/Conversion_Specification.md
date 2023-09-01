# Conversion Specification

Conversion parameters are used to convert transducer data
into meaningful data.
Discrete signals require converting between levels and states 
(That is, on, off, high, low, etc.).
Analog conversions require converting between levels and engineering units
(That is, pressure, temperature, level, etc.).
These conversions are made to provide operators and application codes
with values in meaningful units.

The following sections discuss these types of conversions.
The actual field names appear in capital letters.

## Discrete Conversions

The simplest type of discrete conversion would be
the case of a discrete input that indicates the on/off state of a device.
If the level is high it indicates that the state of the device is on.
Conversely, if the level is low it indicates that the device is off. 
In the database, parameters are available to enter strings
which correspond to each level, which, in turn, correspond to a state (0,1).
By defining these strings,
the operator isn't required to know that a specific transducer
is on when the level of its transmitter is high or off when the level is low.
In a typical example, the conversion parameters for a discrete input
would be entered as follows:

**Zero Name (ZNAM)**: Off  
**One Name (ONAM)**: On

The equivalent discrete output example would be an on/off controller.
Consider a case where the safe state of a device is On, the zero state.
The level being low drives the device on,
so that a broken cable  will drive the device to a safe state. 
In this example the database parameters are entered as follows:

**Zero Name (`ZNAM`)**: On  
**One Name (`ONAM`)**: Off

By giving the outside world the device state, the information is clear.
Binary inputs and binary outputs are used to represent such on/off devices.

A more complex example involving discrete values
is a multi-bit binary output record.
Consider a two state valve which has four states: 
Traveling, full open, full closed, and disconnected.
The bit pattern for each control state is entered into the database
with the string that describes that state.
The database parameters for the monitor would be entered as follows:

**Number of Bits (`NOBT`):** 2  
**First Input Bit Spec (`INP`):** Address of the least significant bit  
**Zero Value (`ZRVL`):** 0  
**One Value (`ONVL`):** 1  
**Two Value (`TWVL`):** 2  
**Three Value (`THVL`):** 3  
**Zero String (`ZRST`):** Traveling  
**One String (`ONST`):** Open  
**Two String (`TWST`):** Closed  
**Three String (`THST`):** Disconnected

In this case, when the database record is scanned,
the monitor bits are read and compared with the bit patterns for each state.
When the bit pattern is found, the device is set to that state.
For instance, if the two monitor bits read equal 10 (binary),
the Two value is the corresponding value,
and the device would be set to state 2 which indicates that the valve is Closed.

If the bit pattern isn't found, the device is in an unknown state.
In this example all possible states are defined.

In addition, the `DOL` fields of binary output records (bo and mbbo)
will accept values in strings.
When they retrieve the string or when the value field is given a string
via put_enum_strs, a match is sought with one of the states.
If a match is found, the value for that state is written.

## Analog Conversions

Analog conversions require knowledge
of the transducer, the filters, and the I/O cards.
Together they measure the process,
transmit the data, and interface the data to the IOC.
Smoothing is available to filter noisy signals.
The smoothing argument is a constant between 0 and 1 and
is specified in the `SMOO` field.
It's applied to the converted hardware signal as follows:

```
eng units = (new eng units × (1 - smoothing)) + (old eng units × smoothing)
```
The analog conversions from raw values to engineering units
can be either linear or breakpoint conversions.

Whether an analog record performs linear conversions, breakpoint conversions,
or no conversions at all depends on how the record's `LINR` field is configured.
The possible choices for the `LINR` field are as follows:

  - LINEAR
  - SLOPE
  - NO CONVERSION
  - typeKdegF
  - typeKdegC
  - typeJdegF
  - typeJdegC

If either LINEAR or SLOPE is chosen, 
the record performs a linear conversion on the data.
If NO CONVERSION is chosen, the record performs no conversion on its data.
The other choices are the names of breakpoint tables.
When one of these is specified in the `LINR` field,
the record uses the specified table to convert its data. 

>**Note:**
> 
> Additional breakpoint tables are often added at specific sites,
> so more breakpoint tables than are listed here may be available
> at the user's site. 
  
The following sections explain linear and breakpoint conversions.


## Linear conversions

The engineering units full scale and low scale
are specified in the `EGUF` and `EGUL` fields, respectively.
The values of the `EGUF` and `EGUL` fields
correspond to the maximum and minimum values of the transducer, respectively.
Thus, the value of these fields is device dependent. 
For example, if the transducer has a range of –10 to +10 volts,
then the `EGUF` field should be 10 and the `EGUL` field should be -10.
In all cases, the `EGU` field is a string
that contains the text to indicate the units of the value.

The distinction between the LINEAR and SLOPE settings for the `LINR` field
are in how the conversion parameters are calculated:

With LINEAR conversion the user must set `EGUL` and `EGUF`
to the lowest and highest  possible engineering units values respectively
that can be converted by the hardware.
The device support knows the range of the raw data and calculates
`ESLO` and `EOFF` from them.

SLOPE conversion requires the user to calculate the appropriate scaling and
offset factors and put them directly in `ESLO` and `EOFF`.

When considering the linear conversion parameters,
there are three formulae to know.
The conversion from measured value to engineering units is as follows:

```{math}
\text{engunits} = \text{eng units low} + \frac{\text{ measured A/D counts}}{\text{full scale A/D counts}} * (\text{eng units full scale - eng units low})
```

In the following examples the determination of engineering units
full scale and low scale is shown.
The conversion to engineering units is
also shown to familiarize the reader with the signal conversions from
signal source to database engineering units.

### Transducer matches the I/O module

First consider a linear conversion. 
In this example, the  transducer transmits 0–10 Volts,
there is no amplification, and the I/O card uses a 0–10 Volt interface.

![Transducer matches the I/O module](media/dbconcepts/image6.png)

The transducer transmits pressure:
0 PSI at 0 Volts and 175 PSI at 10 Volts.
The engineering units full scale and low scale are determined as follows:

```{math}
eng. units full scale = 17.5 × 10.0  
eng. units low scale = 17.5 × 0.0
```

The field entries in an analog input record to convert this pressure
will be as follows:

`LINR`: Linear  
`EGUF`: 175.0  
`EGUL`: 0  
`EGU`: PSI

The conversion will also take into account the precision of the I/O module.
In this example (assuming a 12 bit analog input card)
the conversion is as follows:

```{math}
  \text{eng units} = 0 + \frac{\text{ measured A/D counts}}{4095} * (175 - 0)
```

When the pressure is 175 PSI, 10 Volts is sent to the I/O module.
At 10 Volts the signal is read as 4095.
When this is plugged into the conversion, the value is 175 PSI.

### Transducer lower than the I/O module

Consider a variation of this linear conversion where the transducer is 0–5 Volts.

![Transducer lower than the I/O module](media/dbconcepts/image7.png)

In this example the transducer is producing 0 Volts at 0 PSI
and 5 Volts at 175 PSI.
The engineering units full scale and low scale are determined as follows:

```{math}
eng. units low scale = 35 × 10 eng. units full scale = 35 × 0
```

The field entries in an analog record to convert this pressure
will be as follows:

`LINR`: Linear  
`EGUF`: 350  
`EGUL`: 0  
`EGU`: PSI

The conversion will also take into account the precision of the I/O module.
In this example (assuming a 12 bit analog input card)
the conversion is as follows:

```{math}
  \text{eng units} = 0 + \frac{\text{ measured A/D counts}}{4095} * (350 - 0)
```

Notice that at full scale,
the transducer will generate 5 Volts to represent 175 PSI.
This is only half of what the input card accepts;
input is 2048.

Plug in the numbers to see the result:

```{math}
  0 + (2048 / 4095) * (350 - 0) = 175
```

In this example we had to adjust the engineering units full scale
to compensate for the difference between the transmitter
and the analog input card.

### Transducer positive and I/O module bipolar


Consider another variation of this linear conversion,
where the input card accepts –10 Volts to 10 Volts
(that is, Bipolar instead of Unipolar).

![Transducer positive and I/O module bipolar](media/dbconcepts/image8.png)

In this example the transducer is producing 0 Volts at 0 PSI
and 10 Volts at 175 PSI.
The input module has a different range of voltages and
the engineering units full scale and low scale are determined as follows:

eng. units full scale = 17.5 × 10 eng. units low scale = 17.5 × (-10)

The database entries to convert this pressure will be as follows:

`LINR`: Linear  
`EGUF`: 175  
`EGUL`: -175  
`EGU`: PSI

The conversion will also take into account the precision of the I/O module.
In this example (assuming a 12 bit analog input card)
the conversion is as follows:

```{math}
  \text{eng units} = -175 + \frac{\text{ measured A/D counts}}{4095} * (175 - (-175))
```

Notice that at low scale the transducer will generate 0 Volts to represent 0 PSI.
Because this is half of what the input card accepts, it's input as 2048.
Let's plug in the numbers to see the result:
```{math}
  -175 + (2048 / 4095) * (175 - (-175)) = 0
```
In this example we had to adjust the engineering units low scale to
compensate for the difference between the unipolar transmitter and the
bipolar analog input card.

### Combining linear conversion with an amplifier

Consider another variation of this linear conversion
where the input card accepts –10 Volts to 10 Volts,
the transducer transmits 0–2 Volts for 0–175 PSI
and a 2x amplifier is on the transmitter.

![Combining linear conversion with an amplifier](media/dbconcepts/image9.png)

At 0 PSI the transducer transmits 0 Volts.
This is amplified to 0 Volts.
At half scale, it's read as 2048.
At 175 PSI, full scale, the transducer transmits 2 Volts,
which is amplified to 4 Volts.
The analog input card sees 4 Volts as 70 percent of range or 2867 counts.
The engineering units full scale and low scale are determined as follows:

eng units full scale = 43.75 × 10  
eng units low scale = 43.75 × (-10)  
(175 / 4 = 43.75) 

The record's field entries to convert this pressure will be as follows:

`LINR`: Linear  
`EGUF`: 437.5  
`EGUL`: -437.5  
`EGU`: PSI

The conversion will also take into account the precision of the I/O module.
In this example (assuming a 12 bit analog input card)
the conversion is as follows:

```{math}
  \text{eng units} = -437.5 + \frac{\text{ measured A/D counts}}{4095} * (437.5 - (-437.5))
```

Notice that at low scale the transducer will generate 0 Volts to represent 0 PSI.
Because this is half of what the input card accepts, it's input as 2048.
Let's plug in the numbers to see the result:

```{math}
  -437.5 + (2048 / 4095) * (437.5 - (-437.5)) = 0
```

Notice that at full scale the transducer will generate 2 volts
which represents 175 PSI.
The amplifier will change the 2 Volts to 4 Volts.
4 Volts is 14/20 or 70 percent of the I/O card's scale.
The input from the I/O card is therefore 2866 (that is, 0.7 \* 4095).
Let's plug in the numbers to see the result:

```{math}
  -437.5 + (2866 / 4095) * (437.5 - (-437.5)) = 175 PSI
```

We had to adjust the engineering units full scale
to adjust for the difference between the transducer with the amplifier effects
and the range of the I/O card.
We also adjusted the low scale to compensate for
the difference between the unipolar transmitter/amplifier
and the bipolar analog input card.

## Breakpoint conversions

Now let us consider a non-linear conversion.
These are conversions that could be entered as polynomials.
As these are more time-consuming to execute,
a breakpoint table is created that breaks the non-linear conversion
into linear segments that are accurate enough.

### Breakpoint Table

The breakpoint table is then used to do a piecewise linear conversion.
Each piecewise segment of the breakpoint table contains:

Raw Value Start for this segment, Engineering Units at the start.

```
     breaktable(typeJdegC) {
        0.000000 0.000000
        365.023224 67.000000
        1000.046448 178.000000
        3007.255859 524.000000
        3543.383789 613.000000
        4042.988281 692.000000
        4101.488281 701.000000
     }
```

### Breakpoint Conversion Example


When a new raw value is read,
the conversion routine starts from the previously used line segment,
compares the raw value start,
and either going forward or backward in the table searches the proper segment
for this new raw value.
Once the proper segment is found,
the new engineering units value
is the engineering units value at the start of this segment
plus the slope of this segment times the position on this segment.

  value = eng.units at segment start + (raw value - raw at segment start) * slope


A table that has an entry for each possible raw count
is effectively a lookup table.

Breakpoint tables are loaded to the IOC using the *dbLoadDatabase* shell function.
The slope corresponding to each segment is calculated when the table is loaded.
For raw values that exceed the last point in the breakpoint table,
the slope of the last segment is used.

In this example the transducer is a thermocouple which transmits 0–20 milliAmps.
An amplifier is present which amplifies milliAmps to volts.
The I/O card uses a 0–10 Volt interface and a 12-bit ADC.
Raw value range would thus be 0 to 4095.

![Breakpoint conversion example](media/dbconcepts/image10.png)

The transducer is transmitting temperature.
The database entries in the analog input record
that are needed to convert this temperature will be as follows:

`LINR`: typeJdegC  
`EGUF`: 0  
`EGUL`: 0  
`EGU`: DGC

For analog records that use breakpoint tables,
the `EGUF` and `EGUL` fields aren't used in the conversion,
so they don't have to be given values.

With this example setup and assuming we get an ADC raw reading of 3500,
the formula above would give:

```{math}
Value = 524.0 + (3500 - 3007) * 0.166 = 605.838 DGC
```

EPICS Base distribution currently includes lookup tables
for J and K thermocouples in degrees F and degrees C.

Other potential applications for a lookup table are,
for example, other types of thermocouples,
logarithmic output controllers,
and exponential transducers.
The piecewise linearisation of the signals provides a mechanism for conversion
that minimizes the amount of floating point arithmetic required
to convert non-linear signals.
Additional breakpoint tables can be added to the predefined ones.

### Creating breakpoint tables

New breakpoint tables can be created in two ways:

1) Type in the data for each segment,
giving the raw and corresponding engineering unit value for each point
in the following format.

```
  breaktable(<tablename>) {
    <first point> <first eng units>
    <next point> <next eng units>
    <etc.> <...>
  }
```

where the `<tablename>` is the name of the table, such as typeKdegC,
and `<first point>` is the raw value of the beginning point for each line segment,
and `<first eng units>` is the corresponding engineering unit value.
The slope is calculated by the software and shouldn't be specified.

2) Create a file consisting of a table
of an arbitrary number of values in engineering units
and use the utility called **makeBpt** 
to convert the table into a breakpoint table.
As an example,
the contents data file to create the typeJdegC breakpoint table look like this:

```
  !header
  "typeJdegC" 0 0 700 4095 .5 -210 760 1
  !data
  -8.096 -8.076 -8.057 <many more numbers>
```

The file name must have the extension .data.
The file must first have a header specifying these nine things:

1. Name of breakpoint table in quotes: **"typeJdegC"**
2. Engineering units for 1st breakpoint table entry: **0**
3. Raw value for 1st breakpoint table entry: **0**
4. Highest value desired in engineering units: **700**
5. Raw value corresponding to high value in engineering units: **4095**
6. Allowed error in engineering units: **.5**
7. Engineering units corresponding to first entry in data table: **-210**
8. Engineering units corresponding to last entry in data table: **760**
9. Change in engineering units between data table entries: **1**

The rest of the file contains lines of equally spaced engineering values,
with each line no more than 160 characters before the new-line character.
The header and the actual table should be specified
by **!header** and **!data**, respectively.
The file for this data table is called typeJdegC.data,
and can be converted to a breakpoint table with the **makeBpt** utility as follows:

```
unix% makeBpt typeJdegC.data
```