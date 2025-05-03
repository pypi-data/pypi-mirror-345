# sagikoza
A Python library for crawling and retrieving all notices published under Japan’s Furikome Sagi Relief Act, with support for both full data extraction and incremental updates.  

## Installation  
----------------------
sagikoza is available on pip installation.
```shell
$ python -m pip install sagikoza
```
  
### GitHub Install
Installing the latest version from GitHub:  
```shell
$ git clone https://github.com/new-village/sagikoza
$ cd sagikoza
$ python setup.py install
```
    
## Usage
This section describes how to use this library.  
  
### Get a specific year's notice
Fetch notices published under the Furikome Sagi Relief Act from 2008 onwards. Returns the notices for the year passed as an argument as 'YYYY'.
```python
>>> import sagikoza
>>> mule_accounts = sagikoza.fetch('2025')
>>> print(mule_accounts)
```

### Get a last 3 monthes notice
Fetch notices published under the Furikome Sagi Relief Act during the most recent three-month period.
```python
>>> import sagikoza
>>> mule_accounts = sagikoza.update()
>>> print(mule_accounts)
```

## Referece
* [振り込め詐欺救済法に基づく公告](https://furikomesagi.dic.go.jp/index.php)  
