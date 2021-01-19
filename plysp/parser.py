import sys
import re
import ply.yacc as yacc
from lexer import PlyspLex
from core import (
    Atom,
    # NMsym,
    Keyword,
    List,
    Vector,
    Map,
    # Ignore,
    Set,
    Def,
    Do,
    If,
    NewNS,
    In_NS,
    Import,
    Refer,
    Require,
    PyNew,
    Pyattr,
    Py_interop,
    Quote,
    SyntaxQuote,
    UnQuote,
    UnQuote_splicing,
    Regex,
    Deref,
    Gensym,
    Uuid,
    Inline_func,
    Var,
    Anonymous_Arg,
    Function,
    Let,
    Octal,
    Hex,
    Base2,
    Ochar,
    Uchar,
    Char,
)

# BNF grammar for 'lisp'
# sexpr : atom
#       | readmacro sexpr
#       | keyword
#       | float
#       | integer
#       | list
#       | set
#       | vector
#       | map
#       | ignoreform
#       | nil
# sexprs : sexpr
#        | sexprs sexpr
# list : ( sexprs )
#      | ( )

_quiet = True


class LispLogger(yacc.PlyLogger):
    def debug(self, *args, **kwargs):
        if not _quiet:
            super(type(self), self).debug(*args, **kwargs)


def make_map(args):
    m = {}
    kvlist = [(args[i], args[i + 1]) for i in range(0, len(args), 2)]
    for k, v in kvlist:
        m[k] = v
    return Map(m)


def quote_expr(raw):
    return List(Atom("quote"), raw)


def deref_expr(raw):
    return List(Atom("deref"), raw)


def init_type(raw):
    # Due to how python types are initialized, we can just treat them
    # as function calls.
    return raw


def print_stuff(production_name, p):
    print("Production: ", production_name)
    print("LEN P: ", len(p))
    print("ARGS: ", [p[i] for i in range(3, len(p))])


# ### NO LONGER NEEDED !!!!!

# Map from the regex that matches the atom to the function that takes
# in an ast, and modifies it as specified by the macro
READER_MACROS = {
    r"@": deref_expr,
    r"\'": quote_expr,
    r"\.": init_type,
}


class PlyspParse(object):
    def __init__(self, env):
        self.env = env

    def build(self):
        self.parser = yacc.yacc(module=self, errorlog=LispLogger(sys.stderr))
        return self.parser

    tokens = PlyspLex.tokens
    tokens.remove("NUMBER")
    # tokens.remove("UNQUOTE")
    # tokens.remove("UNQUOTE_SYM")
    # tokens.remove("INSTDISCARD")
    # tokens.remove('CHAR')
    # tokens.remove('LIGNOREFORM')
    # tokens.extend(('FLOAT', 'INTEGER'))

    def p_sexpr_nil(self, p):
        "sexpr : NIL"
        p[0] = None

    def p_sexpr_readmacro(self, p):
        "sexpr : READMACRO sexpr"
        for regex, func in READER_MACROS.items():
            if re.match(regex, p[1]):
                p[0] = func(p[2])
                return

    def p_sexpr_atom(self, p):
        "sexpr : ATOM"
        p[0] = Atom(p[1])

    # def p_sexpr_nm_sym(self, p):
    #     """sexpr : NM_SYM"""
    #     p[0] = NMsym(p[1])

    def p_keyword(self, p):
        "sexpr : KEYWORD"
        p[0] = Keyword(p[1])

    def p_string(self, p):
        "sexpr : STRING"
        p[0] = str(p[1])

    def p_regex(self, p):
        "sexpr : REGEX"
        p[0] = Regex(p[1])

    def p_sexpr_float(self, p):
        "sexpr : FLOAT"
        p[0] = float(p[1])

    def p_sexpr_integer(self, p):
        "sexpr : INTEGER"
        p[0] = int(p[1])

    def p_sexpr_octal(self, p):
        "sexpr : OCTAL"
        p[0] = Octal(p[1])

    def p_sexpr_hex(self, p):
        "sexpr : HEX"
        p[0] = Hex(p[1])

    def p_sexpr_Base2(self, p):
        "sexpr : BASE2"
        p[0] = Base2(p[1])

    def p_sexpr_char(self, p):
        "sexpr : CHAR"
        p[0] = str(p[1])

    def p_sexpr_unicode_char(self, p):
        "sexpr : UNICODE_CHAR"
        p[0] = Uchar(p[1])

    def p_sexpr_octal_char(self, p):
        "sexpr : OCTAL_CHAR"
        p[0] = Ochar(p[1])

    def p_sexpr_deref(self, p):
        """sexpr : DEREF_SYM sexpr
        | DEREF sexpr"""
        p[0] = Deref(p[1])

        # QUOTING

    def p_sexpr_quote(self, p):
        """sexpr : QUOTE_SYM sexpr
        | QUOTE sexpr"""
        p[0] = Quote(p[1])

    def p_sexpr_unquote(self, p):
        """sexpr : UNQUOTE_SYM sexpr
        | UNQUOTE sexpr"""
        p[0] = UnQuote(p[1])

    def p_sexpr_syntax_quote(self, p):
        """sexpr : SYNTAX_QUOTE_SYM sexpr
        | SYNTAX_QUOTE sexpr"""
        p[0] = SyntaxQuote(p[1])

    def p_sexpr_unquote_splicing(self, p):
        """sexpr : UNQUOTE_SPLICING_SYM sexpr
        | UNQUOTE_SPLICING sexpr"""
        p[0] = UnQuote_splicing(p[1])

    def p_sexpr_var(self, p):
        """sexpr : VAR_QUOTE sexpr
        | VAR sexpr"""
        p[0] = Var(p[1])

    # def p_sexpr_auto_gensym(self, p):
    #     'sexpr : SYMBOL AUTO_GENSYM'
    #     p[0] = Auto_gensym(p[1])

    def p_sexpr_gensym(self, p):
        "sexpr : GENSYM"
        p[0] = Gensym(p[1])

    def p_sexpr_uuid(self, p):
        "sexpr : UUID ATOM"
        p[0] = Uuid(p[1])

    # def p_sexpr_inst(self, p):
    #     'sexpr : INST ATOM'
    #     p[0] = Inst(p[1])

    def p_sexpr_seq(self, p):
        """
        sexpr : list
              | vector
              | map
              | set
        """
        p[0] = p[1]

    def p_sexprs_sexpr(self, p):
        "sexprs : sexpr"
        p[0] = p[1]

    def p_sexprs_sexprs_sexpr(self, p):
        "sexprs : sexprs sexpr"
        # p[0] = ', '.join((p[1], p[2]))
        if type(p[1]) is list:
            p[0] = p[1]
            p[0].append(p[2])
        else:
            p[0] = [p[1], p[2]]

    def p_list(self, p):
        "list : LPAREN sexprs RPAREN"
        try:
            p[0] = List(*p[2])
        except TypeError:
            p[0] = List(p[2])

    def p_empty_list(self, p):
        "list : LPAREN RPAREN"
        p[0] = List()

    def p_vector(self, p):
        "vector : LBRACKET sexprs RBRACKET"
        try:
            p[0] = Vector(*p[2])
        except TypeError:
            p[0] = Vector(p[2])

    def p_empty_vector(self, p):
        "vector : LBRACKET RBRACKET"
        p[0] = Vector()

    def p_set(self, p):
        "set : LSETBRACE sexprs RBRACE"
        p[0] = Set(p[2])

    def p_map(self, p):
        "map : LBRACE sexprs RBRACE"
        p[0] = make_map(p[2])

    def p_empty_map(self, p):
        "map : LBRACE RBRACE"
        p[0] = Map()

    def p_sexpr_def(self, p):
        "sexpr : DEF sexpr sexpr"
        p[0] = Def(p[2], p[3], self.env)

    def p_sexpr_do(self, p):
        "sexpr : DO sexprs"
        try:
            p[0] = Do(*p[2])
        except TypeError:
            p[0] = Do(List(p[2]))

    def p_sexpr_if(self, p):
        "sexpr : IF sexpr sexpr sexpr"
        p[0] = If(p[2], p[3], p[4], self.env)

    def p_sexpr_fn(self, p):
        "sexpr : FN vector sexpr"
        p[0] = Function(p[2], p[3], self.env)

    def p_sexpr_let_(self, p):
        "sexpr : LET vector sexpr"
        p[0] = Let(p[2], p[3], self.env)

    def p_sexpr_inline_func(self, p):
        "sexpr : INLINE_FN sexpr RPAREN"
        p[0] = Inline_func(p[1:])

    def p_sexpr_anonymous_arg(self, p):
        "sexpr : ANONYMOUS_ARG"
        p[0] = Anonymous_Arg(p[1:])

    # These can't do this. They should be objects in
    # core that can be called.
    # It short circuits future compileability.
    def p_sexpr_ns(self, p):
        """sexpr : NS ATOM"""
        p[0] = NewNS(p[2])

    def p_sexpr_in_ns(self, p):
        """sexpr : IN_NS ATOM
        | IN_NS PATH"""
        p[0] = In_NS(p[2])

    # Not right. Funcpath should just be a path. and resolve to a func.
    # This is just a hack so that math/sin and so forth work.
    def p_sexpr_path(self, p):
        """sexpr : PATH
        | PATH sexpr"""
        print("PATH: ", len(p))
        if len(p) > 2:
            p[0] = FuncPath(p[1], p[2:])
        else:
            p[0] = Path(p[1])

    def p_sexpr_refer(self, p):
        """
        sexpr : REFER ATOM
              | REFER ATOM AS ATOM
        """
        name = p[2]
        asname = None
        hasas = None
        token = None
        if len(p) > 3:
            for token in p[3:]:
                if hasas is True:
                    asname = token
                elif token == "as":
                    hasas = True
                else:
                    name = "".join([name, token])
        if asname:
            p[0] = Import(name, asname)
        else:
            p[0] = Import(name)

    def p_sexpr_import(self, p):
        """
        sexpr : IMPORT ATOM
              | IMPORT ATOM AS ATOM
              | IMPORT ATOM DOT ATOM
              | IMPORT ATOM DOT ATOM AS ATOM
              | IMPORT ATOM DOT ATOM DOT ATOM AS ATOM
        """
        name = p[2]
        asname = None
        hasas = None
        token = None
        if len(p) > 3:
            for token in p[3:]:
                if hasas is True:
                    asname = token
                elif token == "as":
                    hasas = True
                else:
                    name = "".join([name, token])
        if asname:
            p[0] = Import(name, asname)
        else:
            p[0] = Import(name)

    def p_sexpr_pynew(self, p):
        """
        sexpr : NEW ATOM sexpr sexpr
              | NEW ATOM sexpr
              | NEW ATOM
        """
        print("py New:", p[2])
        args = None
        classname = p[2]
        if len(p) > 3:
            args = p[3:]
        p[0] = PyNew(self.env, classname=classname, args=args)

    # def p_sexpr_pyattr(self, p):
    #     """ sexpr : PYATTR """
    #     attr = p[1][1:]
    #     p[0] = Pyattr(attr)

    def p_sexpr_dot_interop(self, p):
        """sexpr : DOT ATOM
        | DOT ATOM sexprs
        | DOT ATOM ATOM sexprs
        """
        # print(len(p))
        method = p[2]
        if method[0] == "-":
            p[0] = Pyattr(p[2][1:])
        else:
            obj = p[3]
            if len(p) > 3:
                args = p[4:]
            else:
                args = None
            p[0] = Py_interop(method, obj, args)

    def p_error(self, p):
        if p:
            print(p.lineno, "Syntax error in input at token '%s'" % p.value)
        else:
            print("EOF", "Syntax error. No more input.")
