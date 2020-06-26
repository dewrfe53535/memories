# -*- coding: UTF-8 -*-
import configparser
import pyautogui
import cv2
import time
import winsound
import playsound
import random
import numpy
import win32gui
import win32con
import wmi
import tkinter
import multiprocessing
import os
import win32file
import struct
import requests
import re
from datetime import datetime
from multiprocessing import Process


def pptjsparser(data):
    imgre = r'<img id=\".*?\" src="(.*?)"'
    txtre = r'<span id.*?>(.*?)<\/span>'
    return re.findall(imgre, data), re.findall(txtre, data)


class classin:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf8')
        self.lessontime = self._getdaylesson()

    def _getdaylesson(self):
        daobj = datetime.now()

        if str(daobj.weekday() + 1) in self.config['outclass']['L2'].split(','):
            return self._Parsetime(self.config['outclass']['Lessiontime2'].split(","))  # 个别日期使用lesson2课表
        else:
            return self._Parsetime(self.config['outclass']['Lessontime'].split(","))

    def _Parsetime(self, timelist):
        leslist = timelist
        now_time = int(time.time())
        day_time = int(time.mktime(datetime.now().date().timetuple()))
        leslist2 = [day_time + int(i.split(':')[0]) * 3600 + int(i.split(':')[1]) * 60 for i in leslist]
        return leslist2

    def Playsound(self, time=10):
        '''

        :param time: 播放的时间，当config中为system时无效
        :param mode: 0为系统，1为自定义音频
        :return:
        '''
        if self.config['misc']['sound'] == 'system':
            winsound.Beep(random.randint(100, 10000), time * 1000)
        else:
            playsound.playsound(self.config['misc']['sound'])

    def _Takescreenshot(self):
        image = pyautogui.screenshot()
        img = cv2.cvtColor(numpy.asarray(image), cv2.COLOR_RGB2BGR)
        return img

    def Comparepicture(self, img1, img2, threshold=0.8):
        '''

        :param img1: opencv image
        :param img2:
        :param threshold:
        :return: cooperate of image
        '''
        img_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray, img2, cv2.TM_CCOEFF_NORMED)
        loc = numpy.where(res >= threshold)
        return list(zip(*loc[::-1]))

    def Autoclicklesson(self):
        for i in self.lessontime:
            if int(time.time()) > i - 120 and int(time.time()) < i + 160:
                daobj = datetime.now()
                autoconfig = self.config['outclass']['AutoEnter%s' % daobj.isoweekday()].split(',')
                if autoconfig[self.lessontime.index(i)] == '1':
                    win32gui.ShowWindow(win32gui.FindWindow(0, 'classin'), win32con.SW_MAXIMIZE)
                    loc = self.Comparepicture(self._Takescreenshot(), cv2.imread("button1.png", 0))
                    if loc == []:
                        return False
                    pyautogui.click(loc[0][0] + 5, loc[0][1] + 5)
                    return True
                else:
                    return False
        return False

    def Noticerforenterlesson(self):
        for i in self.lessontime:
            if int(time.time()) < i and i - 180 < int(time.time()):
                soundthread = Process(target=self.Playsound, args=(10000,))
                soundthread.start()
                temp1 = pyautogui.alert(text='关闭', title='上课闹钟', button='OK')
                soundthread.terminate()
                return True

        return False

    def Safesleep(self):
        Roundtime = int(self.config['inclass']['Roundtime'])
        Checktime = int(self.config['inclass']['Checktime'])
        while True:
            camera = cv2.VideoCapture(0)
            if camera.read()[0] == False:
                camera.release()
                cv2.destroyAllWindows()
                self.Playsound(10)
                os.system('cls')
                time.sleep(Roundtime)
            else:
                camera.release()
                cv2.destroyAllWindows()
                time.sleep(Checktime)

    def Findclassroomhandle(self):
        hWndList = []
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList)  # 获取所有窗口handle
        for i in hWndList:
            if 'Classroom' in win32gui.GetWindowText(i):
                return i
        return False

    def Reloadconfig(self):
        self.config.read('config.ini', encoding='utf8')
        self.lessontime = self._getdaylesson()


    def smallclass(self):
        uid = self.Findclassroomhandle()
        if uid:
            win32gui.ShowWindow(uid, win32con.SW_MINIMIZE)
            return True
        else:
            return False

    def Init_filewatch(self):
        hDir = win32file.CreateFile(
            os.environ['LOCALAPPDATA'] + "\\ClassIn\\cache",  # os.environ['LOCALAPPDATA'] + "\\ClassIn\\cache"
            0x0001,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,
            None
        )
        return hDir

    def Fileobserver(self, hDir):
        reqheader = {'Proxy-Connection': 'keep-alive',
                     'Cache-Control': 'max-age=0',
                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.44 Safari/537.36',
                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                     'Accept-Language': 'zh-CN,zh;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5,zh-HK;q=0.4,zh-SG;q=0.3,zh-MO;q=0.2'}
        okfile = []
        results = win32file.ReadDirectoryChangesW(
            hDir,
            1024000,
            True,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            win32con.FILE_NOTIFY_CHANGE_SIZE |
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
            0x00000020 |
            0x00000040 |
            win32con.FILE_NOTIFY_CHANGE_SECURITY,
            None,
            None
        )
        for action, file in results:
            okfile.append(os.path.join(os.environ['LOCALAPPDATA'] + "\\ClassIn\\cache", file))
            # okfile.append(os.path.join('C:\\temp\\'+ "cache", file))

        okfile = list(set(okfile))
        if okfile:
            time.sleep(60)  # 避免和原程序抢缓存，让原程序加载完再读取
            savedir = self.config['misc']['savedir']
            for i in okfile:
                if '.d' not in i:
                    continue
                if 'prepared' in i:
                    continue
                try:
                    with open(i, 'rb') as f:
                        f.seek(12)
                        urllen = struct.unpack('>i', f.read(4))[0]
                        url = f.read(urllen).decode()
                except Exception as e:
                    continue
                filetype = url.split('.')[-1]
                filename = url.split('/')[-1].split('.')[0]
                if '?' in filetype:
                    filetype = filetype.split('?')[0]
                if  'slide' in url and filetype == 'js':
                    pptid = url.split('/')[-6] + url.split('/')[-5] + url.split('/')[-4]
                    filedata = requests.get(url, headers=reqheader).text
                    pptdata = pptjsparser(filedata)
                    try:
                        os.mkdir(savedir + '\\' + pptid)
                    except:
                        pass
                    with open(os.path.join(savedir + '\\' + pptid, filename + '_dump.txt'), 'w+',
                              encoding='utf-8') as f:
                        for j in pptdata[1]:
                            f.write(j + '\n')
                    for j in pptdata[0]:
                        fileendurl = j.split('/')[1]
                        urltemp1 = url.split('/')
                        newurl = ''
                        for k in urltemp1[:-1]:
                            newurl += k + '/'
                        newurl += fileendurl
                        imgdata = requests.get(newurl, headers=reqheader).content
                        with open(os.path.join(savedir + '\\' + pptid, fileendurl), 'wb') as f:
                            f.write(imgdata)

                elif filetype == 'pdf':
                    filedata = requests.get(url, headers=reqheader).content
                    with open(os.path.join(savedir, filename + '.pdf'), 'wb') as f:
                        f.write(filedata)

                else:
                    continue
            return True
        else:
            return False


def noticerplus(classinobject, sleeptime, return_dict):
    while True:
        now = classinobject.Noticerforenterlesson()
        if now == True:
            return_dict[0] = True
            return
        time.sleep(sleeptime)


def observerplus(classinobject, sleeptime):
    hdir = classinobject.Init_filewatch()
    while True:
        classinobject.Fileobserver(hdir)
        time.sleep(sleeptime)


def tkclose(a):
    windowtop = tkinter.Tk()
    windowtop.title("***请勿手滑关闭***")
    windowtop.geometry('500x300')
    windowtop.wm_attributes('-topmost', 1)
    noticetext = tkinter.Label(windowtop, text="用于切换为最小化窗口，请确保程序有管理员权限", width=40, height=2)
    notice2text = tkinter.Label(windowtop, text="请最小化本窗口，并在需要使用时用win+tab切换", width=40, height=2)
    smallclass = tkinter.Button(windowtop, text="使classin最小化", command=a.smallclass)
    noticetext.pack()
    notice2text.pack()
    smallclass.pack()
    windowtop.mainloop()


def main():
    print("Classout v1.1  start")
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    a = classin()
    hdir = a.Init_filewatch()
    if a.config.getboolean('misc', 'savefile') == True:
        watchThread = Process(target=observerplus, args=(a, int(a.config['outclass']['Checktime'])))
        watchThread.start()
    print('请正确配置完config.ini再运行本程序!')
    sleepproc = Process(target=a.Safesleep, args=())
    closeproc = Process(target=tkclose, args=(a,))
    noticeproc = Process(target=noticerplus, args=(a, int(a.config['outclass']['Checktime']), return_dict))
    outclassnoticed = 0
    inclassnoticed = 0
    noticenoticed = 0
    return_dict[0] = 0
    while True:
        islesson = a.Findclassroomhandle()
        if islesson:
            if not inclassnoticed:
                print("检测到classroom窗口,进入上课模式")
                if noticeproc.is_alive():
                    noticeproc.terminate()
                if a.config.getboolean('inclass', 'Notice'):
                    sleepproc = Process(target=a.Safesleep, args=())
                    sleepproc.start()
                closeproc = Process(target=tkclose, args=(a,))
                closeproc.start()
                inclassnoticed = 1
                outclassnoticed = 0
                noticenoticed = 0
                return_dict[0] = 0
        if not islesson:
            if not outclassnoticed:
                print("检测到已退出classroom,进入下课模式")
                if sleepproc.is_alive():
                    sleepproc.terminate()
                if closeproc.is_alive():
                    closeproc.terminate()
                outclassnoticed = 1
                inclassnoticed = 0
            a.Autoclicklesson()
            if return_dict[0] == True:
                noticenoticed = 1
            if not noticenoticed and not noticeproc.is_alive() and a.config.getboolean('outclass', 'Notice'):
                noticeproc = Process(target=noticerplus, args=(a, int(a.config['outclass']['Checktime']), return_dict))
                noticeproc.start()
        time.sleep(int(a.config['outclass']['Checktime']))


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
    b = classin()
