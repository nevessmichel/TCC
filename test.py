from Models.Base import Base
from Models.sma import SMA

def test():
    sma = SMA
    print(issubclass(sma, Base))
    print(isinstance(sma(), Base))


if(__name__ == "__main__"):
    test()