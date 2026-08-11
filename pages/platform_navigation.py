from playwright.sync_api import Locator

from pages.base_page import BasePage


class PlatformNavigation(BasePage):
    """体系数字工程开发平台 - 登录后左侧导航栏页面对象"""

    # 左侧导航
    SIDEBAR = ".kd-aside"
    LOGO = ".kd-logo"
    NAV_MENU = ".app-menu.kd-menu"
    MENU_ITEMS = f"{NAV_MENU} .app-menu-item"
    ACTIVE_MENU_ITEM = f"{MENU_ITEMS}.active"
    MENU_ITEM_ICON = "i.iconfont"
    MENU_ITEM_NAME = ".app-menu-name"

    # 侧边栏底部
    SIDEBAR_FOOTER = ".kd-aside-footer"
    FOOTER_MAIL_ICON = f"{SIDEBAR_FOOTER} .icon-youjian_mian"       # 邮件图标
    USER_MENU_TRIGGER = f"{SIDEBAR_FOOTER} .el-popover__reference-wrapper"
    USER_MENU_POPOVER = ".user-menu-popover"
    USER_MENU_ITEMS = ".user-menu-item"

    # 用户信息（在 user-menu-main 中）
    USER_AVATAR = ".user-menu-main .el-avatar"
    USER_NAME = ".user-menu-main .user-name"

    def wait_for_sidebar(self, timeout: int = 30000):
        """等待左侧导航可见"""
        self.wait_for_selector(self.SIDEBAR, timeout=timeout)

    def get_navigation_items(self) -> list[str]:
        """返回侧边栏菜单项文本列表（如：我的空间、项目、成果、组织）"""
        self.wait_for_sidebar()
        locator = self.page.locator(self.MENU_ITEMS)
        locator.first.wait_for(state="visible")
        return [item.locator(self.MENU_ITEM_NAME).first.inner_text().strip()
                for item in locator.all()
                if item.locator(self.MENU_ITEM_NAME).first.inner_text().strip()]

    def get_active_navigation_item(self) -> str:
        """获取当前高亮/选中的菜单项文本"""
        self.wait_for_sidebar()
        locator = self.page.locator(self.ACTIVE_MENU_ITEM)
        locator.first.wait_for(state="visible")
        return locator.locator(self.MENU_ITEM_NAME).first.inner_text().strip()

    def _menu_item_locator(self, item_text: str) -> Locator:
        return self.page.locator(f"{self.MENU_ITEMS}:has-text(\"{item_text}\")")

    def click_navigation_item(self, item_text: str):
        """点击指定菜单项"""
        locator = self._menu_item_locator(item_text)
        locator.first.wait_for(state="visible")
        locator.first.click()

    def is_navigation_item_visible(self, item_text: str) -> bool:
        locator = self._menu_item_locator(item_text)
        return locator.first.is_visible()

    def get_navigation_item_icon_class(self, item_text: str) -> str | None:
        """获取菜单项图标的 iconfont class（如 icon-wodekongjian_mian）"""
        locator = self._menu_item_locator(item_text).first
        locator.wait_for(state="visible")
        icon = locator.locator(self.MENU_ITEM_ICON).first
        if icon.count() == 0:
            return None
        cls = icon.get_attribute("class") or ""
        # 提取 iconfont icon-xxx 中的 icon-xxx 部分
        for name in cls.split():
            if name.startswith("icon-"):
                return name
        return cls

    # -- 侧边栏底部用户区 --

    def get_user_name(self) -> str:
        """获取登录用户名"""
        self.wait_for_sidebar()
        if self.page.locator(self.USER_NAME).count() > 0:
            return self.page.locator(self.USER_NAME).first.inner_text().strip()
        return ""

    def get_user_avatar_url(self) -> str | None:
        """获取用户头像 URL"""
        locator = self.page.locator(self.USER_AVATAR).first
        if locator.count() == 0:
            return None
        return locator.locator("img").get_attribute("src") if locator.locator("img").count() > 0 else None

    def open_user_menu(self):
        """打开侧边栏底部用户菜单"""
        self.page.locator(self.USER_MENU_TRIGGER).first.click()

    def click_user_menu_item(self, item_text: str):
        """点击用户菜单中的指定项"""
        self.open_user_menu()
        locator = self.page.locator(f"{self.USER_MENU_ITEMS}:has-text(\"{item_text}\")")
        locator.first.wait_for(state="visible")
        locator.first.click()

    def click_mail_icon(self):
        """点击侧边栏底部邮件图标"""
        self.page.locator(self.FOOTER_MAIL_ICON).first.click()
