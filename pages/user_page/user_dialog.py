"""
用户管理 - 弹窗页面对象

包含:
- UserDialog: 新增/编辑用户表单弹窗、查看用户弹窗、参与项目弹窗、列设置弹窗
"""

from playwright.sync_api import Page

from pages.component.column_settings import ColumnSettingsDialog


class UserDialog:
    """用户管理模块所有弹窗的页面对象"""

    def __init__(self, page: Page, container: str = "#pane-user"):
        """
        Args:
            page: Playwright Page 对象
            container: 弹窗所在的父容器选择器，如 "#pane-user"
        """
        self.page = page
        self._ctx = container
        self.column_settings = ColumnSettingsDialog(page, container=container)

    # ================= 弹窗基础选择器 =================

    @property
    def DIALOG_WRAPPER(self) -> str:
        # 不限定在 #pane-user 内；Element UI dialog 通常 append-to-body，渲染在 body 级别
        return "body>.el-dialog__wrapper.kd-dialog"

    # ================= 用户表单弹窗（新增/编辑） =================

    @property
    def USER_FORM_DIALOG(self) -> str:
        return (
            f'{self.DIALOG_WRAPPER}:not(:has(.title__text:has-text("列设置"))):'
            f'not(:has(.title__text:has-text("查看用户"))):'
            f'not(:has(.title__text:has-text("参与项目")))'
        )

    @property
    def USER_FORM_DIALOG_TITLE(self) -> str:
        return f"{self.USER_FORM_DIALOG} .title__text"

    @property
    def USER_FORM_DIALOG_CLOSE(self) -> str:
        return f"{self.USER_FORM_DIALOG} .el-dialog__close"

    @property
    def USER_FORM_DIALOG_CANCEL(self) -> str:
        return f"{self.USER_FORM_DIALOG} .el-dialog__footer .el-button--default"

    @property
    def USER_FORM_DIALOG_CONFIRM(self) -> str:
        return f"{self.USER_FORM_DIALOG} .el-dialog__footer .el-button--primary"

    # ================= 列设置弹窗 → 委托给 ColumnSettingsDialog (pages/component/column_settings.py)

    # ================= 查看用户弹窗 =================

    VIEW_USER_TITLE_SELECTOR = '.title__text:has-text("查看用户")'

    @property
    def VIEW_USER_DIALOG(self) -> str:
        return f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("查看用户"))'

    @property
    def VIEW_USER_TITLE(self) -> str:
        return f"{self.VIEW_USER_DIALOG} .title__text"

    @property
    def VIEW_USER_CLOSE(self) -> str:
        return f"{self.VIEW_USER_DIALOG} .el-dialog__close"

    @property
    def VIEW_USER_CONFIRM(self) -> str:
        return f"{self.VIEW_USER_DIALOG} .el-dialog__footer .el-button--primary"

    # ================= 参与项目弹窗 =================

    PROJECTS_DIALOG_TITLE_SELECTOR = '.title__text:has-text("参与项目")'

    @property
    def PROJECTS_DIALOG(self) -> str:
        return f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("参与项目"))'

    @property
    def PROJECTS_DIALOG_TITLE(self) -> str:
        return f"{self.PROJECTS_DIALOG} .title__text"

    @property
    def PROJECTS_DIALOG_CLOSE(self) -> str:
        return f"{self.PROJECTS_DIALOG} .el-dialog__close"

    @property
    def PROJECTS_DIALOG_CONFIRM(self) -> str:
        return f"{self.PROJECTS_DIALOG} .el-dialog__footer .el-button--primary"

    # ========================================================================
    #  通用弹窗方法
    # ========================================================================

    def _wait_for_selector(self, selector: str, timeout: int = 10000):
        """等待选择器对应的元素可见"""
        self.page.locator(selector).first.wait_for(state="visible", timeout=timeout)

    # ========================================================================
    #  通用确认弹窗（el-message-box — 禁用/启用 等操作共用）
    # ========================================================================

    # 确认弹窗可能的形式：
    #   A) .el-message-box__wrapper         → Element UI 消息确认框
    #   B) .el-dialog__wrapper.kd-dialog    → 自定义弹窗
    CONFIRM_DIALOG_A = ".el-message-box__wrapper"
    CONFIRM_DIALOG_B = ".el-dialog__wrapper.kd-dialog"

    @property
    def _confirm_dialog_selector(self) -> str:
        """返回当前可见的确认弹窗选择器"""
        for sel in (self.CONFIRM_DIALOG_A, self.CONFIRM_DIALOG_B):
            loc = self.page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                return sel
        return self.CONFIRM_DIALOG_A

    @property
    def CONFIRM_DIALOG_TITLE(self) -> str:
        return f"{self._confirm_dialog_selector} .el-message-box__title, {self._confirm_dialog_selector} .title__text"

    @property
    def CONFIRM_DIALOG_MESSAGE(self) -> str:
        return f"{self._confirm_dialog_selector} .el-message-box__message, {self._confirm_dialog_selector} .el-dialog__body"

    @property
    def CONFIRM_DIALOG_CONFIRM(self) -> str:
        return f"{self._confirm_dialog_selector} .el-message-box__btns .el-button--primary, {self._confirm_dialog_selector} .el-dialog__footer .el-button--primary"

    @property
    def CONFIRM_DIALOG_CANCEL(self) -> str:
        return f"{self._confirm_dialog_selector} .el-message-box__btns .el-button:not(.el-button--primary), {self._confirm_dialog_selector} .el-dialog__footer .el-button--default"

    def wait_for_confirm_dialog(self, timeout: int = 10000):
        """等待通用确认弹窗出现（兼容 message-box 和 kd-dialog）"""
        selector = f"{self.CONFIRM_DIALOG_A}:visible, {self.CONFIRM_DIALOG_B}:visible"
        self._wait_for_selector(selector, timeout=timeout)

    def is_confirm_dialog_open(self) -> bool:
        """通用确认弹窗是否打开"""
        return (
            self.page.locator(self.CONFIRM_DIALOG_A).first.is_visible()
            or self.page.locator(self.CONFIRM_DIALOG_B).first.is_visible()
        )

    def get_confirm_dialog_title(self) -> str:
        """获取确认弹窗标题"""
        self.wait_for_confirm_dialog()
        title_el = self.page.locator(self.CONFIRM_DIALOG_TITLE).first
        return title_el.inner_text().strip() if title_el.count() > 0 else ""

    def get_confirm_dialog_message(self) -> str:
        """获取确认弹窗消息文本"""
        msg_el = self.page.locator(self.CONFIRM_DIALOG_MESSAGE).first
        return msg_el.inner_text().strip() if msg_el.count() > 0 else ""

    def click_confirm_dialog_confirm(self):
        """点击确认弹窗的确定按钮"""
        self.page.locator(self.CONFIRM_DIALOG_CONFIRM).first.click()

    def click_confirm_dialog_cancel(self):
        """点击确认弹窗的取消按钮"""
        self.page.locator(self.CONFIRM_DIALOG_CANCEL).first.click()

    # ========================================================================
    #  用户表单弹窗（新增/编辑）方法
    # ========================================================================

    def wait_for_user_form_dialog(self, timeout: int = 10000):
        """等待新增/编辑用户弹窗出现"""
        self._wait_for_selector(f"{self.USER_FORM_DIALOG}:visible", timeout=timeout)

    def is_user_form_dialog_open(self) -> bool:
        """新增/编辑用户弹窗是否打开"""
        return self.page.locator(self.USER_FORM_DIALOG).first.is_visible()

    def get_user_form_dialog_title(self) -> str:
        """获取表单弹窗标题（新增用户 / 编辑用户）"""
        title_el = self.page.locator(f"{self.USER_FORM_DIALOG}:visible .title__text").first
        return title_el.inner_text().strip() if title_el.count() > 0 else ""

    def get_user_form_item_labels(self) -> list[str]:
        """获取用户表单弹窗中所有表单项的 label 文本列表"""
        form_dialog = self.page.locator(f"{self.USER_FORM_DIALOG}:visible").first
        labels = form_dialog.locator(".el-form-item__label").all()
        result = []
        for lbl in labels:
            text = lbl.inner_text().strip()
            if text:
                result.append(text)
        return result

    def _find_form_item(self, field_label: str):
        """在表单弹窗中定位指定 label 对应的 el-form-item"""
        form_dialog = self.page.locator(f"{self.USER_FORM_DIALOG}:visible").first
        return form_dialog.locator(f'.el-form-item:has-text("{field_label}")')

    # —— 字段读写 ——

    def get_field_value(self, field_label: str) -> str:
        """获取表单中指定 label 对应 input 的当前值"""
        form_item = self._find_form_item(field_label)
        if form_item.count() == 0:
            return ""
        input_el = form_item.locator("input.el-input__inner")
        if input_el.count() == 0:
            return ""
        return input_el.first.input_value() or ""

    def fill_field(self, field_label: str, value: str):
        """填充表单中单个字段（按 label 匹配 input）"""
        form_item = self._find_form_item(field_label)
        if form_item.count() > 0:
            input_el = form_item.locator("input.el-input__inner")
            if input_el.count() > 0:
                input_el.first.fill(str(value))

    def clear_field(self, field_label: str):
        """清空表单中指定 label 对应的 input"""
        form_item = self._find_form_item(field_label)
        if form_item.count() > 0:
            input_el = form_item.locator("input.el-input__inner")
            if input_el.count() > 0:
                input_el.first.clear()

    def fill_fields(self, **kwargs):
        """批量填充表单字段
        常见字段: 用户名, 姓名, 密码, 角色, 部门, 手机号, 邮箱 等
        """
        for field, value in kwargs.items():
            self.fill_field(field, str(value))

    def get_all_field_values(self) -> dict[str, str]:
        """获取表单中所有字段的 label → value 映射"""
        labels = self.get_user_form_item_labels()
        result = {}
        for label in labels:
            val = self.get_field_value(label)
            if val:
                result[label] = val
        return result

    # —— 字段校验错误 ——

    def get_field_error(self, field_label: str) -> str:
        """获取表单中指定 label 对应的校验错误提示文案"""
        form_item = self._find_form_item(field_label)
        if form_item.count() == 0:
            return ""
        error_el = form_item.locator(".el-form-item__error")
        if error_el.count() > 0:
            return error_el.first.inner_text().strip()
        return ""

    # —— 按钮状态 & 操作 ——

    def is_confirm_enabled(self) -> bool:
        """确定按钮是否可点击（未被 disabled）"""
        btn = self.page.locator(self.USER_FORM_DIALOG_CONFIRM).first
        if btn.count() == 0:
            return False
        cls = btn.get_attribute("class") or ""
        return "is-disabled" not in cls and "disabled" not in cls

    def click_confirm(self):
        """点击确定按钮"""
        self.page.locator(self.USER_FORM_DIALOG_CONFIRM).first.click()

    def click_cancel(self):
        """点击取消按钮"""
        self.page.locator(self.USER_FORM_DIALOG_CANCEL).first.click()

    def click_close(self):
        """点击弹窗右上角 X 关闭"""
        self.page.locator(f"{self.USER_FORM_DIALOG}:visible .el-dialog__close").first.click()

    # ========================================================================
    #  列设置弹窗方法 → 委托给 ColumnSettingsDialog 组件
    # ========================================================================

    def wait_for_column_settings_dialog(self, timeout: int = 10000):
        self.column_settings.wait_for_dialog(timeout=timeout)

    def is_column_settings_dialog_open(self) -> bool:
        return self.column_settings.is_open()

    def get_column_settings_dialog_title(self) -> str:
        return self.column_settings.get_title()

    def click_column_settings_cancel(self):
        self.column_settings.click_cancel()

    def click_column_settings_confirm(self):
        self.column_settings.click_confirm()

    def close_column_settings_dialog(self):
        self.column_settings.click_close()

    # ========================================================================
    #  查看用户弹窗方法
    # ========================================================================

    def wait_for_view_user_dialog(self, timeout: int = 10000):
        self._wait_for_selector(f"{self.VIEW_USER_DIALOG}:visible", timeout=timeout)

    def is_view_user_dialog_open(self) -> bool:
        return self.page.locator(self.VIEW_USER_DIALOG).first.is_visible()

    def get_view_user_dialog_title(self) -> str:
        self.wait_for_view_user_dialog()
        return self.page.locator(self.VIEW_USER_DIALOG).locator(".title__text").first.inner_text().strip()

    def get_view_user_dialog_body_text(self) -> str:
        """获取查看用户弹窗 body 文本内容"""
        body = self.page.locator(f"{self.VIEW_USER_DIALOG}:visible .el-dialog__body").first
        return body.inner_text().strip() if body.count() > 0 else ""

    def click_view_user_dialog_confirm(self):
        """点击查看用户弹窗的'确定'按钮"""
        self.page.locator(self.VIEW_USER_CONFIRM).first.click()

    def close_view_user_dialog(self):
        """关闭查看用户弹窗（点 X 或确定按钮）"""
        close_btn = self.page.locator(f"{self.VIEW_USER_DIALOG}:visible .el-dialog__close")
        if close_btn.count() > 0:
            close_btn.first.click()
        else:
            self.page.locator(self.VIEW_USER_CONFIRM).first.click()

    # ========================================================================
    #  重置密码弹窗（全局弹窗，可能在 #pane-user 内，也可能在 el-message-box 中）
    # ========================================================================

    # 对话框可能的形式：
    #   A) #pane-user .el-dialog__wrapper.kd-dialog  → 与其他弹窗结构一致
    #   B) body 下的 .el-message-box__wrapper         → Element UI 确认框
    RESET_PASSWORD_DIALOG_A = '.el-dialog__wrapper.kd-dialog:has(.title__text:has-text("重置密码"))'
    RESET_PASSWORD_DIALOG_B = '.el-message-box__wrapper'

    @property
    def _reset_dialog_selector(self) -> str:
        """返回当前可见的重置密码弹窗选择器（优先匹配 kd-dialog，其次 message-box）"""
        # 优先匹配带"重置密码"标题的 kd-dialog
        loc_a = self.page.locator(self.RESET_PASSWORD_DIALOG_A)
        if loc_a.count() > 0 and loc_a.first.is_visible():
            return self.RESET_PASSWORD_DIALOG_A
        # 兜底：匹配 message-box
        return self.RESET_PASSWORD_DIALOG_B

    @property
    def RESET_PASSWORD_TITLE(self) -> str:
        return f"{self._reset_dialog_selector} .el-message-box__title, {self._reset_dialog_selector} .title__text"

    @property
    def RESET_PASSWORD_CLOSE(self) -> str:
        return f"{self._reset_dialog_selector} .el-message-box__headerbtn, {self._reset_dialog_selector} .el-dialog__close"

    @property
    def RESET_PASSWORD_CONFIRM(self) -> str:
        return f"{self._reset_dialog_selector} .el-message-box__btns .el-button--primary, {self._reset_dialog_selector} .el-dialog__footer .el-button--primary"

    @property
    def RESET_PASSWORD_CANCEL(self) -> str:
        return f"{self._reset_dialog_selector} .el-message-box__btns .el-button:not(.el-button--primary), {self._reset_dialog_selector} .el-dialog__footer .el-button--default"

    @property
    def RESET_PASSWORD_BODY(self) -> str:
        return f"{self._reset_dialog_selector} .el-message-box__message, {self._reset_dialog_selector} .el-dialog__body"

    def wait_for_reset_password_dialog(self, timeout: int = 10000):
        """等待重置密码弹窗出现（兼容 kd-dialog 和 el-message-box）"""
        selector = f"{self.RESET_PASSWORD_DIALOG_A}:visible, {self.RESET_PASSWORD_DIALOG_B}:visible"
        self._wait_for_selector(selector, timeout=timeout)

    def is_reset_password_dialog_open(self) -> bool:
        """重置密码弹窗是否打开"""
        return (
            self.page.locator(self.RESET_PASSWORD_DIALOG_A).first.is_visible()
            or self.page.locator(self.RESET_PASSWORD_DIALOG_B).first.is_visible()
        )

    def get_reset_password_dialog_title(self) -> str:
        """获取重置密码弹窗标题"""
        self.wait_for_reset_password_dialog()
        title_el = self.page.locator(self.RESET_PASSWORD_TITLE).first
        return title_el.inner_text().strip() if title_el.count() > 0 else ""

    def get_reset_password_dialog_body_text(self) -> str:
        """获取重置密码弹窗 body 文本（提示语）"""
        body = self.page.locator(self.RESET_PASSWORD_BODY).first
        return body.inner_text().strip() if body.count() > 0 else ""

    def click_reset_password_confirm(self):
        """点击重置密码弹窗的确定按钮"""
        self.page.locator(self.RESET_PASSWORD_CONFIRM).first.click()

    def click_reset_password_cancel(self):
        """点击重置密码弹窗的取消按钮"""
        self.page.locator(self.RESET_PASSWORD_CANCEL).first.click()

    def close_reset_password_dialog(self):
        """点击重置密码弹窗右上角 X 关闭"""
        self.page.locator(self.RESET_PASSWORD_CLOSE).first.click()

    # ========================================================================
    #  参与项目弹窗方法
    # ========================================================================

    def wait_for_projects_dialog(self, timeout: int = 10000):
        self._wait_for_selector(f"{self.PROJECTS_DIALOG}:visible", timeout=timeout)

    def is_projects_dialog_open(self) -> bool:
        return self.page.locator(self.PROJECTS_DIALOG).first.is_visible()

    def get_projects_dialog_title(self) -> str:
        return self.page.locator(self.PROJECTS_DIALOG_TITLE).first.inner_text().strip()

    def get_projects_dialog_body_text(self) -> str:
        body = self.page.locator(f"{self.PROJECTS_DIALOG}:visible .el-dialog__body").first
        return body.inner_text().strip() if body.count() > 0 else ""

    def close_projects_dialog(self):
        """关闭参与项目弹窗"""
        self.page.locator(self.PROJECTS_DIALOG_CLOSE).first.click()

    def click_projects_dialog_confirm(self):
        """关闭参与项目弹窗的确定按钮"""
        self.page.locator(self.PROJECTS_DIALOG_CONFIRM).first.click()