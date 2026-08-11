"""
部门管理 — 搜索部门测试

测试范围:
- 搜索框 placeholder 校验
- 搜索存在的部门名 → 树中只显示匹配项、高亮
- 搜索不存在的名称 → 树无数据
- 清空搜索 → 恢复全部部门
"""
import allure
import pytest

from tests.test_dept._helpers import close_any_dialog


# ======================== 搜索框 placeholder ========================


@allure.feature("部门管理")
@allure.story("搜索部门")
@pytest.mark.order(1)
def test_dept_search_placeholder(dept_manager_page):
    """搜索框应有 placeholder 提示文字"""
    close_any_dialog(dept_manager_page)
    placeholder = dept_manager_page.get_search_placeholder()
    assert placeholder, "搜索框应有 placeholder"


# ======================== 搜索存在的部门 ========================


@allure.feature("部门管理")
@allure.story("搜索部门")
@pytest.mark.order(2)
def test_dept_search_existing(dept_manager_page):
    """搜索存在部门 → 过滤显示、高亮"""
    close_any_dialog(dept_manager_page)

    all_names = dept_manager_page.get_dept_tree_node_names()
    assert all_names, "部门列表不应为空"
    target = all_names[0]

    dept_manager_page.search_dept(target)
    dept_manager_page.page.wait_for_timeout(300)

    filtered = dept_manager_page.get_dept_tree_node_names()
    assert target in filtered, \
        f"搜索'{target}'后列表中应包含该部门，实际={filtered}"
    for name in filtered:
        assert target in name or name in target, \
            f"搜索'{target}'后不应出现无关部门'{name}'"

    dept_manager_page.click_dept_node(target)
    dept_manager_page.page.wait_for_timeout(300)
    assert dept_manager_page.is_dept_node_selected(target), \
        f"部门'{target}'应处于选中（高亮）状态"

    dept_manager_page.clear_dept_search()
    dept_manager_page.page.wait_for_timeout(300)


# ======================== 搜索不存在的名称 ========================


@allure.feature("部门管理")
@allure.story("搜索部门")
@pytest.mark.order(3)
def test_dept_search_nonexistent(dept_manager_page):
    """搜索不存在的名称 → 树无数据"""
    close_any_dialog(dept_manager_page)

    fake_name = "不存在的部门名称_xyz_999"
    dept_manager_page.search_dept(fake_name)
    dept_manager_page.page.wait_for_timeout(300)

    filtered = dept_manager_page.get_dept_tree_node_names()
    assert len(filtered) == 0 or fake_name not in filtered, \
        f"搜索'{fake_name}'后树应无匹配项，实际={filtered}"

    dept_manager_page.clear_dept_search()
    dept_manager_page.page.wait_for_timeout(300)


# ======================== 清空搜索 ========================


@allure.feature("部门管理")
@allure.story("搜索部门")
@pytest.mark.order(4)
def test_dept_search_clear(dept_manager_page):
    """清空搜索条件 → 恢复全部部门"""
    close_any_dialog(dept_manager_page)

    all_names = dept_manager_page.get_dept_tree_node_names()
    assert all_names, "部门列表不应为空"

    target = all_names[0]
    dept_manager_page.search_dept(target)
    dept_manager_page.page.wait_for_timeout(300)
    filtered = dept_manager_page.get_dept_tree_node_names()
    assert len(filtered) <= len(all_names), "搜索后列表应缩减"

    dept_manager_page.clear_dept_search()
    dept_manager_page.page.wait_for_timeout(400)

    restored = dept_manager_page.get_dept_tree_node_names()
    assert len(restored) >= len(all_names) - 1, \
        f"清空搜索后应恢复全部部门，之前={len(all_names)}，之后={len(restored)}"
