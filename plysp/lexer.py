import ply.lex as lex

# The core language as defined in clojure
#
# DEF = Symbol.intern("def");
# LOOP = Symbol.intern("loop*");
# RECUR = Symbol.intern("recur");
# IF = Symbol.intern("if");
# LET = Symbol.intern("let*");
# LETFN = Symbol.intern("letfn*");
# DO = Symbol.intern("do");
# FN = Symbol.intern("fn*");
# FNONCE = (Symbol) Symbol.intern("fn*").withMeta(
#                          RT.map(Keyword.intern(null, "once"), RT.T));
# QUOTE = Symbol.intern("quote");
# THE_VAR = Symbol.intern("var");
# DOT = Symbol.intern(".");
# ASSIGN = Symbol.intern("set!");
# TRY = Symbol.intern("try");
# CATCH = Symbol.intern("catch");
# FINALLY = Symbol.intern("finally");
# THROW = Symbol.intern("throw");
# MONITOR_ENTER = Symbol.intern("monitor-enter");
# MONITOR_EXIT = Symbol.intern("monitor-exit");
# IMPORT = Symbol.intern("clojure.core", "import*");
# INSTANCE = Symbol.intern("instance?");
# DEFTYPE = Symbol.intern("deftype*");
# CASE = Symbol.intern("case*");

# CLASS = Symbol.intern("Class");
# NEW = Symbol.intern("new");
# THIS = Symbol.intern("this");
# REIFY = Symbol.intern("reify*");
# LIST = Symbol.intern("clojure.core", "list");
# HASHMAP = Symbol.intern("clojure.core", "hash-map");
# VECTOR = Symbol.intern("clojure.core", "vector");
# IDENTITY = Symbol.intern("clojure.core", "identity");

# _AMP_ = Symbol.intern("&");
# ISEQ = Symbol.intern("clojure.lang.ISeq");

# loadNs = Keyword.intern(null, "load-ns");
# inlineKey = Keyword.intern(null, "inline");
# inlineAritiesKey = Keyword.intern(null, "inline-arities");
# staticKey = Keyword.intern(null, "static");
# arglistsKey = Keyword.intern(null, "arglists");
# INVOKE_STATIC = Symbol.intern("invokeStatic");

# NS = Symbol.intern("ns");
# IN_NS = Symbol.intern("in-ns");


class PlyspLex(object):
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer

    reserved = {"nil": "NIL"}

    tokens = [
        "ATOM",
        "NM_SYM",
        "KEYWORD",
        "IF",
        "DEF",
        "NS",
        "IN_NS",
        "IMPORT",
        "REFER",
        "REQUIRE",
        "AS",
        "PATH",
        "NEW",
        "LSETBRACE",
        # 'LIGNOREFORM',
        "STRING",
        "DOT",
        "FLOAT",
        "INTEGER",
        "NUMBER",
        "READMACRO",  # going away soon...
        "DEREF_SYM",
        "DEREF",
        "QUOTE_SYM",
        "QUOTE",
        "UNQUOTE_SYM",
        "UNQUOTE",
        "SYNTAX_QUOTE_SYM",
        "SYNTAX_QUOTE",
        "UNQUOTE_SPLICING_SYM",
        "UNQUOTE_SPLICING",
        "REGEX",
        "VAR_QUOTE",
        "VAR",
        "AUTO_GENSYM",
        "GENSYM",
        "UUID",
        "INST",
        "DISCARD",
        "FN",
        "INLINE_FN",
        "ANONYMOUS_ARG",
        "LET",
        "OCTAL",
        "HEX",
        "BASE2",
        "CHAR",
        "UNICODE_CHAR",
        "OCTAL_CHAR",
        "LBRACKET",
        "RBRACKET",
        "LBRACE",
        "RBRACE",
        "LPAREN",
        "RPAREN",
    ] + list(reserved.values())

    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_ignore = " ,\t\r"
    t_ignore_COMMENT = r"\;.*"

    # The next set of symbols to do.

    # #  leading #
    # t_discard = r'\#_'
    # t_inline_fn = r'\#\('

    # #'somevar or (var somevar)  returns reference to somevar.
    # t_var_quote = r"\#\'"
    # t_var     = r"var"

    # t_uuid= r'\#uuid'
    # t_inst = r'\#inst'

    # # trailing # is gensym.
    # t_auto_gensym = r'[\*\+\!\-\_a-zA-Z_-]+#'
    # t_gensym = r"gensym"

    # # args for anonymous functions.
    # t_anonymous_arg = "\%[0-9]*"

    # # quote, unquote, unquote splicing, syntax_quote.
    # t_deref_sym = r'@[\*\+\!\-\_a-zA-Z_-]+'
    # t_deref = r'deref'
    # t_quote_sym = r"\'"
    # t_quote = r"quote"
    # t_unquote_sym = r"\~"
    # t_unquote = r"unquote"
    # t_syntax_quote_sym = r"\`"
    # t_syntax_quote = r"syntax_quote"
    # t_unquote_splicing_sym = r"\~@"
    # t_unquote_splicing = r"unquote_splicing"

    # t_octal = r"0[0-7]{2}"
    # t_hex   = r"0x[A-F0-9]{2,4}"
    # t_base2 = r"2r[0,1]{4}"  # perhaps better to match [0-3]*[0-9]*r<number>.
    #                          # .. 0-36r really.
    #                          # base 36 uses the alphabet entire.

    def t_KEYWORD(self, t):
        r"\:[a-zA-Z_-]+"
        t.value = t.value[1:]
        return t

    def t_REGEX(self, t):
        r"\#\"(\\.|[^\"])*\""
        t.value = t.value[2:-1]
        return t

    def t_STRING(self, t):
        r"\"(\\.|[^\"])*\""
        t.value = t.value[1:-1]
        return t

    def t_UNICODE_CHAR(self, t):
        r"\\u[A-F0-9]{4}"
        t.value = t.value[2:]
        return t

    def t_OCTAL_CHAR(self, t):
        r"\0[0-7]{3}"
        t.value = t.value[1:]
        return t

    def t_CHAR(self, t):
        r"\\(newline|space|tab|formfeed|backspace|return|\\[nstfbr]+|.)"
        t.value = t.value[1:]
        return t

    def t_NUMBER(self, t):
        r"[+-]?((\d+(\.\d+)?([eE][+-]?\d+)?)|(\.\d+([eE][+-]?\d+)?))"
        val = t.value
        if "." in val or "e" in val.lower():
            t.type = "FLOAT"
        else:
            t.type = "INTEGER"
        return t

    def t_NS(self, t):
        r"ns"
        return t

    def t_IN_NS(self, t):
        r"in-ns"
        return t

    def t_IMPORT(self, t):
        r"import"
        return t

    def t_REFER(self, t):
        r"refer"
        return t

    def t_REQUIRE(self, t):
        r"require"
        return t

    def t_AS(self, t):
        r"as"
        return t

    def t_DEF(self, t):
        r"def"
        return t

    def t_IF(self, t):
        r"if"
        return t

    def t_LET(self, t):
        r"let\*"
        return t

    def t_DO(self, t):
        r"do"
        return t

    def t_LETFN(self, t):
        r"letfn\*"
        return t

    def t_FN(self, t):
        r"fn"
        return t

    def t_LOOP(self, t):
        r"loop\*"
        return t

    def t_RECUR(self, t):
        r"recur"
        return t

    def t_NEW(self, t):
        r"new"
        return t

    # # -foo.bar.baz  -foo.bar -foo etc.
    # def t_PYATTR(self, t):
    #     r"(\.\-(([-_A-Za-z0-9]+(\/[-_A-Za-z0-9]+)*)||([-[_A-Za-z0-9]+])))"
    #     return t

    # # foo.bar, foo.bar.baz
    # def t_PYPATH(self, t):
    #     r'[-_A-Za-z0-9]+(\.[-_A-Za-z0-9\.]+)+'
    #     return t

    # # foo.bar.baz.  foo.bar. foo. etc.
    # def t_PYCLASS(self, t):
    #     r'([-_A-Za-z0-9]+)\.'
    #     return t

    # def t_NM_SYM(self, t):
    #     r"[-\?\=\.+\*\+\!_a-zA-Z0-9<>]+"
    #     t.type = self.reserved.get(t.value, "NM_SYM")
    #     return t

    def t_ATOM(self, t):
        r"[-\?\=\/\*\+\!_a-zA-Z0-9<>]+"
        t.type = self.reserved.get(t.value, "ATOM")
        return t

    def t_DOT(self, t):
        r"\."
        return t

    # because tokens are added after the functions and
    # this needs to happen before readmacro.
    def t_LSETBRACE(self, t):
        r"\#\{"
        return t

    # def t_SLASH(self, t):
    #     r"\/"
    #     return t

    # def t_LIGNOREFORM(self, t):
    #     r'\#_\('
    #     return t

    # placeholder.  Each of these needs to be handled
    # differently.  There are variations of each as well.
    # Handle them with a symbol table somehow ?
    # https://clojure.org/guides/weird_characters
    #

    # def t_READMACRO(self, t):
    #     r'[^]+'
    #     # All the possible reader macro chars
    #     return t

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)


# discard #_  next symbol, dict, vector, or list.

# Declare the state
states = (("discard", "exclusive"),)


# Match on #_ Potentially enter discard state, or discard the next token.
def t_discard(t):
    r"\#_"
    t.lexer.discard_start = t.lexer.lexpos  # Record the starting position
    t.lexer.level = 1  # Initial brace level
    start_token = t.lexer.token()
    if start_token not in [r"\{", r"\[", r"\("]:
        t.lexer.skip(1)
    else:
        t.lexer.skip_form = start_token
        t.lexer.begin("discard")  # Enter 'ccode' state


# Rules for the ccode state
def t_discard_lbrace(t):
    r"\{"
    if t.lexer.skip_form == r"\{":
        t.lexer.level += 1


def t_discard_rbrace(t):
    r"\}"
    if t.lexer.skip_form == r"\{":
        t.lexer.level -= 1

        # If closing brace, return the code fragment
        if t.lexer.level == 0:
            t.value = t.lexer.lexdata[t.lexer.code_start : t.lexer.lexpos + 1]
            t.type = "DISCARD"
            t.lexer.lineno += t.value.count("\n")
            t.lexer.begin("INITIAL")
            return t


# Rules for the ccode state
def t_discard_lbracket(t):
    r"\["
    if t.lexer.skip_form == r"\[":
        t.lexer.level += 1


def t_discard_rbracket(t):
    r"\]"
    if t.lexer.skip_form == r"\[":
        t.lexer.level -= 1

        # If closing brace, return the code fragment
        if t.lexer.level == 0:
            t.value = t.lexer.lexdata[t.lexer.code_start : t.lexer.lexpos + 1]
            t.type = "DISCARD"
            t.lexer.lineno += t.value.count("\n")
            t.lexer.begin("INITIAL")
            return t


# Rules for the ccode state
def t_discard_lparen(t):
    r"\("
    if t.lexer.skip_form == r"\(":
        t.lexer.level += 1


def t_discard_rparen(t):
    r"\)"
    if t.lexer.skip_form == r"\(":
        t.lexer.level -= 1

        # If closing brace, return the code fragment
        if t.lexer.level == 0:
            t.value = t.lexer.lexdata[t.lexer.code_start : t.lexer.lexpos + 1]
            t.type = "DISCARD"
            t.lexer.lineno += t.value.count("\n")
            t.lexer.begin("INITIAL")
            return t


# comment (ignore)
def t_discard_comment(t):
    r"(;.*)"
    pass


# C string
def t_discard_string(t):
    r"\"([^\\\n]|(\\.))*?\""


# C character literal
def t_discard_char(t):
    r"\'([^\\\n]|(\\.))*?\'"


# Any sequence of non-whitespace characters (not braces, strings)
def t_discard_nonspace(t):
    r"[^\s\{\}\'\"]+"


# Ignored characters (whitespace)
t_discard_ignore = " \t\n"


# For bad characters, we just skip over it
def t_discard_error(t):
    t.lexer.skip(1)
