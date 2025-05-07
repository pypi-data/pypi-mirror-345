from mcp.server.fastmcp import FastMCP

import requests
import json
from typing import Tuple, List

# Create an MCP server
mcp = FastMCP("oppo-eap-mcp-server")


def auth(account: str, password: str, area: str) -> Tuple[str, str]: 
    """
        Use account and password to authenticate a user to get two tokens splitted by line
        Args:
            account: Account name
            password: Password
            area: Area code, 'zh' for china, 'yd' for india, 'dny' for southeast asia. don't accept other area code
        Returns:
            Tuple[str, str]: tuple of Two string-type tokens 
    """

    assert(area == "zh" or area == "yd" or area == "dny"), f"Error: area code {area} is not supported, please use 'zh', 'yd', 'dny'"

    url = "http://thirdpart.myoas.com/thirdpart-leida/common/getSessionKey"

    payload = json.dumps({
            "username": account,
            "password": password,
            "area": area
        })
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    if response.status_code != 200 or response.json()["code"] != 200:
        raise Exception(f"Error: username or password error, status code: {response.status_code}")
    response_json = response.json()
    
    if response_json["code"] != 200:
        raise Exception(f"Error: username or password error, status code: {response_json}")
    
    tgt = response_json["data"]["tgt"]
    token = response_json["data"]["token"]

    return (tgt, token)

def post(area: str, url: str, headers: dict = {}, data: dict = {}) -> str:
    """
        Send a request to the server
        Args:
            area: which area to query. 'zh' for china, 'yd' for india, 'dny' for southeast asia. don't accept other area code
            url: URL of the server
            headers: Additional Header of the request
            data: Data of the request
        Returns:
            str: Response from the server
    """
    Authorization_qodp, SessionKey = auth(USERNAME, PASSWORD, area)

    default_headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
        'Authorization': Authorization_qodp,
        'Session-Key': SessionKey
    }

    default_headers.update(headers)
    payload = json.dumps(data)
    response = requests.request("POST", url, headers=default_headers, data=payload)
    if response.status_code != 200:
        raise Exception(f"access {url} error with post request: status code {response.status_code}")
    response_json = response.json()
    if response_json["code"] != 200:
        raise Exception(f"access {url} error with post request: status code {response_json}")
    
    return response_json

@mcp.tool()
def get_models_information(area: str) -> str:
    """
        Get models information. You can use this function to get models information list.
        each line have information about model name, market name, series name and go to market time, seperated by ;
        model name format is like PKP110 and so on.
        market name format is like A5 Pro, A5 活力版 and so on.
        series name format is like A系列 and so on.
        go to market time format is like 2023-10-01 format.
        You can use this function to do the following tasks:
            given a model name, you can find the market name, series name and go to market time in the response.
            given a market name, you can find the model name, series name and go to market time in the response.
            given a series name, you can find all model names, market names and go to market time under this series in the response.
            given a market name , such as A5, you can find a last year model name, for example A3; you can find a next year model name, for example A6.
            given a market name , such as A5 活力版, you can find a last year model name , for example A3 活力版; you can find a next year model name, for example A6 活力版.
        Args:
            area: which area to query. 'zh' for china, 'yd' for india, 'dny' for southeast asia, 'om' for europe. don't accept other area code
        Returns:
            str: List of models information, seperated by lines. each line is a string of the format: model name; market name; series name; go to market time
    """
    if area == "zh":
        url = "https://eap.oppoer.me/stage-api/indexBoard/getModelOta2"
    elif area == "yd":
        url = "https://eap-in.oppoer.me/stage-api/indexBoard/getModelOta2"
    elif area == "dny":
        url = "https://eap-sg.oppoer.me/stage-api/indexBoard/getModelOta2"
    else:
        raise Exception(f"Error: area code {area} is not supported, please use 'zh', 'yd', 'dny'")

    data = {
        "gifOta": False,
        "models":[],
        "userNum": USERNAME,
        "isAdmin":0
    }

    response_json = post(area, url, headers={}, data=data)
    response_data =  response_json["data"]

    merged_data = []
    for series in response_data.values():
        for item in series:
            merged_item = {
                "model": item["model"],
                "marketName": item["marketName"],
                "series": item["series"],
                "marketTime": item["marketTime"]
            }
            merged_data.append(merged_item)
    
    return_data = []
    for series in response_data.values():
        for item in series:
            merged_item = f"{item['model']}; {item['marketName']}; {item['series']}; {item['marketTime']}"
            return_data.append(merged_item)

    return "\n".join(return_data)

@mcp.tool()
def get_ota_version_list_by_model_name(area: str, model_name: str) -> str:
    """
        Get OTA version list by model name. You can use this function to get OTA version list by model name.
        Args:
            area: which area to query. 'zh' for china, 'yd' for india, 'dny' for southeast asia. don't accept other area code
            model_name: model name, such as PKP110 and so on.
        Returns:
            str: List of OTA version, seperated by lines. each line is a string of the format: otaVersion; versionDate; number of users in this ota version
    """
    if area == "zh":
        url = "https://eap.oppoer.me/stage-api/pbi/getOtaVersionByModels"
    elif area == "yd":
        url = "https://eap-in.oppoer.me/stage-api/pbi/getOtaVersionByModels"
    elif area == "dny":
        url = "https://eap-sg.oppoer.me/stage-api/pbi/getOtaVersionByModels"
    else:
        raise Exception(f"Error: area code {area} is not supported, please use 'zh', 'yd', 'dny'")

    data = {
            "models":[ model_name ],
            "isPre": None,
            "sort":1
        }

    response_json = post(area, url, data=data)
    version_list = response_json["data"][0]["otaConditionVos"]

    return_data = []
    for version in version_list:
        return_data.append(f"{version['otaVersion']}; {version['versionDate']}; {version['uv']}")

    return "\n".join(return_data)

@mcp.tool()
def today() -> str:
    """
        Get today's date and time. You can use this function to get today's date and time.
        Returns:
            str: Today's date and time in the format of YYYY-MM-DD
    """
    from datetime import datetime
    today = datetime.today().strftime('%Y-%m-%d')
    return today

@mcp.tool()
def get_crash_or_anr_trend(
        area: str,
        exceptionType: int,
        model: str,
        otaVersion: str,
        applicationType: int,
        startDate: str,
        endDate: str,
        dataType: int,
        queryType: int,
        foregroundType: int,
        availableRate: str
    ) -> str:
    """
        Query crash or ANR trend.
        Args:
            exceptionType: 0 for crash, 1 for ANR
            model: model name, such as PKP110 and so on. don't accept market name.
            otaVersion: OTA version, such as PKP110_11_A.11.1.1.1_2023-10-01. "" for querying all OTA versions.
            applicationType: 1 for system application, 2 for third party application, 3 for all application.
            startDate: start date of data range, format must be YYYY-MM-DD. such as 2023-10-01.
            endDate: end date of data range, format must be YYYY-MM-DD. such as 2023-10-30. you should put today's date here.
            dataType: 0 for error times, 1 for error affected users, 2 for error rate(error times/application launch times), 3 for error affected users rate(error affected users/total users).
            queryType: 1 for quering by model, 2 for query by model and otaVersion.
            foregroundType: 1 for foreground, 2 for background, 3 for all.
            availableRate: query for specified storage usage rate."" for all or "0~10%", "10%~25%", "25%~50%", "50%~100%".
        Returns:
            str: List of crash or ANR trend, seperated by lines. each line is a string of the format: date; error times / affected users/error rate/ affected users rate
    """
    if area == "zh":
        url = "https://eap.oppoer.me/stage-api/sys/available/overview/crashanr/trend"
    elif area == "yd":
        url = "https://eap-in.oppoer.me/stage-api/sys/available/overview/crashanr/trend"
    elif area == "dny":
        url = "https://eap-sg.oppoer.me/stage-api/sys/available/overview/crashanr/trend"
    else:
        raise Exception(f"Error: area code {area} is not supported, please use 'zh', 'yd', 'dny'")

    # set ota_version list
    if otaVersion or otaVersion.strip() != "":
        otaVerList = [otaVersion]
    else:
        otaVerList = []

    data = {
        "excepType": exceptionType,
        "models": [
            {
                "model": model.strip(),
                "otaVerList": otaVerList
            }
        ],
        "self": applicationType,
        "dateType": 8,
        "startDate": startDate,
        "endDate": endDate,
        "order": "asc",
        "dataType": dataType,
        "systemType": queryType,
        "foreGround": foregroundType,
        "download": 2,
        "isTotal": 0,
        "memoryDeviceVersionList": [],
        "storageDeviceVersionList": [],
        "storageSizeList": []
    }

    if availableRate or availableRate.strip() != "":
        data["availableRateList"] = [ availableRate ]
    else:
        data["availableRateList"] = []

    response_json = post(area, url, data=data)
    response_data = response_json["data"]
    data = response_data["yAxisData"][0]
    datetime = response_data["xAxisData"]
    
    return_data = []
    for i in range(len(datetime)):
        return_data.append(f"{datetime[i]}; {data[i]}")
    
    return "\n".join(return_data)

@mcp.tool()
def get_active_users_trend(
        area:str,
        model:str,
        startDate:str ,
        endDate:str,
        otaVersion:str = ''
    ) -> str:
    """
        Query active users trend.
        Args:
            area: which area to query. 'zh' for china, 'yd' for india, 'dny' for southeast asia. don't accept other area code
            model_name: model name, such as PKP110 and so on. don't accept market name
            startDate: start date, format must be YYYY-MM-DD. such as 2023-10-01
            endDate: end date, format must be YYYY-MM-DD. such as 2023-10-30
            otaVersion: OTA version, such as PKP110_11_A.11.1.1.1_2023-10-01. if not specified, it will query all OTA versions
        Returns:
            str: List of active users trend, seperated by lines. each line is a string of the format: date; active users
    """

    # set url
    if area == "zh":
        url = "https://eap.oppoer.me/stage-api/sys/performance/analyse/standby/getActiveTrend"
    elif area == "yd":
        url = "https://eap-in.oppoer.me/stage-api/sys/performance/analyse/standby/getActiveTrend"
    elif area == "dny":
        url = "https://eap-sg.oppoer.me/stage-api/sys/performance/analyse/standby/getActiveTrend"
    else:
        raise Exception(f"Error: area code {area} is not supported, please use 'zh', 'yd', 'dny'")

    # set ota_version list
    if otaVersion or otaVersion.strip() != "":
        ota_version_list = [otaVersion]
    else:
        ota_version_list = []

    data = {
        "excepType": 0,
        "models": [
            {
                "model": model,
                "otaVerList": ota_version_list
            }
        ],
        "self": 3,  # 3 查询所有， 1 表示自研， 2 表示非自研
        "dateType": 8,
        "startDate": startDate,
        "endDate": endDate,
        "order": "asc",
        "dataType": 4,
        "systemType": 1,
        "download": 2,
        "isTotal": 0,
        "memoryDeviceVersionList": [],
        "storageDeviceVersionList": [],
        "storageSizeList": [],
        "availableRateList": [],
        "isCrashRestartTotal": 1
    }

    print(data)

    response_json = post(area, url, data=data)
    response_data = response_json["data"]
    activie_users = response_data["yAxisData"][0]
    datetime = response_data["xAxisData"]
    

    return_data = []
    for i in range(len(datetime)):
        return_data.append(f"{datetime[i]}; {activie_users[i]}")
    
    return "\n".join(return_data)

@mcp.prompt()
def analyze_crash_or_anr_prompt(model: str, type: str) -> str:
    """
        Prompt for analyzing crash or ANR.
        Args:
            model: model name, such as PKP110 or Market name, such as A5 Pro and so on.
            type: crash or anr
        Returns:
            str: Prompt for analyzing crash or ANR.
    """
    return """
        Role:
            You are a data analyst. You are responsible for analyzing {type} data for user
        Task:
            Given a model name: {model}, you need to analyze {type} data for this model. You need to analyze the data and give a report.
        Setup:
            If user gvies a market name, you need to find the model name first, and then analyze the {type} data for this model.
            Before you analyze the {type} data, you should figure out the datetime of today
        Details:
            1. You should analyze foreground and background {type} data separately.
            2. You should look at {type} times data for the last month, and use regression analysis to find if there is a anomaly in the trend
            3. You should look at {type} affected users data for the last month, and use regression analysis to find if there is a anomaly in the trend
            4. You should look at {type} rate data for the last month, and use regression analysis to find if there is a anomaly in the trend
            5. You should look at {type} affected users rate data for the last month, and use regression analysis to find if there is a anomaly in the trend
    """

def main():

    # parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="FastMCP")
    parser.add_argument("--username", type=str, required=True, help="Username")
    parser.add_argument("--password", type=str, required=True, help="Password")
    args = parser.parse_args()

    # # save username and password to global variables
    global USERNAME
    global PASSWORD
    USERNAME = args.username
    PASSWORD = args.password


    # start the server by STDIO mode
    mcp.run(transport="stdio")

if __name__ == "__main__":
   
    main()