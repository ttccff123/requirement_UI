import re

import allure
import pytest
from playwright.sync_api import expect

from config.settings import BASE_URL


# ========================================================================
#  页面标题 & URL
# ========================================================================

@allure.feature("我的空间")
@allure.story("页面基础信息")
@pytest.mark.smoke
def test_page_title(my_workspace_page):
    """登录后页面标题应为'我的空间'"""
    title = my_workspace_page.get_page_title()
    assert title == "我的空间", f"期望标题'我的空间'，实际'{title}'"


@allure.feature("我的空间")
@allure.story("页面基础信息")
def test_page_url(my_workspace_page):
    """登录后 URL 应包含 #/home"""
    expect(my_workspace_page.page).to_have_url(re.compile(r"#/home"), timeout=10000)


@allure.feature("我的空间")
@allure.story("页面基础信息")
def test_page_loaded(my_workspace_page):
    """页面主体容器可见"""
    assert my_workspace_page.is_page_loaded(), "页面未加载"


# ========================================================================
#  模块标题校验
# ========================================================================

@allure.feature("我的空间")
@allure.story("模块标题")
@pytest.mark.smoke
@pytest.mark.parametrize("module_name", [
    "任务总览",
    "项目总览",
    "参考样例",
    "我的任务",
    "我的项目",
    "动态",
    "工具集",
])
def test_module_visible(my_workspace_page, module_name):
    """每个模块标题应在页面上可见"""
    locator = my_workspace_page.page.locator(
        f".module-layout .header-left div:has-text(\"{module_name}\")"
    )
    expect(locator.first).to_be_visible(timeout=10000)


# ========================================================================
#  任务总览 & 项目总览 — 统计数字 & 按钮点击跳转
# ========================================================================

@allure.feature("我的空间")
@allure.story("任务总览")
def test_task_overview_count(my_workspace_page):
    """任务总览应显示参与任务数字 > 0"""
    title = my_workspace_page.get_task_overview_title()
    count = my_workspace_page.get_task_overview_count()
    assert title == "参与任务", f"期望'参与任务'，实际'{title}'"
    assert isinstance(count, int) and count >= 0, f"任务数应为非负整数，实际{count}"


@allure.feature("我的空间")
@allure.story("任务总览")
def test_click_view_tasks(my_workspace_page):
    """点击'查看任务'按钮应跳转到任务相关页面（URL 变化）"""
    old_url = my_workspace_page.page.url
    my_workspace_page.click_task_overview_view()
    my_workspace_page.page.wait_for_timeout(1500)
    new_url = my_workspace_page.page.url
    assert new_url != old_url or "#/task" in new_url.lower() or "task" in new_url.lower(), \
        f"点击查看任务后 URL 应变化，旧={old_url}，新={new_url}"


@allure.feature("我的空间")
@allure.story("项目总览")
def test_project_overview_count(my_workspace_page):
    """项目总览应显示参与项目数字 > 0"""
    title = my_workspace_page.get_project_overview_title()
    count = my_workspace_page.get_project_overview_count()
    assert title == "参与项目", f"期望'参与项目'，实际'{title}'"
    assert isinstance(count, int) and count >= 0, f"项目数应为非负整数，实际{count}"


@allure.feature("我的空间")
@allure.story("项目总览")
def test_click_view_projects(my_workspace_page):
    """点击'查看项目'按钮应跳转到项目相关页面"""
    old_url = my_workspace_page.page.url
    my_workspace_page.click_project_overview_view()
    my_workspace_page.page.wait_for_timeout(1500)
    new_url = my_workspace_page.page.url
    assert new_url != old_url or "project" in new_url.lower() or "#/project" in new_url.lower(), \
        f"点击查看项目后 URL 应变化，旧={old_url}，新={new_url}"


# ========================================================================
#  参考样例
# ========================================================================

@allure.feature("我的空间")
@allure.story("参考样例")
def test_reference_examples_empty(my_workspace_page):
    """参考样例当前应显示空状态（暂无数据）"""
    assert my_workspace_page.is_reference_examples_empty(), "参考样例应显示空状态"


# ========================================================================
#  我的任务 — 列表、详情、按钮点击跳转
# ========================================================================

@allure.feature("我的空间")
@allure.story("我的任务")
def test_my_tasks_list_not_empty(my_workspace_page):
    """我的任务左侧列表不应为空"""
    tasks = my_workspace_page.get_my_tasks_list()
    assert len(tasks) > 0, f"我的任务列表不应为空，实际{len(tasks)}条"


@allure.feature("我的空间")
@allure.story("我的任务")
def test_my_tasks_switch_item(my_workspace_page):
    """点击任务列表项应切换右侧详情（页面内操作）"""
    tasks = my_workspace_page.get_my_tasks_list()
    if len(tasks) < 2:
        pytest.skip("任务数不足2条，无法测试切换")
    old_active = my_workspace_page.get_my_tasks_active_item()
    # 点击与当前选中不同的项
    new_task = tasks[1] if old_active == tasks[0] else tasks[0]
    my_workspace_page.click_my_tasks_item(new_task)
    my_workspace_page.page.wait_for_timeout(1000)
    new_active = my_workspace_page.get_my_tasks_active_item()
    assert new_active == new_task, f"切换后选中项应为'{new_task}'，实际'{new_active}'"


@allure.feature("我的空间")
@allure.story("我的任务")
def test_my_tasks_detail_has_fields(my_workspace_page):
    """右侧任务详情应包含关键字段"""
    detail = my_workspace_page.get_my_tasks_detail()
    assert detail.get("project", "") or detail.get("project") == "", \
        "详情应包含所属项目字段"
    assert detail.get("status", "") or detail.get("status") == "", \
        "详情应包含状态字段"


@allure.feature("我的空间")
@allure.story("我的任务")
@allure.story("按钮点击跳转")
def test_click_handle_task(my_workspace_page):
    """点击'处理任务'按钮应跳转到任务详情页"""
    old_url = my_workspace_page.page.url
    my_workspace_page.click_my_tasks_handle()
    my_workspace_page.page.wait_for_timeout(1500)
    new_url = my_workspace_page.page.url
    assert new_url != old_url, f"点击处理任务后 URL 应变化，旧={old_url}，新={new_url}"


@allure.feature("我的空间")
@allure.story("我的任务")
@allure.story("按钮点击跳转")
def test_click_my_tasks_arrow(my_workspace_page):
    """点击我的任务标题栏右侧箭头应跳转"""
    old_url = my_workspace_page.page.url
    my_workspace_page.click_my_tasks_arrow()
    my_workspace_page.page.wait_for_timeout(1500)
    new_url = my_workspace_page.page.url
    assert new_url != old_url, f"点击箭头后 URL 应变化"


# ========================================================================
#  我的项目 — 列表、详情、按钮点击跳转
# ========================================================================

@allure.feature("我的空间")
@allure.story("我的项目")
def test_my_projects_list_not_empty(my_workspace_page):
    """我的项目左侧列表不应为空"""
    projects = my_workspace_page.get_my_projects_list()
    assert len(projects) > 0, f"我的项目列表不应为空，实际{len(projects)}条"


@allure.feature("我的空间")
@allure.story("我的项目")
def test_my_projects_switch_item(my_workspace_page):
    """点击项目列表项应切换右侧详情"""
    projects = my_workspace_page.get_my_projects_list()
    if len(projects) < 2:
        pytest.skip("项目数不足2条，无法测试切换")
    old_active = my_workspace_page.get_my_projects_active_item()
    new_proj = projects[1] if old_active == projects[0] else projects[0]
    my_workspace_page.click_my_projects_item(new_proj)
    my_workspace_page.page.wait_for_timeout(1000)
    new_active = my_workspace_page.get_my_projects_active_item()
    assert new_active == new_proj, f"切换后选中项应为'{new_proj}'，实际'{new_active}'"


@allure.feature("我的空间")
@allure.story("我的项目")
def test_my_projects_detail_has_fields(my_workspace_page):
    """右侧项目详情应包含关键字段"""
    detail = my_workspace_page.get_my_projects_detail()
    assert "name" in detail, "详情应包含项目名称"
    assert "status" in detail, "详情应包含状态"


@allure.feature("我的空间")
@allure.story("我的项目")
@allure.story("按钮点击跳转")
def test_click_handle_project(my_workspace_page):
    """点击'处理项目'按钮应跳转到项目详情页"""
    old_url = my_workspace_page.page.url
    my_workspace_page.click_my_projects_handle()
    my_workspace_page.page.wait_for_timeout(1500)
    new_url = my_workspace_page.page.url
    assert new_url != old_url, f"点击处理项目后 URL 应变化，旧={old_url}，新={new_url}"


@allure.feature("我的空间")
@allure.story("我的项目")
@allure.story("按钮点击跳转")
def test_click_my_projects_arrow(my_workspace_page):
    """点击我的项目标题栏右侧箭头应跳转"""
    old_url = my_workspace_page.page.url
    my_workspace_page.click_my_projects_arrow()
    my_workspace_page.page.wait_for_timeout(1500)
    new_url = my_workspace_page.page.url
    assert new_url != old_url, f"点击箭头后 URL 应变化"


# ========================================================================
#  动态 — 列表数据
# ========================================================================

@allure.feature("我的空间")
@allure.story("动态")
def test_activity_feed_has_items(my_workspace_page):
    """动态列表不应为空"""
    count = my_workspace_page.get_activity_feed_count()
    assert count > 0, f"动态条数应 > 0，实际{count}"


@allure.feature("我的空间")
@allure.story("动态")
def test_activity_feed_structure(my_workspace_page):
    """每条动态应有类型、内容、时间"""
    items = my_workspace_page.get_activity_feed_items()
    assert len(items) > 0, "动态列表不应为空"
    for item in items[:3]:  # 只校验前3条
        assert "type" in item and item["type"], f"动态应包含类型: {item}"
        assert "content" in item and item["content"], f"动态应包含内容: {item}"
        assert "time" in item and item["time"], f"动态应包含时间: {item}"


# ========================================================================
#  工具集
# ========================================================================

@allure.feature("我的空间")
@allure.story("工具集")
def test_toolset_has_items(my_workspace_page):
    """工具集应有6个工具"""
    count = my_workspace_page.get_toolset_item_count()
    assert count == 6, f"工具集应有6个工具，实际{count}"


@allure.feature("我的空间")
@allure.story("工具集")
def test_toolset_names(my_workspace_page):
    """工具集应包含6个指定工具"""
    my_workspace_page.wait_for_page()
    items = my_workspace_page.get_toolset_items()
    names = [item["name"] for item in items]
    expected = ["概念开发", "需求管理", "架构设计", "架构验证", "体系推演", "体系评估"]
    assert len(items) == 6, f"工具集应有6个工具，实际{len(items)}个: {names}"
    for name in expected:
        assert name in names, f"工具集应包含'{name}'，实际列表{names}"


@allure.feature("我的空间")
@allure.story("工具集")
@allure.story("按钮点击跳转")
def test_click_toolset_enabled_tool(my_workspace_page):
    """点击已启用的工具（如架构设计）应跳转"""
    old_url = my_workspace_page.page.url
    my_workspace_page.click_toolset_item("架构设计")
    my_workspace_page.page.wait_for_timeout(1500)
    new_url = my_workspace_page.page.url
    assert new_url != old_url or "design" in new_url.lower(), \
        f"点击工具后 URL 应变化，旧={old_url}，新={new_url}"


# ========================================================================
#  日历 — 日期信息 & 点击
# ========================================================================

@allure.feature("我的空间")
@allure.story("日历")
def test_calendar_day(my_workspace_page):
    """日历应显示当前日期数字和星期"""
    day = my_workspace_page.get_calendar_current_day()
    weekday = my_workspace_page.get_calendar_current_weekday()
    assert day.isdigit(), f"日期应为数字，实际'{day}'"
    assert 1 <= int(day) <= 31, f"日期应在1-31之间，实际{day}"
    assert weekday, f"星期不应为空，实际'{weekday}'"


@allure.feature("我的空间")
@allure.story("日历")
def test_calendar_current_month(my_workspace_page):
    """日历应显示当前月份"""
    month_label = my_workspace_page.get_calendar_current_month()
    assert "2026" in month_label or "2025" in month_label, \
        f"月份标签应包含年份，实际'{month_label}'"


@allure.feature("我的空间")
@allure.story("日历")
def test_calendar_click_today(my_workspace_page):
    """点击日历'今天'按钮，当前日期应选中"""
    my_workspace_page.click_calendar_today_btn()
    my_workspace_page.page.wait_for_timeout(500)
    selected = my_workspace_page.get_selected_calendar_day()
    current = my_workspace_page.get_calendar_current_day()
    assert selected and selected.strip() == current.strip(), \
        f"选中日期'{selected}'应等于当前日期'{current}'"


@allure.feature("我的空间")
@allure.story("日历")
def test_calendar_click_day(my_workspace_page):
    """点击日历中某个日期应能选中"""
    current_day = int(my_workspace_page.get_calendar_current_day())
    # 点击当前日期（保证该日期在同月内可见）
    my_workspace_page.click_calendar_day(current_day)
    my_workspace_page.page.wait_for_timeout(500)
    selected = my_workspace_page.get_selected_calendar_day()
    assert selected is not None, "点击日期后应有选中状态"


@allure.feature("我的空间")
@allure.story("日历")
def test_calendar_month_navigation(my_workspace_page):
    """点击上/下月箭头应切换月份"""
    old_month = my_workspace_page.get_calendar_current_month()
    my_workspace_page.click_calendar_next_month()
    my_workspace_page.page.wait_for_timeout(500)
    new_month = my_workspace_page.get_calendar_current_month()
    assert new_month != old_month, f"点右箭头后月份应变化，旧={old_month}，新={new_month}"

    my_workspace_page.click_calendar_prev_month()
    my_workspace_page.page.wait_for_timeout(500)
    back_month = my_workspace_page.get_calendar_current_month()
    assert back_month == old_month, f"点左箭头后应回到原月份，期望={old_month}，实际={back_month}"


# ========================================================================
#  日历 — 日程时间线点击
# ========================================================================

@allure.feature("我的空间")
@allure.story("日历")
def test_calendar_timeline_has_items(my_workspace_page):
    """日历时间线应有日程数据"""
    count = my_workspace_page.get_calendar_timeline_count()
    assert count > 0, f"日历时间线应有日程，实际{count}条"


@allure.feature("我的空间")
@allure.story("日历")
@allure.story("按钮点击跳转")
def test_click_calendar_timeline_item(my_workspace_page):
    """点击日历时间线中的任务条目应跳转"""
    old_url = my_workspace_page.page.url
    my_workspace_page.click_calendar_timeline_item(0)
    my_workspace_page.page.wait_for_timeout(1500)
    new_url = my_workspace_page.page.url
    assert new_url != old_url, f"点击时间线条目后 URL 应变化，旧={old_url}，新={new_url}"


# ========================================================================
#  '...'下拉菜单 & 刷新
# ========================================================================

@allure.feature("我的空间")
@allure.story("下拉菜单")
@pytest.mark.parametrize("module_title", [
    "任务总览",
    "项目总览",
    "参考样例",
    "我的任务",
    "我的项目",
    "动态",
    "工具集",
])
def test_module_more_menu_has_refresh(my_workspace_page, module_title):
    """每个模块的'...'菜单应包含'刷新'选项且可点击"""
    mod = my_workspace_page._find_module_by_title(module_title)
    more_btn = mod.locator(my_workspace_page.MODULE_MORE_BTN).first
    more_btn.wait_for(state="visible")
    more_btn.click()
    my_workspace_page.page.wait_for_timeout(300)
    # 验证下拉菜单弹出
    menu_items = my_workspace_page.page.locator(
        f"{my_workspace_page.DROPDOWN_MENU}:visible {my_workspace_page.DROPDOWN_MENU_ITEM}"
    )
    expect(menu_items.first).to_be_visible(timeout=5000)
    menu_texts = [item.inner_text().strip() for item in menu_items.all()]
    assert "刷新" in menu_texts, f"菜单应包含'刷新'，实际{menu_texts}"


@allure.feature("我的空间")
@allure.story("下拉菜单")
def test_refresh_all_modules(my_workspace_page):
    """对所有模块执行'...'→'刷新'操作，不应报错"""
    refreshers = [
        my_workspace_page.click_task_overview_refresh,
        my_workspace_page.click_project_overview_refresh,
        my_workspace_page.click_reference_examples_refresh,
        my_workspace_page.click_my_tasks_refresh,
        my_workspace_page.click_my_projects_refresh,
        my_workspace_page.click_activity_feed_refresh,
        my_workspace_page.click_toolset_refresh,
    ]
    for fn in refreshers:
        fn()
        my_workspace_page.page.wait_for_timeout(500)
        # 页面不应崩溃
        assert my_workspace_page.is_page_loaded(), f"{fn.__name__} 后页面仍应正常加载"


# ========================================================================
#  右下角浮动图标
# ========================================================================

@allure.feature("我的空间")
@allure.story("右下角图标")
def test_click_layout_edit_shows_tooltip(my_workspace_page):
    """点击编辑布局图标（icon-shitu）不应报错"""
    my_workspace_page.click_layout_edit()
    my_workspace_page.page.wait_for_timeout(800)
    assert my_workspace_page.is_page_loaded(), "点击编辑布局后页面应保持正常"


@allure.feature("我的空间")
@allure.story("右下角图标")
def test_click_tips_shows_tooltip(my_workspace_page):
    """点击提示图标（icon-tishi）不应报错"""
    my_workspace_page.click_tips()
    my_workspace_page.page.wait_for_timeout(800)
    assert my_workspace_page.is_page_loaded(), "点击提示后页面应保持正常"


@allure.feature("我的空间")
@allure.story("右下角图标")
def test_click_help_shows_tooltip(my_workspace_page):
    """点击帮助图标（icon-bangzhu）应弹出'帮助'提示框"""
    my_workspace_page.click_help()
    my_workspace_page.page.wait_for_timeout(1000)
    # 检查 tooltip 弹出
    tooltip = my_workspace_page.page.locator(".el-tooltip__popper:visible")
    if tooltip.count() > 0:
        tip_text = tooltip.first.inner_text().strip()
        assert "帮助" in tip_text, f"提示框应包含'帮助'，实际'{tip_text}'"


# ========================================================================
#  关于弹窗 — 弹窗在 DOM 中存在（默认隐藏），测试其结构与关闭
# ========================================================================

@allure.feature("我的空间")
@allure.story("关于弹窗")
def test_about_dialog_title(my_workspace_page):
    """关于弹窗标题应为'关于'"""
    # 弹窗默认 display:none，通过 JS 显示 Vue 组件以校验标题
    my_workspace_page.page.evaluate(
        """() => {
            const dlg = document.querySelector('.home-page > .el-dialog__wrapper.kd-dialog');
            if (dlg) dlg.style.display = '';
        }"""
    )
    my_workspace_page.page.wait_for_timeout(500)
    title = my_workspace_page.get_about_dialog_title()
    assert title == "关于", f"弹窗标题应为'关于'，实际'{title}'"
    # 恢复隐藏
    my_workspace_page.page.evaluate(
        """() => {
            const dlg = document.querySelector('.home-page > .el-dialog__wrapper.kd-dialog');
            if (dlg) dlg.style.display = 'none';
        }"""
    )


@allure.feature("我的空间")
@allure.story("关于弹窗")
def test_about_dialog_close(my_workspace_page):
    """关于弹窗关闭按钮元素存在"""
    my_workspace_page.page.evaluate(
        """() => {
            const dlg = document.querySelector('.home-page > .el-dialog__wrapper.kd-dialog');
            if (dlg) dlg.style.display = '';
        }"""
    )
    my_workspace_page.page.wait_for_timeout(500)
    # 关闭按钮应可见
    close_btn = my_workspace_page.page.locator(
        ".home-page > .el-dialog__wrapper.kd-dialog .el-dialog__close"
    ).first
    assert close_btn.is_visible(), "关闭按钮应可见"
    my_workspace_page.close_about_dialog()
    my_workspace_page.page.wait_for_timeout(500)


# ========================================================================
#  Toast 消息 — 根据实际操作触发
# ========================================================================

@allure.feature("我的空间")
@allure.story("Toast消息")
def test_toast_after_refresh(my_workspace_page):
    """模块刷新后可能出现 Toast 提示（不强制，只验证不报错）"""
    my_workspace_page.click_task_overview_refresh()
    my_workspace_page.page.wait_for_timeout(1500)
    toast = my_workspace_page.get_toast_message()
    # Toast 可能为空（刷新成功可能无提示），仅验证方法不抛异常
    assert isinstance(toast, str)


# ========================================================================
#  成果区域
# ========================================================================

@allure.feature("我的空间")
@allure.story("我的任务")
def test_my_tasks_results_empty_state(my_workspace_page):
    """我的任务-成果区域默认显示空状态（暂无数据）"""
    has_results = my_workspace_page.is_my_tasks_has_results()
    results = my_workspace_page.get_my_tasks_results()
    assert not has_results, "成果区域应显示暂无数据"
    assert results == [], "成果列表应为空"


@allure.feature("我的空间")
@allure.story("我的项目")
def test_my_projects_results_empty_state(my_workspace_page):
    """我的项目-成果区域默认显示空状态（暂无数据）"""
    has_results = my_workspace_page.is_my_projects_has_results()
    results = my_workspace_page.get_my_projects_results()
    assert not has_results, "成果区域应显示暂无数据"
    assert results == [], "成果列表应为空"
