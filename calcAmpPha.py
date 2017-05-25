import numpy as np
import csv
import argparse
import matplotlib.pyplot as plt

##コマンドライン引数
parser = argparse.ArgumentParser()
parser.add_argument("-f",'--filename', type=str, help="open fileame")
parser.add_argument("-s", "--start",type=int, help="data start point",default=100)
args = parser.parse_args()

TIME_COLUMN_NAME = "time[s]" #time列のヘッダー名
TIME_COLUMN_DEFAULTS = 0 #time列のヘッダー名が一致しないときの読み込む列番号
SEND_COLUMN_NAME = "send front" #send列のヘッダー名
SEND_COLUMN_DEFAULTS = 1 #send列のヘッダー名が一致しないときの読み込む列番号
RECI_COLUMN_NAME = "recieve front" #recieve列のヘッダー名
RECI_COLUMN_DEFAULTS = 4 #recieve列のヘッダー名が一致しないときの読み込む列番号

if not args.filename:
    print("Please select --filename")
    args.filename = "5Hz.csv" ##test用
    # exit()

'''
csvを読み込む関数
'''
def loadCSV(filename):
    times = []
    sends = []
    recieves = []
    timeColumn = TIME_COLUMN_DEFAULTS
    sendColumn = SEND_COLUMN_DEFAULTS
    reciveColumn = RECI_COLUMN_DEFAULTS
    with open(filename) as fp:
        reader = csv.reader(fp)  # Instantiate CSV reader with file pointer.

        ##headerの識別
        header = next(reader)
        for i, head in enumerate(header):
            if head == TIME_COLUMN_NAME:
                timeColumn = i
            elif head == SEND_COLUMN_NAME:
                sendColumn = i
            elif head == RECI_COLUMN_NAME:
                reciveColumn = i

        ##振り分け
        for r in reader:
            # Assign each field on individual variables.
            time = float(r[timeColumn])
            send = float(r[sendColumn]) - 2000 ##中心を2000にする
            recieve = float(r[reciveColumn]) - 2000

            times.append(time)
            sends.append(send)
            recieves.append(recieve)
    return (times,sends,recieves)


def get1Cycle(data):
    startAmp = data[0]
    if startAmp > data[1]:
        for i in range(len(data)):
            if startAmp < data[i]:
                for j, d in enumerate(data[i:]):
                    if startAmp > d:
                        return data[:j+i]

    elif startAmp < data[1]:
        for i in range(len(data)):
            if startAmp > data[i]:
                for j, d in enumerate(data[i:]):
                    if startAmp < d:
                        return data[:j+i]
    else:
        print("不明なデータ")
        exit()

'''
メイン
'''
def main():
    filename = args.filename
    startPoint = args.start
    time, send, recieve = loadCSV(filename)

    startPoint = int(len(send)*(3/5))

    validTime = time[startPoint:]
    sendCycle = get1Cycle(send[startPoint:])
    recieveCycle = get1Cycle(recieve[startPoint:])

    sendAmp = np.max(sendCycle) - np.min(sendCycle)
    recieveAmp = np.max(recieveCycle) - np.min(recieveCycle)

    sendMaxTime = validTime[np.argmax(sendCycle)] ##1周期での最大値の点の時間
    recieveMaxTime = validTime[np.argmax(recieveCycle)]
    cycle = validTime[len(sendCycle)] - validTime[0]

    print("sendAmp:"+str(sendAmp)+" receiveAmp:"+str(recieveAmp))
    print("振幅比:"+str(recieveAmp/sendAmp))
    print("周期:"+str(cycle))
    print("位相差:" + str(recieveMaxTime - sendMaxTime)+ "[ms]")
    print("位相差:" + str(360*(((recieveMaxTime-sendMaxTime)/cycle))) + "degree")


    plt.plot(validTime[:len(recieveCycle)], recieveCycle)
    plt.plot(validTime[:len(sendCycle)], sendCycle)

    plt.axvline(x=sendMaxTime)
    plt.axvline(x=recieveMaxTime)

    plt.show()

if __name__ == '__main__':
    main()