#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import argparse
from argparse import RawTextHelpFormatter
import time
import requests
from termcolor import *
import signal
import inspect
import json

def login(userEmail, passWord):
    token = ''
    zoomEyeLoginUrl = 'https://api.zoomeye.org/user/login'
    #userInfos = '"{"username": {}, "password": {}}"'.format(userEmail, password)
    userInfos = {'username': userEmail, 'password': passWord}
    ui = json.dumps(userInfos)
    try:
        resp = requests.post(url = zoomEyeLoginUrl, data = ui)
        if 200 == resp.status_code:
            token = json.loads(resp.content)['access_token']
        else:
            print 'login status_code: ', resp.status_code
    except Exception, e:
        print str(e)
        return token
            
    return token

def dorkSearch(token, query):
    header = {}
    header['Authorization'] = 'JWT ' + token
    zoomEyeQueryUrl = 'https://api.zoomeye.org/host/search?query='
    url = zoomEyeQueryUrl + query
    result = {}
    try:
        resp = requests.get(url, headers = header)
        if 200 == resp.status_code:
           result = json.loads(resp.content)
    except Exception, e:
        print str(e)
        return result

    return result

def parseResult2File(matches, fileName, subCC, subOS):
    if 0 >= len(matches):
        return
    #print len(matches)
    with open(fileName, 'a') as f:
        for item in matches:
            if item['geoinfo']['country']['code'] in subCC:
                continue
            if None != subOS and item['portinfo']['os'] in subOS:
                continue

            ip = item['ip'].encode('utf-8')
            port = str(item['portinfo']['port'])
            os = item['portinfo']['os']
            if '' == os:
                os = 'unknow'
            country = item['geoinfo']['country']['names']['zh-CN'].encode('utf-8')
            if '' == country:
                country = 'unknow'
            city = item['geoinfo']['city']['names']['zh-CN'].encode('utf-8')
            if '' == city:
                city = 'unknow'
            ipp = ip + ':' + port
            Line= '{:22s}{:12s}\t{:s},{:s}\n'.format(ipp, os, country, city)
            f.write(Line)
                        
        f.close()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='使用说明')
    parser.add_argument('-useremail', help='zoomeye\'s user email.')
    parser.add_argument('-password', help='zoomeye\'s user password.')
    parser.add_argument('-query', help='search query string.')
    parser.add_argument('-page', default = 1,
                                    help='the return search result number of page.')
    parser.add_argument('-subCC', default = 'CN',
                                    help='the country code to sub result.')
    parser.add_argument('-subOS', 
                                    help='the country code to sub result.(example: -subOS Unix,linux)')
    
    if not os.path.exists('outfiles'):
        os.mkdir('outfiles')
    outfile = 'outfiles/' + time.strftime('%Y%m%d%H%M%S', time.localtime()) + '.txt'
    parser.add_argument('-outfile', default = outfile,
                                    help='the result of out file to save in.(default: /outfiles/DATE.txt)')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')

    args = parser.parse_args()

    if (None == args.useremail or '' == args.useremail) or (None == args.password or '' == args.password) or (None == args.query or '' == args.query):
        parser.print_help()
        sys.exit()

    subCC = []
    if None != args.subCC:
        subCC = args.subCC.split(',')
    
    subOS = []
    if None != args.subOS:
        subOS = args.subOS.split(',')
         

#    print 'useremail: ', args.useremail
#    print 'password: ', args.password
    print 'query: ', args.query
    print 'page: ', args.page
    print 'subCC: ', args.subCC
    print 'subOS: ', args.subOS
    print 'outfile: ', args.outfile
    
    token = login(args.useremail, args.password)
    if None == token or '' == token:
        print 'login error!'
        sys.exit()

    for i in range(1, (int(args.page) + 1)):
        tmpQuery = args.query + '&page=' + str(i)
        result = dorkSearch(token, tmpQuery)
        if None == result:
            print 'dorkSearch error!'
            sys.exit()

        matches = result['matches']
        parseResult2File(matches, args.outfile, subCC, subOS)

