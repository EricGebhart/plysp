import logging
import sys
import inspect

message_fmt = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"

stdout_format = "%(message)s"

# message_fmt = '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s'
# message_fmt = '[%(levelname)s] %(name)s %(asctime)s - %(message)s'
message_fmt = "[%(name)s] %(asctime)s - %(message)s"


def validate_loglevel(loglevel):
    nloglevel = getattr(logging, loglevel.upper(), None)
    if not isinstance(nloglevel, int):
        raise ValueError("Invalid log level: %s" % nloglevel)
    return nloglevel


# this one was not working but maybe it will now. I'd like
# to study it.
def start_logging(loglevel):
    """Start up logging with 2 handlers. One for the logfile and
    on for stdout. Set the log level the same to all loggers."""

    nloglevel = validate_loglevel(loglevel)

    # file_handler = logging.FileHandler(logfile)
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [stdout_handler]
    logger = logging.getLogger()

    logging.basicConfig(
        encoding="utf-8", format=message_fmt, level=nloglevel, handlers=handlers
    )

    return logger()


def set_level(logger, lvl):
    "Set the level for the logger."
    logger.setLevel(validate_loglevel(lvl))


# log = logging.getLogger()
def add_file_handler(logger, loglevel, filename):
    """
    Takes a logger, a string loglevel, and a filename,
    to create and add a file handler to a logger.
    """
    nloglevel = validate_loglevel(loglevel)
    fh = logging.FileHandler(filename, mode="w", encoding="utf-8")
    fh.setFormatter(logging.Formatter(message_fmt))
    # if we set these, then changing the root level has no effect.
    # fh.setLevel(nloglevel)
    logger.addHandler(fh)
    logger.setLevel(nloglevel)

    return logger


# log = logging.getLogger()
def add_stdout_handler(logger, loglevel):
    """"setup a root level logger with the stdout handler"""
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter(stdout_format))
    # out_hdlr.setLevel(logging.INFO)
    logger.addHandler(out_hdlr)
    logger.setLevel(logging.INFO)

    return logger


def get_class_from_frame(fr):
    args, _, _, value_dict = inspect.getargvalues(fr)
    # we check the first parameter for the frame function is
    # named 'self'
    if len(args) and args[0] == "self":
        # in that case, 'self' will be referenced in value_dict
        instance = value_dict.get("self", None)
        if instance:
            # return its class
            return str(getattr(instance, "__class__", None)).split(" ")[-1][1:-2]
    # return None otherwise
    return None


def logdebug(logger, message):
    "Add in function details for debug messages."

    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    frame = inspect.currentframe().f_back
    func = frame.f_code
    cname = get_class_from_frame(frame)
    # filename = func.co_filename.split("/")[-1]
    funcname = "[%s : %i]" % (func.co_name, func.co_firstlineno)
    logger.debug("[ %-20s %-20s ] %s" % (cname, funcname, message))
