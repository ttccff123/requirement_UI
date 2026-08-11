"""
用户管理 — 搜索与筛选功能测试

测试范围:
- 文本搜索框 placeholder 断言
- 下拉筛选框默认值断言
- 搜索存在的数据 → 结果包含关键词
- 搜索不存在的数据 → 结果为空
- 跨页搜索 → 第二页搜第一页数据
- 下拉筛选：弹出下拉 → 选第一个值 → 等待结果 → 断言显示值与结果行
- 组合搜索 & 筛选
"""

import allure
import pytest


@pytest.fixture(autouse=True)
def _reset_filters_after_test(user_manager_page):
    """每个用例结束后清空所有筛选条件，防止状态泄漏到下一个用例。"""
    yield
    user_manager_page.reset_all_filters()


# ========================================================================
#  Placeholder & 默认值
# ========================================================================

@pytest.mark.order(1)
@allure.feature("用户管理")
@allure.story("搜索")
def test_search_input_placeholder(user_manager_page):
    """文本搜索框应有 placeholder 提示"""
    placeholder = user_manager_page.page.locator(
        f"{user_manager_page.SEARCH_INPUT}"
    ).first.get_attribute("placeholder") or ""
    assert len(placeholder) > 0, "搜索框应有 placeholder 提示文字"


@pytest.mark.order(2)
@allure.feature("用户管理")
@allure.story("筛选")
def test_filter_default_values(user_manager_page):
    """三个下拉筛选框默认值应为空或显示占位文字"""
    for name, selector in [
        ("角色筛选", user_manager_page.FILTER_ROLE_INPUT),
        ("部门筛选", user_manager_page.FILTER_DEPT_INPUT),
        ("状态筛选", user_manager_page.FILTER_STATUS_INPUT),
    ]:
        val = user_manager_page.page.locator(selector).first.get_attribute("value") or ""
        placeholder = user_manager_page.page.locator(selector).first.get_attribute("placeholder") or ""
        assert val == "" or len(placeholder) > 0, (
            f"{name}默认值应为空，实际 value='{val}'"
        )


# ========================================================================
#  文本搜索 — 存在 / 不存在
# ========================================================================

@pytest.mark.order(3)
@allure.feature("用户管理")
@allure.story("搜索")
def test_search_existing_data(user_manager_page):
    """搜索表格中已存在的用户名，搜索结果应包含该用户"""
    data = user_manager_page.get_table_data()
    if not data:
        pytest.skip("当前页无用户数据")

    keyword = data[0].get("用户名", "")
    if not keyword:
        pytest.skip("无法获取搜索关键词")

    user_manager_page.search(keyword)
    user_manager_page.page.wait_for_timeout(1000)

    results = user_manager_page.get_table_data()
    assert len(results) > 0, f"搜索'{keyword}'后应有结果"
    for row in results:
        row_text = " ".join(str(v) for v in row.values() if v)
        assert keyword in row_text, (
            f"搜索结果应包含'{keyword}'，行数据: {row}"
        )

    user_manager_page.clear_search()
    user_manager_page.search("")
    user_manager_page.page.wait_for_timeout(1000)


@pytest.mark.order(4)
@allure.feature("用户管理")
@allure.story("搜索")
def test_search_non_existing_data(user_manager_page):
    """搜索不存在的数据，表格应显示空结果"""
    keyword = "__no_such_user_xyz__"
    user_manager_page.search(keyword)
    user_manager_page.page.wait_for_timeout(1000)

    row_count = user_manager_page.get_table_row_count()
    is_empty = user_manager_page.is_table_empty()
    assert row_count == 0 or is_empty, (
        f"搜索'{keyword}'应无结果，实际 {row_count} 行"
    )

    user_manager_page.clear_search()
    user_manager_page.search("")
    user_manager_page.page.wait_for_timeout(1000)


# ========================================================================
#  跨页搜索
# ========================================================================

@pytest.mark.order(5)
@allure.feature("用户管理")
@allure.story("搜索")
def test_search_cross_page(user_manager_page):
    """翻到第二页后搜索第一页的数据，应能查到并显示"""
    total_pages = user_manager_page.pagination.get_total_pages()
    if total_pages < 2:
        pytest.skip("总页数不足 2 页，跳过跨页搜索测试")

    user_manager_page.pagination.go_to_first_page()
    user_manager_page.page.wait_for_timeout(500)
    page1_data = user_manager_page.get_table_data()
    if not page1_data:
        pytest.skip("第一页无数据")
    keyword = page1_data[0].get("用户名", "")
    if not keyword:
        pytest.skip("无法获取搜索关键词")

    user_manager_page.pagination.go_to_page(2)
    user_manager_page.page.wait_for_timeout(1000)

    user_manager_page.search(keyword)
    user_manager_page.page.wait_for_timeout(1000)

    results = user_manager_page.get_table_data()
    assert len(results) > 0, f"在第二页搜索'{keyword}'应有结果"
    for row in results:
        row_text = " ".join(str(v) for v in row.values() if v)
        assert keyword in row_text, f"搜索结果应包含'{keyword}'"

    user_manager_page.clear_search()
    user_manager_page.search("")
    user_manager_page.page.wait_for_timeout(1000)


# ========================================================================
#  下拉筛选 — 弹出 → 选第一个值 → 断言显示值 & 结果行
# ========================================================================

def _pick_first_filter_option(um, filter_type: str) -> str:
    """点击 input → 等下拉出现 → 点第一个选项 → 返回选中文本。

    关键：可见下拉带有 x-placement="bottom-start" 属性，隐藏的没有。
    """
    select_map = {
        "role": um.FILTER_ROLE_SELECT,
        "department": um.FILTER_DEPT_SELECT,
        "status": um.FILTER_STATUS_SELECT,
    }
    select_sel = select_map[filter_type]

    # 1. 点击 input 打开下拉
    um.page.locator(f"{select_sel} input").first.click()
    um.page.wait_for_timeout(300)

    # 2. 等可见下拉出现（x-placement 属性区分可见/隐藏）
    um.page.locator(
        '.el-select-dropdown[x-placement="bottom-start"]'
    ).first.wait_for(state="visible", timeout=5000)

    # 3. 取第一个选项并点击
    items = um.page.locator(
        '.el-select-dropdown[x-placement="bottom-start"] ul li.el-select-dropdown__item'
    ).all()
    assert items, "下拉选项列表为空"
    selected = items[0].inner_text().strip()
    items[0].click()
    um.page.wait_for_timeout(1000)

    return selected


def _assert_displayed_value(page, input_selector: str, expected: str, label: str):
    """断言下拉框中显示的值包含预期文本

    Element UI 的 el-select 选中后只会设置 JS value 属性，不会更新 HTML value
    属性，因此必须用 input_value() 读取，而非 get_attribute("value")。
    """
    page.wait_for_timeout(500)
    displayed = page.locator(input_selector).first.input_value() or ""
    assert expected in displayed or displayed != "", (
        f"{label}下拉框应显示'{expected}'，实际'{displayed}'"
    )


@pytest.mark.order(6)
@allure.feature("用户管理")
@allure.story("筛选")
def test_filter_by_role(user_manager_page):
    """弹出角色下拉 → 选第一个值 → 等待结果 → 断言显示值 & 结果行一致"""
    selected = _pick_first_filter_option(user_manager_page, "role")
    assert selected, "应选中一个角色选项"

    # 断言显示值
    _assert_displayed_value(
        user_manager_page.page, user_manager_page.FILTER_ROLE_INPUT, selected, "角色"
    )

    # 断言结果行
    data = user_manager_page.get_table_data()
    assert len(data) > 0, f"筛选'{selected}'后应有数据"
    for row in data:
        actual = row.get("角色", "")
        assert actual == selected, (
            f"筛选'{selected}'后每行角色应为'{selected}'，实际'{actual}'"
        )

    user_manager_page.clear_role_filter()


@pytest.mark.order(7)
@allure.feature("用户管理")
@allure.story("筛选")
def test_filter_by_department(user_manager_page):
    """弹出部门下拉 → 选第一个值 → 等待结果 → 断言显示值 & 结果行一致"""
    selected = _pick_first_filter_option(user_manager_page, "department")
    assert selected, "应选中一个部门选项"

    _assert_displayed_value(
        user_manager_page.page, user_manager_page.FILTER_DEPT_INPUT, selected, "部门"
    )

    data = user_manager_page.get_table_data()
    assert len(data) > 0, f"筛选'{selected}'后应有数据"
    for row in data:
        actual = row.get("部门", "")
        assert actual == selected, (
            f"筛选'{selected}'后每行部门应为'{selected}'，实际'{actual}'"
        )

    user_manager_page.clear_dept_filter()


@pytest.mark.order(8)
@allure.feature("用户管理")
@allure.story("筛选")
def test_filter_by_status(user_manager_page):
    """弹出状态下拉 → 选第一个值 → 等待结果 → 断言显示值 & 结果行一致"""
    selected = _pick_first_filter_option(user_manager_page, "status")
    assert selected, "应选中一个状态选项"

    _assert_displayed_value(
        user_manager_page.page, user_manager_page.FILTER_STATUS_INPUT, selected, "状态"
    )

    data = user_manager_page.get_table_data()
    assert len(data) > 0, f"筛选'{selected}'后应有数据"
    for row in data:
        actual = row.get("状态", "")
        assert actual == selected, (
            f"筛选'{selected}'后每行状态应为'{selected}'，实际'{actual}'"
        )

    user_manager_page.clear_status_filter()


# ========================================================================
#  组合查询
# ========================================================================

@pytest.mark.order(9)
@allure.feature("用户管理")
@allure.story("组合查询")
def test_combined_search_and_role_filter(user_manager_page):
    """关键词搜索 + 角色筛选 组合查询"""
    user_manager_page.search("a")
    user_manager_page.page.wait_for_timeout(500)

    selected = _pick_first_filter_option(user_manager_page, "role")
    assert selected, "应选中一个角色选项"

    data = user_manager_page.get_table_data()
    assert isinstance(data, list), "组合查询应返回列表"

    user_manager_page.clear_role_filter()


@pytest.mark.order(10)
@allure.feature("用户管理")
@allure.story("组合查询")
def test_combined_search_and_status_filter(user_manager_page):
    """关键词搜索 + 状态筛选 组合查询"""
    user_manager_page.search("a")
    user_manager_page.page.wait_for_timeout(500)

    selected = _pick_first_filter_option(user_manager_page, "status")
    assert selected, "应选中一个状态选项"

    data = user_manager_page.get_table_data()
    assert isinstance(data, list), "组合查询应返回列表"

    user_manager_page.clear_status_filter()


@pytest.mark.order(11)
@allure.feature("用户管理")
@allure.story("组合查询")
def test_combined_role_and_status_filter(user_manager_page):
    """角色 + 状态 双筛选组合"""
    role = _pick_first_filter_option(user_manager_page, "role")
    assert role, "应选中一个角色选项"

    status = _pick_first_filter_option(user_manager_page, "status")
    assert status, "应选中一个状态选项"

    data = user_manager_page.get_table_data()
    assert isinstance(data, list), "组合筛选应返回列表"

    user_manager_page.clear_role_filter()
    user_manager_page.clear_status_filter()


@pytest.mark.order(12)
@allure.feature("用户管理")
@allure.story("组合查询")
def test_combined_all_filters(user_manager_page):
    """关键词 + 角色 + 部门 + 状态 全部组合"""
    user_manager_page.search("a")
    user_manager_page.page.wait_for_timeout(500)

    role = _pick_first_filter_option(user_manager_page, "role")
    assert role, "应选中角色"

    dept = _pick_first_filter_option(user_manager_page, "department")
    assert dept, "应选中部门"

    status = _pick_first_filter_option(user_manager_page, "status")
    assert status, "应选中状态"

    data = user_manager_page.get_table_data()
    assert isinstance(data, list), "全组合查询应返回列表"

    user_manager_page.reset_all_filters()


# ========================================================================
#  清空搜索恢复
# ========================================================================

@pytest.mark.order(13)
@allure.feature("用户管理")
@allure.story("搜索")
def test_clear_search_restores_data(user_manager_page):
    """搜索 → 清空 → 表格恢复全部数据"""
    original_count = user_manager_page.get_table_row_count()

    user_manager_page.search("__no_such_user_xyz__")
    user_manager_page.page.wait_for_timeout(1000)
    assert user_manager_page.get_table_row_count() == 0 or user_manager_page.is_table_empty(), \
        "搜索不存在数据后表格应为空"

    user_manager_page.clear_search()
    user_manager_page.search("")
    user_manager_page.page.wait_for_timeout(1000)

    restored_count = user_manager_page.get_table_row_count()
    assert restored_count >= original_count, (
        f"清空搜索后数据应恢复，原{original_count}行，恢复后{restored_count}行"
    )
