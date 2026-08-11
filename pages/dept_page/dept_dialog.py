"""
部门管理 - 弹窗页面对象

包含：
- 新增/编辑部门表单弹窗
- 删除部门确认弹窗
- 成员管理弹窗
- 查看用户弹窗
- 参与项目弹窗
"""
from playwright.sync_api import Page


class DeptDialog:
    """部门管理模块所有弹窗的页面对象"""

    def __init__(self, page: Page):
        self.page = page

    # ================= 弹窗选择器 =================

    @property
    def DIALOG_WRAPPER(self) -> str:
        """所有 kd-dialog 弹窗（append-to-body，渲染在 body 级别）"""
        return "body>.el-dialog__wrapper.kd-dialog"

    # ================= 部门表单弹窗（新增/编辑） =================

    @property
    def DEPT_FORM_DIALOG(self) -> str:
        # 精确匹配部门表单弹窗：标题含"部门"但不含"成员"
        return (
            f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("部门"))'
            f':not(:has(.title__text:has-text("成员"))),'
            # 回退：标题含"新建"或"编辑"但不含"成员"/"角色"/"用户"
            f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("新建"))'
            f':not(:has(.title__text:has-text("角色"))),'
            f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("编辑"))'
            f':not(:has(.title__text:has-text("角色")))'
        )

    @property
    def DEPT_FORM_TITLE(self) -> str:
        return f"{self.DEPT_FORM_DIALOG}:visible .title__text"

    @property
    def DEPT_FORM_CLOSE(self) -> str:
        return f"{self.DEPT_FORM_DIALOG}:visible .el-dialog__close"

    @property
    def DEPT_FORM_CONFIRM(self) -> str:
        return f"{self.DEPT_FORM_DIALOG}:visible .el-dialog__footer .el-button--primary"

    @property
    def DEPT_FORM_CANCEL(self) -> str:
        return f"{self.DEPT_FORM_DIALOG}:visible .el-dialog__footer .el-button--default"

    @property
    def DEPT_FORM_BODY(self) -> str:
        return f"{self.DEPT_FORM_DIALOG}:visible .el-dialog__body"

    # ================= 成员管理弹窗 =================

    @property
    def MEMBER_DIALOG(self) -> str:
        # 部门成员管理弹窗标题可能是"添加部门成员"或"成员管理"或"添加成员"
        return (
            f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("添加部门成员")),'
            f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("部门成员")),'
            f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("添加成员")):not(:has(.title__text:has-text("角色"))),'
            f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("成员管理")):not(:has(.title__text:has-text("角色")))'
        )

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

    # ================= 部门表单弹窗 =================

    def wait_for_dept_form_dialog(self, timeout: int = 10000):
        self._wait_for_selector(f"{self.DEPT_FORM_DIALOG}:visible", timeout=timeout)

    def is_dept_form_dialog_open(self) -> bool:
        dlg = self._visible_form_dialog()
        el = self.page.locator(dlg).first
        return el.count() > 0 and el.is_visible()

    def wait_for_form_dialog_closed(self, timeout: int = 2000):
        """等待部门表单弹窗关闭。"""
        try:
            self.page.locator(f"{self.DEPT_FORM_DIALOG}:visible").first.wait_for(
                state="hidden", timeout=timeout
            )
        except Exception:
            pass

    def get_dept_form_title(self) -> str:
        dlg = self._visible_form_dialog()
        # 尝试多种可能的标题选择器
        for sel in [".title__text", ".el-dialog__title", ".kd-dialog__title", "h3", ".dialog-title"]:
            el = self.page.locator(f"{dlg} {sel}").first
            if el.count() > 0:
                text = el.inner_text().strip()
                if text:
                    return text
        # 回退：取弹窗内第一个可见文本
        body = self.page.locator(f"{dlg} .el-dialog__body").first
        return body.inner_text().strip()[:50] if body.count() > 0 else ""

    def _visible_form_dialog(self) -> str:
        """返回当前真正可见的部门表单弹窗选择器（动态检测，避免匹配成员弹窗）。"""
        for title in ["部门", "新建", "编辑"]:
            sel = (
                f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("{title}"))'
                f':not(:has(.title__text:has-text("成员"))):visible'
            )
            el = self.page.locator(sel).first
            if el.count() > 0 and el.is_visible():
                return sel
        return f"{self.DIALOG_WRAPPER}:visible"

    def click_dept_form_confirm(self):
        dlg = self._visible_form_dialog()
        btn = self.page.locator(f"{dlg} .el-dialog__footer .el-button--primary").first
        if btn.count() > 0:
            btn.click()
        else:
            # 有些弹窗没有 footer 按钮，尝试 Enter 键
            self.page.keyboard.press("Enter")

    def click_dept_form_cancel(self):
        dlg = self._visible_form_dialog()
        btn = self.page.locator(f"{dlg} .el-dialog__footer .el-button--default").first
        if btn.count() > 0:
            btn.click()
        else:
            self.page.keyboard.press("Escape")

    def click_dept_form_close(self):
        dlg = self._visible_form_dialog()
        btn = self.page.locator(f"{dlg} .el-dialog__close").first
        if btn.count() > 0:
            btn.click()
        else:
            self.page.keyboard.press("Escape")

    def _find_form_item(self, field_label: str):
        """在部门表单弹窗中定位指定 label 的 el-form-item"""
        dlg = self._visible_form_dialog()
        return self.page.locator(
            f'{dlg} .el-form-item:has-text("{field_label}")'
        ).first

    def fill_dept_field(self, field_label: str, value: str):
        """填充部门表单中指定 label 的 input 或 textarea"""
        form_item = self._find_form_item(field_label)
        if form_item.count() == 0:
            return
        ta = form_item.locator("textarea.el-textarea__inner").first
        if ta.count() > 0:
            ta.fill(str(value))
            return
        inp = form_item.locator("input.el-input__inner").first
        if inp.count() > 0:
            inp.fill(str(value))

    def clear_dept_field(self, field_label: str):
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

    def get_dept_field_value(self, field_label: str) -> str:
        """获取指定字段值"""
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

    def get_dept_field_placeholder(self, field_label: str) -> str:
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

    def wait_for_member_dialog(self, timeout: int = 5000):
        """等待任意对话框打开（成员管理/添加部门成员 等）。"""
        # 先尝试精确匹配
        try:
            self._wait_for_selector(f"{self.MEMBER_DIALOG}:visible", timeout=timeout)
            return
        except Exception:
            pass
        # 回退：接受任意新打开的可见弹窗
        try:
            self._wait_for_selector(f"{self.DIALOG_WRAPPER}:visible", timeout=timeout)
        except Exception:
            pass

    def is_member_dialog_open(self) -> bool:
        if self.page.locator(self.MEMBER_DIALOG).first.is_visible():
            return True
        # 回退：任意可见弹窗
        return self.page.locator(f"{self.DIALOG_WRAPPER}:visible").first.is_visible()

    def click_member_dialog_confirm(self):
        self.page.locator(self.MEMBER_DIALOG_CONFIRM).first.click()

    def click_member_dialog_cancel(self):
        self.page.locator(self.MEMBER_DIALOG_CANCEL).first.click()

    def click_member_dialog_close(self):
        self.page.locator(self.MEMBER_DIALOG_CLOSE).first.click()

    # ================= 查看用户弹窗 =================

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
