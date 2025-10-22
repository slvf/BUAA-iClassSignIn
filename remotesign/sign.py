import requests
import json
import time
import datetime


def sign(student_id):
    # 获取用户id和sessionId，为查询课表和根据课表打卡做准备
    url = 'https://iclass.buaa.edu.cn:8346/app/user/login.action'
    para = {
        'password': '',
        'phone': student_id,
        'userLevel': '1',
        'verificationType': '2',
        'verificationUrl': ''
    }

    #尝试获取用户信息
    try:
        res = requests.get(url=url, params=para)
        userData = json.loads(res.text)
        userId = userData['result']['id']
        sessionId = userData['result']['sessionId']
        
        # 获取当前日期
        today = datetime.datetime.today()
        dateStr = today.strftime('%Y%m%d')
        # 查询课表
        url = 'https://iclass.buaa.edu.cn:8346/app/course/get_stu_course_sched.action'
        para = {
            'dateStr': dateStr,
            'id': userId
        }
        headers = {
            'sessionId': sessionId,
        }
        res = requests.get(url=url, params=para, headers=headers)
        json_data = json.loads(res.text)
        if json_data['STATUS'] == '0':
            for item in json_data['result']:
                    courseSchedId = item['id']
                    params = {
                        'id': userId
                    }
                    
                    classBeginTime = item['classBeginTime']
                    classEndTime = item['classEndTime']
                    date = classBeginTime[:10] 
                    begin = classBeginTime[11:16] 
                    end = classEndTime[11:16]

                    current_time = datetime.datetime.now()
                    current_time_str = current_time.strftime('%Y-%m-%d %H:%M')
                    
                    delta = datetime.timedelta(minutes=10)
                    #只能在课程开始前10分钟到课程结束时间之间签到
                    check_time_begin = (current_time + delta).strftime('%Y-%m-%d %H:%M')
                    check_time_end = (current_time).strftime('%Y-%m-%d %H:%M')

                    #只保留时间部分
                    check_time_begin = check_time_begin[11:16]
                    check_time_end = check_time_end[11:16]

                    if current_time_str[:10] == date and begin <= check_time_begin and check_time_end <= end:
                        current_timestamp_seconds = time.time()
                        current_timestamp_milliseconds = int(current_timestamp_seconds * 1000)
                        str = f'http://iclass.buaa.edu.cn:8081/app/course/stu_scan_sign.action?courseSchedId={courseSchedId}&timestamp={current_timestamp_milliseconds}'
                        r = requests.post(url=str, params=params)                
                                
                        if r.ok:
                            return f"已打卡：{date}\t{item['courseName']}\t{begin}-{end}"
                    
            return '当前时间无可签到课程'
        
    except Exception as e:
        return '查无此人，请检查网络或学号是否正确'
       