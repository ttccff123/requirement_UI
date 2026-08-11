from playwright.sync_api import Locator, Page, expect

from common.utils.log_util import logger


class BasePage:
    """封装 Playwright Page 对象的通用操作"""

    def __init__(self, page: Page):
        self.page = page

    # ================= 导航操作 =================
    def navigate_to(self, url: str):
        """访问指定 URL"""
        logger.info(f"正在访问页面: {url}")
        self.page.goto(url)

    def reload(self):
        """刷新当前页面"""
        logger.info("刷新当前页面...")
        self.page.reload()

    def go_back(self):
        """浏览器后退"""
        self.page.go_back()

    def go_forward(self):
        """浏览器前进"""
        self.page.go_forward()

    # ================= 元素定位与操作 =================
    def find_element(self, selector: str) -> Locator:
        """获取元素定位器"""
        return self.page.locator(selector)

    def click(self, selector: str):
        """点击元素"""
        logger.info(f"点击元素: {selector}")
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str, mask: bool = False):
        """输入文本 (会自动清空原有内容)"""
        display = "*" * len(value) if mask else value
        logger.info(f"在 {selector} 中输入: {display}")
        self.page.locator(selector).fill(value)

    def type_text(self, selector: str, value: str, delay: int = 50, mask: bool = False):
        """模拟逐字输入 (适合有输入监听的场景)，delay 单位为毫秒"""
        display = "*" * len(value) if mask else value
        logger.info(f"模拟打字输入 {selector}: {display}")
        self.page.locator(selector).press_sequentially(value, delay=delay)

    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        text = self.page.locator(selector).inner_text()
        logger.info(f"获取元素 {selector} 文本: {text}")
        return text

    def get_attribute(self, selector: str, name: str) -> str | None:
        """获取元素属性"""
        return self.page.locator(selector).get_attribute(name)

    # ================= 等待与断言 =================
    def wait_for_selector(self, selector: str, timeout: int = 10000):
        """等待元素可见（默认10秒，避免长时挂死）"""
        logger.info(f"等待元素出现: {selector}")
        self.page.locator(selector).wait_for(state="visible", timeout=timeout)

    def wait_for_url(self, url_pattern: str, timeout: int = 30000):
        """等待 URL 匹配"""
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def assert_visible(self, selector: str):
        """断言元素可见"""
        expect(self.page.locator(selector)).to_be_visible()

    def assert_text(self, selector: str, expected_text: str):
        """断言元素包含指定文本"""
        expect(self.page.locator(selector)).to_contain_text(expected_text)

    # ================= 高级操作 =================
    def screenshot(self, path: str, full_page: bool = False):
        """页面截图"""
        logger.info(f"正在截图并保存至: {path}")
        self.page.screenshot(path=path, full_page=full_page)

    def frame(self, frame_selector: str):
        """获取 iframe 的 FrameLocator（非 Selenium 式全局切换）"""
        logger.info(f"定位 iframe: {frame_selector}")
        return self.page.frame_locator(frame_selector)

    def upload_file(self, selector: str, file_path: str):
        """上传文件"""
        logger.info(f"上传文件: {file_path}")
        self.page.locator(selector).set_input_files(file_path)
