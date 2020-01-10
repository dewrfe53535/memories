# -!- coding: utf-8 -!-
import re
import requests
import urllib.parse
import html.parser
import random

regex1 = re.compile(r'<td class="ptitle"><a title=".*?>(.*)<\/a>')
postcontent = 'method=backpu_list&type=json&page_name=%s&currentPage=1'
headers = {'Content-Type': 'application/x-www-form-urlencoded',
           'X-Requested-With': 'XMLHttpRequest',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.33 Safari/537.36'}
url1 = 'http://dvdbd.wiki.fc2.com/list/'
url2 = 'http://dvdbd.wiki.fc2.com/action/'
cookie = 'fc2cnt_7752750=1-1530010148; plistper=100; fc2_analyzer_1250300=1-1227329999-1530010149-1530065550-87-2-1530010149; FC2ANASESSION1250300=74662260; bloguid=c0bd29e7-fddd-488f-968f-d0845e7cada5; fc2cnt_7752750=1-1530010148; fclo=1530062304949%2Czh-CN%2C8; sid=usit0sshedc56hopv4p4vkd2o0; fc2_analyzer_1250300=1-1227329999-1530010149-1530065490-141-2-1530010149; FC2ANASESSION1250300=74661398'
postcontent2 = 'method=backup_preview&type=json&page=%s&date=%s'
regex2 = re.compile(r'divstyle"> ○(.*?)<br \/>')

def getrangestr(count):
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(count):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt

def convertbrowsercookiesdict(s):
    '''Covert cookies string from browser to a dict'''
    ss = s.split(';')
    outdict = {}
    for item in ss:
        i1 = item.split('=', 1)[0].strip()
        i2 = item.split('=', 1)[1].strip()
        outdict[i1] = i2
    return outdict


cvcookie = convertbrowsercookiesdict(cookie)

req = requests.session()


def getanimename():
    animename = []
    for i in range(1, 18):
        a = req.get(url1 + 'page%s/' % i, headers=headers, cookies=cvcookie).text
        b = re.findall(regex1, a)
        animename += b
    return animename

def writeerrname(errname):
    with open('name.txt','a+') as f:
        tempname = getrangestr(8)
        f.write(tempname+'      '+errname)
        return tempname

def writetodisk(name,data):
    try:
        with open(name+'.html','a+')as f:
            f.write(data)
    except:
        tm = writeerrname(name)
        with open(tm+'.html','a+')as f:
            f.write(data)

editlist = []
def getbackuplist(name):
    return req.post(url2,data=postcontent%urllib.parse.quote(name),cookies=cvcookie,headers=headers).json()

for i in getanimename():
    for j in getbackuplist(i)['itemData']:
        if '05-17' in j['backup_date'] and int(j['backup_date'][11:13]) < 8:
            a = req.post(url2,postcontent2%(urllib.parse.quote(i),j['backup_date']),headers=headers,cookies=cvcookie).json()[0]
            writetodisk(i,a)
            break