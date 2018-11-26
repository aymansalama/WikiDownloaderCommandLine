# WikiDownloaderCommandLine
Download wiki content from command line

Usage
-----

```
python wdcli.py [OPTION]
``` 
- -m, --mirrors &rarr; Number choice of mirror link consists of:  
                        1:<https://dumps.wikimedia.your.org>  
                        2:<http://wikipedia.c3sl.ufpr.br>  
                        3:<https://dumps.wikimedia.org>  
 ```python -m 1```

- -d, --dates   &rarr; A single data only  
```python wdcli.py -d 20181101 ```
- -p. --projects &rarr; Type of Projects such as wikipedia(wiki), wikibooks, wiktionary, wikimedia, wikinews,wikiversity, wikiquote, wikisource, wikivoyage  
```python wdcli.py -p wiki wiktionary```
- -r, --maxretries &rarr; Number of retries. Default = 3  
```python wdcli.py -r 5```
- -l, --locales &rarr; Languages  
```python wdcli.py -l en my ar```
