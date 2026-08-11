from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from common.utils.log_util import logger
from config.settings import DEFAULT_TIMEOUT, SLOW_MO


class BrowserManager:
    """封装 Playwright 浏览器核心操作"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def start_browser(self, browser_type: str = "chromium") -> Browser:
        """启动浏览器"""
        logger.info(f"正在启动 {browser_type} 浏览器...")
        self.playwright = sync_playwright().start()

        launchers = {
            "chromium": self.playwright.chromium,
            "firefox": self.playwright.firefox,
            "webkit": self.playwright.webkit,
        }
        if browser_type not in launchers:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")

        launch_kwargs: dict = {
            "headless": self.headless,
            "slow_mo": int(SLOW_MO) if str(SLOW_MO).isdigit() else 0,
        }
        if browser_type == "chromium":
            # 避免在本机上因 channel=chrome 过于依赖系统 Chrome 而导致页面异常关闭
            launch_kwargs.setdefault("args", ["--no-sandbox", "--disable-dev-shm-usage"])

        try:
            self.browser = launchers[browser_type].launch(**launch_kwargs)
            return self.browser
        except Exception as exc:
            logger.warning(f"{browser_type} 启动失败，尝试回退到默认配置: {exc}")
            fallback_kwargs = {
                "headless": self.headless,
                "slow_mo": int(SLOW_MO) if str(SLOW_MO).isdigit() else 0,
            }
            self.browser = launchers[browser_type].launch(**fallback_kwargs)
            return self.browser

    def new_context(self, **kwargs) -> BrowserContext:
        """创建新的浏览器上下文 (Context)"""
        if not self.browser:
            raise RuntimeError("浏览器尚未启动，请先调用 start_browser()")

        logger.info("正在创建新的浏览器上下文...")
        self.context = self.browser.new_context(**kwargs)
        self.context.set_default_timeout(DEFAULT_TIMEOUT)
        return self.context

    def new_page(self) -> Page:
        """在当前上下文中创建新页面"""
        if not self.context:
            raise RuntimeError("上下文尚未创建，请先调用 new_context()")

        logger.info("正在创建新页面...")
        self.page = self.context.new_page()
        return self.page

    def close(self) -> None:
        """关闭浏览器及清理资源"""
        logger.info("正在关闭浏览器...")
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
