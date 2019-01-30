# plysp

I've been interested in having a lisp with access to the python system for
a while. Everytime I code in Python I miss Lisp. I like python too, but
sometimes I just don't want to swap out my functional brain for the OO brain
just to write something with a python library.

I really like clojure, and that seems like a good fit in many ways, it has
dictionaries, and sets and lists... But a clojure
on top of python is really a different animal than one on top of java. Also, 
Clojure is a beast at this point. It seems unreasonable to think that a 
python version of clojure would survive and thrive.  
It's been done before, and it's not happening.

I've written other languages, and I like working with 
[BNF](https://en.wikipedia.org/wiki/Backus–Naur_form) grammars, I'm still not
sure that's a good fit for a lisp. But that's what I'm doing here. I played around with
Lex and Yacc for a bit, considered doing it all in C, with a python interpreter embedded.
Then I found Cython and [PLY](http://www.dabeaz.com/ply/), and I thought, why not try that.

So here it is, so far.  

## Capabilities so far

It is, at this point, just an interpreter.  Run it like this, you must have python 3.

`python repl.py`

The parser creates python objects.  Compiling is essentially pickling (when I get to it).  
And runtime is asking the objects to execute.

There are a set of commands in the repl that you can execute to change the behavior and to
see what is going on in the lexer and parser.

-help at the repl prompt will give a list of the commands.

There are namespaces, and a stack of stackframes.  There is no reall way to do a *let* yet
so scoping is kind of limited.  Also there's no way to make a function yet. So
really this is just a toy at this point.

Basic python interop and namespaces do work.  You can create an instance of somthing and then
use it, and you can access python libraries like math. all the core functions of python
are imported into the core namespcae automatically. 

`(import math as "m")`  Will let you do things like `(m/sin 2)` and `(-m/pi)`  --> 3.142527...

The *-* is for attributes in the library. This is following clojure's syntax for accessing 
class attributes in java.

Although that is not really needed.  Math is imported as `math` into the core namespace so
`(math/sin 2)` works out of the box.  also the operators are there so `(+ 1 1 5)`  also works.
You can define variables.  `(def x 10)`  Then use them.  `(+ x 3)`  or `(math/sin x)`
More complex things work too.  `(+ x (math/sin x) 1000)` what ever you like.

Named arguments have some work ahead. 
Macros are on the way as are
lambdas *fn* and the rest of the core symbols needed to write everything else.

There are immutable lists, vectors, hashmaps, sets, etc.  There isn't too much to do with
them yet because I haven't gotten to the point of surfacing their API's in the language.
But that will be easy when the time comes.


Testing is pretty much non-existant. There are a few things there.


## drawing the line between core, and lang.

The plan is to  move a bit more of the internals into python/C instead of doing it in the 
language itself as is done in most lisps including clojure.  
Where to draw the line between what the
language implements itself and what is in the core is an interesting question.  My thought is
that most of what a lisp does, is maintain scope, which is how we get deconstruction of parameters
into a signature, so having as much of that as possible in C is going to be more performant. 
It's still not very much code, and it makes things a little easier as the bootstrap layer to 
the language is much thinner.

The plan is to move all of the classes which represent the core language into Cython classes.
That should give good performance while still allowing the use of python libraries as we desire.

Compiling is a matter of parsing the code into it's objects and then pickling the result. Reloading
the pickled code would give an executable that would run in the runtime.  Of course this means
breaking up the parser and the interpreter/repl. All doable.

### symbol table - or not.

Another oddity, is using the tokenizer to find the reader macro symbols. #/\'\"\` etc. Most lisps
have a symbol table for this stuff. Even clojure, which doesn't let you change them like most
lisps do. I really haven't decided one way or another. But in the interest of getting it working
quickly I just made them tokens. Which then depending on their patterns, get turned into objects
in the parser.  The end affect is the same. So I'm not sure how a parser table might make things
better or worse.

## Related Projects.

### Clojure

This isn't clojure. I've read a lot of source code for clojure and this isn't that.
Going with a [BNF](https://en.wikipedia.org/wiki/Backus–Naur_form) 
parser changes things from the start. But, I know clojure, and I have
studied the syntax and behavior. So it's related.  
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

There is also [Hylang] (https://github.com/hylang/hy)  For me this language falls short. It is
too intertwined and dependent upon how python works. It doesn't have scoping or a *Let*. That
just isn't a lisp to me.  It looks like a lisp.  But it doesn't act like a lisp.


### Peter Norvig's [Lis.py](http://www.norvig.com/lispy.html) and 
[Lispy.py](https://norvig.com/lispy2.html)

Peter Norvig wrote a couple of articles on building your own lisp
(scheme) in python. They are popular articles, but I find the code pretty
sloppy. The original versions can be found with some effort, but there are
better versions out there.  Peter wrote 2 versions. lis.py and lispy.py.
Lispy.py is the better, more capable version.

IMHO, The best adaptations, that I have found, of Peter's Lispys are these. 
[Adam Haney's Lispy with dialects] (https://github.com/adamhaney/lispy)
and 
[Norvigs Lisps for Py3k](https://github.com/Shambles-Dev/Norvig_Lisps_for_Py3k) 
which is a cleaned up version of the originals. They stay close to the
originals but with better coding style.

[another more advanced lispy](https://github.com/ridwanmsharif/lispy)

### Learn C and build your own Lisp.

Another good resource for lisps is [Learn C and build your own Lisp](https://github.com/orangeduck/BuildYourOwnLisp)  I already know C, but this is a fun project and a great way to learn C and a lisp similar to Scheme.




