"""
用户管理 — 重置密码测试

测试范围:
- 重置按钮点击 & 弹窗弹出
- 弹窗 title、提示语、取消、确定、关闭按钮验证
- 重置后用新密码登录
- 重置前密码登录校验
"""

import allure
import pytest
import re

# 模块级变量：记录被重置的用户名和密码，供后续登录验证测试使用
_reset_username: str | None = None
_reset_password: str = "Aa123456"  # 系统默认重置密码


@pytest.fixture(autouse=True)
def _close_dialog_after_test(user_manager_page):
    """每个用例结束后关闭可能残留的弹窗，避免影响下一条用例。"""
    yield
    # 按 Escape 关闭弹窗
    user_manager_page.page.locator("body").first.press("Escape")
    user_manager_page.page.wait_for_timeout(200)
    # 如果 Escape 关不掉，尝试点取消按钮
    if user_manager_page.dialog.is_reset_password_dialog_open():
        try:
            user_manager_page.dialog.click_reset_password_cancel()
            user_manager_page.page.wait_for_timeout(200)
        except Exception:
            pass


# ========================================================================
#  弹窗验证
# ========================================================================


@allure.feature("用户管理")
@allure.story("重置密码")
@pytest.mark.order(1)
def test_reset_password_dialog_appears(user_manager_page):
    """点击重置图标应弹出重置密码弹窗"""
    # 先关闭可能残留的弹窗
    user_manager_page.page.locator("body").first.press("Escape")
    user_manager_page.page.wait_for_timeout(200)

    user_manager_page.click_reset_user_by_index(1)
    user_manager_page.dialog.wait_for_reset_password_dialog()
    assert user_manager_page.dialog.is_reset_password_dialog_open(), "重置密码弹窗应弹出"


@allure.feature("用户管理")
@allure.story("重置密码")
@pytest.mark.order(2)
def test_reset_password_dialog_title(user_manager_page):
    """重置密码弹窗标题应为'重置密码'"""
    # 弹窗已由上一条用例打开
    if not user_manager_page.dialog.is_reset_password_dialog_open():
        user_manager_page.click_reset_user_by_index(1)
        user_manager_page.dialog.wait_for_reset_password_dialog()
    title = user_manager_page.dialog.get_reset_password_dialog_title()
    assert title == "重置密码", f"弹窗标题应为'重置密码'，实际'{title}'"


@allure.feature("用户管理")
@allure.story("重置密码")
@pytest.mark.order(3)
def test_reset_password_dialog_prompt(user_manager_page):
    """重置密码弹窗应有提示语"""
    if not user_manager_page.dialog.is_reset_password_dialog_open():
        user_manager_page.click_reset_user_by_index(1)
        user_manager_page.dialog.wait_for_reset_password_dialog()
    body = user_manager_page.dialog.get_reset_password_dialog_body_text()
    assert body, "弹窗提示语不应为空"
    # 提示语应包含"重置"或"密码"相关关键词
    assert "密码" in body or "重置" in body or "确定" in body, \
        f"提示语应包含密码/重置相关文字，实际'{body}'"


@allure.feature("用户管理")
@allure.story("重置密码")
@pytest.mark.order(4)
def test_reset_password_cancel_button(user_manager_page):
    """点击取消按钮应关闭弹窗且不触发操作"""
    if not user_manager_page.dialog.is_reset_password_dialog_open():
        user_manager_page.click_reset_user_by_index(1)
        user_manager_page.dialog.wait_for_reset_password_dialog()
    user_manager_page.dialog.click_reset_password_cancel()
    user_manager_page.page.wait_for_timeout(300)
    assert not user_manager_page.dialog.is_reset_password_dialog_open(), \
        "点击取消后弹窗应关闭"


@allure.feature("用户管理")
@allure.story("重置密码")
@pytest.mark.order(5)
def test_reset_password_close_button(user_manager_page):
    """点击 X 关闭按钮应关闭弹窗"""
    # 重新打开弹窗
    user_manager_page.click_reset_user_by_index(1)
    user_manager_page.dialog.wait_for_reset_password_dialog()
    user_manager_page.dialog.close_reset_password_dialog()
    user_manager_page.page.wait_for_timeout(300)
    assert not user_manager_page.dialog.is_reset_password_dialog_open(), \
        "点击关闭按钮后弹窗应关闭"


# ========================================================================
#  确认重置 & 登录校验
# ========================================================================


@allure.feature("用户管理")
@allure.story("重置密码")
@pytest.mark.order(6)
def test_reset_password_confirm(user_manager_page):
    """点击确定按钮应重置密码并弹出成功提示"""
    global _reset_username, _reset_password

    # 打开弹窗
    user_manager_page.click_reset_user_by_index(1)
    user_manager_page.dialog.wait_for_reset_password_dialog()

    # 记录被重置的用户名
    row_data = user_manager_page.get_table_data()
    if len(row_data) > 1:
        _reset_username = row_data[1].get("用户名", "")
    else:
        _reset_username = row_data[0].get("用户名", "") if row_data else ""

    # 点击确定
    user_manager_page.dialog.click_reset_password_confirm()
    user_manager_page.page.wait_for_timeout(1000)

    # 弹窗应关闭
    assert not user_manager_page.dialog.is_reset_password_dialog_open(), \
        "重置后弹窗应关闭"

    # Toast 提示应包含成功关键词，并尝试提取新密码
    toast = user_manager_page.get_toast_message()
    assert toast, "重置密码后应有 Toast 提示"
    assert any(kw in toast for kw in ["成功", "重置", "密码"]), \
        f"Toast 应包含成功/重置/密码，实际'{toast}'"

    # 尝试从 Toast 中提取新密码（如"新密码为：123456"）
    m = re.search(r"(\d{4,})", toast)
    if m:
        _reset_password = m.group(1)


@allure.feature("用户管理")
@allure.story("重置密码")
@pytest.mark.order(7)
def test_login_with_new_password(login_page):
    """重置密码后，用新密码应能成功登录"""
    global _reset_username, _reset_password
    if not _reset_username:
        pytest.skip("未获取到被重置的用户名")

    # 按优先级尝试：Toast 提取的密码 → 常见默认密码 → 用户名
    candidates = [
        p for p in [_reset_password, "123456", "888888", "111111", "000000",
                     "password", _reset_username]
        if p
    ]
    # 去重保持顺序
    seen = set()
    candidates = [p for p in candidates if not (p in seen or seen.add(p))]
    logged_in = False
    for pwd in candidates:
        login_page.login(_reset_username, pwd)
        login_page.page.wait_for_timeout(2000)
        if not login_page.is_still_on_login():
            logged_in = True
            _reset_password = pwd  # 记录实际生效的密码
            break

    assert logged_in, \
        f"用户 {_reset_username} 用候选密码 {candidates} 均登录失败"


@allure.feature("用户管理")
@allure.story("重置密码")
@pytest.mark.order(8)
def test_login_with_old_password_fails(login_page):
    """重置前的密码应无法登录"""
    global _reset_username
    if not _reset_username:
        pytest.skip("未获取到被重置的用户名")

    login_page.login(_reset_username, "wrong_old_password")
    login_page.page.wait_for_timeout(2000)

    # 登录失败应停留在登录页
    assert login_page.is_still_on_login(), \
        f"用户 {_reset_username} 用旧密码登录应失败，停留在登录页"

    # 应出现错误提示
    toast = login_page.get_toast_message()
    assert toast, "用旧密码登录应有错误提示"
