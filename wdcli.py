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
import hashlib
import logging
### TODOLIST
# interactive
# error generator
# log

logging.basicConfig(filename='logfile.txt', filemode='a', format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)
mirrors = ['https://dumps.wikimedia.org','https://dumps.wikimedia.your.org','http://wikipedia.c3sl.ufpr.br']
projects = ['wiki','wikibooks','wiktionary','wikiquote','wikimedia','wikisource','wikinews','wikiversity','wikivoyage']
locales = list()
with open('./wikilocale.txt', 'r') as filehandle:
    for line in filehandle:
        # remove linebreak which is the last character of the string
        currentPlace = line[:-1]
        locales.append(currentPlace)

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

        mirror = str(mirror)
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

        date = str(date)
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
    project_string = ''

    for p in projects:
        project_string = project_string + p + '\n';

    while True:
        if project is None:
            project = input('Select projects:\n' + project_string + '(leave empty for default)\n').split()

            if not project:
                return projects
            else:
                pass
        else:
            if type(project) is str:
                project = project.split(' ')

            if checkProject(project):
                return project
            else:
                project = None
                print('\nInvalid selection of projects. Please try again.')


def select_locale(locale):
    while True:
        if locale is None:
            locale = input('Select locale: (leave empty for default "en")\n').split()

            if not locale:
                locale = []
                locale.append('en')
                return locale
            else:
                pass
        else:
            if type(locale) is str:
                locale = locale.split(' ')

            if checkLocale(locale):
                return locale
            else:
                locale = None
                print('\nInvalid selection of locales. Please try again.')


def checkProject(project):
    for p in project:
        if p not in projects:
            return False
    return True


def checkLocale(locale):
    for l in locale:
        if l not in locales:
            return False
    return True



def DownloadFile(url_link, path, dumpfilename):
    done = 0
    total = 0

    try:
        url = requests.get(url_link, stream = True)
        total = int(url.headers.get('content-length'))
    except:
        print('link not found')
        return False

    if url.status_code == 200:
        with open('%s/%s' % (path, dumpfilename), 'wb') as f:
            for chunk in url.iter_content(1024):
                done += len(chunk)
                f.write(chunk)
                sys.stdout.write('\r%s [%.2f]' % (dumpfilename, done/total*100))

        print('\n%s [Completed]' % (dumpfilename))
        return True


def GetMD5sums(url):
	try:
		raw = urlopen(url).read().decode('utf-8')
	except:
		return ''

	return raw


def MatchMD5(file, md5raw):
	hash_md5 = hashlib.md5()
	try:
		with open(file, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hash_md5.update(chunk)
	except:
		return False

	f = hash_md5.hexdigest()

	if re.search(f, md5raw):
		return True
	else:
		return False

# class
def main():
    parser = argparse.ArgumentParser(description='Downloader of Wikimedia Dumps')
    parser.add_argument('-m', '--mirrors', nargs='?', type=int, help='Use mirror links instead of wikimedia. Such as 1:https://dumps.wikimedia.your.org 2:http://wikipedia.c3sl.ufpr.br', required=False)
    parser.add_argument('-d', '--dates', nargs='?', type=int, help='Set the date of the dumps. (e.g. 20181101). Default = 1st day of current month', required=False)
    parser.add_argument('-p', '--projects', help='Choose which wikimedia projects to download (e.g. all, wikipedia, wikibooks, wiktionary, wikimedia, wikinews, wikiversity, wikiquote, wikisource, wikivoyage)', required=False)
    parser.add_argument('-r', '--maxretries', help='Max retries to download a dump when md5sum doesn\'t fit. Default: 3', required=False)
    parser.add_argument('-l', '--locales', help='Choose which language dumps to download (e.g en my ar)', required=False)
    args = parser.parse_args()

    # Dumps Domain and Mirror
    dumpsdomain = select_mirrors(args.mirrors)

    # Dumps Date, default latest
    dates = select_dates(args.dates)

    # Projects selection
    proj = select_projects(args.projects)

    # Retry downloads when MD5 checker not match
    # Default = 3
    maxretries = 3
    if args.maxretries and int(args.maxretries) >= 0:
        maxretries = int(args.maxretries)

    # Set the locale
    allLocale = select_locale(args.locales)


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
    # print(fulldumps)

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

                path = 'Download/%s/%s%s' % (locale, locale, project)

                if not os.path.exists(path):
                    os.makedirs(path)

                md5raw = GetMD5sums('%s/%s%s/%s/%s%s-%s-md5sums.txt' % (dumpsdomain, locale, project, date, locale, project, date))
                if not md5raw:
                    logging.error("md5sums link not found")
                else:
                    logging.info("md5sums link found")

                # print (urldumps)
                for urldump in urldumps:
                    dumpfilename = urldump.split('/')[-1]
                    DownloadFile(urldump, path, dumpfilename)

                    # md5check
                    if MatchMD5('%s/%s' % (path, dumpfilename), md5raw):
                        logging.info("Matching MD5")
                        corrupted = False
                    else:
                        logging.error("Not matching MD5")
                        os.remove('%s/%s' % (path, dumpfilename))


if __name__ == '__main__':
    main()
