from Models.Base import Base

# Simple Moving Average (SMA)
class SMA(Base):

    @staticmethod
    def getName():
        return "SMA"

    def predict(self, vector, size):
        return sum(vector)/size