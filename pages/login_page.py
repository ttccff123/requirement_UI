from pages.base_page import BasePage
from pages.component.toast import Toast


class LoginPage(BasePage):
    """体系数字工程开发平台 - 登录页"""

    def __init__(self, page):
        super().__init__(page)
        self.toast = Toast(page)

    # 品牌/文案
    TOOL_NAME = ".login-text .name"  # 工具名称，如 KD-SDP
    CN_NAME = ".login-text .title"  # 中文名称，如 体系数字工程
    EN_NAME = ".login-text .intro"  # 英文名称

    # 表单
    USERNAME = ".login-container-user input.el-input__inner"
    PASSWORD = ".login-container-password input.el-input__inner"
    LOGIN_BTN = "button.login-container-button"

    def open(self, base_url: str):
        self.navigate_to(base_url)

    def get_page_title(self) -> str:
        """浏览器页签 title"""
        return self.page.title()

    def get_tool_name(self) -> str:
        self.wait_for_selector(self.TOOL_NAME)
        return self.get_text(self.TOOL_NAME).strip()

    def get_cn_name(self) -> str:
        self.wait_for_selector(self.CN_NAME)
        return self.get_text(self.CN_NAME).strip()

    def get_en_name(self) -> str:
        self.wait_for_selector(self.EN_NAME)
        return self.get_text(self.EN_NAME).strip()

    def login(self, username: str, password: str):
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, password, mask=True)
        self.click(self.LOGIN_BTN)

    def get_toast_message(self) -> str:
        """获取页面提示文案（校验 warning / 业务 error，可能有多条）"""
        return self.toast.get_message()

    def is_still_on_login(self) -> bool:
        return "#/login" in self.page.url
