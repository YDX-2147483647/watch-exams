import logging
from os import makedirs, chdir
from os.path import join
from argparse import ArgumentParser

from dingding import DingDing
# spell-checker: disable-next-line
from urllib.request import getproxies as get_proxies

from fetch_notification import fetch_notification_markdown
from util import load_watches, root

from typing import Final


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
    last_message = ''
    try:
        with open(join(root, 'output/message.txt'), 'r', encoding='utf-8') as f:
            last_message = f.read()
    except FileNotFoundError:
        pass

    # compare the content
    return last_message[last_message.index('\n'):] != message[message.index('\n'):]


def save(message: str) -> None:
    makedirs(join(root, 'output/'), exist_ok=True)
    with open(join(root, 'output/message.txt'), 'w', encoding='utf-8') as f:
        f.write(message)
    logging.info(
        f"The message was saved to {join(root, 'output/message.txt')}.")


def ding(message: str) -> None:
    with open(join(root, 'config/ding_secrets.txt'), 'r', encoding='utf-8') as f:
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
    chdir(root)  # Therefore the script can be called from anywhere.

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
