import dknovautils as dku

from dknovautils.dkat import AT
from dknovautils.myadd import m_add


def test_ccc():

    print(f"version: {AT.VERSION}")

    assert m_add(1, 2) == 3


if __name__ == "__main__":
    test_ccc()
