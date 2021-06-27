import pandas as pd
import random

date_index=pd.date_range(start='2020-10-19-00',end='2020-12-19-00', freq='1s')
print(len(date_index))

#サーバーアドレス一覧（3つのサブネットに分ける。）
a1 = '10.20.30.1/16'
a2 = '10.20.30.2/16'
a3 = '192.168.1.1/24'
a4 = '192.168.1.2/24'
a5 = '10.77.1.1/24'
a6 = '10.77.1.2/24'
A = [a1,a2,a3,a4,a5,a6]


f = open('test.log','w')
j = 0

for _ in range(10**5):
    if random.uniform(1,10) <= 3:
        #毎回1秒間隔でないようにする。
        j += 1
    #ping応答時間は、平均1の対数正規分布に従う乱数+(1～10のどれか)を与えてみる。。。
    ping = int(abs(random.lognormvariate(1,15)+random.uniform(1,10)))
    if ping > 100000:
        ping = '-'
    else:
        ping = str(ping%100)

    da = str(date_index[j].year)+str(date_index[j].month).zfill(2)+str(date_index[j].day).zfill(2)+str(date_index[j].hour).zfill(2)+str(date_index[j].minute).zfill(2)+str(date_index[j].second).zfill(2)
    da2 = da+','+A[int(random.uniform(0,5.999))]+','+ping+'\n'

    f.write(da2)
    j += 1

f.close()
