class Arquive:
    #class constructor
    def __init__(self, filePath, encoding = "utf-8"):
        #save file path
        self.__filePath = filePath
        #save encoding
        self.__encoding = encoding
        self.__file = None

    #function to load all file as string
    def load(self):
        #open file in read mode
        arq = open(self.__filePath, mode="r", encoding=self.__encoding)
        #load all content as string
        string = arq.read()
        #close file
        arq.close()
        # return string
        return string

    #function to overwrite file
    def save(self, string):
        #open/create file in write mode
        arq = open(self.__filePath, mode="w+", encoding=self.__encoding)
        #overwrite content
        arq.write(string)
        #close file
        arq.close()
        
    #function to append content
    def append(self, string):
        #open/create file in append mode
        arq = open(self.__filePath, mode="a+", encoding=self.__encoding)
        #write content
        arq.write(string)
        #close file
        arq.close()

    #function to read content split in lines
    def readAllLines(self):
        #load content as string
        data = self.load()
        #return splited data
        return data.split("\n")

    def keepOpen(self):
        self.__file = open(self.__filePath, mode="a+", encoding=self.__encoding)

    def writeOpen(self, data):
        self.__file.write(data)
