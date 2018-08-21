import re
import requests
from requests.exceptions import RequestException
from hashlib import md5
import os
from multiprocessing import Pool
from config import *
from pymongo import MongoClient


client = MongoClient(MONGO_URL,connect=False)
db = client[MONGO_DB]


def get_one_page(offset):
    url = 'http://desk.zol.com.cn/fengjing/'+str(offset)+'.html'
    try:
        response = requests.get(url)
        if response.status_code ==200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出错',url)
        return None

def parse_url_list(html):
    pattern = re.compile('<a class="pic" href="(.*?)" target="_blank"',re.S)
    results = re.findall(pattern,html)
    if results:
        for result in results:
            yield result
    else:
        print('未匹配成功')

def get_one_detail(url):
    url = 'http://desk.zol.com.cn'+url
    try:
        response = requests.get(url)
        if response.status_code ==200:
            return response.text
        return None
    except RequestException:
        print('请求详情页页出错',url)
        return None


def parse_one_detail(html):
    pattern = re.compile('<a class="pic" href="(.*?)" target="_blank"', re.S)
    results = re.findall(pattern, html)
    if results:
        for result in results:
            yield result
    else:
        print('未匹配成功')

def parse_detail_downurl(html):
    pattern = re.compile('<li class="show.*?<a href=\"(.*?)\">', re.S)
    results = re.findall(pattern, html)
    return results

def down_url(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': '你的cookise!',
        'Host': 'desk.zol.com.cn',
        'Referer': 'http://desk.zol.com.cn/bizhi/7301_90293_2.html',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    pic_id = re.search(r'/bizhi/\d+_(\d+)_\d+.html',url)
    url = 'http://desk.zol.com.cn/down/1920x1080_' + pic_id.group(1)+'.html'
    try:
        response = requests.get(url,headers=headers)
    except RequestException:
        print('状态码出错:',response.status_code)

    if response.url:
        try:
            res_pic = requests.get(response.url)
            print('download...', response.url)
            save_pic(res_pic.content)
            yield {
                'url':response.url
            }
        except RequestException:
            print('请求图片下载地址出错', url)
            return None

def save_pic(content):
    file_path ='{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

def save_to_mongo(data):
    if db[MONGO_TABLE].insert(data):
        print('Successfully Saved to MongoDB',data)
        return True
    return False


def main(offset):
    html = get_one_page(offset)
    for url in parse_url_list(html):
        details = get_one_detail(url)
        for item in parse_detail_downurl(details):
            data = down_url(item)
            save_to_mongo(data)




if __name__ == '__main__':
    pool = Pool()
    pool.map(main,[i for i in range(int(OFFSET))])
    pool.close()
    pool.join()
