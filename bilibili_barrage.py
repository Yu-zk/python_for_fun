# -*- coding:utf-8 -*-

import requests, re
import time
import mysql.connector
import datetime
import codecs

mydb = mysql.connector.connect(
        host="119.***.***.***",
        port="3306",
        user="********",
        passwd="***********",
        database="****")
mycursor = mydb.cursor()
goal = []



def whtml(qd):
    f = codecs.open("/var/www/html/index.html", "w","utf-8")
    s='<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><meta http-equiv="refresh" content="10"><p ALIGN=Right style = "margin:0px"><font size="7" color="blue">当前签到人数:'+str(qd)+'</font></p>'
    s=s+'<p ALIGN=Right style = "margin:0px"><font size="5" color="blue">发送以"目标"开头弹幕，设一个小目标吧！</font></p>'
    s=s+'<p ALIGN=Right style = "margin:0px"><font size="5">'
    for i in goal:
        s=s+i+'<br>'
    s=s+'</font></p>'
    f.write(s)
    f.close()

def add(id,time2,content,roomid, token,headers,qd):
    try:
        sql=""
        finish = 0
        s = ""
        if content[0:2] == '目标':
            s = id + "设置成功，完成后别忘说‘完成’"
            goal.append(id+content.replace('目标',''))
            finish = 1
        elif content.find('完成')>=0:
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
            sql = "select time from biliid where id='" + id + "' limit 1 "
            mycursor.execute(sql)
            r = mycursor.fetchall()

            if r == [(None,)]:
                # sql="insert into biliid (id,point, status, time)"
                # sql=sql+"value('" + id + "',1,1,'" + time2 + "')"
                sql = "update biliid  set point =  "
                sql = sql + str(point + 1) + "  , status = 1 , time =  '" + time2 + "' where id ='" + id + "'; "
                s = id + "签到成功，这是第" + str(point + 1) + "天来啦"

                qd=qd+1

                mycursor.execute(sql)
                mydb.commit()
            elif (datetime.datetime.now() - r[0][0] + datetime.timedelta(seconds=21600)).days > 0:
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
                    sql = sql + str(total) + " , status = 0 where id ='" + id + "'; "
                    qd = qd - 1
                    mycursor.execute(sql)
                    mydb.commit()
        send(s, roomid, token, headers)
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err)+'\n'+s+'\n'+sql)
    return qd


def send(barrage,roomid,token,headers):
    url_send = 'https://api.live.bilibili.com/msg/send'
    barrage=barrage.replace('摸','*')
    barrage = barrage.replace('撸', '*')
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
    qd=0
    url = 'https://live.bilibili.com/5290652' 
    cookie ='_uuid=****************; buvid3=**-*-*-*-*********; LIVE_BUVID=**********; sid=*; DedeUserID=*; DedeUserID__ckMd5=*; SESSDATA=*%*%***; bili_jct=*; _dfcaptcha=*'
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
            goal.append(i[0]+" "+i[1].replace('目标',''))

    print(goal)
    b = True
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
        # add('test5', '2019-04-28 00:00:01', '签到', roomid, token, headers,qd)
        # for test
        for i in result:
            time.sleep(1)
            t1 = datetime.datetime.strptime(str(i['timeline']), '%Y-%m-%d %H:%M:%S')
            name1=i['nickname']
            if t1>t:   # or i['nickname'] != name
                time2=i['timeline']
                content=i['text']
                s = time2 + '[' + name1 + ']:' + content
                l.append(s)
                t=t1
                name=name1
                print(s)
                if name1 !='zk的机器人':
                    qd = add(name1, time2, content,roomid, token,headers,qd)
                # if barrage!="":
                    # send(s, roomid, token,headers)
                    # print('--'+barrage)
        whtml(qd)
        time.sleep(5)



if __name__ == '__main__':
    main()