from random import seed, randint, sample
from arquive import Arquive

def low():
    return randint(0,10)

def medium():
    return randint(11,30)

def high():
    return randint(31,100)

def genFlow(ipList, entries_num = 30):
    files = {}
    size = len(ipList)
    counters = [0]*size
    for ip in ipList:
        files[ip] = Arquive("Flows/{}.csv".format(ip))
    originList = ipList.copy()
    destinationList = ipList.copy()
    index = size - 1
    quantity = [low, medium]
    while(len(originList) != 0):
        origin = originList[index]
        destinationList = ipList.copy()
        destinationList.remove(origin)
        destination = sample(destinationList,1)[0]
        flow = sample(quantity,1)[0]()
        files[origin].append("{},{},{}\n".format(origin,destination,flow))
        counters[index] += 1
        if(counters[index] == entries_num):
            index -= 1
            originList.pop()
