#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from webscraping import xpath
import re
import urllib2
import util

# Init logger
logger = util.initlog('updater.log')

def update_url(app_obj):
    try:
        # http://a.3533.com/ruanjian/4180.htm
        print app_obj['app_url']
        data = urllib2.urlopen(app_obj['app_url']).read()
        global cnt_updated
        
        # process_ruanjian_url finder version to compare
        if(re.search('/(ruanjian|youxi)/', app_obj['app_url'])):
            apk_left = xpath.search(data, '//div[@class="apkleft"]/ul/li')
            if(apk_left):
                found_version = re.search('([.\d]+)', apk_left[0])
                if(found_version):
                    version = found_version.group(1)
                    if(version == app_obj['version']):
                        return
                    app_obj['version'] = version
                    
                    found2 = re.search('([.\d]+)([MK])', apk_left[4])
                    if(found2):
                        if(found2.group(2) == 'M'):
                            app_obj['size'] = int(float(found2.group(1)) * 1024 * 1024)
                        else:
                            # KB
                            app_obj['size'] = int(float(found2.group(1)) * 1024)
                    
                    short_url = xpath.search(data, '//div[@class="apkdown"]/a/@href')
                    if(short_url):
                        opener = urllib2.build_opener(util.RedirectHandler)
                        apk_url= opener.open(short_url[0]).geturl()
                        app_obj['download_link'] = apk_url
                        app_obj['type'] = 0  # update is 0
                    
                    util.sql_do(app_obj)
                    util.put_job(app_obj)
                    cnt_updated += 1
                    print "updated url: %s" % app_obj['app_url']
                    return
            
            print "page format changed at url: %s" % app_obj['app_url']
            app_obj['app_status'] += 2
            util.sql_do(app_obj)
        # process_bizhi_url find size to compare
        elif(re.search('/bizhi/', app_obj['app_url'])):
            infoleft = xpath.search(data, '//ul[@class="infoleft"]/li')
            if(infoleft):
                found_size = re.search('([.\d]+)([MK])', infoleft[1])
                if(found_size):
                    if(found_size.group(2).upper() == 'M'):
                        # MB
                        size = int(float(found_size.group(1)) * 1024 * 1024)
                    elif(found_size.group(2).upper() == 'K'):
                        # KB
                        size = int(float(found_size.group(1)) * 1024)
                    else:
                        print "wrong size format at %s" % app_obj['app_url']
                        app_obj['app_status'] += 2
                        util.sql_do(app_obj)
                        return
                    if(size == app_obj['size']):
                        return
                    app_obj['size'] = size
                    
                    short_url = xpath.search(data, '//div[@class="inforight"]/a/@href')
                    if(short_url):
                        opener = urllib2.build_opener(util.RedirectHandler)
                        apk_url= opener.open(short_url[0]).geturl()
                        app_obj['download_link'] = apk_url
                        app_obj['type'] = 0  # update is 0
                    
                    util.sql_do(app_obj)
                    util.put_job(app_obj)
                    print "updated url: %s" % app_obj['app_url']
                    cnt_updated += 1
                    return
            print "page format changed at url: %s" % app_obj['app_url']
            app_obj['app_status'] += 2
            util.sql_do(app_obj)
        else:
            print "found new category at url: %s" % app_obj['app_url']
            app_obj['app_status'] += 2
            util.sql_do(app_obj)
        
    except urllib2.URLError, e:
        # timeout
        app_obj['app_status'] += 2
        util.sql_do(app_obj)
    except Exception, e:
        logger.error('update_url exception: %s, %s' % (app_obj['app_url'], e.message)) 

if __name__ == "__main__":
    # global VARs
    
    market = '3533.com'
    cnt_all = 0
    cnt_updated = 0
    
    while(1):
        try:
            md5_list = util.sql_query({'market':market}) # return all the md5s of the market
            print "urls to be updated: %d" % md5_list.count()
            
            for md5 in md5_list:
                app_obj = util.sql_query({'app_url_md5':md5["app_url_md5"]})
                cnt_all += 1
                update_url(app_obj)
        except Exception, e:
            logger.error('exception in util.sql_query: %s, %s' % (market, e.message))
        
        # stats
        print "This round update rate is: (%d/%d)" % (cnt_updated, cnt_all)
        # print "This round update rate is: %.2f%%(%d/%d)" % (100*cnt_updated/float(cnt_all), cnt_updated, cnt_all)