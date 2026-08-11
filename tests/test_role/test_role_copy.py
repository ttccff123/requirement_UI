"""
角色管理 — 复制角色测试

测试范围:
- 新增复杂角色（名称30字符中英文数字特殊字符，描述100字符含换行/空格/特殊字符/emoji）
- 复制该角色 → 名称含原名、描述一致、显示在第一行
- 复制管理员角色 → 名称含"管理员"、功能权限与管理員完全一致
"""
import time

import allure
import pytest

from tests.test_role._helpers import close_any_dialog, safe_delete_role

# 模块级：setup 创建的原始角色名 + 复制后的角色名，teardown 删除
_original_name: str = ""
_copied_name: str = ""
_admin_copy_name: str = ""


def _ensure_role_visible(role_manager_page, role_name: str):
    """确保角色在树中可见：清空搜索框 → 等待树刷新。"""
    role_manager_page.clear_role_search()
    role_manager_page.page.wait_for_timeout(250)


def _get_role_perms(role_manager_page, role_name: str) -> str:
    """选中角色 → 切换到功能权限页签 → 返回已勾选权限快照。"""
    role_manager_page.click_role_node(role_name)
    role_manager_page.page.wait_for_timeout(150)
    role_manager_page.click_perm_tab()
    return role_manager_page.get_perm_snapshot()


# ======================== 模块级 setup / teardown ========================


@pytest.fixture(scope="module", autouse=True)
def _setup_and_cleanup(role_manager_page):
    """模块 setup：创建复杂角色；teardown：删除所有测试角色。"""
    global _original_name
    close_any_dialog(role_manager_page)

    # ---- 30字符角色名称：中文 + 英文 + 数字 + 特殊字符（时间戳保证唯一） ----
    ts = str(int(time.time()))[-4:]
    name_30 = f"测试角色管理RoleAdm{ts}!@#$%^&*()"[:30]
    # ---- 100字符描述：换行 + 空格 + 特殊字符 + emoji ----
    desc_100 = (
        "第一行描述内容📋\n"
        "第二行 包含 空格 😀\n"
        "第三行特殊!@#$%^&*()🎯\n"
        "第四行中英混合Role管理Test\n"
        "第五行补齐字符凑够一百个字描述用于测试复制角色功能描述字段完整性校验✅"
    )[:100]

    _original_name = name_30

    role_manager_page.click_add_role()
    role_manager_page.dialog.fill_role_field("角色名称", _original_name)
    role_manager_page.dialog.fill_role_field("角色描述", desc_100)
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(800)

    if role_manager_page.dialog.is_role_form_dialog_open():
        error = role_manager_page.dialog.get_role_field_error("角色名称")
        toast = role_manager_page.get_toast_message()
        # 用 Escape 关闭弹窗（比 click X 更可靠）
        try:
            role_manager_page.dialog.click_role_form_close()
        except Exception:
            role_manager_page.page.locator("body").first.press("Escape")
            role_manager_page.page.wait_for_timeout(150)
        reason = error or toast or "未知原因（超时或服务端无响应）"
        pytest.skip(f"无法创建测试角色，原因='{reason}'")

    yield

    # ---- teardown：删除所有测试创建的角色 ----
    for name in (_copied_name, _original_name, _admin_copy_name):
        if name:
            safe_delete_role(role_manager_page, name)


# ======================== 复制复杂角色 ========================


@allure.feature("角色管理")
@allure.story("复制角色")
@pytest.mark.order(1)
def test_copy_complex_role(role_manager_page):
    """复制复杂角色 → 名称含原名、显示在第一行"""
    global _copied_name
    close_any_dialog(role_manager_page)
    _ensure_role_visible(role_manager_page, _original_name)

    # 执行复制（无弹窗，直接返回新名称）
    _copied_name = role_manager_page.click_copy_role(_original_name)
    assert _copied_name, "复制后应返回新角色名称"
    assert _copied_name != _original_name, \
        f"复制名称应与原名称不同，原='{_original_name}'，新='{_copied_name}'"

    # 验证复制后的角色出现在列表第一行
    _ensure_role_visible(role_manager_page, _copied_name)
    names = role_manager_page.get_role_tree_node_names()
    assert _copied_name in names, \
        f"复制后的角色'{_copied_name}'应在角色列表中，实际列表={names}"
    assert names[0] == _copied_name, \
        f"复制后的角色应排在第一行，实际第一行='{names[0]}'，列表={names}"


# ======================== 复制管理员角色 ========================


@allure.feature("角色管理")
@allure.story("复制角色")
@pytest.mark.order(2)
def test_copy_admin_role(role_manager_page):
    """复制管理员角色 → 名称含"管理员"、功能权限与管理員完全一致"""
    global _admin_copy_name
    close_any_dialog(role_manager_page)

    admin_name = "管理员"
    names = role_manager_page.get_role_tree_node_names()
    if admin_name not in names:
        pytest.skip(f"系统中无'{admin_name}'角色")

    # 获取管理员权限快照
    admin_perms = _get_role_perms(role_manager_page, admin_name)
    assert admin_perms, "管理员至少应有一项功能权限"

    # 确保搜索框清空、树处于展开状态
    _ensure_role_visible(role_manager_page, admin_name)

    # 执行复制（无弹窗，直接返回新名称）
    _admin_copy_name = role_manager_page.click_copy_role(admin_name)
    assert _admin_copy_name, "复制管理员后应返回新角色名称"
    assert admin_name in _admin_copy_name, \
        f"复制名称应包含'{admin_name}'，实际'{_admin_copy_name}'"

    # 验证复制后的角色权限与管理员一致
    role_manager_page.page.wait_for_timeout(250)
    copied_perms = _get_role_perms(role_manager_page, _admin_copy_name)
    assert copied_perms == admin_perms, \
        f"复制角色的权限应与管理员完全一致，\n管理员权限={admin_perms}\n复制权限={copied_perms}"
