"""
Toast / Message 提示组件 — Element UI 消息提示的页面对象。

可复用于任意包含 el-message 提示的页面。

使用方式:
    toast = Toast(page)
    msg = toast.get_message()
    toast.wait_for_toast()
    if toast.is_visible():
        ...
"""

from playwright.sync_api import Page

from common.utils.log_util import logger


class Toast:
    """Element UI Toast / Message 消息提示组件"""

    def __init__(self, page: Page):
        """
        Args:
            page: Playwright Page 对象
        """
        self.page = page

    # ================= 选择器 =================

    @property
    def TOAST_CONTAINER(self) -> str:
        """Element UI message 消息容器"""
        return ".el-message"

    @property
    def TOAST_CONTENT(self) -> str:
        """Element UI message 消息内容"""
        return ".el-message .el-message__content"

    # ================= 等待 & 可见性 =================

    def wait_for_visible(self, timeout: int = 5000):
        """等待 Toast 消息出现"""
        logger.info("等待 Toast 消息...")
        self.page.locator(self.TOAST_CONTENT).first.wait_for(state="visible", timeout=timeout)

    def is_visible(self) -> bool:
        """Toast 消息当前是否可见"""
        return self.page.locator(self.TOAST_CONTENT).first.is_visible()

    def is_present(self) -> bool:
        """Toast 消息是否存在于 DOM 中（可能隐藏）"""
        return self.page.locator(self.TOAST_CONTENT).count() > 0

    # ================= 消息获取 =================

    def get_message(self) -> str:
        """获取当前页面所有可见 Toast 消息文本（多条以 ' | ' 连接）"""
        locator = self.page.locator(self.TOAST_CONTENT)
        if locator.count() == 0:
            return ""
        locator.first.wait_for(state="visible", timeout=5000)
        texts = [t.strip() for t in locator.all_inner_texts() if t.strip()]
        return " | ".join(texts) if texts else ""

    def get_all_messages(self) -> list[str]:
        """获取所有 Toast 消息文本列表（不去重）"""
        locator = self.page.locator(self.TOAST_CONTENT)
        if locator.count() == 0:
            return []
        return [t.strip() for t in locator.all_inner_texts() if t.strip()]

    # ================= 类型判断 =================

    def get_type(self) -> str | None:
        """获取 Toast 消息类型。

        Returns:
            'success' / 'warning' / 'error' / 'info'，或 None（无 toast）
        """
        container = self.page.locator(self.TOAST_CONTAINER).first
        if container.count() == 0:
            return None
        cls = container.get_attribute("class") or ""
        for t in ("success", "warning", "error", "info"):
            if f"el-message--{t}" in cls:
                return t
        return None

    # ================= 快捷断言 =================

    def assert_contains(self, keyword: str, timeout: int = 5000):
        """断言 Toast 消息中包含指定关键词"""
        logger.info(f"断言 Toast 包含: '{keyword}'")
        self.wait_for_visible(timeout=timeout)
        msg = self.get_message()
        assert keyword in msg, f"期望 Toast 消息包含 '{keyword}'，实际为: '{msg}'"
