"""
部门管理 - 主页面对象

体系数字工程开发平台 - 组织 → 部门页签页面对象 (#/organization, tab: 部门)

布局：
  左侧：部门树（搜索框 + 新建图标 + el-tree）
  右侧：成员表格（成员管理按钮 + vxe-table）
"""
import time

from playwright.sync_api import Locator

from pages.base_page import BasePage
from pages.component.toast import Toast
from pages.dept_page.dept_dialog import DeptDialog


class DeptManager(BasePage):
    """体系数字工程开发平台 - 组织 → 部门管理页面对象"""

    def __init__(self, page):
        super().__init__(page)
        self.toast = Toast(page)
        self.dialog = DeptDialog(page)

    # ================= 页面容器 =================
    PANE_DEPT = "#pane-department"

    # ================= Tab 切换 =================
    TAB_DEPT = '.el-tabs__item:has-text("部门")'

    def click_dept_tab(self):
        self.page.locator(self.TAB_DEPT).first.click()
        self.wait_for_page()

    # ================= 左侧部门树 =================
    # 部门面板可能使用与角色面板不同的布局，提供多个回退选择器
    DEPT_ASIDE_SEL = (
        f"{PANE_DEPT} .el-aside.aside-left-box,"
        f"{PANE_DEPT} .el-aside,"
        f"{PANE_DEPT} .left-panel,"
        f"{PANE_DEPT} .left-box"
    )
    TREE_SEARCH_INPUT_SEL = (
        f"{PANE_DEPT} .input-div input.el-input__inner,"
        f"{PANE_DEPT} .el-input input[placeholder*='搜索'],"
        f"{PANE_DEPT} input[placeholder*='部门']"
    )
    ADD_DEPT_ICON_SEL = (
        f"{PANE_DEPT} .icon-xinjian_xinzeng_tianjia,"
        f"{PANE_DEPT} [class*='xinjian'],"
        f"{PANE_DEPT} .el-button--primary .el-icon-plus,"
        f"{PANE_DEPT} button:has-text('新建')"
    )
    TREE_SEL = (
        f"{PANE_DEPT} .el-tree,"
        f"{PANE_DEPT} .kd-tree"
    )
    TREE_NODES_SEL = ".el-tree-node"
    TREE_NODE_CONTENT = ".el-tree-node__content"
    TREE_NODE_LABEL = f"{TREE_NODE_CONTENT} .custom-tree-node .ellipsis, {TREE_NODE_CONTENT} .el-tree-node__label"

    # 部门操作菜单
    DEPT_MENU_TRIGGER = ".el-dropdown-selfdefine i.el-icon-more"
    DEPT_MENU = ".el-dropdown-menu.el-popper"
    DEPT_MENU_ITEMS = f"{DEPT_MENU} .el-dropdown-menu__item"

    # ================= 右侧成员区域 =================
    DEPT_MAIN = f"{PANE_DEPT} .el-container:not(.el-aside), {PANE_DEPT} .right-panel, {PANE_DEPT} .main-panel"
    MEMBER_HEADER = f"{DEPT_MAIN} .kd-table-pro__header"
    MEMBER_HEADER_RIGHT = f"{MEMBER_HEADER} .kd-table-pro__header-right"
    MEMBER_MANAGE_BTN = f"{MEMBER_HEADER_RIGHT} .el-button--primary:has-text(\"成员管理\")"

    TABLE_PRO = ".kd-table-pro"
    TABLE_MAIN = f"{TABLE_PRO} .kd-table-pro__main"
    TABLE_BODY_ROWS = f"{TABLE_MAIN} .vxe-table--body tr.vxe-body--row"

    # ================= 页面操作 =================

    def wait_for_page(self, timeout: int = 2000):
        """快速检查 #pane-department 是否在 DOM 中（不强制可见）。"""
        try:
            self.page.locator(self.PANE_DEPT).first.wait_for(state="attached", timeout=timeout)
        except Exception:
            pass

    def is_page_loaded(self) -> bool:
        return self.page.locator(self.PANE_DEPT).first.is_visible()

    # ================= 左侧树操作 =================

    def _tree_locator(self) -> str:
        """动态解析可用树选择器。"""
        for sel in self.TREE_SEL.split(","):
            s = sel.strip()
            if self.page.locator(s).count() > 0:
                return s
        return self.TREE_SEL.split(",")[0].strip()

    def get_dept_tree_nodes(self) -> list[Locator]:
        tree = self._tree_locator()
        return self.page.locator(f"{tree} {self.TREE_NODES_SEL}").all()

    def get_dept_tree_node_names(self) -> list[str]:
        tree = self._tree_locator()
        nodes = self.page.locator(f"{tree} {self.TREE_NODES_SEL} {self.TREE_NODE_LABEL}").all()
        return [n.inner_text().strip() for n in nodes]

    def click_dept_node(self, dept_name: str):
        tree = self._tree_locator()
        node = self.page.locator(
            f'{tree} {self.TREE_NODES_SEL}:has(.ellipsis:text-is("{dept_name}")),'
            f'{tree} {self.TREE_NODES_SEL}:has(.el-tree-node__label:text-is("{dept_name}"))'
        ).first
        node.locator(self.TREE_NODE_CONTENT).first.click()

    def is_dept_node_selected(self, dept_name: str) -> bool:
        tree = self._tree_locator()
        node = self.page.locator(
            f'{tree} {self.TREE_NODES_SEL}:has(.ellipsis:text-is("{dept_name}")),'
            f'{tree} {self.TREE_NODES_SEL}:has(.el-tree-node__label:text-is("{dept_name}"))'
        ).first
        cls = node.get_attribute("class") or ""
        return "is-current" in cls

    def open_dept_context_menu(self, dept_name: str):
        tree = self._tree_locator()
        node = self.page.locator(
            f'{tree} {self.TREE_NODES_SEL}:has(.ellipsis:text-is("{dept_name}")),'
            f'{tree} {self.TREE_NODES_SEL}:has(.el-tree-node__label:text-is("{dept_name}"))'
        ).first
        if node.count() == 0:
            raise RuntimeError(f"未找到部门节点: {dept_name}")
        node.locator(self.TREE_NODE_CONTENT).first.hover()
        self.page.wait_for_timeout(100)
        # 尝试找菜单触发图标（不存在则抛异常）
        icon = node.locator(self.DEPT_MENU_TRIGGER).first
        icon.wait_for(state="visible", timeout=3000)
        icon.click()
        self.page.wait_for_timeout(200)

    def click_dept_menu_item(self, item_text: str):
        menu_item = self.page.locator(
            f'{self.DEPT_MENU_ITEMS}:has-text("{item_text}"):visible'
        ).first
        menu_item.wait_for(state="visible", timeout=5000)
        menu_item.click()

    def get_dept_menu_items(self) -> list[str]:
        items = self.page.locator(f"{self.DEPT_MENU_ITEMS}:visible").all()
        return [it.inner_text().strip() for it in items]

    # ================= 左侧搜索 =================

    def search_dept(self, keyword: str):
        for sel in self.TREE_SEARCH_INPUT_SEL.split(","):
            s = sel.strip()
            inp = self.page.locator(s).first
            if inp.count() > 0:
                inp.fill(keyword)
                self.page.wait_for_timeout(150)
                return

    def clear_dept_search(self):
        for sel in self.TREE_SEARCH_INPUT_SEL.split(","):
            s = sel.strip()
            inp = self.page.locator(s).first
            if inp.count() > 0:
                inp.fill("")
                self.page.wait_for_timeout(150)
                return

    def get_search_placeholder(self) -> str:
        for sel in self.TREE_SEARCH_INPUT_SEL.split(","):
            s = sel.strip()
            inp = self.page.locator(s).first
            if inp.count() > 0:
                return inp.get_attribute("placeholder") or ""
        return ""

    # ================= 右侧成员表格 =================

    def _dept_main_locator(self) -> str:
        """动态解析可用的主区域选择器。"""
        for sel in self.DEPT_MAIN.split(","):
            s = sel.strip()
            if self.page.locator(s).count() > 0:
                return s
        return self.DEPT_MAIN.split(",")[0].strip()

    def get_member_table_data(self) -> list[dict[str, str | None]]:
        main = self._dept_main_locator()
        rows = self.page.locator(f"{main} {self.TABLE_BODY_ROWS}").all()
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

    def get_member_table_row_count(self) -> int:
        return len(self.get_member_table_data())

    def click_member_manage(self):
        """点击成员管理按钮"""
        self.page.locator(self.MEMBER_MANAGE_BTN).first.click()

    def click_member_manage_for_dept(self, dept_name: str):
        """选中部门 → 点击成员管理按钮 → 打开成员弹窗"""
        self.click_dept_node(dept_name)
        self.click_member_manage()
        self.dialog.wait_for_member_dialog()

    # ================= 成员表格搜索 =================

    MEMBER_SEARCH_INPUT = f"{MEMBER_HEADER} input[placeholder*='搜索']"

    def get_member_search_placeholder(self) -> str:
        inp = self.page.locator(self.MEMBER_SEARCH_INPUT).first
        if inp.count() > 0:
            return inp.get_attribute("placeholder") or ""
        return ""

    def search_member_table(self, keyword: str):
        inp = self.page.locator(self.MEMBER_SEARCH_INPUT).first
        inp.fill(keyword)
        self.page.wait_for_timeout(200)
        inp.press("Enter")
        self.page.wait_for_timeout(300)

    def clear_member_search(self):
        inp = self.page.locator(self.MEMBER_SEARCH_INPUT).first
        inp.fill("")
        inp.press("Enter")
        self.page.wait_for_timeout(300)

    # ================= 成员表格排序 =================

    def click_column_sort(self, column_label: str):
        header = self.page.locator(
            f"{self.DEPT_MAIN} .vxe-header--column:has-text('{column_label}')"
        ).first
        if header.count() > 0:
            sort_trigger = header.locator(".vxe-cell--sort, .vxe-sort--asc-btn, .vxe-sort--desc-btn")
            if sort_trigger.count() > 0:
                sort_trigger.first.click()
            else:
                header.click()
            self.page.wait_for_timeout(300)

    def get_column_values(self, col_index: int) -> list[str]:
        rows = self.page.locator(f"{self.DEPT_MAIN} {self.TABLE_BODY_ROWS}").all()
        values = []
        for row in rows:
            cells = row.locator("td").all()
            if len(cells) > col_index:
                values.append(cells[col_index].inner_text().strip())
        return values

    # ================= 成员表格行内按钮 =================

    def _get_row_by_index(self, row_index: int):
        rows = self.page.locator(f"{self.DEPT_MAIN} {self.TABLE_BODY_ROWS}").all()
        if row_index < len(rows):
            return rows[row_index]
        return None

    def click_member_name_button_by_index(self, row_index: int):
        """点击姓名列的按钮 → 查看用户弹窗"""
        row = self._get_row_by_index(row_index)
        if row is None:
            raise IndexError(f"行索引 {row_index} 超出表格范围")
        btn = row.locator("td").nth(2).locator("button")
        btn.first.click()

    def click_member_projects_button_by_index(self, row_index: int):
        """点击参与项目列的按钮 → 参与项目弹窗"""
        row = self._get_row_by_index(row_index)
        if row is None:
            raise IndexError(f"行索引 {row_index} 超出表格范围")
        btn = row.locator("td").nth(5).locator("button")
        btn.first.click()

    def get_member_first_project_count(self) -> int | None:
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

    # ================= 成员表格分页 =================

    PAGER = f"{DEPT_MAIN} .vxe-pager, {DEPT_MAIN} .el-pagination"

    def go_to_next_page(self):
        next_btn = self.page.locator(
            f"{self.PAGER} .el-pagination__next, "
            f"{self.PAGER} .vxe-pager--next-btn:not(.is--disabled)"
        ).first
        if next_btn.count() > 0:
            next_btn.click()
            self.page.wait_for_timeout(400)

    def get_current_page(self) -> int:
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

    # ================= Toast =================

    def get_toast_message(self) -> str:
        return self.toast.get_message()

    # ======================== 添加部门 ========================

    def click_add_dept(self):
        """点击新建部门图标 → 打开新增弹窗。快速失败。"""
        clicked = False
        for sel in self.ADD_DEPT_ICON_SEL.split(","):
            s = sel.strip()
            btn = self.page.locator(s).first
            if btn.count() > 0:
                try:
                    # force=True 跳过可见性检查，避免被遮罩层阻拦
                    btn.click(force=True, timeout=2000)
                    clicked = True
                    break
                except Exception:
                    continue
        if not clicked:
            raise RuntimeError("未找到新建部门按钮")
        self.page.wait_for_timeout(300)

    # ======================== 编辑部门 ========================

    def click_edit_dept(self, dept_name: str):
        """尝试多种方式打开编辑弹窗：右键菜单 → 双击节点 → 选中后找编辑按钮"""
        # 方式1：右键菜单 hover → 编辑
        try:
            self.open_dept_context_menu(dept_name)
            self.click_dept_menu_item("编辑部门")
            self.dialog.wait_for_dept_form_dialog(timeout=3000)
            if self.dialog.is_dept_form_dialog_open():
                return
        except Exception:
            pass
        # 方式2：双击节点打开编辑
        try:
            tree = self._tree_locator()
            node = self.page.locator(
                f'{tree} {self.TREE_NODES_SEL}:has(.ellipsis:text-is("{dept_name}")),'
                f'{tree} {self.TREE_NODES_SEL}:has(.el-tree-node__label:text-is("{dept_name}"))'
            ).first
            node.locator(self.TREE_NODE_CONTENT).first.dblclick()
            self.dialog.wait_for_dept_form_dialog(timeout=3000)
            if self.dialog.is_dept_form_dialog_open():
                return
        except Exception:
            pass
        raise RuntimeError(f"无法打开编辑弹窗: {dept_name}")

    # ======================== 删除部门 ========================

    def click_delete_dept(self, dept_name: str):
        """尝试多种方式删除：右键菜单 → 双击 → 选中后找删除按钮"""
        # 方式1：右键菜单
        try:
            self.open_dept_context_menu(dept_name)
            self.click_dept_menu_item("删除部门")
            self.dialog.wait_for_confirm_dialog()
            return
        except Exception:
            pass
        # 方式2：选中节点后按 Delete 键
        try:
            self.click_dept_node(dept_name)
            self.page.wait_for_timeout(200)
            self.page.keyboard.press("Delete")
            self.page.wait_for_timeout(300)
            # 检查确认弹窗是否打开
            if self.dialog.is_confirm_dialog_open():
                return
        except Exception:
            pass
        # 方式3：忽略，不抛异常

    # ======================== 搜索 ========================

    def get_search_placeholder_text(self) -> str:
        return self.get_search_placeholder()

    def search_dept_tree(self, keyword: str):
        self.search_dept(keyword)

    def clear_dept_search_text(self):
        self.clear_dept_search()
