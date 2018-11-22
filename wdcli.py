#!/usr/bin/env python3

import argparse
import os
import sys
import time
import re       # regex
import datetime
import requests
from requests.exceptions import HTTPError
from urllib.request import urlopen
### TODOLIST
# interactive
# error generator
# log

mirrors = ['https://dumps.wikimedia.org','https://dumps.wikimedia.your.org','http://wikipedia.c3sl.ufpr.br']
projects = ['wiki','wikibooks','wiktionary','wikiquote','wikimedia','wikisource','wikinews','wikiversity','wikivoyage']

def select_mirrors(mirror):
    mirror_string = ''
    i = 1

    for m in mirrors:
        mirror_string = mirror_string + str(i) + ': ' + m + ' '
        if i is 1:
            mirror_string += '(default)'
        mirror_string += '\n'
        i += 1

    while True:
        if mirror is None:
            mirror = input('Select Mirrors: \n' + mirror_string + '(leave empty for default) \n').replace(' ','')

        if mirror is '':
            mirror = mirrors[0]
            break
        elif mirror is '1':
            mirror = mirrors[0]
            break
        elif mirror is '2':
            mirror = mirrors[1]
            break
        elif mirror is '3':
            mirror = mirrors[2]
            break
        else:
            mirror = None
            print('Invalid input. Please try again\n')

    return mirror


def select_dates(date):
    while True:
        if date is None:
            date = input('Enter Date: (leave empty for default)\n').replace(' ','')

        if date is '':
            date = datetime.date.today().replace(day=1)
            break
        elif len(str(date)) < 8 or len(str(date)) > 8:
            date = None
            print('\nWrong date format! Please enter as YYYYMMDD format.\n')
        elif int(date) > int(datetime.date.today().strftime("%Y%m%d")):
            date = None
            print('\nUh Oh! Dumps are not from the future.\n')
        else:
            break

    return str(date).replace('-','')


def select_projects(project):


# class
def main():
    parser = argparse.ArgumentParser(description='Downloader of Wikimedia Dumps')
    parser.add_argument('-m', '--mirrors', nargs='?', type=int, help='Use mirror links instead of wikimedia. Such as 1:https://dumps.wikimedia.your.org 2:http://wikipedia.c3sl.ufpr.br', required=False)
    parser.add_argument('-d', '--dates', nargs='?', type=int, help='Set the date of the dumps. (e.g. 20181101). Default = 1st day of current month', required=False)
    parser.add_argument('-p', '--projects', help='Choose which wikimedia projects to download (e.g. all, wikipedia, wikibooks, wiktionary, wikimedia, wikinews, wikiversity, wikiquote, wikisource, wikivoyage)', required=False)
    parser.add_argument('-r', '--maxretries', help='Max retries to download a dump when md5sum doesn\'t fit. Default: 3', required=False)
    parser.add_argument('-l', '--locales', nargs='+', help='Choose which language dumps to download (e.g en my ar)', required=False)
    args = parser.parse_args()

    # Dumps Domain and Mirror
    dumpsdomain = select_mirrors(args.mirrors)

    # Dumps Date, default latest
    dates = select_dates(args.dates)


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
    downloadlink = ""
    for l in locale:
        for p in proj:
            try:
                downloadlink = '{}/{}{}/{}'.format(dumpsdomain, l, p, dates)
                r = requests.get(downloadlink)
                r.raise_for_status()
                fulldumps.append([l,p,dates])
                print(downloadlink, '--  Link Ready')
            except HTTPError:
                print(downloadlink, '--  Not Exist')
    print(fulldumps)

    # Exit application if no file can be download
    if fulldumps == []:
        print("\nRequested dumps are not available.\nIf server are updating, try again later.\
        \nEnsure the argument passed are correct.","\n" *3)
        sys.exit(0)

    for locale, project, date in fulldumps:
        print ('-' * 50, '\n', 'Preparing to download', '\n', '-' * 50)
        time.sleep(1)  # ctrl-c
        print(downloadlink)
        with urlopen(downloadlink) as url:
            htmlproj = url.read().decode('utf-8')

        for dumptypes in ['pages-meta-history\d*\.xml[^\.]*\.7z']:
            corrupted = True
            maxRetriesCheck = maxretries
            while (corrupted) and maxRetriesCheck > 0:
                maxRetriesCheck -=1
                # refer "/enwiki/20181101/enwiki-20181101-pages-meta-history1.xml-p26584p28273.7z"
                # enwiki is have many files, looping is required
                m = re.compile(r'<a href="/(?P<urldump>%s%s/%s/%s%s-%s-%s)">' %  (locale,project,date,locale,project,date,dumptypes))
                urldumps = []
                for match in re.finditer(m, htmlproj):
                    print(match)
                    urldumps.append('%s/%s' % (dumpsdomain, match.group('urldump')))


                print (urldumps)
                for urldump in urldumps:
                    dumpfilename = urldump.split('/')[-1]

                    path = 'Download/%s/%s%s' % (locale, locale, project)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    # wget continue downloadlink log to path with dumpfilename
                    os.system('wget --continue %s -O %s/%s' % (urldump, path, dumpfilename))

                    # md5check IN PROGRESS DO NOT DELETE
                    os.system('md5sum %s/%s > md5' % (path, dumpfilename))
                    f = open('md5', 'r')
                    raw = f.read()
                    f.close()
                    md51 = re.findall(
                        r'(?P<md5>[a-f0-9]{32})\s+%s/%s' % (path, dumpfilename), raw)[0]
                    print ((md51))

                    with urlopen('%s/%s%s/%s/%s%s-%s-md5sums.txt' % (dumpsdomain, locale, project, date, locale, project, date)) as f:
                        raw = f.read().decode('utf-8')

                    f = open('%s/%s-%s-md5sums.txt' %
                             (path, project, date), 'w')
                    f.write(raw)
                    f.close()
                    md52 = re.findall(
                        r'(?P<md5>[a-f0-9]{32})\s+%s' % (dumpfilename), raw)[0]
                    print ((md52))

                    if md51 == md52:
                        print ('md5sum Check Pass!')
                        print ('\n' * 3)
                        corrupted = False
                    else:
                        os.remove('%s/%s' % (path, dumpfilename))


if __name__ == '__main__':
    main()
