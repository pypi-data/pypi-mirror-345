import argparse

from .commands import clone


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    clone.add_subparser(subparsers)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
