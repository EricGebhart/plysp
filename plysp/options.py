import argparse
import textwrap

help_prefix = textwrap.dedent(
    """\
       This is a lisp interpreter with clojure like syntax, Namespaces
       and full python interoperability"""
)


help_suffix = textwrap.dedent("""""")


def get_argp():
    """Get an argument parser."""
    return argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=help_prefix,
        epilog=help_suffix,
    )


def create_parser(defaults):
    """Create argument parser."""
    parser = get_argp()

    parser.add_argument(
        "--config-file", dest="config_file", type=argparse.FileType(mode="r")
    )

    parser.add_argument(
        "--logfile",
        default=defaults["logfile"],
        help="logfile to use",
    )

    parser.add_argument("-r", "--repl", action="store_true", help="Start a REPL")

    parser.add_argument(
        "-p",
        "--prompt",
        default=defaults["prompt"],
        help="REPL Prompt, should have spot for namespace.",
    )

    # One file or many ?
    # parser.add_argument("file", help="input filename", metavar="FILE")
    parser.add_argument("Files", nargs="*")

    return parser


def parse_cli(defaults):
    """parse the command line, provide a dictionary for the defaults."""
    return create_parser(defaults).parse_args()
