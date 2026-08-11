import allure
import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL
from pages.homePage import HomePage

HOME_URL = BASE_URL

# 菜单项：(显示名, 方法名)
MENU_ITEMS: list[tuple[str, str]] = [
    ("新建", "click_new"),
    ("原始需求", "click_raw_requirements"),
    ("最近打开", "click_recent_open"),
    ("我的方案", "click_my_solutions"),
    ("我的收藏", "click_my_collection"),
    ("回收站", "click_recycle_bin"),
    ("下载管理", "click_download_management"),
    ("文档模板", "click_document_templates"),
    ("属性设置", "click_property_settings"),
    ("数据资源", "click_data_resources"),
]

# 侧边栏预期可见的元素
SIDEBAR_ELEMENTS = [
    "恺脉",
    "KD-REP",
    "Requirement Engineering Development Platform",
    "新建",
    "原始需求",
    "最近打开",
    "我的方案",
    "我的收藏",
    "回收站",
    "下载管理",
    "文档模板",
    "属性设置",
    "数据资源",
]


@pytest.fixture(scope="function")
def home_page(page):
    """直接打开需求工具首页"""
    page.goto(HOME_URL, wait_until="domcontentloaded", timeout=30000)
    return HomePage(page)


# ==================== 页面基础文案 ====================

@allure.feature("首页")
@allure.story("页面文案")
def test_homepage_tool_name_and_english_name(home_page):
    """校验首页工具名称和英文名称"""
    page = home_page.page
    page_text = page.locator("body").inner_text()

    assert "KD-REP" in page_text or "KD-REP" in page.title()
    assert (
        "Requirement Engineering Development Platform" in page_text
        or "Requirement Engineering Development Platform" in page.title()
    )


# ==================== 侧边栏元素校验 ====================

@allure.feature("首页")
@allure.story("侧边栏元素")
def test_homepage_sidebar_contains_all_menu_items(home_page):
    """校验侧边栏包含所有预期的菜单和标识元素"""
    page = home_page.page

    # 侧边栏容器可见
    expect(home_page.get_sidebar()).to_be_visible()

    # 每个预期元素都存在于页面文本中
    sidebar_text = home_page.get_sidebar().inner_text()
    for name in SIDEBAR_ELEMENTS:
        assert name in sidebar_text, f"侧边栏中未找到: {name}"


# ==================== 菜单点击导航 ====================

@allure.feature("首页")
@allure.story("菜单导航")
def test_homepage_menu_clicks_navigate_correctly(home_page):
    """点击每个菜单项后页面能正常打开（URL 或页面内容包含 requirementTool）"""
    page = home_page.page
    expect(home_page.get_sidebar()).to_be_visible()

    for menu_name, method_name in MENU_ITEMS:
        home_page.open(HOME_URL)
        getattr(home_page, method_name)()

        page_url = page.url
        page_text = page.locator("body").inner_text()
        assert page_url and page_url.startswith("http"), f"点击 {menu_name} 后 URL 为空"
        assert (
            "requirementTool" in page_url or page_text
        ), f"点击 {menu_name} 后未停留在 requirementTool 页面"
