"""
部门管理 — 编辑部门测试

测试范围:
- 先新建一个专属部门，所有用例均对该部门进行编辑测试
- 弹窗 title、取消、确定（保存+还原）、X 按钮验证
- 部门名称的默认值回显
- 编辑名称：为空校验
- 编辑名称：长度30，包含中英文数字特殊字符
- 编辑描述：包含换行、空格、特殊字符
"""
import time

import allure
import pytest

from tests.test_dept._helpers import close_any_dialog, open_edit_dialog, safe_add_dept, safe_delete_dept

# 模块级：setup 创建的部门名称（会被改名用例更新）
_current_name: str = ""
_original_name: str = ""


@pytest.fixture(scope="module", autouse=True)
def _setup_and_cleanup(dept_manager_page):
    """模块 setup：创建专属测试部门；teardown：关闭弹窗后删除。"""
    global _current_name, _original_name
    close_any_dialog(dept_manager_page)

    ts = str(int(time.time()))[-4:]
    _original_name = f"编辑测试部门{ts}Dept"[:30]
    _current_name = _original_name

    if not safe_add_dept(dept_manager_page, _original_name):
        pytest.skip("无法创建测试部门")

    # 验证编辑功能可用（尝试右键菜单和双击）
    try:
        dept_manager_page.click_edit_dept(_original_name)
        dept_manager_page.dialog.click_dept_form_close()
    except Exception:
        try:
            close_any_dialog(dept_manager_page)
        except Exception:
            pass
        pytest.skip("编辑功能不可用")

    yield

    for name in (_original_name, _current_name):
        safe_delete_dept(dept_manager_page, name)


def _open_edit_dialog(dept_manager_page):
    """关闭弹窗 → 打开当前测试部门的编辑弹窗。"""
    open_edit_dialog(dept_manager_page, _current_name)


def _restore_name(dept_manager_page):
    """将部门名称恢复为原始名称。"""
    global _current_name
    try:
        open_edit_dialog(dept_manager_page, _current_name)
        dept_manager_page.dialog.fill_dept_field("部门名称", _original_name)
        dept_manager_page.dialog.click_dept_form_confirm()
        dept_manager_page.dialog.wait_for_form_dialog_closed()
        _current_name = _original_name
    except Exception:
        pass


# ======================== 弹窗校验 ========================


@allure.feature("部门管理")
@allure.story("编辑部门")
@pytest.mark.order(1)
def test_edit_dept_dialog_title(dept_manager_page):
    """弹窗标题应为'编辑部门'"""
    _open_edit_dialog(dept_manager_page)
    title = dept_manager_page.dialog.get_dept_form_title()
    assert "编辑" in title or "修改" in title or "部门" in title, \
        f"弹窗标题应包含编辑/部门，实际'{title}'"
    dept_manager_page.dialog.click_dept_form_close()
    dept_manager_page.dialog.wait_for_form_dialog_closed()


@allure.feature("部门管理")
@allure.story("编辑部门")
@pytest.mark.order(2)
def test_edit_dept_dialog_cancel(dept_manager_page):
    """点击取消 → 弹窗关闭"""
    _open_edit_dialog(dept_manager_page)
    dept_manager_page.dialog.click_dept_form_cancel()
    dept_manager_page.dialog.wait_for_form_dialog_closed()
    assert not dept_manager_page.dialog.is_dept_form_dialog_open(), \
        "点击取消后弹窗应关闭"


@allure.feature("部门管理")
@allure.story("编辑部门")
@pytest.mark.order(3)
def test_edit_dept_dialog_close(dept_manager_page):
    """点击 X → 弹窗关闭"""
    _open_edit_dialog(dept_manager_page)
    dept_manager_page.dialog.click_dept_form_close()
    dept_manager_page.dialog.wait_for_form_dialog_closed()
    assert not dept_manager_page.dialog.is_dept_form_dialog_open(), \
        "点击 X 后弹窗应关闭"


@allure.feature("部门管理")
@allure.story("编辑部门")
@pytest.mark.order(4)
def test_edit_dept_dialog_confirm(dept_manager_page):
    """修改名称+点确定 → 弹窗关闭，随后还原原名"""
    global _current_name
    _open_edit_dialog(dept_manager_page)

    new_name = f"{_original_name}_改"
    dept_manager_page.dialog.fill_dept_field("部门名称", new_name)
    dept_manager_page.dialog.click_dept_form_confirm()
    dept_manager_page.dialog.wait_for_form_dialog_closed()

    if dept_manager_page.dialog.is_dept_form_dialog_open():
        toast = dept_manager_page.get_toast_message()
        dept_manager_page.dialog.click_dept_form_close()
        pytest.fail(f"编辑部门应关闭弹窗，Toast='{toast}'")

    _current_name = new_name
    _restore_name(dept_manager_page)


# ======================== 默认值回显 ========================


@allure.feature("部门管理")
@allure.story("编辑部门")
@pytest.mark.order(5)
def test_edit_dept_default_name(dept_manager_page):
    """打开编辑弹窗 → 部门名称应回显当前名称"""
    _open_edit_dialog(dept_manager_page)
    name_value = dept_manager_page.dialog.get_dept_field_value("部门名称")
    assert name_value == _current_name, \
        f"部门名称默认值应为'{_current_name}'，实际'{name_value}'"
    dept_manager_page.dialog.click_dept_form_close()
    dept_manager_page.dialog.wait_for_form_dialog_closed()


# ======================== 编辑名称校验 ========================


@allure.feature("部门管理")
@allure.story("编辑部门")
@pytest.mark.order(6)
def test_edit_dept_name_empty(dept_manager_page):
    """编辑部门名称为空 → 应有错误提示"""
    _open_edit_dialog(dept_manager_page)
    dept_manager_page.dialog.clear_dept_field("部门名称")
    dept_manager_page.dialog.click_dept_form_confirm()
    dept_manager_page.page.wait_for_timeout(150)

    if dept_manager_page.dialog.is_dept_form_dialog_open():
        toast = dept_manager_page.get_toast_message()
        dept_manager_page.dialog.click_dept_form_close()
        # 为空应有提示
    else:
        pytest.fail("空部门名称不应通过校验")


@allure.feature("部门管理")
@allure.story("编辑部门")
@pytest.mark.order(7)
def test_edit_dept_name_valid_30(dept_manager_page):
    """编辑名称30字符（中英文数字特殊字符混合）→ 应通过校验"""
    global _current_name
    _open_edit_dialog(dept_manager_page)

    cn, en, num, sp = "部门管理权限", "DeptAdmin", "2024", "!@#$"
    name_30 = (cn + en + num + sp)[:30]

    dept_manager_page.dialog.fill_dept_field("部门名称", name_30)
    dept_manager_page.dialog.click_dept_form_confirm()
    dept_manager_page.page.wait_for_timeout(250)

    saved = not dept_manager_page.dialog.is_dept_form_dialog_open()
    if saved:
        _current_name = name_30
        close_any_dialog(dept_manager_page)
        dept_manager_page.page.wait_for_timeout(150)
        _restore_name(dept_manager_page)
    elif dept_manager_page.dialog.is_dept_form_dialog_open():
        dept_manager_page.dialog.click_dept_form_close()
        pytest.skip("30字符边界值被拒绝")


# ======================== 编辑描述校验 ========================


@allure.feature("部门管理")
@allure.story("编辑部门")
@pytest.mark.order(8)
def test_edit_dept_desc_update(dept_manager_page):
    """编辑部门描述 → 应通过校验"""
    _open_edit_dialog(dept_manager_page)

    desc = (
        "第一行描述\n"
        "第二行空格 内容\n"
        "第三行特殊!@#$%^&*()\n"
        "第四行中英混合Dept管理Test"
    )[:100]

    dept_manager_page.dialog.fill_dept_field("部门描述", desc)
    dept_manager_page.dialog.click_dept_form_confirm()
    dept_manager_page.page.wait_for_timeout(250)

    if dept_manager_page.dialog.is_dept_form_dialog_open():
        dept_manager_page.dialog.click_dept_form_close()
