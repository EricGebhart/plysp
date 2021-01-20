import traceback
import types
import logs
import logging
import regex as re
from imcoll import ImMap, ImVector, ImList, ImSet

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


class Map(ComparableExpr, ImMap):
    def __init__(self, *args, **kwargs):
        if not kwargs:
            if len(args) == 1:
                ImMap.__init__(self, args[0])
            else:
                ImMap.__init__(self)
        else:
            ImMap.__init__(self, kwargs)

    def __eq__(self, other):
        return ImMap.__eq__(self, other)

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

        debug(logger, "- Env %s : keys ---- %s" % (env.name, env.keys()))
        debug(logger, "- %s : Type ---- %s" % (self.name, type(val)))
        if val is callable:
            debug(logger, "- %s " % val(1))
        if not val:
            raise UnknownVariable("Function %s is unknown" % self.name)

        return val


class Do(ComparableExpr):
    """Evaluate a list of expressions returning the value of the last"""

    def __init__(self, *exprs):
        # A path using dots, or a word.
        self.exprs = exprs

    def name(self):
        return None

    def __str__(self):
        return "."

    def __repr__(self):
        return "."

    def __call__(self, env, rest=None):
        res = None
        for x in self.exprs:
            res = eval_list(x, env)

        return res


class Try(object):
    """Try to do something, catch exceptions, etc."""

    def __init__(self, expr, *handlers):
        self.expr = expr
        self.handlers = handlers
        self.catches = [c for c in handlers if type(c[0]) is Catch]
        self.finallys = [f for f in handlers if type(f[0]) is Finally]
        debug(logger, "handlers %d" % len(self.handlers))
        debug(
            logger,
            "catchs and finallys,  %d - %d" % (len(self.catches), len(self.finallys)),
        )

    def name(self):
        return None

    def __str__(self):
        return "Try"

    def __repr__(self):
        return "Try"

    def __call__(self, env, rest=None):
        """Try to do something in a try, look through the catches on exception,
        The return value is from the thing to do, or from a catch, if not
        caught the finally's are done and the exception is propogated.
        execute finallys regardless, for side effects."""
        res = None
        raise_it = None
        exception = None
        try:

            debug(logger, "Try expr: %s" % str(self.expr))
            res = eval_list(self.expr, env)

            debug(logger, "Try result: %s" % str(res))

        except Exception as e:
            debug(logger, "----------------Exception: %s" % e)
            exception = e
            for x in self.catches:
                cort = x[0]
                debug(logger, "Try to match Catch: %s - %s" % (e, cort.name))
                debug(logger, "e Class: %s - %s" % (e.__class__, e.__cause__))
                debug(
                    logger, "e Class %s - %s" % ((e.__class__ == cort.name), cort.name)
                )
                if e.__class__ == cort.name or cort.name == Exception:
                    env.set_symbol(cort.varname, e)
                    res = cort(env)
                    break
            else:
                raise_it = True

        finally:
            for x in self.finallys:
                cort = x[0]
                cort(env)  # purposefully ignoring the return value.

        debug(logger, "Try result after: %s" % str(res))

        if raise_it:
            raise Exception(exception)

        return res


class Catch(object):
    def __init__(self, exception, varname, expr, env):
        # A path using dots, or a word.
        debug(logger, "New Catch for %s" % str(exception))
        self.name = env.find_path([exception])
        self.expr = expr
        self.varname = varname
        debug(logger, "Catch find %s : %s" % (exception, self.name))

    def name(self):
        return None

    def __str__(self):
        return "Catch %s" % self.name

    def __repr__(self):
        return self.__str__()

    def __call__(self, env, rest=None):
        debug(logger, "Call Catch %s : %s" % (self.name, self.expr))
        return eval_scalar(self.expr, env)


class Finally(object):
    def __init__(self, expr):
        # A path using dots, or a word.
        self.expr = expr

    def name(self):
        return None

    def __str__(self):
        return "Finally %s" % self.expr

    def __repr__(self):
        return self.__str__()

    def __call__(self, env, rest=None):
        return eval_scalar(self.expr, env)


class Throw(object):
    def __init__(self, exception, expr):
        # A path using dots, or a word.
        self.name = exception
        self.expr = expr

    def name(self):
        return None

    def __str__(self):
        return "Throw %s %s" % (self.name, self.expr)

    def __repr__(self):
        return self.__str__()

    def __call__(self, env, rest=None):
        msg = eval_scalar(self.expr, env)
        debug(logger, "Raising exception %s with %s" % (self.name, msg))
        raise Exception(self.name, msg)
        return


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


class List(ComparableIter, ImList):
    def __init__(self, *args):
        ImList.__init__(self, args)

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


class Vector(ComparableIter, ImVector):
    def __init__(self, *args):
        ImVector.__init__(self, args)

    def __str__(self):
        inner = " ".join([str(x) for x in self])
        return "[%s]" % inner

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self))

    def __call__(self, env, index=None):
        if index is not None:
            return self.get(index)
        else:
            return self  # Vector(*[eval_scalar(el, env) for el in self])


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


class Set(ImSet):
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
        if type(self.name) is Atom:
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
            # debug(logger, "Parms: %s" % str(self.parms))
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
    elif type(x) in (
        Atom,
        Import,
        Vector,
        ImVector,
        Map,
        ImMap,
        List,
        ImList,
        Set,
        Pyattr,
    ):
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

    if type(first) is Atom:
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
    if type(first) in (types.FunctionType, types.BuiltinFunctionType, type):
        args = map((lambda obj: eval_scalar(obj, env)), rest)
        debug(logger, "---------- Type Args: %s\n" % type(args))
        debug(logger, "---------- rest: %s | Args: %s\n" % (rest, args))
        return first(*args)

    if type(first) in (Map, Keyword):
        args = map((lambda obj: eval_scalar(obj, env)), rest)
        return first(env, rest)

    if type(first) in (Def, If, Py_interop, Import, Pyattr, Do, Try, Throw):
        return first(env)

    # debug(logger, "Returning first env rest: %s" % rest)
    # return first(env, rest)


def eval_to_string(txt, env):
    return tostring(eval_scalar(txt, env))
