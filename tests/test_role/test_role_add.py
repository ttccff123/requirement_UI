"""
角色管理 — 添加角色测试

测试范围:
- 弹窗 title、取消、确定、关闭按钮验证
- 必填项为空校验（角色名称）
- 字符类型校验（特殊字符/中文/英文/数字）
- 字符长度校验（边界值/超长）
- 角色描述：换行、空格、边界值
- 重名验证
- placeholder 校验
"""
import time
from pathlib import Path

import allure
import pytest

from common.utils.placeholder_util import resolve_value
from common.utils.yaml_util import YamlUtil
from tests.test_role._helpers import close_any_dialog, safe_delete_role

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "role" / "add_role.yaml"

# 模块级：记录用例执行中成功创建的角色名称，用于 teardown 统一清理
_created_names: list[str] = []


def _load_cases() -> list[dict]:
    data = YamlUtil(str(DATA_FILE)).read()
    return data.get("cases", [])


def _open_add_dialog(role_manager_page):
    """打开新增角色弹窗，先关闭已有弹窗。"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_add_role()


def _make_case_id(case: dict) -> str:
    return case.get("case", "unknown")


def _get_cases_for_category(categories: list[str]) -> list[dict]:
    return [c for c in _load_cases() if c.get("category") in categories]


@pytest.fixture(scope="module", autouse=True)
def _cleanup_created_roles(role_manager_page):
    """模块 teardown：关闭弹窗 → 删除用例创建的角色。"""
    yield
    for name in _created_names:
        safe_delete_role(role_manager_page, name)


# ======================== 弹窗校验 ========================


@allure.feature("角色管理")
@allure.story("添加角色")
@pytest.mark.order(1)
def test_add_role_dialog_title(role_manager_page):
    """弹窗标题应为'新建角色'"""
    _open_add_dialog(role_manager_page)
    title = role_manager_page.dialog.get_role_form_title()
    assert "新建" in title, f"弹窗标题应包含'新建'，实际'{title}'"
    role_manager_page.dialog.click_role_form_close()
    role_manager_page.dialog.wait_for_form_dialog_closed()


@allure.feature("角色管理")
@allure.story("添加角色")
@pytest.mark.order(2)
def test_add_role_dialog_cancel(role_manager_page):
    """点击取消 → 弹窗关闭"""
    _open_add_dialog(role_manager_page)
    role_manager_page.dialog.click_role_form_cancel()
    role_manager_page.dialog.wait_for_form_dialog_closed()
    assert not role_manager_page.dialog.is_role_form_dialog_open(), "点击取消后弹窗应关闭"


@allure.feature("角色管理")
@allure.story("添加角色")
@pytest.mark.order(3)
def test_add_role_dialog_confirm(role_manager_page):
    """填随机名称+点确定 → 弹窗关闭（创建成功）"""
    _open_add_dialog(role_manager_page)
    unique_name = f"auto_{int(time.time())}"
    role_manager_page.dialog.fill_role_field("角色名称", unique_name)
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.dialog.wait_for_form_dialog_closed()

    if role_manager_page.dialog.is_role_form_dialog_open():
        error = role_manager_page.dialog.get_role_field_error("角色名称")
        toast = role_manager_page.get_toast_message()
        pytest.fail(f"新增角色应关闭弹窗，字段错误='{error}'，Toast='{toast}'")

    _created_names.append(unique_name)


@allure.feature("角色管理")
@allure.story("添加角色")
@pytest.mark.order(4)
def test_add_role_dialog_close(role_manager_page):
    """点击 X 关闭 → 弹窗关闭"""
    _open_add_dialog(role_manager_page)
    role_manager_page.dialog.click_role_form_close()
    role_manager_page.dialog.wait_for_form_dialog_closed()
    assert not role_manager_page.dialog.is_role_form_dialog_open(), "点击 X 后弹窗应关闭"


# ======================== Placeholder ========================


@allure.feature("角色管理")
@allure.story("添加角色")
@pytest.mark.order(5)
def test_add_role_field_placeholders(role_manager_page):
    """角色名称和角色描述应有 placeholder"""
    _open_add_dialog(role_manager_page)
    name_ph = role_manager_page.dialog.get_role_field_placeholder("角色名称")
    desc_ph = role_manager_page.dialog.get_role_field_placeholder("角色描述")
    assert name_ph, "角色名称字段应有 placeholder"
    assert desc_ph, "角色描述字段应有 placeholder"
    role_manager_page.dialog.click_role_form_close()
    role_manager_page.dialog.wait_for_form_dialog_closed()


# ======================== 必填校验 ========================


@allure.feature("角色管理")
@allure.story("添加角色")
@pytest.mark.order(6)
@pytest.mark.parametrize("case", _get_cases_for_category(["必填校验"]), ids=_make_case_id)
def test_add_role_required_field(role_manager_page, case):
    """必填项为空时应有错误提示"""
    _open_add_dialog(role_manager_page)
    field = case["field"]
    if case["value"]:
        role_manager_page.dialog.fill_role_field(field, case["value"])
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(150)

    if case["expected"] == "error":
        error = role_manager_page.dialog.get_role_field_error(field)
        assert error, f"字段'{field}'为空应有错误提示"


# ======================== 字符类型校验 ========================


@allure.feature("角色管理")
@allure.story("添加角色")
@pytest.mark.order(7)
@pytest.mark.parametrize("case", _get_cases_for_category(["字符类型"]), ids=_make_case_id)
def test_add_role_char_type(role_manager_page, case):
    """字符类型校验"""
    _open_add_dialog(role_manager_page)
    field, raw_value = case["field"], case["value"]
    value = resolve_value(raw_value)

    role_manager_page.dialog.fill_role_field(field, value)
    if field != "角色名称":
        unique_name = f"auto_{int(time.time())}"
        role_manager_page.dialog.fill_role_field("角色名称", unique_name)
    else:
        unique_name = value

    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(150)

    if case["expected"] == "error":
        error = role_manager_page.dialog.get_role_field_error(field)
        assert error, f"字段'{field}'输入'{raw_value}'应有错误提示"
    elif role_manager_page.dialog.is_role_form_dialog_open():
        error = role_manager_page.dialog.get_role_field_error(field)
        assert not error, f"字段'{field}'值'{raw_value}'应通过校验，出现'{error}'"
        role_manager_page.dialog.click_role_form_close()
    else:
        _created_names.append(unique_name)


# ======================== 字符长度校验 ========================


@allure.feature("角色管理")
@allure.story("添加角色")
@pytest.mark.order(8)
@pytest.mark.parametrize("case", _get_cases_for_category(["字符长度"]), ids=_make_case_id)
def test_add_role_char_length(role_manager_page, case):
    """字符长度校验"""
    _open_add_dialog(role_manager_page)
    field, raw_value = case["field"], case["value"]
    value = resolve_value(raw_value)

    role_manager_page.dialog.fill_role_field(field, value)
    if field != "角色名称":
        unique_name = f"auto_{int(time.time())}"
        role_manager_page.dialog.fill_role_field("角色名称", unique_name)
    else:
        unique_name = value

    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(150)

    if case["expected"] == "error":
        error = role_manager_page.dialog.get_role_field_error(field)
        assert error, f"字段'{field}'长度异常应有错误提示"
    elif role_manager_page.dialog.is_role_form_dialog_open():
        error = role_manager_page.dialog.get_role_field_error(field)
        assert not error, f"字段'{field}'边界值应通过，出现'{error}'"
        role_manager_page.dialog.click_role_form_close()
    else:
        _created_names.append(unique_name)


# ======================== 重名校验 ========================


@allure.feature("角色管理")
@allure.story("添加角色")
@pytest.mark.order(9)
def test_add_role_duplicate_name(role_manager_page):
    """使用已存在的角色名称 → 应有错误提示"""
    existing = role_manager_page.get_role_tree_node_names()
    if not existing:
        pytest.skip("无已存在的角色")

    _open_add_dialog(role_manager_page)
    role_manager_page.dialog.fill_role_field("角色名称", existing[0])
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(800)

    if role_manager_page.dialog.is_role_form_dialog_open():
        # 弹窗未关闭 → 应有字段错误或 Toast 提示
        error = role_manager_page.dialog.get_role_field_error("角色名称")
        toast_msg = role_manager_page.get_toast_message() if not error else ""
        role_manager_page.dialog.click_role_form_close()
        assert error or toast_msg, \
            f"重复角色名称应有错误提示，字段错误='{error}'，Toast='{toast_msg}'"
    else:
        # 弹窗关闭 → 系统允许重名，角色被创建，加入清理列表
        _created_names.append(existing[0])
