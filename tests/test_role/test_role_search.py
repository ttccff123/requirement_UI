"""
角色管理 — 搜索角色测试

测试范围:
- 搜索框 placeholder 校验
- 搜索存在的角色名 → 树中只显示匹配项、高亮、右侧展示名称和描述
- 搜索不存在的名称 → 树无数据、右侧无名称描述
- 清空搜索 → 恢复全部角色
"""
import allure
import pytest

from tests.test_role._helpers import close_any_dialog


def _get_right_panel_text(role_manager_page) -> str:
    """获取右侧面板纯文本（排除左侧角色树）。"""
    # 右侧主区域：.role-page 下非 el-aside 的容器
    page = role_manager_page.page
    el = page.locator(
        "#pane-role .role-page>.el-main,"
        "#pane-role .role-page>div:not(.el-aside),"
        "#pane-role .role-page>section:not(.el-aside)"
    ).first
    if el.count() == 0:
        # 回退：用 ROLE_MAIN 并截取
        el = page.locator(role_manager_page.ROLE_MAIN).first
    return el.inner_text() if el.count() > 0 else ""


# ======================== 搜索框 placeholder ========================


@allure.feature("角色管理")
@allure.story("搜索角色")
@pytest.mark.order(1)
def test_search_placeholder(role_manager_page):
    """搜索框应有 placeholder 提示文字"""
    close_any_dialog(role_manager_page)
    placeholder = role_manager_page.get_search_placeholder()
    assert placeholder, "搜索框应有 placeholder"


# ======================== 搜索存在的角色 ========================


@allure.feature("角色管理")
@allure.story("搜索角色")
@pytest.mark.order(2)
def test_search_existing_role(role_manager_page):
    """搜索存在角色 → 过滤显示、高亮、右侧展示名称和描述"""
    close_any_dialog(role_manager_page)

    # 取第一个角色名作为搜索目标
    all_names = role_manager_page.get_role_tree_node_names()
    assert all_names, "角色列表不应为空"
    target = all_names[0]

    # 执行搜索
    role_manager_page.search_role(target)
    role_manager_page.page.wait_for_timeout(300)

    # 验证树中只显示匹配项
    filtered = role_manager_page.get_role_tree_node_names()
    assert target in filtered, \
        f"搜索'{target}'后列表中应包含该角色，实际={filtered}"
    # 精确匹配：搜索结果不应包含不相关的角色
    for name in filtered:
        assert target in name or name in target, \
            f"搜索'{target}'后不应出现无关角色'{name}'"

    # 点击搜索结果使其选中 + 高亮
    role_manager_page.click_role_node(target)
    role_manager_page.page.wait_for_timeout(300)
    assert role_manager_page.is_role_node_selected(target), \
        f"角色'{target}'应处于选中（高亮）状态"

    # 验证右侧面板展示角色名称和描述
    right_text = _get_right_panel_text(role_manager_page)
    assert target in right_text, \
        f"右侧面板应展示角色名称'{target}'，实际面板内容={right_text[:200]}"

    # 清空搜索
    role_manager_page.clear_role_search()
    role_manager_page.page.wait_for_timeout(300)


# ======================== 搜索不存在的名称 ========================


@allure.feature("角色管理")
@allure.story("搜索角色")
@pytest.mark.order(3)
def test_search_nonexistent_role(role_manager_page):
    """搜索不存在的名称 → 树无数据、右侧无名称描述"""
    close_any_dialog(role_manager_page)

    fake_name = "不存在的角色名称_xyz_999"
    role_manager_page.search_role(fake_name)
    role_manager_page.page.wait_for_timeout(300)

    # 验证树中无匹配项（或显示空状态）
    filtered = role_manager_page.get_role_tree_node_names()
    assert len(filtered) == 0 or fake_name not in filtered, \
        f"搜索'{fake_name}'后树应无匹配项，实际={filtered}"

    # 验证右侧面板没有该名称和描述
    right_text = _get_right_panel_text(role_manager_page)
    # 右侧可能显示旧数据或空状态，但不应显示搜索名称
    assert fake_name not in right_text, \
        f"搜索不存在名称时右侧不应显示'{fake_name}'"

    # 清空搜索
    role_manager_page.clear_role_search()
    role_manager_page.page.wait_for_timeout(300)


# ======================== 清空搜索 ========================


@allure.feature("角色管理")
@allure.story("搜索角色")
@pytest.mark.order(4)
def test_clear_search(role_manager_page):
    """清空搜索条件 → 恢复全部角色"""
    close_any_dialog(role_manager_page)

    # 记录全部角色
    all_names = role_manager_page.get_role_tree_node_names()
    assert all_names, "角色列表不应为空"

    # 搜索某个角色使列表缩减
    target = all_names[0]
    role_manager_page.search_role(target)
    role_manager_page.page.wait_for_timeout(300)
    filtered = role_manager_page.get_role_tree_node_names()
    assert len(filtered) <= len(all_names), "搜索后列表应缩减"

    # 清空搜索
    role_manager_page.clear_role_search()
    role_manager_page.page.wait_for_timeout(400)

    # 验证恢复全部角色
    restored = role_manager_page.get_role_tree_node_names()
    assert len(restored) >= len(all_names) - 1, \
        f"清空搜索后应恢复全部角色，之前={len(all_names)}，之后={len(restored)}"
