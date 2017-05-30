import numpy as np
import matplotlib.pyplot as plt
import csv
import argparse

'''
実行例 $python3 bodePlot -f noisze.csv
      $python3 bodePlot --filename noisze.csv

      1024点でFFTする場合(指定なしだと4096点)
      $python3 bodePlot -f noisze.csv -p 1024
      $python3 bodePlot -f noisze.csv --point 1024

      サンプリングを開始する位置を指定する場合(指定なしだと500点)
      $python3 bodePlot -f noisze.csv -s 300
      $python3 bodePlot -f noisze.csv -start 300

      x軸、y軸それぞれの最大値・最小値を指定することができる。
      $python3 bodePlot -f noisze.csv --xmax 10 --xmin 0
      $python3 bodePlot -f noisze.csv --ymax 10 --ymin -10

      線形グラフで表示する
      $python3 bodePlot -f noisze.csv -li
      $python3 bodePlot -f noisze.csv --linear

      シフトする数を指定する
      $python3 bodePlot -f noisze.csv --shift 5

      ブラックマンの窓関数をかける
      $python3 bodePlot -f noisze.csv --blackman
'''

N = 4096  # FFTのサンプル数
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
parser.add_argument("-f",'--filename', type=str, help="open fileame")
parser.add_argument("-p", "--point",type=int, help="fft point",default=4096)
parser.add_argument("-s", "--start",type=int, help="data start point",default=20)
parser.add_argument("--shift", type=int, help="data shift num", default=4)
parser.add_argument("--blackman", action='store_true', help="use brackman window")

parser.add_argument('--xmin', type=float, help="graph limit x min")
parser.add_argument('--xmax', type=float, help="graph limit x max")
parser.add_argument('--yminA', type=float, help="amplitude graph limit y min")
parser.add_argument('--ymaxA', type=float, help="amplitude graph limit y max")
parser.add_argument('--yminP', type=float, help="phase graph limit y min")
parser.add_argument('--ymaxP', type=float, help="phase graph limit y max")
parser.add_argument('-li', '--linear', action='store_true', help="plot linear axis")
args = parser.parse_args()

N = args.point
START_ROW = args.start
if not args.filename:
    print("Please select --filename")
    args.filename = "randomNoise8min.csv" ##test用
    # exit()
if N % 2 != 0:
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
            send = float(r[sendColumn])# - 2000 ##中心を2000にする
            recieve = float(r[reciveColumn])# - 2000

            times.append(time)
            sends.append(send)
            recieves.append(recieve)
    return (times,sends,recieves)

'''
窓関数をかけて、FFT後平均をとるメソッド
'''
def MeanFFT(send, recieve, N):
    splitNum = args.shift ## N/splitNumずつシフトしていく
    shiftCount = int(N/splitNum)
    roopnum = int((len(send)-START_ROW)/shiftCount) - (splitNum-1)
    yfInArray = []
    yfOutArray = []
    if roopnum == 0:
        print("not enough data amount for "+str(N)+"point fft.")
        exit()
    for i in range(0, roopnum):
        sp = i*shiftCount + START_ROW
        ep = sp + N

        window = np.hamming(N) ##ハミング窓をかける
        if args.blackman:
            window = np.blackman(N)

        windSend = window * send[sp:ep]
        windRecieve = window * recieve[sp:ep]

        yfIn = np.fft.fft(windSend)
        yfOut = np.fft.fft(windRecieve)
        # yfIn = fftpack.fft(send[sp:ep]) / (N / 2)
        # yfOut = fftpack.fft(recieve[sp:ep]) / (N / 2)

        yfInArray.append(yfIn)
        yfOutArray.append(yfOut)
    print(str(roopnum)+"回平均")
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
    if args.linear:
        plt.plot(freq, 10*np.log10(np.abs(FRF)))
    else:
        plt.semilogx(freq, 10*np.log10(np.abs(FRF)))
    plt.ylabel("Amplitude[dB]")
    plt.axis("tight")

    limitAxisX()
    limitAxisYAmplitude()

def plotAmplitude2(freq, FRF):
    # plt.figure()
    # plt.subplot(2, 1, 1)  # 上から一行目にグラフを描画
    if args.linear:
        plt.plot(freq, 10*np.log10(np.abs(FRF)),"r--o")
    else:
        plt.semilogx(freq, 10*np.log10(np.abs(FRF)),"r--o")
    plt.ylabel("Amplitude[dB]")
    plt.axis("tight")

    limitAxisX()
    limitAxisYAmplitude()

'''
位相をplot
'''
def plotPhase(freq, FRF):
    plt.subplot(2, 1, 2)  # 上から二行目にグラフを描画
    if args.linear:
        plt.plot(freq, np.degrees(np.angle(FRF)))
    else:
        plt.semilogx(freq, np.degrees(np.angle(FRF)))
    plt.xlabel("Frequency[Hz]")
    plt.ylabel("Phase[deg]")
    plt.axis("tight")
    plt.ylim(-180, 180)
    limitAxisX()
    limitAxisYPhase()

def plotPhase2(freq, FRF):
    # plt.subplot(2, 1, 2)  # 上から二行目にグラフを描画
    if args.linear:
        plt.plot(freq, np.degrees(np.angle(FRF)),"r--o")
    else:
        plt.semilogx(freq, np.degrees(np.angle(FRF)),"r--o")
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

def sinbode():
    filenames = ["0_1Hz.csv", "0_2Hz.csv", "0_5Hz.csv", "1Hz.csv", "2Hz.csv", "5Hz.csv"]
    frequents = [0.1, 0.2, 0.5, 1, 2, 5]
    fftpoints = [4096, 4096, 4096, 4096, 4096, 4096]
    plotFreq = []
    plotFRF = []
    for (fn, fre, point) in zip(filenames, frequents, fftpoints):
        time, send, recieve = loadCSV(fn)

        yfIn, yfOut = MeanFFT(send, recieve, point)
        freq = np.fft.fftfreq(point, DT)

        # FRF = yfOut / yfIn #通常の方法
        FRF = (yfOut * np.conj(yfIn)) / (yfIn * np.conj(yfIn))  # クロススペクトル法

        plotNum = np.searchsorted(freq[0:int(point / 2)], fre)  # プロットする周波数に近いインデックスを取得
        plotFreq.append(freq[plotNum])
        plotFRF.append(FRF[plotNum])

    return plotFreq, plotFRF

def bode():
    filename = args.filename
    time, send, recieve = loadCSV(filename)

    yfIn, yfOut = MeanFFT(send, recieve, N)
    freq = np.fft.fftfreq(N, DT)

    # FRF = yfOut / yfIn #通常の方法
    FRF = (yfOut * np.conj(yfIn)) / (yfIn * np.conj(yfIn))  # クロススペクトル法

    return freq,FRF

def main():
    plotFreq, plotFRF = sinbode()
    freq, FRF = bode()

    plotAmplitude(freq[0:int(N / 2)], FRF[0:int(N / 2)])
    plotAmplitude2(plotFreq, plotFRF)


    plotPhase(freq[0:int(N / 2)], FRF[0:int(N / 2)])
    plotPhase2(plotFreq, plotFRF)

    plt.show()

if __name__ == '__main__':
    main()
