# sagikoza
A Python library for crawling and retrieving all notices published under Japan’s Furikome Sagi Relief Act, with support for both full data extraction and incremental updates.

## Features
- Automatically retrieves public notices under the Furikome Sagi Relief Act
- Supports fetching by year or for the most recent 3 months
- Incremental data retrieval
- Returns data as a list of dictionaries

## Supported Python Versions
- Python 3.8 or later

## Installation
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

### Get the last 3 months' notices
Fetch notices published under the Furikome Sagi Relief Act during the most recent three-month period.
```python
>>> import sagikoza
>>> mule_accounts = sagikoza.fetch()
>>> print(mule_accounts)
[{'doc_id': '12345', 'link': '/pubs_basic_frame.php?inst_code=1234&p_id=06&pn=123456&re=0', 'id': '1234-5678-9012', 'process': '債権消滅手続開始', 'bank_name': '大江戸銀行', 'branch_name': '丸の内支店', 'branch_code': '234', 'type': '普通預金', 'account': '1234567', 'name': 'カ）エドムラサキ'}, ... ]
```

## Logging Example
sagikoza uses Python's standard `logging` module. To troubleshoot or verify detailed behavior, you can configure logging as shown below to output detailed logs.

```python
import logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG if more detailed logs are needed
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
import sagikoza
sagikoza.fetch()
```
By default, only logs with a level of WARNING or higher are displayed. If you need detailed traces, set `level=logging.DEBUG`.

## Contribution
Bug reports, feature requests, and pull requests are welcome. Please use GitHub Issues or Pull Requests.

## License
This project is licensed under the Apache License. See the LICENSE file for details.

## Notes
- This library retrieves data from public sources. Changes to the source website may affect functionality.
- The accuracy and completeness of the retrieved data are not guaranteed. Please use it together with official information.

## Referece
* [振り込め詐欺救済法に基づく公告](https://furikomesagi.dic.go.jp/index.php)

