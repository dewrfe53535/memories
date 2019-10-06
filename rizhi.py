import re
import requests
import os
import time

savedir = 'K:/bilidata/1'

os.chdir(savedir)

aregpic = re.compile(r'<img.*?src="(http.*?)"')#图片正则表达式
aregjs = re.compile(r'javascript" src="(http.*?js)"')#js,大概每个空间都一样?爬了再说
aregcss = re.compile(r'link href="(http.*?css)"')#css,早期空间支持自定义css，因此需要
cookie = ''
url = 'http://member.bilibili.com/space?act=arc&arc_id=%s'
head = {'Cookie':cookie,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

  
def saveHtml(file_name, file_content):  #存网页，这段是抄的
    with open(file_name.replace('/', '_') + ".html", "wb") as f:  
        f.write(file_content)

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

req =requests.session()

if __name__ == '__main__':
    for i in range(1,10611):#再后面应该没了
        for b in range(3):
            a = req.get(url %i,headers=head,allow_redirects=False)
            if a.status_code ==200:
                break
            elif a.status_code ==503:
                time.sleep(5)
        if a.status_code ==302:
            continue
        else:
            a = a.text.replace("loli.my","hdslb.com")
        if '未知操作' not in a and '帐号已封停'not in a:#有既没有，没有既有
            os.mkdir(str(i))
            os.chdir(str(i))
            saveHtml(str(i),bytes(a,encoding='utf-8'))
            findurl = re.findall(re.compile(r'<div class="txt-box">(.*?)</div>',re.DOTALL),a)[0]
            picurl = (list(set(re.findall(aregpic,findurl))))
            jsurl = (list(set(re.findall(aregjs,a))))
            cssurl = (list(set(re.findall(aregcss,a))))
            allurl = picurl+jsurl+cssurl
            for durl in allurl:
                try:
                    for i in range(3):#重试
                        try:
                            doc = req.get(durl.replace("loli.my","hdslb.com"),timeout=20)
                            if int(doc.status_code /200) ==1:
                                break
                        except:
                            pass
                    filename = os.path.basename(durl)
                    if ".css" in filename:
                        if "loli.my" in doc.text:
                            for m in re.findall(aregpic,doc):
                                cssin = req.get(m.replace("loli.my","hdslb.com"))
                                filename2 = os.path.basename(cssin)
                                with open(validateTitle(filename2), "wb") as f:
                                    f.write(cssin.content)  # 写文件
                    with open(validateTitle(filename),"wb") as f:
                        f.write(doc.content)#写文件
                except:
                    pass
            os.chdir("..")#返回上一级
