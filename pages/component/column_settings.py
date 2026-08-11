"""
列设置弹窗组件 — Element UI 弹窗，标题为"列设置"。

可复用于任意包含列设置弹窗的页面。中间字段列表由各页面自行处理（通过接口获取动态列），
本组件只封装弹窗外壳和按钮操作。

使用方式:
    col_settings = ColumnSettingsDialog(page, container="#pane-user")
    col_settings.wait_for_dialog()
    col_settings.click_confirm()
    col_settings.close_dialog()
"""

from playwright.sync_api import Page

from common.utils.log_util import logger


class ColumnSettingsDialog:
    """列设置弹窗组件（Element UI Dialog）"""

    TITLE_TEXT = "列设置"

    def __init__(self, page: Page, container: str = ""):
        """
        Args:
            page: Playwright Page 对象
            container: 弹窗所在的父容器选择器，如 "#pane-user"
                       为空时使用全局选择器
        """
        self.page = page
        self._ctx = container

    # ================= 选择器 =================

    @property
    def DIALOG_WRAPPER(self) -> str:
        """最外层弹窗容器（Element UI dialog 使用 append-to-body，渲染在 body 级别）"""
        return "body>.el-dialog__wrapper.kd-dialog"

    @property
    def DIALOG(self) -> str:
        """列设置弹窗 """
        return f'{self.DIALOG_WRAPPER}:has(.title__text:has-text("{self.TITLE_TEXT}"))'

    @property
    def DIALOG_TITLE(self) -> str:
        """弹窗标题区域 """
        return f"{self.DIALOG} .title__text"

    @property
    def DIALOG_CLOSE(self) -> str:
        """右上角 X 关闭按钮 """
        return f"{self.DIALOG} .el-dialog__close"

    @property
    def DIALOG_CANCEL(self) -> str:
        """底部取消按钮 """
        return f"{self.DIALOG} .el-dialog__footer .el-button--default"

    @property
    def DIALOG_CONFIRM(self) -> str:
        """底部确定按钮 """
        return f"{self.DIALOG} .el-dialog__footer .el-button--primary"

    @property
    def DIALOG_BODY(self) -> str:
        """弹窗 body 区域（中间动态字段列表所在） """
        return f"{self.DIALOG} .el-dialog__body"

    # ================= 等待 & 可见性 =================

    def wait_for_dialog(self, timeout: int = 10000):
        """等待列设置弹窗出现"""
        logger.info("等待列设置弹窗...")
        self.page.locator(f"{self.DIALOG}:visible").first.wait_for(state="visible", timeout=timeout)

    def is_open(self) -> bool:
        """列设置弹窗是否打开"""
        return self.page.locator(self.DIALOG).first.is_visible()

    def is_present(self) -> bool:
        """列设置弹窗是否存在于 DOM 中（可能隐藏）"""
        return self.page.locator(self.DIALOG).count() > 0

    # ================= 信息获取 =================

    def get_title(self) -> str:
        """获取弹窗标题文本"""
        return self.page.locator(self.DIALOG_TITLE).first.inner_text().strip()

    def get_body_text(self) -> str:
        """获取弹窗 body 区域文本"""
        body = self.page.locator(self.DIALOG_BODY).first
        return body.inner_text().strip() if body.count() > 0 else ""

    # ================= 按钮操作 =================

    def click_confirm(self):
        """点击底部确定按钮"""
        logger.info("列设置弹窗 — 点击确定")
        self.page.locator(f"{self.DIALOG}:visible .el-button--primary").first.click()

    def click_cancel(self):
        """点击底部取消按钮"""
        logger.info("列设置弹窗 — 点击取消")
        self.page.locator(f"{self.DIALOG}:visible .el-button--default").first.click()

    def click_close(self):
        """点击右上角 X 关闭弹窗"""
        logger.info("列设置弹窗 — 点击关闭")
        self.page.locator(f"{self.DIALOG}:visible .el-dialog__close").first.click()

    # ================= 中间字段区域（由各页面自行扩展） =================

    def get_checkbox_items(self) -> list[dict[str, str | bool]]:
        """获取弹窗中所有 checkbox 选项。

        Returns:
            [{label: "序号", checked: True}, ...]
            各页面的列字段由接口动态获取，结构可能不同，此处提供基础实现。
        """
        checkboxes = self.page.locator(f"{self.DIALOG}:visible .el-checkbox").all()
        result = []
        for cb in checkboxes:
            label_el = cb.locator(".el-checkbox__label")
            input_el = cb.locator("input.el-checkbox__original")
            label = label_el.first.inner_text().strip() if label_el.count() > 0 else ""
            checked = input_el.is_checked() if input_el.count() > 0 else False
            result.append({"label": label, "checked": checked})
        return result

    def toggle_checkbox(self, label: str):
        """切换指定 label 的 checkbox 选中状态"""
        logger.info(f"列设置弹窗 — 切换 checkbox: {label}")
        cb = self.page.locator(
            f'{self.DIALOG}:visible .el-checkbox:has(.el-checkbox__label:text-is("{label}"))'
        )
        if cb.count() > 0:
            cb.first.click()

    # ================= 搜索框 =================

    @property
    def SEARCH_INPUT(self) -> str:
        """弹窗中的搜索输入框"""
        return f"{self.DIALOG}:visible .el-input__inner"

    def get_search_placeholder(self) -> str:
        """获取搜索框的 placeholder 文本"""
        inp = self.page.locator(self.SEARCH_INPUT).first
        if inp.count() > 0:
            return inp.get_attribute("placeholder") or ""
        return ""

    def search(self, keyword: str):
        """在搜索框中输入关键字"""
        inp = self.page.locator(self.SEARCH_INPUT).first
        if inp.count() > 0:
            inp.fill(keyword)
            self.page.wait_for_timeout(300)

    def clear_search(self):
        """清空搜索框"""
        inp = self.page.locator(self.SEARCH_INPUT).first
        if inp.count() > 0:
            inp.fill("")
            self.page.wait_for_timeout(300)

    def get_visible_checkbox_count(self) -> int:
        """获取当前可见的 checkbox 数量（搜索过滤后）"""
        return self.page.locator(f"{self.DIALOG}:visible .el-checkbox").count()

    # ================= 拖拽排序 =================

    def get_checkbox_labels(self) -> list[str]:
        """获取当前所有 checkbox 的 label 文本列表（按 DOM 顺序）"""
        checkboxes = self.page.locator(f"{self.DIALOG}:visible .el-checkbox").all()
        result = []
        for cb in checkboxes:
            label_el = cb.locator(".el-checkbox__label")
            if label_el.count() > 0:
                result.append(label_el.first.inner_text().strip())
        return result

    def drag_checkbox(self, from_label: str, to_label: str):
        """将 checkbox 从 from_label 位置拖到 to_label 位置"""
        from_el = self.page.locator(
            f'{self.DIALOG}:visible .el-checkbox:has(.el-checkbox__label:text-is("{from_label}"))'
        ).first
        to_el = self.page.locator(
            f'{self.DIALOG}:visible .el-checkbox:has(.el-checkbox__label:text-is("{to_label}"))'
        ).first
        if from_el.count() > 0 and to_el.count() > 0:
            from_el.drag_to(to_el)
            self.page.wait_for_timeout(500)
