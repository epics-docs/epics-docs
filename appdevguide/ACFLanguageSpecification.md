# ACF Full Language Specification:

## Lexical tokens

**Ignored stuff**

-   *Whitespace*: space, tab, `\r` (carriage return) -- may appear between tokens.

-   *Newlines*: `\n` -- same as whitespace for syntax, but tracked for error messages.

-   *Comments*: `#` ... end of line -- ignored.

**Terminals**

-   `UAG` → literal string `"UAG"`
-   `HAG` → `"HAG"`
-   `ASG` → `"ASG"`
-   `RULE` → `"RULE"`
-   `CALC` → `"CALC"`
-   `INP(link)` → literal `"INP"` followed immediately by one uppercase letter `A`-`U`
```text
    link-letter  ::= "A" | "B" | ... | "U"
    INP(link)    ::= "INP" link-letter
```
-   `INT` → integer literal

```text
    INT ::= [ "+" | "-" ]? DIGIT+
    DIGIT ::= "0" | "1" | ... | "9"
```
-   `FLOAT` → floating-point literal with decimal point
```text
    FLOAT ::= [ "+" | "-" ]? DIGIT* "." DIGIT+ [ ( "e" | "E" ) [ "+" | "-" ] DIGIT+ ]?
```
-   `STRING` → either
    -   **unquoted**: one or more of
```text
        NAMECHAR ::= letter | digit | "_" | "-" | "+" | ":" | "." | "[" | "]" | "<" | ">" | ";"
        STRING(unquoted) ::= NAMECHAR+
```
-   -   **quoted**:
```text
        STRING(quoted) ::= '"' { STRINGCHAR | ESCAPE } '"'
        STRINGCHAR     ::= any char except '"' "\" "\n"
        ESCAPE         ::= "\" any-char
```
        The surrounding quotes are stripped; escapes are kept literal at parse level.
-   Punctuation tokens (single-character terminals):
```text
    "("  ")"  "{"  "}"  ","
```
---

# Grammar

## Top level

```ebnf
acf-file ::= asconfig ;

asconfig ::= asconfig-item { asconfig-item } ;

asconfig-item ::=
      uag-def
    | hag-def
    | asg-def
    | generic-top-level-item ;
```
### UAG / HAG groups

```ebnf
uag-def ::= "UAG" uag-head [ uag-body ] ;

uag-head ::= "(" STRING ")" ;

uag-body ::= "{" uag-user-list "}" ;

uag-user-list ::= STRING { "," STRING } ;
```

```ebnf
hag-def ::= "HAG" hag-head [ hag-body ] ;

hag-head ::= "(" STRING ")" ;

hag-body ::= "{" hag-host-list "}" ;

hag-host-list ::= STRING { "," STRING } ;
```

### ASG (access security group)

```ebnf
asg-def ::= "ASG" asg-head [ asg-body ] ;

asg-head ::= "(" STRING ")" ;

asg-body ::= "{" asg-body-item { asg-body-item } "}" ;

asg-body-item ::=
      inp-config
    | rule-config ;
```

#### INP config

```ebnf
inp-config ::= INP(link) "(" STRING ")" ;`
```

#### RULE config
```ebnf
rule-config ::= "RULE" rule-head [ rule-body ] ;

rule-head ::=
      "(" rule-head-mandatory "," rule-log-option ")"
    | "(" rule-head-mandatory ")" ;

rule-head-mandatory ::= INT "," STRING ;

rule-log-option ::= STRING ;
```
```ebnf
rule-body ::= "{" rule-list "}" ;

rule-list ::= rule-list-item { rule-list-item } ;

rule-list-item ::=
      "UAG" "(" rule-uag-list ")"
    | "HAG" "(" rule-hag-list ")"
    | "CALC" "(" STRING ")"
    | rule-generic-block-elem ;
```

```ebnf
rule-uag-list ::= STRING { "," STRING } ;

rule-hag-list ::= STRING { "," STRING } ;`
```

### Generic / future-proof syntax

These are the "catch-all" constructs that are **parsed** but currently **ignored** semantically.

#### Keyword classes

These are parser-level categories used inside generic constructs:
```ebnf
keyword ::=
      "UAG"
    | "HAG"
    | "CALC"
    | non-rule-keyword ;

non-rule-keyword ::=
      "ASG"
    | "RULE"
    | INP(link) ;   (* INPA..INPU *)
```
#### Generic head (argument list)

```ebnf
generic-head ::=
      "(" ")"
    | "(" generic-element ")"
    | "(" generic-list ")" ;

generic-list ::= generic-element "," generic-element { "," generic-element } ;

generic-element ::=
      keyword
    | STRING
    | INT
    | FLOAT ;
```
#### Generic blocks

```ebnf
generic-block ::=
      "{" generic-element "}"
    | "{" generic-list "}"
    | "{" generic-block-list "}" ;

generic-block-list ::= generic-block-elem { generic-block-elem } ;

generic-block-elem ::=
    generic-block-elem-name generic-head [ generic-block ] ;

generic-block-elem-name ::= keyword | STRING ;`
```
#### Generic top-level items

These are "unknown" top-level constructs, all of which are parsed and then ignored with a warning.
```ebnf
generic-top-level-item ::=
      STRING generic-head generic-list-block
    | STRING generic-head generic-block
    | STRING generic-head ;
```
where
```ebnf
generic-list-block ::=
    "{" generic-element "}" "{" generic-list "}" ;
```
#### Generic blocks inside RULE bodies

These are the "future predicates" in a RULE's body; they cause the RULE to be disabled with a warning, but they **must** still parse.

```ebnf
rule-generic-block-elem ::=
    rule-generic-block-elem-name generic-head [ generic-block ] ;

rule-generic-block-elem-name ::= non-rule-keyword | STRING ;
```
