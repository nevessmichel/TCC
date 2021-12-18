import math
import time

class PMA:
    def __init__(self, alertCallback, size=0):
        
        # alert callback function
        self.__alertCallback = alertCallback
        # factorial vector
        self.__factorial = [1]
        # factorial vector size
        self.__factorial_size = 1
        # window vector size
        self.__window_size = size
        # package counter in interval
        self.__frame = 0
        # frame prediction
        self.__predicted = 0
        # poisson vector
        self.__poisson = []
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

        # set factorial vector
        self.__adjustFactorial()
        # set poisson vector
        self.__adjustPoisson()

    # function to set factorial vector values
    def __adjustFactorial(self):
        #print("window_size", self.__window_size)
        # block to decrease factorial vector
        if(self.__factorial_size > self.__window_size):
            # decrese factorial size
            while (self.__factorial_size > self.__window_size):
                # remove last item from factorial vector
                self.__factorial.pop()
                # decrement variable that contains factorial size
                self.__factorial_size -= 1
        # block to increase factorial vector
        if(self.__factorial_size < self.__window_size):
            # increse factorial size
            while (self.__factorial_size < self.__window_size):
                # increment factorial vector with size * last item
                self.__factorial.append(
                    self.__factorial[-1] * (self.__factorial_size))
                # increment variable that contains factorial size
                self.__factorial_size += 1
        # print("factorial", self.__factorial)

    # function to calculate poisson truncate distribution
    def __adjustPoisson(self):
        # reset poissson vector
        self.__poisson = []
        # pre-calculate e^-lambda
        e_m_lambda = math.exp(-self.__window_size)
        # iterate from 0 to window_size -1, ex: 0,2,3,4,5
        for k in range(self.__window_size):
            # append the result of iteration k to vector
            self.__poisson.append(math.pow(self.__window_size, k) * e_m_lambda / self.__factorial[k])
        
        #multiplier to normalize vector sum to 1
        normalize = 1 / sum(self.__poisson)
        #iterate poisson vector
        for i in range(self.__window_size):
            #nomalize values
            self.__poisson[i] = self.__poisson[i] * normalize
        
    #function to resize window
    def __adjustWindow(self, size):
        #set new window size
        self.__window_size = size
        #recalculate factorial
        self.__adjustFactorial()
        #recalculate poisson truncate distribution
        self.__adjustPoisson()

    # generate prediction
    def __predict(self):
        # reset predicted
        self.__predicted = 0
        # iterate from 0 to window_size - 1
        for i in range(self.__window_size):
            # accumulate frame relevance * frame
            self.__predicted += (
                self.__poisson[i] * self.__history[self.__history_size - self.__window_size + i])

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
                self.__adjustWindow(math.ceil(new_size))

        # generate prediction
        self.__predict()
        

    # function to return prediction
    def __callback(self):
        self.__alertCallback(self.__frame, self.__predicted)


    #__________public functions_____________

    # function to end model analysis
    def stop(self):
        # sum 1 to frames count
        self.__frames_count += 1
        # call anomaly test
        self.__callback()
        # recalculate window and slide window
        self.__slideWindow()
        # start new frame count
        self.__frame = 1

    # set initial value for time and interval
    def setStart(self, interval, start_time = time.time()):
        # set variable time
        self.__time = start_time
        # set time interval
        self.__interval = interval

    #change package interval on run
    def setInterval(self, interval):
        # set new time interval
        self.__interval = interval

    # function to processo package in
    def packageIn(self, packages, time_sec = time.time()):
        print(packages, time_sec)
        # verify if package time is out of frame time
        if(time_sec > self.__time + self.__interval):
            # check frame anomaly
            self.__callback()
            # recalculate window and slide window
            self.__slideWindow()
            # set next frame base time
            self.__time += self.__interval
            # frames count increment
            self.__frames_count += 1
            # start new frame count
            self.__frame = packages
        # increment package in frame
        self.__frame += packages

        