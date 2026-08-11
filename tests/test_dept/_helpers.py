"""test_dept 共享工具函数。"""


def close_any_dialog(dept_manager_page):
    """关闭页面上所有可见弹窗（Escape 优先，残留遮罩兜底移除）。"""
    try:
        page = dept_manager_page.page
        # 一次查询：无弹窗且无遮罩 → 直接跳过
        if page.locator(".v-modal, .el-dialog__wrapper:visible, [role=dialog]:visible").count() == 0:
            return
        # 有弹窗 → 按 Escape 关闭
        for _ in range(2):
            page.keyboard.press("Escape")
            page.wait_for_timeout(80)
        # 兜底：残留遮罩层直接移除（避免遮挡按钮导致后续 click 失败）
        if page.locator(".v-modal").count() > 0:
            try:
                page.locator(".v-modal").first.evaluate("el => el.remove()")
            except Exception:
                pass
    except Exception:
        pass


def open_add_dialog(dept_manager_page):
    """打开新增部门弹窗，先关闭已有弹窗。"""
    close_any_dialog(dept_manager_page)
    dept_manager_page.click_add_dept()


def open_edit_dialog(dept_manager_page, dept_name: str):
    """关闭弹窗 → 打开指定部门的编辑弹窗。"""
    close_any_dialog(dept_manager_page)
    dept_manager_page.click_edit_dept(dept_name)


def find_dept_with_members(dept_manager_page) -> str | None:
    """遍历部门树，返回第一个有成员的部门名；无则返回 None。"""
    names = dept_manager_page.get_dept_tree_node_names()
    for name in names:
        try:
            dept_manager_page.click_dept_node(name)
            dept_manager_page.page.wait_for_timeout(250)
            members = dept_manager_page.get_member_table_data()
            if members:
                return name
        except Exception:
            continue
    return None


def safe_add_dept(dept_manager_page, name: str, desc: str = "") -> bool:
    """安全创建部门：尝试填充所有可用字段。返回 True 表示创建成功。"""
    close_any_dialog(dept_manager_page)
    try:
        dept_manager_page.click_add_dept()
    except Exception:
        return False
    if not dept_manager_page.dialog.is_dept_form_dialog_open():
        return False
    # 填充名称
    dept_manager_page.dialog.fill_dept_field("部门名称", name)
    # 尝试填充可能的额外字段
    for field in ["上级部门", "父部门", "部门编码", "部门代码", "部门类型", "排序", "负责人"]:
        try:
            dept_manager_page.dialog.fill_dept_field(field, name if field == "部门编码" else "1")
        except Exception:
            pass
    if desc:
        dept_manager_page.dialog.fill_dept_field("部门描述", desc)
    dept_manager_page.dialog.click_dept_form_confirm()
    dept_manager_page.page.wait_for_timeout(300)
    dept_manager_page.dialog.wait_for_form_dialog_closed(timeout=2000)
    if dept_manager_page.dialog.is_dept_form_dialog_open():
        dept_manager_page.dialog.click_dept_form_close()
        return False
    return True


def safe_delete_dept(dept_manager_page, name: str):
    """安全删除部门（忽略异常）。"""
    try:
        close_any_dialog(dept_manager_page)
        dept_manager_page.click_delete_dept(name)
        dept_manager_page.dialog.wait_for_confirm_dialog()
        dept_manager_page.dialog.click_confirm_dialog_confirm()
        dept_manager_page.page.wait_for_timeout(250)
    except Exception:
        pass


def open_member_dialog(dept_manager_page, dept_name: str) -> str | None:
    """打开成员管理弹窗并返回弹窗内作用域选择器。失败返回 None。"""
    close_any_dialog(dept_manager_page)
    dept_manager_page.click_dept_node(dept_name)
    dept_manager_page.page.wait_for_timeout(200)
    dept_manager_page.click_member_manage()
    try:
        dept_manager_page.dialog.wait_for_member_dialog(timeout=5000)
        return f"{dept_manager_page.dialog.MEMBER_DIALOG}:visible"
    except Exception:
        return None
