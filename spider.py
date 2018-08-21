import re
import requests
from requests.exceptions import RequestException
from hashlib import md5
import os
from multiprocessing import Pool

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
        'Cookie': 'ip_ck=1I2t1I+yv8EuMDAxMTM4LjE1MjYwMTY2MzE%3D; gr_user_id=b7cb853b-f464-4d8a-963a-4206324efaa9; BDTUJIAID=30d8dd56e6057f674addec6d812c0cb4; z_pro_city=s_provice%3Djuyuwang%26s_city%3Dnull; userProvinceId=1; userCityId=0; userLocationId=1; vjuids=334da4b4b.16545ca76b9.0.2409f62a24506; vjlast=1534474221.1534474221.30; z_day=izol102715%3D10%26izol102591%3D10%26izol102612%3D10%26izol102569%3D10%26ixgo20%3D1; Hm_lvt_ae5edc2bc4fc71370807f6187f0a2dd0=1532395707,1533520394,1534148960,1534476503; lv=1534489949; vn=15; afpCT=1; ecaaedbddccbe3bbddbb7a09beef3e3c=31o4u6h1u41s3amg%7B%7BZ%7D%7D%25E4%25B8%258B%25E8%25BD%25BD%25E5%25A3%2581%25E7%25BA%25B8%7B%7BZ%7D%7Dnull; MyZClick_ecaaedbddccbe3bbddbb7a09beef3e3c=/html/body/div%5B4%5D/ul/li%5B3%5D/a/; Adshow=4; Hm_lpvt_ae5edc2bc4fc71370807f6187f0a2dd0=1534493615; questionnaire_pv=1534464096; 99cd60e1415abb11414c07f08ef299ab=2fk4u6h1u34k39lg%7B%7BZ%7D%7D%25E4%25B8%258B%25E8%25BD%25BD%25E5%25A3%2581%25E7%25BA%25B8%7B%7BZ%7D%7Dnull; 3e9d46f7388b2f408b80f362cccd910a=2fk4u6h1u34k39lg%7B%7BZ%7D%7D%25E4%25B8%258B%25E8%25BD%25BD%25E5%25A3%2581%25E7%25BA%25B8%7B%7BZ%7D%7Dnull; MyZClick_99cd60e1415abb11414c07f08ef299ab=/html/body/div%5B4%5D/ul/li%5B3%5D/a/; MyZClick_3e9d46f7388b2f408b80f362cccd910a=/html/body/div%5B4%5D/ul/li%5B3%5D/a/',
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
    print('download...',response.url)
    if response.url:
        try:
            res_pic = requests.get(response.url)
            save_pic(res_pic.content)
        except RequestException:
            print('请求图片下载地址出错', url)
            return None

def save_pic(content):
    file_path ='{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    html = get_one_page(offset)
    for url in parse_url_list(html):
        details = get_one_detail(url)
        for item in parse_detail_downurl(details):
            down_url(item)



if __name__ == '__main__':
    pool = Pool()
    pool.map(main,[i for i in range(1)])
