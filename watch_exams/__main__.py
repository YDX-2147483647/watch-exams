import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import Final

# spell-checker: disable-next-line
from urllib.request import getproxies as get_proxies

from .display import to_markdown
from .fetch import fetch_plans
from .save import Saver
from .util import ding, load_watches


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Watch exam plans.")
    parser.add_argument(
        "--ding",
        help="Send the message to Ding if anything has changed.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--force", help="Force update message.txt.", default=False, action="store_true"
    )
    parser.add_argument(
        "--verbose", help="Print verbose messages.", default=False, action="store_true"
    )

    return parser


def get_fixed_proxies() -> dict[str, str]:
    proxies = get_proxies()
    if "https" in proxies:
        if "localhost" in proxies["https"] or "127.0.0.1" in proxies["https"]:
            proxies["https"] = proxies["https"].replace("https://", "http://")
    return proxies


def main() -> None:
    args = build_parser().parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

    # 1. Prepare paths

    root: Final = Path.cwd()
    saver = Saver(output_dir=root / "output")

    # 2. Get messages

    plans, note = fetch_plans(
        watches=load_watches(root / "config/watches.csv"),
        proxies=get_fixed_proxies(),
    )
    saver.message = to_markdown(plans, note)

    # 3. Update

    if not args.force and not saver.changed():
        print("Nothing updated.")
    else:
        print(saver.message)

        if args.ding:
            ding(
                saver.diff(),
                secrets_file=root / "config/ding_secrets.txt",
            )

        saver.save()


main()
