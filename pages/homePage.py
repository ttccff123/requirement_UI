from core.base_page import BasePage


class HomePage(BasePage):
    """需求工具首页：左侧导航菜单

    基于实际 DOM 结构（Element UI + 自定义 Vue 组件）：
    - 侧边栏容器：div.sidebar-box
    - 新建按钮：  div.add-btn > button.el-button--primary
    - 菜单项：    div.menu-row（图标 <i> + 文本 <div>）
    - 我的方案：  div.scheme-box 内 Element UI Tree（span.custom-tree-node-label）
    - 该页面无侧边栏折叠/展开功能，顶部 header 也无汉堡菜单
    """

    # -- 核心选择器（按实际 DOM 编写） --
    SIDEBAR = ".sidebar-box"
    SIDEBAR_CONTENT = ".sidebar-box-content"
    MENU_ROW = ".sidebar-box-content .menu-row"
    SCHEME_LABEL = ".custom-tree-node-label"
    NEW_BUTTON = ".add-btn button.el-button--primary"

    # 所有可见菜单项的中文名 → 右侧约定定位策略
    # 普通菜单：通过 .menu-row 文本匹配
    # 我的方案：通过 .custom-tree-node-label
    # 新建：    通过 .add-btn button
    _MENU_DEFS: tuple[tuple[str, str, str], ...] = (
        # (中文名, 定位策略, 右边约定说明)
        ("新建",         "new_button",  ".add-btn button.el-button--primary"),
        ("原始需求",     "menu_row",    ".menu-row"),
        ("最近打开",     "menu_row",    ".menu-row"),
        ("我的方案",     "scheme_label",".custom-tree-node-label"),
        ("我的收藏",     "menu_row",    ".menu-row"),
        ("回收站",       "menu_row",    ".menu-row"),
        ("下载管理",     "menu_row",    ".menu-row"),
        ("文档模板",     "menu_row",    ".menu-row"),
        ("属性设置",     "menu_row",    ".menu-row"),
        ("数据资源",     "menu_row",    ".menu-row"),
    )

    def __init__(self, page):
        super().__init__(page)

    # ================= 导航 =================

    def open(self, url: str):
        """打开需求工具首页并等待侧边栏加载"""
        self.navigate_to(url)
        self.wait_for_page()

    def wait_for_page(self, timeout: int = 15000):
        """等待侧边栏容器可见"""
        self.page.locator(self.SIDEBAR).first.wait_for(state="visible", timeout=timeout)

    def get_sidebar(self):
        """返回侧边栏容器定位器"""
        return self.page.locator(self.SIDEBAR).first

    # ================= 定位 =================

    def get_menu_by_name(self, menu_name: str):
        """按菜单中文名返回可点击的定位器。

        查找优先级：
        1. 普通菜单行 (.menu-row) — 包含图标和文本的 div
        2. 方案树标签 (.custom-tree-node-label) — 仅"我的方案"
        3. Playwright 内置文本匹配 — 兜底
        """
        # 1) 普通菜单行：.sidebar-box-content .menu-row
        locator = (self.page.locator(self.MENU_ROW)
                   .filter(has_text=menu_name)
                   .first)
        if locator.count() > 0:
            return locator

        # 2) 方案树标签："我的方案" 在 Element UI Tree 中
        locator = (self.page.locator(self.SCHEME_LABEL)
                   .filter(has_text=menu_name)
                   .first)
        if locator.count() > 0:
            return locator

        # 3) 兜底：在整个侧边栏内按精确文本查找
        return self.page.locator(self.SIDEBAR).get_by_text(menu_name, exact=True).first

    # ================= 点击操作 =================

    def click_menu(self, menu_name: str):
        """点击左侧菜单项（force=True 绕过可能的浮层拦截）"""
        locator = self.get_menu_by_name(menu_name)
        locator.click(force=True)
        return self

    def click_new(self):
        """点击「新建」按钮（该按钮在菜单区上方，不是 div.menu-row）"""
        self.page.locator(self.NEW_BUTTON).first.click(force=True)
        return self

    def click_raw_requirements(self):
        return self.click_menu("原始需求")

    def click_recent_open(self):
        return self.click_menu("最近打开")

    def click_my_solutions(self):
        return self.click_menu("我的方案")

    def click_my_collection(self):
        return self.click_menu("我的收藏")

    def click_recycle_bin(self):
        return self.click_menu("回收站")

    def click_download_management(self):
        return self.click_menu("下载管理")

    def click_document_templates(self):
        return self.click_menu("文档模板")

    def click_property_settings(self):
        return self.click_menu("属性设置")

    def click_data_resources(self):
        return self.click_menu("数据资源")
