#!/usr/bin/env python

import re
import traceback
import logging
from logs import logdebug

from lexer import PlyspLex
from parser import PlyspParse
from core import eval_to_string
from namespace import Env

logger = logging.getLogger("plysp")
debug = logdebug


class compiler(object):
    def __init__(self):

        self.env = Env(
            compiler=self, name="/"
        )  # Parent Env to all envs and namespaces.
        self.lexer = PlyspLex().build()
        self.parser = PlyspParse(self.env).build()
        self.test_lexer = False
        self.test_parser = False
        self.command_prefix = "-"
        self.basepath = None

        self.compile_file("plysp/plysp/core.yl")

        # just to check... works...
        self.env.refer(["plysp", "core"])

    def current_ns(self):
        return self.env.current_ns

    def lexit(self, txt):
        self.lexer.input(txt)
        return [tok for tok in self.lexer]

    def parseit(self, txt):
        # get rid of the ignored sexprs. ie. #_(...)
        if self.test_lexer is True:
            l = self.lexit(txt)
            return l

        elif self.test_parser is True:
            pt = self.parser.parse(txt, lexer=self.lexer)
            print("-------")
            return pt

        else:
            pt = self.parser.parse(txt, lexer=self.lexer)
            return eval_to_string(pt, self.env.current_ns)

    def load_lib(self, namepath):
        path = os.path.join(self.basepath, namepath) + ".yl"
        self.compile_file(path)

    def compile_file(self, filename):
        """Open, read, and compile/evaluate a file."""
        if self.basepath is None:
            self.basepath = os.path.split(filename)

        i = 1
        txt = ""
        with open(filename, "r") as reader:
            for line in reader:
                if line != "\n":
                    txt += line
                    debug(logger, "*** [%d] %s" % (i, line))
                    if balanced(txt) == 0:
                        print(self.parseit(txt))
                        txt = ""
                    i = i + 1

        if len(txt):
            print("Error: missing ()'s, %s" % txt)

    def command_help(self):
        print("Command prefix is %s" % self.command_prefix)
        print("Available commands are: help, lex, parse, verbose, quiet")

    def toggle_lexer(self):
        if self.test_lexer is False:
            self.test_lexer = True
            print("Testing Lexer Mode On")
        else:
            self.test_lexer = False
            print("Testing Lexer Mode Off")

    def toggle_parser(self):
        if self.test_parser is False:
            self.test_parser = True
            print("Testing parser Mode On")
        else:
            self.test_parser = False
            print("Testing parser Mode Off")

    def commands(self, txt):
        txt = txt[len(self.command_prefix) :]
        if txt == "help":
            self.command_help()

        elif txt == "lex":
            self.toggle_lexer()

        elif txt == "parse":
            self.toggle_parser()

        elif txt == "eval verbose" or txt == "verbose":
            self.env.eval_verbose = True

        elif txt == "eval quiet" or txt == "quiet":
            self.env.eval_verbose = False

        elif txt == "showns":
            print("attributes")
            print(self.env.current_ns.show_attributes())
            # print (self.env.current_ns.show_methods())
            print("python callables")
            print(self.env.current_ns.show_python_callables())

        elif txt == "show ns":
            txt = input("namespace name: ")
            print("attributes")
            print(self.env.namespaces[txt].show_attributes())
            # print (self.env.namespaces[txt].show_methods())
            print("python callables")
            print(self.env.namespaces[txt].show_python_callables())

        else:
            print("command %s not known" % txt)

        # not sure why this doesn't work here. It worked in the repl.
        # it's not an ideal solution anyway...
        # return (List[sexpr for sexpr in t if type(sexpr) is not Ignore])


try:
    import readline
except ImportError:
    pass
else:
    import os

    histfile = os.path.join(os.path.expanduser("~"), ".plysphist")
    try:
        readline.read_history_file(histfile)
    except IOError:
        # Pass here as there isn't any history file, so one will be
        # written by atexit
        pass
    import atexit

    atexit.register(readline.write_history_file, histfile)


def balanced(txt):
    opens = re.findall(r"\(", txt)
    closes = re.findall(r"\)", txt)
    return len(opens) - len(closes)


def repl(comp, prompt="\nPlysp - %s > "):
    comp.command_help()
    prmpt = prompt
    while True:
        try:
            txt = ""
            while True:
                txt += input(prmpt % comp.current_ns())
                if re.search(r"^\s*$", txt):
                    continue

                well_formed = balanced(txt)

                if well_formed == 0:
                    prmpt = prompt
                    debug(logger, "balanced: %s" % txt)
                    break

                if well_formed < 0:
                    # Syntax Error, too many parentheses.
                    break

                if well_formed > 0:
                    prmpt = "..."
                    txt += " "

            if txt[0 : len(comp.command_prefix)] == comp.command_prefix:
                comp.commands(txt)
            else:
                debug(logger, txt)
                print(comp.parseit(txt))

        except EOFError:

            break
        except KeyboardInterrupt:
            print  # Give user a newline after Cntrl-C for readability
            break
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            logger.info(e)
            logger.info(traceback.format_exc())
            #  return 1  <-- for now, we assume interactive session at REPL.)
            #  later/soon, we should handle source files as well.


# if __name__ == "__main__":
#     exit_code = main()
#     if exit_code:
#         sys.exit(exit_code)
