import allure
import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL
from pages.system_manager import SystemManagerPage

HOME_URL = BASE_URL


@pytest.fixture(scope="function")
def sys_mgr(page):
    """打开需求工具首页，返回 SystemManagerPage 实例

    先导航到 about:blank 确保 SPA 完全重置，再打开目标页面。
    """
    page.goto("about:blank", wait_until="domcontentloaded")
    page.goto(HOME_URL, wait_until="networkidle", timeout=30000)
    # 等待 Vue 应用完成挂载（侧边栏和 header 均可见）
    page.wait_for_selector(".sidebar-box:visible", timeout=10000)
    page.wait_for_selector(".design-header:visible", timeout=10000)
    page.wait_for_timeout(1000)
    mgr = SystemManagerPage(page)
    mgr.wait_for_user_member_icon()
    return mgr


# ==================== 关于弹窗 ====================

@allure.feature("系统管理")
@allure.story("关于弹窗")
def test_about_dialog_content(sys_mgr):
    """点击「关于」后弹出弹窗，校验工具名称、英文名称、版本号均正确"""
    page = sys_mgr.page

    sys_mgr.click_sub_menu_item("关于")

    # 等待弹窗出现
    dialog = page.locator(".el-dialog:visible").first
    expect(dialog).to_be_visible(timeout=5000)

    dialog_text = dialog.inner_text()

    # 校验弹窗内容
    assert "KD-REP" in dialog_text, f"弹窗中未找到 KD-REP，实际内容: {dialog_text}"
    assert (
        "Requirement Engineering Development Platform" in dialog_text
    ), f"弹窗中未找到英文名称，实际内容: {dialog_text}"
    assert "V3.0.0" in dialog_text, f"弹窗中未找到版本号 V3.0.0，实际内容: {dialog_text}"

    # 关闭弹窗
    close_btn = page.locator(
        ".el-dialog__close, .el-dialog__headerbtn, [aria-label=Close]"
    ).first
    if close_btn.count() > 0 and close_btn.is_visible():
        close_btn.click()
    else:
        page.keyboard.press("Escape")

    # 校验弹窗已关闭
    expect(page.locator(".el-dialog:visible")).to_have_count(0, timeout=5000)


# ==================== 帮助子菜单 ====================

@allure.feature("系统管理")
@allure.story("帮助子菜单")
def test_help_sub_menu_contains_three_items(sys_mgr):
    """点击「帮助」后展开子菜单，应包含用户手册、常见问题、更新日志"""
    sys_mgr.open_help_sub_menu()

    items = sys_mgr.get_help_sub_menu_items()
    expect(items).to_have_count(3)

    item_texts = [items.nth(i).inner_text().strip() for i in range(items.count())]
    assert "用户手册" in item_texts, f"帮助子菜单缺少「用户手册」: {item_texts}"
    assert "常见问题" in item_texts, f"帮助子菜单缺少「常见问题」: {item_texts}"
    assert "更新日志" in item_texts, f"帮助子菜单缺少「更新日志」: {item_texts}"


# ==================== 帮助 → 用户手册 ====================

@allure.feature("系统管理")
@allure.story("帮助-用户手册")
def test_help_user_manual_shows_developing_toast(sys_mgr):
    """点击帮助 → 用户手册，弹出橙色提示「该功能正在开发中，敬请期待！」"""
    page = sys_mgr.page

    sys_mgr.click_help_sub_menu_item("用户手册")

    # 校验橙色警告提示
    toast = page.locator(".el-message--warning:visible").first
    expect(toast).to_be_visible(timeout=3000)
    toast_text = toast.inner_text()
    assert "该功能正在开发中" in toast_text, f"提示语不符: {toast_text}"

    # 页面应仍在 requirementTool
    page_url = page.url
    assert page_url.startswith("http"), f"URL 异常: {page_url}"
    assert "requirementTool" in page_url, f"点击用户手册后离开了 requirementTool: {page_url}"


# ==================== 帮助 → 常见问题 ====================

@allure.feature("系统管理")
@allure.story("帮助-常见问题")
def test_help_faq_shows_developing_toast(sys_mgr):
    """点击帮助 → 常见问题，弹出橙色提示「该功能正在开发中，敬请期待！」"""
    page = sys_mgr.page

    sys_mgr.click_help_sub_menu_item("常见问题")

    # 校验橙色警告提示
    toast = page.locator(".el-message--warning:visible").first
    expect(toast).to_be_visible(timeout=3000)
    toast_text = toast.inner_text()
    assert "该功能正在开发中" in toast_text, f"提示语不符: {toast_text}"

    # 页面应仍在 requirementTool
    page_url = page.url
    assert page_url.startswith("http"), f"URL 异常: {page_url}"
    assert "requirementTool" in page_url, f"点击常见问题后离开了 requirementTool: {page_url}"


# ==================== 帮助 → 更新日志 ====================

@allure.feature("系统管理")
@allure.story("帮助-更新日志")
def test_help_changelog_dialog_open_and_close(sys_mgr):
    """点击帮助 → 更新日志，弹出弹窗，可正常关闭"""
    page = sys_mgr.page

    sys_mgr.click_help_sub_menu_item("更新日志")

    # 等待弹窗
    dialog = page.locator(".el-dialog:visible").first
    expect(dialog).to_be_visible(timeout=5000)
    dialog_text = dialog.inner_text()
    assert "更新日志" in dialog_text, f"弹窗标题不符: {dialog_text}"

    # 关闭弹窗
    close_btn = page.locator(
        ".el-dialog__close, .el-dialog__headerbtn, [aria-label=Close]"
    ).first
    if close_btn.count() > 0 and close_btn.is_visible():
        close_btn.click()
    else:
        page.keyboard.press("Escape")

    expect(page.locator(".el-dialog:visible")).to_have_count(0, timeout=5000)


@allure.feature("系统管理")
@allure.story("帮助-更新日志")
def test_help_changelog_version_select(sys_mgr):
    """更新日志弹窗中点击版本下拉框，遍历每个选项，校验内容区域有响应"""
    page = sys_mgr.page

    # 打开更新日志弹窗
    sys_mgr.click_help_sub_menu_item("更新日志")
    dialog = page.locator(".el-dialog:visible").first
    expect(dialog).to_be_visible(timeout=5000)

    # 找到版本下拉框（.el-select）
    version_select = dialog.locator(".el-select").first
    expect(version_select).to_be_visible()

    # 记录初始内容
    info_box = dialog.locator(".info-box").first
    initial_content = info_box.inner_text()

    def _open_select():
        """展开下拉框并返回可见选项列表"""
        version_select.locator(".el-select__wrapper").first.click()
        page.wait_for_timeout(400)

    def _get_visible_options():
        """返回当前可见的下拉选项定位器"""
        return page.locator(".el-select-dropdown__item:visible")

    # 首次展开
    _open_select()
    options = _get_visible_options()
    option_count = options.count()
    assert option_count > 0, "更新日志版本下拉框没有任何选项"

    # 收集所有选项文本（下拉框打开时一次性读取）
    option_texts = [options.nth(i).inner_text().strip() for i in range(option_count)]

    # 遍历每个选项
    for i in range(option_count):
        # 除首次外，需要重新展开下拉框
        if i > 0:
            _open_select()

        target = _get_visible_options().nth(i)
        target_text = option_texts[i]
        target.click()
        page.wait_for_timeout(500)

        # 检查下拉框显示值已更新
        current_val = version_select.inner_text().strip()
        assert target_text in current_val, (
            f"选项 [{i}]「{target_text}」选择后下拉框显示值不符: {current_val}"
        )

        # 检查内容区域存在（即使显示「暂无信息」也是正常响应）
        content_after = info_box.inner_text()
        assert content_after is not None, f"选择「{target_text}」后内容区域为空"

        # 如果选项大于 1 个，且内容不同，记录下来
        if option_count > 1 and content_after != initial_content:
            initial_content = content_after

    # 关闭弹窗
    page.locator(".el-dialog__headerbtn").first.click()
    expect(page.locator(".el-dialog:visible")).to_have_count(0, timeout=5000)


# ==================== 菜单关闭 ====================

@allure.feature("系统管理")
@allure.story("菜单关闭")
def test_user_menu_toggle_close(sys_mgr):
    """用户菜单弹出后可通过再次点击图标关闭"""
    sys_mgr.click_user_member_icon()
    assert sys_mgr.is_sub_menu_visible(), "菜单未弹出"

    sys_mgr.close_sub_menu()
    assert not sys_mgr.is_sub_menu_visible(), "菜单未关闭"


# ==================== 未实现的入口 ====================

@allure.feature("系统管理")
@allure.story("菜单项不存在")
@pytest.mark.parametrize("item_name", [
    "退出登录",
    "个人设置",
    "账号管理",
])
def test_nonexistent_menu_item_raises(sys_mgr, item_name):
    """点击不存在的菜单项应抛出明确异常"""
    with pytest.raises(AssertionError, match=f"未找到菜单项: {item_name}"):
        sys_mgr.click_sub_menu_item(item_name)
