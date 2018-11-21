#!/usr/bin/env python3

import argparse
import os
import sys
import time
import re       # regex
from urllib.request import urlopen
### TODOLIST
# interactive
# error generator
# log
# md5checker

# class 
def main():
    parser = argparse.ArgumentParser(description='Downloader of Wikimedia Dumps')
    parser.add_argument('-m', '--mirrors', nargs='?', type=int, help='Use mirror links instead of wikimedia. Such as 1:https://dumps.wikimedia.your.org 2:http://wikipedia.c3sl.ufpr.br', required=False)
    parser.add_argument('-d', '--dates', nargs='?', help='Set the date of the dumps. Default = latest', required=False)
    parser.add_argument('-p', '--projects', help='Choose which wikimedia projects to download (e.g. all, wikipedia, wikibooks, wiktionary, wikimedia, wikinews, wikiversity, wikiquote, wikisource, wikivoyage)', required=False)
    parser.add_argument('-r', '--maxretries', help='Max retries to download a dump when md5sum doesn\'t fit. Default: 3', required=False)
    parser.add_argument('-l', '--locales', nargs='+', help='Choose which language dumps to download (e.g)', required=False)
    args = parser.parse_args()
    
    # Dumps Domain and Mirror
    if args.mirrors == None:
        dumpsdomain = 'https://dumps.wikimedia.org'
    elif args.mirrors == 1:
        dumpsdomain = 'https://dumps.wikimedia.your.org'
    elif args.mirrors == 2:
        dumpsdomain = 'http://wikipedia.c3sl.ufpr.br'
    else:
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
                

    with urlopen('{}/backup-index.html'.format(dumpsdomain)) as url:
        html = url.read().decode('utf-8')

    # Dumps Date
    if args.dates:
        dates = args.dates 
    else:
        dates = 20181021   # default testing
    
    # Projects selection
    proj = []
    if args.projects:
        proj = [args.projects]
    else:
        proj = ['wiki','wikibooks','wiktionary','wikiquote','wikimedia','wikisource','wikinews','wikiversity','wikivoyage']

    # Retry downloads when MD5 checker not match
    # Default = 3
    maxretries = 3
    if args.maxretries and int(args.maxretries) >= 0:
        maxretries = int(args.maxretries)
    

    # Set the locale
    allLocale = []
    if args.locales:
        allLocale = args.locales
    else:
        with open('wikilocale.txt', 'r') as filehandle:
            for line in filehandle:
                # remove linebreak which is the last character of the string
                currentPlace = line[:-1]
                allLocale.append(currentPlace)       


    locale = allLocale
    print ('-' * 50, '\n', 'Checking')
    print("Max retries set to:", maxretries)
    print("Dumps Domain use:", dumpsdomain)
    print("Dates selected:", dates)
    print("Project selected:",proj)
    print("Locale selected:", locale)
    print('\n', '-' * 50)



    fulldumps = []
    # Regex to get date from the html page
    for l in locale:
        for p in proj:
            REGEXPROJDATE = r'<a href="(?P<language>%s)(?P<project>%s)/(?P<date>%s)">[^<]+</a>: <span class=\'done\'>Dump complete</span>' % (l, p, dates)
            m = re.compile(REGEXPROJDATE)
            # print(m)
            for match in re.finditer(m, html):
                # print(match)
                fulldumps.append([match.group('language'), match.group('project'),match.group('date')])
    
    # Exit application if no file can be download.
    if fulldumps == []:
        print("\nRequested dumps are not available.\nIf server are updating, try again later.\
        \nEnsure the argument passed are correct.","\n" *3)
        sys.exit(0)
        
    for locale, project, date in fulldumps:
        print ('-' * 50, '\n', 'Checking', locale, project, date, '\n', '-' * 50)
        time.sleep(1)  # ctrl-c
        f = urlopen('%s/%s%s/%s/' % (dumpsdomain, locale, project, date))
        htmlproj = f.read().decode('utf-8')
        # print (htmlproj)
        f.close()

        for dumptypes in ['pages-meta-history\d*\.xml[^\.]*\.7z']:
            corrupted = False
            maxRetriesCheck = maxretries
            while (not corrupted) and maxRetriesCheck > 0:
                maxRetriesCheck -=1
                # refer "/enwiki/20181101/enwiki-20181101-pages-meta-history1.xml-p26584p28273.7z"
                # enwiki is have many files, looping is required
                m = re.compile(r'<a href="(?P<urldump>/%s%s/%s/%s%s-%s-%s)">' %  (locale,project,date,locale,project,date,dumptypes))
                urldumps = []
                for match in re.finditer(m, htmlproj):
                    urldumps.append('%s/%s' % (dumpsdomain, match.group('urldump')))
                
                
                # print (urldumps)
                for urldump in urldumps:
                    dumpfilename = urldump.split('/')[-1]

                    path = 'Download/%s/%s%s' % (locale, locale, project)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    # wget continue downloadlink log to path with dumpfilename
                    os.system('wget --continue %s -O %s/%s' % (urldump, path, dumpfilename))

                    # # md5check
                    # os.system('md5sum %s/%s > md5' % (path, dumpfilename))
                    # f = open('md5', 'r')
                    # raw = f.read()
                    # f.close()
                    # md51 = re.findall(
                    #     r'(?P<md5>[a-f0-9]{32})\s+%s/%s' % (path, dumpfilename), raw)[0]
                    # print ((md51))

                    # f = urlopen(
                    #     '%s/%s/%s/%s-%s-md5sums.txt' % (dumpsdomain, project, date, project, date)).decode('utf-8')
                    # raw = f.read()
                    # f.close()
                    # f = open('%s/%s-%s-md5sums.txt' %
                    #          (path, project, date), 'w')
                    # f.write(raw)
                    # f.close()
                    # md52 = re.findall(
                    #     r'(?P<md5>[a-f0-9]{32})\s+%s' % (dumpfilename), raw)[0]
                    # print ((md52))

                    # if md51 == md52:
                    #     print ('MD5SUM Check Pass!')
                    #     print ('\n' * 3)
                    #     corrupted = False
                    # else:
                    #     os.remove('%s/%s' % (path, dumpfilename))               


if __name__ == '__main__':
    main()
