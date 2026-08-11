# UI Auto (Python + Playwright + Pytest)

小型 UI 自动化框架：方案 A 自管 Browser，POM + YAML 数据驱动。

使用本机已安装的 Python 环境，无需 pip install / requirements.txt。

## 项目结构

```text
├── conftest.py              # page / login_page 等 fixture
├── pytest.ini
├── run.py / run.ps1         # 一键运行 + 生成 Allure 报告
├── .env / .env.example
├── config/settings.py       # 环境配置
├── core/browser.py          # BrowserManager
├── pages/
│   ├── base_page.py         # 通用页面操作
│   ├── login_page.py
│   └── home_page.py
├── tests/                   # 测试用例
├── data/                    # 测试数据 (YAML)
├── common/utils/
│   ├── log_util.py          # 日志
│   └── yaml_util.py         # YAML 读/写/清空
├── logs/                    # 运行日志
└── reports/                 # Allure 报告 / 失败截图
```

## 快速开始

```powershell
cd c:\Users\pengh\Desktop\cursor_code

# 推荐：运行脚本（自动生成 reports/allure-report 并打开）
python run.py
.\run.ps1

# 常用参数（按用例类型）
python run.py -m smoke      # 冒烟：页面文案 + 空用户名/空密码
python run.py -m system     # 系统：用户名/密码不正确
python run.py -m core       # 核心：正确账号登录
python run.py tests/test_login.py
python run.py --headless
python run.py --no-open

# 也可直接用 pytest + allure CLI
python -m pytest -m smoke --alluredir=reports/allure-results --clean-alluredir
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

依赖需已在本机装好：`playwright`、`pytest`、`allure-pytest`、`PyYAML`、`python-dotenv`、`loguru`，以及 Allure CLI（`allure` 命令）。

## 说明

- 目标登录页：`http://192.168.4.171:40013/webapp/#/login`
- 成功登录账号写在 `.env`：`LOGIN_USERNAME` / `LOGIN_PASSWORD`
- 用例与数据分离：`tests/` 写逻辑，`data/login.yaml` 写期望文案与用例
- 失败截图自动保存到 `reports/`
