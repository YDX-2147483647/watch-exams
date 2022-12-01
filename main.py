import logging
from argparse import ArgumentParser
from typing import Final
# spell-checker: disable-next-line
from urllib.request import getproxies as get_proxies

from dingding import DingDing

from fetch_notification import fetch_notification_markdown
from util import load_watches, root


def prepare_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Watch exam plans.')
    parser.add_argument(
        '--ding',
        help='Send the message to Ding if anything has changed.',
        default=False,
        action='store_true'
    )
    parser.add_argument(
        '--force',
        help='Force update message.txt.',
        default=False,
        action='store_true'
    )
    parser.add_argument(
        '--verbose',
        help='Print verbose messages.',
        default=False,
        action='store_true'
    )

    return parser


def get_fixed_proxies() -> dict[str, str]:
    proxies = get_proxies()
    if 'https' in proxies:
        if 'localhost' in proxies['https'] or '127.0.0.1' in proxies['https']:
            proxies['https'] = proxies['https'].replace('https://', 'http://')
    return proxies


def has_changed(message: str) -> bool:
    last_message = '\n'
    try:
        with open(root / 'output/message.txt', 'r', encoding='utf-8') as f:
            last_message = f.read()
    except FileNotFoundError:
        pass

    # compare the content
    return last_message[last_message.index('\n'):] != message[message.index('\n'):]


def save(message: str) -> None:
    output_dir = root / 'output'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'message.txt'

    # Backup the old
    old_output_file = output_file.with_stem('message-old')
    old_output_file.unlink(missing_ok=True)
    try:
        output_file.rename(old_output_file)
    except FileNotFoundError:
        pass

    # Save the new
    with output_file.open('w', encoding='utf-8') as f:
        f.write(message)
    logging.info(
        f"The message was saved to {output_file}.")


def ding(message: str) -> None:
    with open(root / 'config/ding_secrets.txt', 'r', encoding='utf-8') as f:
        access_token: Final
        secret: Final
        access_token, secret = [
            line.strip()
            for line in f.readlines()
            if not line.startswith('#')
        ]

    ding = DingDing(access_token)
    ding.set_secret(secret)

    ding.send_markdown('学生考试安排', message)
    logging.info('The message was sent to Ding.')


if __name__ == '__main__':
    parser = prepare_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    message = fetch_notification_markdown(
        watches=load_watches(),
        proxies=get_fixed_proxies()
    )

    should_update: Final = args.force or has_changed(message)

    if not should_update:
        print('Nothing updated.')
    else:
        print(message)

        if args.ding:
            ding(message)

        save(message)
