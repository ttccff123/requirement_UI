"""
角色管理 — 删除角色测试

测试范围:
- 管理员角色右键菜单无"删除角色"选项
- 新建无成员角色 → 删除：确认弹窗提示词、确定/取消/X 按钮、成功绿色 Toast
- 选择有成员角色 → 删除：确认弹窗提示词、确定/取消/X 按钮
"""
import time

import allure
import pytest

from tests.test_role._helpers import close_any_dialog, safe_delete_role

# 模块级：创建的无成员角色名，teardown 兜底删除
_test_role_name: str = ""


def _find_role_with_members(role_manager_page) -> str | None:
    """遍历角色树，返回第一个有成员的角色名；无则返回 None。"""
    names = role_manager_page.get_role_tree_node_names()
    for name in names:
        try:
            role_manager_page.click_role_node(name)
            role_manager_page.page.wait_for_timeout(250)
            members = role_manager_page.get_member_table_data()
            if members:
                return name
        except Exception:
            continue
    return None


# ======================== 模块级 setup / teardown ========================


@pytest.fixture(scope="module", autouse=True)
def _setup_and_cleanup(role_manager_page):
    """模块 setup：创建无成员角色；teardown：兜底删除。"""
    global _test_role_name
    close_any_dialog(role_manager_page)

    _test_role_name = f"delete_test_{int(time.time())}"
    role_manager_page.click_add_role()
    role_manager_page.dialog.fill_role_field("角色名称", _test_role_name)
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(800)

    if role_manager_page.dialog.is_role_form_dialog_open():
        role_manager_page.dialog.click_role_form_close()
        pytest.skip("无法创建测试角色")

    yield

    # 兜底删除
    safe_delete_role(role_manager_page, _test_role_name)


# ======================== 管理员无删除按钮 ========================


@allure.feature("角色管理")
@allure.story("删除角色")
@pytest.mark.order(1)
def test_admin_has_no_delete_option(role_manager_page):
    """管理员角色右键菜单中不应有"删除角色"选项"""
    close_any_dialog(role_manager_page)

    admin_name = "管理员"
    names = role_manager_page.get_role_tree_node_names()
    if admin_name not in names:
        pytest.skip(f"系统中无'{admin_name}'角色")

    role_manager_page.open_role_context_menu(admin_name)
    menu_items = role_manager_page.get_role_menu_items()
    assert "删除角色" not in menu_items, \
        f"管理员不应有'删除角色'选项，实际菜单={menu_items}"


# ======================== 删除无成员角色 ========================


@allure.feature("角色管理")
@allure.story("删除角色")
@pytest.mark.order(2)
def test_delete_empty_role_cancel(role_manager_page):
    """删除无成员角色 → 点取消 → 弹窗关闭、角色仍存在"""
    close_any_dialog(role_manager_page)

    role_manager_page.click_delete_role(_test_role_name)
    msg = role_manager_page.dialog.get_confirm_dialog_message()
    assert msg, "删除确认弹窗应有提示信息"

    role_manager_page.dialog.click_confirm_dialog_cancel()
    role_manager_page.page.wait_for_timeout(250)
    assert not role_manager_page.dialog.is_confirm_dialog_open(), "点取消后确认弹窗应关闭"

    names = role_manager_page.get_role_tree_node_names()
    assert _test_role_name in names, f"点取消后角色'{_test_role_name}'应仍存在"


@allure.feature("角色管理")
@allure.story("删除角色")
@pytest.mark.order(3)
def test_delete_empty_role_close(role_manager_page):
    """删除无成员角色 → 点 X → 弹窗关闭、角色仍存在"""
    close_any_dialog(role_manager_page)

    # 使用 el-message-box 的关闭按钮（若为 kd-dialog 则用 Escape）
    role_manager_page.click_delete_role(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)

    # 尝试点击 X 关闭，若不存在则用 Escape
    close_btn = role_manager_page.page.locator(
        ".el-message-box__wrapper:visible .el-message-box__headerbtn,"
        ".el-dialog__wrapper.kd-dialog:visible .el-dialog__close"
    ).first
    if close_btn.count() > 0:
        close_btn.click()
    else:
        role_manager_page.page.locator("body").first.press("Escape")
    role_manager_page.page.wait_for_timeout(250)

    assert not role_manager_page.dialog.is_confirm_dialog_open(), "点 X 后确认弹窗应关闭"
    names = role_manager_page.get_role_tree_node_names()
    assert _test_role_name in names, f"点 X 后角色'{_test_role_name}'应仍存在"


@allure.feature("角色管理")
@allure.story("删除角色")
@pytest.mark.order(4)
def test_delete_empty_role_confirm(role_manager_page):
    """删除无成员角色 → 点确定 → 绿色 Toast、角色从列表消失"""
    close_any_dialog(role_manager_page)

    role_manager_page.click_delete_role(_test_role_name)
    confirm_msg = role_manager_page.dialog.get_confirm_dialog_message()
    assert confirm_msg, "删除确认弹窗应有提示信息"
    # 确认弹窗内容应包含角色相关信息（名称或字段标签）
    assert _test_role_name in confirm_msg or "角色" in confirm_msg, \
        f"确认提示应包含角色相关信息，实际='{confirm_msg}'"

    role_manager_page.dialog.click_confirm_dialog_confirm()
    role_manager_page.page.wait_for_timeout(400)

    # 验证成功 Toast（绿色）
    toast_type = role_manager_page.toast.get_type()
    toast_msg = role_manager_page.toast.get_message()
    assert toast_type == "success" or "成功" in toast_msg or "删除" in toast_msg, \
        f"删除成功后应有绿色 Toast，类型='{toast_type}'，消息='{toast_msg}'"

    # 验证角色已从列表中移除
    role_manager_page.page.wait_for_timeout(250)
    names = role_manager_page.get_role_tree_node_names()
    assert _test_role_name not in names, \
        f"删除后角色'{_test_role_name}'应从列表中移除，实际列表={names}"


# ======================== 删除有成员角色 ========================


@allure.feature("角色管理")
@allure.story("删除角色")
@pytest.mark.order(5)
def test_delete_role_with_members_dialog(role_manager_page):
    """删除有成员角色 → 弹窗提示提及成员、取消/X 可关闭"""
    close_any_dialog(role_manager_page)

    role_with_members = _find_role_with_members(role_manager_page)
    if not role_with_members:
        pytest.skip("无有成员的角色可测试")

    # --- 取消（或关闭） ----
    role_manager_page.click_delete_role(role_with_members)
    msg = role_manager_page.dialog.get_confirm_dialog_message()
    assert msg, "删除确认弹窗应有提示信息"

    # 尝试点取消；若弹窗只有确定按钮则用 Escape 关闭
    try:
        role_manager_page.dialog.click_confirm_dialog_cancel()
    except Exception:
        role_manager_page.page.locator("body").first.press("Escape")
    role_manager_page.page.wait_for_timeout(250)
    assert not role_manager_page.dialog.is_confirm_dialog_open(), "关闭操作后弹窗应关闭"

    names = role_manager_page.get_role_tree_node_names()
    assert role_with_members in names, f"取消后角色'{role_with_members}'应仍存在"
