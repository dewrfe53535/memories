import requests
import json
import platform
import os


def getaid():
    url = 'http://interface.bilibili.com/offsite_loader?cid='
    scid = int(input("请输入开始cid:"))
    aid = int(input("请输入你想找到cid的视频的aid:"))
    check = input("是否启用连续模式？Y/N(默认Y):")
    f = -3
    while f != 0:
        cc = requests.session()
        r = cc.head(url + str(scid))
        rh = r.headers  # aid在header里
        if str(aid) in str(rh):  # 写文件
            print("成功:aid:%s,cid:%s" % (aid, scid))
            filetext = open('cidtoaid.txt', 'a+')
            filetext.write('aid:%s,cid:%s\n' % (aid, scid))
            filetext.close()
            scid += 1
            if check == 'N':
                break
        elif r.status_code == 404:
            f += 1
            scid += 1
        else:
            scid += 1

    else:
        print("多次404 ，可能当前存在视频都扫描完了")


def findplayurl(onekeylist, title=None, cid=None):
    if onekeylist == 1:
        cid = str(input("请输入开始cid"))
    url = 'http://vs%s.acg.tv/vg%s/%s/%s/%s/%s-1.mp4'
    cidt = []
    cidt.extend(cid)  # 将数字切割存入列表 取前2位和第3,4位
    urls = []
    forok = 0
    while forok != 3:
        if forok == 0:
            start = 401
            end = 413
        elif forok == 1:
            start = 301
            end = 359
        elif forok == 2:
            start = 701
            end = 707
        for i in range(start, end):
            for vg in range(0, 8):
                urls.append(url % (i, vg, cidt[0] + cidt[1], cidt[2] + cidt[3], cid, cid))
                # example:vs301.acg.tv/vg0/12/34/123456/123456-1-hd.mp4
        forok += 1
    for i in urls:
        cc = requests.session()
        r = cc.head(i)  # 遍历列表，判断有无
        if r.status_code == 200:
            if onekeylist == 1:
                print(i)
            else:
                print(title, '       ', i)
            break
    else:
        print("找不到视频播放链接")
