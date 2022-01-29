import os, sys
#seconds to datetime lib
from datetime import datetime
import matplotlib.pyplot as plt
#matplotlib custom patches for legend
import matplotlib.patches as mpatches

from arquive import Arquive

def showResults():
    models = ["SMA", "WMA", "EMA", "PMA"]
    predictions = [[],[],[],[]]
    frames = []
    totalPackets = 0
    for i in range(len(models)):
        arq = Arquive("Log/{}.csv".format(models[i]))
        #read file lines
        lines = arq.readAllLines()
        lines.pop(0)
        lines.pop()
        for line in lines:
            [timestamp, window, frame, predict] = line.split(",")
            if(totalPackets == 0):
                frames.append(int(frame))

            predictions[i].append(float(predict))
        totalPackets = len(lines)

    xAxis = range(1,totalPackets+1)
    colors = ["blue","lightgreen","orange","red"]

    plotOneByOne(models, xAxis,predictions,frames, colors)
    plotAllInOne(models, xAxis,predictions,frames, colors)

def plotOneByOne(models, xAxis, predictions,frames, colors):
    fig, (ax0, ax1, ax2, ax3) = plt.subplots(4,1)
    axis = [ax0, ax1, ax2, ax3]
    for i in range(len(axis)):
        axis[i].set_title("Model {}: Real vs Prediction".format(models[i]))
        #plot frame data
        axis[i].plot(xAxis, frames, label='Real', color="black")
        #plot predictions
        axis[i].plot(xAxis, predictions[i], label='Predicted', color = colors[i])
        #create legend at lower right
        axis[i].legend(loc="upper right")
    fig.tight_layout()
    plt.show()

def plotAllInOne(models, xAxis, predictions, frames, colors):
    fig, (ax0) = plt.subplots(1,1)
    ax0.plot(xAxis, frames, label='Real', color="black")
    for i in range(len(models)):
        ax0.plot(xAxis, predictions[i], label=models[i], color = colors[i])
        ax0.legend(loc="upper right")
    #fig.tight_layout()
    fig.suptitle("Models vs Real")
    plt.show()

if(__name__ == "__main__"):
    showResults()