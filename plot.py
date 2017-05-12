import numpy as np
import matplotlib.pyplot as plt
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-f",'--filename', type=str, action='append', help="open fileame")
parser.add_argument('--xmin', type=float, help="graph limit x min")
parser.add_argument('--xmax', type=float, help="graph limit x max")
parser.add_argument('--ymin', type=float, help="graph limit y min")
parser.add_argument('--ymax', type=float, help="graph limit y max")
parser.add_argument('--xlabel', type=str, help="graph x label", default="t[s](×1/11025)")
parser.add_argument('--ylabel', type=str, help="graph y label", default="Output error[dB]")
args = parser.parse_args()
if not args.filename:
    print("Please select --filename")
    ##args.filename = ["5Hz.csv"] ##test用
    exit()

def loadText(filename,columnName,columnDefaluts):
    f = open(filename,"r")
    readColumn = columnDefaluts
    result = []

    header = f.readline()
    for i,head in enumerate(header.split(',')):
        if head == columnName:
            readColumn = i

    lines = f.readlines()
    for line in lines:
        data = float(line.split(',')[readColumn])
        result.append(data)

    f.close()
    return result

def draw(filename):
    x = loadText(filename, columnName="time[s]", columnDefaluts=0)
    y1 = loadText(filename, "send1", 1)
    plt.plot(x,y1)
    y2 = loadText(filename, "send2", 2)
    plt.plot(x,y2)
    y3 = loadText(filename, "send3", 3)
    plt.plot(x,y3)
    y4 = loadText(filename, "recieve1", 4)
    plt.plot(x,y4)
    y5 = loadText(filename, "recieve2", 5)
    plt.plot(x,y5)
    y6 = loadText(filename, "recieve3", 6)
    plt.plot(x,y6)

def main():
    for file in args.filename:
        draw(file)
    if args.xlabel:
        plt.xlabel(args.xlabel)
    if args.ylabel:
        plt.ylabel(args.ylabel)
    if args.xmin:
        plt.xlim(xmin=args.xmin)
    if args.xmax:
        plt.xlim(xmax=args.xmax)
    if args.ymin:
        plt.ylim(ymin=args.ymin)
    if args.ymax:
        plt.ylim(ymax=args.ymax)
    plt.show()

if __name__ == '__main__':
    main();
