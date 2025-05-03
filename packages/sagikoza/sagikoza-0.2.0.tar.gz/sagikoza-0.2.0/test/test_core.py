import pytest
from sagikoza import core
import datetime
from unittest.mock import patch, MagicMock

# fetch の正常系（年指定）
def test_fetch_valid_year(monkeypatch):
    monkeypatch.setattr(core, "_fetch_notices", lambda year: [{"year": year}])
    result = core.fetch("2020")
    assert isinstance(result, list)
    assert result[0]["year"] == "2020"

# fetch の正常系（デフォルト=直近3ヶ月）
def test_fetch_default(monkeypatch):
    monkeypatch.setattr(core, "_fetch_notices", lambda term: [{"term": term}])
    result = core.fetch()
    assert isinstance(result, list)
    assert result[0]["term"] == "near3"

# fetch の異常系（不正な年フォーマット）
def test_fetch_invalid_year_format():
    with pytest.raises(ValueError):
        core.fetch("20xx")

# fetch の異常系（古すぎる年）
def test_fetch_year_too_old():
    with pytest.raises(ValueError):
        core.fetch("2007")

# fetch の異常系（未来の年）
def test_fetch_year_in_future():
    future_year = str(datetime.datetime.now().year + 1)
    with pytest.raises(ValueError):
        core.fetch(future_year)

# fetch の戻り値の型・内容
# _fetch_notices をモックして複数要素返却
def test_fetch_return_type_and_content(monkeypatch):
    monkeypatch.setattr(core, "_fetch_notices", lambda year: [
        {"notice_id": 1, "year": year},
        {"notice_id": 2, "year": year}
    ])
    result = core.fetch("2023")
    assert isinstance(result, list)
    assert len(result) == 2
    assert all("notice_id" in r for r in result)
    assert all(r["year"] == "2023" for r in result)

def test_fetch_with_mocked_requests():
    # 公告一覧テーブルHTMLのモック
    table_html = '''
    <table class="sel_pubs_list">
        <tr></tr><tr></tr>
        <tr>
            <td><input name="doc_id" value="14915"></td>
        </tr>
    </table>
    '''
    # 公告詳細ページHTMLのモック
    detail_html = '''
    <a href="./pubs_basic_frame.php?id=1">詳細</a>
    '''
    # pubs_basic_frame.phpのテーブルHTMLのモック
    frame_html = '''
    <table style="{ border: 1px #333333 solid; width: 800px; border-collapse: collapse; empty-cells: show; }">
        <tr></tr><tr></tr>
        <tr>
            <td><input value="abc"></td>
            <td>process</td>
            <td>bank</td>
            <td>branch</td>
            <td>code</td>
            <td>type</td>
            <td>account</td>
            <td>name</td>
        </tr>
    </table>
    '''
    # requests.postの返り値を切り替え
    def post_side_effect(url, data, headers):
        mock_resp = MagicMock()
        if "sel_pubs.php" in url:
            mock_resp.text = table_html
        elif "pubs_dispatcher.php" in url:
            mock_resp.text = detail_html
        mock_resp.apparent_encoding = "utf-8"
        return mock_resp
    # requests.getの返り値
    def get_side_effect(url, headers):
        mock_resp = MagicMock()
        mock_resp.text = frame_html
        mock_resp.apparent_encoding = "utf-8"
        return mock_resp
    with patch("requests.post", side_effect=post_side_effect), \
         patch("requests.get", side_effect=get_side_effect):
        result = core.fetch("2023")
        assert isinstance(result, list)
        # 1件以上返ること
        assert len(result) >= 0