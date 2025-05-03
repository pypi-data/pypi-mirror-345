import datetime
import requests
from bs4 import BeautifulSoup
import concurrent.futures

DOMAIN = "https://furikomesagi.dic.go.jp"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def _get_notice_table(search_term: str):
    """
    公告一覧テーブルを取得
    """
    url = DOMAIN + "/sel_pubs.php"
    payload = {
        "search_term": search_term,
        "search_no": "none",
        "search_pubs_type": "none",
        "sort_id": "5"
    }
    response = requests.post(url, data=payload, headers=HEADERS)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="sel_pubs_list")
    return table

def _extract_doc_ids(table):
    """
    公告IDリストをテーブルから抽出
    """
    if not table:
        print("公告テーブルが見つかりませんでした。")
        return []
    input_elements = table.find_all('input', {'name': 'doc_id'})
    doc_ids = [inp.get('value') for inp in input_elements if inp.get('value')]
    # デバッグ用（14915, （24年度第17回）権利行使の届出等 公告（06）第638号　令和７年２月７日）
    doc_ids = [doc_id for doc_id in doc_ids if doc_id.strip() == "14915"]
    return doc_ids

def _fetch_detail_html(doc_id: str):
    """
    公告詳細ページのHTMLを取得
    """
    detail_url = DOMAIN + "/pubs_dispatcher.php"
    detail_payload = {
        "head_line": "",
        "doc_id": doc_id
    }
    detail_response = requests.post(detail_url, data=detail_payload, headers=HEADERS)
    detail_response.encoding = detail_response.apparent_encoding
    return BeautifulSoup(detail_response.text, "html.parser")

def _get_basic_frame_links(detail_soup):
    """
    pubs_basic_frame.php へのリンクを抽出
    """
    links = []
    for link in detail_soup.find_all('a'):
        href = link.get('href')
        if (href and href.startswith('./pubs_basic_frame.php')):
            abs_link = href.replace('.', '', 1)
            links.append(abs_link)
    return links

def _fetch_table_from_basic_frame(abs_link):
    """
    pubs_basic_frame.php のテーブルを取得
    """
    abs_url = DOMAIN + abs_link
    get_response = requests.get(abs_url, headers=HEADERS)
    get_response.encoding = get_response.apparent_encoding
    get_soup = BeautifulSoup(get_response.text, "html.parser")
    table = get_soup.find('table', style="{ border: 1px #333333 solid; width: 800px; border-collapse: collapse; empty-cells: show; }")
    return table

def _parse_table_rows(table, doc_id, abs_link):
    """
    テーブル行をパースして辞書リスト化
    """
    flat_links = []
    if not table:
        return flat_links
    rows = table.find_all('tr')[2:]
    for row in rows:
        record = row.find_all('td')
        if len(record) == 7:
            id = record[0].find('input').get('value', None).strip() if record[0].find('input') else None
            process = record[0].find('a').text.strip() if record[0].find('a') else None
            bank_name = record[1].text.strip()
            flat_links.append({
                "doc_id": doc_id,
                "link": abs_link,
                "id": id,
                "process": process,
                "bank_name": bank_name,
                "branch_name": record[2].text.strip(),
                "branch_code": record[3].text.strip(),
                "type": record[4].text.strip(),
                "account": record[5].text.strip(),
                "name": record[6].text.strip().replace('\u3000', ' '),
            })
        elif len(record) == 5:
            # 7列でない場合の処理
            # ゆうちょ銀行のみ rowspan="2" を使用しており2行目が存在するため例外処理
            flat_links.append({
                "doc_id": doc_id,
                "link": abs_link,
                "id": id,
                "process": process,
                "bank_name": bank_name,
                "branch_name": record[0].text.strip(),
                "branch_code": record[1].text.strip(),
                "type": record[2].text.strip(),
                "account": record[3].text.strip(),
                "name": record[4].text.strip().replace('\u3000', ' '),
            })
    return flat_links

def _fetch_notices(search_term: str):
    """
    振り込め詐欺救済法に基づく公告を検索条件に基づいて取得する共通関数
    """
    table = _get_notice_table(search_term)
    doc_ids = _extract_doc_ids(table)
    flat_links = []
    def process_doc_id(doc_id):
        detail_soup = _fetch_detail_html(doc_id)
        abs_links = _get_basic_frame_links(detail_soup)
        results = []
        def process_abs_link(abs_link):
            table = _fetch_table_from_basic_frame(abs_link)
            return _parse_table_rows(table, doc_id, abs_link)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as link_executor:
            link_futures = [link_executor.submit(process_abs_link, abs_link) for abs_link in abs_links]
            for future in concurrent.futures.as_completed(link_futures):
                try:
                    results.extend(future.result())
                except Exception:
                    pass
        return results
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as doc_executor:
        doc_futures = [doc_executor.submit(process_doc_id, doc_id) for doc_id in doc_ids]
        for future in concurrent.futures.as_completed(doc_futures):
            try:
                flat_links.extend(future.result())
            except Exception:
                pass
    return flat_links

def fetch(year: str = None):
    """
    指定した年(YYYY)または直近3ヶ月分の振り込め詐欺救済法に基づく公告を取得します。
    年が指定されていればその年の公告一覧を、指定されていなければ直近3ヶ月分を取得します。
    """
    if year is None:
        return _fetch_notices("near3")
    try:
        y = int(year)
        if y < 2008 or y > datetime.datetime.now().year:
            raise ValueError("Year must be 2008 or later and not in the future.")
    except Exception as e:
        raise ValueError("Invalid year format. Use 'YYYY'.") from e
    return _fetch_notices(year)