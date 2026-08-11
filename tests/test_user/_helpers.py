"""test_create.py 和 test_edit.py 的共享工具函数。"""

import random
from pathlib import Path

from common.utils.placeholder_util import resolve_value  # noqa: F401 — 从旧路径重导出
from common.utils.yaml_util import YamlUtil

# 下拉框字段（不能用 fill_field 直接填充，选择第一个可用值）
SELECT_FIELDS = {"角色", "部门"}
# 单选框字段（随机选第一个或第二个）
RADIO_FIELDS = {"性别", "状态"}


# ======================== YAML 数据加载 ========================


def load_cases(yaml_path: str | Path) -> list[dict]:
    """从 YAML 文件加载 cases 列表。"""
    data = YamlUtil(str(yaml_path)).read()
    return data.get("cases", [])


def get_cases_for_category(yaml_path: str | Path, categories: list[str]) -> list[dict]:
    """获取指定 category 的测试用例。"""
    cases = load_cases(yaml_path)
    return [c for c in cases if c.get("category") in categories]


def make_case_id(case: dict) -> str:
    """生成参数化用例的 ID。"""
    return case.get("case", "unknown")




# ======================== 弹窗操作 ========================


def close_any_open_dialog(user_manager_page):
    """关闭页面上所有可见的 kd-dialog 弹窗（通用方式，不依赖弹窗标题）。"""
    page = user_manager_page.page
    dialogs = page.locator(".el-dialog__wrapper.kd-dialog:visible")
    count = dialogs.count()
    for i in range(count):
        dialog = dialogs.nth(i)
        if not dialog.is_visible():
            continue
        close_btn = dialog.locator(".el-dialog__close")
        if close_btn.count() > 0 and close_btn.first.is_visible():
            close_btn.first.click()
        else:
            page.locator("body").first.press("Escape")
        page.wait_for_timeout(300)


# ======================== 表单字段填充 ========================


def fill_select_field(user_manager_page, field_label: str, option_text: str = ""):
    """填充 el-select 字段（角色/部门等下拉选择框）。

    角色下拉框：li.el-select-dropdown__item
    部门下拉框：li.el-select-dropdown__item span.el-tree-node__label（树形结构）

    若 option_text 为空，则选择第一个可用选项。
    """
    form_item = user_manager_page.dialog._find_form_item(field_label)
    if form_item.count() == 0:
        return
    form_item.locator("input.el-input__inner").first.click()
    user_manager_page.page.wait_for_timeout(300)
    dropdown = user_manager_page.page.locator(
        '.el-select-dropdown[x-placement="bottom-start"]:visible, '
        '.el-select-dropdown:not([style*="display: none"])'
    ).first
    dropdown.wait_for(state="visible", timeout=5000)

    if field_label == "部门":
        if option_text:
            item = dropdown.locator(
                f'li.el-select-dropdown__item span.el-tree-node__label:has-text("{option_text}")'
            ).first
        else:
            item = dropdown.locator(
                "li.el-select-dropdown__item span.el-tree-node__label"
            ).first
    else:
        if option_text:
            item = dropdown.locator(
                f'li.el-select-dropdown__item:has-text("{option_text}")'
            ).first
        else:
            item = dropdown.locator("li.el-select-dropdown__item").first

    item.click()
    user_manager_page.page.wait_for_timeout(300)


def fill_radio_field(user_manager_page, field_label: str):
    """填充 el-radio 单选框字段（性别/状态等），随机选第一个或第二个选项。"""
    form_item = user_manager_page.dialog._find_form_item(field_label)
    if form_item.count() == 0:
        return
    radios = form_item.locator(".el-radio").all()
    if not radios:
        return
    enabled = [r for r in radios if "is-disabled" not in (r.get_attribute("class") or "")]
    if not enabled:
        enabled = radios
    chosen = random.choice(enabled[:2])
    chosen.click()
    user_manager_page.page.wait_for_timeout(200)


def fill_other_fields(user_manager_page, skip_field: str):
    """填充除 skip_field 外的下拉框和单选框字段（角色/部门/性别/状态）。"""
    for field in SELECT_FIELDS:
        if field == skip_field:
            continue
        fill_select_field(user_manager_page, field)
    for field in RADIO_FIELDS:
        if field == skip_field:
            continue
        fill_radio_field(user_manager_page, field)
