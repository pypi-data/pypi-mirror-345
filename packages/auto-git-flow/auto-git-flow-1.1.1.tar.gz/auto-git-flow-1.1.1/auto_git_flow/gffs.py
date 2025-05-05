""" Entry point for gffs. """
import argparse
import logging
import sys

from auto_git_flow.utils import get_cmd_output


def main():
    parser = argparse.ArgumentParser(
        prog='gffs',
        description='Create a new feature branch'
    )
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('feature', nargs=1, help='feature name')
    args = parser.parse_args()

    logging.basicConfig(
        format="%(message)s",
        level={
            1: "INFO",
            2: "DEBUG"
        }.get(args.verbose, "WARNING")
    )
    logging.info(args)

    feature = args.feature[0]
    cmd = f"git flow feature start {feature}"

    print(cmd)
    try:
        print(get_cmd_output(cmd))
    except ValueError as exc:
        logging.error(exc)
        return 1


if __name__ == '__main__':
    sys.exit(main())
