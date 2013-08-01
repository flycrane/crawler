#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from webscraping import xpath
import hashlib
import re
import urllib2
import util

#Init logger
logger = util.initlog('finder.log')

def process_ruanjian_url(url):
    try:
        # http://a.3533.com/ruanjian/4180.htm
        # charset=utf-8
        print url
        data = urllib2.urlopen(url).read()        
        down_obj = util.app_info({'market':market})
        down_obj['app_url'] = url
        down_obj['app_url_md5'] = hashlib.md5(url).hexdigest()
        
        app_name = xpath.search(data, '//div[@class="gametit"]/h1/')
        if(app_name):
            down_obj['app_name'] = app_name[0]
        
        apk_left = xpath.search(data, '//div[@class="apkleft"]/ul/li')
        if(apk_left):
            found1 = re.search('([.\d]+)', apk_left[0])
            if(found1):
                down_obj['version'] = found1.group(1)
            
            found2 = re.search('([.\d]+)([MK])', apk_left[4])
            if(found2):
                if(found2.group(2) == 'M'):
                    down_obj['size'] = int(float(found2.group(1)) * 1024 * 1024)
                else:
                    down_obj['size'] = int(float(found2.group(1)) * 1024)
        
        short_url = xpath.search(data, '//div[@class="apkdown"]/a/@href')
        if(short_url):
            opener = urllib2.build_opener(util.RedirectHandler)
            apk_url= opener.open(short_url[0]).geturl()
            down_obj['download_link'] = apk_url
            
            print down_obj
            util.sql_do(down_obj)
            util.put_job(down_obj)
            global cnt_all
            cnt_all += 1
    except urllib2.URLError, e:
        logger.error('process_url Exception at: %s, %s' % (url, e.message))    
    except Exception, e:
        logger.error('process_url Exception at: %s, %s' % (url, e.message))  

def process_bizhi_url(url):
    try:
        # print url
        data = urllib2.urlopen(url).read()
        down_obj = util.app_info({'market':market})
        down_obj['app_url'] = url
        down_obj['app_url_md5'] = hashlib.md5(url).hexdigest()
                
        app_name = xpath.search(data, '//div[@class="viewh"]/h1/')
        if(app_name):
            down_obj['app_name'] = app_name[0]
        
        infoleft = xpath.search(data, '//ul[@class="infoleft"]/li')
        if(infoleft):
            found = re.search('([.\d]+)([MK])', infoleft[1])
            if(found):
                if(found.group(2) == 'M'):
                    down_obj['size'] = int(float(found.group(1)) * 1024 * 1024)
                else:
                    # KB
                    down_obj['size'] = int(float(found.group(1)) * 1024)
                    
        short_url = xpath.search(data, '//div[@class="inforight"]/a/@href')
        if(short_url):
            opener = urllib2.build_opener(util.RedirectHandler)
            apk_url= opener.open(short_url[0]).geturl()
            down_obj['download_link'] = apk_url
            
            print down_obj
            util.sql_do(down_obj)
            util.put_job(down_obj)
            global cnt_all
            cnt_all += 1
        
    except urllib2.URLError, e:
        logger.error('process_url Exception at: %s, %s' % (url, e.message))
    except Exception, e:
        logger.error('process_url Exception at: %s, %s' % (url, e.message))      

def process_page_ruanjian(page):
    '''get all app links from a big page'''
    try:
        html = urllib2.urlopen(page).read()
        app_list = xpath.search(html, '//div[@id="iconlist"]/ul/li/a/@href')
        if(not app_list):
            print "page format changed at: %s" % page
            return
        for app in app_list:
            process_ruanjian_url('http://a.3533.com' + app)
        
        page_next = xpath.search(html, '//div[@class="page"]/ul/li/a[@class="next"]/@href')
        if(page_next):
            process_page_ruanjian('http://a.3533.com' + page_next[0])
        else:
            print "reached at the max page or page format changed: %s" % page
    except urllib2.URLError, e:
        logger.error('process_url URLError Exception at: %s, %s' % (page, e.message))
    except Exception, e:
        logger.error('process_page Exception at %s, %s' % (page, e.message))

process_page_game = process_page_ruanjian

def process_page_bizhi(page):
    try:
        html = urllib2.urlopen(page).read()
        app_list = xpath.search(html, '//div[@id="plistbox"]/span/a/@href')
        if(not app_list):
            print "page format changed at: %s" % page
            return
        for app in app_list:
            process_bizhi_url('http://a.3533.com' + app)
        
        page_next = xpath.search(html, '//div[@class="page"]/ul/li/a[@class="next"]/@href')
        if(page_next):
            process_page_bizhi('http://a.3533.com' + page_next[0])
        else:
            print "reached at the max page or page format changed: %s" % page
    except urllib2.URLError, e:
        logger.error('process_url URLError Exception at: %s, %s' % (page, e.message))
    except Exception, e:
        logger.error('process_page Exception at %s, %s' % (page, e.message))

if __name__ == "__main__":
    # global VARs
    entry1 = 'http://a.3533.com/ruanjian/0/1.htm'
    entry2 = 'http://a.3533.com/youxi/0/1.htm'
    entry3 = 'http://a.3533.com/bizhi/0/1.htm'
    market  = '3533.com'
    cnt_all = 0
    
    process_page_ruanjian(entry1)
    process_page_game(entry2)
    process_page_bizhi(entry3)
    
    print "found urls total: %d" % cnt_all
