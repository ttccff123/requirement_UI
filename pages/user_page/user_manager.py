"""
用户管理 - 主页面对象

体系数字工程开发平台 - 组织 → 用户管理页面对象 (#/organization, 默认 tab: 用户)
"""

from playwright.sync_api import Locator

from pages.base_page import BasePage
from pages.component.column_settings import ColumnSettingsDialog
from pages.component.pagination import Pagination
from pages.component.toast import Toast
from pages.user_page.user_dialog import UserDialog


class UserManager(BasePage):
    """体系数字工程开发平台 - 组织 → 用户管理页面对象 (#/organization, 默认 tab: 用户)"""

    def __init__(self, page):
        super().__init__(page)
        self.pagination = Pagination(page, container="#pane-user")
        self.dialog = UserDialog(page, container="#pane-user")
        self.toast = Toast(page)
        self.column_settings = ColumnSettingsDialog(page, container="#pane-user")

    # ================= 页面整体 / Tab 切换 =================
    PAGE_CONTAINER = "#pane-user"
    TAB_HEADER = ".el-tabs__header.is-top"
    TAB_ITEM = f"{TAB_HEADER} .el-tabs__item.is-top"
    TAB_USER = f'{TAB_ITEM}:has-text("用户")'
    TAB_ROLE = f'{TAB_ITEM}:has-text("角色")'
    TAB_DEPARTMENT = f'{TAB_ITEM}:has-text("部门")'
    TAB_ACTIVE = f"{TAB_ITEM}.is-active"

    # Tab 面板容器（Element UI tabs 的 el-tab-pane）
    PANE_USER = "#pane-user"
    PANE_ROLE = "#pane-role"
    PANE_DEPARTMENT = "#pane-department"

    # ================= 表头区域 =================
    TABLE_PRO = ".kd-table-pro"
    HEADER = f"{TABLE_PRO} .kd-table-pro__header"
    HEADER_LEFT = f"{HEADER} .kd-table-pro__header-left"
    HEADER_RIGHT = f"{HEADER} .kd-table-pro__header-right"

    # 搜索
    SEARCH_DIV = f"{HEADER_LEFT} .input-div"
    SEARCH_ICON = f"{SEARCH_DIV} .icon-sousuo_chaxun"
    SEARCH_INPUT = f"{SEARCH_DIV} input.el-input__inner"

    # 筛选下拉框 — 用 placeholder 属性定位，比 :nth-child 可靠
    FILTER_ROLE_SELECT = f'{HEADER_LEFT} > .el-select:has(input[placeholder="角色"])'
    FILTER_ROLE_INPUT = f'{FILTER_ROLE_SELECT} input.el-input__inner'
    FILTER_DEPT_SELECT = f'{HEADER_LEFT} > .el-select:has(input[placeholder="部门"])'
    FILTER_DEPT_INPUT = f'{FILTER_DEPT_SELECT} input.el-input__inner'
    FILTER_STATUS_SELECT = f'{HEADER_LEFT} > .el-select:has(input[placeholder="状态"])'
    FILTER_STATUS_INPUT = f'{FILTER_STATUS_SELECT} input.el-input__inner'

    # 新建用户按钮
    CREATE_USER_BTN = f"{HEADER_RIGHT} .el-button--primary"
    CREATE_USER_ICON = f"{CREATE_USER_BTN} .icon-xinjian_xinzeng_tianjia"

    # ================= 表格主体 (VXE-Table) =================
    TABLE_MAIN = f"{TABLE_PRO} .kd-table-pro__main"
    VXE_TABLE = f"{TABLE_MAIN} .vxe-table"
    TABLE_HEADER_WRAPPER = f"{VXE_TABLE} .vxe-table--header-wrapper"
    TABLE_HEADER_TABLE = f"{TABLE_HEADER_WRAPPER} table.vxe-table--header"
    TABLE_HEADER_ROW = f"{TABLE_HEADER_TABLE} tr.vxe-header--row"
    TABLE_HEADER_CELLS = f"{TABLE_HEADER_ROW} th.vxe-header--column"

    # 表体
    TABLE_BODY_WRAPPER = f"{VXE_TABLE} .vxe-table--body-wrapper"
    TABLE_BODY_TABLE = f"{TABLE_BODY_WRAPPER} table.vxe-table--body"
    TABLE_BODY_ROWS = f"{TABLE_BODY_TABLE} tr.vxe-body--row"
    TABLE_BODY_CELLS = "td.vxe-body--column"

    # 列设置 (col_id)
    COL_SEQ = "col_5"        # 序号
    COL_USERNAME = "col_6"   # 用户名
    COL_REALNAME = "col_7"   # 姓名
    COL_GENDER = "col_8"     # 性别
    COL_ROLE = "col_9"       # 角色
    COL_DEPT = "col_10"      # 部门
    COL_PROJECTS = "col_11"  # 参与项目
    COL_VISITS = "col_12"    # 访问次数
    COL_STATUS = "col_13"    # 状态
    COL_ACTION = "col_14"    # 操作

    # 空状态
    TABLE_EMPTY = f"{TABLE_BODY_TABLE} .noData"
    TABLE_EMPTY_TEXT = f"{TABLE_EMPTY} .noData__span"

    # ================= 操作列图标 =================
    ACTION_EDIT_ICON = "i.iconfont.icon-bianji"              # 编辑
    ACTION_DISABLE_ICON = "i.iconfont.icon-jinzhi"           # 禁用
    ACTION_RESET_ICON = "i.iconfont.icon-zhongzhi"           # 重置
    ACTION_DELETE_ICON = "i.iconfont.icon-shanchu_huishouzhan"  # 删除

    # ================= Toast =================

    def get_toast_message(self) -> str:
        """获取页面 Toast 提示文案"""
        return self.toast.get_message()

    # ========================================================================
    #  页面级操作
    # ========================================================================

    def wait_for_page(self, timeout: int = 30000):
        """等待用户管理页面加载（默认 tab：用户）"""
        self.wait_for_selector(self.PAGE_CONTAINER, timeout=timeout)
        self.page.locator(self.PAGE_CONTAINER).first.wait_for(state="visible", timeout=timeout)

    def is_page_loaded(self) -> bool:
        return self.page.locator(self.PAGE_CONTAINER).first.is_visible()

    def get_current_url_hash(self) -> str:
        """获取当前 URL 的 hash 部分"""
        url = self.page.url
        return url.split("#")[-1] if "#" in url else ""

    # ========================================================================
    #  Tab 切换
    # ========================================================================

    def get_active_tab_name(self) -> str:
        """获取当前激活的 tab 名称（用户/角色/部门）"""
        return self.page.locator(self.TAB_ACTIVE).first.inner_text().strip()

    def click_tab_user(self):
        """切换到'用户' tab"""
        self.page.locator(self.TAB_USER).first.click()
        self.wait_for_page()

    def click_tab_role(self):
        """切换到'角色' tab"""
        self.page.locator(self.TAB_ROLE).first.click()

    def click_tab_department(self):
        """切换到'部门' tab"""
        self.page.locator(self.TAB_DEPARTMENT).first.click()

    def is_user_tab_active(self) -> bool:
        return "is-active" in (self.page.locator(self.TAB_USER).first.get_attribute("class") or "")

    # ========================================================================
    #  Tab 面板内容
    # ========================================================================

    def _wait_for_pane(self, pane_selector: str, timeout: int = 10000):
        """等待指定 tab 面板可见"""
        self.page.locator(pane_selector).first.wait_for(state="visible", timeout=timeout)

    def _is_pane_visible(self, pane_selector: str) -> bool:
        """指定 tab 面板是否可见"""
        return self.page.locator(pane_selector).first.is_visible()

    def _is_pane_present(self, pane_selector: str) -> bool:
        """指定 tab 面板是否存在于 DOM"""
        return self.page.locator(pane_selector).count() > 0

    def _get_pane_text(self, pane_selector: str) -> str:
        """获取 tab 面板内全部文本"""
        return self.page.locator(pane_selector).first.inner_text().strip()

    # —— 用户 tab 面板 ——

    def wait_for_user_pane(self, timeout: int = 10000):
        self._wait_for_pane(self.PANE_USER, timeout=timeout)

    def is_user_pane_visible(self) -> bool:
        return self._is_pane_visible(self.PANE_USER)

    def is_user_pane_present(self) -> bool:
        return self._is_pane_present(self.PANE_USER)

    def get_user_pane_text(self) -> str:
        return self._get_pane_text(self.PANE_USER)

    # —— 角色 tab 面板 ——

    def wait_for_role_pane(self, timeout: int = 10000):
        self._wait_for_pane(self.PANE_ROLE, timeout=timeout)

    def is_role_pane_visible(self) -> bool:
        return self._is_pane_visible(self.PANE_ROLE)

    def is_role_pane_present(self) -> bool:
        return self._is_pane_present(self.PANE_ROLE)

    def get_role_pane_text(self) -> str:
        return self._get_pane_text(self.PANE_ROLE)

    # —— 部门 tab 面板 ——

    def wait_for_department_pane(self, timeout: int = 10000):
        self._wait_for_pane(self.PANE_DEPARTMENT, timeout=timeout)

    def is_department_pane_visible(self) -> bool:
        return self._is_pane_visible(self.PANE_DEPARTMENT)

    def is_department_pane_present(self) -> bool:
        return self._is_pane_present(self.PANE_DEPARTMENT)

    def get_department_pane_text(self) -> str:
        return self._get_pane_text(self.PANE_DEPARTMENT)

    # ========================================================================
    #  Tab 面板 — 表格内容（根据面板作用域获取列头、行数据等）
    # ========================================================================

    def _pane_table_headers(self, pane: str) -> list[str]:
        """获取指定面板中表格的列头文本列表"""
        sel = f"{pane} {self.TABLE_HEADER_CELLS}"
        cells = self.page.locator(sel).all()
        return [
            c.locator(".vxe-cell--title span").first.inner_text().strip()
            for c in cells
        ]

    def _pane_table_row_count(self, pane: str) -> int:
        """获取指定面板中表格的数据行数"""
        return self.page.locator(f"{pane} {self.TABLE_BODY_ROWS}").count()

    def _pane_has_table(self, pane: str) -> bool:
        """指定面板中是否存在表格组件"""
        return self.page.locator(f"{pane} {self.TABLE_PRO}").count() > 0

    def _pane_has_create_btn(self, pane: str) -> bool:
        """指定面板中是否存在新建按钮 (.el-button--primary > i.iconfont)"""
        return self.page.locator(
            f'{pane} .kd-table-pro__header-right .el-button--primary i.iconfont'
        ).count() > 0

    # —— 用户 tab 表格 ——

    def get_user_table_headers(self) -> list[str]:
        return self._pane_table_headers(self.PANE_USER)

    def get_user_table_row_count(self) -> int:
        return self._pane_table_row_count(self.PANE_USER)

    def user_pane_has_table(self) -> bool:
        return self._pane_has_table(self.PANE_USER)

    def user_pane_has_create_btn(self) -> bool:
        return self._pane_has_create_btn(self.PANE_USER)

    # —— 角色 tab 表格 ——

    def get_role_table_headers(self) -> list[str]:
        return self._pane_table_headers(self.PANE_ROLE)

    def get_role_table_row_count(self) -> int:
        return self._pane_table_row_count(self.PANE_ROLE)

    def role_pane_has_table(self) -> bool:
        return self._pane_has_table(self.PANE_ROLE)

    def role_pane_has_create_btn(self) -> bool:
        return self._pane_has_create_btn(self.PANE_ROLE)

    # —— 部门 tab 表格 ——

    def get_department_table_headers(self) -> list[str]:
        return self._pane_table_headers(self.PANE_DEPARTMENT)

    def get_department_table_row_count(self) -> int:
        return self._pane_table_row_count(self.PANE_DEPARTMENT)

    def department_pane_has_table(self) -> bool:
        return self._pane_has_table(self.PANE_DEPARTMENT)

    def department_pane_has_create_btn(self) -> bool:
        return self._pane_has_create_btn(self.PANE_DEPARTMENT)

    # ========================================================================
    #  搜索 & 筛选
    # ========================================================================

    def search(self, keyword: str):
        """在搜索框中输入关键词并回车触发搜索"""
        self.fill(self.SEARCH_INPUT, keyword)
        self.page.locator(self.SEARCH_INPUT).first.press("Enter")

    def clear_search(self):
        """清空搜索框 — 先尝试清空图标，再走 fill 兜底"""
        current = self.page.locator(self.SEARCH_INPUT).first.input_value() or ""
        if not current.strip():
            return
        locator = self.page.locator(self.SEARCH_INPUT).first
        # 方式1：点击搜索框内的清空图标（如果有）
        clear_icon = self.page.locator(f"{self.SEARCH_DIV} .el-input__clear")
        if clear_icon.count() > 0:
            try:
                self.page.locator(self.SEARCH_DIV).first.hover()
                self.page.wait_for_timeout(100)
                clear_icon.first.click(force=True)
                self.page.wait_for_timeout(300)
                return
            except Exception:
                pass
        # 方式2：Ctrl+A → Backspace → Enter 模拟手动清空
        locator.click()
        locator.press("Control+a")
        locator.press("Backspace")
        locator.press("Enter")
        self.page.wait_for_timeout(300)

    def get_search_value(self) -> str:
        """获取搜索框当前值"""
        return self.page.locator(self.SEARCH_INPUT).first.input_value()

    def filter_by_role(self, role_name: str):
        """按角色筛选：点击筛选下拉 → 选择指定角色"""
        self._select_filter_option(self.FILTER_ROLE_SELECT, role_name)

    def filter_by_department(self, dept_name: str):
        """按部门筛选：点击筛选下拉 → 选择指定部门"""
        self._select_filter_option(self.FILTER_DEPT_SELECT, dept_name)

    def filter_by_status(self, status: str):
        """按状态筛选：点击筛选下拉 → 选择'正常'或'禁用'"""
        self._select_filter_option(self.FILTER_STATUS_SELECT, status)

    def get_filter_role_value(self) -> str:
        return self.page.locator(self.FILTER_ROLE_INPUT).first.input_value() or ""

    def get_filter_dept_value(self) -> str:
        return self.page.locator(self.FILTER_DEPT_INPUT).first.input_value() or ""

    def get_filter_status_value(self) -> str:
        return self.page.locator(self.FILTER_STATUS_INPUT).first.input_value() or ""

    DROPDOWN_VISIBLE = '.el-select-dropdown[x-placement="bottom-start"]'
    DROPDOWN_ITEMS = f"{DROPDOWN_VISIBLE} ul li.el-select-dropdown__item"

    def _select_filter_option(self, select_selector: str, option_text: str):
        """点击 input → 等下拉 → 点选项"""
        self.page.locator(f"{select_selector} input").first.click()
        self.page.locator(self.DROPDOWN_VISIBLE).first.wait_for(state="visible", timeout=5000)
        self.page.locator(f'{self.DROPDOWN_ITEMS}:has-text("{option_text}")').first.click()
        self.page.wait_for_timeout(300)

    def _get_filter_options(self, select_selector: str) -> list[str]:
        """获取下拉选项列表"""
        self.page.locator(f"{select_selector} input").first.click()
        self.page.locator(self.DROPDOWN_VISIBLE).first.wait_for(state="visible", timeout=5000)
        items = self.page.locator(self.DROPDOWN_ITEMS).all()
        result = [item.inner_text().strip() for item in items if item.inner_text().strip()]
        self.page.locator("body").first.press("Escape")
        self.page.wait_for_timeout(150)
        return result

    def get_role_filter_options(self) -> list[str]:
        """获取角色筛选下拉的所有选项"""
        return self._get_filter_options(self.FILTER_ROLE_SELECT)

    def get_department_filter_options(self) -> list[str]:
        """获取部门筛选下拉的所有选项"""
        return self._get_filter_options(self.FILTER_DEPT_SELECT)

    def get_status_filter_options(self) -> list[str]:
        """获取状态下拉筛选的所有选项"""
        return self._get_filter_options(self.FILTER_STATUS_SELECT)

    # -- 清空筛选 --

    def _clear_select(self, select_selector: str):
        """清空 el-select 的选中值。

        策略（按优先级）：
        1. 先 hover 让 Element UI 的清空图标出现，再点击
        2. force-click 隐藏的清空图标
        3. JS 直接重置 Vue 组件值
        """
        current = self.page.locator(f"{select_selector} input").first.input_value() or ""
        if not current.strip():
            return

        # 先 hover 让清空图标可见
        self.page.locator(select_selector).first.hover()
        self.page.wait_for_timeout(150)

        clear_icon = self.page.locator(f"{select_selector} .el-icon-circle-close")
        # 尝试点击清空图标（force=True 可点击非完全可见的元素）
        if clear_icon.count() > 0:
            try:
                clear_icon.first.click(force=True, timeout=3000)
                self.page.wait_for_timeout(300)
                # 验证是否清空成功
                after = self.page.locator(f"{select_selector} input").first.input_value() or ""
                if not after.strip():
                    return
            except Exception:
                pass

        # 兜底：用 JS 重置（兼容 Vue2 __vue__ 和 Vue3 __vue_app__）
        try:
            self.page.locator(f"{select_selector} input").first.evaluate(
                """el => {
                    // Vue 2
                    let vm = el.__vue__;
                    if (vm && vm.$parent) {
                        vm.$parent.$emit('input', '');
                        return;
                    }
                    // Vue 3 / Element Plus
                    const root = el.closest('.el-select');
                    if (root && root.__vue__) {
                        root.__vue__.modelValue = '';
                        root.__vue__.selectedLabel = '';
                        return;
                    }
                    // 最后手段：直接改 DOM
                    el.value = '';
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                }"""
            )
            self.page.wait_for_timeout(200)
        except Exception:
            pass

    def clear_role_filter(self):
        """清空角色筛选下拉"""
        self._clear_select(self.FILTER_ROLE_SELECT)

    def clear_dept_filter(self):
        """清空部门筛选下拉"""
        self._clear_select(self.FILTER_DEPT_SELECT)

    def clear_status_filter(self):
        """清空状态筛选下拉"""
        self._clear_select(self.FILTER_STATUS_SELECT)

    def reset_all_filters(self):
        """清空所有筛选条件（搜索框 + 三个下拉），恢复表格默认状态。"""
        self.clear_search()
        self.clear_role_filter()
        self.clear_dept_filter()
        self.clear_status_filter()
        self.page.wait_for_timeout(300)

    # ========================================================================
    #  新建用户按钮
    # ========================================================================

    def click_create_user(self):
        """点击'新建用户'按钮，弹出新增用户表单弹窗"""
        self.page.locator(self.CREATE_USER_BTN).first.click()

    def is_create_user_button_visible(self) -> bool:
        return self.page.locator(self.CREATE_USER_BTN).first.is_visible()

    # ========================================================================
    #  表格列头操作
    # ========================================================================

    def get_table_headers(self) -> list[str]:
        """获取所有列头文本"""
        cells = self.page.locator(self.TABLE_HEADER_CELLS).all()
        return [c.locator(".vxe-cell--title span").first.inner_text().strip()
                for c in cells]

    def get_table_header_sortable(self) -> dict[str, bool]:
        """返回列头是否可排序的字典"""
        cells = self.page.locator(self.TABLE_HEADER_CELLS).all()
        result = {}
        for c in cells:
            title_el = c.locator(".vxe-cell--title span").first
            if title_el.count() > 0:
                name = title_el.inner_text().strip()
                # 存在排序图标说明可排序
                sortable = c.locator(".vxe-cell--sort").count() > 0
                result[name] = sortable
        return result

    def sort_by_column(self, column_name: str, ascending: bool = True):
        """点击列头排序图标
        column_name: '用户名' / '姓名' / '性别' / '角色' / '部门' / '参与项目' / '访问次数'
        ascending: True=升序, False=降序
        """
        header = self.page.locator(f'{self.TABLE_HEADER_CELLS}:has-text("{column_name}")')
        header.first.wait_for(state="visible")
        if ascending:
            header.locator("i.vxe-sort--asc-btn").first.click()
        else:
            header.locator("i.vxe-sort--desc-btn").first.click()

    def click_column_settings(self):
        """点击列设置图标（#pane-user .el-icon-setting）"""
        self.page.locator("#pane-user .el-icon-setting").first.click()

    # ========================================================================
    #  表格数据读取
    # ========================================================================

    def get_table_row_count(self) -> int:
        """获取当前页数据行数"""
        return self.page.locator(self.TABLE_BODY_ROWS).count()

    def get_table_data(self) -> list[dict[str, str | None]]:
        """读取当前页所有行数据
        Returns: [{序号, 用户名, 姓名, 性别, 角色, 部门, 参与项目, 访问次数, 状态}, ...]
        """
        rows = self.page.locator(self.TABLE_BODY_ROWS).all()
        result = []
        for row in rows:
            cells = row.locator("td")
            result.append({
                "序号": self._get_cell_text(cells.nth(0)),
                "用户名": self._get_cell_text(cells.nth(1)),
                "姓名": self._get_cell_text(cells.nth(2)),
                "性别": self._get_cell_text(cells.nth(3)),
                "角色": self._get_cell_text(cells.nth(4)),
                "部门": self._get_cell_text(cells.nth(5)),
                "参与项目": self._get_cell_text(cells.nth(6)),
                "访问次数": self._get_cell_text(cells.nth(7)),
                "状态": self._get_cell_text(cells.nth(8)),
            })
        return result

    def get_row_by_username(self, username: str) -> dict[str, str | None] | None:
        """按用户名查找行数据"""
        rows = self.get_table_data()
        for row in rows:
            if row.get("用户名") == username:
                return row
        return None

    def is_table_empty(self) -> bool:
        """表格是否为空（显示暂无数据）"""
        return self.page.locator(self.TABLE_EMPTY).first.is_visible()

    def get_empty_text(self) -> str:
        """获取空状态提示文本"""
        if self.page.locator(self.TABLE_EMPTY_TEXT).count() > 0:
            return self.page.locator(self.TABLE_EMPTY_TEXT).first.inner_text().strip()
        return ""

    def _get_cell_text(self, cell: Locator) -> str:
        """从 VXE-Table 的 td 中提取文本"""
        wrapper = cell.locator(".vxe-cell--wrapper")
        if wrapper.count() > 0:
            return wrapper.first.inner_text().strip()
        return cell.inner_text().strip()

    # ========================================================================
    #  行操作
    # ========================================================================

    def _get_row_by_index(self, index: int) -> Locator:
        """获取第 index 行（0-based）"""
        return self.page.locator(self.TABLE_BODY_ROWS).nth(index)

    def _get_row_by_username_cell(self, username: str) -> Locator | None:
        """通过用户名定位行"""
        rows = self.page.locator(self.TABLE_BODY_ROWS).all()
        for row in rows:
            uname_cell = row.locator("td").nth(1)
            if self._get_cell_text(uname_cell) == username:
                return row
        return None

    # -- 姓名按钮 → 查看用户详情弹窗 --

    def click_user_realname(self, username: str):
        """点击指定用户的姓名按钮，打开'查看用户'弹窗"""
        row = self._get_row_by_username_cell(username)
        if row is None:
            raise ValueError(f"用户 {username} 未在当前页找到")
        btn = row.locator("td").nth(2).locator("button")
        btn.first.click()

    def click_user_realname_by_index(self, row_index: int):
        """按行索引点击姓名按钮"""
        row = self._get_row_by_index(row_index)
        btn = row.locator("td").nth(2).locator("button")
        btn.first.click()

    # -- 参与项目按钮 → 参与项目弹窗 --

    def click_user_projects(self, username: str):
        """点击指定用户的参与项目数按钮"""
        row = self._get_row_by_username_cell(username)
        if row is None:
            raise ValueError(f"用户 {username} 未在当前页找到")
        btn = row.locator("td").nth(6).locator("button")
        btn.first.click()

    def click_user_projects_by_index(self, row_index: int):
        """按行索引点击参与项目数按钮"""
        row = self._get_row_by_index(row_index)
        btn = row.locator("td").nth(6).locator("button")
        btn.first.click()

    # -- 操作列图标 --

    def _get_action_cell(self, row: Locator) -> Locator:
        """获取行的操作列 cell（最后一列）"""
        return row.locator("td").last()

    def click_edit_user(self, username: str):
        """点击指定行的编辑图标"""
        row = self._get_row_by_username_cell(username)
        if row is None:
            raise ValueError(f"用户 {username} 未在当前页找到")
        row.locator(self.ACTION_EDIT_ICON).first.click()

    def click_edit_user_by_index(self, row_index: int):
        """按行索引点击编辑图标"""
        row = self._get_row_by_index(row_index)
        row.locator(self.ACTION_EDIT_ICON).first.click()

    def click_disable_user(self, username: str):
        """点击指定行的禁用图标"""
        row = self._get_row_by_username_cell(username)
        if row is None:
            raise ValueError(f"用户 {username} 未在当前页找到")
        row.locator(self.ACTION_DISABLE_ICON).first.click()

    def click_disable_user_by_index(self, row_index: int):
        """按行索引点击禁用图标"""
        row = self._get_row_by_index(row_index)
        row.locator(self.ACTION_DISABLE_ICON).first.click()

    def click_reset_user(self, username: str):
        """点击指定行的重置图标"""
        row = self._get_row_by_username_cell(username)
        if row is None:
            raise ValueError(f"用户 {username} 未在当前页找到")
        row.locator(self.ACTION_RESET_ICON).first.click()

    def click_reset_user_by_index(self, row_index: int):
        """按行索引点击重置图标"""
        row = self._get_row_by_index(row_index)
        row.locator(self.ACTION_RESET_ICON).first.click()

    def click_delete_user(self, username: str):
        """点击指定行的删除图标"""
        row = self._get_row_by_username_cell(username)
        if row is None:
            raise ValueError(f"用户 {username} 未在当前页找到")
        row.locator(self.ACTION_DELETE_ICON).first.click()

    def click_delete_user_by_index(self, row_index: int):
        """按行索引点击删除图标"""
        row = self._get_row_by_index(row_index)
        row.locator(self.ACTION_DELETE_ICON).first.click()

    def get_row_action_icons(self, row_index: int) -> list[str]:
        """获取指定行操作列所有图标的 iconfont class"""
        row = self._get_row_by_index(row_index)
        icons = row.locator("td").last().locator("i.iconfont").all()
        result = []
        for icon in icons:
            cls = icon.get_attribute("class") or ""
            for name in cls.split():
                if name.startswith("icon-"):
                    result.append(name)
                    break
        return result

    # ========================================================================
    #  分页操作（委托给 Pagination 组件，见 pages/component/pagination.py）
    #  使用方式：user_manager.pagination.get_total_count_number()
    #           user_manager.pagination.go_to_page(3)
    # ========================================================================

    # ========================================================================
    #  弹窗操作 — 全部委托给 UserDialog (pages/user_page/user_dialog.py)
    #  使用方式：user_manager.dialog.wait_for_user_form_dialog()
    #           user_manager.dialog.fill_fields(用户名="xxx", 姓名="xxx")
    #           user_manager.dialog.get_field_error("用户名")
    # ========================================================================

    # ========================================================================
    #  Toast 消息 → 委托给 Toast 组件 (pages/component/toast.py)
    #  使用方式：user_manager.toast.get_message()
    #           user_manager.toast.get_type()
    # ========================================================================
