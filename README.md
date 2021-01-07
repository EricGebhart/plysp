# plysp

I've been interested in having a lisp with access to the python system for
a while. Every time I code in Python I miss Lisp. I like python too, but
sometimes I just don't want to swap out my functional brain for the OO brain
just to write something with a python library.  I miss multi-arity, multi-functions,
map, reduce, and easy list manipulation. cond and condp. Let. Nice deconstructors.

I really like clojure, and that seems like a good fit in many ways, it has
dictionaries, and sets and lists... But a clojure
on top of python is really a different animal than one on top of java. Also, 
Clojure is a beast at this point. It seems unreasonable to think that a 
python version of clojure would survive and thrive.

I've written other languages, and I like working with 
[BNF](https://en.wikipedia.org/wiki/Backus–Naur_form) grammars, I'm still not
sure that's a good fit for a lisp. But that's what I'm doing here. I played around with
Lex and Yacc for a bit, considered doing it all in C, with a python interpreter embedded.
Then I found Cython and [PLY](http://www.dabeaz.com/ply/), why not try that.

So here it is, so far.

## Capabilities so far

It is, at this point, just an interpreter.  Run the Repl like this, 
you must have python 3.

`python plysp -r`

The parser creates python objects.  Compiling is essentially pickling (when I get to it).
And runtime is asking the objects to execute.

There are a set of commands in the repl that you can execute to change
the behavior and to see what is going on in the lexer and parser. This
should be going away soon, but there will be a better equivalent.

-help at the repl prompt will give a list of the commands.

### Namespaces, Python interop, lambda, etc.

There are namespaces, scoping, lambda, define, python interop, immutable collections.

Namespaces, python interop, it all works. You can create an instance
of somthing and then use it, and you can access python libraries like
math. all the core functions of python are imported into the core
namespace automatically.

`(import math as "m")`  Will let you do things like `(m/sin 2)` and `(.-m/pi)`  --> 3.142527...

Although, the python builtins, math, cmath, operators, py-reduce, and py-partial are
imported as part of the plysp core namespace.

The *.-* is for attributes in the library. This is following clojure's dot syntax 
for accessing class attributes in java.

Math is imported as `math` into the core namespace so `(math/sin 2)`
works out of the box.  The operators are there so `(+ 1 1 5)`
also works. You can define variables.  `(def x 10)`  Then use them.
`(+ x 3)`  or `(math/sin x)` More complex things work too.  `(+ x
(math/sin x) 1000)` what ever you like.

### Lambdas

They work:  `((fn [x] (* x x)) 10)`  --> 100
To make a named function: `(def sqr (fn [x] (* x x)))`

### Still To go

There are some miscellaneous foundation bits to tie together 
and then all the special symbols which will allow for the creation of Macros.

The problems are fewer and fewer, Sometimes I wonder if it is because of the
parser that I have caused difficulties, but usually, it's just I haven't looked
at it the right way yet.  This also works.

```clojure
    Plysp - User > (def make-incr (fn [x] (fn [y] (+ y x))))
    make-incr

    Plysp - User > ((make-incr 5) 5)
    10

    Plysp - User > (def incv (make-incr 5))
    incv

    Plysp - User > (incv 4)
    9

    (def make-incr (fn [x] (fn [y] (+ y x))))
    (def incv (make-incr 5))
    (incv 4)
```
    
### symbol table - or not.

Another oddity, is using the tokenizer to find the reader macro symbols. #/\'\"\` etc. Most lisps
have a symbol table for this stuff. Even clojure, which doesn't let you change them like most
lisps do. I really haven't decided one way or another. But in the interest of getting it working
quickly I just made them tokens. Which then depending on their patterns, get turned into objects
in the parser.  The end affect is the same. So I'm not sure how a parser table might make things
better or worse.

## Related Projects.

### Clojure

This isn't clojure. I am a clojure programmer, and this is not that.
Going with a [BNF](https://en.wikipedia.org/wiki/Backus–Naur_form) 
parser changes things from the start. But, I know clojure, and I have
studied source. So it's related, like all lisps.
[Clojure is here](https://github.com/clojure/clojure)

### Clojure-py

[Clojure-PY](https://github.com/rcarmo/clojure-py) is, I think, as close as you
can get to a direct port of clojure to python. It's old and stale now. It's performance
was not great. So, why think something else might work?  I don't. But this is fun, and
maybe it will.

### PyClojure

There is also [Pyclojure](http://github.com/halgari/clojure-py) It's really not
any further than using ply to tokenize and parse a clojure program. And
anyone who has ever written a language knows, just because you have
a tokenizer and parser that doesn't throw up when you feed it what it
expects, that doesn't mean you actually have something useful. It's a
start.  And this project uses the immutable lists, vectors and Maps from
[funktown](https://github.com/zhemao/funktown) Which I wouldn't have known
about otherwise. It might still be better to use the immutable collections
from Clojure-py, but I don't know. I like the simplicity of using funktown so far.

### Hylang

There is also [Hylang] (https://github.com/hylang/hy)  
For me this language falls short. It is
too intertwined and dependent upon how python works. 
The last time I checked It still doesn't have scoping or a *Let*. That
just isn't a lisp to me.  It looks like a lisp.  But it doesn't act like a lisp.


### Peter Norvig's Lispys
[Lis.py](http://www.norvig.com/lispy.html) and 
[Lispy.py](https://norvig.com/lispy2.html)

Peter Norvig wrote a couple of essays on building your own lisp
(scheme) in python. I recommend them for understanding compilers
and interpreters. The code is not Black, but Black will mostly fix it.

The best adaptations, that I have found, of Peter's Lispys are these. 
[Adam Haney's Lispy with dialects] (https://github.com/adamhaney/lispy)
and 
[Norvigs Lisps for Py3k](https://github.com/Shambles-Dev/Norvig_Lisps_for_Py3k) 
which is a cleaned up python 3 version of the originals. 

[another more advanced lispy](https://github.com/ridwanmsharif/lispy)

### Learn C and build your own Lisp.

Another good resource for lisps is [Learn C and build your own Lisp](https://github.com/orangeduck/BuildYourOwnLisp)  I already know C, but this is a fun project and a great way to learn C and a lisp similar to Scheme.

### MAL - Make a lisp. 

Everyone should [make a lisp.](https://github.com/kanaka/mal)


