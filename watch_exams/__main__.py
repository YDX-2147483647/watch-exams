import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import Final

# spell-checker: disable-next-line
from urllib.request import getproxies as get_proxies

from .fetch_notification import fetch_notification_markdown
from .util import compare, ding, has_changed, load_watches


def prepare_parser() -> ArgumentParser:
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


def update_file(message: str, output_file: Path, old_output_file: Path) -> None:
    """备份并更新 message.txt"""

    # Backup the old
    old_output_file.unlink(missing_ok=True)
    try:
        output_file.rename(old_output_file)
    except FileNotFoundError:
        pass

    # Save the new
    output_file.write_text(message, encoding="utf-8")
    logging.info(f"The message was saved to {output_file}.")


if __name__ == "__main__":
    parser = prepare_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    # 1. Prepare paths

    root: Final = Path.cwd()
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "message.txt"

    # 2. Get messages

    message = fetch_notification_markdown(
        watches=load_watches(root / "config/watches.csv"), proxies=get_fixed_proxies()
    )

    if output_file.exists():
        old_message: str | None = output_file.read_text(encoding="utf-8")
    else:
        old_message = None

    # 3. Update

    should_update: Final = args.force or has_changed(message, old_message)

    if not should_update:
        print("Nothing updated.")
    else:
        print(message)

        if args.ding:
            ding(
                compare(message, old_message),
                secrets_file=root / "config/ding_secrets.txt",
            )

        update_file(
            message,
            output_file=output_file,
            old_output_file=output_file.with_stem("message-old"),
        )
