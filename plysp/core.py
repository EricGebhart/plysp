import operator
from funktown import ImmutableDict, ImmutableVector, ImmutableList
from functools import reduce
from namespace import namespace

isa = isinstance

class ComparableExpr(object):
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

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
        inner = ', '.join(['%s %s' % (k, v) for k, v in x.items()])
        return '{%s}' % inner

    def __repr__(self):
        return 'MAP(%s)' % (str(self))

    def __call__(self, env, key=None):
        if key is not None:
            return self.get(key)
        else:
            return(Map(dict([(env.eval_scalar(k), env.eval_scalar(v))
                             for k, v in x.items()])))

        # if not rest.rest().empty():
        #     raise TypeError("Map lookup takes one argument")
        # return self.get([env.eval_scalar(rest.first())])


class Atom(ComparableExpr):
    def __init__(self, name=None, value=None):
        self.name = name

    def name(self):
        return self.name

    def __str__(self):
        return(self.name)

    def __repr__(self):
        return "ATOM(%s)" % (self.name)

    def __call__(self, env, rest=None):
        val = env.find(self.name)

        if not val:
            raise UnknownVariable("Function %s is unknown" % self.name)

        if type(val) is Atom:
            return str(val)
        else:
            if rest is None:
                return (env.eval_scalar(val)) 
            else:
                args = map((lambda obj: env.eval_scalar(obj)), rest)
                return val(*args)

            # else:
            # raise TypeError("value of %s is not callable" % self.name)


class Octal(object):
    pass

class Hex(object):
    pass

class Base2(object):
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
class gensym(object):
    pass
class Auto_gensym(object):
    pass
class Uuid(object):
    pass
class Inst(object):
    pass
class Inline_func(object):
    pass
class anonymous_Arg(object):
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
        except:
            return False
        else:
            return True


class List(ComparableIter, ImmutableList):
    def __init__(self, *args):
        ImmutableList.__init__(self, args)

    def __str__(self):
        inner = ' '.join([self.tostring(x) for x in x])
        return '(%s)' % inner

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__.upper(),
                           ','.join([repr(el) for el in self]))

    def __call__(self, env, index=None):
        if index is None:
            return (env.eval_list(self))
        else:
            return (self.get(index))


class Vector(ComparableIter, ImmutableVector):
    def __init__(self, *args):
        ImmutableVector.__init__(self, args)

    def __str__(self):
        inner = ' '.join([self.tostring(x) for x in x])
        return '[%s]' % inner

    def __repr__(self):
        return ("%s(%s)" % (self.__class__.__name__,
                           str(self)))

    def __call__(self, env, index=None):
        if index is not None:
            return self.get(index)
        else:
            return Vector(*[env.eval_scalar(el) for el in self])


class Keyword(ComparableExpr):
    def __init__(self, name):
        self.name = ":" + name

    def key(self):
        return (self.__repr__())

    def __str__(self):
        return (self.name)

    def __repr__(self):
        return ("Keyword: (%s)" % self.name)

    def __lt__(self, other):
        return (self.key() < other.key())

    def __eq__(self, other):
        return (self.key() == other.key())

    def __hash__(self):
        return (hash(self.key()))

    def __call__(self, env, rest):
        #return (d.get(self.key()))
        if not rest.rest().empty():
            raise TypeError("Keyword lookup takes one argument")
        return (env.eval_scalar(rest.first()).get(self.key))


class Set(frozenset):

    def __str__(self):
        inner = ' '.join([self.tostring(x) for x in x])
        return '#{%s}' % inner

    def __repr__(self):
        inner = ' '.join([str(x) for x in self])
        return '#{%s}' % inner

class Path(object):
    def __init__(self, value):
        self.name = value

    def pypath (self):
        return(self.name.replace('/', '.'))

    def path_list(self):
        return(self.name.split('/'))

    def __str__(self):
        return (self.name)
      
    def __repr__(self):
        return ('%s %s' % (x, type(self.find(x.path_list()))))

    def __call__(self, env):
        return (env.find(self.path_list()))

class FuncPath(object):
    def __init__(self, value, args):
        self.name = value
        self.args = args

    def path_list(self):
        return(self.name.split('/'))
      
    def __repr__(self):
        print(type(self))
        return ("(%s %s)" % (self.name, self.args))

    # find the function math/sin or whatever in the namespace
    # then call it with the args.
    # this really needs to push a stackframe, do the bindings like that.
    def __call__(self, env):
        # print ("funcPath Call")
        # print ("path list is:", self.path_list())
        # print ("Args are:", self.args)

        func = env.find(self.path_list())

        #print ("Func is: ", func)

        val = func(env.eval_scalar(*self.args))

        #print ("val is: ", val)
        return (val)


class Import(object):
    def __init__(self, name, asname=None):
        self.name = name
        self.asname = asname

    def __call__(self, env):
        if type(self.name) == Atom:
            name = self.name.name
        if type(self.name) == Path:
            name = self.path_list()
        else:
            name = self.name

        env.current_ns.py_import(name, self.asname)
        env.current_ns.add_import(self)

    def __repr__(self):
        if self.asname is not None:
            return ("(import %s as %s)" % (self.name, self.asname))
        else:
            return ("(import %s)" % self.name)


class Procedure(object):
    "A user-defined procedure."
    def __init__(self, parms, exp, env):
        self.parms, self.exp, self.env = parms, exp, env
    def __call__(self, *args): 
        return eval(self.exp, Env(self.parms, args, self.env))



class PyNew(object):
    def __init__(self, env, classpath, args):
        self.env = env
        self.classpath = classpath
        self.args = args

    def path_list(self):
        if '/' in self.classpath:
            return(self.attr.split('/'))
        else:
            return self.classpath

    def __repr__(self):
        return ("New %s with Args: %s" % (self.classpath, self.args))

    def __call__(self, env):
        self.__repr__()
        classobj = env.find(self.path_list())
        return(classobj(*self.args))


    
class Pyattr(object):
    def __init__(self, attr):
        self.attr = attr

    def __str__(self):
        return ("-%s" % self.attr)

    def path_list(self):
        return(self.attr.split('/'))

    def __repr__(self):
        return ('%s %s' % (x, type(self.find(x.path_list()))))

    def __call__(self, env):
        self.__repr__()
        path = self.path_list()
        return(env.find(path))

class Py_interop(object):
    def __init__(self, method, obj, args):
        self.method = method
        self.obj = obj
        self.args = args

    def __str__(self):
        return(self.__repr__())

    def __repr__(self):
        return ("%s %s %s" % (self.method, self.obj, self.args))

    def __call__(self, env):
        self.__repr__()

        # obj = env.find(self.obj)
        # print(self.method)
        # ins_method = obj.__getattribute__(self.method)
        # print(self.args)
        # r = ins_method(*self.args)
        # print ("result is", r)
        # return (r)

        return(env.find(self.obj).__getattribute__(self.method)(*self.args))



class Function(ComparableExpr):
    pass



class UnknownVariable(Exception):
    pass



class Def(object):
    def __init__(self, arg1, arg2, stackframe):
        self.symbol = arg1
        self.rest = arg2
        self.stackframe = stackframe
        # this should be unnecessary because the grammar will take care of it.
        if type(self.symbol) is not Atom:
            raise TypeError("First argument to def must be atom")
        stackframe.set_symbol(self.symbol, self.rest)
        #self.__call__(stackframe)
        #return (self.symbol)

    def __str__(self):
        return(self.symbol.name())

    def __call__(self, env):
        env.set_symbol(self.symbol.name,
                       env.eval_scalar(self.rest))
        return (self.symbol)



class Env(object):

    def __init__(self, ns=None):

        # for now it just has python callables
        # once there is a yalispy.core.yl then we
        # need to start loading it, so we have more.

        self.eval_verbose = False
        self.core_ns = namespace("plysp/core")
        self.namespaces = {"plysp/core" : self.core_ns}

        if ns is None:
            ns = "User"

        self.current_ns = namespace(ns)
        self.namespaces[ns] = self.current_ns

    def in_ns(self, name):
        if type(name) is not str:
            name = name.name  # it's a Path or an Atom
        if name in self.namespaces.keys():
            self.current_ns = self.namespaces[name]
            return (self.current_ns)
        else:
            return (None)

    def new_ns(self, name):
        if type(name) is not str:
            name = name.name  # it's a Path or an Atom
        if name not in self.namespaces.keys():
            self.current_ns = namespace(name)
            self.namespaces[name] = self.current_ns
        return(self.current_ns)

    def load_ns(self, name):
        """read a file and load it into it's ns"""
        pass

    def find(self, symbol):
        if self.eval_verbose is True:
            print ("EnV find", type(symbol), "in", self.current_ns.name)
        sym = self.current_ns.find(symbol)
        if sym == None:
            if self.eval_verbose is True:
                print ("EnV find", type(symbol), "in", self.core_ns.name)
            sym = self.core_ns.find(symbol)
        return (sym)

    def set_symbol(self, symbol, val):
        if self.eval_verbose is True:
            print ("set symbol")
            print (type(symbol))
            print (val)
        sym = self.current_ns.set_symbol(symbol, val)

    def to_string(x):
        "Convert a Python object back into a Lisp-readable string."
        if x is True: return "#t"
        elif x is False: return "#f"
        elif isa(x, Symbol): return x
        elif isa(x, str): return '"%s"' % x.encode('unicode_escape').decode('utf_8').replace('"',r'\"')
        elif isa(x, list): return '('+' '.join(map(to_string, x))+')'
        elif isa(x, complex): return str(x).replace('j', 'i')
        else: return str(x)

    def tostring(self, x):
        if x is None:
            return 'nil'
        elif type (x) is str:
            return (x)
        elif type(x) in (int, float):
            return str(x)
        elif x.__class__.__name__ in ['function', 'builtin_function_or_method']:
            return str(x)
        elif type(x) in (Atom, Keyword, list, List, namespace, Vector, Map, Set,\
                         Pyattr, Path, PyNew, FuncPath):
            return x.__str__()
        else:
            print(str(x), type(x))
            raise TypeError("Sorry can't pretty print, %s is unknown!" % x)


    def eval_scalar(self, x):
        if self.eval_verbose is True:
            print("Eval: ", x, type(x))

        if x is None:
            return
        if type(x) in (int, float, str, Keyword):
            return x
        elif type(x) in (Atom, Import, Vector, Map, List, Set, Pyattr, FuncPath, Path):
            return(x(self))
        elif type(x) is List:
            return self.eval_list(contents)
        return x


    def eval_list(self, contents):
        if contents.empty():
            return List()  # ()

        first = contents.first()
        rest = contents.rest()

        #print("Eval List: ", first, rest)

        if type(first) in (Map, Keyword, Atom):
            return(first(self, rest))

        if type(first) in (Def, Py_interop, FuncPath, Import, Pyattr):
            return (first(self))


    def eval_to_string(self,txt):
        return(self.tostring(self.eval_scalar(txt)))
        
