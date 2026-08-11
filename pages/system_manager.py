from core.base_page import BasePage


class SystemManagerPage(BasePage):
    """右上角用户成员图标与弹出子菜单

    基于实际 DOM 结构（Element UI el-popover）：
    - 入口：   div.user-menu > i.iconfont.icon-yonghu_chengyuan（用户图标）
    - 主菜单： div.el-popper.user-menu-popover > div.user-menu-main
    - 菜单项： div.user-menu-item（"帮助" 带 special 类 + 右箭头，可展开子级）
    - 帮助子菜单：div.el-popper.user-menu-popover.user-menu-help-popover
    """

    # -- 核心选择器（按实际 DOM） --
    USER_MENU_TRIGGER = ".user-menu"
    USER_ICON = ".user-menu .icon-yonghu_chengyuan"
    POPOVER = ".user-menu-popover"
    POPOVER_VISIBLE = ".user-menu-popover:visible"
    POPOVER_MAIN = ".user-menu-main"
    MENU_ITEM = ".user-menu-item"
    HELP_SUB_POPOVER = ".user-menu-help-popover"
    HELP_TRIGGER = ".user-menu-item.special"  # 带 special 类的帮助项

    def __init__(self, page):
        super().__init__(page)

    # ================= 图标入口 =================

    def wait_for_user_member_icon(self, timeout: int = 15000):
        """等待用户图标出现"""
        self.page.locator(self.USER_ICON).first.wait_for(
            state="visible", timeout=timeout
        )

    def get_user_member_icon(self):
        """返回用户图标定位器"""
        return self.page.locator(self.USER_ICON).first

    def click_user_member_icon(self):
        """点击用户图标，弹出主菜单"""
        icon = self.get_user_member_icon()
        if icon.count() == 0:
            raise AssertionError("未找到用户图标: .user-menu .icon-yonghu_chengyuan")
        icon.click()
        # 等待 popover 可见
        self.page.locator(self.POPOVER).first.wait_for(
            state="visible", timeout=5000
        )
        return self

    # ================= 主菜单 =================

    def get_sub_menu(self):
        """返回弹出的主菜单容器（el-popover）"""
        return self.page.locator(self.POPOVER).first

    def is_sub_menu_visible(self) -> bool:
        """判断主菜单是否已弹出"""
        menu = self.get_sub_menu()
        return menu.count() > 0 and menu.is_visible()

    def get_sub_menu_items(self):
        """返回主菜单中的所有可见菜单项（限定在可见的 popover 内）"""
        return (
            self.page.locator(self.POPOVER_VISIBLE)
            .locator(self.POPOVER_MAIN)
            .locator(self.MENU_ITEM)
        )

    def get_sub_menu_item(self, item_text: str):
        """按文本获取主菜单项定位器（限定在可见 popover 内）"""
        locator = (
            self.page.locator(self.POPOVER_VISIBLE)
            .locator(self.MENU_ITEM)
            .filter(has_text=item_text)
            .first
        )
        if locator.count() == 0:
            # 兜底：在可见 popover 内按文本匹配
            locator = (
                self.page.locator(self.POPOVER_VISIBLE)
                .get_by_text(item_text, exact=False)
                .first
            )
        return locator

    def click_sub_menu_item(self, item_text: str):
        """弹出菜单后点击指定文本的菜单项"""
        self.click_user_member_icon()
        locator = self.get_sub_menu_item(item_text)
        if locator.count() == 0:
            self.close_sub_menu()
            raise AssertionError(f"未找到菜单项: {item_text}")
        locator.click()
        return self

    def click_first_sub_menu_item(self):
        """点击主菜单第一个可见项"""
        self.click_user_member_icon()
        self.get_sub_menu_items().first.click()
        return self

    def close_sub_menu(self):
        """关闭所有弹出菜单（再次点击用户图标切换关闭）"""
        if self.is_sub_menu_visible() or self.page.locator(f"{self.POPOVER}:visible").count() > 0:
            self.get_user_member_icon().click()
            self.page.wait_for_timeout(300)
        return self

    # ================= 帮助子菜单 =================

    def open_help_sub_menu(self):
        """展开「帮助」子菜单（click 触发 el-popover）"""
        if not self.is_sub_menu_visible():
            self.click_user_member_icon()
        help_item = self.page.locator(self.HELP_TRIGGER).first
        if help_item.count() == 0:
            raise AssertionError("未找到「帮助」菜单项")
        # 使用 JS 原生 click 触发 Vue 的 popover 展示
        help_item.evaluate("el => el.click()")
        self.page.locator(self.HELP_SUB_POPOVER).first.wait_for(
            state="visible", timeout=5000
        )
        return self

    def get_help_sub_menu_items(self):
        """返回帮助子菜单中的所有项"""
        return self.page.locator(self.HELP_SUB_POPOVER).locator(self.MENU_ITEM)

    def click_help_sub_menu_item(self, item_text: str):
        """点击帮助子菜单中的项"""
        self.open_help_sub_menu()
        locator = (
            self.page.locator(self.HELP_SUB_POPOVER)
            .locator(self.MENU_ITEM)
            .filter(has_text=item_text)
            .first
        )
        if locator.count() == 0:
            raise AssertionError(f"未找到帮助子菜单项: {item_text}")
        locator.click()
        return self
