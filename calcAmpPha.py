import numpy as np
import csv
import argparse
import matplotlib.pyplot as plt
from scipy import stats

##コマンドライン引数
parser = argparse.ArgumentParser()
parser.add_argument("-f",'--filename', type=str, help="open fileame")
parser.add_argument("-s", "--start",type=int, help="data start point",default=5)
args = parser.parse_args()

TIME_COLUMN_NAME = "time[s]" #time列のヘッダー名
TIME_COLUMN_DEFAULTS = 0 #time列のヘッダー名が一致しないときの読み込む列番号
SEND_COLUMN_NAME = "send front" #send列のヘッダー名
SEND_COLUMN_DEFAULTS = 1 #send列のヘッダー名が一致しないときの読み込む列番号
RECI_COLUMN_NAME = "recieve front" #recieve列のヘッダー名
RECI_COLUMN_DEFAULTS = 4 #recieve列のヘッダー名が一致しないときの読み込む列番号

if not args.filename:
    print("Please select --filename")
    args.filename = "1Hz.csv" ##test用
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
            send = float(r[sendColumn])# - 2000 ##中心を2000にする
            recieve = float(r[reciveColumn])# - 2000

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
        print("unknown start point")
        return get1Cycle(data[7:])

def iqr(data):
    # 四分位範囲を計算
    data_q1 = stats.scoreatpercentile(data, 25)  # 第一四分位数（=25パーセンタイル）
    data_q3 = stats.scoreatpercentile(data, 75)  # 第三四分位数（=75パーセンタイル）
    data_iqr = data_q3 - data_q1  # 四分位範囲

    # 外れ値の範囲を計算する
    data_iqr_min = data_q1 - (data_iqr) * 1.5  # 第一四分位数 から四分位範囲（iqr*1.5）を引き算。
    data_iqr_max = data_q3 + (data_iqr) * 1.5  # 第一四分位数 から四分位範囲（iqr*1.5）を。

    # 範囲から外れている値を除く
    returndata = []
    for d in data:
        if(d>data_iqr_min and d<data_iqr_max):
            returndata.append(d)
    return returndata
'''
メイン
'''
def main():
    filename = args.filename
    loadTime, loadSend, loadtRecieve = loadCSV(filename)

    startPoint = int(len(loadSend)*(3/5)) + args.start

    validTime = loadTime[startPoint:] #有効な部分
    validSend = loadSend[startPoint:]
    validRecieve = loadtRecieve[startPoint:]

    sendCycle = get1Cycle(loadSend[startPoint:])
    recieveCycle = get1Cycle(loadtRecieve[startPoint:])

    cycleLength = int((len(sendCycle)+len(sendCycle))/2 + 5) #一周期の長さ、余分に持つ
    timeCycle = loadTime[startPoint:startPoint+cycleLength]

    zipValidTime = zip(*[iter(validTime)] * cycleLength) #サイクル毎に分割する
    zipSendCycle = zip(*[iter(validSend)] * cycleLength)
    zipRecieveCycle = zip(*[iter(validRecieve)] * cycleLength)

    totalSendAmp, totalRecieveAmp = [], []
    totalPhase,totalCycle = [], []

    for time,send,recieve in zip(zipValidTime, zipSendCycle, zipRecieveCycle):

        sendAmp = np.max(send) - np.min(send)
        recieveAmp = np.max(recieve) - np.min(recieve)
        totalSendAmp.append(sendAmp),totalRecieveAmp.append(recieveAmp)

        sendMaxTime = time[np.argmax(send)] ##1周期での最大値の点の時間
        recieveMaxTime = time[np.argmax(recieve)]
        cycle = time[-1] - time[0]
        phase = recieveMaxTime-sendMaxTime
        totalPhase.append(phase),totalCycle.append(cycle)

    aveSendAmp, aveRecieveAmp = np.average(totalSendAmp), np.average(totalRecieveAmp)
    avePhase, aveCycle = np.average(totalPhase), np.average(totalCycle)

    print("第一周期目")
    print("sendAmp:"+str(totalSendAmp[0])+" receiveAmp:"+str(totalRecieveAmp[0]))
    print("振幅比:"+str(totalRecieveAmp[0]/totalSendAmp[0]))
    print("周期:"+str(totalCycle[0]))
    print("位相差:" + str(totalPhase[0])+ "[ms]")
    print("位相差:" + str(360*((totalPhase[0]/totalCycle[0]))) + "degree")

    print("平均")
    print("sendAmp:" + str(aveSendAmp) + " 平均receiveAmp:" + str(aveRecieveAmp))
    print("平均振幅比:" + str(aveRecieveAmp / aveSendAmp))
    print("平均周期:" + str(aveCycle))
    print("平均位相差:" + str(avePhase) + "[ms]")
    print("平均位相差:" + str(360 * ((avePhase / aveCycle))) + "degree")


    plt.plot(validTime[:len(recieveCycle)], recieveCycle)
    plt.plot(validTime[:len(sendCycle)], sendCycle)

    plt.axvline(x=timeCycle[np.argmax(sendCycle)])
    plt.axvline(x=timeCycle[np.argmax(recieveCycle)])

    plt.show()

if __name__ == '__main__':
    main()