# coding=u8

"功能"
'''
获取新浪微博用户相册照片到本地
'''

"使用方法"
'''
1.填写储存目录
2.指定微博用户id
3.填写cookie
4.运行
'''

# ---------------------------------------------------------------|| 初始参数 ||----------------------------------------------------------------------
dirpath = r'images' #储存目录
uid = '1005052495158140' #用户id
cookie = 'SINAGLOBAL=7096614666686.993.1478933549913; SCF=As9EXPnkiArRA4WnZDDqKwxMqDuhByIuF7xOWaFyllSVBrRIucqvH7G019xOOW-DvOwyS980Z-qhDhvjQ5KADjM.; SUHB=0C1CIC7sshc16C; ALF=1511684170; SUB=_2AkMvZk4nf8NhqwJRmP4VxGjkaoR1yw_EieLBAH7sJRMxHRl-yT83qm4ytRBGWF_rq7FhGYThrYAZmIqeJ6jpng..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFToROOH4BacWGBOsPOl71T; _s_tentry=auto.ifeng.com; Apache=1350895953090.9514.1481955434953; ULV=1481955434972:11:2:1:1350895953090.9514.1481955434953:1481022799070; YF-Page-G0=734c07cbfd1a4edf254d8b9173a162eb; UOR=,,www.baidu.com' #cookie

# 说明：
#   1.uid可在页面html文档中搜索"oid"，获取其值
#   2.cookies可在登录新浪微博后观测浏览器记录的cookies信息获得

import os
import requests
import urllib
import re
import pickle
import traceback
import time
from PIL import Image
from StringIO import StringIO
import creeper

# global
total_num = 0

def list_find(alist,ele):
    try:
        return alist.index(ele)
    except:
        return -1

def get_response(url,cookies='',headers='',params='', stream=False, mtt=20, wt=2, st=0.25):
    '稳定高效的获取响应方法'
    max_try_times = mtt # 最大尝试次数
    wait_time = wt # 最大单次尝试时间
    sleep_time = st # 尝试失败延时
    #print('[%s][INFO] Start trying to connect ...' % time.asctime()[11:19])
    for times in range(1,max_try_times+1):
        # print('[%s][INFO] The %s time try begin ...' % (time.asctime()[11:19], times))
        try:
            response = requests.get(url, timeout=wait_time, cookies=cookies, headers=headers, params=params, stream=stream)
            # print('[%s][INFO] The %s time try success!' % (time.asctime()[11:19], times))
            break
        except:
            #traceback.print_exc()
            if times < max_try_times:
                # print('[%s][WARN] The %s time try failed!' % (time.asctime()[11:19], times))
                time.sleep(sleep_time)
                continue
            else:
                print('[%s][ERROR] The last try failed at last , exit pro ...' % time.asctime()[11:19])
                traceback.print_exc()
                exit()
    # print('[%s][INFO] Successfully get the response!' % time.asctime()[11:19])
    response.encoding = 'u8'
    return response



def retrieve(imgurl,imgpath):
    '稳定高效的下载图片方法（多次尝试失败后跳过）'
    max_try_times = 5 # 最大尝试次数
    wait_time = 15 # 最大单次尝试时间
    sleep_time = 3 # 尝试失败延时
    import socket
    socket.setdefaulttimeout(wait_time)
    #print('[%s][INFO] Start trying to connect ...' % time.asctime()[11:19])
    for times in range(1,max_try_times+1):
        # print('[%s][INFO] The %s time try begin ...' % (time.asctime()[11:19], times))
        try:
            urllib.urlretrieve(imgurl,imgpath)
            # print('[%s][INFO] The %s time try success!' % (time.asctime()[11:19], times))
            return True
        except:
            if times < max_try_times:
                # print('[%s][WARN] The %s time try failed!' % (time.asctime()[11:19], times))
                time.sleep(sleep_time)
                continue
            else:
                print('[%s][ERROR] The last try failed at last , pass ...' % time.asctime()[11:19])
                break
    return False
    # print('[%s][INFO] Successfully get the response!' % time.asctime()[11:19])

def save_img2(imgurl, imgpath, headers='', params=''):
    '稳定高效的下载图片方法（多次尝试失败后跳过）'
    max_try_times = 10 # 最大尝试次数
    sleep_time = 0 # 尝试失败延时
    print('[%s][INFO] Start trying to download ...' % time.asctime()[11:19])
    for times in range(1,max_try_times+1):
        # print('[%s][INFO] The %s time try begin ...' % (time.asctime()[11:19], times))
        try:
            # __save_img2(imgurl, dirpath, imgname, headers, params)
            response = get_response(imgurl, headers=headers,params=params, stream=False, mtt=10, wt=15, st=2)
            img = Image.open(StringIO(response.content))
            img.save(imgpath)
            img.close()
            # print('[%s][INFO] The %s time try success!' % (time.asctime()[11:19], times))
            return True
        except:
            traceback.print_exc()
            if times < max_try_times:
                print('[%s][WARN][IMG] The %s time try failed!' % (time.asctime()[11:19], times))
                time.sleep(sleep_time)
                continue
            else:
                print('[%s][ERROR] The last try failed at last , pass ...' % time.asctime()[11:19])
                break
    return False

def save_img(imgurl,savepath,imgname):
    '向本地目录储存图像'
    imgext = imgurl[-4:]
    imgname = imgname + imgext 
    flag = retrieve(imgurl,savepath+os.sep+imgname)
    if flag == True:
        return True
    else:
        return False


def secp(string,pattern1,pattern2=''):
    '替换字符串中所有指定字符串为新字符串(效率低)'
    while True:
        index = string.find(pattern1)
        if index > -1:
            string = string[:index]+pattern2+string[index+len(pattern1):]
        else:
            break
    return string 

def url_deal(url):
    'URL处理'
    urld = secp(url,'\\')
    urld = secp(urld,'thumb300','large')
    return urld

def get_imgurl(html):
    '解析html，获取图像url列表'
    imgurl_list = []
    extlist = ['jpg','gif','png']
    for ext in extlist:
        pattern = r'class=\\\"photo_pict\\\" src=\\\"(http:\S+thumb300\S+.'+ext+')'
        result = re.findall(pattern,html,re.S)
        if len(result) > 0:
            for url in result:
                imgurl_list.append(url_deal(url))    
    return imgurl_list   



def save_log(dic, path):
    '以pickle文件格式储存到目标路径'
    try:
        out_file = open(path, 'wb')
        pickle.dump(dic,out_file)
        return path
    except:
        traceback.print_exc()
        return None
    finally:
        out_file.close()      

def load_log(path):
    '从指定文件读取pickle文件转成字典'
    try:
        in_file = open(path, 'rb')
        dic = pickle.load(in_file)
        return dic
    except:
        traceback.print_exc()
        return None

def re_search(pattern, text):
    regex = re.search(pattern, text, re.S)
    try:
        get = regex.group(1).strip()
        return get
    except:
        return ''

def main():
    creeper.cmkdir("./images")
    url1 = 'http://www.weibo.com/u/' + uid
    url2 = 'http://www.weibo.com/p/' + uid
    url3 = 'http://www.weibo.com/' + uid

    cookies = dict(cookies_are=cookie) # use cookies alone
    print('[%s][INFO] Pro starting ...' % (time.asctime()[11:19]))
    for url in (url1,url2,url3):  
        print('[%s][INFO] Start analysis at %s ...' % (time.asctime()[11:19], url))
        response = requests.get(url, cookies=cookies)
        html = response.text
        page_id = re_search("page_id']='(\d+)';",html)
        if len(page_id) > 0:
            print('[%s][INFO] Successfully get page_id %s ...' % (time.asctime()[11:19], page_id))
            break 
    url = 'http://www.weibo.com/p/'+str(page_id)+'/photos'
    '访问网址，获取html文档'
    response = get_response(url, cookies=cookies)
    response.encoding = 'u8'
    html = response.text
    '检查html是否有效；若无效，报错并中止'
    if len(re.findall('thumb300',html,re.S)) < 1 and len(re.findall('oid',html,re.S)) < 1 and len(re.findall('的微博',re.S)) < 1:
        print('[%s][ERROR] Invalid cookies or page_id, please check !' % (time.asctime()[11:19]))
        exit()
    '解析文档，获取用户信息和图片路径'
    uname = re.findall(u'content="(.+?)，',html,re.S)[0]
    imgurl_list = get_imgurl(html)
    '动态获取循环'
    while True:
        '获取since_id，进一步获取动态加载的页面'
        result = re.findall('since_id=(\S+)">',html,re.S)
        if len(result)>0:
            since_id = result[0][:-1]
        else:
            break
        #print(since_id)
        payload={
            'since_id': since_id,
            'page_id': page_id,
            'ajax_call': 1
        }
        url = 'http://weibo.com/p/aj/album/loading'
        while True:
            response = get_response(url,params=payload,cookies=cookies)
            if response.url != 'http://weibo.com/sorry?sysbusy':
                break
        html = response.text
        print('[%s][INFO] Got new page of %s !' % (time.asctime()[11:19], response.url))
        '解析文档，获取html路径'
        imgurl_list = imgurl_list + get_imgurl(html)
    #pprint(imgurl_list)
    savepath = dirpath + os.sep + uname
    print('[%s][INFO] Got savepath %s !' % (time.asctime()[11:19], savepath))
    if(os.path.exists(savepath)==False or os.path.isdir(savepath)==False):
        os.mkdir(savepath)
    imgurl_list.reverse()
    global total_num
    total_num = len(imgurl_list)
    print('[%s][INFO] Got all images, total %d !' % (time.asctime()[11:19], len(imgurl_list)))

    cp = creeper.Creeper_imgs(imgurl_list)
    cp.save(savepath)

if __name__ == '__main__':
    main()

