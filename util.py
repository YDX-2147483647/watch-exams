from os.path import dirname, join, realpath
from typing import Final

from pandas import read_csv

root: Final = dirname(realpath(__file__))


def load_watches() -> list[str]:
    watches = read_csv(join(root, 'config/watches.csv'),
                       encoding='utf-8', comment='#',)

    return list(watches['学号'])
