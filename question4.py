import collections
import datetime
##----------管理データ＆パラメータ---------------------------------------------

#temp_dict = {サーバーアドレス:タイムアウト発生開始時間}
#サーバーアドレス毎にタイムアウト開始時間を保持しておく。
temp_dict = {}

#SeriesTimeoutConter = {サーバーアドレス:連続タイムアウト回数}
#サーバーアドレス毎に連続で何回タイムアウトしているか保持。
SeriesTimeoutConter = collections.Counter()
N = 3

#Q_dict = {サーバーアドレス:直近のPingが要素のキュー}
Q_dict = {}

#P_sum ={サーバーアドレス:直近m回のPingの合計値}
Ping_sum = {}
m = 7
t = 100
#直近m回のPingの合計値を計算する際、タイムアウトしている場合の応答時間を　(t+dt)　と近似する。
dt = 15

#temp_dict = {サーバーアドレス:過負荷状態の発生開始時間}
#サーバーアドレス毎に過負荷状態の開始時間を保持しておく。
temp_dict2 = {}

#Network_dict = {ネットワークアドレス:そこに属する稼働中のサーバーアドレスを要素に持つリスト}
SubNet_dict = collections.defaultdict(list)

#現在、故障中（N回以上連続タイムアウト）のサーバーアドレスを保持するリスト。
Now_accident = []

#temp_dict3 = {ネットワークアドレス:故障状態の発生開始時間}
#ネットワークアドレス毎に故障状態の開始時間を保持しておく。
temp_dict3 = {}

#SeverConter = {サーバーアドレス:入力されていない回数}
#サーバーアドレス毎に、全入力の内、連続で何回入力されていない保持。
#→SeverChangePara以上になると、作動していないとみなす。(サブネットの故障を正しくチェックするため)
SeverConter = collections.Counter()
SeverChangePara = 10**3



##--------------関数----------------------------------------------------------
def time_sep(t1,t2):
    #引数に（Str型の）開始時刻と終了時刻をうけて、整えて返す。（出力用に）
    dt1 = datetime.datetime(int(t1[:4]),int(t1[4:6]),int(t1[6:8]),int(t1[8:10]), int(t1[10:12]),int(t1[12:14]))
    dt2 = datetime.datetime(int(t2[:4]),int(t2[4:6]),int(t2[6:8]),int(t2[8:10]), int(t2[10:12]),int(t2[12:14]))
    return F'{dt1}から,{dt2}までの {(dt2-dt1).total_seconds()}秒間'

def calc_sumping(Q,p):
    #引数に、直近m+1個のPingが入ったキューと、前回から直近m回のping合計値を受け取り、今回から直近m回のping合計値を返す。
    #また、キューから要素を1つ取り出しm個にする。
    j = Q.popleft()
    if j == '-':
        temp1 = t+dt
    else:
        temp1 = int(j)
    if Ping == '-':
        temp2 = t+dt
    else:
        temp2 = int(Ping)

    # temp1=直近m+1回目のping、 temp2=現在のping
    return p-temp1+temp2

def net_classify(a):
    #引数にサーバーアドレスを受け取って、ネットワークアドレス毎に分類する。
    #また、使っていないサーバーアドレスを取り除く。(サブネットの故障を正しくチェックするため)

    def find_networkaddress(aa):
    #引数にサーバーアドレスを受け取って、ネットワークアドレスを返す。
        a1,a2 = aa.split('/')
        a3 = int(int(a2)/8)
        a4 = list(a1.split('.'))
        network_address = ''
        for j in range(a3):
            network_address += a4[j]
            if j != a3-1:
                network_address += '.'
        return network_address

    #ネットワークアドレス毎に分類する。
    network_address = find_networkaddress(a)
    if a not in SubNet_dict[network_address]:
        SubNet_dict[network_address].append(a)

    #使っていないサーバーアドレスを取り除く。(サブネットの故障を正しくチェックするため)
    if a not in SeverConter.keys():
        SeverConter[a] = 0
    for sa in SeverConter.keys():
        if sa == a:
            SeverConter[sa] = 0
        SeverConter[sa] += 1
        if SeverConter[sa] >=  SeverChangePara:
            #連続でSeverChangePara回以上入力がないなら、稼働していないとみなし、サーバーアドレスを取り除く。
            del SeverConter[sa]
            SubNet_dict[find_networkaddress(sa)].remove(sa)

    return

##---------------------------------------------------------------------
f = open('test.log','r')
f2 = open('output4.txt','w')

for line in f:
    #データを1行ずつ読み込む。
    Time,Address,Ping = line.rstrip().split(',')

    #ネットワークアドレス毎に、稼働しているサーバーを分類する。
    net_classify(Address)


##-------------以下、過負荷状態をチェック---------------------------------------
    if Address not in Q_dict.keys():
        Q_dict[Address] = collections.deque()
    else:
        #現在のPingを追加
        Q_dict[Address].append(Ping)

    if Address not in Ping_sum.keys():
        #最初のｍ個の合計を計算する時のために、0で初期化しておく。(以降０になることはない)
        Ping_sum[Address] = 0

    if len(Q_dict[Address]) == m and Ping_sum[Address] == 0:
        #最初のｍ個の合計値を計算する。
        for q1 in Q_dict[Address]:
            if q1 == '-':
                Ping_sum[Address] += (t+dt)
            else:
                Ping_sum[Address] += int(q1)

    if len(Q_dict[Address]) == m+1:
        #直近ｍ回の合計値を計算する。
        Ping_sum[Address] = calc_sumping(Q_dict[Address],Ping_sum[Address])

    if Ping_sum[Address] > t*m and Address not in temp_dict2.keys():
        #過負荷状態の発生開始時間を保持しておく。
        temp_dict2[Address] = Time
    elif Ping_sum[Address] < t*m and Address in temp_dict2.keys():
        #過負荷状態の期間が終了したら、ファイルに記録して、temp_dict2から削除する
        f2.write('サーバーアドレス:'+Address+'が過負荷状態　'+time_sep(temp_dict2[Address],Time)+'\n')
        del temp_dict2[Address]

##-----------------以下、故障をチェック--------------------------------------
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


##----------以下、サブネットの故障をチェック-------------------------------------
    #---Now_accidentを管理---------------------------------------------------
    if Ping == '-' and SeriesTimeoutConter[Address] >= N:
        #連続N回以上タイムアウトしている時、Now_accidentに重複なく保持する。
        if Address not in Now_accident:
            Now_accident.append(Address)
    else:
        if Address  in Now_accident:
            Now_accident.remove(Address)

    #---現在故障しているサブネットを調べて、故障開始or故障終了をチェック---------
    for n1 in SubNet_dict.keys():
        #n1はネットワークアドレス
        flag = False
        for n2 in SubNet_dict[n1]:
            #n2はサーバーアドレス
            if n2 not in Now_accident:
                flag = True
                break
        if flag == False:
            #flag=Falseのままならば、故障中。
                if n1 not in temp_dict3.keys():
                    #サブネットの故障開始期間を保持する。
                    temp_dict3[n1] = Time
        else:
            if n1 in temp_dict3.keys():
                #サブネットの故障期間が終了したならば、ファイルに記録して、temp_dict3から故障開始時間を削除する。
                f2.write('ネットワークアドレス:'+n1+'が故障　'+time_sep(temp_dict3[n1],Time)+'\n')
                del temp_dict3[n1]

##----------------------------------------------------------------------------


f.close()
f2.close()
