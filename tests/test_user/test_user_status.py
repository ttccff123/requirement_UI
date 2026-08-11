"""
用户管理 — 禁用/启用状态测试

测试范围:
- 有项目用户禁用：弹窗提示"无法禁用" → 验证提示词、取消、确定、关闭按钮
- 无项目用户禁用：绿色成功提示 → 表格状态="禁用" → 用户无法登录
- 禁用用户启用：绿色成功提示 → 表格状态="正常" → 用户可以登录
"""

import allure
import pytest

# 模块级变量
_test_username: str | None = None      # 无项目测试用户
_test_password: str = "Aa123456"


@pytest.fixture(autouse=True)
def _cleanup_after_test(user_manager_page):
    """每个用例结束后关闭可能残留的弹窗。"""
    yield
    user_manager_page.page.locator("body").first.press("Escape")
    user_manager_page.page.wait_for_timeout(200)


# ========================================================================
#  工具函数
# ========================================================================

def _find_user_with_projects(user_manager_page) -> str | None:
    """找一个有参与项目的非 admin 用户。"""
    for row in user_manager_page.get_table_data():
        username = row.get("用户名", "")
        if username.lower() == "admin":
            continue
        projects = row.get("参与项目", "0")
        try:
            if projects and int(projects) > 0:
                return username
        except (ValueError, TypeError):
            pass
    return None


# ========================================================================
#  准备无项目测试用户
# ========================================================================


@allure.feature("用户管理")
@allure.story("禁用/启用")
@pytest.mark.order(1)
def test_prepare_user_for_status_test(user_manager_page):
    """准备：找一个无参与项目的用户，重置密码为已知值"""
    global _test_username

    row_data = user_manager_page.get_table_data()
    if not row_data:
        pytest.skip("表格无用户数据")

    candidates = []
    for row in row_data:
        username = row.get("用户名", "")
        if username.lower() == "admin":
            continue
        projects = row.get("参与项目", "0")
        try:
            proj_count = int(projects) if projects and projects.isdigit() else 99
        except (ValueError, TypeError):
            proj_count = 99
        candidates.append((proj_count, username))

    if not candidates:
        pytest.skip("无可用的非 admin 用户")

    candidates.sort(key=lambda x: x[0])
    _test_username = candidates[0][1]

    # 重置密码
    user_manager_page.click_reset_user(_test_username)
    user_manager_page.dialog.wait_for_confirm_dialog()
    user_manager_page.dialog.click_confirm_dialog_confirm()
    user_manager_page.page.wait_for_timeout(1000)


# ========================================================================
#  场景一：有项目用户禁用 → 弹窗提示"无法禁用"
# ========================================================================


@allure.feature("用户管理")
@allure.story("禁用/启用")
@pytest.mark.order(2)
def test_disable_user_with_projects_dialog_prompt(user_manager_page):
    """有项目用户禁用弹窗：提示词验证"""
    username = _find_user_with_projects(user_manager_page)
    if not username:
        pytest.skip("未找到有参与项目的用户")

    user_manager_page.click_disable_user(username)
    user_manager_page.dialog.wait_for_confirm_dialog()

    title = user_manager_page.dialog.get_confirm_dialog_title()
    msg = user_manager_page.dialog.get_confirm_dialog_message()
    assert "无法" in msg or "禁用" in msg, \
        f"弹窗提示应包含'无法禁用'相关文字，标题='{title}'，内容='{msg}'"


@allure.feature("用户管理")
@allure.story("禁用/启用")
@pytest.mark.order(3)
def test_disable_user_with_projects_dialog_cancel(user_manager_page):
    """有项目用户禁用弹窗：取消按钮关闭弹窗，状态不变"""
    username = _find_user_with_projects(user_manager_page)
    if not username:
        pytest.skip("未找到有参与项目的用户")

    # 重新打开弹窗
    user_manager_page.click_disable_user(username)
    user_manager_page.dialog.wait_for_confirm_dialog()

    row_before = user_manager_page.get_row_by_username(username)
    status_before = row_before.get("状态", "") if row_before else ""

    user_manager_page.dialog.click_confirm_dialog_cancel()
    user_manager_page.page.wait_for_timeout(300)

    assert not user_manager_page.dialog.is_confirm_dialog_open(), \
        "点击取消后弹窗应关闭"
    row_after = user_manager_page.get_row_by_username(username)
    assert (row_after.get("状态", "") if row_after else "") == status_before, \
        "取消后状态不应改变"


@allure.feature("用户管理")
@allure.story("禁用/启用")
@pytest.mark.order(4)
def test_disable_user_with_projects_dialog_close(user_manager_page):
    """有项目用户禁用弹窗：关闭按钮关闭弹窗"""
    username = _find_user_with_projects(user_manager_page)
    if not username:
        pytest.skip("未找到有参与项目的用户")

    user_manager_page.click_disable_user(username)
    user_manager_page.dialog.wait_for_confirm_dialog()

    # 尝试点击关闭按钮，不可见时用 Escape 兜底
    close_btn = user_manager_page.page.locator(".el-message-box__headerbtn").first
    if close_btn.count() > 0 and close_btn.is_visible():
        close_btn.click()
    else:
        user_manager_page.page.locator("body").first.press("Escape")
    user_manager_page.page.wait_for_timeout(300)

    assert not user_manager_page.dialog.is_confirm_dialog_open(), \
        "点击关闭按钮后弹窗应关闭"


@allure.feature("用户管理")
@allure.story("禁用/启用")
@pytest.mark.order(5)
def test_disable_user_with_projects_dialog_confirm(user_manager_page):
    """有项目用户禁用弹窗：确定按钮关闭弹窗，状态不变"""
    username = _find_user_with_projects(user_manager_page)
    if not username:
        pytest.skip("未找到有参与项目的用户")

    # 重新打开
    if not user_manager_page.dialog.is_confirm_dialog_open():
        user_manager_page.click_disable_user(username)
        user_manager_page.dialog.wait_for_confirm_dialog()

    row_before = user_manager_page.get_row_by_username(username)
    status_before = row_before.get("状态", "") if row_before else ""

    user_manager_page.dialog.click_confirm_dialog_confirm()
    user_manager_page.page.wait_for_timeout(500)

    assert not user_manager_page.dialog.is_confirm_dialog_open(), \
        "点击确定后弹窗应关闭"
    row_after = user_manager_page.get_row_by_username(username)
    assert (row_after.get("状态", "") if row_after else "") == status_before, \
        "有项目用户状态不应改变"


# ========================================================================
#  场景二：无项目用户禁用 → 绿色成功提示
# ========================================================================


@allure.feature("用户管理")
@allure.story("禁用/启用")
@pytest.mark.order(6)
def test_disable_user_without_projects(user_manager_page):
    """无项目用户禁用：绿色成功提示 + 表格状态变为'禁用'"""
    global _test_username
    if not _test_username:
        pytest.skip("未获取到测试用户名")

    # 确保当前为正常状态
    row = user_manager_page.get_row_by_username(_test_username)
    if row is None:
        pytest.skip(f"用户 {_test_username} 未在当前页找到")
    if row.get("状态", "") == "禁用":
        # 先启用
        user_manager_page.click_disable_user(_test_username)
        user_manager_page.page.wait_for_timeout(1500)

    # 禁用用户
    user_manager_page.click_disable_user(_test_username)
    user_manager_page.page.wait_for_timeout(1500)

    # 如果弹出 Element UI 警告弹窗，跳过
    if user_manager_page.dialog.is_confirm_dialog_open():
        msg = user_manager_page.dialog.get_confirm_dialog_message()
        user_manager_page.dialog.click_confirm_dialog_confirm()
        user_manager_page.page.wait_for_timeout(300)
        pytest.skip(f"用户 {_test_username} 无法禁用: {msg}")

    # 绿色成功提示
    toast_msg = user_manager_page.get_toast_message()
    assert toast_msg, "禁用后应有 Toast 提示"
    toast_type = user_manager_page.toast.get_type()
    assert toast_type == "success", \
        f"禁用成功应为绿色(success)，实际'{toast_type}'"

    # 表格状态
    user_manager_page.page.wait_for_timeout(500)
    row_after = user_manager_page.get_row_by_username(_test_username)
    assert row_after is not None, f"禁用后用户 {_test_username} 应在表格中"
    assert row_after.get("状态", "") == "禁用", \
        f"禁用后状态应为'禁用'，实际'{row_after.get('状态', '')}'"


@allure.feature("用户管理")
@allure.story("禁用/启用")
@pytest.mark.order(7)
def test_disabled_user_cannot_login(login_page):
    """禁用用户无法登录"""
    global _test_username
    if not _test_username:
        pytest.skip("未获取到测试用户名")

    login_page.login(_test_username, _test_password)
    login_page.page.wait_for_timeout(2000)

    assert login_page.is_still_on_login(), \
        f"禁用用户 {_test_username} 应无法登录"


# ========================================================================
#  场景三：启用用户 → 绿色成功提示
# ========================================================================


@allure.feature("用户管理")
@allure.story("禁用/启用")
@pytest.mark.order(8)
def test_enable_user(user_manager_page):
    """启用用户：绿色成功提示 + 表格状态变为'正常'"""
    global _test_username
    if not _test_username:
        pytest.skip("未获取到测试用户名")

    user_manager_page.click_disable_user(_test_username)
    user_manager_page.page.wait_for_timeout(1500)

    # 绿色成功提示
    toast_msg = user_manager_page.get_toast_message()
    assert toast_msg, "启用后应有 Toast 提示"
    toast_type = user_manager_page.toast.get_type()
    assert toast_type == "success", \
        f"启用成功应为绿色(success)，实际'{toast_type}'"

    # 表格状态
    user_manager_page.page.wait_for_timeout(500)
    row_after = user_manager_page.get_row_by_username(_test_username)
    assert row_after is not None
    assert row_after.get("状态", "") == "正常", \
        f"启用后状态应为'正常'，实际'{row_after.get('状态', '')}'"


@allure.feature("用户管理")
@allure.story("禁用/启用")
@pytest.mark.order(9)
def test_enabled_user_can_login(login_page):
    """启用用户可以正常登录"""
    global _test_username
    if not _test_username:
        pytest.skip("未获取到测试用户名")

    login_page.login(_test_username, _test_password)
    login_page.page.wait_for_timeout(2000)

    assert not login_page.is_still_on_login(), \
        f"启用用户 {_test_username} 应能成功登录"
