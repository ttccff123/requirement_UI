"""新建方案弹窗测试

数据文件：data/scheme/scheme_add.yaml
"""
import os
from datetime import datetime
from pathlib import Path

import allure
import pytest
import yaml
from playwright.sync_api import expect

from config.settings import BASE_URL
from pages.scheme_manager.myScheme.scheme_add import SchemeAddPage

HOME_URL = BASE_URL
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "scheme" / "scheme_add.yaml"

# 模块级加载测试数据
with open(DATA_PATH, "r", encoding="utf-8") as f:
    _TEST_DATA = yaml.safe_load(f)
DIALOG = _TEST_DATA.get("dialog", {})
CASES = _TEST_DATA.get("cases", [])


# ==================== fixture ====================

@pytest.fixture(scope="function")
def dialog(page):
    """打开需求工具首页 → 新建 → 空白方案 → 返回 SchemeAddPage"""
    page.goto("about:blank", wait_until="domcontentloaded")
    page.goto(HOME_URL, wait_until="networkidle", timeout=30000)
    page.wait_for_selector(".sidebar-box:visible", timeout=10000)
    page.wait_for_timeout(1000)
    dlg = SchemeAddPage(page)
    dlg.open()
    return dlg


def _unique_name(prefix: str = "test") -> str:
    """生成唯一方案名"""
    return f"{prefix}_{datetime.now().strftime('%H%M%S%f')}"


# ==================== 辅助：按 category 筛选 cases ====================

def _cases_by_category(category: str):
    """返回指定 category 的用例列表"""
    return [c for c in CASES if c.get("category") == category]


def _resolve_value(value: str) -> str:
    """将 <PLACEHOLDER> 转为实际值（与 add_user / add_role 一致）"""
    if value == "<ALPHA_200>":
        return "A" * 200
    if value == "<ALPHA_B_200>":
        return "B" * 200
    return value


# ==================== 标题 ====================

@allure.feature("新建方案")
@allure.story("弹窗标题")
def test_dialog_title(dialog):
    """弹窗标题应为「新建方案」（数据来源 YAML）"""
    assert dialog.get_title() == DIALOG["title"]


# ==================== 关闭弹窗 ====================

@allure.feature("新建方案")
@allure.story("关闭弹窗")
def test_dialog_close_via_x_button(dialog):
    """点击右上角 X 关闭弹窗"""
    dialog.close()
    expect(dialog.page.locator(dialog.DIALOG_VISIBLE)).to_have_count(0, timeout=5000)


@allure.feature("新建方案")
@allure.story("关闭弹窗")
def test_dialog_close_via_cancel_button(dialog):
    """点击「取 消」按钮关闭弹窗"""
    dialog.cancel()
    expect(dialog.page.locator(dialog.DIALOG_VISIBLE)).to_have_count(0, timeout=5000)


# ==================== 必填字段校验 ====================

@allure.feature("新建方案")
@allure.story("必填校验")
def test_required_field_validation_empty_name(dialog):
    """空表单提交时出现「请输入方案名称」错误提示"""
    page = dialog.page
    dialog.confirm()
    assert dialog.is_dialog_visible(), "空提交后弹窗被关闭"
    error = page.locator(".el-form-item__error:visible").first
    expect(error).to_be_visible(timeout=3000)
    # expected message from YAML 里 message 为 "请输入方案名称"
    case = next(c for c in CASES if c.get("field") == "方案名称" and c.get("value") == "")
    assert case["message"] in error.inner_text()


@allure.feature("新建方案")
@allure.story("必填校验")
def test_required_fields_all_labeled(dialog):
    """方案名称、方案类型、方案标识均为必填项（字段名来源 YAML）"""
    page = dialog.page
    dialog_el = page.locator(dialog.DIALOG_VISIBLE).first
    case = next(c for c in CASES if c.get("check") == "required_labels")
    for label_text in case["required_fields"]:
        item = dialog_el.locator(".el-form-item").filter(has_text=label_text).first
        assert "is-required" in (item.get_attribute("class") or ""), (
            f"{label_text} 未标记为必填"
        )


# ==================== 字符类型（参数化驱动） ====================

@allure.feature("新建方案")
@allure.story("字符输入")
@pytest.mark.parametrize("case", _cases_by_category("字符类型"))
def test_input_accepts_characters(dialog, case):
    """方案名称/方案标识接受各类字符输入（数据来源 YAML）"""
    field = case["field"]
    value = case["value"]
    if field == "方案名称":
        dialog.fill_scheme_name(value)
        actual = dialog.get_scheme_name()
    elif field == "方案标识":
        dialog.fill_scheme_code(value)
        actual = dialog.get_scheme_code()
    else:
        pytest.skip(f"未知字段: {field}")
    assert actual == value, f"输入值「{value}」与读取值「{actual}」不一致"


# ==================== 字符长度（参数化驱动） ====================

@allure.feature("新建方案")
@allure.story("字符长度")
@pytest.mark.parametrize("case", _cases_by_category("字符长度"))
def test_scheme_length(dialog, case):
    """方案名称/方案标识字符长度校验（数据来源 YAML）"""
    field = case["field"]
    value = _resolve_value(case["value"])
    expected = case["expected"]

    if field == "方案名称":
        if value == "":
            # 空值 + 直接提交 → 应被拦截
            dialog.fill_scheme_name(value)
            dialog.confirm()
            assert dialog.is_dialog_visible(), "空名称提交后弹窗被关闭"
            return
        else:
            dialog.fill_scheme_name(value)
            actual_len = len(dialog.get_scheme_name())
    elif field == "方案标识":
        dialog.fill_scheme_code(value)
        actual_len = len(dialog.get_scheme_code())
    else:
        pytest.skip(f"未知字段: {field}")

    if expected == "may_pass":
        assert actual_len == len(value), f"长度应为 {len(value)}，实际: {actual_len}"


# ==================== 方案描述 ====================

@allure.feature("新建方案")
@allure.story("方案描述")
def test_description_preserves_spaces(dialog):
    """方案描述保留空格字符（期望值来源 YAML）"""
    case = next(c for c in CASES if c.get("check") == "preserves_spaces")
    text = case["value"]
    dialog.fill_scheme_desc(text)
    assert dialog.get_scheme_desc() == text


@allure.feature("新建方案")
@allure.story("方案描述")
def test_description_preserves_line_breaks(dialog):
    """方案描述保留换行符（期望值来源 YAML）"""
    case = next(c for c in CASES if c.get("check") == "preserves_line_breaks")
    text = case["value"]
    dialog.fill_scheme_desc(text)
    assert dialog.get_scheme_desc() == text


@allure.feature("新建方案")
@allure.story("方案描述")
def test_description_max_500_chars(dialog):
    """方案描述最多 500 个字符（maxlength 来源 YAML）"""
    textarea = dialog.get_scheme_desc_textarea()
    maxlen = textarea.get_attribute("maxlength")
    assert maxlen == str(DIALOG["desc_maxlength"]), (
        f"maxlength 应为 {DIALOG['desc_maxlength']}，实际: {maxlen}"
    )


# ==================== 方案类型 ====================

@allure.feature("新建方案")
@allure.story("方案类型")
def test_scheme_type_has_three_options(dialog):
    """方案类型下拉框有三个选项（选项值来源 YAML）"""
    options = dialog.get_scheme_type_options()
    assert options == DIALOG["scheme_types"], f"选项不符: {options}"


@allure.feature("新建方案")
@allure.story("方案类型")
def test_default_scheme_type_is_mission(dialog):
    """方案类型默认为指定值（默认值来源 YAML）"""
    assert dialog.get_scheme_type_value() == DIALOG["default_scheme_type"]


@allure.feature("新建方案")
@allure.story("方案类型")
@pytest.mark.parametrize("stype", DIALOG["scheme_types"])
def test_select_each_scheme_type(dialog, stype):
    """逐个选择每种方案类型并校验选中值（选项列表来源 YAML）"""
    dialog.select_scheme_type(stype)
    assert dialog.get_scheme_type_value() == stype


# ==================== 打开方案 ====================

@allure.feature("新建方案")
@allure.story("打开方案")
def test_open_scheme_checked_by_default(dialog):
    """「打开方案」默认勾选（期望值来源 YAML）"""
    assert dialog.is_open_scheme_checked() == DIALOG["open_scheme_default"]


@allure.feature("新建方案")
@allure.story("打开方案")
def test_open_scheme_toggle(dialog):
    """可切换「打开方案」勾选状态"""
    dialog.toggle_open_scheme(False)
    assert not dialog.is_open_scheme_checked(), "取消勾选失败"
    dialog.toggle_open_scheme(True)
    assert dialog.is_open_scheme_checked(), "重新勾选失败"


@allure.feature("新建方案")
@allure.story("打开方案")
def test_create_without_open_scheme_stays_on_page(dialog):
    """不勾选「打开方案」创建后停留在 requirementTool 页面（导航断言来源 YAML）"""
    case = next(c for c in CASES if c.get("check") == "create_without_open")
    dialog.toggle_open_scheme(False)
    name = _unique_name("nostay")
    dialog.fill_scheme_name(name)
    dialog.fill_scheme_code(name)
    dialog.confirm()
    dialog.page.wait_for_timeout(1500)
    assert case["navigate"] in dialog.page.url, (
        f"不应离开 {case['navigate']}，实际 URL: {dialog.page.url}"
    )


@allure.feature("新建方案")
@allure.story("打开方案")
def test_create_with_open_scheme_navigates_to_document(dialog):
    """勾选「打开方案」创建后跳转到文档编辑页面（导航断言来源 YAML）"""
    case = next(c for c in CASES if c.get("check") == "create_with_open")
    dialog.toggle_open_scheme(True)
    name = _unique_name("stay")
    dialog.fill_scheme_name(name)
    dialog.fill_scheme_code(name)
    dialog.confirm()
    dialog.page.wait_for_timeout(2000)
    assert case["navigate"] in dialog.page.url, (
        f"应跳转到 {case['navigate']} 页面，实际 URL: {dialog.page.url}"
    )


# ==================== 最近打开 ====================

@allure.feature("新建方案")
@allure.story("最近打开")
def test_created_scheme_appears_in_recent_open(dialog):
    """勾选「打开方案」创建后，方案出现在「最近打开」中"""
    page = dialog.page
    dialog.toggle_open_scheme(True)
    name = _unique_name("recent")
    dialog.fill_scheme_name(name)
    dialog.fill_scheme_code(name)
    dialog.confirm()
    page.wait_for_timeout(2000)

    page.goto(HOME_URL, wait_until="networkidle", timeout=30000)
    page.wait_for_selector(".sidebar-box:visible", timeout=10000)
    page.wait_for_timeout(1000)

    page.locator(".sidebar-box-content .menu-row").filter(has_text="最近打开").first.click(force=True)
    page.wait_for_timeout(1000)

    body_text = page.locator("body").inner_text()
    assert name in body_text, f"「{name}」未出现在最近打开页面中"


@allure.feature("新建方案")
@allure.story("最近打开")
def test_created_without_open_scheme_not_in_recent(dialog):
    """不勾选「打开方案」创建后，方案不出现在「最近打开」中"""
    page = dialog.page
    dialog.toggle_open_scheme(False)
    name = _unique_name("norecent")
    dialog.fill_scheme_name(name)
    dialog.fill_scheme_code(name)
    dialog.confirm()
    page.wait_for_timeout(1500)

    page.locator(".sidebar-box-content .menu-row").filter(has_text="最近打开").first.click(force=True)
    page.wait_for_timeout(1000)

    body_text = page.locator("body").inner_text()
    assert name not in body_text, f"不勾选时「{name}」不应出现在最近打开"
