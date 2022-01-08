from abc import ABC, abstractmethod
 
class Base(ABC):
 
    @abstractmethod
    def predict(self, vector, size):
        pass