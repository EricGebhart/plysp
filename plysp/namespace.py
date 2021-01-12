import importlib as il
import types
import logging
from logs import logdebug as debug

# for now.  These should really only be within the namespace
from functools import reduce
import operator as op

logger = logging.getLogger("plysp")


# I think this is my atom...
class Symbol(str):
    pass


class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    core_ns = None
    current_ns = None

    def __init__(self, parms=(), args=(), outer=None, name=None):
        # Bind parm list to corresponding args, or single parm to list of args

        # Need to bind very first outer with the plysp/core env when
        # it loads. ? when's that?
        self.outer = outer
        self.name = name
        self.eval_verbose = False
        if name is not None:
            debug(logger, "-- NewENV: %s" % name)
            self.__setitem__("*ns*", self.__str__())
            self.__setitem__("*current-ns*", self)

            if outer is None and self.current_ns is None:
                self.__core_it__()  # until core.yl is there.
                Env.current_ns = self

        if isinstance(parms, Symbol):  # just case.
            self.update({parms: list(args)})

        else:
            if args and parms:  # Needs & for rest...research...
                if len(args) != len(parms):
                    raise TypeError("expected %s, given %s, " % (parms, args))
                # All we get for parms are simple atoms.
                parms = [p.name[0] for p in parms]
                self.update(list(zip(parms, args)))

    def __core_it__(self):
        """Install the python builtins+."""
        # should be able to do this with py_import() below
        # from builtins import *
        [
            self.set_symbol(name, obj)
            for name, obj in __builtins__.items()
            if callable(obj)
        ]

        # Get some builtins built in.
        self.update((name, func) for name, func in some_builtins().items())

        # if name == "plysp/core":
        self.py_import("math")
        self.py_import("cmath")
        self.py_import("operator", "op")
        self.py_import("functools.reduce", "py-reduce")
        self.py_import("functools.partial", "py-partial")

        # this should be empty to start and all things
        # go into the namespace until there is a scope.
        # leaving for now because there isn't a plysp.core yet.

    def find_top(self):
        "Find the Env at the top of the envs."
        env = self.outer
        while env.outer is not None:
            env = env.outer
        return env

    def find_path(self, path_var):
        # ns = self.find("*current-ns*")
        debug(logger, (" %s " % str(path_var)))
        ns = self.current_ns or self
        debug(logger, "Self, %s" % self.name)
        # debug(logger, "Items, %s" % self.items())
        # debug(logger, "NS: %s" % str(ns.items()))
        debug(logger, "FIND Path IN: %s" % self.name)

        thing = None
        if path_var[0] in self:
            debug(logger, "path_var[0]: %s" % path_var[0])
            thing = self.__getitem__(path_var[0])
            rest = path_var[1:]
            debug(logger, "Rest: %s" % rest)

            if not rest:
                return thing

            # if type(thing) is types.ModuleType:
            # potential BUG here.
            if isinstance(thing, types.ModuleType):
                # print("found module thing")
                # print("rest is; ", rest[0])
                # print("returning : ", rest[0])
                thing = thing.__getattribute__(rest[0])

            elif isinstance(thing, Env):
                thing = thing.find_path(rest)

        else:
            thing = self.outer.find_path(path_var)

        return thing

    def find(self, pathlist):
        sym = self.find_path(pathlist)
        if sym is None and self.core_ns is not None:
            sym = self.core_ns.find_path(pathlist)
        return sym

    # def find(self, var):
    #     "Find the innermost Env where var appears."
    #     # has to be a namespace, so go look there.
    #     debug(logger, "local Scope: %s" % var)
    #     if len(var) > 1:
    #         return self.find_path(var)
    #     elif len(var) == 1:
    #         var = var[0]
    #     if var in self.keys():
    #         debug(logger, "Found: %s " % var)
    #         return self.__getitem__(var)
    #     elif self.outer is None:
    #         raise LookupError(var)
    #     else:
    #         return self.outer.find(var)

    def __str__(self):
        return "/".join(self.name)

    def set_symbol(self, name, val):
        return self.__setitem__(name, val)

    def set_core_ns(self):
        """Once we have a plysp core, set it so its easy to get to"""
        core = self.find(["plysp", "core"])
        if isinstance(core, Env):
            top = self.find_top()
            top.set_symbol("*core-ns*", core)
        Env.core_ns = core

    def __import_func__(self, name, func):
        return il.import_module(name).__getattribute__(func)

    def __import_mod__(self, name):
        return il.import_module(name)

    def __import_pkg__(self, name, pkg):
        return il.import_module(name, pkg)

    def py_import(self, name, asname=None, pkg=None, functions=None):
        f = name.split(".")[-1:][0]
        p = str.join(".", name.split(".")[:-1])
        if asname is None:
            # if we get a multipart name, then import it at the top level.
            if f is not None and len(p) > 0:
                asname = f
            else:
                asname = name

        self.set_symbol(asname, {})

        if len(p) > 0:
            print("importing function %s %s as %s" % (p, f, asname))
            name = p
            # if we got foo.bar.baz assign baz to self.baz
            self[asname] = self.__import_func__(name, f)

        elif pkg is None:
            print("importing %s as %s" % (name, asname))
            # if we got a name, import and assign to self.asname or self.name.
            self[asname] = self.__import_mod__(name)

        else:
            print("importing %s from package %s" % (name, pkg))
            # if we got a name and a pkg, import and assign to self.asname or
            # self.name.
            self[asname] = self.__import_pkg__(name, pkg)

    def isfunc(self, obj):
        return (
            isinstance(obj, types.MethodType)
            or isinstance(obj, types.FunctionType)
            or str(type(obj)) == "<class 'method-wrapper'>"
        )

    def show_methods(self):
        return [
            thing
            for thing in self.__dir__()
            if self.isfunc(self.__getattribute__(thing))
        ]

    def show_attributes(self):
        return [
            thing
            for thing in self.__dir__()
            if not self.isfunc(self.__getattribute__(thing))
        ]

    def is_module(self, thing):
        return str(type(thing)) == "<class 'module'>"

    def show_module_or_func(self, thing):
        # print(thing, type(thing))
        if str(type(thing)) == "<class 'module'>":
            return dir(thing)
        else:
            return str(thing)

    def print_module_contents(self, k):
        print("------------------------------------------------------------")
        print(k)
        print(dir(self.__getitem__[k]))

    def show_python_callables(self):
        thing_keys = [thing for thing in self.keys()]
        # print("Local")
        [k for k in thing_keys if self.is_module(self.__getitem__(k)) is not True]
        [
            self.print_module_contents(k)
            for k in thing_keys
            if self.is_module(self.__getitem__(k)) is True
        ]

    def in_ns(self, name):
        if type(name) is not str:
            name = name.name  # it's an Atom
        if name in self.namespaces.keys():
            Env.current_ns = self.namespaces[name]
            return Env.current_ns
        else:
            return None

    def new_ns(self, name):
        """Take a atom/list of names, create a new namespace environment
        in the current namespace."""
        ns = self.find(["*current-ns*"])

        # debug(logger, "me has: %s" % (self.items()))
        debug(logger, "me: %s %s" % (self.name, type(self)))
        debug(logger, "name: %s %s" % (name, type(name)))
        debug(logger, "ns: %s" % self.current_ns)
        for n in name:
            debug(logger, "n: %s" % n)
            if n not in ns.items():
                debug(logger, "New Env %s" % n)
                ns = Env(name=name, outer=ns)
            else:
                debug(logger, "Using Env: %s" % ns[n])
                ns = ns[n]

        Env.current_ns = ns
        return ns

    def load_ns(self, name):
        """read a file and load it into it's ns"""
        pass


def some_builtins():
    # These functions take a variable number of arguments
    ops = {}

    variadic_operators = {
        "+": (op.add, 0),
        "-": (op.sub, 0),
        "*": (op.mul, 1),
        "/": (op.truediv, 1),
        "==": (op.eq, 0),
        "=": (op.eq, 0),
        "max": (max, 0),
        "min": (min, 0),
    }

    def variadic_generator(func, default):
        ret = lambda *args: reduce(func, args) if args else default
        # For string representation; otherwise just get 'lambda':
        ret.__name__ = func.__name__
        return ret

    for name, info in variadic_operators.items():
        ops[name] = variadic_generator(*info)

    # Something to start with, I think a lot of this can be
    # better done in core.yl when I get one.
    non_variadic_operators = {
        "!": op.inv,
        ">": op.gt,
        "<": op.lt,
        ">=": op.ge,
        "<=": op.le,
        "abs": abs,
        "first": lambda x: x[0],
        "last": lambda x: x[-1],
        "rest": lambda x: x[1:],
        "cons": lambda x, y: [x] + y,
        "eq?": op.is_,
        "equal?": op.eq,
        "length": len,
        # Needs to be List, so refactor collections out of core.
        # Then we can reference them here.
        "list": lambda *x: list(x),
        "list?": lambda x: isinstance(x, list),
        "map?": lambda x: isinstance(x, map),
        # "vector?": lambda x: isinstance(x, Vector),
        "not": op.not_,
        "nil?": lambda x: x is None,
        "empty?": lambda x: x == [],
        "number?": lambda x: isinstance(x, Number),
        "round": round,
        "symbol?": lambda x: isinstance(x, Symbol),
    }
    return ops | non_variadic_operators


# importlib.__import__(name, globals=None, locals=None, fromlist=(), level=0)
# An implementation of the built-in __import__() function.

# import math.sin
# p, m = name.rsplit('.', 1)

# mod = import_module(p)
# met = getattr(mod, m)

# met()


# a = A()
# >>> a.bar
# <bound method A.bar of <__main__.A instance at 0x00A9BC88>>
# >>>
# Bound methods have been "bound" (how descriptive) to an instance, and
# that instance will be passed as the first argument whenever the method
# is called.

# Callables that are attributes of a class (as opposed to an instance)
# are still unbound, though, so you can modify the class definition whenever
# you want:


# def spam():
#     print("Spam")


# # A.foo = foo
# # A.spam = spam
# # a2 = A()
# # a2.spam
# # a2.spam()```
# essentially with this object.   I can do things like this.
# ```myns = ns("myns")
# myns.import("math.sin")
# myns.sin(2)
# >>> something...
# myns.import("math", "m")  # import math as m
# myns.m.cos(2)
# >>> something...
# myns.spam = spam
# myns.spam()
# >>> Spam.
# etc...```
