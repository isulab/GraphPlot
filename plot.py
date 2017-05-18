import matplotlib.pyplot as plt
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-f",'--filename', type=str, action='append', help="open fileame")
parser.add_argument('--xmin', type=float, help="graph limit x min")
parser.add_argument('--xmax', type=float, help="graph limit x max")
parser.add_argument('--ymin', type=float, help="graph limit y min")
parser.add_argument('--ymax', type=float, help="graph limit y max")
parser.add_argument('--xlabel', type=str, help="graph x label", default="t[s]")
parser.add_argument('--ylabel', type=str, help="graph y label", default="Position")
parser.add_argument('--all', action='store_true', help="use all column")
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
    if args.all:
        y1 = loadText(filename, "send front", 1)
        plt.plot(x,y1)
        y2 = loadText(filename, "send right", 2)
        plt.plot(x,y2)
        y3 = loadText(filename, "send left", 3)
        plt.plot(x,y3)
        y4 = loadText(filename, "recieve front", 4)
        plt.plot(x,y4)
        y5 = loadText(filename, "recieve right", 5)
        plt.plot(x,y5)
        y6 = loadText(filename, "recieve left", 6)
        plt.plot(x,y6)
    else:
        y1 = loadText(filename, "send front", 1)
        plt.plot(x, y1)
        y4 = loadText(filename, "recieve front", 4)
        plt.plot(x, y4)
    return x[-1] ##時間の最大値を返す

def main():
    timelength = []
    for file in args.filename:
        timemax = draw(file)
        timelength.append(timemax)

    if args.xlabel:
        plt.xlabel(args.xlabel)
    if args.ylabel:
        plt.ylabel(args.ylabel)
    if args.xmin:
        plt.xlim(xmin=args.xmin)
    if args.xmax:
        plt.xlim(xmax=args.xmax)
    else:
        plt.xlim(xmax=max(timelength))
    if args.ymin:
        plt.ylim(ymin=args.ymin)
    if args.ymax:
        plt.ylim(ymax=args.ymax)
    plt.show()

if __name__ == '__main__':
    main()
