import traceback
import types
import logs
import logging
import regex as re
from funktown import ImmutableDict, ImmutableVector, ImmutableList

# from pyrsistent import m, pmap, v, pvector, s
from namespace import Env

isa = isinstance

# logger = logs.add_file_handler(logging.getLogger(), "info", "plysp.log")
logger = logging.getLogger("plysp")
debug = logs.logdebug


class ComparableExpr(object):
    def __eq__(self, other):
        return isa(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))


class Map(ComparableExpr, ImmutableDict):
    def __init__(self, *args, **kwargs):
        if not kwargs:
            if len(args) == 1:
                ImmutableDict.__init__(self, args[0])
            else:
                ImmutableDict.__init__(self)
        else:
            ImmutableDict.__init__(self, kwargs)

    def __eq__(self, other):
        return ImmutableDict.__eq__(self, other)

    def __str__(self):
        inner = ", ".join(["%s %s" % (k, v) for k, v in self.items()])
        return "{%s}" % inner

    def __repr__(self):
        return "MAP(%s)" % (str(self))

    def __call__(self, env, key=None):
        if key is not None:
            return self.get(key)
        else:
            return Map(
                dict(
                    [
                        (eval_scalar(k, env), eval_scalar(v, env))
                        for k, v in self.items()
                    ]
                )
            )

        # if not rest.rest().empty():
        #     raise TypeError("Map lookup takes one argument")
        # return self.get([eval_scalar(rest.first())])


class Atom(ComparableExpr):
    def __init__(self, name=None, value=None):
        # Nothing but /'s, a path, or a word.
        if re.match(r"^/+$", name):
            self.name = [name]
        elif re.findall(r"/", name):
            self.name = name.split("/")
        else:
            self.name = [name]
        debug(logger, "New Atom: %s " % self.name)

    def name(self):
        return self.name

    def __str__(self):
        return "/".join(self.name)

    def pypath(self):
        return ".".join(self.name)

    def __repr__(self):
        return "/".join(self.name)
        # return "ATOM(%s)" % (self.name)

    def __call__(self, env, rest=None):
        val = env.find(self.name)

        debug(logger, "-Env %s : keys ---- %s" % (env.name, env.keys()))
        debug(logger, "- %s : Type ---- %s" % (self.name, type(val)))
        # debug(logger, str(traceback.print_stack(limit=4)))
        if not val:
            raise UnknownVariable("Function %s is unknown" % self.name)

        return val


class NMsym(ComparableExpr):
    def __init__(self, name=None, value=None):
        # A path using dots, or a word.
        if re.findall(r"\.", name):
            self.name = name.split(".")
        else:
            self.name = [name]
        debug(logger, "New NM Sym: %s " % self.name)

    def name(self):
        return self.name

    def __str__(self):
        return ".".join(self.name)

    def pypath(self):
        return ".".join(self.name)

    def __repr__(self):
        return "/".join(self.name)
        # return "NMSYM(%s)" % (self.name)

    def __call__(self, env, rest=None):
        val = env.find(self.name)

        debug(logger, "- %s : Type ---- %s" % (self.name, type(val)))
        # debug(logger, str(traceback.print_stack(limit=4)))
        if not val:
            raise UnknownVariable("Name: %s is unknown" % self.name)

        return val


class Octal(object):
    pass


class Hex(object):
    pass


class Base2(object):
    pass


class Char(object):
    pass


class Uchar(object):
    pass


class Ochar(object):
    pass


class Deref(object):
    pass


class Quote(object):
    pass


class UnQuote(object):
    pass


class SyntaxQuote(object):
    pass


class UnQuote_splicing(object):
    pass


class Var(object):
    pass


class Gensym(object):
    pass


class Auto_gensym(object):
    pass


class Regex(object):
    pass


class Uuid(object):
    pass


class Inst(object):
    pass


class Inline_func(object):
    pass


class Anonymous_Arg(object):
    pass


class Ignore(ComparableExpr):
    def __init__(self, value=None):
        self.__value = value

    def value(self):
        return self.__value

    def __repr__(self):
        return "IGNORE(%s)" % (self.__value)


class ComparableIter(ComparableExpr):
    def __eq__(self, other):
        try:
            if len(self) != len(other):
                return False
            for a, b in zip(self, other):
                if a != b:
                    return False
        except Exception:
            return False
        else:
            return True


class List(ComparableIter, ImmutableList):
    def __init__(self, *args):
        ImmutableList.__init__(self, args)

    def __str__(self):
        inner = " ".join([str(x) for x in self])
        return "(%s)" % inner

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__.upper(),
            ",".join([repr(el) for el in self]),
        )

    def __call__(self, env, index=None):
        if index is None:
            return eval_list(self, env)
        else:
            return self.get(index)


class Vector(ComparableIter, ImmutableVector):
    def __init__(self, *args):
        ImmutableVector.__init__(self, args)

    def __str__(self):
        inner = " ".join([str(x) for x in self])
        return "[%s]" % inner

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self))

    def __call__(self, env, index=None):
        if index is not None:
            return self.get(index)
        else:
            return Vector(*[eval_scalar(el, env) for el in self])


class Keyword(ComparableExpr):
    def __init__(self, name):
        self.name = ":" + name

    def key(self):
        return self.__repr__()

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Keyword: (%s)" % self.name

    def __lt__(self, other):
        return self.key() < other.key()

    def __eq__(self, other):
        return self.key() == other.key()

    def __hash__(self):
        return hash(self.key())

    def __call__(self, env, rest):
        # return (d.get(self.key()))
        if not rest.rest().empty():
            raise TypeError("Keyword lookup takes one argument")
        return eval_scalar(rest.first()).get(self.key)


class Set(frozenset):
    def __str__(self):
        inner = " ".join([self.tostring(x) for x in self])
        return "#{%s}" % inner

    def __repr__(self):
        inner = " ".join([str(x) for x in self])
        return "#{%s}" % inner


class Import(object):
    def __init__(self, name, asname=None):
        self.name = name
        self.asname = asname

    def __call__(self, env):
        if type(self.name) in (Atom, NMsym):
            name = self.name.name
        else:
            name = self.name

        env.current_ns.py_import(name, self.asname)

    def __repr__(self):
        if self.asname is not None:
            return "(import %s as %s)" % (self.name, self.asname)
        else:
            return "(import %s)" % self.name


class PyNew(object):
    def __init__(self, env, classpath, args):
        self.env = env
        self.classpath = classpath
        self.args = args

    def path_list(self):
        if "/" in self.classpath:
            return self.attr.split("/")
        else:
            return self.classpath

    def __repr__(self):
        return "New %s with Args: %s" % (self.classpath, self.args)

    def __call__(self, env):
        self.__repr__()
        classobj = env.find(self.path_list())
        return classobj(*self.args)


class Pyattr(object):
    def __init__(self, attr):
        self.attr = attr

    def __str__(self):
        return "-%s" % self.attr

    def path_list(self):
        return self.attr.split("/")

    def __repr__(self):
        # return "%s %s" % (x, type(self.find(x.path_list())))
        return self.attr

    def __call__(self, env):
        self.__repr__()
        path = self.path_list()
        return env.find(path)


class Py_interop(object):
    def __init__(self, method, obj, args):
        self.method = method
        self.obj = obj
        self.args = args

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s %s %s" % (self.method, self.obj, self.args)

    def __call__(self, env):
        self.__repr__()

        # obj = env.find(self.obj)
        # print(self.method)
        # ins_method = obj.__getattribute__(self.method)
        # print(self.args)
        # r = ins_method(*self.args)
        # print ("result is", r)
        # return (r)

        return env.find(self.obj).__getattribute__(self.method)(*self.args)


class Function(ComparableExpr):
    def __init__(self, parms, body, env):
        self.parms = parms
        self.body = body
        self.env = env

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "(fn %s %s)" % (self.parms, self.body)

    def __call__(self, env):
        self.env = env  # don't need to do this. just put it in the lambda.

        def eval_function(*args):
            debug(logger, "Args: %s" % str(args))
            return eval_list(self.body, Env(self.parms, args, self.env))

        return eval_function


class Let(ComparableExpr):
    pass


class UnknownVariable(Exception):
    pass


class If(object):
    def __init__(self, test, true_expr, false_expr, env):
        self.test = test
        self.true_expr = true_expr
        self.false_expr = false_expr
        self.env = env

    def __str__(self):
        return "(if %s %s %s)" % (self.test, self.true_expr, self.false_expr)

    def __call__(self, env):
        # print(self.symbol.__str__(), self.rest)
        if eval_scalar(self.test, env):
            return eval_scalar(self.true_expr, env)
        else:
            return eval_scalar(self.false_expr, env)


class Def(object):
    def __init__(self, arg1, arg2, env):
        self.symbol = arg1
        self.rest = arg2
        self.env = env

    def __str__(self):
        return self.symbol.name()

    def __call__(self, env):
        debug(logger, "%s %s " % (self.symbol.__str__(), self.rest))
        env.set_symbol(self.symbol.__str__(), eval_scalar(self.rest, env))
        return self.symbol


class Refer(object):
    """Provide references to things in other namespaces."""

    def __init__(self, namespace, exclude=[], only=[], rename={}):
        self.namespace = namespace.split(".")
        self.exclude = exclude
        self.only = only
        self.rename = rename

    def __str__(self):
        return self.symbol.name()

    def __call__(self, env):
        debug(logger, "require namespace: %s " % namespace)
        return env.require(self.namespace, self.exclude, self.only, self.rename)


class Require(object):
    """load libraries and provide references to things in other namespaces."""

    def __init__(self, namespace, exclude=[], only=[], rename={}):
        self.namespace = namespace.split(".")
        self.exclude = exclude
        self.only = only
        self.rename = rename

    def __str__(self):
        return self.symbol.name()

    def __call__(self, env):
        debug(logger, "require namespace: %s " % namespace)
        return env.require(self.namespace, self.exclude, self.only, self.rename)


class NewNS(object):
    def __init__(self, name):
        debug(logger, type(name))
        # Nothing but /'s, a path, or a word.
        if re.match(r"^/+$", name):
            self.name = [name]
        elif re.findall(r"/", name):
            self.name = name.split("/")
        else:
            self.name = [name]

    def __str__(self):
        return self.name()

    def __call__(self, env, rest):
        debug(logger, self.name.__str__())
        return env.new_ns(self.name)


class In_NS(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name()

    def __call__(self, env, rest):
        debug(logger, self.name.__str__())
        return env.find(self.name)


def to_string(x):
    "Convert a Python object back into a Lisp-readable string."
    if x is True:
        return "#t"
    elif x is False:
        return "#f"
    elif isa(x, Atom):
        return x
    elif isa(x, NMsym):
        return x
    elif isa(x, str):
        return '"%s"' % x.encode("unicode_escape").decode("utf_8").replace('"', r"\"")
    elif isa(x, list):
        return "(" + " ".join(map(str, x)) + ")"
    elif isa(x, complex):
        return str(x).replace("j", "i")
    else:
        return str(x)


def tostring(x):
    if x is None:
        return "nil"
    elif type(x) is str:
        return x
    elif type(x) in (int, float):
        return str(x)
    elif x.__class__.__name__ in [
        "function",
        "builtin_function_or_method",
    ]:
        return str(x)

    elif type(x) in (
        Atom,
        NMsym,
        Keyword,
        list,
        List,
        Env,
        Vector,
        Map,
        Set,
        Pyattr,
        PyNew,
        Def,
        If,
    ):
        return x.__str__()
    else:
        print(str(x), type(x))
        # raise TypeError("Sorry can't pretty print, %s is unknown!" % x)


def eval_scalar(x, env=None):
    if x is None:
        return
    if type(x) in (int, float, str, Keyword):
        return x
    elif type(x) in (Atom, Import, Vector, Map, List, Set, Pyattr):
        return x(env)
    elif type(x) is List:
        return eval_list(x.contents, env)
    # Needs to create a new scope. env.
    elif type(x) in (Function, types.FunctionType):
        return x(env)
    return x


def eval_list(contents, env):
    """
    If what we have to evaluate is a list, then we need to take care of
    that. First thing is the function, the rest are the args. Some things
    have everything in their object ready to go.
    """
    # while True:

    debug(logger, "contents isa: %s" % type(contents))
    if type(contents) is Atom:
        debug(logger, "Atom: %s" % contents.name)
        return contents(env)

    if contents.empty():
        return List()  # ()

    first = contents.first()
    rest = contents.rest()

    debug(logger, "First isa: %s" % type(first))
    debug(logger, "rest is: %s" % rest)

    if type(first) is List:
        first = eval_list(first, env)

    if type(first) in (Atom, NMsym):
        first = first(env)

    # plysp function
    # We get a pointer to it.
    if type(first) is Function:
        return first(env)

    # New name space or old, change there.
    if type(first) in (NewNS, In_NS):
        env = first(env, rest)

    # or python function..
    # If it is a python function, to call directly.
    # isinstance(first, (types.FunctionType, types.BuiltinFunctionType)
    if type(first) in (types.FunctionType, types.BuiltinFunctionType):
        args = map((lambda obj: eval_scalar(obj, env)), rest)
        debug(logger, "---------- Type Args: %s\n" % type(args))
        debug(logger, "---------- rest: %s | Args: %s\n" % (rest, args))
        return first(*args)

    if type(first) in (Map, Keyword):
        args = map((lambda obj: eval_scalar(obj, env)), rest)
        return first(env, rest)

    # I'm not clear on if this could even be hit.
    # parser gobbles, objects come about.
    if type(first) in (Def, If, Py_interop, Import, Pyattr):
        return first(env)

    # debug(logger, "Returning first env rest: %s" % rest)
    # return first(env, rest)


def eval_to_string(txt, env):
    return tostring(eval_scalar(txt, env))
