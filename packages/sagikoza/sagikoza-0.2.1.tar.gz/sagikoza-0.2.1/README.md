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
[{'doc_id': '12345', 'link': '/pubs_basic_frame.php?inst_code=1234&p_id=06&pn=123456&re=0', 'id': '1234-5678-9012', 'process': '債権消滅手続開始', 'bank_name': '大江戸銀行', 'branch_name': '丸の内支店', 'branch_code': '234', 'type': '普通預金', 'account': '1234567', 'name': 'カ）エドムラサキ'}, ... ]
```

### Get a last 3 monthes notice
Fetch notices published under the Furikome Sagi Relief Act during the most recent three-month period.
```python
>>> import sagikoza
>>> mule_accounts = sagikoza.fetch()
>>> print(mule_accounts)
[{'doc_id': '12345', 'link': '/pubs_basic_frame.php?inst_code=1234&p_id=06&pn=123456&re=0', 'id': '1234-5678-9012', 'process': '債権消滅手続開始', 'bank_name': '大江戸銀行', 'branch_name': '丸の内支店', 'branch_code': '234', 'type': '普通預金', 'account': '1234567', 'name': 'カ）エドムラサキ'}, ... ]
```

## Referece
* [振り込め詐欺救済法に基づく公告](https://furikomesagi.dic.go.jp/index.php)  
