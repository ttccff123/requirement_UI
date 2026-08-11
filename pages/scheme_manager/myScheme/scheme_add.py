from core.base_page import BasePage


class SchemeAddPage(BasePage):
    """新建方案弹窗（点击侧边栏「新建」→「空白方案」弹出）

    DOM 结构（Element UI el-dialog）：
    - 弹窗容器：div.el-dialog.add-product.kd-dialog（width: 480px）
    - 标题：    span.title__text → "新建方案"
    - 表单字段：
        1. 方案名称：input.el-input__inner（placeholder="请输入方案名称"）
        2. 方案类型：div.el-select（选项：使命需求 / 作战需求 / 系统需求）
        3. 方案标识：input.el-input__inner（placeholder="请输入方案标识"）
        4. 方案描述：textarea.el-textarea__inner（maxlength=500, placeholder="请输入方案的简要描述"）
    - 底部：
        - 勾选框：label.el-checkbox → "打开方案"（默认勾选）
        - 按钮：  button.el-button → "取 消"
                  button.el-button.el-button--primary → "确 定"
    """

    # -- 核心选择器 --
    DIALOG = ".el-dialog.add-product"
    DIALOG_VISIBLE = ".el-dialog.add-product:visible"
    TITLE = ".kd-dialog__title .title__text"

    # 表单字段（按 label 定位表单项，再取内部控件）
    FORM_ITEM = ".el-form-item"
    FORM_LABEL = ".el-form-item__label"
    FORM_INPUT = ".el-input__inner"
    FORM_TEXTAREA = ".el-textarea__inner"
    FORM_SELECT = ".el-select"
    FORM_SELECT_INPUT = ".el-select__input"
    FORM_SELECT_WRAPPER = ".el-select__wrapper"
    FORM_SELECT_DROPDOWN_ITEM = ".el-select-dropdown__item:visible"

    # 方案类型选项
    SCHEME_TYPES = ["使命需求", "作战需求", "系统需求"]

    # 底部控件
    CHECKBOX = ".el-checkbox"
    CHECKBOX_INPUT = ".el-checkbox__original"
    BTN_CANCEL = "button.el-button:not(.el-button--primary)"
    BTN_CONFIRM = "button.el-button--primary"
    BTN_CLOSE = ".el-dialog__headerbtn"

    def __init__(self, page):
        super().__init__(page)

    # ================= 打开 / 关闭 =================

    def open(self):
        """通过侧边栏「新建」→「空白方案」打开弹窗"""
        self.page.locator(".add-btn button").first.click()
        self.page.wait_for_timeout(500)
        self.page.locator(".add-box .row-box").filter(has_text="空白方案").first.click()
        self.wait_for_dialog()
        return self

    def wait_for_dialog(self, timeout: int = 8000):
        """等待弹窗可见"""
        self.page.locator(self.DIALOG).first.wait_for(state="visible", timeout=timeout)
        return self

    def close(self):
        """点击右上角 X 关闭弹窗"""
        self.page.locator(self.DIALOG_VISIBLE).locator(self.BTN_CLOSE).first.click()
        self.page.wait_for_timeout(300)
        return self

    def cancel(self):
        """点击「取 消」按钮关闭弹窗"""
        self.page.locator(self.DIALOG_VISIBLE).locator(self.BTN_CANCEL).first.click()
        self.page.wait_for_timeout(300)
        return self

    def confirm(self):
        """点击「确 定」按钮提交"""
        self.page.locator(self.DIALOG_VISIBLE).locator(self.BTN_CONFIRM).first.click()
        self.page.wait_for_timeout(500)
        return self

    def is_dialog_visible(self) -> bool:
        """弹窗是否可见"""
        el = self.page.locator(self.DIALOG_VISIBLE)
        return el.count() > 0 and el.first.is_visible()

    def get_title(self) -> str:
        """返回弹窗标题文本"""
        return self.page.locator(self.DIALOG_VISIBLE).locator(self.TITLE).first.inner_text()

    # ================= 表单字段定位 =================

    def _form_item(self, label_text: str):
        """根据 label 文本返回对应表单项容器"""
        return (
            self.page.locator(self.DIALOG_VISIBLE)
            .locator(self.FORM_ITEM)
            .filter(has_text=label_text)
            .first
        )

    # ---------- 方案名称 ----------

    def get_scheme_name_input(self):
        """返回「方案名称」输入框定位器"""
        return self._form_item("方案名称").locator(self.FORM_INPUT).first

    def fill_scheme_name(self, name: str):
        """填写方案名称"""
        inp = self.get_scheme_name_input()
        inp.fill(name)
        return self

    def get_scheme_name(self) -> str:
        """获取已填写的方案名称"""
        return self.get_scheme_name_input().input_value()

    # ---------- 方案类型 ----------

    def get_scheme_type_select(self):
        """返回「方案类型」下拉框定位器"""
        return self._form_item("方案类型").locator(self.FORM_SELECT).first

    def get_scheme_type_value(self) -> str:
        """获取当前选中的方案类型"""
        return self.get_scheme_type_select().inner_text().strip()

    def _is_select_dropdown_open(self) -> bool:
        """方案类型下拉框是否已展开"""
        dropdown = self.page.locator(".el-select-dropdown:visible")
        return dropdown.count() > 0

    def open_scheme_type_options(self):
        """展开方案类型下拉框（已展开时不做操作）"""
        if self._is_select_dropdown_open():
            return self
        self.get_scheme_type_select().locator(self.FORM_SELECT_WRAPPER).first.click()
        self.page.wait_for_timeout(400)
        return self

    def get_scheme_type_options(self):
        """返回方案类型所有可选值的文本列表（自动展开下拉框）"""
        self.open_scheme_type_options()
        items = self.page.locator(self.FORM_SELECT_DROPDOWN_ITEM)
        return [items.nth(i).inner_text().strip() for i in range(items.count())]

    def select_scheme_type(self, type_name: str):
        """选择方案类型（使命需求 / 作战需求 / 系统需求）"""
        # 如果当前已选中目标类型，无需操作
        if self.get_scheme_type_value() == type_name:
            return self
        self.open_scheme_type_options()
        item = (
            self.page.locator(self.FORM_SELECT_DROPDOWN_ITEM)
            .filter(has_text=type_name)
            .first
        )
        if item.count() == 0:
            available = self.get_scheme_type_options()
            raise AssertionError(
                f"未找到方案类型「{type_name}」，可选值: {available}"
            )
        item.click()
        self.page.wait_for_timeout(300)
        return self

    # ---------- 方案标识 ----------

    def get_scheme_code_input(self):
        """返回「方案标识」输入框定位器"""
        return self._form_item("方案标识").locator(self.FORM_INPUT).first

    def fill_scheme_code(self, code: str):
        """填写方案标识"""
        self.get_scheme_code_input().fill(code)
        return self

    def get_scheme_code(self) -> str:
        """获取已填写的方案标识"""
        return self.get_scheme_code_input().input_value()

    # ---------- 方案描述 ----------

    def get_scheme_desc_textarea(self):
        """返回「方案描述」文本域定位器"""
        return self._form_item("方案描述").locator(self.FORM_TEXTAREA).first

    def fill_scheme_desc(self, desc: str):
        """填写方案描述"""
        self.get_scheme_desc_textarea().fill(desc)
        return self

    def get_scheme_desc(self) -> str:
        """获取已填写的方案描述"""
        return self.get_scheme_desc_textarea().input_value()

    # ---------- 底部勾选框 ----------

    def get_open_scheme_checkbox(self):
        """返回「打开方案」勾选框定位器"""
        return (
            self.page.locator(self.DIALOG_VISIBLE)
            .locator(self.CHECKBOX)
            .filter(has_text="打开方案")
            .first
        )

    def is_open_scheme_checked(self) -> bool:
        """「打开方案」是否已勾选"""
        cb = self.get_open_scheme_checkbox()
        return "is-checked" in (cb.get_attribute("class") or "")

    def toggle_open_scheme(self, checked: bool = True):
        """设置「打开方案」勾选状态"""
        if self.is_open_scheme_checked() != checked:
            self.get_open_scheme_checkbox().click()
            self.page.wait_for_timeout(200)
        return self

    # ================= 快捷操作 =================

    def fill_form(
        self,
        name: str,
        scheme_type: str = "使命需求",
        code: str = "",
        desc: str = "",
        open_scheme: bool = True,
    ):
        """一次性填写整个表单"""
        self.fill_scheme_name(name)
        if scheme_type and scheme_type != self.get_scheme_type_value():
            self.select_scheme_type(scheme_type)
        if code:
            self.fill_scheme_code(code)
        if desc:
            self.fill_scheme_desc(desc)
        self.toggle_open_scheme(open_scheme)
        return self

    def submit(self, name: str, scheme_type: str = "使命需求", code: str = "", desc: str = ""):
        """填写表单并点击确定"""
        self.fill_form(name, scheme_type, code, desc)
        self.confirm()
        return self
