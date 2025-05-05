import logging
import re
import subprocess
import shlex


def get_cmd_output(cmd):
    """ Execute a command and returns the output.

    :param str cmd: Command to execute.
    :returns: Command stdout content.
    :raises: ValueError with stderr content if their is one.
    """
    logging.debug(cmd)
    args = shlex.split(cmd)
    process = subprocess.Popen(args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, strerr = process.communicate()
    logging.debug(stdout)
    if strerr:
        raise ValueError(strerr.decode())
    return stdout.decode()


def get_current_version():
    """ Get the latest version using `git describe`.
    The default version is 0.0.0.

    :return: tuple (major, minor, hotfix)
    :rtype: (int, int, int)
    """
    output = get_cmd_output("git describe --always")
    tag_regex = r"(?P<major>\d+).(?P<minor>\d+).(?P<hotfix>\d+)-?.*"
    result = re.search(tag_regex, output)
    if result is None:
        logging.warning("Warning: no tag matching the format Major.Minor.Hotfix detected")
        return (0, 0, 0)
    groups = result.groupdict()
    return (int(groups['major']), int(groups['minor']), int(groups['hotfix']))
