""" Entry point for gfhs. """
import argparse
import logging
import sys

from auto_git_flow.utils import get_current_version, get_cmd_output


def main():
    parser = argparse.ArgumentParser(
        prog='gfhs',
        description='Create a new hotfix branch'
    )
    parser.add_argument('--verbose', '-v', action='count', default=0)
    args = parser.parse_args()

    logging.basicConfig(
        format="%(message)s",
        level={
            1: "INFO",
            2: "DEBUG"
        }.get(args.verbose, "WARNING")
    )
    logging.info(args)

    major, minor, hotfix = get_current_version()

    cmd = f"git flow hotfix start {major}.{minor}.{hotfix+1}"

    print(cmd)
    try:
        print(get_cmd_output(cmd))
    except ValueError as exc:
        logging.error(exc)
        return 1


if __name__ == '__main__':
    sys.exit(main())
