import re
import requests
import json
import io
from multiprocessing.dummy import Pool as ThreadPool

def gettext(text3):
    try:
        text4 = re.findall('[0-9A-Z]{16}',str(text3))
        print(text4)
        return text4
    except Exception as e:
        print("正则匹配出错",e)

def writeToTxt(list_name,file_path):
    try:
        fp = open(file_path,"a+")
        for item in list_name:
            fp.write(str(item)+"\n")
        fp.close()
    except IOError:
        print("fail to open file")

def test(url):
    success=False
    while success == False:
        try:
            text1 = requests.get(url)
            text2 = text1.text
            text3 = json.loads(text2)
            text4 = gettext(text3)
            writeToTxt(text4,"code1.txt")
            print("成功")
            success = True
        except:
            print("网络爆炸?")

urls= []
pg = 1
while pg <372:
    url = 'http://api.bilibili.com/feedback?mode=arc&type=jsonp&ver=3&aid=2610147&page='
    url = url + str(pg)
    urls.append(url)
    pg =pg + 1

pool = ThreadPool(30)
results = pool.map(test, urls)
