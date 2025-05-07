import re
import requests
import time
from datetime import datetime, timedelta,timezone
import json
import pandas as pd

def get_original_log(data):
    """默认查询最近5d,返回最原始的日记信息"""
    # 从输入数据中提取参数
    project = data["project"]
    logStore = data["logStore"]
    url = "https://xjp-logger-service-s-backend-sysop.inshopline.com/api/getLogs"
    headers = {"Content-Type": "application/json"}
    line = data.get("line", 2)
    offset = data.get("offset", 0)
    # 计算时间范围
    time_15_minutes_ago = datetime.now() - timedelta(days=1)
    timestamp_15_minutes_ago = int(time_15_minutes_ago.timestamp())
    start_time = timestamp_15_minutes_ago
    end_time = int(time.time())
    # 覆盖默认时间范围，如果提供了自定义时间
    start_time = data.get("from",start_time)
    end_time = data.get("to", end_time)
    # 设置请求参数
    params = {"project": project, "logStore": logStore, "from": start_time, "to": end_time,"line":line,"offset":offset}
    # 添加查询条件
    if "query" in data:
        query = data["query"]
        params["query"] = query
    response = requests.get(url, params=params, headers=headers).json()
    return response

def get_original_count(data):
    """查询日记条数"""
    # 从输入数据中提取参数
    project = data["project"]
    logStore = data["logStore"]
    url = "https://sls4service.console.aliyun.com/console/logstoreindex/getHistograms.json"
    headers = {"Content-Type": "application/json"}
    # 计算时间范围
    time_15_minutes_ago = datetime.now() - timedelta(days=1)
    timestamp_15_minutes_ago = int(time_15_minutes_ago.timestamp())
    start_time = timestamp_15_minutes_ago
    end_time = int(time.time())
    # 覆盖默认时间范围，如果提供了自定义时间
    start_time = data.get("from",start_time)
    end_time = data.get("to", end_time)
    # 设置请求参数
    params = {"project": project, "logStore": logStore, "from": start_time, "to": end_time,"reverse":True}
    # 添加查询条件
    if "query" in data:
        query = data["query"]
        params["query"] = query
    response = requests.get(url, params=params, headers=headers).json()
    print(response)
    # print(response["data"]["count"])
    # return response


def get_msg_log(data):
    """处理返回的日记，"""
    response = get_original_log(data)
    logs = response["data"]["logs"]
    # print("logs",logs)
    m_contents = [log["mLogItem"]["mContents"] for log in logs]
    # print(json.dumps(m_contents))
    log_msg_list = []
    for cotent in m_contents:
        log_msg = {}
        for t in cotent:
            if t["mKey"]=="msg" or t["mKey"]=="message":
                log_msg["msg"] = t["mValue"]
            elif t["mKey"]=="traceId":
                log_msg["traceId"] = t["mValue"]
        log_msg_list.append(log_msg)
    return log_msg_list

def get_http_data(http_data):
    """提取go服务http请求日记"""
    fields = {}
    patterns = {
        'method': r'(?<=method: )\s*(\w+)',
        'uri': r'(?<=uri: )\s*(?P<uri>.+)',
        'requestHeader': r'(?<=requestHeader: )\s*(\{.*?\})',
        'requestParams': r'(?<=requestParams: )\s*(\{.*?\})',
        'requestBody': r'(?<=requestBody: )(\{[^}]+\})[\s\S]*?(?=responseCode)',
        'responseCode': r'(?<=responseCode: )\s*(\d+)',
        'responseHeader': r'(?<=responseHeader: )\s*(\{.*?\})',
        'responseBody': r'(?<=responseBody: )\s*(\{.*?\})[\s\S]*?(?=error)'
    }
    for i in patterns.keys():
        # print(i)
        match = re.search(patterns[i], http_data)
        if match:
            result = match.group(0)
            fields[i] = result
            # print("%s:"%i,result)
    # print(fields)
    if "requestHeader" in fields:
        fields['requestHeader'] = json.loads(fields['requestHeader'])
    if "requestParams" in fields:
        fields['requestParams'] = json.loads(fields['requestParams'])
    if "requestBody" in fields:
        fields['requestBody'] = json.loads(fields['requestBody'])
    if "responseHeader" in fields:
        fields['responseHeader'] = json.loads(fields['responseHeader'])
    if "responseBody" in fields:
        fields['responseBody'] = json.loads(fields['responseBody'])
    return fields

def get_java_http_data(http_data):
    """提取java的日记http请求"""
    fields = {}
    patterns = {
        "urlEvent": r"urlEvent:(.*?),",
        "request": r"request:\{(.*?)\}",
        "method": r"method:\s*(\w+)",
        "queryParams": r"queryParams:\{(.*?)\}",
        "stringData": r"stringData:\{\{(.*?)\}\}",
        "headers": r"headers:\{(.*?)\}",
        "response": r"response:\{(.*?)\}"
    }
    for i in patterns.keys():
        # print(i)
        match = re.search(patterns[i], http_data)
        if match:
            result = match.group(0)
            fields[i] = result.strip()
            # print("%s:"%i,result)
    # print(json.dumps(fields))
    #JSON 字符串进行序列化
    # print(fields["requestBody"])
    fields['urlEvent'] = fields['urlEvent'].replace(",","").replace("urlEvent:","").strip()
    fields['method'] = fields['method'].replace("method:","").strip()
    # fields['requestHeader'] = json.loads(fields['headers'])
    requestParams = fields['queryParams'].replace("queryParams:","").strip()
    # print("---:",requestParams)
    fields['requestParams'] = requestParams
    requestBody = fields['stringData'].replace("stringData:","")
    # print("---:",requestBody)
    fields['requestBody'] = requestBody
    response = fields['response'].replace("response:","")
    fields['responseBody'] = response
    print("fields:",fields)
    return fields


def sc_assert(data):
    """

    :param data: 格式：[{"actual": "123", "expect": "123", "type": "eq"}, {"actual": "1234", "expect": "123", "type": "in"},
              {"actual": "123", "expect": "123"}]
    :return:
    """
    for i in data:
        actual = i["actual"]
        expect = i["expect"]
        type= i.get("type","eq")
        # data_type = i.get("data_type","str")
        if type=="eq":
            try:
                assert actual==expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败"%(actual,expect)
        elif type == "neq":
            try:
                assert actual != expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type=="in":
            try:
                assert actual in expect or expect in actual
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "notin":
            try:
                assert actual not in expect or expect not in actual
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "gt":
            try:
                assert actual>expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "egt":
            try:
                assert actual >= expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "lt":
            try:
                assert actual < expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "elt":
            try:
                assert actual <= expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)

def get_current_utc_time():
    # 获取当前 UTC 时间
    current_utc_time = datetime.now(timezone.utc)
    # 格式化为 YYYY-MM-DDTHH:MM
    formatted_time = current_utc_time.strftime('%Y-%m-%dT%H:%M')
    return formatted_time

def str_to_stamp(time_string,format="%Y-%m-%dT%H:%M:%S.%fZ"):
    # 解析时间字符串为 datetime 对象
    # 使用 strptime 方法并指定格式
    if "Z" in time_string:
        dt_utc = datetime.strptime(time_string, format).replace(tzinfo=timezone.utc)
        # 格式化为所需的字符串格式
        time_string = dt_utc.strftime(format)[:-3] + '+00:00'
        # dt = datetime.strptime(time_string, format)
        # # 转换为时间戳
        # timestamp = int(dt.timestamp()*1000)
        # return timestamp
    if "+" in time_string:
        #fromisoformat 只支持三位数字（即毫秒）
        time_string = time_string[:-7]  # 去掉最后的时区偏移
        time_string = time_string+"+00:00"  # 加上时区偏移
        # print(time_string)
    print(time_string)
    dt = datetime.fromisoformat(time_string)
    return int(dt.timestamp() * 1000)

def get_stamp_time(data):
    #拿到指定时间的时间戳
    num = data.get("num",5)
    time_type = data.get("time_type","add")
    unit = data.get("unit","minutes")
    # 获取当前 UTC 时间
    now = datetime.now()
    if time_type not in {"add", "sub"}:
        raise ValueError("Invalid time_type. Use 'add' or 'sub'.")
    stamp_time = now+timedelta(**{unit:num if time_type=="add" else -num})
    return int(stamp_time.timestamp()*1000)

def write_excel(data, file_name = "../data/live_OA.csv", columns=None):
    # 将数据转换为 DataFrame
    if columns is None:
        columns = ["urlEvent", "method","requestParams","requestBody","responseBody"]
    df = pd.DataFrame(data, columns=columns)
    # 定义 Excel 文件名
    excel_file = file_name
    # 写入 Excel 文件
    df.to_excel(excel_file, index=False, sheet_name='Sheet1')

def is_contain(oa_http_data,value):
    for i in oa_http_data:
        if value in i:
            return True

def get_service_http_data(data):
    log_msg_list = get_msg_log(data)
    oa_http_data = []
    for i in log_msg_list:
        msg = i["msg"]
        field = get_java_http_data(msg)
        urlEvent = field["field"]
        method = field["method"]
        if is_contain(oa_http_data, urlEvent) and is_contain(oa_http_data, method):
            continue
        else:
            oa_http_data.append(field)



if __name__=="__main__":
    pass















