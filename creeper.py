# !/usr/bin/env python
# coding=utf-8

'''
Creeper:
    爬虫包。
    功能: 获取网页文档和图片等资源，多线程，支持断点续传，支持数据库。
'''
'''
    类:
        Creeper:
            用于get、post并获取响应内容等。
        Creeper_imgs:
            对多个连接的内容进行下载。多线程/断点续传。
        Creeper_thread:
            多线程类。

'''
'''
    1.增加记录功能。
    2.修改requests的cookies参数
    3.尝试找到requests下载gif图片的方法
    4.增加小视频下载功能
    5.智能线程数控制
'''


import os
import requests
import urllib
import re
from StringIO import StringIO
import pickle
import traceback
import time
from PIL import Image
import threading
from Queue import Queue



# **************** Creeper *********************

class Creeper(object):
    def __init__(self,url,headers='',params='',data='',proxies='',encoding=''):
        self.url = url
        self.headers = headers
        self.params = params
        self.data = data
        self.proxies = proxies
        self.response = None
        self.html = None
        self.max_try_times = 10
        self.wait_time = 5
        self.sleep_time = 0
        self.encoding = encoding
        self.lock = None

    def get(self,url='',headers='',params='',proxies='',stream=False):
        'get方法'
        if url != '':
            self.set_url(url)
        if headers != '':
            self.set_headers(headers)
        if params != '':
            self.set_params(params)
        if proxies != '':
            self.set_proxies(proxies)
        response = self.__response('get',self.url,self.headers,self.params,self.proxies,stream)
        if response != False:
            self.response = response
            return response
        else:
            if self.lock != None:
                self.lock.acquire()
                print('[Creeper] Failed to get response. ')
                self.lock.release()
            return False

    def post(self,url='',headers='',params='',data='',proxies=''):
        if url != '':
            self.set_url(url)
        if headers != '':
            self.set_headers(headers)
        if data != '':
            self.set_data(data)
        if params != '':
            self.set_params(params)
        if proxies != '':
            self.set_proxies(proxies)
        response = self.__response('post',self.url,self.headers,self.params,self.proxies)
        if response != False:
            self.response = response
            return response
        else:
            if self.lock != None:
                self.lock.acquire()
                print('[Creeper] Failed to post. ')
                self.lock.release()
            return False

    def __response(self,work,url,headers='',params='',data='',proxies='',stream=False):
        '获取响应'
        max_try_times = self.max_try_times # 最大尝试次数
        wait_time = self.wait_time # 最大单次尝试时间
        sleep_time = self.sleep_time # 尝试失败延时
        for times in range(1,max_try_times+1):
            try:
                if work == 'get':
                    # response = requests.get(url, timeout = wait_time, headers=headers, params=params, proxies=proxies, stream=stream)
                    response = requests.get(url, timeout = wait_time, headers=headers, params=params, stream=stream)
                elif work == 'post':
                    # response = requests.post(url, timeout = wait_time, headers=headers, params=params,data=data, proxies=proxies)
                    response = requests.post(url, timeout = wait_time, headers=headers, params=params,data=data)
                break
            except:
                #traceback.print_exc()
                if times < max_try_times:
                    time.sleep(sleep_time)
                    continue
                else:
                    traceback.print_exc()
                    return False
        if self.encoding == '':
            try:
                encoding = re_find('charset=(.+?)>',response.text,report=False)
                encoding = string_removeall(encoding,['"',"'",' ','=','/'])
                self.encoding = encoding
            except:
                traceback.print_exc()
                self.encoding = 'utf-8'
            if self.encoding.lower() not in ['utf-8','utf8','gbk','gb2312']:
                self.encoding = 'utf-8'
                if self.lock != None:
                    self.lock.acquire()
                    print('[Creeper] Can not find charset, set encoding:utf-8')
                    self.lock.release()
        self.response = response
        self.response.encoding = self.encoding
        return response

    def set_url(self,url):
        if isinstance(url,str) or isinstance(url,unicode):
            self.url = url
            self.__flush()
        else:
            print('[Creeper] Url should be a string')

    def set_headers(self,headers):
        if isinstance(headers,dict):
            self.headers = headers
            self.__flush()
        else:
            print('[Creeper] Headers should be a dict')

    def set_params(self,params):
        if isinstance(params,dict):
            self.params = params
            self.__flush()
        else:
            print('[Creeper] Params should be a dict')

    def set_data(self,data):
        if isinstance(data,dict):
            self.data = data
            self.__flush()
        else:
            print('[Creeper] Data should be a dict')

    def set_proxies(self,proxies):
        if isinstance(proxies,dict):
            self.proxies = proxies
            self.__flush()
        else:
            print('[Creeper] Proxies should be a dict')

    def __flush(self):
        self.response = None
        self.html = None   

    def find(self,pattern,text=''):
        if text == '':
            text = self.html
        if isinstance(text,str)==False and isinstance(text,unicode)==False:
            print('[Creeper] Invalid Text')
            return ''
        regex = re.search(pattern, text, re.S)
        num = pattern.count('(')
        try:
            if num == 1:
                get = regex.group(1)
            else:
                get = regex.groups()
            return get.strip()
        except:
            print('[Creeper] No Found')

            return ''

    def findall(self,pattern,text=''):
        if text == '':
            text = self.html
        if len(text) < 1:
            print('[Creeper] Invalid Text')
            return ''
        get_list = re.findall(pattern, text, re.S)
        find_list = []
        for get in get_list:
            find_list.append(get.strip())
        if len(find_list) > 0:
            return find_list
        else:
            print('[Creeper] No Found')

            return ''          

    def get_html(self):
        if self.response == None:
            self.get()
            self.html = self.response.text
        elif self.html == None:
            self.html = self.response.text
        return self.html

# **************** Creepers *********************

# class Creepers(Creeper_imgs):
#     '专门用于多个链接内容的获取'
#     def __init__(self,url_list,headers='',params='',data=''):
#         super(Creepers,self).__init__(self,url_list[0],headers,params,data)
#         self.set_url_list(url_list)
#         self.lock = None
#         self.thread_list = []
#         self.thread_num = 5

#     def set_url_list(self,url_list):
#         if isinstance(url_list,list):
#             flag = True
#             for url in url_list:
#                 if not isinstance(url,str):
#                     flag = False
#             if flag == True:
#                 self.url_list = url_list

#     def thread_num(num):
#         if isinstance(num,int):
#             if 1 <= num <= 20:
#                 self.thread_num = num
#             else:
#                 print('[Creeper] Please make threads number between 1 and 20 ')
#         else:
#             print('[Creeper] threads number shoud be a integer ')

#     def __get(self,tname,lock,url='',headers='',params=''):
#         '单个线程的get方法'
#         if url != '':
#             self.set_url(url)
#         if headers != '':
#             self.set_headers(headers)
#         if params != '':
#             self.set_params(params)
#         response = self.__response('get',self.url,self.headers,self.params)
#         if response != False:
#             self.response = response
#             return response
#         else:
#             print('[Creeper] Failed to get response. ')
#             exit()

#     def getall(self,url_list='',headers='',params=''):
#         if url_list != '':
#             self.set_url_list(url_list)
#         if headers != '':
#             self.set_headers(headers)
#         if params != '':
#             self.set_params(params)
#         self.url_queue = list2queue(self.url_list)
#         self.lock = threading.Lock()
#         self.thread_list = []
#         for i in range(self.thread_num):
#             thread = MultiThread(self.__get,'t'+str(i),lock,(self.url_queue,savepath,headers))
#             thread_list.append(thread)
#             thread.start()
#         for thread in thread_list:
#             thread.join()





# **************** Creepers *********************

class Creeper_imgs(Creeper):
    '专门用于多个链接图片的下载'
    def __init__(self,url_list,dirpath='',headers='',params=''):
        super(Creeper_imgs,self).__init__(self,'',headers,params)
        self.url = None
        self.url_list = None
        self.set_url_list(url_list)
        self.dirpath = None
        if dirpath != '':
            self.set_dirpath(dirpath)
        self.done_list = []
        self.failed_dict = {}
        self.task_total = len(self.url_list)
        self.lock = None
        self.thread_list = []
        self.thread_num = 10
        self.task_done = 0
        self.task_last = 0
        self.filename_list = None

    def set_url_list(self,url_list):
        if isinstance(url_list,list):
            flag = True
            for url in url_list:
                if not isinstance(url,str) and not isinstance(url, unicode):
                    flag = False
            if flag == True:
                self.url_list = url_list
                return True
            else:
                print('[Creeper] Wrong url_list Input')
                self.url_list = None
                return False

    def set_dirpath(self,dirpath):
        if not isinstance(dirpath,str) and not isinstance(dirpath,unicode):
            print('[Creeper] Wrong dirpath Input: Not a String')
            return False
        else:
            flag = cmkdir(dirpath)
            if flag == True:
                self.dirpath = dirpath
                return True
            else:
                print('[Creeper] Wrong dirpath Input: Can Not Create Path')
                return False

    def set_filename(self,filename_list):
        if len(filename_list) == len(self.url_list):
            self.filename_list = filename_list

    def save(self,dirpath='',url_list='',headers='',params=''):
        flag = True
        if url_list != '':
            flag = self.set_url_list(url_list)
        if headers != '':
            self.set_headers(headers)
        if params != '':
            self.set_params(params)
        if dirpath != '':
            flag = self.set_dirpath(dirpath)
        elif self.dirpath == None:
            print('[Creeper] No dirpath exsits')
            flag = False
        if flag == True:
            self.__load_log()
            # deal with url_list and task_last
            url_list_checked = []
            for imgurl in self.url_list:
                if not imgurl in self.done_list:
                    url_list_checked.append(imgurl)
            self.url_list = url_list_checked
            # download th failed ones first
            self.failed_list = self.failed_dict.values()
            for url_list in (self.failed_list, self.url_list):
                list_length = len(url_list)
                self.task_total = list_length
                url_queue = list2queue(url_list)
                self.lock = threading.Lock()
                self.thread_list = []
                for i in range(self.thread_num):
                    if url_list is self.url_list:
                        thread = Creeper_thread(self.__save_thread,'thread'+'{:0>2}'.format(i),self.lock,args=(url_queue,self.dirpath,headers,params))
                    else:
                        # thread = Creeper_thread(self.__save_thread,'thread'+'{:0>2}'.format(i),self.lock,args=(url_queue,self.dirpath,headers,params),flag_failed=True)
                        thread = Creeper_thread(self.__save_thread,'thread'+'{:0>2}'.format(i),self.lock,args=(url_queue,self.dirpath,headers,params))
                    self.thread_list.append(thread)
                    thread.start()
                for thread in self.thread_list:
                    thread.join()
                print('[Creeper][%s] All Thread Exit !' % (time.asctime()[11:19]))
            print('[Creeper][%s] All Task Done !' % (time.asctime()[11:19]))

            

    def __save_thread(self,tname,lock,args,flag_failed=False):
        (url_queue,dirpath,headers,params) = args
        self.lock.acquire()
        print('[Creeper][%s][%s] Thread Start !' % (time.asctime()[11:19], tname))
        self.lock.release()
        while True:
            if url_queue.empty() == True:
                break
            imgurl = url_queue.get()
            self.lock.acquire()
            print('[Creeper][%s][%s] Getting %s ... !' % (time.asctime()[11:19], tname, imgurl))
            self.lock.release()
            self.task_last = self.task_last + 1
            self.url = imgurl
            imgext = imgurl[imgurl.rfind('.'):]
            if flag_failed == True:
                imgname = self.failed_list[imgurl]
            else:
                if self.filename_list == None:
                    imgname = format_num(self.task_last-1,len(str(self.task_total))) + imgext
                else:
                    imgname = self.filename_list[self.url_list.index(imgurl)]
            flag = self.__save_img(imgurl, dirpath, imgname, headers, params)
            self.task_done = self.task_done + 1
            if not imgurl in self.failed_list:
                self.failed_dict[imgurl] = imgname
            if flag == True:
                self.lock.acquire()
                print('[Creeper][%s][%s] Successfully saved image %s as %s (%d/%d) !' % (time.asctime()[11:19], tname, imgurl, imgname, self.task_done, self.task_total))
                self.lock.release()
                self.done_list.append(imgurl)
                if imgurl in self.failed_dict:
                    self.failed_dict.pop(imgurl)
                self.__write_log()
            if flag == False:
                self.lock.acquire()
                print('[Creeper][%s][%s] Failed saved image %s as %s (%d/%d) !' % (time.asctime()[11:19], tname, imgurl, imgname, self.task_done, self.task_total)) 
                self.lock.release()

                self.__write_log()
        self.lock.acquire()
        print('[Creeper][%s][%s] Thread Exit !' % (time.asctime()[11:19], tname))
        self.lock.release()

    def __save_img(self,imgurl,dirpath,imgname,headers='',params=''):
        '稳定高效的下载图片方法（多次尝试失败后跳过）'
        max_try_times = 10 # 最大尝试次数
        sleep_time = 0 # 尝试失败延时
        self.max_try_times = 10
        self.wait_time = 5
        self.sleep_time = 0
        imgpath = dirpath + os.sep + imgname
        # flag_gif = False
        # if imgname[-4:] == '.gif':
        #     flag_gif = True
        for times in range(1,max_try_times+1):
            # print('[%s][INFO] The %s time try begin ...' % (time.asctime()[11:19], times))
            try:
                # if flag_gif == False:
                #     print('notgif')
                response = self.get(imgurl,headers=headers,params=params,stream=True)
                if response.status_code != requests.codes.ok:
                    print('[Creeper] 404 Client Error')
                    imgurl = imgurl[:-4] + '.png'
                    response = self.get(imgurl,headers=headers,params=params,stream=True)
                img = Image.open(StringIO(response.content))
                img.save(imgpath)
                img.close()

                with open(imgpath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk: # filter out keep-alive new chunks  
                            f.write(chunk)
                            f.flush()
                    f.close() 

                # else:
                #     print('isgif')
                #     urllib.urlretrieve(imgurl,imgpath) #暂时不能反反盗链
                # print('[%s][INFO] The %s time try success!' % (time.asctime()[11:19], times))
                return True
            except:
                if times < max_try_times:
                    # print('[%s][WARN][IMG] The %s time try failed!' % (time.asctime()[11:19], times))
                    time.sleep(sleep_time)
                    continue
                else:
                    traceback.print_exc()
                    break
        return False

    def __write_log(self):
        log_dict = {
            'done_list':self.done_list,
            'failed_dict':self.failed_dict,
            'task_last':self.task_last-1
        }
        logpath = self.dirpath + os.sep + 'log.pkl'
        try:
            out_file = open(logpath, 'wb')
            pickle.dump(log_dict,out_file)
            return True
        except:
            traceback.print_exc()
            return None
        finally:
            out_file.close() 

    def __load_log(self):
        logpath = self.dirpath + os.sep + 'log.pkl'
        if os.path.exists(logpath) and os.path.isfile(logpath):
            print('[Creeper] Found Log File, Reading ...')
            try:
                in_file = open(logpath, 'rb')
            except:
                traceback.print_exc()
                return None
            dic = pickle.load(in_file)
            self.done_list = dic['done_list']
            self.failed_dict = dic['failed_dict']
            self.task_last = dic['task_last']
        else:
            print('[Creeper] Not Found Log File, Will Create a New One')
            self.done_list = []
            self.failed_dict = {}
            self.task_last = 0
            cmkdir(self.dirpath)


# **************** Creeper_thread *********************

class Creeper_thread(threading.Thread):
    '可传递参数、指定运行函数的线程类'
    def __init__(self,target,tname,lock,args):
        super(Creeper_thread,self).__init__()
        self.setDaemon(True)
        self.target = target
        self.tname = tname
        self.lock = lock
        self.args = args

    def run(self):
        self.target(self.tname,self.lock,self.args)

# **************** Single Functions *********************

# def string_removeall(string,ele):
#     if isinstance(ele,str) == True or isinstance(ele,unicode) == True:
#         while True:
#             if ele in string:
#                 string = string[:string.index(ele)] + string[string.index(ele)+len(ele):]
#             else:
#                 break
#         return string
#     elif isinstance(ele,list) or isinstance(ele,tuple):
#         for eele in ele:
#             while True:
#                 if eele in string:
#                     string = string[:string.index(eele)] + string[string.index(eele)+len(eele):]
#                 else:
#                     break
#         return string

def string_removeall(string,ele):
    if isinstance(ele,str) == True or isinstance(ele,unicode) == True:
        return string.replace(ele,'')
    elif isinstance(ele,list) or isinstance(ele,tuple):
        for eele in ele:
            string = string.replace(eele,'')
        return string


def list_remove(alist,ele):
    try:
        alist.remove(ele)
        return True
    except:
        return False

def format_num(num,length):
    string = str(num)
    for i in range(length-len(string)):
        string = '0' + string
    return string

def cmkdir(path):
        try:
            if(os.path.exists(path)==False or os.path.isdir(path)==False):
                os.mkdir(path)
        except:
            traceback.print_exc()
            return False
        return True

def re_search(pattern, text):
    if len(text) < 1:
        print('[Creeper] Invalid Text')
        return ''
    regex = re.search(pattern, text, re.S)
    try:
        get = regex.group(1).strip()
        return get
    except:
        print('[Creeper] No Search')
        return ''

def list2queue(alist):
    queue = Queue()
    for ele in alist:
        queue.put(ele)
    return queue

re_digits = re.compile(r'(\d+)')  
  
def emb_numbers(s):  
    pieces=re_digits.split(s)  
    pieces[1::2]=map(int,pieces[1::2])      
    return pieces  

def lsort(alist):
    return sorted(alist, key=emb_numbers)  

def save(target,dirpath='',url_list='',headers='',params=''):
    '多线程下载方法'
    flag = True
    if url_list != '':
        flag = self.set_url_list(url_list)
    if headers != '':
        self.set_headers(headers)
    if params != '':
        self.set_params(params)
    if dirpath != '':
        flag = self.set_dirpath(dirpath)
    elif self.dirpath == None:
        print('[Creeper] No dirpath exsits')
        flag = False
    if flag == True:
        self.__load_log()
        # deal with url_list and task_last
        url_list_checked = []
        for imgurl in self.url_list:
            if not imgurl in self.done_list:
                url_list_checked.append(imgurl)
        self.url_list = url_list_checked
        # download th failed ones first
        self.failed_list = self.failed_dict.values()
        for url_list in (self.failed_list, self.url_list):
            list_length = len(url_list)
            self.task_total = list_length
            if list_length == 0:
                continue
            elif 0 < list_length <= 20:
                self.thread_num = 5
            else:
                self.thread_num = 10
            url_queue = list2queue(url_list)
            self.lock = threading.Lock()
            self.thread_list = []
            for i in range(self.thread_num):
                if url_list is self.url_list:
                    thread = Creeper_thread(target,'thread'+'{:0>2}'.format(i),self.lock,args=(url_queue,self.dirpath,headers,params))
                else:
                    thread = Creeper_thread(target,'thread'+'{:0>2}'.format(i),self.lock,args=(url_queue,self.dirpath,headers,params),flag_failed=True)
                self.thread_list.append(thread)
                thread.start()
            for thread in self.thread_list:
                thread.join()
            print('[Creeper][%s] All Thread Exit !' % (time.asctime()[11:19]))
        print('[Creeper][%s] All Task Done !' % (time.asctime()[11:19]))

def re_find(pattern,text,report=True):
    if len(text) < 1:
        print('[Creeper] Invalid Text')
        return ''
    regex = re.search(pattern, text, re.S)
    num = pattern.count('(')
    try:
        if num == 1:
            get = regex.group(1)
        else:
            get = regex.groups()
        return get.strip()
    except:
        if report == True:
            print('[Creeper] No Found')
        return ''

def re_findall(pattern,text,report=True):
    if len(text) < 1:
        print('[Creeper] Invalid Text')
        return ''
    get_list = re.findall(pattern, text, re.S)
    find_list = []
    for get in get_list:
        find_list.append(get.strip())
    if len(find_list) > 0:
        return find_list
    else:
        if report == True:
            print('[Creeper] No Found')
        return ''          

def list_remove_same(alist):
    newlist = []
    for ele in alist:
        if ele not in newlist:
            newlist.append(ele)
    return newlist

def num_format(num,total):
    bitnum = len(str(total))
    if bitnum == 1:
        return '{:0>1}'.format(num)
    elif bitnum == 2:
        return '{:0>2}'.format(num)
    elif bitnum == 3:
        return '{:0>3}'.format(num)
    elif bitnum == 4:
        return '{:0>4}'.format(num)
    elif bitnum == 5:
        return '{:0>5}'.format(num)
    elif bitnum == 6:
        return '{:0>6}'.format(num)
    elif bitnum == 7:
        return '{:0>7}'.format(num)
    elif bitnum == 8:
        return '{:0>8}'.format(num)
    elif bitnum == 9:
        return '{:0>9}'.format(num)

# ****************** testing ********************

def main():
    print num_format(12,300)

if __name__ == '__main__':
    main()

