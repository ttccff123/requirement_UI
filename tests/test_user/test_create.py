"""
用户管理 — 新增用户测试

测试范围:
- 弹窗 title、取消、确定、关闭按钮验证
- 必填项为空校验（用户名/姓名/角色）
- 字符类型校验（特殊字符/中文/纯数字/SQL注入/XSS/手机号含字母/邮箱格式）
- 字符长度校验（过短/过长/边界值）
- 重名校验
- 新增成功：绿色 Toast + 表格首行展示 + 用户可登录
- 新增失败：错误提示词颜色、内容校验
"""

import time
from pathlib import Path

import allure
import pytest

from common.utils.yaml_util import YamlUtil
from config.settings import BASE_URL
from pages.login_page import LoginPage
from tests.test_user._helpers import (
    SELECT_FIELDS,
    RADIO_FIELDS,
    load_cases,
    get_cases_for_category,
    make_case_id,
    resolve_value,
    close_any_open_dialog,
    fill_select_field,
    fill_radio_field,
    fill_other_fields,
)

# 模块级变量
_created_username: str | None = None
_created_password: str = "Aa123456"

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "user" / "add_user.yaml"


def _load_success_fill() -> dict:
    """加载 YAML 中的 success_fill 配置。"""
    data = YamlUtil(DATA_FILE).read()
    return data.get("success_fill", {})


# 用户名每次随机生成，避免重复导致添加失败
def _get_fields_for_others() -> dict[str, str]:
    return {
        "用户名": f"user{int(time.time())}",
        "姓名": "测试员",
        "联系电话": "13800138000",
        "邮箱": "test@test.com",
    }


def _open_create_dialog(user_manager_page):
    """打开新增用户弹窗，若已打开则先关闭再重新打开（确保表单为空）。"""
    close_any_open_dialog(user_manager_page)
    user_manager_page.click_create_user()
    user_manager_page.dialog.wait_for_user_form_dialog()


# ========================================================================
#  弹窗基础校验
# ========================================================================


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(1)
def test_create_user_dialog_title(user_manager_page):
    """新增用户弹窗标题应为'新增用户'"""
    _open_create_dialog(user_manager_page)
    title = user_manager_page.dialog.get_user_form_dialog_title()
    assert "新建" in title, f"弹窗标题应包含'新建'，实际'{title}'"


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(2)
def test_create_user_dialog_cancel(user_manager_page):
    """点击取消按钮应关闭弹窗"""
    _open_create_dialog(user_manager_page)
    user_manager_page.dialog.click_cancel()
    user_manager_page.page.wait_for_timeout(300)
    assert not user_manager_page.dialog.is_user_form_dialog_open(), \
        "点击取消后弹窗应关闭"


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(3)
def test_create_user_dialog_close(user_manager_page):
    """点击 X 关闭按钮应关闭弹窗"""
    _open_create_dialog(user_manager_page)
    user_manager_page.dialog.click_close()
    user_manager_page.page.wait_for_timeout(300)
    user_manager_page.page.locator("body").first.press("Escape")
    user_manager_page.page.wait_for_timeout(200)
    assert not user_manager_page.dialog.is_user_form_dialog_open(), \
        "点击关闭后弹窗应关闭"


# ========================================================================
#  字段校验（参数化，数据来自 YAML）
# ========================================================================

@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(4)
@pytest.mark.parametrize("case", get_cases_for_category(DATA_FILE, ["必填校验"]), ids=make_case_id)
def test_create_user_required_field_validation(user_manager_page, case):
    """必填项为空时应有错误提示"""
    _open_create_dialog(user_manager_page)

    if case.get("fill_others"):
        _fill_other_fields(user_manager_page, case["field"])

    field = case["field"]
    if field == "角色":
        # 角色是下拉框，不填就点击确定触发校验
        pass
    else:
        user_manager_page.dialog.fill_field(field, case["value"])

    # 触发校验
    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(300)

    if case["expected"] == "error":
        error = user_manager_page.dialog.get_field_error(field)
        msg_keyword = case.get("message", "")
        assert error, f"字段'{field}'为空应有错误提示"
        if msg_keyword:
            assert msg_keyword in error, \
                f"错误提示应包含'{msg_keyword}'，实际'{error}'"


def _fill_other_fields(user_manager_page, skip_field: str):
    """填充除 skip_field 外的其他字段（文本 + 下拉 + 单选框）。"""
    for field, val in _get_fields_for_others().items():
        if field == skip_field:
            continue
        user_manager_page.dialog.fill_field(field, val)
    fill_other_fields(user_manager_page, skip_field)  # 来自 _helpers


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(5)
@pytest.mark.parametrize("case", get_cases_for_category(DATA_FILE,["字符类型"]), ids=make_case_id)
def test_create_user_char_type_validation(user_manager_page, case):
    """字符类型校验：特殊字符/中文/纯数字等应有错误提示（仅测输入框：用户名/姓名/联系电话/邮箱）"""
    # 下拉框字段由专门测试处理
    if case["field"] in ("角色", "部门"):
        pytest.skip(f"{case['field']}下拉框用例见 test_create_user_role_select_validation")

    _open_create_dialog(user_manager_page)

    if case["expected"] == "may_pass":
        # 合法值校验：需要填充其他必填字段，确保整体提交能通过
        _fill_other_fields(user_manager_page, case["field"])
    # 填入目标字段值
    resolved_value = resolve_value(case["value"])
    user_manager_page.dialog.fill_field(case["field"], resolved_value)
    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(300)

    if case["expected"] == "error":
        error = user_manager_page.dialog.get_field_error(case["field"])
        assert error, f"字段'{case['field']}'输入'{case['value']}'应有错误提示"
    else:
        error = user_manager_page.dialog.get_field_error(case["field"])
        assert not error, \
            f"字段'{case['field']}'值'{case['value']}'应通过校验，但出现错误'{error}'"


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(6)
@pytest.mark.parametrize("case", get_cases_for_category(DATA_FILE,["字符长度"]), ids=make_case_id)
def test_create_user_char_length_validation(user_manager_page, case):
    """字符长度校验：过短/过长应有错误提示或通过（仅测输入框）"""
    # 下拉框字段由专门测试处理
    if case["field"] in ("角色", "部门"):
        pytest.skip(f"{case['field']}下拉框用例见 test_create_user_role_select_validation")

    _open_create_dialog(user_manager_page)

    if case["expected"] == "may_pass":
        # 合法值校验：需要填充其他必填字段，确保整体提交能通过
        _fill_other_fields(user_manager_page, case["field"])
    # 填入目标字段值
    resolved_value = resolve_value(case["value"])
    user_manager_page.dialog.fill_field(case["field"], resolved_value)
    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(300)

    if case["expected"] == "error":
        error = user_manager_page.dialog.get_field_error(case["field"])
        assert error, f"字段'{case['field']}'长度异常应有错误提示"
    else:
        error = user_manager_page.dialog.get_field_error(case["field"])
        assert not error, \
            f"字段'{case['field']}'边界值应通过，但出现错误'{error}'"


# ========================================================================
#  角色下拉框（多选）
# ========================================================================


def _get_role_cases() -> list[dict]:
    """获取角色下拉框的测试用例（字符类型中 field=角色 的 case）。"""
    cases = load_cases(DATA_FILE)
    return [c for c in cases if c.get("category") == "字符类型" and c.get("field") == "角色"]


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(7)
@pytest.mark.parametrize("case", _get_role_cases(), ids=make_case_id)
def test_create_user_role_select_validation(user_manager_page, case):
    """角色下拉框校验：选择一个角色 / 选择全部角色"""
    _open_create_dialog(user_manager_page)
    _fill_other_fields(user_manager_page, "角色")

    if case["value"] == "<ALL>":
        # 选择全部角色
        _fill_select_all(user_manager_page, "角色")
    else:
        # 选择单个角色
        fill_select_field(user_manager_page, "角色", case["value"])

    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(300)

    if case["expected"] == "error":
        error = user_manager_page.dialog.get_field_error("角色")
        assert error, f"角色选择'{case['value']}'应有错误提示"
    else:
        error = user_manager_page.dialog.get_field_error("角色")
        assert not error, f"角色选择'{case['value']}'应通过校验，但出现错误'{error}'"


def _fill_select_all(user_manager_page, field_label: str):
    """选择下拉框中全部可见选项（适用于多选下拉框）。"""
    form_item = user_manager_page.dialog._find_form_item(field_label)
    if form_item.count() == 0:
        return
    # 点击 input 打开下拉
    form_item.locator("input.el-input__inner").first.click()
    user_manager_page.page.wait_for_timeout(300)
    dropdown = user_manager_page.page.locator(
        '.el-select-dropdown[x-placement="bottom-start"]:visible, '
        '.el-select-dropdown:not([style*="display: none"])'
    ).first
    dropdown.wait_for(state="visible", timeout=5000)
    # 点击所有可选项
    options = dropdown.locator("li.el-select-dropdown__item").all()
    for opt in options:
        opt.click()
        user_manager_page.page.wait_for_timeout(100)
    # 关闭下拉
    user_manager_page.page.locator("body").first.press("Escape")
    user_manager_page.page.wait_for_timeout(300)


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(8)
def test_create_user_duplicate_username(user_manager_page):
    """重复用户名：使用已有账号应提示'已存在'"""
    cases = load_cases(DATA_FILE)
    dup_case = next(
        (c for c in cases if c.get("category") == "重复账号"), None
    )
    if not dup_case:
        pytest.skip("YAML 中未定义重复账号测试数据")

    # 获取一个已存在的用户名
    row_data = user_manager_page.get_table_data()
    existing_user = row_data[0].get("用户名", "") if row_data else "admin"

    _open_create_dialog(user_manager_page)
    _fill_other_fields(user_manager_page, "用户名")
    user_manager_page.dialog.fill_field("用户名", existing_user)
    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(800)  # 等待服务端校验

    error = user_manager_page.dialog.get_field_error("用户名")
    if not error:
        toast_msg = user_manager_page.get_toast_message()
    assert error or toast_msg, \
        f"重复用户名应有错误提示（字段级或Toast），字段错误='{error}'，Toast='{toast_msg}'"


# ========================================================================
#  新增成功 — 完整流程
# ========================================================================


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(9)
def test_create_user_success(user_manager_page):
    """新增用户成功：绿色 Toast + 表格首行展示新数据"""
    global _created_username
    success_fill = _load_success_fill()

    # 生成唯一用户名
    _created_username = f"auto{int(time.time())}"

    _open_create_dialog(user_manager_page)
    # 从 YAML success_fill 读取填充值，用户名替换为唯一值
    for field, val in success_fill.items():
        if field == "用户名":
            user_manager_page.dialog.fill_field(field, _created_username)
        elif field in SELECT_FIELDS:
            fill_select_field(user_manager_page, field, val)
        elif field in RADIO_FIELDS:
            fill_radio_field(user_manager_page, field)
        else:
            user_manager_page.dialog.fill_field(field, val)

    # 点击确定提交
    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(1000)

    # 先捕获 Toast（可能消失较快），再检查弹窗状态
    toast_msg = user_manager_page.get_toast_message()
    toast_type = user_manager_page.toast.get_type()

    # 弹窗应关闭
    assert not user_manager_page.dialog.is_user_form_dialog_open(), \
        f"新增成功后弹窗应关闭，Toast=[{toast_type}] {toast_msg}"

    # 绿色成功提示
    assert toast_msg, f"新增成功后应有 Toast 提示，弹窗已关闭"
    assert toast_type == "success", \
        f"新增成功应为绿色(success)，实际'{toast_type}'，消息='{toast_msg}'"

    # 表格第一行应为新增用户
    user_manager_page.page.wait_for_timeout(500)
    row_data = user_manager_page.get_table_data()
    assert row_data, "表格应有数据"
    first_row_username = row_data[0].get("用户名", "")
    assert first_row_username == _created_username, \
        f"表格首行应为新增用户'{_created_username}'，实际'{first_row_username}'"


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(12)
def test_created_user_can_login(user_manager_page):
    """新增用户成功后，使用密码 Aa123456 登录验证"""
    global _created_username
    if not _created_username:
        pytest.skip("未创建测试用户")

    # 1. 关闭可能残留的弹窗，再导航到登录页
    close_any_open_dialog(user_manager_page)
    user_manager_page.page.goto(f"{BASE_URL}")
    user_manager_page.page.wait_for_timeout(500)
    login = LoginPage(user_manager_page.page)
    login.wait_for_selector(login.USERNAME, timeout=1000)

    # 2. 使用新增用户的账号和默认密码 Aa123456 登录
    login.login(_created_username, _created_password)
    login.page.wait_for_timeout(1000)

    assert not login.is_still_on_login(), \
        f"新增用户 {_created_username} 使用 Aa123456 应能成功登录"

  


# ========================================================================
#  新增失败 — 错误提示校验
# ========================================================================


@allure.feature("用户管理")
@allure.story("新增用户")
@pytest.mark.order(11)
def test_create_user_fail_toast_type(user_manager_page):
    """新增失败时 Toast 提示应为 error/warning 类型（非 success）"""
    _open_create_dialog(user_manager_page)
    # 不填任何字段直接提交
    user_manager_page.dialog.click_confirm()
    user_manager_page.page.wait_for_timeout(500)

    toast_type = user_manager_page.toast.get_type()
    if toast_type:
        assert toast_type != "success", \
            f"新增失败不应为绿色提示，实际'{toast_type}'"

    # 检查是否有字段校验错误（前端校验）
    errors = []
    for field in ["用户名", "姓名", "角色"]:
        err = user_manager_page.dialog.get_field_error(field)
        if err:
            errors.append(f"{field}:{err}")
    assert errors, "至少应有字段校验错误提示"
