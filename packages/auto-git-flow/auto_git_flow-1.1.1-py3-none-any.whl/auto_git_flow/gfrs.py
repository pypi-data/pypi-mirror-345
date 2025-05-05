""" Entry point for gfrs. """
import sys
import logging
import argparse

from auto_git_flow.utils import get_current_version, get_cmd_output


def main():
    parser = argparse.ArgumentParser(
        prog='gfrs',
        description='Create a new hotfix branch'
    )
    parser.add_argument("m",
                        nargs='?',
                        help="start a new major release")
    parser.add_argument('--major',
                        '-m',
                        action='count',
                        default=0)
    parser.add_argument('--verbose',
                        '-v',
                        action='count',
                        default=0)
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

    if args.major or args.m == 'm':
        major += 1
        minor = 0
        hotfix = 0
    else:
        minor += 1
        hotfix = 0

    cmd = f"git flow release start {major}.{minor}.{hotfix}"

    print(cmd)
    try:
        print(get_cmd_output(cmd))
    except ValueError as exc:
        logging.error(exc)
        return 1


if __name__ == '__main__':
    sys.exit(main())
