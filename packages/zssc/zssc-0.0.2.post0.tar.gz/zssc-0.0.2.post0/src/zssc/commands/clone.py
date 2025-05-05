import os
import pathlib

HTTPS_PREF = "https://github.com/"
SSH_PREF = "git@github.com:"


def add_subparser(subparsers):
    parser = subparsers.add_parser("clone")
    parser.add_argument(
        "url",
        type=str,
        help="Remote URL to clone",
    )
    parser.add_argument(
        "--target_dir",
        "-t",
        type=str,
        default=None,
        help="Local directory to clone to",
    )
    parser.set_defaults(func=main)


def main(args):
    if args.target_dir is None:
        args.target_dir = os.getenv("GITHUB_ROOT", ".")
    target_dir = pathlib.Path(args.target_dir)
    url = args.url

    if url.startswith(HTTPS_PREF):
        if "?" in url:
            url = url[: url.index("?")]
        if "#" in url:
            url = url[: url.index("#")]
        if url.endswith(".git"):
            url = url[: -len(".git")]
        repo = url[len(HTTPS_PREF) :]
    elif url.startswith(SSH_PREF) and url.endswith(".git"):
        repo = url[len(SSH_PREF) : -len(".git")]
    elif url.count("/") == 1:
        repo = url
        url = f"{HTTPS_PREF}{url}"
    else:
        raise ValueError(f"Invalid URL: {url}")

    cmd = f"git clone {url} {target_dir / repo}"
    os.system(cmd)
