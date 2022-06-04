from os.path import dirname, realpath, join
from typing import List, Final

root: Final = dirname(realpath(__file__))


def load_watches() -> List[str]:
    with open(join(root, 'config/watches.txt'), 'r', encoding='utf-8') as f:
        watches: List[str] = [
            s.strip()
            for s in f.readlines()
            if not s.startswith('#')
        ]
    return watches
