import numpy as np
import matplotlib.pyplot as plt
import csv
import argparse


START_ROW = 50 # サンプリングする開始位置
DT = 0.01 # サンプリング間隔 100Hz = 0.01s

TIME_COLUMN_NAME = "time[s]" #time列のヘッダー名
TIME_COLUMN_DEFAULTS = 0 #time列のヘッダー名が一致しないときの読み込む列番号
SEND_COLUMN_NAME = "send front" #send列のヘッダー名
SEND_COLUMN_DEFAULTS = 1 #send列のヘッダー名が一致しないときの読み込む列番号
RECI_COLUMN_NAME = "recieve front" #recieve列のヘッダー名
RECI_COLUMN_DEFAULTS = 4 #recieve列のヘッダー名が一致しないときの読み込む列番号

##コマンドライン引数
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start",type=int, help="data start point",default=0)

parser.add_argument('--xmin', type=float, help="graph limit x min")
parser.add_argument('--xmax', type=float, help="graph limit x max")
parser.add_argument('--yminA', type=float, help="amplitude graph limit y min")
parser.add_argument('--ymaxA', type=float, help="amplitude graph limit y max")
parser.add_argument('--yminP', type=float, help="phase graph limit y min")
parser.add_argument('--ymaxP', type=float, help="phase graph limit y max")
parser.add_argument('-l', '--logarithm', action='store_true', help="plot logarithm axis")

parser.add_argument('-fi', '--filename', type=str, nargs='+', help="open fileame")
parser.add_argument('-fr', '--frequent', type=float, nargs='+', help="input open file's frequent")
parser.add_argument("-p", "--points", type=int, nargs='+', help="fft point",default=[512])
args = parser.parse_args()

print(args.filename)

START_ROW = args.start
if len(args.filename) != len(args.frequent):
    print("not match number of file and frequent.")
    # exit()
for n in args.points:
    if n % 2 != 0:
        print("fft point is not match.")
        exit()

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
            time = r[timeColumn]
            send = float(r[sendColumn]) - 2000 ##中心を2000にする
            recieve = float(r[reciveColumn]) - 2000

            times.append(time)
            sends.append(send)
            recieves.append(recieve)
    return (times,sends,recieves)

'''
FFT後平均をとるメソッド
'''
def MeanFFT(send, recieve, N):
    roopnum = int((len(send)-START_ROW)/N)
    yfInArray = []
    yfOutArray = []
    if roopnum == 0:
        print("not enough data amount for "+str(N)+"point fft.")
        exit()
    for i in range(0, roopnum):
        sp = i*N + START_ROW
        ep = sp + N
        yfIn = np.fft.fft(send[sp:ep])
        yfOut = np.fft.fft(recieve[sp:ep])
        # yfIn = fftpack.fft(send[sp:ep]) / (N / 2)
        # yfOut = fftpack.fft(recieve[sp:ep]) / (N / 2)

        yfInArray.append(yfIn)
        yfOutArray.append(yfOut)
    return np.sum(yfInArray, axis=0),np.sum(yfOutArray, axis=0)

'''
軸の最大値・最小値をリミットする関数
'''
def limitAxisX():
    if args.xmin:
        plt.xlim(xmin=args.xmin)
    if args.xmax:
        plt.xlim(xmax=args.xmax)
def limitAxisYAmplitude():
    if args.yminA:
        plt.ylim(ymin=args.yminA)
    if args.ymaxA:
        plt.ylim(ymax=args.ymaxA)
def limitAxisYPhase():
    if args.yminP:
        plt.ylim(ymin=args.yminP)
    if args.ymaxP:
        plt.ylim(ymax=args.ymaxP)

'''
振幅をplot
'''
def plotAmplitude(freq, FRF):
    plt.figure()
    plt.subplot(2, 1, 1)  # 上から一行目にグラフを描画
    if args.logarithm:
        plt.loglog(freq, np.abs(FRF),"r--o")
    else:
        plt.semilogy(freq, np.abs(FRF),"r--o")
    plt.ylabel("Amplitude[dB]")
    plt.axis("tight")

    limitAxisX()
    limitAxisYAmplitude()

'''
位相をplot
'''
def plotPhase(freq, FRF):
    plt.subplot(2, 1, 2)  # 上から二行目にグラフを描画
    if args.logarithm:
        plt.semilogx(freq, np.degrees(np.angle(FRF)),"r--o")
    else:
        plt.plot(freq, np.degrees(np.angle(FRF)),"r--o")
    plt.xlabel("Frequency[Hz]")
    plt.ylabel("Phase[deg]")
    plt.axis("tight")
    plt.ylim(-180, 180)
    limitAxisX()
    limitAxisYPhase()

'''
片対数、両対数の書き方
plt.semilogy(x, y) # y軸が対数
plt.semilogx(x, y) # x軸が対数
plt.loglog(x, y) # 両対数
ax.plot(x, y)
ax.set_xscale("log") # あとからでも設定可能
ax.set_yscale("log", nonposy='clip') # 負になる場合の対処．'mask'もある
'''

'''
メイン
'''
def main():
    filenames = args.filename
    frequents = args.frequent
    fftpoints = args.points
    plotFreq = []
    plotFRF = []
    for (fn, fre, point) in zip(filenames, frequents, fftpoints):
        time, send, recieve = loadCSV(fn)

        yfIn, yfOut = MeanFFT(send, recieve, point)
        freq = np.fft.fftfreq(point, DT)

        # FRF = yfOut / yfIn #通常の方法
        FRF = (yfOut * np.conj(yfIn)) / (yfIn * np.conj(yfIn)) #クロススペクトル法

        plotNum = np.searchsorted(freq[1:int(point / 2)], fre)# プロットする周波数に近いインデックスを取得
        plotFreq.append(freq[plotNum])
        plotFRF.append(FRF[plotNum])

    plotAmplitude(plotFreq, plotFRF)
    plotPhase(plotFreq, plotFRF)
    plt.show()



if __name__ == '__main__':
    main()