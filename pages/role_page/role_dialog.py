"""
角色管理 - 弹窗页面对象

包含：
- 新增/编辑/复制角色表单弹窗
- 删除角色确认弹窗
- 成员管理弹窗
- 功能权限弹窗
"""
from playwright.sync_api import Page


class RoleDialog:
    """角色管理模块所有弹窗的页面对象"""

    def __init__(self, page: Page):
        self.page = page

    # ================= 弹窗选择器 =================

    @property
    def DIALOG_WRAPPER(self) -> str:
        """所有 kd-dialog 弹窗（append-to-body，渲染在 body 级别）"""
        return "body>.el-dialog__wrapper.kd-dialog"

    # ================= 角色表单弹窗（新增/编辑/复制） =================

    @property
    def ROLE_FORM_DIALOG(self) -> str:
        return (
            f'{self.DIALOG_WRAPPER}:not(:has(.title__text:has-text("成员管理"))):'
            f'not(:has(.title__text:has-text("功能权限")))'
        )

    @property
    def ROLE_FORM_TITLE(self) -> str:
        return f"{self.ROLE_FORM_DIALOG}:visible .title__text"

    @property
    def ROLE_FORM_CLOSE(self) -> str:
        return f"{self.ROLE_FORM_DIALOG}:visible .el-dialog__close"

    @property
    def ROLE_FORM_CONFIRM(self) -> str:
        return f"{self.ROLE_FORM_DIALOG}:visible .el-dialog__footer .el-button--primary"

    @property
    def ROLE_FORM_CANCEL(self) -> str:
        return f"{self.ROLE_FORM_DIALOG}:visible .el-dialog__footer .el-button--default"

    @property
    def ROLE_FORM_BODY(self) -> str:
        return f"{self.ROLE_FORM_DIALOG}:visible .el-dialog__body"

    # ================= 成员管理弹窗 =================

    @property
    def MEMBER_DIALOG(self) -> str:
        return f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("添加角色成员"))'

    @property
    def MEMBER_DIALOG_TITLE(self) -> str:
        return f"{self.MEMBER_DIALOG}:visible .title__text"

    @property
    def MEMBER_DIALOG_CLOSE(self) -> str:
        return f"{self.MEMBER_DIALOG}:visible .el-dialog__close"

    @property
    def MEMBER_DIALOG_CONFIRM(self) -> str:
        return f"{self.MEMBER_DIALOG}:visible .el-dialog__footer .el-button--primary"

    @property
    def MEMBER_DIALOG_CANCEL(self) -> str:
        return f"{self.MEMBER_DIALOG}:visible .el-dialog__footer .el-button--default"

    # ================= 功能权限弹窗 =================

    @property
    def PERMISSION_DIALOG(self) -> str:
        return f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("功能权限"))'

    @property
    def PERMISSION_DIALOG_TITLE(self) -> str:
        return f"{self.PERMISSION_DIALOG}:visible .title__text"

    @property
    def PERMISSION_DIALOG_CLOSE(self) -> str:
        return f"{self.PERMISSION_DIALOG}:visible .el-dialog__close"

    @property
    def PERMISSION_DIALOG_CONFIRM(self) -> str:
        return f"{self.PERMISSION_DIALOG}:visible .el-dialog__footer .el-button--primary"

    @property
    def PERMISSION_DIALOG_CANCEL(self) -> str:
        return f"{self.PERMISSION_DIALOG}:visible .el-dialog__footer .el-button--default"

    # ================= 通用确认弹窗（删除等） =================
    CONFIRM_DIALOG_A = ".el-message-box__wrapper"
    CONFIRM_DIALOG_B = ".el-dialog__wrapper.kd-dialog"

    @property
    def CONFIRM_DIALOG_MESSAGE(self) -> str:
        return f"{self.CONFIRM_DIALOG_A} .el-message-box__message, {self.CONFIRM_DIALOG_B} .el-dialog__body"

    @property
    def CONFIRM_DIALOG_CONFIRM(self) -> str:
        return (
            f"{self.CONFIRM_DIALOG_A}:visible .el-message-box__btns .el-button--primary,"
            f"{self.CONFIRM_DIALOG_B}:visible .el-dialog__footer .el-button--primary"
        )

    @property
    def CONFIRM_DIALOG_CANCEL(self) -> str:
        return (
            f"{self.CONFIRM_DIALOG_A}:visible .el-message-box__btns .el-button:not(.el-button--primary),"
            f"{self.CONFIRM_DIALOG_B}:visible .el-dialog__footer .el-button--default"
        )

    # ================= 基础方法 =================

    def _wait_for_selector(self, selector: str, timeout: int = 5000):
        self.page.locator(selector).first.wait_for(state="visible", timeout=timeout)

    # ================= 角色表单弹窗 =================

    def wait_for_role_form_dialog(self, timeout: int = 10000):
        self._wait_for_selector(f"{self.ROLE_FORM_DIALOG}:visible", timeout=timeout)

    def is_role_form_dialog_open(self) -> bool:
        return self.page.locator(self.ROLE_FORM_DIALOG).first.is_visible()

    def wait_for_form_dialog_closed(self, timeout: int = 3000):
        """等待角色表单弹窗关闭（用于确认/取消/关闭后）。"""
        try:
            self.page.locator(f"{self.ROLE_FORM_DIALOG}:visible").first.wait_for(
                state="hidden", timeout=timeout
            )
        except Exception:
            pass

    def get_role_form_title(self) -> str:
        el = self.page.locator(self.ROLE_FORM_TITLE).first
        return el.inner_text().strip() if el.count() > 0 else ""

    def click_role_form_confirm(self):
        self.page.locator(self.ROLE_FORM_CONFIRM).first.click()

    def click_role_form_cancel(self):
        self.page.locator(self.ROLE_FORM_CANCEL).first.click()

    def click_role_form_close(self):
        self.page.locator(self.ROLE_FORM_CLOSE).first.click()

    def _find_form_item(self, field_label: str):
        """在角色表单弹窗中定位指定 label 的 el-form-item"""
        return self.page.locator(
            f'{self.ROLE_FORM_DIALOG}:visible .el-form-item:has-text("{field_label}")'
        ).first

    def fill_role_field(self, field_label: str, value: str):
        """填充角色表单中指定 label 的 input 或 textarea"""
        form_item = self._find_form_item(field_label)
        if form_item.count() == 0:
            return
        # 优先 textarea，其次 input
        ta = form_item.locator("textarea.el-textarea__inner").first
        if ta.count() > 0:
            ta.fill(str(value))
            return
        inp = form_item.locator("input.el-input__inner").first
        if inp.count() > 0:
            inp.fill(str(value))

    def clear_role_field(self, field_label: str):
        """清空指定字段"""
        form_item = self._find_form_item(field_label)
        if form_item.count() == 0:
            return
        ta = form_item.locator("textarea.el-textarea__inner").first
        if ta.count() > 0:
            ta.fill("")
            return
        inp = form_item.locator("input.el-input__inner").first
        if inp.count() > 0:
            inp.fill("")

    def get_role_field_value(self, field_label: str) -> str:
        """获取指定字段值（input 或 textarea）"""
        form_item = self._find_form_item(field_label)
        if form_item.count() == 0:
            return ""
        ta = form_item.locator("textarea.el-textarea__inner").first
        if ta.count() > 0:
            return ta.input_value() or ""
        inp = form_item.locator("input.el-input__inner").first
        if inp.count() > 0:
            return inp.input_value() or ""
        return ""

    def get_role_field_error(self, field_label: str) -> str:
        """获取字段校验错误提示"""
        form_item = self._find_form_item(field_label)
        if form_item.count() == 0:
            return ""
        err = form_item.locator(".el-form-item__error").first
        if err.count() > 0:
            return err.inner_text().strip()
        return ""

    def get_role_field_placeholder(self, field_label: str) -> str:
        """获取字段的 placeholder"""
        form_item = self._find_form_item(field_label)
        if form_item.count() == 0:
            return ""
        ta = form_item.locator("textarea.el-textarea__inner").first
        if ta.count() > 0:
            return ta.get_attribute("placeholder") or ""
        inp = form_item.locator("input.el-input__inner").first
        if inp.count() > 0:
            return inp.get_attribute("placeholder") or ""
        return ""

    # ================= 成员管理弹窗 =================

    def wait_for_member_dialog(self, timeout: int = 10000):
        self._wait_for_selector(f"{self.MEMBER_DIALOG}:visible", timeout=timeout)

    def is_member_dialog_open(self) -> bool:
        return self.page.locator(self.MEMBER_DIALOG).first.is_visible()

    def click_member_dialog_confirm(self):
        self.page.locator(self.MEMBER_DIALOG_CONFIRM).first.click()

    def click_member_dialog_cancel(self):
        self.page.locator(self.MEMBER_DIALOG_CANCEL).first.click()

    def click_member_dialog_close(self):
        self.page.locator(self.MEMBER_DIALOG_CLOSE).first.click()

    # ================= 功能权限弹窗 =================

    def wait_for_permission_dialog(self, timeout: int = 10000):
        self._wait_for_selector(f"{self.PERMISSION_DIALOG}:visible", timeout=timeout)

    def is_permission_dialog_open(self) -> bool:
        return self.page.locator(self.PERMISSION_DIALOG).first.is_visible()

    def click_permission_dialog_confirm(self):
        self.page.locator(self.PERMISSION_DIALOG_CONFIRM).first.click()

    def click_permission_dialog_cancel(self):
        self.page.locator(self.PERMISSION_DIALOG_CANCEL).first.click()

    def click_permission_dialog_close(self):
        self.page.locator(self.PERMISSION_DIALOG_CLOSE).first.click()

    # ================= 查看用户弹窗 =================

    @property
    def VIEW_USER_DIALOG(self) -> str:
        return f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("查看用户"))'

    @property
    def VIEW_USER_DIALOG_TITLE(self) -> str:
        return f"{self.VIEW_USER_DIALOG}:visible .title__text"

    @property
    def VIEW_USER_DIALOG_CLOSE(self) -> str:
        return f"{self.VIEW_USER_DIALOG}:visible .el-dialog__close"

    @property
    def VIEW_USER_DIALOG_CONFIRM(self) -> str:
        return f"{self.VIEW_USER_DIALOG}:visible .el-dialog__footer .el-button--primary"

    def wait_for_view_user_dialog(self, timeout: int = 10000):
        self._wait_for_selector(f"{self.VIEW_USER_DIALOG}:visible", timeout=timeout)

    def is_view_user_dialog_open(self) -> bool:
        return self.page.locator(self.VIEW_USER_DIALOG).first.is_visible()

    def get_view_user_dialog_title(self) -> str:
        self.wait_for_view_user_dialog()
        return self.page.locator(self.VIEW_USER_DIALOG_TITLE).first.inner_text().strip()

    def get_view_user_dialog_body_text(self) -> str:
        body = self.page.locator(f"{self.VIEW_USER_DIALOG}:visible .el-dialog__body").first
        return body.inner_text().strip() if body.count() > 0 else ""

    def click_view_user_dialog_confirm(self):
        self.page.locator(self.VIEW_USER_DIALOG_CONFIRM).first.click()

    def close_view_user_dialog(self):
        close_btn = self.page.locator(self.VIEW_USER_DIALOG_CLOSE)
        if close_btn.count() > 0:
            close_btn.first.click()
        else:
            self.page.locator(self.VIEW_USER_DIALOG_CONFIRM).first.click()

    # ================= 参与项目弹窗 =================

    @property
    def PROJECTS_DIALOG(self) -> str:
        return f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("参与项目"))'

    @property
    def PROJECTS_DIALOG_TITLE(self) -> str:
        return f"{self.PROJECTS_DIALOG}:visible .title__text"

    @property
    def PROJECTS_DIALOG_CLOSE(self) -> str:
        return f"{self.PROJECTS_DIALOG}:visible .el-dialog__close"

    @property
    def PROJECTS_DIALOG_CONFIRM(self) -> str:
        return f"{self.PROJECTS_DIALOG}:visible .el-dialog__footer .el-button--primary"

    def wait_for_projects_dialog(self, timeout: int = 10000):
        self._wait_for_selector(f"{self.PROJECTS_DIALOG}:visible", timeout=timeout)

    def is_projects_dialog_open(self) -> bool:
        return self.page.locator(self.PROJECTS_DIALOG).first.is_visible()

    def get_projects_dialog_title(self) -> str:
        return self.page.locator(self.PROJECTS_DIALOG_TITLE).first.inner_text().strip()

    def close_projects_dialog(self):
        self.page.locator(self.PROJECTS_DIALOG_CLOSE).first.click()

    def click_projects_dialog_confirm(self):
        btn = self.page.locator(self.PROJECTS_DIALOG_CONFIRM).first
        if btn.count() > 0 and btn.is_visible():
            btn.click()
        else:
            self.close_projects_dialog()

    # ================= 通用确认弹窗 =================

    def wait_for_confirm_dialog(self, timeout: int = 10000):
        self._wait_for_selector(
            f"{self.CONFIRM_DIALOG_A}:visible, {self.CONFIRM_DIALOG_B}:visible",
            timeout=timeout,
        )

    def is_confirm_dialog_open(self) -> bool:
        return (
            self.page.locator(self.CONFIRM_DIALOG_A).first.is_visible()
            or self.page.locator(self.CONFIRM_DIALOG_B).first.is_visible()
        )

    def get_confirm_dialog_message(self) -> str:
        el = self.page.locator(self.CONFIRM_DIALOG_MESSAGE).first
        return el.inner_text().strip() if el.count() > 0 else ""

    def click_confirm_dialog_confirm(self):
        self.page.locator(self.CONFIRM_DIALOG_CONFIRM).first.click()

    def click_confirm_dialog_cancel(self):
        self.page.locator(self.CONFIRM_DIALOG_CANCEL).first.click()
