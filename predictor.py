import math
import time
from threading import Thread
from Models.Base import Base

class Predictor(Thread):
    def __init__(self, alertCallback, model, size=10, interval = 10):
        self.super = Thread.__init__(self)
        # alert callback function
        self.__alertCallback = alertCallback
        self.setModel(model)
        # window vector size
        self.__window_size = size
        # package counter in interval
        self.__frame = 0
        # time of last interval end
        self.__time = None
        # interval of frame
        self.__interval = None
        # frames counter
        self.__frames_count = 0
        # vector to save history of last frames
        self.__history_size = 100
        self.__history = [0]*self.__history_size

        # ------window resize variables
        #confidence 95%
        self.__resize_alpha = 0.05
        #last window mean
        self.__avg_old = 0
        #last window variance
        self.__variance_old = 0
        #current window mean
        self.__avg = 0
        #current window variance
        self.__variance = 0
        # ------
        self.__running = True
        self.__online = True
        self.__offline_fifo = []


    def setModel(self, model):
        if(not issubclass(model, Base)):
            raise Exception("model is not a subclass of Base abstract class")
        self.__model = model()

    # generate prediction
    def __predict(self):
        return self.__model.predict(self.__history[self.__history_size-self.__window_size:], self.__window_size)

    # function to calculate variance
    def __calcVariance(self):
        #print("__________calcVariance___________")
        # reset current variance
        self.__variance = 0
        # iterate window frames
        for frame in self.__history[self.__history_size - self.__window_size:]:
            # sommation
            self.__variance += math.pow(frame - self.__avg, 2)
            #print(self.__variance)
        # divide summation by vector size
        self.__variance = self.__variance / self.__window_size
        
        #print("__________end calcVariance___________")

    # function to get min and max frame from window
    def __calcMinMax(self):
        # set min_frame as infinite
        min_frame = float("inf")
        # set max_frame as zero
        max_frame = 0
        # iterate all frames from window
        for frame in self.__history[self.__history_size - self.__window_size:]:
            # save frame if it's lower than min_frame
            min_frame = (frame < min_frame) * frame or min_frame
            # save frame if it's higher than max_frame
            max_frame = (frame > max_frame) * frame or max_frame
        # return min and max frames
        return min_frame, max_frame

    # function to slide window and calculate statistics
    def __slideWindow(self):
        # save current variance as old
        self.__variance_old = self.__variance
        # save current avg as old
        self.__avg_old = self.__avg
        # append frame to history
        self.__history.append(self.__frame)
        # remove oldest frame from history
        self.__history.pop(0)
        # calculate new avg
        self.__avg = sum(
            self.__history[self.__history_size - self.__window_size:])/self.__window_size
        # calculate new variance
        self.__calcVariance()
        #check if window is not empty
        if(self.__avg != 0 and self.__avg_old != 0 and self.__variance != 0):
            direct = self.__avg / self.__avg_old
            inverse = self.__avg_old / self.__avg
            ratio = abs(direct - inverse)
            #print("Resize" * (ratio >= 1 + self.__resize_alpha) or "Don't Resize")
            # verify whether ration above threshold
            if(ratio >= 1 + self.__resize_alpha):
                # get min and max frame from window
                min_frame, max_frame = self.__calcMinMax()
                # calculate max variance
                variance_max = (self.__avg - min_frame) * \
                    (max_frame - self.__avg)

                #print("________________________________________")
                #print(self.__history)
                # calculate volume to resize window
                volume = variance_max / self.__variance
                # calculate new window size
                new_size = self.__window_size + \
                    ((self.__avg > self.__avg_old) * volume or -volume)

                # call adjust window function passing ceil of new size
                self.__window_size = math.ceil(new_size)
        

    # function to return prediction
    def __callback(self):
        #self.__alertCallback("[{}]".format(";".join(map(str, self.__history[self.__history_size - self.__window_size:]))),self.__frame, self.__predict())
        self.__alertCallback("None",self.__frame, self.__predict())


    #__________public functions_____________

    # function to end model analysis
    def stop(self):
        self.__running = False
        # sum 1 to frames count
        self.__frames_count += 1
        # call anomaly test
        
        if(not self.__online):
            while(len(self.__offline_fifo) > 0):
                [time, packets] = self.__offline_fifo.pop(0)
                if(self.__time + self.__interval < time):
                    self.__callback()
                    # recalculate window and slide window
                    self.__slideWindow()
                    # frames count increment
                    self.__frames_count += 1
                    self.__time += self.__interval
                    self.__frame = 0
                # start new frame count
                self.__frame += packets
        if(self.__frame != 0):
            self.__callback()
            # recalculate window and slide window
            self.__slideWindow()
            self.__frame = 0
        


    # set initial value for time and interval
    def setStart(self, start_time = time.time()):
        # set variable time
        self.__time = start_time
        # set time interval
        self.start()

    #change package interval on run
    def setInterval(self, interval):
        # set new time interval
        self.__interval = interval

    # function to process package in
    def packetIn(self, packets = 1):
        self.__frame += packets

    def packetInOffline(self, time, packets = 1):
        self.__offline_fifo.append([time,packets])

    def setOnline(self):
        self.__online = True

    def setOffline(self):
        self.__online = False

    def __runOnline(self):
        while(self.__running):
            time.sleep(self.__interval)
            self.__callback()
            # recalculate window and slide window
            self.__slideWindow()
            # set next frame base time
            self.__time += self.__interval
            # frames count increment
            self.__frames_count += 1
            # start new frame count
            self.__frame = 0

    def __runOffline(self):
        while(self.__running):
            if(len(self.__offline_fifo) > 0):
                [time, packets] = self.__offline_fifo.pop(0)
                if(self.__time + self.__interval < time):
                    self.__callback()
                    # recalculate window and slide window
                    self.__slideWindow()
                    # frames count increment
                    self.__frames_count += 1
                    self.__time += self.__interval
                    self.__frame = 0
                # start new frame count
                self.__frame += packets


    def run(self):
        if(self.__online):
            self.__runOnline()
        else:
            self.__runOffline()
