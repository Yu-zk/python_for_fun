# -*- coding:utf-8 -*-

import requests, re
import time
import mysql.connector
import datetime
import codecs

mydb = mysql.connector.connect(
        host="**************",
        port="3306",
        user="*******************",
        passwd="*******************",
        database="mp")
mycursor = mydb.cursor()
goal = []



def whtml(qd):
    f = codecs.open("/var/www/html/index.html", "w","utf-8")
    # f = codecs.open("D:\\index.html", "w","utf-8")
    # s='<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><meta http-equiv="refresh" content="120"><p ALIGN=Right style = "margin:0px">'
    # s=s+  '<table width="100%" ><tr><td width="25%"><p ALIGN=Right style = "margin:0px"><font size="7">'
    # s=s+  '今日签到人数:'+str(qd)+'<br>弹幕发"签到"即可'
    # s=s+'</font></p></td><td><marquee  direction="left"  behavior="scroll"  scrollamount="18"  scrolldelay="5"  loop="10"   ><p ALIGN=Right '
    # s=s+'style = "margin:0px"><font  size="7" style="font-family:隶书" >'
    # j=0
    # ss=""
    # for i in goal:
    #     if j==10:
    #         j=0
    #         ss=ss+'  以"目标"开头发送弹幕，设一个小目标吧！     '
    #     ss = ss + i + '    '
    #     j = j + 1
    # ss=ss.replace(' ','&nbsp;')
    # s=s+ss[:int(len(ss)/2)]+'<br>'+ss[int(len(ss)/2+1):]
    # s=s+'</font></p></marquee>'

    s='<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><meta http-equiv="refresh" content="120"><p ALIGN=Right style = "margin:0px"><p ALIGN=left style = "margin:0px"><font size="8">今日签到人数:'
    s=s+str(qd)+'<br>"目标"开头发弹幕 设一个小目标吧！ </font></p><marquee direction="up"  behavior="scroll"  scrollamount="8"  scrolldelay="5"  loop="10" height="350"  ><p ALIGN=left style = "margin:0px"><font  size="7" style="font-family:隶书" >'
    ss=''
    for i in goal:
        ss = ss + i +'<br>'
    # ss=ss.replace(' ','&nbsp;')
    s=s+ss
    s=s+'</font></p></marquee>'
    # print(s)

    f.write(s)
    f.close()

def add(id,time2,content,roomid, token,headers,qd):
    try:
        sql=""
        finish = 0
        s = ""
        if content[0:2] == '目标' or content[1:3] == '目标':
            s = id + "设置成功，完成目标后别忘了告诉主播，弹幕发‘完成’"
            goal.append(id+content.replace(' ','').replace('：','').replace('目标',':'))
            finish = 1
        elif content[0:2] == '完成':
            s = "恭喜" + id + "完成目标"
            sql = "update barrage  set finish =  2 where finish = 1 and id ='" + id + "'; "
            for i in goal:
                if i[:len(id)] == id:
                    goal.remove(i)

            mycursor.execute(sql)
            mydb.commit()
            finish = 2

        sql = "insert into barrage (id, time, content, finish) "
        sql = sql + "value('" + id + "','" + time2 + "','" + content + "'," + str(finish) + ")"
        try:
            mycursor.execute(sql)
            mydb.commit()
        except:
            print("exp" + sql)
        sql = "select id,point,number,total,status,time from biliid where id='" + id + "' limit 1 "

        mycursor.execute(sql)
        rid = mycursor.fetchall()
        if rid == []:
            sql = "insert into biliid (id, point, number,total) "

            sql = sql + "value('" + id + "',0,1,0);"
            point = 0
        else:
            sql = "update biliid  set number =  "
            point = rid[0][1]
            total = rid[0][3]
            sql = sql + str(rid[0][2] + 1) + " where id ='" + id + "'; "
        try:
            mycursor.execute(sql)
            mydb.commit()
        except:
            print("exp" + sql)

        if content.find('签到')>=0 or content.find('打卡')>=0:
            # sql = "select time from biliid where id='" + id + "' limit 1 "
            # sql = "select status from biliid where id='" + id + "' limit 1 "
            # mycursor.execute(sql)
            # r = mycursor.fetchall()

            # or r == [(None,)]
            if rid==[] or rid[0][5]==None  :
                # sql="insert into biliid (id,point, status, time)"
                # sql=sql+"value('" + id + "',1,1,'" + time2 + "')"
                sql = "update biliid  set point =  "
                sql = sql + str(point + 1) + "  , status = 1 , time =  '" + time2 + "' where id ='" + id + "'; "
                s = id + "签到成功，这是第1次签到，关注一波之后常来呀"
                qd=qd+1
                mycursor.execute(sql)
                mydb.commit()

            # elif (datetime.datetime.now() - r[0][0] + datetime.timedelta(seconds=21600)).days > 0:
            elif rid[0][4]==0 :
                sql = "update biliid  set point =  "
                sql = sql + str(point + 1) + "  , status = 1 , time =  '" + time2 + "' where id ='" + id + "'; "
                s = id + "签到成功，这是第" + str(point + 1) + "天来啦"
                qd = qd + 1
                mycursor.execute(sql)
                mydb.commit()
            else:
                s = id + "今天签过了，明天再来吧"
        elif content.replace(' ', '') == '开始':
            sql = "update biliid  set status = 1, time = '" + time2+"'  where id ='" + id + "'; "
            s = id[:9] + "继续学习吧"
            qd = qd + 1
            mycursor.execute(sql)
            mydb.commit()

        #status 1=on,0=off
        elif content.find('拜拜') >-1:
            if rid == [] or rid ==[(None,)]:
                s = id + "今天还没有签到呢"
            elif rid[0][4]==0:
                s = id + "今天还没有签到呢"
            elif rid[0][4]==2:
                s = id + "已经拜拜过了"
            else:
                t = str(datetime.datetime.now() - rid[0][5]).split(':')
                if int(t[0]) > 12:
                    s = id[:9] + "貌似今天还没有签到呢"
                else:
                    s = id + "今天学习" + t[0] + "小时" + t[1] + "分钟,"
                    total = total + int(t[0]) * 60 + int(t[1])
                    s = s + "一共学习了" + str(total) + "分钟啦"
                    send(s, roomid, token, headers)
                    s = "拜拜，明天见"
                    sql = "update biliid set total =  "
                    sql = sql + str(total) + " , status = 2 where id ='" + id + "'; "
                    # qd = qd - 1
                    mycursor.execute(sql)
                    mydb.commit()
        send(s, roomid, token, headers)
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err)+'\n'+s+'\n'+sql)
    return qd


def send(barrage,roomid,token,headers):
    url_send = 'https://api.live.bilibili.com/msg/send'
    barrage=barrage.replace('摸','*').replace('撸', '*').replace('鸡鸡', '*')
    if barrage=='':
        return
    l=len(barrage)
    i=0
    while i<l:
        s=barrage[i:i+19]
        i=i+19
        time.sleep(1)
        data = {
            'color': '16777215',
            'fontsize': '25',
            'mode': '1',
            'msg': s,
            'rnd': '1555761478',
            'roomid': roomid,
            'bubble': '0',
            'csrf': token,
            'csrf_token': token
        }
        try:
            html_send = requests.post(url_send, data=data, headers=headers)
            result = html_send.json()
            if result['message'] == '你被禁言啦':
                print('*' * 5 + '禁言,失败' + '*' * 5)
                exit()
            if result['code'] == 0 and result['message'] == '':
                print('*' * 5 + '[' + barrage + ']' + ' 成功~' + '*' * 5)
            else:
                print('*' * 5 + '[' + barrage + ']' + ' 失败' + '*' * 5)
        except:
            print('*' * 5 + '[' + barrage + ']' + ' 失败except' + '*' * 5)




def main():
    qd=40
    url = 'https://live.bilibili.com/5290652'   # input('请输出您要查看的直播房间网址链接:')
    cookie ='*************************************************'
    token = re.search(r'bili_jct=(.*?);', cookie).group(1)
    html = requests.get(url).text
    # if re.search(r'room_id":(.*?),', html):
    #     roomid = re.search(r'room_id":(.*?),', html).group(1)
    #     print('直播房间号为:' + roomid)
    # else:
    #     print('抱歉,未找到此直播房间号~')
    roomid='5290652'
    l = []
    name=''
    # t = datetime.datetime.strptime('Jun 1 2000', '%b %d %Y')
    t = datetime.datetime.now()
    time.sleep(5)

    sql = "select id,content from barrage where finish =1"
    mycursor.execute(sql)
    r = mycursor.fetchall()
    if r!=[]:
        for i in r:
            goal.append(i[0]+" "+i[1].replace(' ', '').replace('：', '').replace('目标',':'))

    # print(goal)
    b = True
    ti =0




    while True:
        url = 'https://api.live.bilibili.com/ajax/msg'
        form = {
            'roomid': roomid,
            'visit_id': '',
            'csrf_token': token
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            'Cookie': cookie
        }
        html = requests.post(url, data=form)
        result = html.json()['data']['room']

        # abc = '''   '''
        # t1 = 50
        # a1 = abc.split('\n')

        # for i in a1:
        #     b = (i.split('：'))
        #     print(b)
        #     add(b[0], '2019-05-19 20:' + str(t1) + ':00', b[1], roomid, token, headers, qd)
        #     t1 = t1 + 1
        # 1 + atr

        # for test

        # 1+shws

        for i in result:
            time.sleep(1)
            t1 = datetime.datetime.strptime(str(i['timeline']), '%Y-%m-%d %H:%M:%S')
            name1 = i['nickname']
            if t1 > t:  # or i['nickname'] != name
                time2 = i['timeline']
                content = i['text']
                s = time2 + '[' + name1 + ']:' + content
                l.append(s)
                t = t1
                name = name1
                print(s)
                if name1 != 'zk的机器人':
                    qd = add(name1, time2, content, roomid, token, headers, qd)
                # if barrage!="":
                # send(s, roomid, token,headers)
                # print('--'+barrage)

        time.sleep(5)
        ti = ti + 1
        if ti == 10:
            whtml(qd)
            ti = 0




if __name__ == '__main__':
    main()