import requests
from bs4 import BeautifulSoup
import os
import json
# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID即 用户列表中的微信号
openId = os.environ.get("OPEN_ID")
openIdss = os.environ.get("OPEN_ID_S")
weather_template_id = os.environ.get("TEMPLATE_ID")
news_template_id = os.environ.get("NEWS_TEMPLATE_ID")

def get_baidu_news_top10():
    # 构造请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    url = 'https://news.baidu.com/'
    response = requests.get(url, headers=headers)

    # 检查响应状态
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"Failed to retrieve data, status code: {response.status_code}")
        return []

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取新闻信息
    news_list = []
    hotnews = soup.find('div', class_='hotnews')
    if hotnews:
        news_items = hotnews.find_all('a')
        for item in news_items[:10]:  # 获取前10条新闻
            title = item.get_text()
            link = item['href']
            news_list.append({'title': title, 'link': link})

    return news_list

def get_access_token():
    # 获取access token的url
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token


def send_news(access_token, top10_news,openId):
    # touser 就是 openID
    # template_id 就是模板ID
    # url 就是点击模板跳转的url
    # data就按这种格式写，time和text就是之前{{time.DATA}}中的那个time，value就是你要替换DATA的值

    import datetime
    # 获取当前日期和时间
    now = datetime.datetime.now()

    # 格式化为“年月日时分秒”的格式
    now_str = now.strftime("%Y年%m月%d日 %H时%M分%S秒")
    for news in top10_news:
        i=0
        body = {
            "touser": openId.strip(),
            "template_id": news_template_id.strip(),
            "url": "https://weixin.qq.com",
            "data": {
                "date": {
                    "value": now_str
                },
                "top": {
                    "value": i+1
                },
                "title": {
                    "value": news.title
                },
                "link": {
                    "value": news.link
                }
            }
        }
        i=i
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
        print(requests.post(url, json.dumps(body)).text)


def top10_news():
    # 1.获取access_token
    access_token = get_access_token()
    top10_news_list = get_baidu_news_top10()
    print(f"新闻前10条： {top10_news_list}")
    # 3. 发送消息
    openIds = openIdss.split(",")
    for openId in openIds:
        send_news(access_token, top10_news_list,openId)

if __name__ == '__main__':
    top10_news()
