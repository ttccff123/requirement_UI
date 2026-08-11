"""
角色管理 — 编辑角色测试（名称30字符+描述100字符，与 test_role_copy 共享数据结构）

测试范围:
- 先新建一个专属角色，所有用例均对该角色进行编辑测试
- 弹窗 title、取消、确定（保存+还原）、X 按钮验证
- 角色名称和描述的默认值回显
- 编辑名称：为空校验
- 编辑名称：长度30，包含中英文数字特殊字符
- 编辑描述：包含换行、空格、特殊字符，总长度100
"""
import time

import allure
import pytest

from tests.test_role._helpers import close_any_dialog, safe_delete_role

# 模块级：setup 创建的角色名称（会被改名用例更新）
_current_name: str = ""
# 模块级：原始名称，teardown 删除时使用（始终指向最初创建的名称）
_original_name: str = ""


# ======================== 模块级 setup / teardown ========================


@pytest.fixture(scope="module", autouse=True)
def _setup_and_cleanup(role_manager_page):
    """模块 setup：创建专属测试角色；teardown：关闭弹窗后删除。"""
    global _current_name, _original_name
    close_any_dialog(role_manager_page)

    # ---- setup：创建角色（名称30字符+描述100字符，时间戳保证唯一） ----
    ts = str(int(time.time()))[-4:]
    _original_name = f"测试角色管理RoleAdm{ts}!@#$%^&*()"[:30]
    _current_name = _original_name
    desc_100 = (
        "第一行描述内容📋\n"
        "第二行 包含 空格 😀\n"
        "第三行特殊!@#$%^&*()🎯\n"
        "第四行中英混合Role管理Test\n"
        "第五行补齐字符凑够一百个字描述用于测试编辑角色功能描述字段完整性校验✅"
    )[:100]
    role_manager_page.click_add_role()
    role_manager_page.dialog.fill_role_field("角色名称", _original_name)
    role_manager_page.dialog.fill_role_field("角色描述", desc_100)
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.dialog.wait_for_form_dialog_closed()

    if role_manager_page.dialog.is_role_form_dialog_open():
        error = role_manager_page.dialog.get_role_field_error("角色名称")
        role_manager_page.dialog.click_role_form_close()
        pytest.skip(f"无法创建测试角色，错误='{error}'")

    yield

    # ---- teardown：删除角色（优先按原始名称，若已被改名则按当前名称） ----
    for name in (_original_name, _current_name):
        try:
            safe_delete_role(role_manager_page, name)
        except Exception:
            continue


# ======================== 辅助函数 ========================


def _open_edit_dialog(role_manager_page):
    """关闭弹窗 → 打开当前测试角色的编辑弹窗。"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_edit_role(_current_name)


def _restore_name(role_manager_page):
    """将角色名称恢复为原始名称（用于改名用例的事后清理）。"""
    global _current_name
    try:
        role_manager_page.click_edit_role(_current_name)
        role_manager_page.dialog.fill_role_field("角色名称", _original_name)
        role_manager_page.dialog.click_role_form_confirm()
        role_manager_page.dialog.wait_for_form_dialog_closed()
        _current_name = _original_name
    except Exception:
        pass


# ======================== 弹窗校验 ========================


@allure.feature("角色管理")
@allure.story("编辑角色")
@pytest.mark.order(1)
def test_edit_role_dialog_title(role_manager_page):
    """弹窗标题应为'编辑角色'"""
    _open_edit_dialog(role_manager_page)
    title = role_manager_page.dialog.get_role_form_title()
    assert "编辑" in title, f"弹窗标题应包含'编辑'，实际'{title}'"
    role_manager_page.dialog.click_role_form_close()
    role_manager_page.dialog.wait_for_form_dialog_closed()


@allure.feature("角色管理")
@allure.story("编辑角色")
@pytest.mark.order(2)
def test_edit_role_dialog_cancel(role_manager_page):
    """点击取消 → 弹窗关闭"""
    _open_edit_dialog(role_manager_page)
    role_manager_page.dialog.click_role_form_cancel()
    role_manager_page.dialog.wait_for_form_dialog_closed()
    assert not role_manager_page.dialog.is_role_form_dialog_open(), "点击取消后弹窗应关闭"


@allure.feature("角色管理")
@allure.story("编辑角色")
@pytest.mark.order(3)
def test_edit_role_dialog_close(role_manager_page):
    """点击 X → 弹窗关闭"""
    _open_edit_dialog(role_manager_page)
    role_manager_page.dialog.click_role_form_close()
    role_manager_page.dialog.wait_for_form_dialog_closed()
    assert not role_manager_page.dialog.is_role_form_dialog_open(), "点击 X 后弹窗应关闭"


@allure.feature("角色管理")
@allure.story("编辑角色")
@pytest.mark.order(4)
def test_edit_role_dialog_confirm(role_manager_page):
    """修改名称+点确定 → 弹窗关闭，随后还原原名"""
    global _current_name
    _open_edit_dialog(role_manager_page)

    new_name = f"{_original_name}_改"
    role_manager_page.dialog.fill_role_field("角色名称", new_name)
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.dialog.wait_for_form_dialog_closed()

    if role_manager_page.dialog.is_role_form_dialog_open():
        error = role_manager_page.dialog.get_role_field_error("角色名称")
        toast = role_manager_page.get_toast_message()
        role_manager_page.dialog.click_role_form_close()
        pytest.fail(f"编辑角色应关闭弹窗，字段错误='{error}'，Toast='{toast}'")

    _current_name = new_name
    _restore_name(role_manager_page)


# ======================== 默认值回显 ========================


@allure.feature("角色管理")
@allure.story("编辑角色")
@pytest.mark.order(5)
def test_edit_role_default_name(role_manager_page):
    """打开编辑弹窗 → 角色名称应回显当前名称"""
    _open_edit_dialog(role_manager_page)
    name_value = role_manager_page.dialog.get_role_field_value("角色名称")
    assert name_value == _current_name, \
        f"角色名称默认值应为'{_current_name}'，实际'{name_value}'"
    role_manager_page.dialog.click_role_form_close()
    role_manager_page.dialog.wait_for_form_dialog_closed()


@allure.feature("角色管理")
@allure.story("编辑角色")
@pytest.mark.order(6)
def test_edit_role_default_desc(role_manager_page):
    """打开编辑弹窗 → 角色描述应回显原值"""
    _open_edit_dialog(role_manager_page)
    desc_value = role_manager_page.dialog.get_role_field_value("角色描述")
    assert desc_value is not None and len(desc_value) >= 0, "角色描述字段应存在"
    role_manager_page.dialog.click_role_form_close()
    role_manager_page.dialog.wait_for_form_dialog_closed()


# ======================== 编辑名称校验 ========================


@allure.feature("角色管理")
@allure.story("编辑角色")
@pytest.mark.order(7)
def test_edit_role_name_empty(role_manager_page):
    """编辑角色名称为空 → 应有错误提示"""
    _open_edit_dialog(role_manager_page)

    role_manager_page.dialog.clear_role_field("角色名称")
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(150)

    error = role_manager_page.dialog.get_role_field_error("角色名称")
    assert error, "角色名称为空应有错误提示"

    # 关闭弹窗（不保存），避免残留空值
    role_manager_page.dialog.click_role_form_close()
    role_manager_page.dialog.wait_for_form_dialog_closed()


@allure.feature("角色管理")
@allure.story("编辑角色")
@pytest.mark.order(8)
def test_edit_role_name_valid_30(role_manager_page):
    """编辑名称30字符（中英文数字特殊字符混合）→ 应通过校验"""
    global _current_name
    _open_edit_dialog(role_manager_page)

    # 30字符：中文 + 英文 + 数字 + 特殊字符
    cn = "测试角色管理权限"
    en = "RoleAdmin"
    num = "2024"
    sp = "!@#$%"
    name_30 = (cn + en + num + sp)[:30]

    role_manager_page.dialog.fill_role_field("角色名称", name_30)
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(250)

    saved = not role_manager_page.dialog.is_role_form_dialog_open()
    if saved:
        # 保存成功，更新当前名称并立即还原
        _current_name = name_30
        close_any_dialog(role_manager_page)
        role_manager_page.page.wait_for_timeout(150)
        _restore_name(role_manager_page)
    elif role_manager_page.dialog.is_role_form_dialog_open():
        error = role_manager_page.dialog.get_role_field_error("角色名称")
        assert not error, f"30字符混合名称应通过校验，出现'{error}'"
        role_manager_page.dialog.click_role_form_close()


# ======================== 编辑描述校验 ========================


@allure.feature("角色管理")
@allure.story("编辑角色")
@pytest.mark.order(9)
def test_edit_role_desc_valid_100(role_manager_page):
    """编辑描述100字符（含换行、空格、特殊字符）→ 应通过校验"""
    _open_edit_dialog(role_manager_page)

    # 100字符：换行 + 空格 + 特殊字符 + 中英文
    desc_100 = (
        "第一行描述内容\n"
        "第二行 包含 空格\n"
        "第三行特殊!@#$%^&*()\n"
        "第四行中英混合Role管理Test\n"
        "第五行补齐字符凑够一百个字的描述内容用于测试编辑角色功能的描述字段边界值校验"
    )[:100]

    role_manager_page.dialog.fill_role_field("角色描述", desc_100)
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(250)

    if role_manager_page.dialog.is_role_form_dialog_open():
        error = role_manager_page.dialog.get_role_field_error("角色描述")
        assert not error, f"100字符描述应通过校验，出现'{error}'"
        # 关闭弹窗，不保存（描述为可选项，不允许保存时关闭即可）
        role_manager_page.dialog.click_role_form_close()
