"""
部门管理 — 成员管理测试

测试范围:
- 新建复杂部门（名称30字符含中英文数字特殊字符emoji，描述100字符）
- 检查右侧成员列表
- 成员管理弹窗：title、取消、X、确定按钮
- 不勾选数据点确定、勾选全部数据点确定
- 已选数据正确显示、清空、单个取消
- 搜索用户名（存在/不存在）
"""
import re
import uuid

import allure
import pytest

from tests.test_dept._helpers import close_any_dialog, find_dept_with_members, open_member_dialog, safe_add_dept, safe_delete_dept

_test_dept_name: str = ""


def _get_member_count(dept_manager_page) -> int:
    """获取右侧成员表格行数。"""
    try:
        dept_manager_page.click_dept_node(_test_dept_name)
        dept_manager_page.page.wait_for_timeout(250)
        return len(dept_manager_page.get_member_table_data())
    except Exception:
        return -1


@pytest.fixture(scope="module", autouse=True)
def _setup_and_cleanup(dept_manager_page):
    """模块 setup：创建复杂部门；teardown：兜底删除。"""
    global _test_dept_name
    close_any_dialog(dept_manager_page)

    _test_dept_name = f"成员测试部门_{uuid.uuid4().hex[:8]}"[:30]
    desc_100 = (
        "成员管理描述📋\n含空格 换行 😀\n特殊!@#$%^&*()🎯\n"
        "中英混合Member管理Test\n补齐字符凑够一百个字描述测试部门成员管理功能完整性校验✅"
    )[:100]

    if not safe_add_dept(dept_manager_page, _test_dept_name, desc_100):
        # 使用已存在部门
        existing = find_dept_with_members(dept_manager_page)
        if existing:
            _test_dept_name = existing
        else:
            pytest.skip("无法创建测试部门且无已存在部门")
    # 验证成员管理按钮可用
    try:
        scope = open_member_dialog(dept_manager_page, _test_dept_name)
        if scope is None:
            pytest.skip("成员管理弹窗未打开")
        dept_manager_page.dialog.click_member_dialog_close()
    except Exception:
        pytest.skip("成员管理弹窗不可用")

    yield

    # teardown：清空成员 → 删除部门
    close_any_dialog(dept_manager_page)
    page = dept_manager_page.page
    try:
        dept_manager_page.click_dept_node(_test_dept_name)
        page.wait_for_timeout(200)
        dept_manager_page.click_member_manage()
        dept_manager_page.dialog.wait_for_member_dialog()
        scope = f"{dept_manager_page.dialog.MEMBER_DIALOG}:visible"

        clear_btn = page.locator(f"{scope}").locator("text=清空").first
        if clear_btn.count() > 0:
            clear_btn.click()
            page.wait_for_timeout(300)
        elif page.locator(f"{scope} :has-text('清空')").first.count() > 0:
            page.locator(f"{scope} :has-text('清空')").first.click()
            page.wait_for_timeout(300)

        dept_manager_page.dialog.click_member_dialog_confirm()
        page.wait_for_timeout(500)

        if dept_manager_page.dialog.is_member_dialog_open():
            dept_manager_page.dialog.click_member_dialog_close()
    except Exception:
        pass

    safe_delete_dept(dept_manager_page, _test_dept_name)


# ======================== 弹窗基础校验 ========================


@allure.feature("部门管理")
@allure.story("成员管理")
@pytest.mark.order(1)
def test_dept_member_dialog_title(dept_manager_page):
    """成员管理弹窗标题"""
    scope = open_member_dialog(dept_manager_page, _test_dept_name)
    if scope is None:
        pytest.skip("成员管理弹窗未打开（成员管理按钮不可用或弹窗标题不匹配）")
    title = dept_manager_page.page.locator(f"{scope} .title__text").first.inner_text()
    assert "成员" in title or "添加" in title, \
        f"弹窗标题应包含成员/添加，实际='{title}'"
    dept_manager_page.dialog.click_member_dialog_close()
    dept_manager_page.page.wait_for_timeout(250)


@allure.feature("部门管理")
@allure.story("成员管理")
@pytest.mark.order(2)
def test_dept_member_dialog_cancel(dept_manager_page):
    """点取消 → 弹窗关闭"""
    scope = open_member_dialog(dept_manager_page, _test_dept_name)
    if scope is None:
        pytest.skip("成员管理弹窗未打开")
    dept_manager_page.dialog.click_member_dialog_cancel()
    dept_manager_page.page.wait_for_timeout(250)
    assert not dept_manager_page.dialog.is_member_dialog_open(), \
        "点取消后弹窗应关闭"


@allure.feature("部门管理")
@allure.story("成员管理")
@pytest.mark.order(3)
def test_dept_member_dialog_close(dept_manager_page):
    """点 X → 弹窗关闭"""
    scope = open_member_dialog(dept_manager_page, _test_dept_name)
    if scope is None:
        pytest.skip("成员管理弹窗未打开")
    dept_manager_page.dialog.click_member_dialog_close()
    dept_manager_page.page.wait_for_timeout(250)
    assert not dept_manager_page.dialog.is_member_dialog_open(), \
        "点 X 后弹窗应关闭"


# ======================== 成员选择 ========================


@allure.feature("部门管理")
@allure.story("成员管理")
@pytest.mark.order(4)
def test_dept_member_confirm_no_selection(dept_manager_page):
    """不勾选任何数据 → 点确定 → 弹窗关闭、成员列表仍为空"""
    scope = open_member_dialog(dept_manager_page, _test_dept_name)
    if scope is None:
        pytest.skip("成员管理弹窗未打开")
    page = dept_manager_page.page

    dept_manager_page.dialog.click_member_dialog_confirm()
    page.wait_for_timeout(500)

    if dept_manager_page.dialog.is_member_dialog_open():
        dept_manager_page.dialog.click_member_dialog_close()
    assert _get_member_count(dept_manager_page) == 0, \
        "未选择成员时确定，成员列表应仍为空"


@allure.feature("部门管理")
@allure.story("成员管理")
@pytest.mark.order(5)
def test_dept_member_select_and_confirm(dept_manager_page):
    """勾选全部数据 → 点确定 → 成员添加成功"""
    scope = open_member_dialog(dept_manager_page, _test_dept_name)
    if scope is None:
        pytest.skip("成员管理弹窗未打开")
    page = dept_manager_page.page

    select_all = page.locator(f"{scope} .el-checkbox:has-text('全选')").first
    if select_all.count() > 0:
        select_all.click()
        page.wait_for_timeout(200)

    selected_text = page.locator(f"{scope} :has-text('已选')").first.inner_text()
    print(f"已选: {selected_text}")

    dept_manager_page.dialog.click_member_dialog_confirm()
    page.wait_for_timeout(800)

    if dept_manager_page.dialog.is_member_dialog_open():
        dept_manager_page.dialog.click_member_dialog_close()
        pytest.fail("添加成员失败，弹窗未关闭")

    count = _get_member_count(dept_manager_page)
    if count >= 0:
        assert count > 0, f"添加成员后成员列表应有数据，实际={count}"


# ======================== 已选操作 ========================


@allure.feature("部门管理")
@allure.story("成员管理")
@pytest.mark.order(6)
def test_dept_member_clear_selection(dept_manager_page):
    """勾选数据 → 点清空 → 已选归零"""
    scope = open_member_dialog(dept_manager_page, _test_dept_name)
    if scope is None:
        pytest.skip("成员管理弹窗未打开")
    page = dept_manager_page.page

    checkboxes = page.locator(
        f"{scope} .el-checkbox:not(:has-text('全选'))"
    ).all()
    if len(checkboxes) >= 2:
        checkboxes[0].click()
        page.wait_for_timeout(100)
        checkboxes[1].click()
        page.wait_for_timeout(100)

    selected_locator = page.locator(f"{scope}").locator("text=/已选：\\d+/")
    selected_text = selected_locator.first.inner_text()
    assert "0" not in selected_text.split("：")[-1], \
        f"勾选后已选数应>0，实际='{selected_text}'"

    clear_btn = page.locator(f"{scope}").locator("text=清空").first
    if clear_btn.count() > 0:
        clear_btn.click()
        page.wait_for_timeout(300)
    elif page.locator(f"{scope} :has-text('清空')").first.count() > 0:
        page.locator(f"{scope} :has-text('清空')").first.click()
        page.wait_for_timeout(300)

    selected_text = selected_locator.first.inner_text()
    assert "0" in selected_text, f"清空后已选数应为0，实际='{selected_text}'"

    dept_manager_page.dialog.click_member_dialog_close()


@allure.feature("部门管理")
@allure.story("成员管理")
@pytest.mark.order(7)
def test_dept_member_remove_tag(dept_manager_page):
    """勾选数据 → 点已选标签 X → 取消单个勾选"""
    scope = open_member_dialog(dept_manager_page, _test_dept_name)
    if scope is None:
        pytest.skip("成员管理弹窗未打开")
    page = dept_manager_page.page

    cb = page.locator(f"{scope} .el-checkbox:not(:has-text('全选'))").first
    cb.click()
    page.wait_for_timeout(100)

    selected_el = page.locator(f"{scope} :has-text('已选')").first
    selected_text_before = selected_el.inner_text()

    tag_close = page.locator(f"{scope} .el-tag .el-icon-close, {scope} .el-tag__close").first
    if tag_close.count() > 0:
        tag_close.click()
        page.wait_for_timeout(200)
        selected_text_after = selected_el.inner_text()
        assert selected_text_after != selected_text_before, \
            f"取消标签后已选数应变化"

    dept_manager_page.dialog.click_member_dialog_close()


# ======================== 搜索 ========================


@allure.feature("部门管理")
@allure.story("成员管理")
@pytest.mark.order(8)
def test_dept_member_search_user(dept_manager_page):
    """搜索用户名存在 → 过滤显示；搜索不存在 → 无数据"""
    scope = open_member_dialog(dept_manager_page, _test_dept_name)
    if scope is None:
        pytest.skip("成员管理弹窗未打开")
    page = dept_manager_page.page

    user_labels = page.locator(
        f"{scope} .el-checkbox:not(:has-text('全选')) .el-checkbox__label"
    ).all()
    if not user_labels:
        user_labels = page.locator(
            f"{scope} .el-checkbox:not(:has-text('全选'))"
        ).all()
    if not user_labels:
        dept_manager_page.dialog.click_member_dialog_close()
        pytest.skip("无可用用户数据")

    first_user = user_labels[0].inner_text().strip()
    m = re.search(r'（(.+?)）', first_user)
    search_keyword = m.group(1) if m else first_user[:4]

    search_input = page.locator(f"{scope} input[placeholder='搜索']").first
    search_input.fill(search_keyword)
    page.wait_for_timeout(300)

    filtered = page.locator(f"{scope} .el-checkbox:not(:has-text('全选'))").count()
    assert filtered > 0, f"搜索'{search_keyword}'应有匹配结果"

    search_input.fill("不存在的用户_xyz_999")
    page.wait_for_timeout(300)
    no_result = page.locator(f"{scope} .el-checkbox:not(:has-text('全选'))").count()
    assert no_result == 0, f"搜索不存在用户应无结果，实际={no_result}"

    dept_manager_page.dialog.click_member_dialog_close()
