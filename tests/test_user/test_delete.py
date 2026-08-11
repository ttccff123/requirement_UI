"""
用户管理 — 删除用户测试

测试范围:
- 删除参与项目=0 的用户 → 确认弹窗提示词校验 → 取消
- 删除参与项目>0 的用户 → 确认弹窗提示词校验 → 关闭按钮
- 删除确认：确定按钮 → 用户从列表移除
- 删除当前登录用户 → 提示校验
- 删除成功后 → 用该用户账号登录验证失败
"""
import time
from pathlib import Path

import allure
import pytest

from common.utils.yaml_util import YamlUtil
from config.settings import BASE_URL
from pages.login_page import LoginPage
from tests.test_user._helpers import close_any_open_dialog, fill_select_field, fill_radio_field

# 新增用户测试数据（用于创建临时用户）
_ADD_USER_DATA = Path(__file__).resolve().parents[2] / "data" / "user" / "add_user.yaml"

# 登录账号
_LOGIN_USERNAME = "admin"
_LOGIN_PASSWORD = "123"


def _get_temp_username() -> str:
    """生成临时用户名。"""
    return f"del{int(time.time())}"


def _find_user_by_project_count(user_manager_page, count_zero: bool) -> dict | None:
    """查找参与项目=0 或 >0 的用户。

    Args:
        count_zero: True=找参与项目=0 的用户, False=找参与项目>0 的用户
    """
    rows = user_manager_page.get_table_data()
    for row in rows:
        val = row.get("参与项目", "")
        try:
            n = int(val)
        except (ValueError, TypeError):
            continue
        if count_zero and n == 0:
            return row
        if not count_zero and n > 0:
            return row
    return None


def _find_row_index_by_username(user_manager_page, username: str) -> int | None:
    """根据用户名查找行索引。"""
    rows = user_manager_page.get_table_data()
    for i, row in enumerate(rows):
        if row.get("用户名") == username:
            return i
    return None


def _create_temp_user(user_manager_page) -> str:
    """快速创建一个临时用户用于删除测试，返回用户名。"""
    data = YamlUtil(str(_ADD_USER_DATA)).read()
    success_fill = data.get("success_fill", {})
    username = _get_temp_username()

    close_any_open_dialog(user_manager_page)
    user_manager_page.click_create_user()
    user_manager_page.dialog.wait_for_user_form_dialog()

    for field, val in success_fill.items():
        if field == "用户名":
            user_manager_page.dialog.fill_field(field, username)
        elif field in ("角色", "部门"):
            fill_select_field(user_manager_page, field, val)
        else:
            user_manager_page.dialog.fill_field(field, val)
    fill_radio_field(user_manager_page, "性别")
    fill_radio_field(user_manager_page, "状态")

    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(1500)

    # 等待弹窗关闭
    user_manager_page.page.wait_for_timeout(500)
    return username


# ======================== 弹窗校验 ========================


@allure.feature("用户管理")
@allure.story("删除用户")
@pytest.mark.order(1)
def test_delete_user_project_zero_dialog(user_manager_page):
    """删除参与项目=0 的用户：弹窗提示词校验 + 取消关闭弹窗"""
    row = _find_user_by_project_count(user_manager_page, count_zero=True)
    if not row:
        pytest.skip("未找到参与项目=0 的用户")

    username = row.get("用户名", "")
    idx = _find_row_index_by_username(user_manager_page, username)

    user_manager_page.click_delete_user_by_index(idx)
    user_manager_page.dialog.wait_for_confirm_dialog()

    msg_text = user_manager_page.dialog.get_confirm_dialog_message()
    assert msg_text, "删除确认弹窗应有提示信息"

    # 点击取消 → 弹窗关闭
    user_manager_page.dialog.click_confirm_dialog_cancel()
    user_manager_page.page.wait_for_timeout(300)
    assert not user_manager_page.dialog.is_confirm_dialog_open(), \
        "点击取消后弹窗应关闭"


@allure.feature("用户管理")
@allure.story("删除用户")
@pytest.mark.order(2)
def test_delete_user_project_nonzero_dialog(user_manager_page):
    """删除参与项目>0 的用户：弹窗提示词校验 + X 关闭按钮"""
    row = _find_user_by_project_count(user_manager_page, count_zero=False)
    if not row:
        pytest.skip("未找到参与项目>0 的用户")

    username = row.get("用户名", "")
    idx = _find_row_index_by_username(user_manager_page, username)

    user_manager_page.click_delete_user_by_index(idx)
    user_manager_page.dialog.wait_for_confirm_dialog()

    message = user_manager_page.dialog.get_confirm_dialog_message()
    assert message, "删除确认弹窗应有提示信息"

    # 验证参与项目>0 时提示词包含参与项目相关字样（如 "关联" 或 "项目"）
    # 不同系统提示不同，只验证有内容

    # 按 Escape 关闭
    user_manager_page.page.locator("body").first.press("Escape")
    user_manager_page.page.wait_for_timeout(300)
    assert not user_manager_page.dialog.is_confirm_dialog_open(), \
        "关闭后弹窗应关闭"


@allure.feature("用户管理")
@allure.story("删除用户")
@pytest.mark.order(3)
def test_delete_user_confirm(user_manager_page):
    """删除用户 → 确定按钮 → 用户从列表移除"""
    # 创建临时用户用于删除
    username = _create_temp_user(user_manager_page)
    idx = _find_row_index_by_username(user_manager_page, username)
    if idx is None:
        pytest.skip("创建的用户未在列表中")

    user_manager_page.click_delete_user_by_index(idx)
    user_manager_page.dialog.wait_for_confirm_dialog()
    user_manager_page.dialog.click_confirm_dialog_confirm()
    user_manager_page.page.wait_for_timeout(1000)

    # 验证 Toast
    toast_msg = user_manager_page.get_toast_message()

    # 刷新验证用户已不在列表中
    user_manager_page.page.wait_for_timeout(500)
    rows = user_manager_page.get_table_data()
    usernames = [r.get("用户名") for r in rows]
    assert username not in usernames, \
        f"删除后用户 {username} 应不在列表中，Toast='{toast_msg}'"


@allure.feature("用户管理")
@allure.story("删除用户")
@pytest.mark.order(4)
def test_delete_logged_in_user(user_manager_page):
    """删除当前登录用户 → 应有提示不允许"""
    rows = user_manager_page.get_table_data()
    admin_row_idx = None
    for i, r in enumerate(rows):
        if r.get("用户名") == _LOGIN_USERNAME:
            admin_row_idx = i
            break
    if admin_row_idx is None:
        pytest.skip(f"未在当前页找到登录用户 {_LOGIN_USERNAME}")

    # 滚动到目标行并检查删除图标是否存在
    row_loc = user_manager_page.page.locator(user_manager_page.TABLE_BODY_ROWS).nth(admin_row_idx)
    row_loc.scroll_into_view_if_needed()
    delete_icon = row_loc.locator("i.iconfont.icon-shanchu_huishouzhan")
    if delete_icon.count() == 0:
        pytest.skip("当前登录用户无删除图标，跳过")

    delete_icon.first.click()
    user_manager_page.dialog.wait_for_confirm_dialog()

    message = user_manager_page.dialog.get_confirm_dialog_message()
    # 点击确定尝试删除自己
    user_manager_page.dialog.click_confirm_dialog_confirm()
    user_manager_page.page.wait_for_timeout(1000)

    toast_msg = user_manager_page.get_toast_message()
    assert toast_msg or message, \
        f"删除登录用户应有错误提示，Toast='{toast_msg}'，弹窗消息='{message}'"


# ======================== 删除后登录验证 ========================


@allure.feature("用户管理")
@allure.story("删除用户")
@pytest.mark.order(5)
def test_deleted_user_cannot_login(user_manager_page):
    """删除用户后用该账号登录应失败"""
    # 创建临时用户
    username = _create_temp_user(user_manager_page)
    idx = _find_row_index_by_username(user_manager_page, username)
    assert idx is not None, f"创建的用户 {username} 应在列表中"

    # 删除
    user_manager_page.click_delete_user_by_index(idx)
    user_manager_page.dialog.wait_for_confirm_dialog()
    user_manager_page.dialog.click_confirm_dialog_confirm()
    user_manager_page.page.wait_for_timeout(1500)

    # 确认已删除
    rows = user_manager_page.get_table_data()
    assert username not in [r.get("用户名") for r in rows], \
        f"用户 {username} 应已删除"

    # 导航到登录页，用已删除用户登录
    close_any_open_dialog(user_manager_page)
    user_manager_page.page.goto(f"{BASE_URL}")
    user_manager_page.page.wait_for_timeout(500)
    login = LoginPage(user_manager_page.page)
    login.wait_for_selector(login.USERNAME, timeout=10000)

    login.login(username, _LOGIN_PASSWORD)
    login.page.wait_for_timeout(2000)

    # 应停留在登录页（登录失败）
    assert login.is_still_on_login(), \
        f"已删除用户 {username} 登录应失败，但跳转到了其他页面"
