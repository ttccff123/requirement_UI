"""
角色管理 - 主页面对象

体系数字工程开发平台 - 组织 → 角色页签页面对象 (#/organization, tab: 角色)

布局：
  左侧：角色树（搜索框 + 新建图标 + el-tree）
  右侧：成员表格（成员管理按钮 + vxe-table）
"""
import time

from playwright.sync_api import Locator

from pages.base_page import BasePage
from pages.component.toast import Toast
from pages.role_page.role_dialog import RoleDialog


class RoleManager(BasePage):
    """体系数字工程开发平台 - 组织 → 角色管理页面对象"""

    def __init__(self, page):
        super().__init__(page)
        self.toast = Toast(page)
        self.dialog = RoleDialog(page)

    # ================= 页面容器 =================
    PANE_ROLE = "#pane-role"
    ROLE_PAGE = f"{PANE_ROLE} .role-page"

    # ================= Tab 切换 =================
    TAB_ROLE = '.el-tabs__item:has-text("角色")'

    def click_role_tab(self):
        """切换到角色 tab"""
        self.page.locator(self.TAB_ROLE).first.click()
        self.wait_for_page()

    # ================= 左侧角色树 =================
    ROLE_ASIDE = f"{PANE_ROLE} .el-aside.aside-left-box"
    LEFT_TITLE = f"{ROLE_ASIDE} .left-title"
    ROLE_TREE = f"{ROLE_ASIDE} .el-tree"
    TREE_NODES = f"{ROLE_TREE} .el-tree-node"
    TREE_NODE_CONTENT = ".el-tree-node__content"
    TREE_NODE_LABEL = f"{TREE_NODE_CONTENT} .custom-tree-node .ellipsis"

    # 角色树搜索
    TREE_SEARCH_INPUT = f"{ROLE_ASIDE} .input-div input.el-input__inner"

    # 新建角色图标（左侧标题栏 +）
    ADD_ROLE_ICON = f"{LEFT_TITLE} .icon-xinjian_xinzeng_tianjia"

    # 角色操作菜单（el-dropdown）
    ROLE_MENU_TRIGGER = ".el-dropdown-selfdefine i.el-icon-more"
    ROLE_MENU = ".el-dropdown-menu.el-popper"
    ROLE_MENU_ITEMS = f"{ROLE_MENU} .el-dropdown-menu__item"

    # ================= 右侧成员区域 =================
    ROLE_MAIN = f"{PANE_ROLE} .el-container:not(.el-aside)"
    MEMBER_HEADER = f"{ROLE_MAIN} .kd-table-pro__header"
    MEMBER_HEADER_RIGHT = f"{MEMBER_HEADER} .kd-table-pro__header-right"
    MEMBER_MANAGE_BTN = f"{MEMBER_HEADER_RIGHT} .el-button--primary:has-text(\"成员管理\")"

    # 右侧表格
    TABLE_PRO = ".kd-table-pro"
    TABLE_MAIN = f"{TABLE_PRO} .kd-table-pro__main"
    TABLE_BODY_ROWS = f"{TABLE_MAIN} .vxe-table--body tr.vxe-body--row"

    # ================= 页面操作 =================

    def wait_for_page(self, timeout: int = 1000):
        """等待角色管理页面加载"""
        self.wait_for_selector(self.PANE_ROLE, timeout=timeout)
        self.page.locator(self.PANE_ROLE).first.wait_for(state="visible", timeout=timeout)

    def is_page_loaded(self) -> bool:
        return self.page.locator(self.PANE_ROLE).first.is_visible()

    # ================= 左侧树操作 =================

    def get_role_tree_nodes(self) -> list[Locator]:
        """获取所有角色树节点"""
        return self.page.locator(self.TREE_NODES).all()

    def get_role_tree_node_names(self) -> list[str]:
        """获取所有角色名称列表"""
        nodes = self.page.locator(f"{self.TREE_NODES} {self.TREE_NODE_LABEL}").all()
        return [n.inner_text().strip() for n in nodes]

    def click_role_node(self, role_name: str):
        """点击指定名称的角色树节点"""
        node = self.page.locator(
            f'{self.TREE_NODES}:has(.ellipsis:text-is("{role_name}"))'
        ).first
        node.locator(self.TREE_NODE_CONTENT).first.click()

    def is_role_node_selected(self, role_name: str) -> bool:
        """检查指定角色节点是否被选中"""
        node = self.page.locator(
            f'{self.TREE_NODES}:has(.ellipsis:text-is("{role_name}"))'
        ).first
        cls = node.get_attribute("class") or ""
        return "is-current" in cls

    def open_role_context_menu(self, role_name: str):
        """打开指定角色的右键菜单（hover 节点 → 点击 ... 图标）。"""
        node = self.page.locator(
            f'{self.TREE_NODES}:has(.ellipsis:text-is("{role_name}"))'
        ).first
        # hover 使 ... 图标出现
        node.locator(self.TREE_NODE_CONTENT).first.hover()
        self.page.wait_for_timeout(100)
        node.locator(self.ROLE_MENU_TRIGGER).first.click()
        self.page.wait_for_timeout(200)

    def click_role_menu_item(self, item_text: str):
        """点击角色菜单中的选项（如：编辑角色、复制角色、删除角色）"""
        menu_item = self.page.locator(
            f'{self.ROLE_MENU_ITEMS}:has-text("{item_text}"):visible'
        ).first
        menu_item.wait_for(state="visible", timeout=5000)
        menu_item.click()

    def get_role_menu_items(self) -> list[str]:
        """获取当前可见的菜单项文本"""
        items = self.page.locator(f"{self.ROLE_MENU_ITEMS}:visible").all()
        return [it.inner_text().strip() for it in items]

    # ================= 左侧搜索 =================

    def search_role(self, keyword: str):
        """在角色树搜索框中输入关键字"""
        inp = self.page.locator(self.TREE_SEARCH_INPUT).first
        inp.fill(keyword)
        self.page.wait_for_timeout(150)

    def clear_role_search(self):
        """清空角色树搜索框"""
        inp = self.page.locator(self.TREE_SEARCH_INPUT).first
        inp.fill("")
        self.page.wait_for_timeout(150)

    def get_search_placeholder(self) -> str:
        """获取搜索框 placeholder"""
        inp = self.page.locator(self.TREE_SEARCH_INPUT).first
        return inp.get_attribute("placeholder") or ""

    # ================= 右侧成员表格 =================

    def get_member_table_data(self) -> list[dict[str, str | None]]:
        """读取右侧成员表格数据"""
        rows = self.page.locator(f"{self.ROLE_MAIN} {self.TABLE_BODY_ROWS}").all()
        result = []
        for row in rows:
            cells = row.locator("td").all()
            if len(cells) < 6:
                continue
            result.append({
                "序号": cells[0].inner_text().strip(),
                "用户名": cells[1].inner_text().strip(),
                "姓名": cells[2].inner_text().strip(),
                "性别": cells[3].inner_text().strip(),
                "部门": cells[4].inner_text().strip(),
                "参与项目": cells[5].inner_text().strip(),
            })
        return result

    def click_member_manage(self):
        """点击成员管理按钮"""
        self.page.locator(self.MEMBER_MANAGE_BTN).first.click()

    # ================= 成员表格搜索 =================

    MEMBER_SEARCH_INPUT = f"{MEMBER_HEADER} input[placeholder*='搜索']"

    def get_member_search_placeholder(self) -> str:
        """获取成员表格搜索框 placeholder"""
        inp = self.page.locator(self.MEMBER_SEARCH_INPUT).first
        if inp.count() > 0:
            return inp.get_attribute("placeholder") or ""
        return ""

    def search_member_table(self, keyword: str):
        """在成员表格搜索框输入关键字并触发搜索"""
        inp = self.page.locator(self.MEMBER_SEARCH_INPUT).first
        inp.fill(keyword)
        self.page.wait_for_timeout(200)
        # 模拟回车触发搜索
        inp.press("Enter")
        self.page.wait_for_timeout(300)

    def clear_member_search(self):
        """清空成员表格搜索框"""
        inp = self.page.locator(self.MEMBER_SEARCH_INPUT).first
        inp.fill("")
        inp.press("Enter")
        self.page.wait_for_timeout(300)

    # ================= 成员表格状态筛选 =================

    STATUS_SELECT = f"{MEMBER_HEADER} .el-select, {MEMBER_HEADER} .kd-select"

    def open_status_dropdown(self):
        """打开状态下拉框"""
        sel = self.page.locator(self.STATUS_SELECT).first
        sel.click()
        self.page.wait_for_timeout(200)

    def get_status_options(self) -> list[str]:
        """获取状态下拉选项文本列表"""
        opts = self.page.locator(
            ".el-select-dropdown:visible .el-select-dropdown__item, "
            ".el-popper:visible .el-select-dropdown__item, "
            ".el-select-dropdown:visible li"
        ).all()
        return [o.inner_text().strip() for o in opts if o.inner_text().strip()]

    def select_status(self, status_text: str):
        """选择指定状态"""
        self.open_status_dropdown()
        opt = self.page.locator(
            f".el-select-dropdown:visible .el-select-dropdown__item:has-text('{status_text}')"
        ).first
        if opt.count() > 0:
            opt.click()
            self.page.wait_for_timeout(300)

    def clear_status_filter(self):
        """清空状态筛选（选择'全部'或第一个选项）"""
        self.open_status_dropdown()
        first = self.page.locator(
            ".el-select-dropdown:visible .el-select-dropdown__item"
        ).first
        if first.count() > 0:
            first.click()
            self.page.wait_for_timeout(300)

    # ================= 成员表格列设置 =================

    COL_SETTINGS_BTN = (
        f"{MEMBER_HEADER_RIGHT} .icon-shezhi, "
        f"{MEMBER_HEADER_RIGHT} [title*='列设置'], "
        f"{MEMBER_HEADER_RIGHT} [title*='设置'], "
        f"{MEMBER_HEADER_RIGHT} .el-icon-setting, "
        f"{MEMBER_HEADER} .el-icon-setting, "
        f"{MEMBER_HEADER_RIGHT} .vxe-icon--setting, "
        f"{MEMBER_HEADER_RIGHT} .kd-table-pro__setting-btn, "
        f"{MEMBER_HEADER_RIGHT} [class*='setting'], "
        f"{MEMBER_HEADER_RIGHT} [class*='shezhi'], "
        f"{MEMBER_HEADER_RIGHT} [class*='gear']"
    )
    COL_SETTINGS_POPOVER = (
        ".el-popper:visible, "
        ".vxe-table--setting-wrapper:visible, "
        ".vxe-table--setting-panel:visible, "
        ".vxe-modal--wrapper:visible, "
        ".el-dialog__wrapper:visible:has(.el-dialog:not(.kd-dialog)), "
        ".kd-table-pro__setting-panel:visible, "
        ".el-dropdown-menu:visible"
    )

    def open_column_settings(self):
        """打开列设置"""
        btn = self.page.locator(self.COL_SETTINGS_BTN).first
        if btn.count() > 0:
            btn.click()
            self.page.wait_for_timeout(300)

    def is_column_settings_open(self) -> bool:
        """列设置是否打开"""
        return self.page.locator(self.COL_SETTINGS_POPOVER).first.is_visible()

    def get_column_settings_title(self) -> str:
        """获取列设置弹窗 title"""
        title_el = self.page.locator(
            f"{self.COL_SETTINGS_POPOVER} .el-dialog__title, "
            f"{self.COL_SETTINGS_POPOVER} .vxe-modal--header-title"
        ).first
        if title_el.count() > 0:
            return title_el.inner_text().strip()
        return ""

    def get_column_settings_checkboxes(self) -> list:
        """获取列设置中所有复选框标签"""
        cbs = self.page.locator(
            f"{self.COL_SETTINGS_POPOVER} .el-checkbox__label"
        ).all()
        return [cb.inner_text().strip() for cb in cbs if cb.inner_text().strip()]

    def toggle_column_setting(self, label: str):
        """切换列设置中指定列的勾选状态"""
        cb = self.page.locator(
            f"{self.COL_SETTINGS_POPOVER} .el-checkbox:has-text('{label}')"
        ).first
        if cb.count() > 0:
            cb.click()
            self.page.wait_for_timeout(100)

    def is_column_setting_checked(self, label: str) -> bool:
        """检查列设置中指定列是否勾选"""
        cb = self.page.locator(
            f"{self.COL_SETTINGS_POPOVER} .el-checkbox:has-text('{label}')"
        ).first
        if cb.count() == 0:
            return False
        return "is-checked" in (cb.get_attribute("class") or "")

    def search_column_setting(self, keyword: str):
        """在列设置中搜索"""
        inp = self.page.locator(
            f"{self.COL_SETTINGS_POPOVER} input[placeholder*='搜索'], "
            f"{self.COL_SETTINGS_POPOVER} input.el-input__inner"
        ).first
        if inp.count() > 0:
            inp.fill(keyword)
            self.page.wait_for_timeout(200)

    def click_column_settings_confirm(self):
        """列设置 - 点确定"""
        btn = self.page.locator(
            f"{self.COL_SETTINGS_POPOVER} .el-button--primary:has-text('确定')"
        ).first
        if btn.count() > 0:
            btn.click()
            self.page.wait_for_timeout(300)

    def click_column_settings_cancel(self):
        """列设置 - 点取消"""
        btn = self.page.locator(
            f"{self.COL_SETTINGS_POPOVER} .el-button--default:has-text('取消')"
        ).first
        if btn.count() > 0:
            btn.click()
            self.page.wait_for_timeout(200)

    def click_column_settings_close(self):
        """列设置 - 点 X 关闭"""
        close_btn = self.page.locator(
            f"{self.COL_SETTINGS_POPOVER} .el-icon-close, "
            f"{self.COL_SETTINGS_POPOVER} .vxe-modal--header-close"
        ).first
        if close_btn.count() > 0:
            close_btn.click()
            self.page.wait_for_timeout(200)

    # ================= 成员表格行内按钮点击 → 弹窗 =================

    def _get_row_by_index(self, row_index: int):
        """获取表格指定行（0-indexed）的 Locator"""
        rows = self.page.locator(f"{self.ROLE_MAIN} {self.TABLE_BODY_ROWS}").all()
        if row_index < len(rows):
            return rows[row_index]
        return None

    def click_member_name_button_by_index(self, row_index: int):
        """按行索引点击姓名列的按钮（跳转查看用户弹窗）"""
        row = self._get_row_by_index(row_index)
        if row is None:
            raise IndexError(f"行索引 {row_index} 超出表格范围")
        btn = row.locator("td").nth(2).locator("button")
        btn.first.click()

    def click_member_projects_button_by_index(self, row_index: int):
        """按行索引点击参与项目列的按钮（跳转参与项目弹窗）"""
        row = self._get_row_by_index(row_index)
        if row is None:
            raise IndexError(f"行索引 {row_index} 超出表格范围")
        btn = row.locator("td").nth(5).locator("button")
        btn.first.click()

    def get_member_first_project_count(self) -> int | None:
        """获取第一个成员的参与项目数。返回 None 表示没有成员或项目数为0。"""
        data = self.get_member_table_data()
        if not data:
            return None
        for row in data:
            try:
                val = int(row.get("参与项目", "0") or "0")
                if val > 0:
                    return val
            except (ValueError, TypeError):
                continue
        return None

    # ================= 成员表格排序 =================

    def click_column_sort(self, column_label: str):
        """点击指定列的排序触发区域"""
        header = self.page.locator(
            f"{self.ROLE_MAIN} .vxe-header--column:has-text('{column_label}')"
        ).first
        if header.count() > 0:
            # 点击列的排序图标或列头
            sort_trigger = header.locator(".vxe-cell--sort, .vxe-sort--asc-btn, .vxe-sort--desc-btn")
            if sort_trigger.count() > 0:
                sort_trigger.first.click()
            else:
                header.click()
            self.page.wait_for_timeout(300)

    def get_sort_order(self, column_label: str) -> str:
        """获取指定列的排序状态: 'asc', 'desc', 'none'"""
        header = self.page.locator(
            f"{self.ROLE_MAIN} .vxe-header--column:has-text('{column_label}')"
        ).first
        if header.count() == 0:
            return "none"
        cls = header.get_attribute("class") or ""
        if "sort-asc" in cls or "vxe-cell--sort-asc" in cls:
            return "asc"
        if "sort-desc" in cls or "vxe-cell--sort-desc" in cls:
            return "desc"
        return "none"

    def get_column_values(self, col_index: int) -> list[str]:
        """获取表格指定列的所有单元格文本（用于排序校验）"""
        rows = self.page.locator(f"{self.ROLE_MAIN} {self.TABLE_BODY_ROWS}").all()
        values = []
        for row in rows:
            cells = row.locator("td").all()
            if len(cells) > col_index:
                values.append(cells[col_index].inner_text().strip())
        return values

    # ================= 成员表格分页 =================

    PAGER = f"{ROLE_MAIN} .vxe-pager, {ROLE_MAIN} .el-pagination"

    def go_to_next_page(self):
        """成员表格 - 翻到下一页"""
        next_btn = self.page.locator(
            f"{self.PAGER} .el-pagination__next, "
            f"{self.PAGER} .vxe-pager--next-btn:not(.is--disabled)"
        ).first
        if next_btn.count() > 0:
            next_btn.click()
            self.page.wait_for_timeout(400)

    def get_current_page(self) -> int:
        """获取当前页码"""
        page_el = self.page.locator(
            f"{self.PAGER} .el-pager li.active, "
            f"{self.PAGER} .vxe-pager--num-btn.is--active"
        ).first
        if page_el.count() > 0:
            try:
                return int(page_el.inner_text().strip())
            except ValueError:
                pass
        return 1

    def get_total_pages(self) -> int:
        """获取总页数"""
        pages = self.page.locator(
            f"{self.PAGER} .el-pager li.number, "
            f"{self.PAGER} .vxe-pager--num-btn"
        ).all()
        if pages:
            nums = []
            for p in pages:
                try:
                    nums.append(int(p.inner_text().strip()))
                except ValueError:
                    pass
            return max(nums) if nums else 1
        return 1

    # ================= Toast =================

    def get_toast_message(self) -> str:
        return self.toast.get_message()

    # ======================== 添加角色 ========================

    def click_add_role(self):
        """点击新建角色图标 → 打开新增弹窗"""
        self.page.locator(self.ADD_ROLE_ICON).first.click()
        self.dialog.wait_for_role_form_dialog()

    # ======================== 编辑角色 ========================

    def click_edit_role(self, role_name: str):
        """右键菜单 → 编辑角色 → 打开编辑弹窗"""
        self.open_role_context_menu(role_name)
        self.click_role_menu_item("编辑角色")
        self.dialog.wait_for_role_form_dialog()

    # ======================== 复制角色 ========================

    def click_copy_role(self, role_name: str) -> str:
        """右键菜单 → 复制角色 → 返回复制后的角色名。

        复制操作无弹窗，点击菜单项后轮询等待树节点增加（最多 8 秒）。
        """
        before = set(self.get_role_tree_node_names())
        self.open_role_context_menu(role_name)
        self.click_role_menu_item("复制角色")
        deadline = time.time() + 6
        while time.time() < deadline:
            self.page.wait_for_timeout(400)
            after = set(self.get_role_tree_node_names())
            new_names = after - before
            if new_names:
                return new_names.pop()
        return f"{role_name}(1)"

    # ======================== 删除角色 ========================

    def click_delete_role(self, role_name: str):
        """右键菜单 → 删除角色 → 打开确认弹窗"""
        self.open_role_context_menu(role_name)
        self.click_role_menu_item("删除角色")
        self.dialog.wait_for_confirm_dialog()

    # ======================== 成员管理 ========================

    def click_member_manage_for_role(self, role_name: str):
        """选中角色 → 点击成员管理按钮 → 打开成员弹窗"""
        self.click_role_node(role_name)
        self.click_member_manage()
        self.dialog.wait_for_member_dialog()

    # ======================== 搜索 ========================

    def get_search_placeholder_text(self) -> str:
        """获取搜索框 placeholder"""
        return self.get_search_placeholder()

    def search_role_tree(self, keyword: str):
        """搜索角色树"""
        self.search_role(keyword)

    def clear_role_search_text(self):
        """清空搜索"""
        self.clear_role_search()

    # ======================== 功能权限页签 ========================

    # 功能权限 tab
    PERM_TAB = '#pane-role .el-tabs__item:has-text("功能权限")'

    # 权限复选框容器（限制在角色主区域）
    PERM_CHECKBOX = f"{ROLE_MAIN} .el-checkbox"
    PERM_CHECKBOX_LABEL = f"{PERM_CHECKBOX} .el-checkbox__label"
    PERM_CHECKBOX_CHECKED = f"{ROLE_MAIN} .el-checkbox.is-checked"
    PERM_SELECT_ALL = f'{ROLE_MAIN} .el-checkbox:has(.el-checkbox__label:text-is("全选"))'

    # 权限保存按钮（如果存在）
    PERM_SAVE_BTN = (
        f'{ROLE_MAIN} .el-button--primary:has-text("保存"),'
        f'{ROLE_MAIN} .el-button--primary:has-text("确定")'
    )

    def click_perm_tab(self):
        """切换到功能权限页签并等待面板加载。"""
        self.page.locator(self.PERM_TAB).first.click()
        self.page.wait_for_timeout(150)
        self.wait_for_perm_panel()

    def wait_for_perm_panel(self, timeout: int = 10000):
        """等待功能权限面板加载（全选复选框可见）。"""
        self.wait_for_selector(f"{self.PERM_SELECT_ALL}:visible", timeout=timeout)

    def is_perm_tab_active(self) -> bool:
        """功能权限页签是否处于激活状态。"""
        tab = self.page.locator(self.PERM_TAB).first
        return "is-active" in (tab.get_attribute("class") or "")

    def get_perm_checkboxes(self) -> list[Locator]:
        """获取功能权限面板中所有复选框元素。"""
        return self.page.locator(self.PERM_CHECKBOX).all()

    def get_perm_labels(self) -> list[str]:
        """获取所有权限项标签文本（不含"全选"）。"""
        labels = self.page.locator(
            f'{self.ROLE_MAIN} .el-checkbox:not(:has(.el-checkbox__label:text-is("全选"))) '
            '.el-checkbox__label'
        ).all()
        return [el.inner_text().strip() for el in labels if el.inner_text().strip()]

    def get_checked_perm_labels(self) -> list[str]:
        """获取已勾选的权限标签文本（排序后返回，便于比对）。"""
        checked = self.page.locator(
            f'{self.PERM_CHECKBOX_CHECKED} .el-checkbox__label'
        ).all()
        return sorted([el.inner_text().strip() for el in checked if el.inner_text().strip()])

    def get_perm_count(self) -> int:
        """获取权限总数（不含全选复选框）。"""
        return self.page.locator(
            f'{self.ROLE_MAIN} .el-checkbox:not(:has(.el-checkbox__label:text-is("全选")))'
        ).count()

    def get_checked_perm_count(self) -> int:
        """获取已勾选权限数。"""
        return self.page.locator(self.PERM_CHECKBOX_CHECKED).count()

    def is_perm_checked(self, label: str) -> bool:
        """检查指定权限是否已勾选。"""
        cb = self.page.locator(
            f'{self.ROLE_MAIN} .el-checkbox:has(.el-checkbox__label:text-is("{label}"))'
        ).first
        if cb.count() == 0:
            return False
        return "is-checked" in (cb.get_attribute("class") or "")

    def toggle_perm(self, label: str):
        """切换指定权限的勾选状态（勾选↔取消）。"""
        cb = self.page.locator(
            f'{self.ROLE_MAIN} .el-checkbox:has(.el-checkbox__label:text-is("{label}"))'
        ).first
        # 点击 checkbox 的 input 区域（而非 label，避免文本选中副作用）
        cb_input = cb.locator(".el-checkbox__input").first
        cb_input.click()
        self.page.wait_for_timeout(100)

    def check_perm(self, label: str):
        """勾选指定权限（已勾选则跳过）。"""
        if not self.is_perm_checked(label):
            self.toggle_perm(label)

    def uncheck_perm(self, label: str):
        """取消勾选指定权限（未勾选则跳过）。"""
        if self.is_perm_checked(label):
            self.toggle_perm(label)

    def toggle_select_all_perms(self):
        """切换全选复选框。"""
        self.page.locator(self.PERM_SELECT_ALL).first.click()
        self.page.wait_for_timeout(150)

    def click_perm_save(self):
        """点击功能权限面板的保存按钮（如存在）。"""
        btn = self.page.locator(self.PERM_SAVE_BTN).first
        if btn.count() > 0:
            btn.click()
            self.page.wait_for_timeout(250)

    def get_perm_snapshot(self) -> str:
        """获取当前角色已勾选权限的快照文本（用于权限比对）。"""
        labels = self.get_checked_perm_labels()
        return "|".join(labels)

    # ================= 权限面板搜索 =================

    PERM_SEARCH_INPUT = f"{ROLE_MAIN} .perm-filter input, {ROLE_MAIN} .el-input input[placeholder*='搜索'], {ROLE_MAIN} input[placeholder*='权限'], {ROLE_MAIN} input[placeholder*='筛选']"

    def get_perm_search_placeholder(self) -> str:
        """获取权限面板搜索框 placeholder"""
        inp = self.page.locator(self.PERM_SEARCH_INPUT).first
        if inp.count() > 0:
            return inp.get_attribute("placeholder") or ""
        return ""

    def search_perm(self, keyword: str):
        """在权限面板搜索框中输入关键字"""
        inp = self.page.locator(self.PERM_SEARCH_INPUT).first
        if inp.count() > 0:
            inp.fill(keyword)
            self.page.wait_for_timeout(400)

    def clear_perm_search(self):
        """清空权限面板搜索框"""
        inp = self.page.locator(self.PERM_SEARCH_INPUT).first
        if inp.count() > 0:
            inp.fill("")
            self.page.wait_for_timeout(300)

    def get_perm_highlighted_labels(self) -> list[str]:
        """获取权限面板中被高亮标记的标签（搜索命中）。"""
        # 常见的搜索高亮方式：mark 标签 / .highlight / .is-highlight / .el-tree-node__label span
        highlighted = self.page.locator(
            f"{self.ROLE_MAIN} .highlight, "
            f"{self.ROLE_MAIN} .is-highlight, "
            f"{self.ROLE_MAIN} .el-tree-node.is-highlight .el-tree-node__label, "
            f"{self.ROLE_MAIN} mark, "
            f"{self.ROLE_MAIN} [class*='highlight'] .el-tree-node__label"
        ).all()
        return [el.inner_text().strip() for el in highlighted if el.inner_text().strip()]

    def get_perm_all_visible_labels(self) -> list[str]:
        """获取当前可见的所有权限标签（搜索过滤后只显示匹配的）。"""
        # 过滤后不可见的节点会有 display:none
        nodes = self.page.locator(
            f"{self.ROLE_MAIN} .el-tree-node:not([style*='display: none']) .el-tree-node__label, "
            f"{self.ROLE_MAIN} .el-checkbox:not([style*='display: none']) .el-checkbox__label"
        ).all()
        return [n.inner_text().strip() for n in nodes if n.inner_text().strip()]

    # ================= 权限树结构 =================

    PERM_TREE = f"{ROLE_MAIN} .el-tree"
    PERM_TREE_NODES = f"{PERM_TREE} .el-tree-node"
    PERM_TREE_NODE_CONTENT = ".el-tree-node__content"
    PERM_TREE_NODE_LABEL = f"{PERM_TREE_NODE_CONTENT} .el-tree-node__label"
    PERM_TREE_NODE_EXPAND = ".el-tree-node__expand-icon"

    def expand_perm_node(self, label: str):
        """展开指定标签的权限树节点。"""
        node = self.page.locator(
            f'{self.PERM_TREE_NODES}:has(.el-tree-node__label:text-is("{label}"))'
        ).first
        if node.count() == 0:
            return
        expand_icon = node.locator(self.PERM_TREE_NODE_EXPAND)
        if expand_icon.count() > 0 and "expanded" not in (expand_icon.get_attribute("class") or ""):
            expand_icon.first.click()
            self.page.wait_for_timeout(200)

    def is_perm_node_expanded(self, label: str) -> bool:
        """检查指定权限节点是否已展开。"""
        node = self.page.locator(
            f'{self.PERM_TREE_NODES}:has(.el-tree-node__label:text-is("{label}"))'
        ).first
        if node.count() == 0:
            return False
        expand_icon = node.locator(self.PERM_TREE_NODE_EXPAND)
        if expand_icon.count() == 0:
            return True  # 叶子节点
        return "expanded" in (expand_icon.get_attribute("class") or "")

    def get_perm_node_children(self, parent_label: str) -> list[str]:
        """获取指定父节点下的直接子节点标签列表。"""
        parent = self.page.locator(
            f'{self.PERM_TREE_NODES}:has(.el-tree-node__label:text-is("{parent_label}"))'
        ).first
        if parent.count() == 0:
            return []
        # 子节点在父节点的 .el-tree-node__children 中（直接子级）
        children = parent.locator("> .el-tree-node__children > .el-tree-node")
        if children.count() == 0:
            return []
        labels = children.locator(self.PERM_TREE_NODE_LABEL).all()
        return [l.inner_text().strip() for l in labels if l.inner_text().strip()]

    def get_perm_node_parent(self, child_label: str) -> str:
        """获取子节点的父节点标签（向上找最近的非叶子节点）。"""
        child = self.page.locator(
            f'{self.PERM_TREE_NODES}:has(.el-tree-node__label:text-is("{child_label}"))'
        ).first
        if child.count() == 0:
            return ""
        # Playwright 支持 CSS :has 但不支持父选择器，用 JS 取
        parent_label = self.page.evaluate("""
            (label) => {
                const nodes = document.querySelectorAll('.el-tree-node');
                for (const node of nodes) {
                    const labelEl = node.querySelector('.el-tree-node__label');
                    if (labelEl && labelEl.textContent.trim() === label) {
                        const parent = node.closest('.el-tree-node__children')?.closest('.el-tree-node');
                        if (parent) {
                            const pLabel = parent.querySelector('.el-tree-node__label');
                            return pLabel ? pLabel.textContent.trim() : '';
                        }
                    }
                }
                return '';
            }
        """, child_label)
        return parent_label.strip() if parent_label else ""

    def perm_node_has_children(self, label: str) -> bool:
        """检查节点是否有子节点（非叶子）。"""
        node = self.page.locator(
            f'{self.PERM_TREE_NODES}:has(.el-tree-node__label:text-is("{label}"))'
        ).first
        if node.count() == 0:
            return False
        return "is-leaf" not in (node.get_attribute("class") or "")

    def is_perm_node_indeterminate(self, label: str) -> bool:
        """检查复选框是否处于半选状态（部分子节点被勾选）。"""
        cb = self.page.locator(
            f'{self.ROLE_MAIN} .el-checkbox:has(.el-checkbox__label:text-is("{label}"))'
        ).first
        if cb.count() == 0:
            return False
        return "is-indeterminate" in (cb.get_attribute("class") or "")

    # ================= 多用户切换 =================

    def create_user_for_role(self, browser_manager, role_name: str):
        """为权限测试创建独立上下文：新建页面 → 登录为 tcf → 返回 page。
        返回 (ctx, page) 元组，使用后需 ctx.close() 清理。
        """
        from pages.login_page import LoginPage
        from config.settings import BASE_URL, LOGIN_PASSWORD
        ctx = browser_manager.browser.new_context(
            viewport={"width": 1440, "height": 900},
        )
        page = ctx.new_page()
        lp = LoginPage(page)
        lp.open(BASE_URL)
        lp.login("tcf", LOGIN_PASSWORD)
        page.locator(".kd-aside").first.wait_for(state="visible", timeout=30000)
        return ctx, page
