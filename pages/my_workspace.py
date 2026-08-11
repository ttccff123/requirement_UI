from playwright.sync_api import Locator

from pages.base_page import BasePage
from pages.component.toast import Toast


class MyWorkspace(BasePage):
    """体系数字工程开发平台 - 我的空间页面对象（登录后默认首页 #/home，右侧为可拖拽模块网格）"""

    def __init__(self, page):
        super().__init__(page)
        self.toast = Toast(page)

    # ================= 页面整体 =================
    PAGE_CONTAINER = ".home-page"
    PAGE_TITLE = ".home-page-header"
    GRID_LAYOUT = ".vue-grid-layout.dashboard-layout"
    GRID_ITEM = f"{GRID_LAYOUT} .vue-grid-item"

    # ================= 公共模块结构 =================
    MODULE_LAYOUT = ".module-layout"
    MODULE_HEADER = ".header-box"
    MODULE_HEADER_LEFT = ".header-left"
    MODULE_HEADER_RIGHT = ".header-right"
    MODULE_TITLE = f"{MODULE_HEADER_LEFT} div"
    MODULE_MORE_BTN = f"{MODULE_HEADER_RIGHT} .el-icon-more"          # "..."更多按钮
    MODULE_ARROW_BTN = f"{MODULE_HEADER_RIGHT} .el-icon-arrow-right"  # 跳转箭头
    MODULE_CONTENT = ".content-box"
    # "..."展开后的下拉菜单
    DROPDOWN_MENU = ".el-dropdown-menu.el-popper"
    DROPDOWN_MENU_ITEM = f"{DROPDOWN_MENU} .el-dropdown-menu__item"

    # ================= Toast =================

    def get_toast_message(self) -> str:
        """获取页面 Toast 提示文案"""
        return self.toast.get_message()

    # ================= 关于弹窗（.home-page 直接子级） =================
    ABOUT_DIALOG = ".home-page > .el-dialog__wrapper.kd-dialog"
    ABOUT_DIALOG_TITLE = f"{ABOUT_DIALOG} .kd-dialog__title .title__text"
    ABOUT_DIALOG_CLOSE = f"{ABOUT_DIALOG} .el-dialog__close"

    # ================= 右下角浮动按钮 =================
    BOTTOM_BTN_BOX = ".home-page-btn-box"
    LAYOUT_EDIT_BTN = f"{BOTTOM_BTN_BOX} .home-page-btn .icon-shitu"   # 编辑布局图标
    TIPS_BTN = f"{BOTTOM_BTN_BOX} .home-page-tool .icon-tishi"          # 提示图标
    HELP_BTN = f"{BOTTOM_BTN_BOX} .home-page-tool .icon-bangzhu"        # 帮助图标

    # ============================================================
    #  模块一：任务总览
    #  info-left（标题 + 数字 + 查看任务按钮）+ line + info-right（ECharts）
    # ============================================================
    TASK_OVERVIEW_INFO_LEFT = ".info-left"
    TASK_OVERVIEW_INFO_TITLE = f"{TASK_OVERVIEW_INFO_LEFT} .info-title"
    TASK_OVERVIEW_COUNT = f"{TASK_OVERVIEW_INFO_LEFT} div"
    TASK_OVERVIEW_VIEW_BTN = f"{TASK_OVERVIEW_INFO_LEFT} .el-button--primary"

    # ============================================================
    #  模块二：项目总览（结构同任务总览）
    # ============================================================
    PROJECT_OVERVIEW_INFO_LEFT = ".info-left"
    PROJECT_OVERVIEW_INFO_TITLE = f"{PROJECT_OVERVIEW_INFO_LEFT} .info-title"
    PROJECT_OVERVIEW_COUNT = f"{PROJECT_OVERVIEW_INFO_LEFT} div"
    PROJECT_OVERVIEW_VIEW_BTN = f"{PROJECT_OVERVIEW_INFO_LEFT} .el-button--primary"

    # ============================================================
    #  模块三：参考样例（空状态）
    # ============================================================
    REFERENCE_EXAMPLES_NO_DATA = ".noData"

    # ============================================================
    #  模块四：我的任务
    #  left-box（任务列表）+ right-box（top-box 详情 + list-box 成果 + bottom-box 按钮）
    # ============================================================
    MY_TASKS_LEFT = ".left-box"
    MY_TASKS_LEFT_ITEMS = f"{MY_TASKS_LEFT} .line-box"
    MY_TASKS_LEFT_ITEM_ACTIVE = ".line-box.active-line"
    MY_TASKS_LEFT_ITEM_ICON = ".line-icon img"
    MY_TASKS_LEFT_ITEM_NAME = ".line-content"
    MY_TASKS_RIGHT = ".right-box"
    MY_TASKS_RIGHT_TOP = ".top-box"
    MY_TASKS_RIGHT_INFO_BOX = ".info-box"
    MY_TASKS_INFO_TIME = ".info-time"
    MY_TASKS_INFO_LIST = ".info-list"
    MY_TASKS_INFO_LIST_STATUS = ".info-list-status"
    MY_TASKS_INFO_LIST_DES = ".info-list-des"
    MY_TASKS_INFO_NAME = ".info-name"
    MY_TASKS_INFO_DES = ".info-des"
    MY_TASKS_PROGRESS = ".progress"
    MY_TASKS_LIST_BOX = ".list-box"
    MY_TASKS_LIST_TITLE = ".list-title"
    MY_TASKS_LIST_OUTER = ".list-line-outer"
    MY_TASKS_NO_DATA = ".noData"
    MY_TASKS_BOTTOM = ".bottom-box"
    MY_TASKS_HANDLE_BTN = f"{MY_TASKS_BOTTOM} .el-button--primary"

    # ============================================================
    #  模块五：我的项目（结构同我的任务）
    # ============================================================
    MY_PROJECTS_LEFT = ".left-box"
    MY_PROJECTS_LEFT_ITEMS = f"{MY_PROJECTS_LEFT} .line-box"
    MY_PROJECTS_LEFT_ITEM_ACTIVE = ".line-box.active-line"
    MY_PROJECTS_LEFT_ITEM_ICON = ".line-icon i"
    MY_PROJECTS_LEFT_ITEM_NAME = ".line-content"
    MY_PROJECTS_RIGHT = ".right-box"
    MY_PROJECTS_RIGHT_TOP = ".top-box"
    MY_PROJECTS_RIGHT_INFO_BOX = ".info-box"
    MY_PROJECTS_INFO_TIME = ".info-time"
    MY_PROJECTS_INFO_LIST = ".info-list"
    MY_PROJECTS_INFO_LIST_STATUS = ".info-list-status"
    MY_PROJECTS_INFO_LIST_DES = ".info-list-des"
    MY_PROJECTS_INFO_NAME = ".info-name"
    MY_PROJECTS_INFO_DES = ".info-des"
    MY_PROJECTS_PROGRESS = ".progress"
    MY_PROJECTS_LIST_BOX = ".list-box"
    MY_PROJECTS_LIST_TITLE = ".list-title"
    MY_PROJECTS_LIST_OUTER = ".list-line-outer"
    MY_PROJECTS_NO_DATA = ".noData"
    MY_PROJECTS_BOTTOM = ".bottom-box"
    MY_PROJECTS_HANDLE_BTN = f"{MY_PROJECTS_BOTTOM} .el-button--primary"

    # ============================================================
    #  模块六：动态
    #  scrollbar-box 内 line-box 列表
    # ============================================================
    ACTIVITY_FEED_SCROLLBAR = ".scrollbar-box"
    ACTIVITY_FEED_ITEMS = f"{ACTIVITY_FEED_SCROLLBAR} .line-box"
    ACTIVITY_FEED_ITEM_TIP = ".line-box-tip"
    ACTIVITY_FEED_ITEM_DESC = ".line-box-dec"
    ACTIVITY_FEED_ITEM_TIME = ".line-box-time"

    # ============================================================
    #  模块七：工具集
    #  center-box 内 item-box 列表
    # ============================================================
    TOOLSET_ITEMS = ".center-box .item-box"
    TOOLSET_ITEM_DISABLED = ".item-box-disable"
    TOOLSET_ITEM_ICON = ".item-box-icon img"
    TOOLSET_ITEM_TITLE = ".item-box-title"

    # ============================================================
    #  模块八：日历（无 module-layout，使用 module-box）
    #  current-data + change-btn-group + data-analysis(日历) + timeLine_box(日程)
    # ============================================================
    CALENDAR_MODULE = ".module-box"
    CALENDAR_CURRENT_DAY = f"{CALENDAR_MODULE} .current-data span:first-child"
    CALENDAR_CURRENT_WEEKDAY = f"{CALENDAR_MODULE} .current-data span:last-child"
    CALENDAR_MONTH_LABEL = f"{CALENDAR_MODULE} .change-btn-group div"
    CALENDAR_PREV_YEAR = ".el-icon-d-arrow-left"
    CALENDAR_PREV_MONTH = ".el-icon-arrow-left"
    CALENDAR_NEXT_MONTH = ".el-icon-arrow-right"
    CALENDAR_NEXT_YEAR = ".el-icon-d-arrow-right"
    CALENDAR_TODAY_BTN = ".el-calendar__button-group button:has-text(\"今天\")"
    CALENDAR_PREV_MONTH_BTN = ".el-calendar__button-group button:has-text(\"上个月\")"
    CALENDAR_NEXT_MONTH_BTN = ".el-calendar__button-group button:has-text(\"下个月\")"
    CALENDAR_BODY = ".data-analysis .el-calendar"
    CALENDAR_TABLE = f"{CALENDAR_BODY} .el-calendar-table"
    CALENDAR_DAY_CELL = f"{CALENDAR_TABLE} td .el-calendar-day .div-Calendar span.active"
    CALENDAR_TODAY_CELL = f"{CALENDAR_TABLE} td.is-today .div-Calendar span.active"
    CALENDAR_SELECTED_CELL = f"{CALENDAR_TABLE} td.is-selected .div-Calendar span.active"
    CALENDAR_TIMELINE = ".timeLine_box"
    CALENDAR_TIMELINE_ITEMS = f"{CALENDAR_TIMELINE} .el-timeline-item"
    CALENDAR_TL_DATE = ".timeLine_data"
    CALENDAR_TL_TITLE = ".timeLine_title .title"
    CALENDAR_TL_SUBTITLE = ".timeLine_title .sub-title"
    CALENDAR_TL_TIP = ".info-tip"

    # ========================================================================
    #  通用定位 — 按模块标题在所有 .vue-grid-item 中查找 .module-layout
    # ========================================================================

    def _find_module_by_title(self, title: str) -> Locator:
        """按标题文字定位模块的 .module-layout 根元素"""
        items = self.page.locator(self.GRID_ITEM).all()
        for item in items:
            header = item.locator(self.MODULE_TITLE)
            if header.count() > 0 and header.first.inner_text().strip() == title:
                return item.locator(self.MODULE_LAYOUT).first
        # 兜底：直接用文本匹配
        return self.page.locator(f"{self.MODULE_LAYOUT}:has(.header-left:has-text(\"{title}\"))").first

    def _find_calendar_module(self) -> Locator:
        """日历模块使用 .module-box 而非 .module-layout"""
        items = self.page.locator(self.GRID_ITEM).all()
        for item in items:
            if item.locator(self.CALENDAR_MODULE).count() > 0:
                return item.locator(self.CALENDAR_MODULE).first
        return self.page.locator(self.CALENDAR_MODULE).first

    def _open_module_more_menu(self, module_locator: Locator):
        """展开模块标题栏右侧的"..."下拉菜单"""
        more_btn = module_locator.locator(self.MODULE_MORE_BTN).first
        more_btn.wait_for(state="visible")
        more_btn.click()

    def _click_dropdown_item(self, item_text: str):
        """点击已展开的下拉菜单中的指定项（如'刷新'）"""
        locator = self.page.locator(f"{self.DROPDOWN_MENU_ITEM}:has-text(\"{item_text}\")")
        locator.first.wait_for(state="visible")
        locator.first.click()

    # ========================================================================
    #  页面级
    # ========================================================================

    def wait_for_page(self, timeout: int = 30000):
        """等待我的空间页面加载完成"""
        self.wait_for_selector(self.PAGE_CONTAINER, timeout=timeout)
        self.page.locator(self.PAGE_CONTAINER).first.wait_for(state="visible", timeout=timeout)

    def is_page_loaded(self) -> bool:
        return self.page.locator(self.PAGE_CONTAINER).first.is_visible()

    def get_page_title(self) -> str:
        """获取页面标题'我的空间'"""
        self.wait_for_page()
        return self.page.locator(self.PAGE_TITLE).first.inner_text().strip()

    # -- 关于弹窗 --

    def open_about_dialog(self):
        """点击帮助图标打开关于弹窗"""
        self.page.locator(self.HELP_BTN).first.click()

    def wait_for_about_dialog(self, timeout: int = 15000):
        self.wait_for_selector(self.ABOUT_DIALOG, timeout=timeout)

    def get_about_dialog_title(self) -> str:
        self.wait_for_about_dialog()
        return self.page.locator(self.ABOUT_DIALOG_TITLE).first.inner_text().strip()

    def close_about_dialog(self):
        self.page.locator(self.ABOUT_DIALOG_CLOSE).first.click()

    def is_about_dialog_open(self) -> bool:
        return self.page.locator(self.ABOUT_DIALOG).first.is_visible()

    # -- 右下角浮动按钮 --

    def click_layout_edit(self):
        """点击右下角编辑布局图标（icon-shitu）"""
        self.page.locator(self.LAYOUT_EDIT_BTN).first.click()

    def click_tips(self):
        """点击右下角提示图标（icon-tishi）"""
        self.page.locator(self.TIPS_BTN).first.click()

    def click_help(self):
        """点击右下角帮助图标（icon-bangzhu）"""
        self.page.locator(self.HELP_BTN).first.click()

    # ========================================================================
    #  模块一：任务总览
    # ========================================================================

    def _task_overview(self) -> Locator:
        return self._find_module_by_title("任务总览")

    def get_task_overview_title(self) -> str:
        mod = self._task_overview()
        return mod.locator(self.TASK_OVERVIEW_INFO_TITLE).first.inner_text().strip() if mod.locator(self.TASK_OVERVIEW_INFO_TITLE).count() > 0 else ""

    def get_task_overview_count(self) -> int | None:
        mod = self._task_overview()
        for div in mod.locator(self.TASK_OVERVIEW_COUNT).all():
            text = div.inner_text().strip()
            if text.isdigit():
                return int(text)
        return None

    def click_task_overview_view(self):
        """点击'查看任务'按钮"""
        self._task_overview().locator(self.TASK_OVERVIEW_VIEW_BTN).first.click()

    def click_task_overview_more(self):
        """展开任务总览的'...'菜单"""
        self._open_module_more_menu(self._task_overview())

    def click_task_overview_refresh(self):
        """任务总览 - '...' → '刷新'"""
        self.click_task_overview_more()
        self._click_dropdown_item("刷新")

    # ========================================================================
    #  模块二：项目总览
    # ========================================================================

    def _project_overview(self) -> Locator:
        return self._find_module_by_title("项目总览")

    def get_project_overview_title(self) -> str:
        mod = self._project_overview()
        return mod.locator(self.PROJECT_OVERVIEW_INFO_TITLE).first.inner_text().strip() if mod.locator(self.PROJECT_OVERVIEW_INFO_TITLE).count() > 0 else ""

    def get_project_overview_count(self) -> int | None:
        mod = self._project_overview()
        for div in mod.locator(self.PROJECT_OVERVIEW_COUNT).all():
            text = div.inner_text().strip()
            if text.isdigit():
                return int(text)
        return None

    def click_project_overview_view(self):
        """点击'查看项目'按钮"""
        self._project_overview().locator(self.PROJECT_OVERVIEW_VIEW_BTN).first.click()

    def click_project_overview_more(self):
        """展开项目总览的'...'菜单"""
        self._open_module_more_menu(self._project_overview())

    def click_project_overview_refresh(self):
        """项目总览 - '...' → '刷新'"""
        self.click_project_overview_more()
        self._click_dropdown_item("刷新")

    # ========================================================================
    #  模块三：参考样例
    # ========================================================================

    def _reference_examples(self) -> Locator:
        return self._find_module_by_title("参考样例")

    def is_reference_examples_empty(self) -> bool:
        return self._reference_examples().locator(self.REFERENCE_EXAMPLES_NO_DATA).first.is_visible()

    def click_reference_examples_more(self):
        """展开参考样例的'...'菜单"""
        self._open_module_more_menu(self._reference_examples())

    def click_reference_examples_refresh(self):
        """参考样例 - '...' → '刷新'"""
        self.click_reference_examples_more()
        self._click_dropdown_item("刷新")

    # ========================================================================
    #  模块四：我的任务
    # ========================================================================

    def _my_tasks(self) -> Locator:
        return self._find_module_by_title("我的任务")

    # -- 左侧任务列表 --

    def get_my_tasks_list(self) -> list[str]:
        items = self._my_tasks().locator(self.MY_TASKS_LEFT_ITEMS).all()
        return [i.locator(self.MY_TASKS_LEFT_ITEM_NAME).first.inner_text().strip() for i in items]

    def get_my_tasks_active_item(self) -> str | None:
        active = self._my_tasks().locator(self.MY_TASKS_LEFT_ITEM_ACTIVE).first
        if active.count() == 0:
            return None
        return active.locator(self.MY_TASKS_LEFT_ITEM_NAME).first.inner_text().strip()

    def click_my_tasks_item(self, task_name: str):
        """点击左侧任务名称，切换右侧详情"""
        mod = self._my_tasks()
        loc = mod.locator(f"{self.MY_TASKS_LEFT_ITEMS}:has-text(\"{task_name}\")")
        loc.first.wait_for(state="visible")
        loc.first.click()

    # -- 右侧详情 --

    def get_my_tasks_detail(self) -> dict[str, str | None]:
        """获取右侧当前任务的详情

        Returns: {time, project, type, assignee, status, overview}
        """
        mod = self._my_tasks()
        info_box = mod.locator(self.MY_TASKS_RIGHT_INFO_BOX).first
        if info_box.count() == 0:
            return {}

        time_str = info_box.locator(self.MY_TASKS_INFO_TIME).first.inner_text().strip() if info_box.locator(self.MY_TASKS_INFO_TIME).count() > 0 else ""

        fields = {}
        for row in info_box.locator(self.MY_TASKS_INFO_LIST).all():
            text = row.inner_text().strip()
            sep = "：" if "：" in text else ":"
            if sep in text:
                key, _, val = text.partition(sep)
                fields[key] = val.strip()

        status = ""
        sr = info_box.locator(self.MY_TASKS_INFO_LIST_STATUS).first
        if sr.count() > 0:
            p = sr.locator(self.MY_TASKS_PROGRESS).first
            if p.count() > 0:
                status = p.inner_text().strip()

        overview = ""
        dr = info_box.locator(self.MY_TASKS_INFO_LIST_DES).first
        if dr.count() > 0:
            d = dr.locator(self.MY_TASKS_INFO_DES).first
            if d.count() > 0:
                overview = d.inner_text().strip()

        return {
            "time": time_str,
            "project": fields.get("所属项目", ""),
            "type": fields.get("任务类型", ""),
            "assignee": fields.get("负责人", ""),
            "status": status,
            "overview": overview,
        }

    def get_my_tasks_results(self) -> list[str]:
        outer = self._my_tasks().locator(self.MY_TASKS_LIST_OUTER).first
        if outer.count() == 0:
            return []
        return [item.inner_text().strip() for item in outer.locator("> div:not(.noData)").all()]

    def is_my_tasks_has_results(self) -> bool:
        outer = self._my_tasks().locator(self.MY_TASKS_LIST_OUTER).first
        return outer.locator(self.MY_TASKS_NO_DATA).count() == 0

    # -- 按钮操作 --

    def click_my_tasks_handle(self):
        """点击'处理任务'按钮"""
        self._my_tasks().locator(self.MY_TASKS_HANDLE_BTN).first.click()

    def click_my_tasks_arrow(self):
        """点击我的任务标题栏右侧跳转箭头"""
        self._my_tasks().locator(self.MODULE_ARROW_BTN).first.click()

    def click_my_tasks_more(self):
        """展开我的任务的'...'菜单"""
        self._open_module_more_menu(self._my_tasks())

    def click_my_tasks_refresh(self):
        """我的任务 - '...' → '刷新'"""
        self.click_my_tasks_more()
        self._click_dropdown_item("刷新")

    # ========================================================================
    #  模块五：我的项目
    # ========================================================================

    def _my_projects(self) -> Locator:
        return self._find_module_by_title("我的项目")

    # -- 左侧项目列表 --

    def get_my_projects_list(self) -> list[str]:
        items = self._my_projects().locator(self.MY_PROJECTS_LEFT_ITEMS).all()
        return [i.locator(self.MY_PROJECTS_LEFT_ITEM_NAME).first.inner_text().strip() for i in items]

    def get_my_projects_active_item(self) -> str | None:
        active = self._my_projects().locator(self.MY_PROJECTS_LEFT_ITEM_ACTIVE).first
        if active.count() == 0:
            return None
        return active.locator(self.MY_PROJECTS_LEFT_ITEM_NAME).first.inner_text().strip()

    def click_my_projects_item(self, project_name: str):
        """点击左侧项目名称，切换右侧详情"""
        mod = self._my_projects()
        loc = mod.locator(f"{self.MY_PROJECTS_LEFT_ITEMS}:has-text(\"{project_name}\")")
        loc.first.wait_for(state="visible")
        loc.first.click()

    # -- 右侧详情 --

    def get_my_projects_detail(self) -> dict[str, str | None]:
        """获取右侧当前项目的详情

        Returns: {time, name, leader, status, overview}
        """
        mod = self._my_projects()
        info_box = mod.locator(self.MY_PROJECTS_RIGHT_INFO_BOX).first
        if info_box.count() == 0:
            return {}

        time_str = info_box.locator(self.MY_PROJECTS_INFO_TIME).first.inner_text().strip() if info_box.locator(self.MY_PROJECTS_INFO_TIME).count() > 0 else ""

        fields = {}
        for row in info_box.locator(self.MY_PROJECTS_INFO_LIST).all():
            text = row.inner_text().strip()
            sep = "：" if "：" in text else ":"
            if sep in text:
                key, _, val = text.partition(sep)
                fields[key] = val.strip()

        status = ""
        sr = info_box.locator(self.MY_PROJECTS_INFO_LIST_STATUS).first
        if sr.count() > 0:
            p = sr.locator(self.MY_PROJECTS_PROGRESS).first
            if p.count() > 0:
                status = p.inner_text().strip()

        overview = ""
        dr = info_box.locator(self.MY_PROJECTS_INFO_LIST_DES).first
        if dr.count() > 0:
            d = dr.locator(self.MY_PROJECTS_INFO_DES).first
            if d.count() > 0:
                overview = d.inner_text().strip()

        return {
            "time": time_str,
            "name": fields.get("项目名称", ""),
            "leader": fields.get("负责人", ""),
            "status": status,
            "overview": overview,
        }

    def get_my_projects_results(self) -> list[str]:
        outer = self._my_projects().locator(self.MY_PROJECTS_LIST_OUTER).first
        if outer.count() == 0:
            return []
        return [item.inner_text().strip() for item in outer.locator("> div:not(.noData)").all()]

    def is_my_projects_has_results(self) -> bool:
        outer = self._my_projects().locator(self.MY_PROJECTS_LIST_OUTER).first
        return outer.locator(self.MY_PROJECTS_NO_DATA).count() == 0

    # -- 按钮操作 --

    def click_my_projects_handle(self):
        """点击'处理项目'按钮"""
        self._my_projects().locator(self.MY_PROJECTS_HANDLE_BTN).first.click()

    def click_my_projects_arrow(self):
        """点击我的项目标题栏右侧跳转箭头"""
        self._my_projects().locator(self.MODULE_ARROW_BTN).first.click()

    def click_my_projects_more(self):
        """展开我的项目的'...'菜单"""
        self._open_module_more_menu(self._my_projects())

    def click_my_projects_refresh(self):
        """我的项目 - '...' → '刷新'"""
        self.click_my_projects_more()
        self._click_dropdown_item("刷新")

    # ========================================================================
    #  模块六：动态
    # ========================================================================

    def _activity_feed(self) -> Locator:
        return self._find_module_by_title("动态")

    def get_activity_feed_items(self) -> list[dict[str, str]]:
        """Returns: [{"type": "通知", "content": "...", "time": "..."}, ...]"""
        items = self._activity_feed().locator(self.ACTIVITY_FEED_ITEMS).all()
        result = []
        for item in items:
            t = item.locator(self.ACTIVITY_FEED_ITEM_TIP).first.inner_text().strip() if item.locator(self.ACTIVITY_FEED_ITEM_TIP).count() > 0 else ""
            d = item.locator(self.ACTIVITY_FEED_ITEM_DESC).first.inner_text().strip() if item.locator(self.ACTIVITY_FEED_ITEM_DESC).count() > 0 else ""
            tm = item.locator(self.ACTIVITY_FEED_ITEM_TIME).first.inner_text().strip() if item.locator(self.ACTIVITY_FEED_ITEM_TIME).count() > 0 else ""
            result.append({"type": t, "content": d, "time": tm})
        return result

    def get_activity_feed_count(self) -> int:
        return self._activity_feed().locator(self.ACTIVITY_FEED_ITEMS).count()

    def click_activity_feed_more(self):
        """展开动态的'...'菜单"""
        self._open_module_more_menu(self._activity_feed())

    def click_activity_feed_refresh(self):
        """动态 - '...' → '刷新'"""
        self.click_activity_feed_more()
        self._click_dropdown_item("刷新")

    # ========================================================================
    #  模块七：工具集
    # ========================================================================

    def _toolset(self) -> Locator:
        return self._find_module_by_title("工具集")

    def get_toolset_items(self) -> list[dict[str, bool | str]]:
        """Returns: [{"name": "概念开发", "disabled": True}, ...]"""
        items = self._toolset().locator(self.TOOLSET_ITEMS).all()
        result = []
        for item in items:
            name = item.locator(self.TOOLSET_ITEM_TITLE).first.inner_text().strip() if item.locator(self.TOOLSET_ITEM_TITLE).count() > 0 else ""
            disabled = "item-box-disable" in (item.get_attribute("class") or "")
            result.append({"name": name, "disabled": disabled})
        return result

    def get_toolset_item_count(self) -> int:
        return self._toolset().locator(self.TOOLSET_ITEMS).count()

    def click_toolset_item(self, tool_name: str):
        """点击工具集中指定名称的工具"""
        mod = self._toolset()
        loc = mod.locator(f"{self.TOOLSET_ITEMS}:has-text(\"{tool_name}\")")
        loc.first.wait_for(state="visible")
        loc.first.click()

    def click_toolset_more(self):
        """展开工具集的'...'菜单"""
        self._open_module_more_menu(self._toolset())

    def click_toolset_refresh(self):
        """工具集 - '...' → '刷新'"""
        self.click_toolset_more()
        self._click_dropdown_item("刷新")

    # ========================================================================
    #  模块八：日历
    # ========================================================================

    # -- 日期信息 --

    def get_calendar_current_day(self) -> str:
        self.page.locator(self.CALENDAR_CURRENT_DAY).first.wait_for(state="visible")
        return self.page.locator(self.CALENDAR_CURRENT_DAY).first.inner_text().strip()

    def get_calendar_current_weekday(self) -> str:
        return self.page.locator(self.CALENDAR_CURRENT_WEEKDAY).first.inner_text().strip()

    def get_calendar_current_month(self) -> str:
        return self.page.locator(self.CALENDAR_MONTH_LABEL).first.inner_text().strip()

    # -- 月份导航 --

    def click_calendar_prev_year(self):
        self.page.locator(self.CALENDAR_PREV_YEAR).first.click()

    def click_calendar_prev_month(self):
        """日历标题区左箭头（上个月）"""
        self.page.locator(self.CALENDAR_PREV_MONTH).first.click()

    def click_calendar_next_month(self):
        """日历标题区右箭头（下个月）"""
        self.page.locator(self.CALENDAR_NEXT_MONTH).first.click()

    def click_calendar_next_year(self):
        self.page.locator(self.CALENDAR_NEXT_YEAR).first.click()

    # -- 按钮：上个月 / 今天 / 下个月 --

    def click_calendar_prev_month_btn(self):
        """点击'上个月'按钮"""
        self.page.locator(self.CALENDAR_PREV_MONTH_BTN).first.click()

    def click_calendar_today_btn(self):
        """点击'今天'按钮"""
        self.page.locator(self.CALENDAR_TODAY_BTN).first.click()

    def click_calendar_next_month_btn(self):
        """点击'下个月'按钮"""
        self.page.locator(self.CALENDAR_NEXT_MONTH_BTN).first.click()

    # -- 日期点击 --

    def click_calendar_day(self, day: int):
        """点击日历中指定日期数字（1-31）"""
        cells = self.page.locator(self.CALENDAR_DAY_CELL).all()
        for cell in cells:
            if cell.inner_text().strip() == str(day):
                cell.click()
                return

    def click_calendar_today_cell(self):
        """点击今天日期"""
        self.page.locator(self.CALENDAR_TODAY_CELL).first.click()

    def get_selected_calendar_day(self) -> str | None:
        el = self.page.locator(self.CALENDAR_SELECTED_CELL).first
        if el.count() == 0:
            return None
        return el.inner_text().strip()

    # -- 日程时间线 --

    def get_calendar_timeline_items(self) -> list[dict[str, str]]:
        """Returns: [{"date_range": "...", "tip": "即将到期", "task": "wx_req", "project": "defaultProjectName"}, ...]"""
        items = self.page.locator(self.CALENDAR_TIMELINE_ITEMS).all()
        result = []
        for item in items:
            dr = item.locator(self.CALENDAR_TL_DATE).first.inner_text().strip() if item.locator(self.CALENDAR_TL_DATE).count() > 0 else ""
            tip = item.locator(self.CALENDAR_TL_TIP).first.inner_text().strip() if item.locator(self.CALENDAR_TL_TIP).count() > 0 else ""
            tn = item.locator(self.CALENDAR_TL_TITLE).first.inner_text().strip() if item.locator(self.CALENDAR_TL_TITLE).count() > 0 else ""
            pn = item.locator(self.CALENDAR_TL_SUBTITLE).first.inner_text().strip() if item.locator(self.CALENDAR_TL_SUBTITLE).count() > 0 else ""
            result.append({"date_range": dr, "tip": tip, "task": tn, "project": pn})
        return result

    def get_calendar_timeline_count(self) -> int:
        return self.page.locator(self.CALENDAR_TIMELINE_ITEMS).count()

    def click_calendar_timeline_item(self, index: int):
        self.page.locator(self.CALENDAR_TIMELINE_ITEMS).nth(index).click()
