#!/usr/bin/env python3

import argparse
import os
import sys
import time
import re       # regex
import datetime
import requests
import logging
from requests.exceptions import HTTPError
from urllib.request import urlopen
### TODOLIST
# interactive
# error generator
# log

logging.basicConfig(filename='logfile.txt', filemode='a', format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)
#
# class 
def main():
    parser = argparse.ArgumentParser(description='Downloader of Wikimedia Dumps')
    parser.add_argument('-m', '--mirror', nargs='?', type=int, help='Use mirror links instead of wikimedia. Such as 1:https://dumps.wikimedia.your.org 2:http://wikipedia.c3sl.ufpr.br', required=False)
    parser.add_argument('-d', '--date', help='Set the date of the dumps. (e.g. 20181101). Default = 1st day of current month', required=False)
    parser.add_argument('-p', '--project', help='Choose which wikimedia projects to download (e.g. all, wikipedia, wikibooks, wiktionary, wikimedia, wikinews, wikiversity, wikiquote, wikisource, wikivoyage)', required=False)
    parser.add_argument('-r', '--maxretries', help='Max retries to download a dump when md5sum doesn\'t fit. Default: 3', required=False)
    parser.add_argument('-l', '--locale', help='Choose which language dumps to download (e.g en my ar)', required=False)
    args = parser.parse_args()
    
    # Dumps Domain and Mirror
    if args.mirror == None:
        dumpsdomain = 'https://dumps.wikimedia.org'
    elif args.mirror == 1:
        dumpsdomain = 'https://dumps.wikimedia.your.org'
    elif args.mirror == 2:
        dumpsdomain = 'http://wikipedia.c3sl.ufpr.br'
    else:
        # Exception Handling for wrong input for mirror choices
        while True:
            secondChance = input("Invalid input for mirror choice.\nInput 1 for dumps.wikimedia.your.org\nInput 2 for wikipedia.c3sl.ufpr.br \
            \nInput 3 for default: dumps.wikimedia.your.org\n")
            if secondChance == '1':
                print(secondChance)
                dumpsdomain = 'https://dumps.wikimedia.your.org'
                break
            elif secondChance == '2':
                dumpsdomain = 'http://wikipedia.c3sl.ufpr.br'
                break
            elif secondChance == '3':
                dumpsdomain = 'https://dumps.wikimedia.org'
                break   

    # Dumps Date, default latest 
    date = ""
    if args.date:
        date = args.date
        print(date)
    
    # Projects selection
    project = ""
    if args.project:
        project = args.project
        print(project)
    #else:
        #proj = ['wiki','wikibooks','wiktionary','wikiquote','wikimedia','wikisource','wikinews','wikiversity','wikivoyage']

    # Retry downloads when MD5 checker not match
    # Default = 3
    maxretries = 3
    if args.maxretries and int(args.maxretries) >= 0:
        maxretries = int(args.maxretries)
    

    # Set the locale
    locale = ""
    if args.locale:
        locale = args.locale  
        print(locale)		


    print ('-' * 50, '\n', 'Checking')
    print("Max retries set to:", maxretries)
    print("Dumps Domain use:", dumpsdomain)
    print("Date selected:", date)
    print("Project selected:",project)
    print("Locale selected:", locale)
    print('\n', '-' * 50)

    
    fulldumps = []
    try:
        downloadlink = '%s/%s%s/%s' % (dumpsdomain, locale, project, date)
        requests.get(downloadlink)
        # r.raise_for_status()
        fulldumps.append([locale,project,date])
        # print('Link : %s -- Ready' % downloadlink)
    except HTTPError:
        print('HTTPError')

    # Exit application if no file can be download
    if fulldumps == []:
        print('Link not found')
        logging.info('Link not found: %s' % downloadlink)
        sys.exit(0)
        
    for locale, project, date in fulldumps:
        # print ('-' * 50, '\n', 'Link found', '\n', '-' * 50)
        time.sleep(1)  # ctrl-c
        print('********Link found***********')
        logging.info('Link found: %s-> Mirror:%s, Project:%s, Date:%s, Locale:%s' % (downloadlink, dumpsdomain, project, date, locale))

if __name__ == '__main__':
    main()
