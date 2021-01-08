from options import parse_cli
import logs
import logging
import yaml
from repl import repl, compiler
from os.path import isfile

logger = logging.getLogger("plysp")

AS = {
    "config": {},
    "args": {},
    "defaults": {
        "config_file": "plysp-defaults.yaml",
        "loglevel": "debug",
        "logfile": "plysp.log",
        "prompt": "\nPlysp - %s > ",
    },
}


def get_in(dict_tree, keys):
    """
    Retrieve a value from a dictionary tree, using a key list
    Returns:
       The value found at the given key path, or `None` if
       any of the keys in the path is not found.
    """
    logger.debug(keys)
    try:
        for key in keys:
            logger.debug("key %s" % key)
            if dict_tree is None:
                return None
            dict_tree = dict_tree.get(key)

        return dict_tree

    except KeyError:
        return None
    except TypeError:
        return None


# could have been a partial.
def get_in_config(keys):
    "Get stuff from the config, takes a list of keys."
    return get_in(AS, ["config"] + keys)


def save_yaml_file(filename, dictionary):
    "Write a dictionary as yaml to a file"
    with open(filename, "w") as f:
        yaml.dump(dictionary, f)


def load_yaml_file(filename):
    "load a dictionary from a yaml file"
    if isfile(filename):
        with open(filename) as f:
            someyaml = yaml.load(f, Loader=yaml.FullLoader)
        return someyaml
    else:
        logger.warning("Unable to load %s" % filename)


def save_config(filename):
    "Save the configuration."
    save_yaml_file(filename, AS["config"])


def load_config(filename):
    """load a yaml file into the application's
    configuration dictionary.
    """
    AS["config"] = load_yaml_file(filename)


def log_lvl(lvl):
    """Change the logging level."""
    logs.set_level(logging.getLogger("plysp"), lvl)


def do_something(compiler):
    """
    Maybe start the REPL,
    or Run a file given on the cli.
    """

    # Might need multiple files here. would be nice.
    files = AS["args"]["Files"]

    if len(files):
        for f in files:
            logger.info("Loading: %s" % f)
            compile_file(compiler, f)

    # Run the repl.
    if AS["args"]["repl"]:
        repl(compiler, prompt=get_in(AS, ["args", "prompt"]))


def compile_file(comp, filename):
    """Open, read, and compile/evaluate a file."""
    with open(filename, "r") as reader:
        for line in reader:
            if line != "\n":
                logs.logdebug(logger, "*** %s" % line)
                print(comp.parseit(line))


def init(defaults={}):
    """
    Merge defaults,
    Parse the cli parameters,
    load the default config or the configuration given,
    start logging, Do something.
    """
    global AS
    global logger
    # merge the dict from the function layer into the App State.
    # if there are defaults, we want to get them there.
    # python 3.9 syntax to merge two dictionaries.
    merge = AS | defaults
    AS = merge

    AS["args"] = vars(parse_cli(AS["defaults"]))

    if AS["args"]["config_file"]:
        AS["config"] = load_yaml_file(AS["args"]["config_file"])
    else:
        AS["config"] = load_yaml_file(get_in(AS, ["defaults", "config_file"]))

    logfile = get_in(AS, ["args", "logfile"])
    if logfile is None:
        logfile = get_in_config(["files", "logfile"])
    if logfile is None:
        logfile = get_in(AS, ["defaults", "logfile"])

    loglvl = get_in(AS, ["args", "loglevel"])
    if loglvl is None:
        loglvl = get_in_config(["files", "loglevel"])
    if loglvl is None:
        loglvl = get_in(AS, ["defaults", "loglevel"])
    if loglvl is None:
        loglvl = "info"

    print(loglvl)

    logger = logs.add_file_handler(logger, loglvl, logfile)
    # logger = logs.add_file_handler(logging.getLogger(), loglvl, "plysp.log")

    logger.debug("Hello from the logger")

    comp = compiler()
    do_something(comp)
