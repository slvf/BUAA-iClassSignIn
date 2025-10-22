import asyncio
import aiohttp
import requests

import json
import time
import datetime


def check_sign_status(student_id): 

    # 获取用户id和sessionId，为查询课表和根据课表打卡做准备
    url = 'https://iclass.buaa.edu.cn:8346/app/user/login.action'
    para = {
        'password': '',
        'phone': student_id,
        'userLevel': '1',
        'verificationType': '2',
        'verificationUrl': ''
    }
    
    try:
        res = requests.get(url=url, params=para)
        userData = json.loads(res.text)

        global userId 
        userId = userData['result']['id']
        sessionId = userData['result']['sessionId']

        #异步协程，加快速度
        async def fetch_date_data(session: aiohttp.ClientSession, date: datetime.datetime, userId: str, sessionId: str, url: str):

            dateStr = date.strftime('%Y%m%d')
            params = {
                'dateStr': dateStr,
                'id': userId
            }
            headers = {
                'sessionId': sessionId
            }
            
            try:
                async with session.get(url=url, params=params, headers=headers) as res:
                    text = await res.text()
                    return (date, json.loads(text))
                
            except Exception as e:
                return (date, None)  # 请求失败时返回None


        async def main(userId: str, sessionId: str, url: str):
            # 主协程：并发请求+处理结果
            today = datetime.datetime.today()
            dates = [today + datetime.timedelta(days=-i) for i in range(150)]
            
            async with aiohttp.ClientSession() as session:
                # 创建150个异步任务（每个日期对应1个任务）
                tasks = [fetch_date_data(session, date, userId, sessionId, url) for date in dates]
                results = await asyncio.gather(*tasks, return_exceptions=False)
            
            cnt = 0  # 连续没课天数
            content_list = []
            id_list = []
            
            for date, json_data in results:
                if cnt == 7:
                    break  # 连续7天没课，停止处理
                
                # 处理请求失败的情况（json_data为None）
                if json_data is None:
                    cnt += 1
                    continue
                
                if json_data.get('STATUS') == '0':
                    cnt = 0  # 重置连续没课天数
                    for item in json_data.get('result', []):
                        if item.get('signStatus') != '1':  # 未签到
                            classBeginTime = item.get('classBeginTime', '')
                            date_str = classBeginTime[:10] if classBeginTime else date.strftime('%Y-%m-%d')

                            content_list.append(f"补签： {item.get('courseName', '')} {date_str}\n")
                            id_list.append(item.get('id', ''))
                else:
                    cnt += 1  # 没课，连续天数+1
            
            return {"course": content_list, "id": id_list}


        USER_ID = userId
        SESSION_ID = sessionId
        COURSE_URL = 'https://iclass.buaa.edu.cn:8346/app/course/get_stu_course_sched.action'
            
        result = asyncio.run(main(USER_ID, SESSION_ID, COURSE_URL))

        return result
            
    except Exception as e:
        return {"course": 'error', "id" : 'error'}
            

def late_sign(id_given):
    courseSchedId = id_given
    params = {
        'id': userId
    }
    current_timestamp_seconds = time.time()
    current_timestamp_milliseconds = int(current_timestamp_seconds * 1000)
    str = f'http://iclass.buaa.edu.cn:8081/app/course/stu_scan_sign.action?courseSchedId={courseSchedId}&timestamp={current_timestamp_milliseconds}'
    r = requests.post(url=str, params=params)

    if r.ok:
        return '签到成功'
    else:
        return '未知错误'

