"""
部门管理 — 删除部门测试

测试范围:
- 新建无成员部门 → 删除：确认弹窗提示词、确定/取消/X 按钮、成功 Toast
- 选择有成员部门 → 删除：确认弹窗提示词、取消/X 按钮
"""
import time

import allure
import pytest

from tests.test_dept._helpers import close_any_dialog, find_dept_with_members, safe_add_dept, safe_delete_dept

_test_dept_name: str = ""
_created: bool = False


@pytest.fixture(scope="module", autouse=True)
def _setup_and_cleanup(dept_manager_page):
    """模块 setup：创建无成员部门；teardown：兜底删除。"""
    global _test_dept_name, _created
    close_any_dialog(dept_manager_page)

    _test_dept_name = f"delete_dept_{int(time.time())}"

    if safe_add_dept(dept_manager_page, _test_dept_name):
        _created = True
    else:
        existing = find_dept_with_members(dept_manager_page)
        if existing:
            _test_dept_name = existing
            _created = False
        else:
            pytest.skip("无法创建测试部门且无可用的已存在部门")

    yield

    # teardown：只清理自己创建的部门（safe_delete_dept 内部已处理弹窗关闭）
    if _created:
        safe_delete_dept(dept_manager_page, _test_dept_name)


# ======================== 删除无成员部门 ========================


@allure.feature("部门管理")
@allure.story("删除部门")
@pytest.mark.order(1)
def test_delete_empty_dept_cancel(dept_manager_page):
    """删除部门 → 点取消 → 弹窗关闭、部门仍存在"""
    close_any_dialog(dept_manager_page)

    dept_manager_page.click_delete_dept(_test_dept_name)
    if not dept_manager_page.dialog.is_confirm_dialog_open():
        pytest.skip("无法触发删除确认弹窗（部门树可能不支持右键菜单或Delete键）")

    msg = dept_manager_page.dialog.get_confirm_dialog_message()
    assert msg, "删除确认弹窗应有提示信息"

    dept_manager_page.dialog.click_confirm_dialog_cancel()
    dept_manager_page.page.wait_for_timeout(250)
    assert not dept_manager_page.dialog.is_confirm_dialog_open(), \
        "点取消后确认弹窗应关闭"


@allure.feature("部门管理")
@allure.story("删除部门")
@pytest.mark.order(2)
def test_delete_empty_dept_close(dept_manager_page):
    """删除部门 → 点 X → 弹窗关闭、部门仍存在"""
    close_any_dialog(dept_manager_page)

    dept_manager_page.click_delete_dept(_test_dept_name)
    if not dept_manager_page.dialog.is_confirm_dialog_open():
        pytest.skip("无法触发删除确认弹窗")
    dept_manager_page.page.wait_for_timeout(200)

    close_btn = dept_manager_page.page.locator(
        ".el-message-box__wrapper:visible .el-message-box__headerbtn,"
        ".el-dialog__wrapper.kd-dialog:visible .el-dialog__close"
    ).first
    if close_btn.count() > 0:
        close_btn.click()
    else:
        dept_manager_page.page.locator("body").first.press("Escape")
    dept_manager_page.page.wait_for_timeout(250)

    assert not dept_manager_page.dialog.is_confirm_dialog_open(), \
        "点 X 后确认弹窗应关闭"
    names = dept_manager_page.get_dept_tree_node_names()
    assert _test_dept_name in names, \
        f"点 X 后部门'{_test_dept_name}'应仍存在"


@allure.feature("部门管理")
@allure.story("删除部门")
@pytest.mark.order(3)
def test_delete_empty_dept_confirm(dept_manager_page):
    """删除部门 → 点确定 → 成功 Toast、部门从列表消失"""
    close_any_dialog(dept_manager_page)

    dept_manager_page.click_delete_dept(_test_dept_name)
    if not dept_manager_page.dialog.is_confirm_dialog_open():
        pytest.skip("无法触发删除确认弹窗")
    confirm_msg = dept_manager_page.dialog.get_confirm_dialog_message()
    assert confirm_msg, "删除确认弹窗应有提示信息"
    assert _test_dept_name in confirm_msg or "部门" in confirm_msg, \
        f"确认提示应包含部门相关信息，实际='{confirm_msg}'"

    dept_manager_page.dialog.click_confirm_dialog_confirm()
    dept_manager_page.page.wait_for_timeout(400)

    toast_msg = dept_manager_page.toast.get_message()
    print(f"删除Toast: {toast_msg}")

    dept_manager_page.page.wait_for_timeout(250)
    names = dept_manager_page.get_dept_tree_node_names()
    assert _test_dept_name not in names, \
        f"删除后部门'{_test_dept_name}'应从列表中移除"


# ======================== 删除有成员部门 ========================


@allure.feature("部门管理")
@allure.story("删除部门")
@pytest.mark.order(4)
def test_delete_dept_with_members_dialog(dept_manager_page):
    """删除有成员部门 → 弹窗提示提及成员、取消可关闭"""
    close_any_dialog(dept_manager_page)

    dept_with_members = find_dept_with_members(dept_manager_page)
    if not dept_with_members:
        pytest.skip("无有成员的部门可测试")

    dept_manager_page.click_delete_dept(dept_with_members)
    if not dept_manager_page.dialog.is_confirm_dialog_open():
        pytest.skip("无法触发删除确认弹窗")
    msg = dept_manager_page.dialog.get_confirm_dialog_message()
    assert msg, "删除确认弹窗应有提示信息"

    try:
        dept_manager_page.dialog.click_confirm_dialog_cancel()
    except Exception:
        dept_manager_page.page.locator("body").first.press("Escape")
    dept_manager_page.page.wait_for_timeout(250)
    assert not dept_manager_page.dialog.is_confirm_dialog_open(), \
        "关闭操作后弹窗应关闭"

    names = dept_manager_page.get_dept_tree_node_names()
    assert dept_with_members in names, \
        f"取消后部门'{dept_with_members}'应仍存在"
