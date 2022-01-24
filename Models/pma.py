import math
from Models.Base import Base

class PMA(Base):
    def __init__(self):
        self.__factorial = [1]
        self.__factorial_size = 1
        self.__poisson = []

    def getName(self):
        return "PMA"
        
    # function to set factorial vector values
    def __adjustFactorial(self, size):
        # block to decrease factorial vector
        if(self.__factorial_size > size):
            # decrese factorial size
            while (self.__factorial_size > size):
                # remove last item from factorial vector
                self.__factorial.pop()
                # decrement variable that contains factorial size
                self.__factorial_size -= 1
        # block to increase factorial vector
        if(self.__factorial_size < size):
            # increse factorial size
            while (self.__factorial_size < size):
                # increment factorial vector with size * last item
                self.__factorial.append(
                    self.__factorial[-1] * (self.__factorial_size))
                # increment variable that contains factorial size
                self.__factorial_size += 1
        # print("factorial", self.__factorial)

    def __adjustPoisson(self, size):
        # reset poissson vector
        self.__poisson = []
        # pre-calculate e^-lambda
        e_m_lambda = math.exp(-size)
        total = 0
        # iterate from 0 to window_size -1, ex: 0,2,3,4,5
        for k in range(size):
            # append the result of iteration k to vector
            self.__poisson.append(math.pow(size, k) * e_m_lambda / self.__factorial[k])
            total+= self.__poisson[k]
        
        #multiplier to normalize vector sum to 1
        normalize = 1 / total
        self.__poisson = [self.__poisson[i] * normalize for i in range(size)]

    def predict(self, vector, size):
        if(self.__factorial_size != size):
            self.__adjustFactorial(size)
            self.__adjustPoisson(size)
        print("Factorial:",self.__factorial)
        print("Poisson:",self.__poisson)
        return sum([vector[i] * self.__poisson[i] for i in range(size)])