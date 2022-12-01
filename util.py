from pathlib import Path
from typing import Final

from pandas import read_csv

root: Final = Path(__file__).parent


def load_watches() -> list[str]:
    watches = read_csv(root / 'config/watches.csv',
                       encoding='utf-8', comment='#', dtype=str)

    return list(watches['学号'])
