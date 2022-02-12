from predictor import Base

class WMA(Base):

    @staticmethod
    def getName():
        return "WMA"

    def predict(self, vector, size):
        multipliers = 0
        partial = 0
        for i in range(size):
            partial += vector[i] * (i + 1)
            multipliers += i + 1
        return partial / (size + multipliers)