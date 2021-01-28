import datetime
import json
import random
import requests
import time

import campus


def main():
    # 定义变量
    success, failure = [], []
    # sectets字段录入
    phone, password = [], []
    # 多人循环录入
    deviceId='ffffffff-fcdd-0ad5-0000-00000033c587'
    while True:
        try:
            users = input()
            info = users.split(',')
            phone.append(info[0])
            password.append(info[1])
            #deviceId.append(info[3])
            
        except:
            break

    # 提交打卡
    for index, value in enumerate(phone):
        print("开始尝试为用户%s打卡" % (value[-4:]))
        count = 0
        while (count <= 3):
            try:
                token = campus.campus_start(phone[index], password[index], deviceId)
                userInfo = getUserInfo(token)
                if mark == 0:
                    response = checkIn(userInfo, token)
                if mark == 1:
                    ownphone = phone[index]
                    response = check(ownphone, userInfo, token)
                strTime = getNowTime()
                if response.json()["msg"] == '成功':
                    success.append(value[-4:])
                    print(response.text)
                    msg = strTime + value[-4:] + "打卡成功"
                    if index == 0:
                        result = response
                    break
                else:
                    failure.append(value[-4:])
                    print(response.text)
                    msg = strTime + value[-4:] + "打卡异常"
                    count = count + 1
                    if index == 0:
                        result = response
                    if count <= 3:
                        print('%s打卡失败，开始第%d次重试...' % (value[-4:], count))
                    time.sleep(5)
            except Exception as e:
                print(e.__class__)
                failure.append(value[-4:])
                strTime = getNowTime()
                msg = strTime + value[-4:] + "出现错误"
                count = count + 1
                result = "出现错误"
                if count <= 3:
                    print('%s打卡出错，开始第%d次重试...' % (value[-4:], count))
                time.sleep(3)
        print(msg)
        print("-----------------------")
    fail = sorted(set(failure), key=failure.index)
    title = "成功: %s 人,失败: %s 人" % (len(success), len(fail))
   
    try:
        print('开始qq推送')
        qqpush(success, fail)
    except:
        print('QQ推送出错')


# 时间函数
def getNowTime():
    cstTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=8))
    strTime = cstTime.strftime("%H:%M:%S ")
    return strTime


# 信息获取函数
def getUserInfo(token):
    for _ in range(3):
        try:
            data = {"appClassify": "DK", "token": token}
            sign_url = "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo"
            response = requests.post(sign_url, data=data)
            return response.json()['userInfo']
        except:
            print('getUserInfo 错误，Retry......')
            time.sleep(3)


# 校内打卡提交函数
def checkIn(userInfo, token):
    sign_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
    # 随机温度(36.0~36.8)
    a = random.uniform(36.0, 36.8)
    temperature = round(a, 1)
    jsons = {
        "businessType": "epmpics",
        "method": "submitUpInfo",
        "jsonData": {
            "deptStr": {
                "deptid": userInfo['classId'],
                "text": userInfo['classDescription']
            },
            # 如果你来自其他学校，请自行打卡抓包修改地址字段
            "areaStr": {"streetNumber": "", "street": "崇德路", "district": "天元区", "city": "株洲市", "province": "湖南省",
                        "town": "", "pois": "湖南工业大学新校区", "lng": 113.11425800000013 + random.random() / 1000,
                        "lat": 113.11425800000013 + random.random() / 1000, "address": "天元区崇德路湖南工业大学新校区",
                        "text": "湖南省-株洲市", "code": ""},
            "reportdate": round(time.time() * 1000),
            "customerid": userInfo['customerId'],
            "deptid": userInfo['classId'],
            "source": "app",
            "templateid": "pneumonia",
            "stuNo": userInfo['stuNo'],
            "username": userInfo['username'],
            "userid": round(time.time()),
            "updatainfo": [
                {
                    "propertyname": "temperature",
                    "value": temperature
                },
                {
                    "propertyname": "symptom",
                    "value": "无症状"
                },
                {
                    "propertyname": "isConfirmed",
                    "value": "否"
                },
                {
                    "propertyname": "isdefinde",
                    "value": "否.未隔离"
                },
                {
                    "propertyname": "isGoWarningAdress",
                    "value": "否"
                },
                {
                    "propertyname": "isTouch",
                    "value": "否"
                },
                {
                    "propertyname": "isFFHasSymptom",
                    "value": "没有"
                },
                {
                    "propertyname": "isContactFriendIn14",
                    "value": "没有"
                },
                {
                    "propertyname": "xinqing",
                    "value": "健康"
                },
                {
                    "propertyname": "bodyzk",
                    "value": "是"
                },
                {
                    "propertyname": "cxjh",
                    "value": "否"
                },
                {
                    "propertyname": "isleaveaddress",
                    "value": "否"
                },
                {
                    "propertyname": "gtjz0511",
                    "value": "否"
                },
                {
                    "propertyname": "medicalObservation",
                    "value": "绿色"
                },
                {
                    "propertyname": "ownPhone",
                    "value": "18674477364"
                },
                {
                    "propertyname": "emergencyContact",
                    "value": "联系人"
                },
                {
                    "propertyname": "mergencyPeoplePhone",
                    "value": "13272222656"
                },
                {
                    "propertyname": "assistRemark",
                    "value": ""
                }
            ],

            "gpsType": 1,
            "token": token
        },

    }
    # 提交打卡
    response = requests.post(sign_url, json=jsons)
    return response


# 校外打卡
def check(ownphone, userInfo, token):
    sign_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
    # 获取datajson
    post_json = {
        "businessType": "epmpics",

        "jsonData": {
            "templateid": "pneumonia",
            "token": token
        },
        "method": "getUpDataInfoDetail"
    }
    response = requests.post(sign_url, json=post_json).json()
    data = json.loads(response['data'])
    info_dict = {
        "add": data['add'],
        "areaStr": data['areaStr'],
        "updatainfo": [{"propertyname": i["propertyname"], "value": i["value"]} for i in
                       data['cusTemplateRelations']]
    }
    # 随机温度
    a = random.uniform(36.0, 36.8)
    temperature = round(a, 1)
    for i in info_dict['updatainfo']:
        if i['propertyname'] == 'temperature':
            i['value'] = temperature
    # 校外打卡提交json
    check_json = {
        "businessType": "epmpics",
        "method": "submitUpInfo",
        "jsonData": {

            "deptStr": {
                "deptid": userInfo['classId'],
                "text": userInfo['classDescription'],
            },

            "areaStr": info_dict['areaStr'],
            "reportdate": round(time.time()),
            "customerid": userInfo['customerId'],
            "deptid": userInfo['classId'],
            "source": "app",
            "templateid": "pneumonia",
            "stuNo": userInfo['stuNo'],
            "username": userInfo['username'],
            "userid": userInfo['userId'],

            "updatainfo": info_dict['updatainfo'],

            "gpsType": 1,
            "token": token
        }
    }
    res = requests.post(sign_url, json=check_json)
    return res


# QQ通知

def qqpush(success, fail):
    data = {
        "token": "10f179ec7405a6426d87b0e42b3aca51",
        "group_id": "698639533",
        "message": "大家早上好呀，今早已经打卡成功的用户如下:\n" + str(success) + "\n打卡失败用户如下:\n" +
                   str(fail) + "\n请打卡出问题的小伙伴联系下小高同学，没打卡的小伙伴尽快打卡。"

    }
    qq_url = 'http://api.qqpusher.yanxianjun.com/send_group_msg'
    try:
        req = requests.post(qq_url, data)
        if req.json()['status'] == True:
            print("QQ推送成功")
        else:
            print("QQ推送失败")
    except:
        print("QQ推送参数错误")


if __name__ == '__main__':
    mark = 0
    main()
