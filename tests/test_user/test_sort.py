"""
用户管理 — 排序功能测试

测试范围:
- 获取可排序列
- 对每个可排序列执行升序排序并断言数据升序
- 对每个可排序列执行降序排序并断言数据降序
"""

import allure
import pytest


def _get_sortable_columns(user_manager_page) -> list[str]:
    """获取当前表格中支持排序的列名列表"""
    sortable = user_manager_page.get_table_header_sortable()
    return [col for col, can_sort in sortable.items() if can_sort]


def _extract_values(data: list[dict], column: str) -> list[str]:
    """从表格数据中提取指定列的值（过滤空值）"""
    return [row.get(column, "") for row in data if row.get(column, "").strip()]


def _parse_values(values: list[str], column: str):
    """根据列类型解析为可比较的对象。

    访问次数 → int；其余 → str。
    """
    if column == "访问次数":
        return [int(v) for v in values if v.isdigit()]
    return values


# ========================================================================
#  单列排序 — 升序 & 降序
# ========================================================================

@allure.feature("用户管理")
@allure.story("排序")
def test_sort_ascending(user_manager_page):
    """每个可排序列执行升序排序，断言数据升序排列"""
    sortable_columns = _get_sortable_columns(user_manager_page)
    assert len(sortable_columns) > 0, "应有可排序的列"

    for col in sortable_columns:
        if col == "序号":
            continue  # 序号不受排序影响

        user_manager_page.sort_by_column(col, ascending=True)
        user_manager_page.page.wait_for_timeout(800)

        values = _extract_values(user_manager_page.get_table_data(), col)
        if len(values) < 2:
            continue  # 数据不足 2 行，跳过比较

        parsed = _parse_values(values, col)
        assert parsed == sorted(parsed), (
            f"列'{col}'升序排序失败\n期望: {sorted(parsed)}\n实际: {parsed}"
        )


@allure.feature("用户管理")
@allure.story("排序")
def test_sort_descending(user_manager_page):
    """每个可排序列执行降序排序，断言数据降序排列"""
    sortable_columns = _get_sortable_columns(user_manager_page)
    assert len(sortable_columns) > 0, "应有可排序的列"

    for col in sortable_columns:
        if col == "序号":
            continue

        user_manager_page.sort_by_column(col, ascending=False)
        user_manager_page.page.wait_for_timeout(800)

        values = _extract_values(user_manager_page.get_table_data(), col)
        if len(values) < 2:
            continue

        parsed = _parse_values(values, col)
        assert parsed == sorted(parsed, reverse=True), (
            f"列'{col}'降序排序失败\n期望: {sorted(parsed, reverse=True)}\n实际: {parsed}"
        )


# ========================================================================
#  升序 ↔ 降序 切换
# ========================================================================

@allure.feature("用户管理")
@allure.story("排序")
def test_sort_toggle_asc_desc(user_manager_page):
    """先升序再降序，两次排序结果应相反"""
    sortable_columns = _get_sortable_columns(user_manager_page)
    assert len(sortable_columns) > 0, "应有可排序的列"

    for col in sortable_columns:
        if col == "序号":
            continue

        # 升序
        user_manager_page.sort_by_column(col, ascending=True)
        user_manager_page.page.wait_for_timeout(800)
        asc_values = _extract_values(user_manager_page.get_table_data(), col)
        if len(asc_values) < 2:
            continue

        # 降序
        user_manager_page.sort_by_column(col, ascending=False)
        user_manager_page.page.wait_for_timeout(800)
        desc_values = _extract_values(user_manager_page.get_table_data(), col)

        asc_parsed = _parse_values(asc_values, col)
        desc_parsed = _parse_values(desc_values, col)

        # 降序应为升序的反向
        assert desc_parsed == list(reversed(asc_parsed)), (
            f"列'{col}'降序应为升序的反向\n升序: {asc_parsed}\n降序: {desc_parsed}"
        )


# ========================================================================
#  跨页排序 — 多页数据排序应全局生效
# ========================================================================

@allure.feature("用户管理")
@allure.story("排序")
def test_sort_across_pages(user_manager_page):
    """排序列在非第一页执行排序后，各页数据都应保持全局排序"""
    total_pages = user_manager_page.pagination.get_total_pages()
    if total_pages < 2:
        pytest.skip("总页数不足 2 页，跳过跨页排序测试")

    sortable_columns = _get_sortable_columns(user_manager_page)
    assert len(sortable_columns) > 0, "应有可排序的列"

    # 选第一个可排序列（非序号）
    col = next((c for c in sortable_columns if c != "序号"), sortable_columns[0])

    # 1. 回到第一页，升序排序，记录第一页数据
    user_manager_page.pagination.go_to_first_page()
    user_manager_page.page.wait_for_timeout(500)
    user_manager_page.sort_by_column(col, ascending=True)
    user_manager_page.page.wait_for_timeout(800)
    page1_values = _extract_values(user_manager_page.get_table_data(), col)

    # 2. 翻到第二页，检查数据也是升序
    user_manager_page.pagination.click_next_page()
    user_manager_page.page.wait_for_timeout(1000)
    page2_values = _extract_values(user_manager_page.get_table_data(), col)

    parsed_p1 = _parse_values(page1_values, col)
    parsed_p2 = _parse_values(page2_values, col)

    # 第二页内部应有序
    assert parsed_p2 == sorted(parsed_p2), (
        f"列'{col}'第二页升序排序失败\n{parsed_p2}"
    )

    # 第一页最大值 ≤ 第二页最小值（全局有序）
    if parsed_p1 and parsed_p2:
        assert parsed_p1[-1] <= parsed_p2[0], (
            f"列'{col}'跨页升序不连续\n第一页最大值: {parsed_p1[-1]}\n第二页最小值: {parsed_p2[0]}"
        )

    # 3. 在第二页执行降序排序
    user_manager_page.sort_by_column(col, ascending=False)
    user_manager_page.page.wait_for_timeout(800)
    page2_desc = _extract_values(user_manager_page.get_table_data(), col)

    parsed_p2d = _parse_values(page2_desc, col)
    assert parsed_p2d == sorted(parsed_p2d, reverse=True), (
        f"列'{col}'第二页降序排序失败\n{parsed_p2d}"
    )

    # 4. 翻回第一页，检查降序也全局生效
    user_manager_page.pagination.click_prev_page()
    user_manager_page.page.wait_for_timeout(1000)
    page1_desc = _extract_values(user_manager_page.get_table_data(), col)

    parsed_p1d = _parse_values(page1_desc, col)
    assert parsed_p1d == sorted(parsed_p1d, reverse=True), (
        f"列'{col}'第一页降序排序失败\n{parsed_p1d}"
    )

    if parsed_p1d and parsed_p2d:
        assert parsed_p1d[-1] >= parsed_p2d[0], (
            f"列'{col}'跨页降序不连续\n第一页最小值: {parsed_p1d[-1]}\n第二页最大值: {parsed_p2d[0]}"
        )

    # 5. 改回默认每页条数
    user_manager_page.pagination.change_page_size(10)
    user_manager_page.page.wait_for_timeout(800)
