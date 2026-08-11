from datetime import datetime

import pytest

from common.utils.log_util import logger
from config.settings import BROWSER, HEADLESS, REPORT_DIR
from core.browser import BrowserManager
from pages.homePage import HomePage

REQUIREMENT_TOOL_URL = (
    "http://192.168.4.179:20081/webapp/requirement-app/#/requirementTool?projectId=defaultProjectID"
)

# 只保留当前需求工具页面对应的测试上下文
_shared_page = None

try:
    import allure
except ImportError:  # pragma: no cover
    allure = None

try:
    from pytest_html import extras
except ImportError:  # pragma: no cover
    extras = None


@pytest.fixture(scope="session")
def browser_manager():
    mgr = BrowserManager(headless=HEADLESS)
    mgr.start_browser(BROWSER)
    mgr.new_context(viewport={"width": 1440, "height": 900})
    yield mgr
    mgr.close()


@pytest.fixture(scope="session")
def page(browser_manager):
    global _shared_page
    p = browser_manager.new_page()
    _shared_page = p
    return p


@pytest.fixture(scope="function")
def requirement_page(page):
    """直接打开需求工具页面，不做登录"""
    page.goto(REQUIREMENT_TOOL_URL)
    page.wait_for_url("**/requirementTool**", timeout=30000)
    yield HomePage(page)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page")
    if page is None:
        return

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = item.nodeid.replace("/", "_").replace("::", "_").replace(" ", "_")
    path = REPORT_DIR / f"{name}_{stamp}.png"
    try:
        page.screenshot(path=str(path), full_page=True)
        logger.error(f"用例失败，已截图: {path}")
        if allure is not None:
            allure.attach.file(
                str(path),
                name="失败截图",
                attachment_type=allure.attachment_type.PNG,
            )
        if extras is not None:
            report.extras = getattr(report, "extras", [])
            report.extras.append(extras.image(str(path)))
            report.extras.append(extras.text(str(path), name="截图路径"))
    except Exception as exc:
        logger.error(f"失败截图异常: {exc}")
