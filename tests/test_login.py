import re

import allure
import pytest
from playwright.sync_api import expect

from common.utils.yaml_util import YamlUtil
from config.settings import DATA_DIR, LOGIN_PASSWORD, LOGIN_USERNAME

login_data = YamlUtil(DATA_DIR / "login.yaml").read()
page_expect = login_data["page"]
login_cases = login_data["cases"]


@allure.feature("登录")
@allure.story("页面文案")
@pytest.mark.smoke
def test_login_page_texts(login_page):
    """校验页签 title、工具名称、中文名称、英文名称"""

    assert login_page.get_page_title() == page_expect["title"]
    assert login_page.get_tool_name() == page_expect["tool_name"]
    assert login_page.get_cn_name() == page_expect["cn_name"]
    assert login_page.get_en_name() == page_expect["en_name"]


def _resolve_credentials(case: dict) -> tuple[str, str]:
    if case.get("use_env"):
        username = LOGIN_USERNAME
        password = case.get("password", LOGIN_PASSWORD)
    else:
        username = case.get("username", "")
        password = case.get("password", "")
    return username, password


@pytest.mark.parametrize(
    "case",
    login_cases,
    ids=[c["case"] for c in login_cases],
)
@allure.feature("登录")
def test_login(login_page, case):
    """登录功能验证：成功跳转离开登录页；失败停留并提示错误"""
    allure.dynamic.title(case["case"])
    if case.get("type"):
        allure.dynamic.tag(case["type"])
    username, password = _resolve_credentials(case)
    if case["expected"] == "success" and (not username or not password):
        pytest.skip("请在 .env 中配置 LOGIN_USERNAME / LOGIN_PASSWORD 后再跑成功登录用例")

    login_page.login(username, password)

    if case["expected"] == "success":
        expect(login_page.page).not_to_have_url(re.compile(r"#/login"), timeout=15000)
        assert not login_page.is_still_on_login()
    else:
        toast = login_page.get_toast_message()
        assert case["message"] in toast
        assert login_page.is_still_on_login()
