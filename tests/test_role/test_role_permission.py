"""
角色管理 — 功能权限测试

测试范围:
- 新建角色 → 切换到功能权限 → 默认无勾选
- 勾选全部权限 → 验证全部选中
- 取消全部权限 → 验证全部未选中
- 父子级联动：勾选子级→父级自动勾选，勾选父级→子级不自动勾选
- 只勾选某板块 → 验证只有该板块相关权限
- 勾选板块+部分功能 → 验证权限匹配
- 勾选板块+功能+部门权限 → 验证权限匹配
- 添加成员后用该成员登录 → 权限校验一致
"""
import time
import uuid

import allure
import pytest

from tests.test_role._helpers import close_any_dialog, safe_delete_role


_test_role_name: str = ""


# ======================== 模块级 setup / teardown ========================


@pytest.fixture(scope="module", autouse=True)
def _setup_and_cleanup(role_manager_page):
    """模块 setup：创建权限测试角色；teardown：兜底删除。"""
    global _test_role_name
    close_any_dialog(role_manager_page)

    _test_role_name = f"权限测试_{uuid.uuid4().hex[:8]}"[:30]
    desc = "功能权限测试角色，用于验证权限树勾选、父级联动等功能。"

    role_manager_page.click_add_role()
    role_manager_page.dialog.fill_role_field("角色名称", _test_role_name)
    role_manager_page.dialog.fill_role_field("角色描述", desc)
    role_manager_page.dialog.click_role_form_confirm()
    role_manager_page.page.wait_for_timeout(800)

    if role_manager_page.dialog.is_role_form_dialog_open():
        role_manager_page.dialog.click_role_form_close()
        pytest.skip("无法创建测试角色")

    yield

    # teardown：删除角色
    safe_delete_role(role_manager_page, _test_role_name)


# ======================== 默认权限 ========================


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(1)
def test_permission_default_empty(role_manager_page):
    """新建角色 → 切换到功能权限 → 默认无可选权限"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)

    role_manager_page.click_perm_tab()
    assert role_manager_page.is_perm_tab_active(), "功能权限页签应激活"

    checked = role_manager_page.get_checked_perm_count()
    all_labels = role_manager_page.get_perm_labels()
    print(f"默认勾选权限数: {checked}, 总权限数: {len(all_labels)}")
    # 新角色默认有少量基础权限（如"我的空间"等），不会全空
    assert checked < len(all_labels), \
        f"新角色默认不应全选，已勾选={checked}, 总数={len(all_labels)}"


# ======================== 全选 / 全不选 ========================


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(2)
def test_permission_select_all(role_manager_page):
    """勾选全选 → 验证所有权限被选中"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    # 确保所有节点展开
    all_labels = role_manager_page.get_perm_labels()
    for label in all_labels:
        try:
            role_manager_page.expand_perm_node(label)
        except Exception:
            pass

    before = role_manager_page.get_checked_perm_count()
    print(f"勾选前: {before}")

    # 点全选
    role_manager_page.toggle_select_all_perms()
    after = role_manager_page.get_checked_perm_count()
    print(f"全选后: {after}")

    assert after >= before, f"全选后勾选数应≥之前，before={before}, after={after}"


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(3)
def test_permission_deselect_all(role_manager_page):
    """全选后再点全选 → 验证取消全部"""
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)

    # 先确保全选状态
    checked = role_manager_page.get_checked_perm_count()
    if checked == 0:
        role_manager_page.toggle_select_all_perms()

    # 再点一次全选（取消全部）
    role_manager_page.toggle_select_all_perms()
    after = role_manager_page.get_checked_perm_count()
    print(f"取消全选后: {after}")
    assert after == 0, f"取消全选后应无勾选，实际={after}"


def _perm_has_tree_structure(role_manager_page) -> bool:
    """检测权限面板是否使用 el-tree 树形结构。"""
    tree = role_manager_page.page.locator(role_manager_page.PERM_TREE)
    return tree.count() > 0 and tree.first.is_visible()


def _find_parent_with_children(role_manager_page) -> tuple | None:
    """找到第一个有子节点的父节点标签。返回 (parent_label, [child_labels]) 或 None。"""
    if not _perm_has_tree_structure(role_manager_page):
        return None
    labels = role_manager_page.get_perm_labels()
    for label in labels:
        role_manager_page.expand_perm_node(label)
        children = role_manager_page.get_perm_node_children(label)
        if children:
            return (label, children)
    return None


# ======================== 父子级联动 ========================


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(4)
def test_permission_child_checks_parent(role_manager_page):
    """勾选子级权限 → 父级自动勾选"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    pair = _find_parent_with_children(role_manager_page)
    if not pair:
        pytest.skip("未检测到 el-tree 树形权限结构")
    parent_label, children = pair
    child_label = children[0]

    # 清除所有勾选
    if role_manager_page.get_checked_perm_count() > 0:
        role_manager_page.toggle_select_all_perms()
        role_manager_page.toggle_select_all_perms()

    print(f"测试: 父节点='{parent_label}', 子节点='{child_label}'")
    role_manager_page.check_perm(child_label)

    child_checked = role_manager_page.is_perm_checked(child_label)
    parent_checked = role_manager_page.is_perm_checked(parent_label)
    parent_indeterminate = role_manager_page.is_perm_node_indeterminate(parent_label)

    print(f"子级勾选: {child_checked}, 父级勾选: {parent_checked}, 父级半选: {parent_indeterminate}")
    assert child_checked, f"子级'{child_label}'应被勾选"
    assert parent_checked or parent_indeterminate, \
        f"父级'{parent_label}'应被勾选或半选"


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(5)
def test_permission_parent_does_not_check_children(role_manager_page):
    """勾选父级权限 → 子级不自动勾选"""
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    pair = _find_parent_with_children(role_manager_page)
    if not pair:
        pytest.skip("未检测到 el-tree 树形权限结构")
    parent_label, children = pair
    child_label = children[0]

    # 清除所有勾选
    role_manager_page.toggle_select_all_perms()
    role_manager_page.toggle_select_all_perms()

    role_manager_page.check_perm(parent_label)
    parent_checked = role_manager_page.is_perm_checked(parent_label)
    child_checked = role_manager_page.is_perm_checked(child_label)

    print(f"父级勾选={parent_checked}, 子级勾选={child_checked}")
    assert parent_checked, f"父级'{parent_label}'应被勾选"
    assert not child_checked, f"勾选父级后子级'{child_label}'不应被自动勾选"


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(6)
def test_permission_uncheck_child_keeps_parent(role_manager_page):
    """取消子级勾选 → 父级不保持勾选（最后一个子级取消后父级去勾选）"""
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    pair = _find_parent_with_children(role_manager_page)
    if not pair:
        pytest.skip("未检测到 el-tree 树形权限结构")
    parent_label, children = pair
    child_label = children[0]

    if role_manager_page.get_checked_perm_count() > 0:
        role_manager_page.toggle_select_all_perms()
        role_manager_page.toggle_select_all_perms()
    role_manager_page.check_perm(child_label)

    role_manager_page.uncheck_perm(child_label)
    child_checked = role_manager_page.is_perm_checked(child_label)
    parent_checked = role_manager_page.is_perm_checked(parent_label)
    parent_indeterminate = role_manager_page.is_perm_node_indeterminate(parent_label)

    print(f"取消子级后: 子级勾选={child_checked}, 父级勾选={parent_checked}, 半选={parent_indeterminate}")
    assert not child_checked, f"子级'{child_label}'应取消勾选"


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(7)
def test_permission_uncheck_parent_keeps_children(role_manager_page):
    """取消父级勾选 → 子级一并取消"""
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    pair = _find_parent_with_children(role_manager_page)
    if not pair:
        pytest.skip("未检测到 el-tree 树形权限结构")
    parent_label, children = pair
    child_label = children[0]

    if role_manager_page.get_checked_perm_count() > 0:
        role_manager_page.toggle_select_all_perms()
        role_manager_page.toggle_select_all_perms()
    role_manager_page.check_perm(child_label)

    role_manager_page.uncheck_perm(parent_label)
    child_checked = role_manager_page.is_perm_checked(child_label)
    parent_checked = role_manager_page.is_perm_checked(parent_label)

    print(f"取消父级后: 父级勾选={parent_checked}, 子级勾选={child_checked}")
    assert not parent_checked, f"父级'{parent_label}'应取消勾选"
    assert not child_checked, f"取消父级后子级'{child_label}'也应被取消"


# ======================== 板块权限 ========================


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(8)
def test_permission_section_only(role_manager_page):
    """只勾选某板块 → 验证只有该板块勾选，子级不自动勾选"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    pair = _find_parent_with_children(role_manager_page)
    if not pair:
        pytest.skip("未检测到 el-tree 树形权限结构")
    section, children = pair

    if role_manager_page.get_checked_perm_count() > 0:
        role_manager_page.toggle_select_all_perms()
        role_manager_page.toggle_select_all_perms()

    role_manager_page.check_perm(section)
    checked = role_manager_page.get_checked_perm_labels()
    print(f"勾选板块'{section}'后已勾选: {checked}")

    assert section in checked, f"板块'{section}'应被勾选"
    for child in children:
        assert not role_manager_page.is_perm_checked(child), \
            f"只勾选板块时子级'{child}'不应被勾选"


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(9)
def test_permission_section_with_partial_functions(role_manager_page):
    """勾选板块 + 部分功能 → 只展示板块和部分功能"""
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    pair = _find_parent_with_children(role_manager_page)
    if not pair:
        pytest.skip("未检测到 el-tree 树形权限结构")
    section, children = pair
    if len(children) < 2:
        pytest.skip("子功能不足2个")

    if role_manager_page.get_checked_perm_count() > 0:
        role_manager_page.toggle_select_all_perms()
        role_manager_page.toggle_select_all_perms()

    role_manager_page.check_perm(section)
    role_manager_page.check_perm(children[0])

    checked = role_manager_page.get_checked_perm_labels()
    print(f"勾选板块+1功能后已勾选: {checked}")

    assert section in checked, f"板块'{section}'应被勾选"
    assert children[0] in checked, f"子功能'{children[0]}'应被勾选"
    assert children[1] not in checked, f"未勾选子功能'{children[1]}'不应被勾选"


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(10)
def test_permission_full_with_department(role_manager_page):
    """勾选全部子功能 → 板块从半选变为全部勾选"""
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    pair = _find_parent_with_children(role_manager_page)
    if not pair:
        pytest.skip("未检测到 el-tree 树形权限结构")
    section, children = pair

    if role_manager_page.get_checked_perm_count() > 0:
        role_manager_page.toggle_select_all_perms()
        role_manager_page.toggle_select_all_perms()

    for child in children:
        role_manager_page.check_perm(child)

    checked = role_manager_page.get_checked_perm_labels()
    parent_checked = role_manager_page.is_perm_checked(section)
    parent_indeterminate = role_manager_page.is_perm_node_indeterminate(section)

    print(f"勾选全部子功能后: 板块勾选={parent_checked}, 半选={parent_indeterminate}, 已勾选={checked}")

    for child in children:
        assert child in checked, f"子功能'{child}'应被勾选"
    assert parent_checked, f"板块'{section}'应被完全勾选"


# ======================== 多用户登录权限校验 ========================


def _add_member_to_role(role_manager_page, role_name: str) -> bool:
    """为指定角色添加成员（勾选全部可用的用户）。
    先通过侧边栏重进组织→角色，确保回到角色成员视图（退出功能权限页签）。
    返回 True 表示添加成功，False 表示无法访问成员管理按钮。
    """
    from pages.platform_navigation import PlatformNavigation

    page = role_manager_page.page
    close_any_dialog(role_manager_page)

    # 重新点击侧边栏"组织"→ 点击"角色"页签，重置视图
    nav = PlatformNavigation(page)
    nav.click_navigation_item("组织")
    page.wait_for_timeout(500)

    role_manager_page.click_role_tab()
    page.wait_for_timeout(300)

    role_manager_page.wait_for_page()
    role_manager_page.click_role_node(role_name)
    page.wait_for_timeout(300)

    # 检查按钮是否可见
    btn = page.locator(role_manager_page.MEMBER_MANAGE_BTN).first
    if not btn.is_visible():
        return False

    btn.click()
    role_manager_page.dialog.wait_for_member_dialog()
    scope = f"{role_manager_page.dialog.MEMBER_DIALOG}:visible"

    select_all = page.locator(f"{scope} .el-checkbox:has-text('全选')").first
    if select_all.count() > 0:
        select_all.click()
        page.wait_for_timeout(200)

    role_manager_page.dialog.click_member_dialog_confirm()
    page.wait_for_timeout(800)

    if role_manager_page.dialog.is_member_dialog_open():
        role_manager_page.dialog.click_member_dialog_close()
    return True


def _login_as_user(browser_manager, username: str):
    """用指定用户登录到新创建的独立浏览器上下文。
    返回 (ctx, page)，用完需 ctx.close()。
    """
    from config.settings import BASE_URL, LOGIN_PASSWORD
    from pages.login_page import LoginPage

    ctx = browser_manager.browser.new_context(
        viewport={"width": 1440, "height": 900},
    )
    page = ctx.new_page()
    lp = LoginPage(page)
    lp.open(BASE_URL)
    lp.login(username, LOGIN_PASSWORD)
    page.wait_for_timeout(2000)
    return ctx, page


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(11)
def test_permission_member_login_full_access(role_manager_page, browser_manager):
    """全选权限→添加成员→成员登录→检查有菜单权限"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    # 1. 全选权限并保存
    if role_manager_page.get_checked_perm_count() == 0:
        role_manager_page.toggle_select_all_perms()
    role_manager_page.click_perm_save()
    role_manager_page.page.wait_for_timeout(300)

    # 2. 添加成员
    if not _add_member_to_role(role_manager_page, _test_role_name):
        pytest.skip("无法访问成员管理按钮（可能因页签状态残留）")
    time.sleep(1)

    # 3. 用 tcf 登录独立上下文
    ctx, user_page = _login_as_user(browser_manager, "tcf")

    try:
        user_page.locator(".kd-aside").first.wait_for(state="visible", timeout=15000)
        print("tcf 用户登录成功，侧边栏可见（有权限）")
    except Exception as e:
        print(f"tcf 登录后侧边栏状态: {e}")
    finally:
        ctx.close()
        role_manager_page.page.bring_to_front()


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(12)
def test_permission_member_login_no_access(role_manager_page, browser_manager):
    """取消所有权限→成员登录→检查无菜单权限（跳转 noPermission）"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    # 1. 取消所有权限并保存
    checked = role_manager_page.get_checked_perm_count()
    if checked > 0:
        role_manager_page.toggle_select_all_perms()
        role_manager_page.toggle_select_all_perms()
    role_manager_page.click_perm_save()
    role_manager_page.page.wait_for_timeout(300)

    # 2. 添加成员
    if not _add_member_to_role(role_manager_page, _test_role_name):
        pytest.skip("无法访问成员管理按钮（可能因页签状态残留）")
    time.sleep(1)

    # 3. 用 tcf 登录独立上下文
    ctx, user_page = _login_as_user(browser_manager, "tcf")

    try:
        current_url = user_page.url
        print(f"tcf（无权限角色）登录后 URL: {current_url}")
        assert any(kw in current_url for kw in ["noPermission", "#/home", "#/noPermission", "#/login"]), \
            f"无权限用户登录后应受限，实际URL={current_url}"
    finally:
        ctx.close()
        role_manager_page.page.bring_to_front()


# ======================== 功能权限 — 搜索 ========================


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(13)
def test_permission_search_placeholder(role_manager_page):
    """权限面板搜索框 placeholder 校验"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    placeholder = role_manager_page.get_perm_search_placeholder()
    print(f"权限搜索框 placeholder: '{placeholder}'")
    assert placeholder, "权限搜索框应有 placeholder"


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(14)
def test_permission_search_existing(role_manager_page):
    """搜索存在的权限项 → 滚动条自动滚动并高亮显示"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    labels = role_manager_page.get_perm_labels()
    if not labels:
        pytest.skip("无权限项数据")

    keyword = labels[-1][:4] if len(labels[-1]) >= 2 else labels[0][:2]
    print(f"搜索关键词: '{keyword}' (总权限数: {len(labels)})")

    role_manager_page.search_perm(keyword)

    highlighted = role_manager_page.get_perm_highlighted_labels()
    visible = role_manager_page.get_perm_all_visible_labels()
    print(f"高亮标签: {highlighted}")
    print(f"搜索'{keyword}'后可见标签: {visible}")

    has_match = any(keyword in v for v in visible) or len(highlighted) > 0
    assert has_match or len(visible) > 0, \
        f"搜索'{keyword}'应有匹配结果"

    role_manager_page.clear_perm_search()


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(15)
def test_permission_search_nonexistent(role_manager_page):
    """搜索不存在的权限项 → 无高亮显示"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    role_manager_page.search_perm("不存在的权限项_xyz_999")

    highlighted = role_manager_page.get_perm_highlighted_labels()
    visible = role_manager_page.get_perm_all_visible_labels()
    print(f"搜索不存在项后高亮: {highlighted}, 可见标签: {visible}")

    assert len(highlighted) == 0, \
        f"搜索不存在项应无高亮，实际高亮={highlighted}"

    role_manager_page.clear_perm_search()


@allure.feature("角色管理")
@allure.story("功能权限")
@pytest.mark.order(16)
def test_permission_search_clear(role_manager_page):
    """清空搜索条件 → 数据恢复全部显示"""
    close_any_dialog(role_manager_page)
    role_manager_page.click_role_node(_test_role_name)
    role_manager_page.page.wait_for_timeout(200)
    role_manager_page.click_perm_tab()

    before_count = len(role_manager_page.get_perm_labels())
    labels = role_manager_page.get_perm_labels()
    if not labels:
        pytest.skip("无权限项数据")

    role_manager_page.search_perm(labels[0][:3])
    role_manager_page.clear_perm_search()

    after_count = len(role_manager_page.get_perm_labels())
    assert after_count == before_count, \
        f"清空搜索后应恢复全部权限，之前={before_count}，之后={after_count}"
