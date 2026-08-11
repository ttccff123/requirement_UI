"""test_role 共享工具函数。"""


def close_any_dialog(role_manager_page):
    """关闭页面上所有可见弹窗 + 清除残留遮罩层。无弹窗时快速返回。"""
    try:
        page = role_manager_page.page
        # 先检查是否有弹窗，没有就直接跳过
        dialogs = page.locator(
            "body>.el-dialog__wrapper.kd-dialog:visible,"
            ".el-message-box__wrapper:visible"
        )
        modal_count = page.locator(".v-modal").count()
        if dialogs.count() == 0 and modal_count == 0:
            return
        # 有弹窗：先尝试 Escape 关闭
        for _ in range(2):
            page.keyboard.press("Escape")
            page.wait_for_timeout(100)
        # 逐一关闭残留弹窗
        for i in range(dialogs.count()):
            d = dialogs.nth(i)
            if not d.is_visible():
                continue
            cls_btn = d.locator(".el-dialog__close, .el-message-box__headerbtn").first
            if cls_btn.count() > 0 and cls_btn.is_visible():
                cls_btn.click()
            else:
                page.keyboard.press("Escape")
            page.wait_for_timeout(100)
        # 清除残留遮罩
        if page.locator(".v-modal").count() > 0:
            try:
                page.locator(".v-modal").first.evaluate("el => el.remove()")
            except Exception:
                pass
    except Exception:
        pass


def safe_delete_role(role_manager_page, name: str):
    """安全删除角色（忽略异常）。"""
    try:
        close_any_dialog(role_manager_page)
        role_manager_page.click_delete_role(name)
        role_manager_page.dialog.wait_for_confirm_dialog()
        role_manager_page.dialog.click_confirm_dialog_confirm()
        role_manager_page.page.wait_for_timeout(250)
    except Exception:
        pass
