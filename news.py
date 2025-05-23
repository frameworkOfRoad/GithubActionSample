import requests
from bs4 import BeautifulSoup
import os
import json
# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID即 用户列表中的微信号
openIdss = os.environ.get("OPEN_ID_S")
weather_template_id = os.environ.get("TEMPLATE_ID")
news_template_id = os.environ.get("NEWS_TEMPLATE_ID")
deep_seek_api = os.environ.get("DEEP_SEEK_API")
def get_baidu_news_top10():
    url = 'https://top.baidu.com/board?tab=realtime'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    # 判断请求是否成功
    if response.status_code == 200:
        # 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找热搜列表
        hot_list = soup.find_all('div', class_='c-single-text-ellipsis')
        print(hot_list)
        news_list = []
        # 输出前10条热搜
        for i in range(10):
            if i < len(hot_list):
                print(f"{i + 1}. {hot_list[i].text.strip()}")
                news_list.append({'title': hot_list[i].text.strip()})

            else:
                print("热搜条目不足10条")
                break
    else:
        print(f"请求失败，状态码：{response.status_code}")
    return news_list


def parse_html(self, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    hot_searches = []
    for item in soup.find_all('div', class_=self.all_content_class):
        title = self.title_pattern.search(str(item))
        introduction = self.introduction_pattern.search(str(item))
        index = self.index_pattern.search(str(item))
        if title and introduction and index:
            hot_searches.append({
                'title': title.group(1),
                'introduction': introduction.group(1),
                'index': index.group(1)
            })
    return hot_searches

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
    ii = 1
    for news in top10_news:
        segmentss =split_text(get_news_summary(news.get("title")))
        print(segmentss)
        while len(segmentss) < 5:
            segmentss.append("")
        body = {
            "touser": openId.strip(),
            "template_id": news_template_id.strip(),
            "url": "https://weixin.qq.com",
            "data": {
                "date": {
                    "value": now_str
                },
                "top": {
                    "value": ii
                },
                "title": {
                    "value": news.get("title")
                },
                "content1": {
                    "value": segmentss[0]
                },
                "content2": {
                    "value": segmentss[1]
                },
                "content3": {
                    "value": segmentss[2]
                },
                "content4": {
                    "value": segmentss[3]
                },
                "content5": {
                    "value": segmentss[4]
                }
            }
        }
        ii=ii+1
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
        print(requests.post(url, json.dumps(body)).text)


def get_news_summary(news_link):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer "+deep_seek_api,
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "针对这个标题【"+news_link+"】搜索相关的新闻，按照犀利的语言简述内容，完整的一句话，不需要分割，字数要求50字左右，"}]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']


def split_text(text, max_length=19):
    """
    将文本分割成每段不超过指定长度的数组。
    :param text: 要分割的文本
    :param max_length: 每段的最大长度
    :return: 分割后的文本数组
    """
    if len(text) <= max_length:
        return [text]

    segments = []
    start = 0
    while start < len(text):
        end = start + max_length
        segment = text[start:end]
        segments.append(segment)
        start = end

    return segments


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
