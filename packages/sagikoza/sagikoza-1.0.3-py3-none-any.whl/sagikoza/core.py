import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
import concurrent.futures
import logging
from typing import Optional, List, Dict, Any

DOMAIN = "https://furikomesagi.dic.go.jp"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

logger = logging.getLogger(__name__)

def _get_notice_table(search_term: str) -> Optional[BeautifulSoup]:
    """
    Fetch the notice table HTML for a given search term.

    Args:
        search_term (str): The search term to use for fetching the notice table.

    Returns:
        bs4.element.Tag or None: The BeautifulSoup Tag object representing the notice table, or None if not found.
    """
    logger.debug(f"Fetching notice table: search_term={search_term}")
    url = f"{DOMAIN}/sel_pubs.php"
    payload = {
        "search_term": search_term,
        "search_no": "none",
        "search_pubs_type": "none",
        "sort_id": "5"
    }
    response = requests.post(url, data=payload, headers=HEADERS)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find("table", class_="sel_pubs_list")

def _extract_doc_ids(table) -> List[str]:
    """
    Extract notice document IDs from the notice table.

    Args:
        table (bs4.element.Tag): The BeautifulSoup Tag object representing the notice table.

    Returns:
        list[str]: A list of document IDs extracted from the table.
    """
    if not table:
        logger.warning("Notice table not found.")
        return []
    doc_ids = [inp.get('value') for inp in table.find_all('input', {'name': 'doc_id'}) if inp.get('value')]
    logger.debug(f"Extracted doc_ids: {doc_ids}")
    # Debug: only extract 14918
    # return ["14918"]
    return doc_ids

def _fetch_detail_html(doc_id: str) -> BeautifulSoup:
    """
    Fetch the HTML of the notice detail page for a given document ID.

    Args:
        doc_id (str): The document ID for which to fetch the detail page.

    Returns:
        bs4.BeautifulSoup: The BeautifulSoup object of the detail page HTML.
    """
    logger.debug(f"Fetching notice detail HTML: doc_id={doc_id}")
    url = f"{DOMAIN}/pubs_dispatcher.php"
    payload = {"head_line": "", "doc_id": doc_id}
    response = requests.post(url, data=payload, headers=HEADERS)
    response.encoding = response.apparent_encoding
    return BeautifulSoup(response.text, "html.parser")

def _get_basic_frame_links(detail_soup: BeautifulSoup) -> List[str]:
    """
    Extract links to 'pubs_basic_frame.php' from the detail page soup.

    Args:
        detail_soup (bs4.BeautifulSoup): The BeautifulSoup object of the detail page HTML.

    Returns:
        list[str]: A list of relative URLs to 'pubs_basic_frame.php'.
    """
    links = [link.get('href').replace('.', '', 1) for link in detail_soup.find_all('a')
            if link.get('href', '').startswith('./pubs_basic_frame.php')]
    logger.debug(f"Extracted basic_frame links: {links}")
    return links

def _fetch_table_from_basic_frame(abs_link: str) -> Optional[Any]:
    """
    Fetch the table from a 'pubs_basic_frame.php' page.

    Args:
        abs_link (str): The absolute link to the 'pubs_basic_frame.php' page.

    Returns:
        bs4.element.Tag or None: The BeautifulSoup Tag object representing the table, or None if not found.
    """
    logger.debug(f"Fetching basic_frame table: abs_link={abs_link}")
    url = f"{DOMAIN}{abs_link}"
    response = requests.get(url, headers=HEADERS)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select_one('table[style*="1px #333333"][style*="width: 800px"]')

def _parse_table_rows(table, doc_id: str, abs_link: str) -> List[Dict[str, Any]]:
    """
    Parse table rows into a list of dictionaries containing notice details.

    Args:
        table (bs4.element.Tag): The BeautifulSoup Tag object representing the table.
        doc_id (str): The document ID associated with the table.
        abs_link (str): The absolute link to the table page.

    Returns:
        list[dict]: A list of dictionaries, each representing a row of notice details.
    """
    if not table:
        logger.warning(f"Table not found: doc_id={doc_id}, abs_link={abs_link}")
        return []
    rows = table.find_all('tr')[2:]
    query_params = parse_qs(urlparse(abs_link).query)
    bank_code = query_params.get('inst_code', [None])[0]
    p_id = query_params.get('p_id', [None])[0]
    pn = query_params.get('pn', [None])[0]
    flat_links = []
    for row in rows:
        record = row.find_all('td')
        if len(record) == 7:
            id = record[0].find('input').get('value', None).strip() if record[0].find('input') else None
            process = record[0].find('a').text.strip() if record[0].find('a') else None
            bank_name = record[1].text.strip()
            flat_links.append({
                "doc_id": doc_id,
                "id": id,
                "p_id": p_id,
                "pn": pn,
                "process": process,
                "bank_name": bank_name,
                "bank_code": bank_code,
                "branch_name": record[2].text.strip(),
                "branch_code": record[3].text.strip(),
                "type": record[4].text.strip(),
                "account": record[5].text.strip(),
                "name": record[6].text.strip().replace('\u3000', ' '),
            })
        elif len(record) == 5:
            # Exception handling for Japan Post Bank, etc.
            logger.debug(f"Exceptional table row: doc_id={doc_id}, abs_link={abs_link}")
            flat_links.append({
                "doc_id": doc_id,
                "id": id,
                "p_id": p_id,
                "pn": pn,
                "process": process,
                "bank_name": bank_name,
                "bank_code": bank_code,
                "branch_name": record[0].text.strip(),
                "branch_code": record[1].text.strip(),
                "type": record[2].text.strip(),
                "account": record[3].text.strip(),
                "name": record[4].text.strip().replace('\u3000', ' '),
            })
    return flat_links

def _fetch_notices(search_term: str) -> List[Dict[str, Any]]:
    """
    Fetch notices based on the given search criteria.

    Args:
        search_term (str): The search term or year to fetch notices for.

    Returns:
        list[dict]: A list of dictionaries containing notice details.
    """
    table = _get_notice_table(search_term)
    doc_ids = _extract_doc_ids(table)
    logger.info(f"Number of doc_ids to fetch: {len(doc_ids)}")
    flat_links = []
    def process_doc_id(doc_id):
        """
        Process a single document ID to fetch and parse its notice details.

        Args:
            doc_id (str): The document ID to process.

        Returns:
            list[dict]: A list of dictionaries containing notice details for the document ID.
        """
        try:
            detail_soup = _fetch_detail_html(doc_id)
            abs_links = _get_basic_frame_links(detail_soup)
            # Memory optimization: explicitly delete soup after use
            del detail_soup
            results = []
            def process_abs_link(abs_link):
                """
                Process a single absolute link to fetch and parse its table rows.

                Args:
                    abs_link (str): The absolute link to process.

                Returns:
                    list[dict]: A list of dictionaries containing notice details for the link.
                """
                try:
                    table = _fetch_table_from_basic_frame(abs_link)
                    parsed = _parse_table_rows(table, doc_id, abs_link)
                    # Memory optimization: explicitly delete table after use
                    del table
                    return parsed
                except Exception as e:
                    logger.exception(f"Exception while processing abs_link: doc_id={doc_id}, abs_link={abs_link}")
                    return []
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as link_executor:
                link_futures = [link_executor.submit(process_abs_link, abs_link) for abs_link in abs_links]
                for future in concurrent.futures.as_completed(link_futures):
                    try:
                        results.extend(future.result())
                    except Exception as e:
                        logger.exception(f"Exception in link_futures: doc_id={doc_id}")
            return results
        except Exception as e:
            logger.exception(f"Exception while processing doc_id: doc_id={doc_id}")
            return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as doc_executor:
        doc_futures = [doc_executor.submit(process_doc_id, doc_id) for doc_id in doc_ids]
        for future in concurrent.futures.as_completed(doc_futures):
            try:
                flat_links.extend(future.result())
            except Exception as e:
                logger.exception("Exception in doc_futures")
    logger.info(f"Total records fetched: {len(flat_links)}")
    return flat_links

def fetch(year: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch notices for the specified year or for the last 3 months.

    Args:
        year (str, optional): The year (YYYY) to fetch notices for. If None, fetches notices for the last 3 months.

    Returns:
        list[dict]: A list of dictionaries containing notice details.

    Raises:
        ValueError: If the year is invalid or in the wrong format.
    """
    if year is None:
        logger.info("Fetching notices for the last 3 months")
        return _fetch_notices("near3")
    try:
        y = int(year)
        now_year = datetime.datetime.now().year
        if y < 2008 or y > now_year:
            logger.error(f"Invalid year specified: {year}")
            raise ValueError("Year must be 2008 or later and not in the future.")
    except Exception as e:
        logger.error(f"Failed to parse year: {year}")
        raise ValueError("Invalid year format. Use 'YYYY'.") from e
    logger.info(f"Fetching notices for year {year}")
    return _fetch_notices(year)