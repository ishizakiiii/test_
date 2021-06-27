import collections
import datetime
#######管理データ＆パラメータ###############

#temp_dict = {サーバーアドレス:タイムアウト発生開始時間}
#サーバーアドレス毎にタイムアウト開始時間を保持しておく。
temp_dict = {}

#SeriesTimeoutConter = {サーバーアドレス:連続タイムアウト回数}
#サーバーアドレス毎に連続で何回タイムアウトしているか保持。
SeriesTimeoutConter = collections.Counter()
N = 5
########関数############
def time_sep(t1,t2):
    #引数に（Str型の）開始時刻と終了時刻をうけて、整えて返す。（出力用に）
    dt1 = datetime.datetime(int(t1[:4]),int(t1[4:6]),int(t1[6:8]),int(t1[8:10]), int(t1[10:12]),int(t1[12:14]))
    dt2 = datetime.datetime(int(t2[:4]),int(t2[4:6]),int(t2[6:8]),int(t2[8:10]), int(t2[10:12]),int(t2[12:14]))
    return F'{dt1}から,{dt2}までの {(dt2-dt1).total_seconds()}秒間'
#########################
f = open('test.log','r')
f2 = open('output2.txt','w')

for line in f:
    #データを1行ずつ読み込む。
    Time,Address,Ping = line.rstrip().split(',')

    if Ping == '-':
        #タイムアウトなら、SeriesTimeoutConterの値に１プラスする。タイムアウトしていない場合は、後で０にする。
        SeriesTimeoutConter[Address] += 1

    if Ping == '-' and Address not in temp_dict.keys():
        #タイムアウトが開始したなら、temp_dictに入れる
        temp_dict[Address] = Time
    elif Ping != '-' and Address in temp_dict.keys() and SeriesTimeoutConter[Address] >= N:
        #故障期間が終了（今回はタイムアウトしていなく、前回まで連続N回以上タイムアウトしていた）場合,ファイルに記録する。
        f2.write('サーバーアドレス:'+Address+'が故障　'+time_sep(temp_dict[Address],Time)
                +F' (連続{SeriesTimeoutConter[Address]}回タイムアウト)'+'\n')

    #タイムアウトしていないなら、SeriesTimeoutConterの値を０に戻す。
    if Ping != '-':
        SeriesTimeoutConter[Address] = 0
        #タイムアウト開始時間として保持していたデータを削除。
        if Address in temp_dict.keys():
            del temp_dict[Address]


f.close()
f2.close()
