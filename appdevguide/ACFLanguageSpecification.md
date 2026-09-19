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

The grammar is given below as a set of production rules. In EBNF terms,
`[ ... ]` denotes an optional element, `{ ... }` denotes zero or more
repetitions, and alternatives are listed on separate lines. Literal terminals
are shown in double quotes. References to other rules are hyperlinked.

For writing an ACF file, start from the {token}`acf_file` rule.

## Top level

```{eval-rst}
.. productionlist::
   acf_file: `asconfig`
   asconfig: `asconfig_item` { `asconfig_item` }
   asconfig_item: `uag_def`
                : `hag_def`
                : `asg_def`
                : `generic_top_level_item`
```

### UAG / HAG groups

```{eval-rst}
.. productionlist::
   uag_def: "UAG" `uag_head` [ `uag_body` ]
   uag_head: "(" STRING ")"
   uag_body: "{" `uag_user_list` "}"
   uag_user_list: STRING { "," STRING }
   hag_def: "HAG" `hag_head` [ `hag_body` ]
   hag_head: "(" STRING ")"
   hag_body: "{" `hag_host_list` "}"
   hag_host_list: STRING { "," STRING }
```

### ASG (access security group)

```{eval-rst}
.. productionlist::
   asg_def: "ASG" `asg_head` [ `asg_body` ]
   asg_head: "(" STRING ")"
   asg_body: "{" `asg_body_item` { `asg_body_item` } "}"
   asg_body_item: `inp_config`
                : `rule_config`
```

#### INP config

```{eval-rst}
.. productionlist::
   inp_config: INP(link) "(" STRING ")"
```

#### RULE config

```{eval-rst}
.. productionlist::
   rule_config: "RULE" `rule_head` [ `rule_body` ]
   rule_head: "(" `rule_head_mandatory` "," `rule_log_option` ")"
            : "(" `rule_head_mandatory` ")"
   rule_head_mandatory: INT "," STRING
   rule_log_option: STRING
   rule_body: "{" `rule_list` "}"
   rule_list: `rule_list_item` { `rule_list_item` }
   rule_list_item: "UAG" "(" `rule_uag_list` ")"
                 : "HAG" "(" `rule_hag_list` ")"
                 : "CALC" "(" STRING ")"
                 : `rule_generic_block_elem`
   rule_uag_list: STRING { "," STRING }
   rule_hag_list: STRING { "," STRING }
```

### Generic / future-proof syntax

These are the "catch-all" constructs that are **parsed** but currently **ignored** semantically.

#### Keyword classes

These are parser-level categories used inside generic constructs:

```{eval-rst}
.. productionlist::
   keyword: "UAG"
          : "HAG"
          : "CALC"
          : `non_rule_keyword`
   non_rule_keyword: "ASG"
                   : "RULE"
                   : INP(link)
```

`INP(link)` above stands for the `INPA` .. `INPU` link terminals.

#### Generic head (argument list)

```{eval-rst}
.. productionlist::
   generic_head: "(" ")"
               : "(" `generic_element` ")"
               : "(" `generic_list` ")"
   generic_list: `generic_element` "," `generic_element` { "," `generic_element` }
   generic_element: `keyword`
                  : STRING
                  : INT
                  : FLOAT
```

#### Generic blocks

```{eval-rst}
.. productionlist::
   generic_block: "{" `generic_element` "}"
                : "{" `generic_list` "}"
                : "{" `generic_block_list` "}"
   generic_block_list: `generic_block_elem` { `generic_block_elem` }
   generic_block_elem: `generic_block_elem_name` `generic_head` [ `generic_block` ]
   generic_block_elem_name: `keyword`
                          : STRING
```

#### Generic top-level items

These are "unknown" top-level constructs, all of which are parsed and then ignored with a warning.

```{eval-rst}
.. productionlist::
   generic_top_level_item: STRING `generic_head` `generic_list_block`
                         : STRING `generic_head` `generic_block`
                         : STRING `generic_head`
   generic_list_block: "{" `generic_element` "}" "{" `generic_list` "}"
```

#### Generic blocks inside RULE bodies

These are the "future predicates" in a RULE's body; they cause the RULE to be disabled with a warning, but they **must** still parse.

```{eval-rst}
.. productionlist::
   rule_generic_block_elem: `rule_generic_block_elem_name` `generic_head` [ `generic_block` ]
   rule_generic_block_elem_name: `non_rule_keyword`
                               : STRING
```
