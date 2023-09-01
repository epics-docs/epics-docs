# Alarm Specification

There are two elements to an alarm condition:
the alarm *status* and the *severity* of that alarm.
Each database record contains its current alarm status
and the corresponding severity for that status.
The scan task, which detects these alarms,
is also capable of generating a message for each change of alarm state.
The types of alarms available fall into these categories:
scan alarms, read/write alarms, limit alarms, and state alarms.
Some of these alarms are configured by the user,
and some are automatic which means that they are called
by the record support routines on certain conditions,
and cannot be changed orconfigured by the user.

## Alarm Severity

An alarm *severity* is used to give weight to the current alarm status.
There are four severities:

  - NO_ALARM
  - MINOR
  - MAJOR
  - INVALID

NO_ALARM means no alarm has been triggered.
An alarm state that needs attention but is not dangerous is a MINOR alarm.
In this instance the alarm state is meant to give a warning to the operator.
A serious state is a MAJOR alarm.
In this instance the operator should give immediate attention to the situation 
and take corrective action.
An INVALID alarm means there's a problem with the data,
which can be any one of several problems;
for instance, a bad address specification, device communication failure,
or signal is over range.
In these cases, an alarm severity of INVALID is set.
An INVALID alarm can point to a simple configuration problem
or a serious operational problem.

For limit alarms and state alarms,
the severity can be configured by the user
to be MAJOR or MINOR for the specified state.
For instance, an analog record can be configured to trigger a MAJOR alarm
when its value exceeds 175.0.
In addition to the MAJOR and MINOR severity,
the user can choose the NO_ALARM severity,
in which case no alarm is generated for that state.

For the other alarm types (i.e., scan, read/write),
the severity is always INVALID and not configurable by the user.

## Alarm Status

Alarm status is a field common to all records.
The field is defined as an enumerated field.
The possible states are listed below.

   - NO_ALARM: This record is not in alarm
   - READ: An INPUT link failed in the device support
   - WRITE: An OUTPUT link failed in the device support
   - HIHI: An analog value limit alarm
   - HIGH: An analog value limit alarm
   - LOLO: An analog value limit alarm
   - LOW: An analog value limit alarm
   - STATE: An digital value state alarm
   - COS: An digital value change of state alarm
   - COMM: A device support alarm that indicates the device is not communicating
   - TIMEOUT: A device sup alarm that indicates the asynchronous device timed out
   - HWLIMIT: A device sup alarm that indicates a hardware limit alarm
   - CALC: A record support alarm for calculation records indicating a bad calculation
   - SCAN: An invalid SCAN field is entered
   - LINK: Soft device support for a link failed:no record, bad field, invalid conversion, INVALID alarm severity on the referenced record.
   - SOFT
   - BAD_SUB
   - UDF
   - DISABLE
   - SIMM
   - READ_ACCESS
   - WRITE_ACCESS

There are a number of issues with this field and menu.

-  The maximum enumerated strings passed through channel access is 16,
   so nothing past SOFT is seen if the value is not requested by Channel Access
   as a string.

-  Only one state can be true at a time,
   meaning the root cause of a problem or multiple problems may be masked.
   This is particularly obvious in the interface between the record support
   and the device support.
   The hardware could have some combination of problems and there is no
   way to see this through the interface provided.

-  The list is not complete.

-  In short, the ability to see failures through the `STAT` field are limited.
   Most problems in the hardware, configuration, or communication
   are reduced to READ or WRITE error and have their severity set to INVALID.
   When you have an INVALID alarm severity,
   some investigation is currently needed to determine the fault.
   Most EPICS drivers provide a report routine that dumps a large set of
   diagnostic information.
   This is a good place to start in these cases.

## Alarm Conditions Configured in the Database

When you have a valid value,
there are fields in the record that allow the user
to configure off normal-conditions.
For analog values these are limit alarms.
For discrete values, these are state alarms.

### Limit Alarms

For analog records 
(this includes such records as the stepper motor record),
there are configurable alarm limits.
There are two limits for above normal operating range
and two limits for the below-limit operating range.
Each of these limits has an associated alarm severity,
which is configured in the database.
If the record's value drops below the low limit
and an alarm severity of MAJOR was specified for that limit,
then a MAJOR alarm is triggered.
When the severity of a limit is set to NO_ALARM,
none will be generated,
even if the limit entered has been violated.

There are two limits at each end,
two low values and two high values,
so that a warning can be set off before the value goes into a dangerous condition.

Analog records also contain a hysteresis field,
which is also used when determining limit violations.
The hysteresis field is the deadband around the alarm limits.
The deadband keeps a signal that is hovering at the limit
from generating too many alarms.
Let's take an example (*Figure 1*) where the range is –100 to 100 volts,
the high alarm limit is 30 Volts, and the hysteresis is 10 Volts.
If the value is normal and approaches the HIGH alarm limit,
an alarm is generated when the value reaches 30 Volts.
This will only go to normal if the value drops below the limit
by more than the hysteresis.
For instance, if the value changes from 30 to 28
this record will remain in HIGH alarm.
Only when the value drops to 20 will this record return to normal state.

![Figure 1](media/dbconcepts/image11.png)
**Figure 1**

### State Alarms

For discrete values there are configurable state alarms.
In this case a user may configure a certain state to be an alarm condition.
Consider a cooling fan whose discrete states are high, low, and off.
The off state can be configured to be an alarm condition
so that whenever the fan is off the record is in a STATE alarm.
The severity of this error is configured for each state.
In this example, the low state could be a STATE alarm of MINOR severity,
and the off state a STATE alarm of MAJOR severity.

Discrete records also have a field
in which the user can specify the severity of an unknown state
to NO_ALARM, MINOR or MAJOR.
Thus, the unknown state alarm is not automatic.

Discrete records also have a field,
which can specify an alarm when the record's state changes.
Thus, an operator can know when the record's alarm state has changed.
If this field specifies NO_ALARM,
then a change of state will not trigger a change of state alarm.
However, if it specifies either MINOR or MAJOR,
a change of state will trigger an alarm with the corresponding severity.

## Alarm Handling

A record handles alarms with the `NSEV`, `NSTA`, `SEVR`, and `STAT` fields.
When  a software component wants to raise an alarm,
it first checks the new alarm state fields:
`NSTA`, new alarm state, and `NSEV`, new alarm severity.
If the severity in the `NSEV` field
is higher than the severity in the  current severity field (`SEVR`),
then the software component sets the `NSTA` and `NSEV` fields
to the severity and alarm state that corresponds to the outstanding alarm.
When the record process routine next processes the record,
it sets the current alarm state (`STAT`) and current severity (`SEVR`)
to the values in the `NSEV` and `NSTA` fields.

This method of handling alarms ensures that the current severity (`STAT`)
reflects the highest severity of outstanding alarm conditions
instead of simply the last raised alarm.
This also means that the if multiple alarms of equal severity are present,
the alarm status indicates the first one detected.

In addition, the get_alarm_double() routine can be called
to format an alarm message and send it to an alarm handler.
The alarm conditions may be monitored by the operator interface
by explicitly monitoring the `STAT` and `SEVR` fields.
All values monitored by the operator interface
are returned from the database access with current status information.
