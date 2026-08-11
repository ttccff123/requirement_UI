from datetime import datetime

import pytest

from common.utils.log_util import logger
from config.settings import BROWSER, DATA_DIR, HEADLESS, LOGIN_PASSWORD, LOGIN_USERNAME, REPORT_DIR, BASE_URL
from core.browser import BrowserManager
from pages.login_page import LoginPage
from pages.my_workspace import MyWorkspace
from pages.platform_navigation import PlatformNavigation
from pages.user_page import UserManager
from common.utils.yaml_util import YamlUtil

# 存储 session 级 page 引用，供 function 级 autouse fixture 使用（避免 scope 提升）
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
    mgr.new_context(
        viewport={"width": 1440, "height": 900},
    )
    yield mgr
    mgr.close()


@pytest.fixture(scope="session")
def page(browser_manager):
    global _shared_page
    p = browser_manager.new_page()
    _shared_page = p
    return p


@pytest.fixture(scope="session")
def _session_login_page(page) -> LoginPage:
    """Session 级：供共享登录流程使用（打开登录页 → 执行登录）。

    非登录测试通过 logged_in_page → my_workspace_page 链间接使用；
    登录测试请使用 function 级 login_page（每个用例独立上下文）。
    """
    lp = LoginPage(page)
    lp.open(BASE_URL)
    logger.info(f"登录页: {BASE_URL}")
    return lp


@pytest.fixture(scope="session")
def logged_in_page(_session_login_page) -> LoginPage:
    """
    前置：已登录状态用于测试登录后才能访问的页面（如：仪表盘、个人中心等）
    依赖 _session_login_page，先打开登录页，再执行登录操作
    """
    page = _session_login_page.page
    _session_login_page.login(LOGIN_USERNAME, LOGIN_PASSWORD)  # 执行登录

    # 等待登录跳转完成
    try:
        page.wait_for_url("**/home**", timeout=12000)
    except Exception:
        try:
            page.wait_for_url("**/organization**", timeout=8000)
        except Exception:
            # URL 未按预期跳转，再试一次登录
            if _session_login_page.is_still_on_login():
                _session_login_page.login(LOGIN_USERNAME, LOGIN_PASSWORD)
                try:
                    page.wait_for_url("**/home**", timeout=12000)
                except Exception:
                    pass
    # 等待页面就绪（侧边栏可见），替代硬等 800ms
    try:
        page.locator(".kd-aside").first.wait_for(state="visible", timeout=10000)
    except Exception:
        pass
    return _session_login_page


@pytest.fixture(scope="module")
def my_workspace_page(logged_in_page) -> MyWorkspace:
    """前置：登录后自动进入我的空间页面（#/home），返回 MyWorkspace 页面对象"""
    my_ws = MyWorkspace(logged_in_page.page)
    my_ws.wait_for_page()
    return my_ws





@pytest.fixture(scope="module")
def user_manager_page(logged_in_page) -> UserManager:
    """前置：登录后点击左侧导航栏'组织'，进入用户管理页面。

    登录成功后不经过我的空间，直接在导航栏点击"组织"进入。
    供 test_user.py 中所有用例使用。
    """
    nav = PlatformNavigation(logged_in_page.page)
    nav.wait_for_sidebar()
    nav.click_navigation_item("组织")
    um = UserManager(logged_in_page.page)
    um.wait_for_page()
    return um


@pytest.fixture(scope="module")
def role_manager_page(logged_in_page) -> "RoleManager":
    """前置：登录后点击左侧导航栏'组织'→ 点击'角色'页签，进入角色管理页面。"""
    from pages.role_page.role_manager import RoleManager
    nav = PlatformNavigation(logged_in_page.page)
    nav.wait_for_sidebar()
    nav.click_navigation_item("组织")
    um = UserManager(logged_in_page.page)
    um.wait_for_page()
    um.click_tab_role()
    rm = RoleManager(logged_in_page.page)
    rm.wait_for_page()
    return rm


@pytest.fixture(scope="module")
def dept_manager_page(logged_in_page, request) -> "DeptManager":
    """前置：登录后点击左侧导航栏'组织'→ 点击'部门'页签，进入部门管理页面。
    不调用 um.wait_for_page() 因为 #pane-user 在部门 tab 下是 aria-hidden。
    """
    from pages.dept_page.dept_manager import DeptManager
    nav = PlatformNavigation(logged_in_page.page)
    nav.wait_for_sidebar()
    nav.click_navigation_item("组织")
    # 等待 tab 栏出现后再切换（替代硬等 800ms）
    try:
        logged_in_page.page.locator(".el-tabs__header").first.wait_for(state="visible", timeout=5000)
    except Exception:
        pytest.skip("组织页面 tab 栏未出现")
    um = UserManager(logged_in_page.page)
    um.click_tab_department()
    dm = DeptManager(logged_in_page.page)
    # 等待部门面板可见（替代硬等 500ms）
    try:
        dm.page.locator("#pane-department").first.wait_for(state="visible", timeout=5000)
    except Exception:
        pytest.skip("部门面板 #pane-department 未变为可见")
    return dm


@pytest.fixture(scope="function")
def login_page(browser_manager) -> LoginPage:
    """每个登录用例独立的浏览器上下文 + 页面。

    登录用例之间互不干扰，也不影响 session 级共享登录状态。
    """
    ctx = browser_manager.browser.new_context(
        viewport={"width": 1440, "height": 900},
    )
    page = ctx.new_page()
    lp = LoginPage(page)
    lp.open(BASE_URL)
    logger.info(f"[独立上下文] 登录页: {BASE_URL}")
    yield lp
    ctx.close()
    logger.info("[独立上下文] 已关闭")


@pytest.fixture(autouse=True)
def _reset_to_workspace(request):
    """test_myworkspace 用例执行前确保停留在我的空间页面，避免上个测试跳转后残留。

    其他页面（如 test_user 在 #/organization）不需要回到我的空间。
    """
    if "test_myworkspace" not in request.node.nodeid:
        return
    global _shared_page
    if _shared_page is not None and "#/home" not in _shared_page.url:
        _shared_page.goto(_shared_page.url.split("#")[0] + "#/home")
        _shared_page.locator(".home-page").first.wait_for(state="visible", timeout=30000)


@pytest.fixture(scope="module")
def myworkspace_data() -> dict:
    """加载我的空间测试数据"""
    return YamlUtil(DATA_DIR / "myworkspace.yaml").read()


def pytest_collection_modifyitems(items):
    """根据 YAML 用例 type 字段自动打标：smoke / system / core"""
    for item in items:
        if not hasattr(item, "callspec") or item.callspec is None:
            continue
        case = item.callspec.params.get("case")
        if not isinstance(case, dict):
            continue
        test_type = case.get("type")
        if test_type in {"smoke", "system", "core"}:
            item.add_marker(getattr(pytest.mark, test_type))


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
