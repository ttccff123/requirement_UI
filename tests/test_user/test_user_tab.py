"""
用户管理（UserManager）E2E 测试 — Tab 切换与内容校验

测试范围:
- 默认加载：进入页面应选中"用户" tab 且内容正确
- 三个 tab 两两切换（6 个方向），每次切换后断言目标面板内容正确
"""

import allure
import pytest

from pages.platform_navigation import PlatformNavigation
from pages.user_page import UserManager


# ========================================================================
#  默认加载
# ========================================================================

@pytest.mark.order(1)
@allure.feature("用户管理")
@allure.story("页面加载")
@pytest.mark.smoke
def test_default_active_tab_is_user(logged_in_page):
    """登录后点击左侧导航栏'组织'，等待页面加载，默认应选中'用户' tab 并展示完整内容"""
    # 点击左侧导航栏"组织"
    nav = PlatformNavigation(logged_in_page.page)
    nav.wait_for_sidebar()
    nav.click_navigation_item("组织")

    # 等待用户管理页面加载
    um = UserManager(logged_in_page.page)
    um.wait_for_page()

    # 激活状态
    assert um.get_active_tab_name() == "用户", "默认激活 tab 应为'用户'"
    assert um.is_user_tab_active(), "用户 tab 应处于激活样式"

    # 面板可见
    assert um.is_user_pane_visible(), "用户面板应可见"

    # 表格列头
    headers = um.get_user_table_headers()
    for col in ["序号", "用户名", "姓名", "性别", "角色", "部门", "参与项目", "访问次数", "状态"]:
        assert col in headers, f"用户表格列头应包含'{col}'，实际: {headers}"

    # 数据行
    assert um.get_user_table_row_count() > 0, "用户表格应有数据行"


# ========================================================================
#  Tab 切换 — 6 个方向
# ========================================================================

@pytest.mark.order(2)
@allure.feature("用户管理")
@allure.story("Tab切换")
def test_switch_user_to_role(user_manager_page):
    """用户 → 角色"""
    user_text = user_manager_page.get_user_pane_text()

    user_manager_page.click_tab_role()
    user_manager_page.wait_for_role_pane()

    assert user_manager_page.get_active_tab_name() == "角色", "激活 tab 应为'角色'"
    assert not user_manager_page.is_user_tab_active(), "用户 tab 不应激活"
    assert user_manager_page.is_role_pane_visible(), "角色面板应可见"
    assert user_manager_page.role_pane_has_table(), "角色面板应有表格"
    assert len(user_manager_page.get_role_table_headers()) > 0, "角色表格应有列头"


    assert user_manager_page.get_role_pane_text() != user_text, "角色内容应不同于用户"


@pytest.mark.order(3)
@allure.feature("用户管理")
@allure.story("Tab切换")
def test_switch_user_to_department(user_manager_page):
    """用户 → 部门"""
    user_text = user_manager_page.get_user_pane_text()

    user_manager_page.click_tab_department()
    user_manager_page.wait_for_department_pane()

    assert user_manager_page.get_active_tab_name() == "部门", "激活 tab 应为'部门'"
    assert not user_manager_page.is_user_tab_active(), "用户 tab 不应激活"
    assert user_manager_page.is_department_pane_visible(), "部门面板应可见"
    assert user_manager_page.department_pane_has_table(), "部门面板应有表格"
    assert len(user_manager_page.get_department_table_headers()) > 0, "部门表格应有列头"


    assert user_manager_page.get_department_pane_text() != user_text, "部门内容应不同于用户"


@pytest.mark.order(4)
@allure.feature("用户管理")
@allure.story("Tab切换")
def test_switch_role_to_user(user_manager_page):
    """角色 → 用户"""
    user_manager_page.click_tab_role()
    user_manager_page.wait_for_role_pane()
    role_text = user_manager_page.get_role_pane_text()

    user_manager_page.click_tab_user()
    user_manager_page.wait_for_user_pane()

    assert user_manager_page.get_active_tab_name() == "用户", "激活 tab 应为'用户'"
    assert user_manager_page.is_user_tab_active(), "用户 tab 应激活"
    assert user_manager_page.is_user_pane_visible(), "用户面板应可见"
    assert user_manager_page.user_pane_has_table(), "用户面板应有表格"

    headers = user_manager_page.get_user_table_headers()
    for col in ["用户名", "姓名", "角色", "部门"]:
        assert col in headers, f"用户表格列头应包含'{col}'，实际: {headers}"

    assert user_manager_page.get_user_table_row_count() > 0, "用户表格应有数据行"
    assert user_manager_page.get_user_pane_text() != role_text, "用户内容应不同于角色"


@pytest.mark.order(5)
@allure.feature("用户管理")
@allure.story("Tab切换")
def test_switch_role_to_department(user_manager_page):
    """角色 → 部门"""
    user_manager_page.click_tab_role()
    user_manager_page.wait_for_role_pane()
    role_text = user_manager_page.get_role_pane_text()

    user_manager_page.click_tab_department()
    user_manager_page.wait_for_department_pane()

    assert user_manager_page.get_active_tab_name() == "部门", "激活 tab 应为'部门'"
    assert user_manager_page.is_department_pane_visible(), "部门面板应可见"
    assert user_manager_page.department_pane_has_table(), "部门面板应有表格"
    assert len(user_manager_page.get_department_table_headers()) > 0, "部门表格应有列头"


    assert user_manager_page.get_department_pane_text() != role_text, "部门内容应不同于角色"


@pytest.mark.order(6)
@allure.feature("用户管理")
@allure.story("Tab切换")
def test_switch_department_to_user(user_manager_page):
    """部门 → 用户"""
    user_manager_page.click_tab_department()
    user_manager_page.wait_for_department_pane()
    dept_text = user_manager_page.get_department_pane_text()

    user_manager_page.click_tab_user()
    user_manager_page.wait_for_user_pane()

    assert user_manager_page.get_active_tab_name() == "用户", "激活 tab 应为'用户'"
    assert user_manager_page.is_user_tab_active(), "用户 tab 应激活"
    assert user_manager_page.is_user_pane_visible(), "用户面板应可见"
    assert user_manager_page.user_pane_has_table(), "用户面板应有表格"

    headers = user_manager_page.get_user_table_headers()
    for col in ["用户名", "姓名", "角色", "部门"]:
        assert col in headers, f"用户表格列头应包含'{col}'"

    assert user_manager_page.get_user_table_row_count() > 0, "用户表格应有数据行"
    assert user_manager_page.get_user_pane_text() != dept_text, "用户内容应不同于部门"


@pytest.mark.order(7)
@allure.feature("用户管理")
@allure.story("Tab切换")
def test_switch_department_to_role(user_manager_page):
    """部门 → 角色"""
    user_manager_page.click_tab_department()
    user_manager_page.wait_for_department_pane()
    dept_text = user_manager_page.get_department_pane_text()

    user_manager_page.click_tab_role()
    user_manager_page.wait_for_role_pane()

    assert user_manager_page.get_active_tab_name() == "角色", "激活 tab 应为'角色'"
    assert user_manager_page.is_role_pane_visible(), "角色面板应可见"
    assert user_manager_page.role_pane_has_table(), "角色面板应有表格"
    assert len(user_manager_page.get_role_table_headers()) > 0, "角色表格应有列头"


    assert user_manager_page.get_role_pane_text() != dept_text, "角色内容应不同于部门"
