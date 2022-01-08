from Models.Base import Base

# Simple Moving Average (SMA)
class SMA(Base):
    def predict(self, vector, size):
        return sum(vector)/size