"""测试数据占位符解析工具。

将 YAML 数据文件中的 <RANDOM_*> 占位符解析为随机值，
用于 may_pass 用例避免因重复名称导致后续执行失败。

支持的占位符：
  <RANDOM_ALPHA>       → 8位随机英文小写
  <RANDOM_ALPHANUM>    → 8位随机英文小写+数字
  <RANDOM_DIGIT>       → 10位随机数字（时间戳后10位）
  <RANDOM_CN>          → 4位随机中文字符
  <RANDOM_ALPHA_N>     → N位随机英文小写（如 <RANDOM_ALPHA_32>）
  <RANDOM_SPECIAL>     → 4位随机英文 + 特殊字符 !@#$%^&*()
  <RANDOM_LEAD_SPACE>  → 前导空格 + 5位随机英文
  <RANDOM_MID_SPACE>   → 3位英文 + 空格 + 3位英文
  <RANDOM_TAIL_SPACE>  → 5位随机英文 + 尾部空格
  <RANDOM_SQL>         → 3位随机英文 + SQL注入模式
  <RANDOM_SCRIPT>      → 3位随机英文 + <script> 标签
  <RANDOM_IMG>         → 3位随机英文 + <img> 标签
"""

import random
import string
import time


def resolve_value(value: str) -> str:
    """解析占位符为随机值，非占位符原样返回。"""
    if not isinstance(value, str) or not value.startswith("<RANDOM"):
        return value

    if value == "<RANDOM_ALPHA>":
        return "".join(random.choices(string.ascii_lowercase, k=8))
    if value == "<RANDOM_ALPHANUM>":
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=8))
    if value == "<RANDOM_DIGIT>":
        return str(int(time.time() * 1000))[-10:]
    if value == "<RANDOM_CN>":
        cn_chars = "测试角色管理权限配置系统用户部门项目"
        return "".join(random.choices(cn_chars, k=4))
    if value.startswith("<RANDOM_ALPHA_"):
        n = int(value[len("<RANDOM_ALPHA_"):-1])
        return "".join(random.choices(string.ascii_lowercase, k=n))

    # may_pass 用例 — 随机前缀 + 特征模式，避免重复名称
    if value == "<RANDOM_SPECIAL>":
        prefix = "".join(random.choices(string.ascii_lowercase, k=4))
        return prefix + "!@#$%^&*()"
    if value == "<RANDOM_LEAD_SPACE>":
        suffix = "".join(random.choices(string.ascii_lowercase, k=5))
        return " " + suffix
    if value == "<RANDOM_MID_SPACE>":
        left = "".join(random.choices(string.ascii_lowercase, k=3))
        right = "".join(random.choices(string.ascii_lowercase, k=3))
        return left + " " + right
    if value == "<RANDOM_TAIL_SPACE>":
        prefix = "".join(random.choices(string.ascii_lowercase, k=5))
        return prefix + " "
    if value == "<RANDOM_SQL>":
        prefix = "".join(random.choices(string.ascii_lowercase, k=3))
        return prefix + "'; DROP TABLE roles; --"
    if value == "<RANDOM_SCRIPT>":
        prefix = "".join(random.choices(string.ascii_lowercase, k=3))
        return prefix + "<script>alert(1)</script>"
    if value == "<RANDOM_IMG>":
        prefix = "".join(random.choices(string.ascii_lowercase, k=3))
        return prefix + "<img onerror=alert(1) src=x>"

    return value
