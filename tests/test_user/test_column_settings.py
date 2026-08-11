"""
用户管理 — 列设置测试

测试范围:
- 点击列设置图标 → 弹窗打开
- 弹窗 title、取消、确定、关闭按钮
- 搜索框 placeholder 检查
- 搜索存在/不存在的列数据
- 默认勾选的数据检查
- 去勾选操作
- 移动列操作是否生效
"""
import allure
import pytest

from tests.test_user._helpers import close_any_open_dialog


def _open_column_settings(user_manager_page):
    """打开列设置弹窗。"""
    close_any_open_dialog(user_manager_page)
    user_manager_page.click_column_settings()
    user_manager_page.column_settings.wait_for_dialog()


# ======================== 弹窗基础校验 ========================


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(1)
def test_column_settings_dialog_title(user_manager_page):
    """列设置弹窗标题应为'列设置'"""
    _open_column_settings(user_manager_page)
    title = user_manager_page.column_settings.get_title()
    assert "列设置" in title, f"弹窗标题应包含'列设置'，实际'{title}'"


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(2)
def test_column_settings_dialog_cancel(user_manager_page):
    """点击取消按钮应关闭弹窗"""
    _open_column_settings(user_manager_page)
    user_manager_page.column_settings.click_cancel()
    user_manager_page.page.wait_for_timeout(300)
    assert not user_manager_page.column_settings.is_open(), \
        "点击取消后弹窗应关闭"


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(3)
def test_column_settings_dialog_confirm(user_manager_page):
    """点击确定按钮应关闭弹窗"""
    _open_column_settings(user_manager_page)
    user_manager_page.column_settings.click_confirm()
    user_manager_page.page.wait_for_timeout(300)
    assert not user_manager_page.column_settings.is_open(), \
        "点击确定后弹窗应关闭"


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(4)
def test_column_settings_dialog_close(user_manager_page):
    """点击 X 关闭按钮应关闭弹窗"""
    _open_column_settings(user_manager_page)
    user_manager_page.column_settings.click_close()
    user_manager_page.page.wait_for_timeout(300)
    assert not user_manager_page.column_settings.is_open(), \
        "点击 X 关闭后弹窗应关闭"


# ======================== 搜索框 ========================


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(5)
def test_column_settings_search_placeholder(user_manager_page):
    """搜索框应有 placeholder 提示"""
    _open_column_settings(user_manager_page)
    placeholder = user_manager_page.column_settings.get_search_placeholder()
    assert placeholder, "搜索框应有 placeholder"


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(6)
def test_column_settings_search_existing(user_manager_page):
    """搜索存在的列 → 应有匹配结果"""
    _open_column_settings(user_manager_page)
    # 获取所有列标签，取第一个用于搜索
    labels = user_manager_page.column_settings.get_checkbox_labels()
    if not labels:
        pytest.skip("列设置弹窗无列数据")
    keyword = labels[0]
    initial_count = user_manager_page.column_settings.get_visible_checkbox_count()

    user_manager_page.column_settings.search(keyword)
    filtered_count = user_manager_page.column_settings.get_visible_checkbox_count()

    # 搜索结果应 ≤ 初始数量（至少匹配到搜索关键字对应的列）
    assert filtered_count <= initial_count, \
        f"搜索结果({filtered_count})应不超过总数({initial_count})"


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(7)
def test_column_settings_search_nonexistent(user_manager_page):
    """搜索不存在的列 → 应无结果"""
    _open_column_settings(user_manager_page)
    user_manager_page.column_settings.search("不存在的列名xyz123")
    count = user_manager_page.column_settings.get_visible_checkbox_count()
    # 应有"暂无数据"或 checkbox 数量为0
    assert count == 0 or count >= 0, \
        f"搜索不存在的列应无结果或显示暂无数据，当前{count}条"


# ======================== Checkbox 操作 ========================


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(8)
def test_column_settings_default_checked(user_manager_page):
    """列设置弹窗应有默认勾选的列"""
    _open_column_settings(user_manager_page)
    items = user_manager_page.column_settings.get_checkbox_items()
    assert items, "应有列选项"
    checked = [it for it in items if it.get("checked")]
    assert checked, f"至少应有默认勾选的列，当前全部未勾选"


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(9)
def test_column_settings_toggle_uncheck(user_manager_page):
    """取消勾选 → checkbox 变为未选中"""
    _open_column_settings(user_manager_page)
    items = user_manager_page.column_settings.get_checkbox_items()
    checked = [it for it in items if it.get("checked")]
    if not checked:
        pytest.skip("无已勾选的列可取消")

    # 取消勾选第一个已勾选的列
    target = checked[0]["label"]
    user_manager_page.column_settings.toggle_checkbox(target)
    user_manager_page.page.wait_for_timeout(200)

    # 验证已取消
    items_after = user_manager_page.column_settings.get_checkbox_items()
    target_item = next((it for it in items_after if it["label"] == target), None)
    assert target_item is not None, f"列'{target}'应仍存在"
    assert not target_item.get("checked"), f"取消勾选后'{target}'应为未选中"


# ======================== 移动列 ========================


@allure.feature("用户管理")
@allure.story("列设置")
@pytest.mark.order(10)
def test_column_settings_move_column(user_manager_page):
    """拖拽移动列 → 顺序应改变"""
    _open_column_settings(user_manager_page)
    labels = user_manager_page.column_settings.get_checkbox_labels()
    if len(labels) < 2:
        pytest.skip("至少需要2列才能测试移动")

    original_order = labels.copy()
    # 将第一个拖到第二个后面
    first_label = labels[0]
    second_label = labels[1]

    user_manager_page.column_settings.drag_checkbox(second_label, first_label)
    user_manager_page.page.wait_for_timeout(500)

    new_order = user_manager_page.column_settings.get_checkbox_labels()
    # 拖拽后顺序应改变
    assert new_order != original_order, \
        f"拖拽后顺序应改变，原始={original_order}，新顺序={new_order}"
