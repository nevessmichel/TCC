from predictor import Base

class EMA(Base):
    def __init__(self, smoothing = 2):
        self.__smoothing = smoothing
        self.__firstDone = False
        self.__yesterday = 0
        self.__oldSize = 0

    @staticmethod
    def getName():
        return "EMA"

    def setSmoothing(self,smoothing):
        self.__smoothing = smoothing

    def predict(self, vector, size):
        
        multiplier = self.__smoothing/(1+size)
        if(not self.__firstDone or self.__oldSize != size):
            yesterday = 0
            for i in range(size):
                yesterday = (vector[i] * multiplier) + (yesterday * (1-multiplier))
            self.__yesterday = yesterday
            self.__firstDone = True
            self.__oldSize = size
        else:
            self.__yesterday = (vector[-1] * multiplier) + (self.__yesterday * (1-multiplier))
        
        return self.__yesterday