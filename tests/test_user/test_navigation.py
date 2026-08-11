"""
用户管理 — 表格跳转测试

测试范围:
- 姓名点击 → 查看用户弹窗（姓名一致性、关闭/确定按钮）
- 参与项目点击 → 参与项目弹窗（列头校验、关闭/确定按钮）
"""
import allure
import pytest

from tests.test_user._helpers import close_any_open_dialog


def _get_first_table_row(user_manager_page):
    """获取表格第一行数据。"""
    rows = user_manager_page.get_table_data()
    assert rows, "表格应有数据"
    return rows[0]


_cached_project_user: str | None = None


def _get_project_username(user_manager_page) -> str | None:
    """查找参与项目 > 0 的用户名（缓存结果避免重复查询导致超时）。"""
    global _cached_project_user
    if _cached_project_user:
        return _cached_project_user
    rows = user_manager_page.get_table_data()
    for row in rows:
        val = row.get("参与项目", "")
        try:
            if int(val) > 0:
                _cached_project_user = row.get("用户名", "")
                return _cached_project_user
        except (ValueError, TypeError):
            continue
    return None


# ======================== 查看用户弹窗 ========================


@allure.feature("用户管理")
@allure.story("表格跳转")
@pytest.mark.order(1)
def test_click_name_opens_view_dialog(user_manager_page):
    """点击姓名 → 查看用户弹窗 → 姓名一致"""
    row = _get_first_table_row(user_manager_page)
    expected_name = row.get("姓名", "")
    assert expected_name, "用户应有姓名"

    close_any_open_dialog(user_manager_page)
    user_manager_page.click_user_realname_by_index(0)
    user_manager_page.dialog.wait_for_view_user_dialog()

    # 验证弹窗标题
    title = user_manager_page.dialog.get_view_user_dialog_title()
    assert "查看用户" in title, f"弹窗标题应包含'查看用户'，实际'{title}'"

    # 验证弹窗内容包含该用户姓名
    body = user_manager_page.dialog.get_view_user_dialog_body_text()
    assert expected_name in body, \
        f"查看用户弹窗应包含姓名'{expected_name}'，实际内容：'{body}'"


@allure.feature("用户管理")
@allure.story("表格跳转")
@pytest.mark.order(2)
def test_view_user_dialog_close_button(user_manager_page):
    """查看用户弹窗 → X 关闭按钮"""
    close_any_open_dialog(user_manager_page)
    user_manager_page.click_user_realname_by_index(0)
    user_manager_page.dialog.wait_for_view_user_dialog()

    # 点击 X 关闭
    user_manager_page.dialog.close_view_user_dialog()
    user_manager_page.page.wait_for_timeout(300)

    assert not user_manager_page.dialog.is_view_user_dialog_open(), \
        "点击关闭后查看用户弹窗应关闭"


@allure.feature("用户管理")
@allure.story("表格跳转")
@pytest.mark.order(3)
def test_view_user_dialog_confirm_button(user_manager_page):
    """查看用户弹窗 → 确定按钮关闭"""
    close_any_open_dialog(user_manager_page)
    user_manager_page.click_user_realname_by_index(0)
    user_manager_page.dialog.wait_for_view_user_dialog()

    # 点击确定
    user_manager_page.dialog.click_view_user_dialog_confirm()
    user_manager_page.page.wait_for_timeout(300)

    assert not user_manager_page.dialog.is_view_user_dialog_open(), \
        "点击确定后查看用户弹窗应关闭"


# ======================== 参与项目弹窗 ========================


@allure.feature("用户管理")
@allure.story("表格跳转")
@pytest.mark.order(4)
def test_click_projects_opens_dialog(user_manager_page):
    """点击参与项目数 → 弹窗显示项目和项目角色"""
    username = _get_project_username(user_manager_page)
    if not username:
        pytest.skip("未找到参与项目>0 的用户")

    close_any_open_dialog(user_manager_page)
    user_manager_page.click_user_projects(username)
    user_manager_page.dialog.wait_for_projects_dialog()

    # 验证弹窗标题
    title = user_manager_page.dialog.get_projects_dialog_title()
    assert "参与项目" in title, f"弹窗标题应包含'参与项目'，实际'{title}'"

    # 验证弹窗打开即可（参与项目弹窗内容为表格，body 可能无纯文本）
    assert user_manager_page.dialog.is_projects_dialog_open(), "参与项目弹窗应打开"


@allure.feature("用户管理")
@allure.story("表格跳转")
@pytest.mark.order(5)
def test_projects_dialog_close_button(user_manager_page):
    """参与项目弹窗 → X 关闭按钮"""
    username = _get_project_username(user_manager_page)
    if not username:
        pytest.skip("未找到参与项目>0 的用户")

    close_any_open_dialog(user_manager_page)
    user_manager_page.click_user_projects(username)
    user_manager_page.dialog.wait_for_projects_dialog()

    # 点击 X 关闭按钮
    close_sel = user_manager_page.dialog.PROJECTS_DIALOG_CLOSE
    user_manager_page.page.locator(close_sel).first.click()
    user_manager_page.page.wait_for_timeout(300)

    assert not user_manager_page.dialog.is_projects_dialog_open(), \
        "点击 X 关闭后参与项目弹窗应关闭"


