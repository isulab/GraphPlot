# GraphPlot
ボード線図や時間-振幅グラフを作成するもの

## 時間-振幅グラフの作成

### 実行方法
実行ファイル名 plot.py

以下のようにファイル名を指定し、ファイルを実行する。

```
$python3 plot.py -f 0_1Hz.csv
```

読み込むファイル名は追加で指定することができ、それぞれの波形を比較できる。

```
$python3 plot.py -f 0_1Hz.csv -f 0_2Hz.csv -f 0_5Hz.csv
```

x軸ラベル・y軸ラベルを指定できる。

```
$python3 plot.py -f 0_1Hz.csv --xlabel 時間 --ylabel 振幅 
```

x軸、y軸それぞれの最大値・最小値を指定することができる。

```
$python3 plot.py -f 0_1Hz.csv --xmin x軸の最小値 --xmax y軸の最大値 
$python3 plot.py -f 0_1Hz.csv --ymin x軸の最小値 --ymax y軸の最大値
```

### グラフの例
![0.1Hz](https://github.com/isulab/GraphPlot/blob/master/sample/graph0_1Hz.png)


## ボード線図の作成
以下の読み込みファイル形式のcsvを読み込み、ボード線図を描く。クロススペクトル法を用いて、ゲイン線図と位相線図の両方を出力する。

### 実行方法
実行ファイル名 bodePlot.py

以下のようにファイル名を指定し、ファイルを実行する。

```
$python3 bodePlot.py -f noisze.csv
$python3 bodePlot.py --filename noisze.csv
```

サンプリングを開始する位置を指定する場合(指定なしだと500点)

```
$python3 bodePlot.py -f noisze.csv -s 300
$python3 bodePlot.py -f noisze.csv -start 300

```

1024点でFFTする場合(指定なしだと4096点)

```
$python3 bodePlot.py -f noisze.csv -p 1024
$python3 bodePlot.py -f noisze.csv --point 1024

```

x軸、y軸それぞれの最大値・最小値を指定することができる。

```
$python3 bodePlot -f noisze.csv --xmax 10 --xmin 0
$python3 bodePlot -f noisze.csv --ymax 10 --ymin -10
```

x軸を対数表示にする

```
$python3 bodePlot -f noisze.csv -l
$python3 bodePlot -f noisze.csv --logarithm

```


### ボード線図の例
![noize](https://github.com/isulab/GraphPlot/blob/master/sample/Bode_plot.png)

## 読み込みファイル形式

| time[s] | send front | send right | send left | recieve front | recieve right  | recieve left |
|:-----------|------------:|:------------:|:------------:|:------------:|:------------:|:------------:|
| 0.01 | 3049 | 5358 | 4370 | 0 | 0 | 0 |
| 0.02 | 4566 | 1036 | 6492 | 0 | 0 | 0 |
| ... | ... | ... | ... | ... | ... | ... |