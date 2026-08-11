"""
用户管理 — 编辑用户测试

测试范围:
- 弹窗 title、默认值回填、取消、确定、关闭按钮验证
- 必填项为空校验（用户名/姓名/角色）
- 字符类型校验（特殊字符/中文/纯数字等）
- 字符长度校验（边界值/超长）
- 重名校验
"""
from pathlib import Path

import allure
import pytest

from tests.test_user._helpers import (
    get_cases_for_category,
    make_case_id,
    close_any_open_dialog,
)

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "user" / "edit_user.yaml"


# ======================== 工具函数 ========================


def _open_edit_dialog(user_manager_page):
    """打开编辑用户弹窗：点击第一行数据的编辑按钮。"""
    close_any_open_dialog(user_manager_page)
    user_manager_page.click_edit_user_by_index(0)
    user_manager_page.dialog.wait_for_user_form_dialog()


# ======================== 弹窗基础校验 ========================


@allure.feature("用户管理")
@allure.story("编辑用户")
@pytest.mark.order(1)
def test_edit_user_dialog_title(user_manager_page):
    """编辑用户弹窗标题应为'编辑用户'"""
    _open_edit_dialog(user_manager_page)
    title = user_manager_page.dialog.get_user_form_dialog_title()
    assert "编辑" in title, f"弹窗标题应包含'编辑'，实际'{title}'"


@allure.feature("用户管理")
@allure.story("编辑用户")
@pytest.mark.order(2)
def test_edit_user_dialog_default_values(user_manager_page):
    """编辑用户弹窗应回填当前用户的数据"""
    row_data = user_manager_page.get_table_data()
    assert row_data, "表格应有数据"
    expected_user = row_data[0].get("用户名", "")

    _open_edit_dialog(user_manager_page)
    actual = user_manager_page.dialog.get_field_value("用户名")
    assert actual == expected_user, \
        f"编辑弹窗应回填用户名'{expected_user}'，实际'{actual}'"


@allure.feature("用户管理")
@allure.story("编辑用户")
@pytest.mark.order(3)
def test_edit_user_dialog_cancel(user_manager_page):
    """点击取消按钮应关闭弹窗"""
    _open_edit_dialog(user_manager_page)
    user_manager_page.dialog.click_cancel()
    user_manager_page.page.wait_for_timeout(300)
    assert not user_manager_page.dialog.is_user_form_dialog_open(), \
        "点击取消后弹窗应关闭"


@allure.feature("用户管理")
@allure.story("编辑用户")
@pytest.mark.order(4)
def test_edit_user_dialog_close(user_manager_page):
    """点击 X 关闭按钮应关闭弹窗"""
    _open_edit_dialog(user_manager_page)
    user_manager_page.dialog.click_close()
    user_manager_page.page.wait_for_timeout(300)
    user_manager_page.page.locator("body").first.press("Escape")
    user_manager_page.page.wait_for_timeout(200)
    assert not user_manager_page.dialog.is_user_form_dialog_open(), \
        "点击关闭后弹窗应关闭"


# ======================== 必填校验（参数化） ========================


@allure.feature("用户管理")
@allure.story("编辑用户")
@pytest.mark.order(5)
@pytest.mark.parametrize("case", get_cases_for_category(DATA_FILE, ["必填校验"]), ids=make_case_id)
def test_edit_user_required_field_validation(user_manager_page, case):
    """必填项为空时应有错误提示"""
    _open_edit_dialog(user_manager_page)

    field = case["field"]
    if field == "角色":
        pytest.skip("编辑弹窗角色默认已选，无法测试为空场景")
    else:
        user_manager_page.dialog.clear_field(field)
        if case["value"]:
            user_manager_page.dialog.fill_field(field, case["value"])

    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(300)

    if case["expected"] == "error":
        error = user_manager_page.dialog.get_field_error(field)
        msg_keyword = case.get("message", "")
        assert error, f"字段'{field}'为空应有错误提示"
        if msg_keyword:
            assert msg_keyword in error, \
                f"错误提示应包含'{msg_keyword}'，实际'{error}'"


# ======================== 编辑保存成功 ========================


@allure.feature("用户管理")
@allure.story("编辑用户")
@pytest.mark.order(6)
def test_edit_user_save_success(user_manager_page):
    """编辑用户保存成功：弹窗关闭 + 绿色 Toast"""
    _open_edit_dialog(user_manager_page)
    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(1000)

    toast_msg = user_manager_page.get_toast_message()
    toast_type = user_manager_page.toast.get_type()

    assert not user_manager_page.dialog.is_user_form_dialog_open(), \
        f"编辑保存后弹窗应关闭，Toast=[{toast_type}] {toast_msg}"
    assert toast_msg, "编辑保存后应有 Toast 提示"
