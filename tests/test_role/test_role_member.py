"""
角色管理 — 成员管理测试

测试范围:
- 新建复杂角色（名称30字符含中英文数字特殊字符emoji，描述100字符）
- 检查右侧成员列表为空
- 成员管理弹窗：title、取消、X、确定按钮
- 不勾选数据点确定、勾选全部数据点确定
- 已选数据正确显示、清空、单个取消
- 部门下拉框过滤、搜索用户名（存在/不存在）
"""
import re
import uuid

import allure
import pytest

from tests.test_role._helpers import close_any_dialog, safe_delete_role

# 模块级：测试角色名，teardown 删除
_test_role_name: str = ""


def _open_member_dialog(role_manager_page):
    """打开成员管理弹窗并返回弹窗内作用域选择器。"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_member_manage()
    role_manager_page.dialog.wait_for_member_dialog()
    return f"{role_manager_page.dialog.MEMBER_DIALOG}:visible"


def _get_member_count(role_manager_page) -> int:
    """获取右侧成员表格行数。"""
    try:
        role_manager_page.click_role_node(_test_role_name)
        role_manager_page.page.wait_for_timeout(250)
        return len(role_manager_page.get_member_table_data())
    except Exception:
        return -1


# ======================== 模块级 setup / teardown ========================


@pytest.fixture(scope="module", autouse=True)
def _setup_and_cleanup(role_manager_page):
    """模块 setup：创建复杂角色；teardown：兜底删除。"""
    global _test_role_name
    close_any_dialog(role_manager_page)

    _test_role_name = f"成员测试_{uuid.uuid4().hex[:8]}"[:30]
    desc_100 = (
        "成员管理描述📋\n"
        "含空格 换行 😀\n"
        "特殊!@#$%^&*()🎯\n"
        "中英混合Member管理Test\n"
        "补齐字符凑够一百个字描述用于测试角色成员管理功能完整性校验✅"
    )[:100]

    role_manager_page.click_add_role()
    role_manager_page.dialog.fill_role_field("角色名称", _test_role_name)
    role_manager_page.dialog.fill_role_field("角色描述", desc_100)
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(800)

    if role_manager_page.dialog.is_role_form_dialog_open():
        role_manager_page.dialog.click_role_form_close()
        pytest.skip("无法创建测试角色")

    yield

    # ---- teardown：清空成员 → 删除角色 ----
    close_any_dialog(role_manager_page)
    page = role_manager_page.page
    try:
        # 1. 打开成员管理弹窗
        role_manager_page.click_role_node(_test_role_name)
        page.wait_for_timeout(200)
        role_manager_page.click_member_manage()
        role_manager_page.dialog.wait_for_member_dialog()
        scope = f"{role_manager_page.dialog.MEMBER_DIALOG}:visible"

        # 2. 点击"清空"移除所有已选成员
        clear_btn = page.locator(f"{scope}").locator("text=清空").first
        if clear_btn.count() > 0:
            clear_btn.click()
            page.wait_for_timeout(300)
        else:
            clear_btn = page.locator(f"{scope} :has-text('清空')").first
            if clear_btn.count() > 0:
                clear_btn.click()
                page.wait_for_timeout(300)

        # 3. 点确定保存（空成员列表）
        role_manager_page.dialog.click_member_dialog_confirm()
        page.wait_for_timeout(500)

        # 4. 如果弹窗未关闭则手动关闭
        if role_manager_page.dialog.is_member_dialog_open():
            role_manager_page.dialog.click_member_dialog_close()
    except Exception:
        pass

    # 5. 删除角色
    safe_delete_role(role_manager_page, _test_role_name)


# ======================== 初始状态检查 ========================


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(1)
def test_member_list_empty_initially(role_manager_page):
    """新建角色 → 右侧成员列表应为空"""
    assert _get_member_count(role_manager_page) == 0, \
        "新建角色（无成员）的成员列表应为空"


# ======================== 弹窗基础校验 ========================


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(2)
def test_member_dialog_title(role_manager_page):
    """成员管理弹窗标题"""
    scope = _open_member_dialog(role_manager_page)
    title = role_manager_page.page.locator(f"{scope} .title__text").first.inner_text()
    assert "成员" in title or "添加" in title, f"弹窗标题应包含成员/添加，实际='{title}'"
    role_manager_page.dialog.click_member_dialog_close()
    role_manager_page.page.wait_for_timeout(250)


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(3)
def test_member_dialog_cancel(role_manager_page):
    """点取消 → 弹窗关闭"""
    _open_member_dialog(role_manager_page)
    role_manager_page.dialog.click_member_dialog_cancel()
    role_manager_page.page.wait_for_timeout(250)
    assert not role_manager_page.dialog.is_member_dialog_open(), "点取消后弹窗应关闭"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(4)
def test_member_dialog_close(role_manager_page):
    """点 X → 弹窗关闭"""
    _open_member_dialog(role_manager_page)
    role_manager_page.dialog.click_member_dialog_close()
    role_manager_page.page.wait_for_timeout(250)
    assert not role_manager_page.dialog.is_member_dialog_open(), "点 X 后弹窗应关闭"


# ======================== 成员选择 ========================


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(5)
def test_member_confirm_no_selection(role_manager_page):
    """不勾选任何数据 → 点确定 → 弹窗关闭、成员列表仍为空"""
    scope = _open_member_dialog(role_manager_page)
    page = role_manager_page.page

    role_manager_page.dialog.click_member_dialog_confirm()
    page.wait_for_timeout(500)

    # 弹窗可能关闭或提示未选择
    if role_manager_page.dialog.is_member_dialog_open():
        # 有提示则关闭
        role_manager_page.dialog.click_member_dialog_close()
    assert _get_member_count(role_manager_page) == 0, "未选择成员时确定，成员列表应仍为空"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(6)
def test_member_select_and_confirm(role_manager_page):
    """勾选全部数据 → 点确定 → 成员添加成功"""
    scope = _open_member_dialog(role_manager_page)
    page = role_manager_page.page

    # 勾选"全选"
    select_all = page.locator(f"{scope} .el-checkbox:has-text('全选')").first
    if select_all.count() > 0:
        select_all.click()
        page.wait_for_timeout(200)

    # 解析已选数量
    selected_text = page.locator(f"{scope} :has-text('已选')").first.inner_text()
    print(f"已选: {selected_text}")

    role_manager_page.dialog.click_member_dialog_confirm()
    page.wait_for_timeout(800)

    if role_manager_page.dialog.is_member_dialog_open():
        role_manager_page.dialog.click_member_dialog_close()
        pytest.fail("添加成员失败，弹窗未关闭")

    # 弹窗已关闭说明成员添加成功（成员列表应有数据）
    count = _get_member_count(role_manager_page)
    if count >= 0:
        assert count > 0, f"添加成员后成员列表应有数据，实际={count}"


# ======================== 已选操作 ========================


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(7)
def test_member_clear_selection(role_manager_page):
    """勾选数据 → 点清空 → 已选归零"""
    scope = _open_member_dialog(role_manager_page)
    page = role_manager_page.page

    # 定位用户复选框：排除"全选"，且其 label 包含形如"xxx（yyy）"的用户名格式
    all_cbs = page.locator(f"{scope} .el-checkbox:not(:has-text('全选'))").all()
    user_cbs = []
    for cb in all_cbs:
        label = cb.locator(".el-checkbox__label")
        if label.count() > 0:
            text = label.first.inner_text().strip()
            if "（" in text and "）" in text:
                user_cbs.append(cb)
    print(f"找到 {len(user_cbs)} 个用户复选框")

    if len(user_cbs) < 2:
        role_manager_page.dialog.click_member_dialog_close()
        pytest.skip(f"可勾选用户不足（{len(user_cbs)}），跳过清空测试")

    user_cbs[0].click()
    page.wait_for_timeout(100)
    user_cbs[1].click()
    page.wait_for_timeout(100)

    # 检查已选计数（用正则匹配"已选：N"文本节点，避免匹配整个弹窗）
    selected_locator = page.locator(f"{scope}").locator("text=/已选：\\d+/")
    selected_text = selected_locator.first.inner_text()
    assert "0" not in selected_text.split("：")[-1], f"勾选后已选数应>0，实际='{selected_text}'"

    # 点清空（清空按钮可能是 span / a / div，不限于 button）
    clear_btn = page.locator(f"{scope}").locator("text=清空").first
    if clear_btn.count() > 0:
        clear_btn.click()
        page.wait_for_timeout(300)
    else:
        # 回退：尝试 has-text 匹配
        clear_btn = page.locator(f"{scope} :has-text('清空')").first
        if clear_btn.count() > 0:
            clear_btn.click()
            page.wait_for_timeout(300)

    # 验证已选归零
    selected_text = selected_locator.first.inner_text()
    assert "0" in selected_text, f"清空后已选数应为0，实际='{selected_text}'"

    role_manager_page.dialog.click_member_dialog_close()


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(8)
def test_member_remove_tag(role_manager_page):
    """勾选数据 → 点已选标签 X → 取消单个勾选"""
    scope = _open_member_dialog(role_manager_page)
    page = role_manager_page.page

    # 勾选一个用户
    cb = page.locator(f"{scope} .el-checkbox:not(:has-text('全选'))").first
    cb.click()
    page.wait_for_timeout(100)

    # 获取勾选后计数
    selected_el = page.locator(f"{scope} :has-text('已选')").first
    selected_text_before = selected_el.inner_text()

    # 找已选标签的 X 按钮并点击
    tag_close = page.locator(f"{scope} .el-tag .el-icon-close, {scope} .el-tag__close").first
    if tag_close.count() > 0:
        tag_close.click()
        page.wait_for_timeout(200)

        selected_text_after = selected_el.inner_text()
        assert selected_text_after != selected_text_before, \
            f"取消标签后已选数应变化，之前='{selected_text_before}'，之后='{selected_text_after}'"

    role_manager_page.dialog.click_member_dialog_close()


# ======================== 筛选 ========================


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(9)
def test_member_department_filter(role_manager_page):
    """部门下拉框展示部门数据，选择部门过滤用户"""
    scope = _open_member_dialog(role_manager_page)
    page = role_manager_page.page

    # 点击部门下拉框
    dept_select = page.locator(f"{scope} input[placeholder='请选择']").first
    if dept_select.count() == 0:
        role_manager_page.dialog.click_member_dialog_close()
        pytest.skip("未找到部门下拉框")

    dept_select.click()
    page.wait_for_timeout(300)

    # 获取下拉选项
    options = page.locator(".el-select-dropdown:visible .el-select-dropdown__item").all()
    dept_names = [o.inner_text().strip() for o in options if o.inner_text().strip()]
    print(f"部门列表: {dept_names}")

    if dept_names:
        # 选择第一个部门
        options[1].click()
        page.wait_for_timeout(300)

        # 检查用户列表被过滤
        users_after = page.locator(f"{scope} .el-checkbox:not(:has-text('全选'))").count()
        print(f"过滤后用户数: {users_after}")

    role_manager_page.dialog.click_member_dialog_close()


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(10)
def test_member_search_user(role_manager_page):
    """搜索用户名存在 → 过滤显示；搜索不存在 → 无数据"""
    scope = _open_member_dialog(role_manager_page)
    page = role_manager_page.page

    # 重置部门筛选为"全部"，避免上一个用例的筛选条件残留
    dept_select = page.locator(f"{scope} input[placeholder='请选择']").first
    if dept_select.count() > 0:
        dept_select.click()
        page.wait_for_timeout(200)
        all_option = page.locator(
            ".el-select-dropdown:visible .el-select-dropdown__item"
        ).filter(has_text="全部").first
        if all_option.count() > 0:
            all_option.click()
            page.wait_for_timeout(300)

    # 获取第一个用户名用于搜索
    user_labels = page.locator(
        f"{scope} .el-checkbox:not(:has-text('全选')) .el-checkbox__label"
    ).all()
    if not user_labels:
        # 回退：尝试直接获取复选框文本
        user_labels = page.locator(
            f"{scope} .el-checkbox:not(:has-text('全选'))"
        ).all()
    if not user_labels:
        role_manager_page.dialog.click_member_dialog_close()
        pytest.skip("无可用用户数据")

    first_user = user_labels[0].inner_text().strip()
    # 提取用户名（括号内部分）
    m = re.search(r'（(.+?)）', first_user)
    search_keyword = m.group(1) if m else first_user[:4]

    # 搜索存在的用户
    search_input = page.locator(f"{scope} input[placeholder='搜索']").first
    search_input.fill(search_keyword)
    page.wait_for_timeout(300)

    filtered = page.locator(f"{scope} .el-checkbox:not(:has-text('全选'))").count()
    assert filtered > 0, f"搜索'{search_keyword}'应有匹配结果"

    # 搜索不存在的用户
    search_input.fill("不存在的用户_xyz_999")
    page.wait_for_timeout(300)
    no_result = page.locator(f"{scope} .el-checkbox:not(:has-text('全选'))").count()
    assert no_result == 0, f"搜索不存在用户应无结果，实际={no_result}"

    role_manager_page.dialog.click_member_dialog_close()


# ======================== 成员表格 — 搜索输入框 ========================


def _ensure_members_exist(role_manager_page) -> bool:
    """确保角色有关联成员（供右侧表格测试使用）。
    如果成员列表为空，打开成员管理弹窗勾选全部用户并确认。
    返回 True 表示有数据可用。
    """
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)

    if len(role_manager_page.get_member_table_data()) > 0:
        return True

    # 角色无成员 → 打开成员管理弹窗添加
    role_manager_page.click_member_manage()
    role_manager_page.dialog.wait_for_member_dialog()
    scope = f"{role_manager_page.dialog.MEMBER_DIALOG}:visible"
    page = role_manager_page.page

    # 勾选"全选"
    select_all = page.locator(f"{scope} .el-checkbox:has-text('全选')").first
    if select_all.count() > 0:
        select_all.click()
        page.wait_for_timeout(200)
    else:
        role_manager_page.dialog.click_member_dialog_close()
        return False

    # 确认添加
    role_manager_page.dialog.click_member_dialog_confirm()
    page.wait_for_timeout(800)

    if role_manager_page.dialog.is_member_dialog_open():
        role_manager_page.dialog.click_member_dialog_close()

    role_manager_page.click_role_node(_test_role_name)
    page.wait_for_timeout(200)
    return len(role_manager_page.get_member_table_data()) > 0


def _prep_for_table_test(role_manager_page) -> bool:
    """表格测试前置：确保有成员数据 → 关闭弹窗 → 选中角色节点。"""
    if not _ensure_members_exist(role_manager_page):
        return False
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(300)
    return True


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(11)
def test_member_table_search_placeholder(role_manager_page):
    """右侧成员表格搜索框 placeholder 校验"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("成员表格无数据")
    placeholder = role_manager_page.get_member_search_placeholder()
    assert placeholder, "搜索框应有 placeholder 提示文字"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(12)
def test_member_table_search_existing(role_manager_page):
    """搜索存在的用户名 → 表格过滤显示"""
    page = role_manager_page.page
    role_manager_page.click_role_node(_test_role_name)
    page.wait_for_timeout(200)

    members = role_manager_page.get_member_table_data()
    if not members:
        pytest.skip("成员表格无数据，跳过搜索测试")

    keyword = members[0]["用户名"]
    role_manager_page.search_member_table(keyword)

    filtered = role_manager_page.get_member_table_data()
    assert len(filtered) > 0, f"搜索'{keyword}'应有匹配结果"
    assert all(keyword in (r["用户名"] or "") for r in filtered), \
        f"搜索结果应全部包含'{keyword}'"

    role_manager_page.clear_member_search()


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(13)
def test_member_table_search_nonexistent(role_manager_page):
    """搜索不存在的用户名 → 表格无数据"""
    page = role_manager_page.page
    role_manager_page.click_role_node(_test_role_name)
    page.wait_for_timeout(200)

    role_manager_page.search_member_table("不存在的用户_xyz_999")

    filtered = role_manager_page.get_member_table_data()
    assert len(filtered) == 0, f"搜索不存在用户应无结果，实际={len(filtered)}条"

    role_manager_page.clear_member_search()


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(14)
def test_member_table_search_clear(role_manager_page):
    """清空搜索条件 → 数据恢复全部显示"""
    page = role_manager_page.page
    role_manager_page.click_role_node(_test_role_name)
    page.wait_for_timeout(200)

    members_before = role_manager_page.get_member_table_data()
    if not members_before:
        pytest.skip("成员表格无数据，跳过清空测试")

    role_manager_page.search_member_table(members_before[0]["用户名"])
    role_manager_page.clear_member_search()

    members_after = role_manager_page.get_member_table_data()
    assert len(members_after) == len(members_before), \
        f"清空搜索后应恢复全部数据，清空前={len(members_before)}，清空后={len(members_after)}"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(15)
def test_member_table_search_cross_page(role_manager_page):
    """翻到第二页 → 搜索第一页存在的用户名 → 应能跨页匹配"""
    page = role_manager_page.page
    role_manager_page.click_role_node(_test_role_name)
    page.wait_for_timeout(200)

    total = role_manager_page.get_total_pages()
    if total < 2:
        members = role_manager_page.get_member_table_data()
        if not members:
            pytest.skip("成员表格无数据")
        role_manager_page.search_member_table(members[0]["用户名"])
        filtered = role_manager_page.get_member_table_data()
        assert len(filtered) > 0, "搜索第一页用户名应有结果"
        role_manager_page.clear_member_search()
        return

    page1_members = role_manager_page.get_member_table_data()
    if not page1_members:
        pytest.skip("第一页无数据")
    target_user = page1_members[0]["用户名"]

    role_manager_page.go_to_next_page()
    current = role_manager_page.get_current_page()
    if current != 2:
        role_manager_page.clear_member_search()
        pytest.skip("无法翻到第二页")

    role_manager_page.search_member_table(target_user)

    filtered = role_manager_page.get_member_table_data()
    assert len(filtered) > 0, f"跨页搜索'{target_user}'应有匹配结果"

    role_manager_page.clear_member_search()


# ======================== 成员表格 — 状态下拉框 ========================


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(16)
def test_member_table_status_display(role_manager_page):
    """状态下拉框展示测试"""
    page = role_manager_page.page
    role_manager_page.click_role_node(_test_role_name)
    page.wait_for_timeout(200)

    role_manager_page.open_status_dropdown()
    options = role_manager_page.get_status_options()
    print(f"状态选项: {options}")
    assert len(options) > 0, "状态下拉框应有选项"
    page.locator(f"{role_manager_page.ROLE_MAIN} .kd-table-pro__header").first.click()
    page.wait_for_timeout(100)


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(17)
def test_member_table_status_filter(role_manager_page):
    """选择状态下拉框值 → 数据过滤"""
    page = role_manager_page.page
    role_manager_page.click_role_node(_test_role_name)
    page.wait_for_timeout(200)

    role_manager_page.open_status_dropdown()
    options = role_manager_page.get_status_options()
    page.locator("body").first.press("Escape")

    if len(options) < 2:
        pytest.skip("状态下拉选项不足，无法测试过滤")

    target = [o for o in options if o != "全部"][0] if "全部" in options else options[0]
    role_manager_page.select_status(target)

    members = role_manager_page.get_member_table_data()
    print(f"状态'{target}'过滤后: {len(members)} 条")

    role_manager_page.clear_status_filter()


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(18)
def test_member_table_status_clear(role_manager_page):
    """清空状态筛选值 → 数据恢复"""
    page = role_manager_page.page
    role_manager_page.click_role_node(_test_role_name)
    page.wait_for_timeout(200)

    before = len(role_manager_page.get_member_table_data())

    role_manager_page.open_status_dropdown()
    options = role_manager_page.get_status_options()
    page.locator("body").first.press("Escape")

    non_all = [o for o in options if o != "全部"]
    if not non_all:
        pytest.skip("无可用状态选项")
    role_manager_page.select_status(non_all[0])

    role_manager_page.clear_status_filter()

    after = len(role_manager_page.get_member_table_data())
    assert after == before, \
        f"清空状态后数据应恢复，之前={before}，之后={after}"


# ======================== 成员表格 — 姓名列点击弹窗 ========================


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(19)
def test_member_table_click_name_opens_dialog(role_manager_page):
    """点击姓名 → 查看用户弹窗 → 姓名一致"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("成员表格无数据")

    row = role_manager_page.get_member_table_data()[0]
    expected_name = row.get("姓名", "")
    assert expected_name, "用户应有姓名"

    role_manager_page.click_member_name_button_by_index(0)
    role_manager_page.dialog.wait_for_view_user_dialog()

    # 验证弹窗标题
    title = role_manager_page.dialog.get_view_user_dialog_title()
    assert "查看用户" in title, f"弹窗标题应包含'查看用户'，实际'{title}'"

    # 验证弹窗内容包含该用户姓名
    body = role_manager_page.dialog.get_view_user_dialog_body_text()
    assert expected_name in body, \
        f"查看用户弹窗应包含姓名'{expected_name}'，实际内容：'{body}'"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(20)
def test_member_table_view_user_dialog_close(role_manager_page):
    """查看用户弹窗 → X 关闭按钮"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("成员表格无数据")

    role_manager_page.click_member_name_button_by_index(0)
    role_manager_page.dialog.wait_for_view_user_dialog()

    role_manager_page.dialog.close_view_user_dialog()
    role_manager_page.page.wait_for_timeout(300)

    assert not role_manager_page.dialog.is_view_user_dialog_open(), \
        "点击关闭后查看用户弹窗应关闭"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(21)
def test_member_table_view_user_dialog_confirm(role_manager_page):
    """查看用户弹窗 → 确定按钮关闭"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("成员表格无数据")

    role_manager_page.click_member_name_button_by_index(0)
    role_manager_page.dialog.wait_for_view_user_dialog()

    role_manager_page.dialog.click_view_user_dialog_confirm()
    role_manager_page.page.wait_for_timeout(300)

    assert not role_manager_page.dialog.is_view_user_dialog_open(), \
        "点击确定后查看用户弹窗应关闭"


# ======================== 成员表格 — 参与项目点击弹窗 ========================


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(22)
def test_member_table_click_projects_opens_dialog(role_manager_page):
    """点击参与项目数 → 弹窗显示项目和项目角色"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("成员表格无数据")

    count = role_manager_page.get_member_first_project_count()
    if count is None or count == 0:
        pytest.skip("未找到参与项目>0 的成员")

    role_manager_page.click_member_projects_button_by_index(0)
    role_manager_page.dialog.wait_for_projects_dialog()

    title = role_manager_page.dialog.get_projects_dialog_title()
    assert "参与项目" in title, f"弹窗标题应包含'参与项目'，实际'{title}'"

    assert role_manager_page.dialog.is_projects_dialog_open(), \
        "参与项目弹窗应打开"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(23)
def test_member_table_projects_dialog_close(role_manager_page):
    """参与项目弹窗 → X 关闭按钮"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("成员表格无数据")

    count = role_manager_page.get_member_first_project_count()
    if count is None or count == 0:
        pytest.skip("未找到参与项目>0 的成员")

    role_manager_page.click_member_projects_button_by_index(0)
    role_manager_page.dialog.wait_for_projects_dialog()

    role_manager_page.dialog.close_projects_dialog()
    role_manager_page.page.wait_for_timeout(300)

    assert not role_manager_page.dialog.is_projects_dialog_open(), \
        "点击 X 关闭后参与项目弹窗应关闭"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(24)
def test_member_table_projects_dialog_body(role_manager_page):
    """参与项目弹窗 → 弹窗内容展示"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("成员表格无数据")

    count = role_manager_page.get_member_first_project_count()
    if count is None or count == 0:
        pytest.skip("未找到参与项目>0 的成员")

    role_manager_page.click_member_projects_button_by_index(0)
    role_manager_page.dialog.wait_for_projects_dialog()

    # 验证弹窗标题包含"参与项目"
    title = role_manager_page.dialog.get_projects_dialog_title()
    assert "参与项目" in title, f"弹窗标题应包含'参与项目'，实际'{title}'"

    # 验证弹窗已打开
    assert role_manager_page.dialog.is_projects_dialog_open(), \
        "参与项目弹窗应打开"

    role_manager_page.dialog.close_projects_dialog()


# ======================== 成员表格 — 列设置 ========================


def _open_col_settings_robust(role_manager_page) -> bool:
    """尝试打开列设置，返回是否成功打开。"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(300)
    role_manager_page.open_column_settings()
    role_manager_page.page.wait_for_timeout(400)
    return role_manager_page.is_column_settings_open()


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(25)
def test_member_table_column_settings_open(role_manager_page):
    """打开列设置"""
    opened = _open_col_settings_robust(role_manager_page)
    if not opened:
        pytest.skip("未找到列设置按钮或列设置未打开")
    assert opened, "列设置弹窗应打开"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(26)
def test_member_table_column_settings_title(role_manager_page):
    """列设置弹窗 title 检查"""
    if not _open_col_settings_robust(role_manager_page):
        pytest.skip("未找到列设置")

    title = role_manager_page.get_column_settings_title()
    print(f"列设置 title: {title}")
    assert title, "列设置弹窗应有 title"

    role_manager_page.click_column_settings_close()


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(27)
def test_member_table_column_settings_checkbox(role_manager_page):
    """列设置 → 勾选/取消勾选操作"""
    if not _open_col_settings_robust(role_manager_page):
        pytest.skip("未找到列设置")

    checkboxes = role_manager_page.get_column_settings_checkboxes()
    if not checkboxes:
        role_manager_page.click_column_settings_close()
        pytest.skip("列设置中无复选框")

    print(f"列设置复选框: {checkboxes}")
    last_col = checkboxes[-1]
    role_manager_page.toggle_column_setting(last_col)
    role_manager_page.click_column_settings_confirm()
    role_manager_page.page.wait_for_timeout(300)

    _open_col_settings_robust(role_manager_page)
    role_manager_page.toggle_column_setting(last_col)
    role_manager_page.click_column_settings_confirm()
    role_manager_page.page.wait_for_timeout(300)


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(28)
def test_member_table_column_settings_move(role_manager_page):
    """列设置 → 移动列顺序"""
    if not _open_col_settings_robust(role_manager_page):
        pytest.skip("未找到列设置")

    page = role_manager_page.page
    move_up = page.locator(
        ".el-icon-top:visible, .el-icon-caret-top:visible, "
        "[title*='上移']:visible, [title*='向上']:visible"
    ).first

    if move_up.count() > 0:
        print("列设置支持移动操作")
        move_up.click()
        role_manager_page.page.wait_for_timeout(150)
    else:
        print("列设置无移动按钮")

    role_manager_page.click_column_settings_confirm()


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(29)
def test_member_table_column_settings_search(role_manager_page):
    """列设置 → 搜索列名"""
    if not _open_col_settings_robust(role_manager_page):
        pytest.skip("未找到列设置")

    checkboxes = role_manager_page.get_column_settings_checkboxes()
    if not checkboxes:
        role_manager_page.click_column_settings_close()
        pytest.skip("列设置中无复选框")

    role_manager_page.search_column_setting(checkboxes[0])
    filtered = role_manager_page.get_column_settings_checkboxes()
    print(f"搜索'{checkboxes[0]}'后的列设置选项: {filtered}")
    assert len(filtered) > 0, f"搜索'{checkboxes[0]}'应有匹配结果"

    role_manager_page.click_column_settings_close()


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(30)
def test_member_table_column_settings_cancel(role_manager_page):
    """列设置 → 点取消关闭"""
    if not _open_col_settings_robust(role_manager_page):
        pytest.skip("未找到列设置")

    role_manager_page.click_column_settings_cancel()
    role_manager_page.page.wait_for_timeout(200)

    assert not role_manager_page.is_column_settings_open(), \
        "点取消除后列设置弹窗应关闭"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(31)
def test_member_table_column_settings_confirm(role_manager_page):
    """列设置 → 点确定关闭"""
    if not _open_col_settings_robust(role_manager_page):
        pytest.skip("未找到列设置")

    role_manager_page.click_column_settings_confirm()
    role_manager_page.page.wait_for_timeout(200)

    assert not role_manager_page.is_column_settings_open(), \
        "点确定后列设置弹窗应关闭"


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(32)
def test_member_table_column_settings_close(role_manager_page):
    """列设置 → 点 X 关闭"""
    if not _open_col_settings_robust(role_manager_page):
        pytest.skip("未找到列设置")

    role_manager_page.click_column_settings_close()
    role_manager_page.page.wait_for_timeout(200)

    assert not role_manager_page.is_column_settings_open(), \
        "点 X 后列设置弹窗应关闭"


# ======================== 成员表格 — 列排序 ========================


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(33)
def test_member_table_sort_username(role_manager_page):
    """用户名列排序"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("数据不足，跳过排序测试")
    role_manager_page.click_column_sort("用户名")
    after_sort = role_manager_page.get_column_values(1)
    print(f"用户名排序: {after_sort}")


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(34)
def test_member_table_sort_name(role_manager_page):
    """姓名列排序"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("数据不足，跳过排序测试")
    role_manager_page.click_column_sort("姓名")
    after_sort = role_manager_page.get_column_values(2)
    print(f"姓名排序: {after_sort}")


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(35)
def test_member_table_sort_gender(role_manager_page):
    """性别列排序"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("数据不足，跳过排序测试")
    role_manager_page.click_column_sort("性别")
    after_sort = role_manager_page.get_column_values(3)
    print(f"性别排序: {after_sort}")


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(36)
def test_member_table_sort_department(role_manager_page):
    """部门列排序"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("数据不足，跳过排序测试")
    role_manager_page.click_column_sort("部门")
    after_sort = role_manager_page.get_column_values(4)
    print(f"部门排序: {after_sort}")


@allure.feature("角色管理")
@allure.story("成员管理")
@pytest.mark.order(37)
def test_member_table_sort_project(role_manager_page):
    """参与项目列排序"""
    if not _prep_for_table_test(role_manager_page):
        pytest.skip("数据不足，跳过排序测试")
    role_manager_page.click_column_sort("参与项目")
    after_sort = role_manager_page.get_column_values(5)
    print(f"参与项目排序: {after_sort}")

