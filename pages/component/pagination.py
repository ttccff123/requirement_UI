from playwright.sync_api import Page

from common.utils.log_util import logger


class Pagination:
    """分页控件组件 — 可复用于任意包含 el-pagination 的页面。

    使用方式:
        pagination = Pagination(page, container="#pane-user .pagination-wrap")
        total = pagination.get_total_count_number()
        pagination.go_to_page(3)
    """

    def __init__(self, page: Page, container: str = ""):
        """
        Args:
            page: Playwright Page 对象
            container: 分页组件的父容器选择器，如 "#pane-user .pagination-wrap"
                       为空时直接使用全局选择器
        """
        self.page = page
        self._ctx = container

    # ================= 选择器（支持按容器限定作用域） =================

    @property
    def PAGINATION_WRAP(self) -> str:
        return f"{self._ctx} .pagination-wrap" if self._ctx else ".pagination-wrap"

    @property
    def PAGINATION_TOTAL(self) -> str:
        return f"{self.PAGINATION_WRAP} .pagination-total"

    @property
    def PAGINATION(self) -> str:
        return f"{self.PAGINATION_WRAP} .el-pagination.is-background"

    @property
    def PAGE_SIZES(self) -> str:
        return f"{self.PAGINATION} .el-pagination__sizes"

    @property
    def PAGE_SIZES_SELECT(self) -> str:
        return f"{self.PAGE_SIZES} .el-select"

    @property
    def PAGE_SIZES_INPUT(self) -> str:
        return f"{self.PAGE_SIZES_SELECT} input.el-input__inner"

    @property
    def PAGE_PREV_BTN(self) -> str:
        return f"{self.PAGINATION} button.btn-prev"

    @property
    def PAGE_NEXT_BTN(self) -> str:
        return f"{self.PAGINATION} button.btn-next"

    @property
    def PAGE_NUMBERS(self) -> str:
        return f"{self.PAGINATION} ul.el-pager li.number"

    @property
    def PAGE_ACTIVE_NUMBER(self) -> str:
        return f"{self.PAGINATION} ul.el-pager li.number.active"

    @property
    def PAGE_JUMP(self) -> str:
        return f"{self.PAGINATION} .el-pagination__jump"

    @property
    def PAGE_JUMP_INPUT(self) -> str:
        return f"{self.PAGE_JUMP} input.el-input__inner"

    # ================= 等待 & 可见性 =================

    def wait_for_pagination(self, timeout: int = 10000):
        """等待分页控件可见"""
        logger.info("等待分页控件加载...")
        self.page.locator(self.PAGINATION).first.wait_for(state="visible", timeout=timeout)

    def is_visible(self) -> bool:
        return self.page.locator(self.PAGINATION).first.is_visible()

    def is_present(self) -> bool:
        """分页控件是否存在于 DOM 中（可能隐藏）"""
        return self.page.locator(self.PAGINATION).count() > 0

    # ================= 总条数 =================

    def get_total_count(self) -> str:
        """获取'共 N 条'文本"""
        return self.page.locator(self.PAGINATION_TOTAL).first.inner_text().strip()

    def get_total_count_number(self) -> int:
        """获取总条数（int）"""
        text = self.get_total_count()
        digits = "".join(c for c in text if c.isdigit())
        return int(digits) if digits else 0

    # ================= 当前页码 =================

    def get_current_page(self) -> int:
        """获取当前页码"""
        active = self.page.locator(self.PAGE_ACTIVE_NUMBER).first
        if active.count() > 0:
            num = active.inner_text().strip()
            if num.isdigit():
                return int(num)
        return 1

    def get_visible_page_numbers(self) -> list[int]:
        """获取分页器上显示的所有页码"""
        nums = self.page.locator(self.PAGE_NUMBERS).all()
        result = []
        for n in nums:
            text = n.inner_text().strip()
            if text.isdigit():
                result.append(int(text))
        return result

    def get_total_pages(self) -> int:
        """推算总页数（总条数 / 每页条数，向上取整）"""
        total = self.get_total_count_number()
        size = self.get_page_size()
        if total <= 0:
            return 0
        return (total + size - 1) // size

    # ================= 每页条数 =================

    def get_page_size(self) -> int:
        """获取当前每页条数"""
        val = self.page.locator(self.PAGE_SIZES_INPUT).first.get_attribute("value") or ""
        digits = "".join(c for c in val if c.isdigit())
        return int(digits) if digits else 10

    DROPDOWN_VISIBLE = '.el-select-dropdown[x-placement="bottom-start"]'
    DROPDOWN_ITEMS = f"{DROPDOWN_VISIBLE} ul li.el-select-dropdown__item"

    def change_page_size(self, size: int):
        """切换每页显示条数：10 / 20 / 30 / 40"""
        logger.info(f"切换每页条数为: {size}")
        self.page.locator(self.PAGE_SIZES_SELECT).first.click()
        self.page.locator(self.DROPDOWN_VISIBLE).first.wait_for(state="visible", timeout=5000)
        self.page.locator(
            f'{self.DROPDOWN_ITEMS}:has-text("{size}条/页")'
        ).first.click()
        self.page.wait_for_timeout(1000)

    def get_page_size_options(self) -> list[int]:
        """获取可用的每页条数选项"""
        self.page.locator(self.PAGE_SIZES_SELECT).first.click()
        self.page.locator(self.DROPDOWN_VISIBLE).first.wait_for(state="visible", timeout=5000)
        dropdown = self.page.locator(".el-select-dropdown.el-popper").first
        items = dropdown.locator("li.el-select-dropdown__item").all()
        result = []
        for item in items:
            text = item.inner_text().strip()
            digits = "".join(c for c in text if c.isdigit())
            if digits:
                result.append(int(digits))
        # 点击空白关闭下拉
        self.page.locator("body").first.press("Escape")
        self.page.wait_for_timeout(300)
        return result

    # ================= 翻页 =================

    def click_prev_page(self):
        """点击上一页按钮"""
        logger.info("点击上一页")
        self.page.locator(self.PAGE_PREV_BTN).first.click()

    def click_next_page(self):
        """点击下一页按钮"""
        logger.info("点击下一页")
        self.page.locator(self.PAGE_NEXT_BTN).first.click()

    def go_to_page(self, page_num: int):
        """跳转到指定页码（优先点击页码按钮，不可见时使用跳转输入框）"""
        logger.info(f"跳转到第 {page_num} 页")
        btn = self.page.locator(f"{self.PAGE_NUMBERS}:has-text(\"{page_num}\")")
        if btn.count() > 0:
            btn.first.click()
        else:
            self.page.locator(self.PAGE_JUMP_INPUT).first.fill(str(page_num))
            self.page.locator(self.PAGE_JUMP_INPUT).first.press("Enter")

    def go_to_first_page(self):
        """跳转到第一页"""
        visible = self.get_visible_page_numbers()
        if visible and visible[0] == 1:
            self.go_to_page(1)
        else:
            # 多次点击上一页直到禁用
            for _ in range(20):
                if self.is_prev_disabled():
                    break
                self.click_prev_page()
                self.page.wait_for_timeout(300)

    def go_to_last_page(self):
        """跳转到最后一页"""
        total_pages = self.get_total_pages()
        if total_pages > 0:
            self.go_to_page(total_pages)

    # ================= 按钮状态 =================

    def is_prev_disabled(self) -> bool:
        """上一页按钮是否禁用"""
        cls = self.page.locator(self.PAGE_PREV_BTN).first.get_attribute("class") or ""
        return "disabled" in cls

    def is_next_disabled(self) -> bool:
        """下一页按钮是否禁用"""
        cls = self.page.locator(self.PAGE_NEXT_BTN).first.get_attribute("class") or ""
        return "disabled" in cls

    def is_prev_enabled(self) -> bool:
        return not self.is_prev_disabled()

    def is_next_enabled(self) -> bool:
        return not self.is_next_disabled()

    # ================= 跳转输入 =================

    def jump_to_page(self, page_num: int):
        """通过跳转输入框直接跳转到指定页"""
        logger.info(f"跳转输入: 第 {page_num} 页")
        self.page.locator(self.PAGE_JUMP_INPUT).first.fill(str(page_num))
        self.page.locator(self.PAGE_JUMP_INPUT).first.press("Enter")

    def get_jump_input_value(self) -> str:
        """获取跳转输入框当前值"""
        return self.page.locator(self.PAGE_JUMP_INPUT).first.input_value()
