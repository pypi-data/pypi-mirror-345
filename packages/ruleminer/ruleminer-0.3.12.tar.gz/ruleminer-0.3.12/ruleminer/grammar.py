"""Parser module."""

import pyparsing

# a class-level static method to enable a memorizing performance enhancement
pyparsing.ParserElement.enable_packrat()

# _lpar, _rpar = map(pyparsing.Suppress, "()")
# _lbra, _rbra = map(pyparsing.Suppress, "[]")
_lpar = pyparsing.Literal("(")
_rpar = pyparsing.Literal(")")
_lbra = pyparsing.Literal("[")
_rbra = pyparsing.Literal("]")
_sep = pyparsing.Literal(",")
_number = pyparsing.Regex(r"[+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?")
_timedate_functions = pyparsing.one_of(
    "day_name \
    month_name \
    days_in_month \
    daysinmonth \
    is_leap_year \
    is_year_end \
    dayofweek \
    weekofyear \
    weekday \
    week \
    is_month_end \
    is_month_start \
    is_year_start \
    is_quarter_end \
    is_quarter_start \
    day \
    month \
    quarter \
    year \
    DAY_NAME \
    MONTH_NAME \
    DAYS_IN_MONTH \
    DAYSINMONTH \
    IS_LEAP_YEAR \
    IS_YEAR_END \
    DAYOFWEEK \
    WEEKOFYEAR \
    WEEKDAY \
    WEEK \
    IS_MONTH_END \
    IS_MONTH_START \
    IS_YEAR_START \
    IS_QUARTER_END \
    IS_QUARTER_START \
    DAY \
    MONTH \
    QUARTER \
    YEAR"
)
_timedelta_functions = pyparsing.one_of(
    "days \
    DAYS \
    months \
    MONTHS \
    years \
    YEARS"
)

_function = (
    pyparsing.one_of(
        "min \
    max \
    abs \
    quantile \
    sum \
    substr \
    split \
    count \
    sumif \
    countif \
    mean \
    std \
    exact \
    corr \
    round \
    floor \
    ceil \
    table \
    MIN \
    MAX \
    ABS \
    QUANTILE \
    SUM \
    SUBSTR \
    SPLIT \
    COUNT \
    SUMIF \
    COUNTIF \
    MEAN \
    STD \
    EXACT \
    CORR \
    ROUND \
    FLOOR \
    CEIL \
    TABLE"
    )
    | _timedelta_functions
    | _timedate_functions
)
_for = pyparsing.one_of("for", "FOR")
_in = pyparsing.one_of("in", "IN")
_empty = pyparsing.one_of(["None", '""', "pd.NA", "np.nan"])
_list_comprehension_var = pyparsing.Word(pyparsing.alphas)
_quote = pyparsing.Literal('"')
_string = (
    pyparsing.srange(r"[a-zA-Z0-9_.,:;<>*=+-/?|@#$%^&\[\]{}\(\)\\']")
    + " "
    + "\x01"
    + "\x02"
    + "\x03"
    # + pyparsing.pyparsing_unicode.Greek.alphas
    # + pyparsing.pyparsing_unicode.Greek.alphanums
)
_quoted_string = pyparsing.Combine(_quote + pyparsing.Word(_string) + _quote)
_column = pyparsing.Combine("{" + _quote + pyparsing.Word(_string) + _quote + "}")
_addop = pyparsing.Literal("+") | pyparsing.Literal("-")
_multop = pyparsing.Literal("*") | pyparsing.Literal("/")
_expop = pyparsing.Literal("**")
_compa_op = (
    pyparsing.one_of(
        ">= > <= < != == in IN between BETWEEN match MATCH contains CONTAINS"
    )
    | pyparsing.Literal("not in")
    | pyparsing.Literal("NOT IN")
    | pyparsing.Literal("not between")
    | pyparsing.Literal("NOT BETWEEN")
    | pyparsing.Literal("not match")
    | pyparsing.Literal("NOT MATCH")
    | pyparsing.Literal("not contains")
    | pyparsing.Literal("NOT CONTAINS")
)

_list = pyparsing.Forward()
_list <<= pyparsing.Group(
    _lbra
    + (_quoted_string | _column | _number | _empty)
    + (_sep + (_quoted_string | _column | _number | _empty))[0, ...]
    + _rbra
)

_base_element = (
    _quoted_string | _column | _number | _empty | _list | _list_comprehension_var
)
################################################################################
# definition of a super simple math expression
################################################################################
# first look for simple function expression then look for base element
# (do not change order because then only the function name is parsed and not the rest)
base_element_math_expression = pyparsing.Forward()
_base_element_math_atom = _base_element | pyparsing.Group(
    _lpar + base_element_math_expression + _rpar
)
_base_element_math_factor = pyparsing.Forward()
# if expression contains ** then put parentheses around this part
_base_element_math_factor <<= (
    pyparsing.Group(
        _base_element_math_atom + (_expop + _base_element_math_factor)[1, ...]
    )
    | _base_element_math_atom
)
# if expression contains * or / then put parentheses around this part
_base_element_math_term = (
    pyparsing.Group(
        _base_element_math_factor + (_multop + _base_element_math_factor)[1, ...]
    )
    | _base_element_math_factor
)
base_element_math_expression <<= (
    _base_element_math_term + (_addop + _base_element_math_term)[...]
)

################################################################################
# definition of a simple function expression
################################################################################
_params = _base_element + (_sep + _base_element)[...]
simple_function_expression = pyparsing.Group(
    _function + pyparsing.Group(_lpar + _params + _rpar)
)

################################################################################
# definition of a simple math expression
################################################################################
# first look for simple function expression then look for base element
# (do not change order because then only the function name is parsed and not the rest)
simple_math_expression = pyparsing.Forward()
_simple_math_element = (
    simple_function_expression | _base_element | base_element_math_expression
)
_simple_math_atom = _simple_math_element | pyparsing.Group(
    _lpar + simple_math_expression + _rpar
)
_simple_math_factor = pyparsing.Forward()
# if expression contains ** then put parentheses around this part
_simple_math_factor <<= (
    pyparsing.Group(_simple_math_atom + (_expop + _simple_math_factor)[1, ...])
    | _simple_math_atom
)
# if expression contains * or / then put parentheses around this part
_simple_math_term = (
    pyparsing.Group(_simple_math_factor + (_multop + _simple_math_factor)[1, ...])
    | _simple_math_factor
)
simple_math_expression <<= _simple_math_term + (_addop + _simple_math_term)[...]

################################################################################
# definition of a simple condition expression
################################################################################
simple_condition_expression = pyparsing.infixNotation(
    (simple_math_expression + _compa_op + simple_math_expression),
    [
        (
            pyparsing.one_of(["NOT", "not", "~"]),
            1,
            pyparsing.opAssoc.RIGHT,
        ),
        (
            pyparsing.one_of(["AND", "and", "&"]),
            2,
            pyparsing.opAssoc.LEFT,
        ),
        (
            pyparsing.one_of(["OR", "or", "|"]),
            2,
            pyparsing.opAssoc.LEFT,
        ),
    ],
    lpar=pyparsing.Literal("("),
    rpar=pyparsing.Literal(")"),
)

################################################################################
# definition of a list expression
################################################################################
list_expression = pyparsing.Group(
    _lbra
    + pyparsing.Group(simple_math_expression)
    + (_sep + pyparsing.Group(simple_math_expression))[...]
    + _rbra
)

################################################################################
# definition of a list_comprehension expression
################################################################################
list_comprehension_expression = pyparsing.Group(
    _lbra
    + pyparsing.Group(simple_condition_expression | simple_math_expression)
    + _for
    + _list_comprehension_var
    + _in
    + (_lbra + _column + (_sep + _column)[...] + _rbra)
    + _rbra
)

################################################################################
# definition of a function_expression
################################################################################
_function_param = (
    simple_condition_expression | simple_math_expression | list_comprehension_expression
)
_function_params = _function_param + (_sep + _function_param)[...]
function_expression = pyparsing.Group(
    _function + pyparsing.Group(_lpar + _function_params + _rpar)
)
# the following is to allow an additional exact-function around a function
exact_function_expression = pyparsing.Group(
    pyparsing.one_of("EXACT exact")
    + pyparsing.Group(_lpar + function_expression + _rpar)
)

################################################################################
# definition of a math_expression
################################################################################
math_expression = pyparsing.Forward()
_math_element = (
    exact_function_expression
    | function_expression
    | simple_math_expression
    | list_expression
)
_math_atom = _math_element | pyparsing.Group(_lpar + math_expression + _rpar)
_math_factor = pyparsing.Forward()
# if expression contains ** then put parentheses around this part
_math_factor <<= (
    pyparsing.Group(_math_atom + (_expop + _math_factor)[1, ...]) | _math_atom
)
# if expression contains * or / then put parentheses around this part
_math_term = (
    pyparsing.Group(_math_factor + (_multop + _math_factor)[1, ...]) | _math_factor
)
math_expression <<= _math_term + (_addop + _math_term)[...]

################################################################################
# definition of a condition_expression
################################################################################
condition_expression = pyparsing.infixNotation(
    pyparsing.Group(_lpar + (math_expression + _compa_op + math_expression) + _rpar),
    [
        (
            pyparsing.one_of(["NOT", "not", "~"]),
            1,
            pyparsing.opAssoc.RIGHT,
        ),
        (
            pyparsing.one_of(["AND", "and", "&"]),
            2,
            pyparsing.opAssoc.LEFT,
        ),
        (
            pyparsing.one_of(["OR", "or", "|"]),
            2,
            pyparsing.opAssoc.LEFT,
        ),
    ],
    lpar=pyparsing.Literal("("),
    rpar=pyparsing.Literal(")"),
)

################################################################################
# definition of a rule expression
################################################################################
_if_then = (
    "if" + condition_expression + "then" + condition_expression
    | "IF" + condition_expression + "THEN" + condition_expression
)
rule_expression = (
    _if_then
    | "if () then " + condition_expression
    | "IF () THEN " + condition_expression
    | condition_expression
)
