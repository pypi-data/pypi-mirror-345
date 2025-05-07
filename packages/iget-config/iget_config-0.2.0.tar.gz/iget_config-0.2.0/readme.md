# Project Setup and Usage Guide

## Environment Setup
This project uses the following environment:
- Micromamba as package manager
- Python 3.13
- PyTorch 2.6.0
- PyTorch Lightning

You can use `setup.ps1` to install all required dependencies.

## Mode Configuration
The project supports different running modes:
- Default mode: test
- Available modes: test, dev, prod

To change the mode, use the following command:
```powershell
.\set_mode.ps1 -Mode [mode_name]
```
Example:
```powershell
.\set_mode.ps1 -Mode prod
.\set_mode.ps1 -Mode dev
.\set_mode.ps1 -Mode test
```

## Running and Debugging
The project is configured for both running and debugging in VS Code:
1. Use the right-click context menu in the editor
2. Select "Run Python File" to execute the current file
3. Debug configurations are available in `.vscode` settings

## Environment Information
The project includes an environment information script (`src/env.py`) that displays:
- Python version
- PyTorch version
- CUDA version and device information (if available)
- Python executable path

To run the environment check:
```powershell
D:/dev/mamba/envs/pytorch/python.exe src/env.py
```

## Temporary Files
When creating temporary files:
- All temporary files must be created in the `temp` directory
- The `temp` directory is ignored by git (configured in `.gitignore`)
- This rule applies to all AI-assisted code generation and temporary file creation

## Unit Testing
The project includes a sample test file (`tests/add_test.py`) that demonstrates basic unittest setup and structure. Here's how to work with unit tests:

### Running Tests
You can run tests in several ways:
1. In Cursor IDE:
   - Open the Testing view in the sidebar
   - All test files will be automatically discovered
   - You can run individual tests or all tests from the Testing view
   - When editing a test file (e.g., `add_test.py`), right-click in the editor and select "Run Python File" to run the test

2. In Editor:
   - Open the test file (e.g., `add_test.py`) in the editor
   - Right-click in the editor
   - Select "Run Python File"
   - The test will run in the terminal

### Test Configuration
1. Configure test settings using `Ctrl+Shift+P`
2. Select "Python: Configure Tests"
3. Choose "unittest" (not pytest) as the test framework
4. Select the `tests` folder
5. Test files should follow the `*_test.py` naming convention

### Example Test Structure
The `add_test.py` demonstrates:
- Basic unittest setup with `unittest.TestCase`
- Test case structure with `setUp` and `tearDown` methods
- Simple assertion testing (1+2=3)

## iget-config 包发布与使用

本节介绍如何将 `src/config` 目录下的代码打包成 `iget-config` 库，发布到 PyPI，以及如何在其他项目中使用这个库。

### 环境准备 (用于编译和上传)

确保您的 Python 环境 (例如 `D:/dev/mamba/envs/pytorch/python.exe`) 中安装了以下包：

```bash
# 如果没有安装，请运行：
D:/dev/mamba/envs/pytorch/python.exe -m pip install build twine
```

### 编译 (构建) 新版本

当您修改了 `src/config` 目录下的代码后，需要重新编译打包：

1.  **更新版本号:**
    *   修改 `pyproject.toml` 文件中的 `version = "..."` 行，增加版本号 (例如从 `0.1.2` 改为 `0.1.3`)。
    *   **同时**修改 `src/config/__init__.py` 文件中的 `__version__ = "..."` 行，使其与 `pyproject.toml` 中的版本号**保持一致**。
2.  **清理旧构建 (重要):** 在项目根目录 (`D:\iget`) 运行以下命令，删除可能存在的旧构建文件：
    ```powershell
    Remove-Item -Recurse -Force dist
    Remove-Item -Recurse -Force build
    Remove-Item -Recurse -Force src\*.egg-info # 清理 egg-info 文件夹
    ```
3.  **执行构建:** 在项目根目录 (`D:\iget`) 运行构建命令：
    ```powershell
    D:/dev/mamba/envs/pytorch/python.exe -m build
    ```
    构建成功后，会在 `dist/` 目录下生成新的 `.tar.gz` 和 `.whl` 文件 (例如 `iget_config-0.1.3.tar.gz` 和 `iget_config-0.1.3-py3-none-any.whl`)。

### 上传新版本到 PyPI

使用 `twine` 将 `dist/` 目录下的新版本文件上传到 PyPI：

1.  **获取 PyPI API 令牌:**
    *   登录 [pypi.org](https://pypi.org/)。
    *   双因素验证在手机上查看微软的app
    *   进入 "Account settings" -> "API tokens"。
    *   **建议为每个项目创建单独的令牌**，点击 "Add API token"，名称随意 (如 `iget-config uploader`)，范围 (Scope) 选择 "Project"，项目名填入 `iget-config`。
    *   **立即复制**新生成的、以 `pypi-` 开头的完整令牌。
2.  **执行上传:** 在项目根目录 (`D:\iget`) 的**本地终端 (例如 PowerShell)** 中运行以下命令：
    ```powershell
    D:/dev/mamba/envs/pytorch/python.exe -m twine upload dist/*
    ```
3.  **输入令牌:** 当提示 `Enter your API token:` 时，粘贴您刚刚获取的 API 令牌，然后按 Enter。
    *   如果上传成功，会看到类似 `View at https://pypi.org/project/iget-config/0.1.3/` 的信息。
    *   如果遇到 `403 Forbidden` 错误，通常是 API 令牌无效或输入错误。
    *   如果遇到 `File already exists` 错误，说明这个版本号已经上传过，您需要回到【编译】步骤增加版本号。

### 在其他项目中使用 `iget-config`

1.  **安装:** 在您想使用该库的项目环境中，通过 `pip` 安装：
    ```bash
    pip install iget-config
    ```
    或者安装特定版本：
    ```bash
    pip install iget-config==0.1.2
    ```
2.  **准备环境 (重要提醒):**
    由于库的原始代码依赖特定的文件结构，在您**运行 Python 脚本**的**当前工作目录**下，**必须**满足以下条件：
    *   存在一个名为 `config` 的文件夹，其中包含您的项目所需的 `.yaml` 配置文件 (例如 `default.yaml`, `default_dev.yaml`, `cnn.yaml` 等)。库会根据模式自动加载这些文件。
    *   存在一个名为 `temp` 的文件夹，其中包含一个名为 `mode.txt` 的文件，文件内容为 `TEST`, `DEV`, 或 `PROD` (不区分大小写)，用于指定运行模式。

    **示例目录结构:**
    ```
    /path/to/your_project/
    ├── main.py             # 您的主程序脚本
    ├── config/             # 必须存在
    │   ├── default.yaml
    │   ├── default_dev.yaml
    │   └── cnn.yaml
    │   └── ... (其他 .yaml 文件)
    └── temp/               # 必须存在
        └── mode.txt        # 必须存在，内容为 TEST/DEV/PROD
    ```

3.  **在代码中使用 (推荐方式):**
    虽然库会尝试读取 `temp/mode.txt` 和 `./config`，但更健壮和明确的方式是在代码中**显式设置**：

    ```python
    import os
    from config import Config, Mode # 直接从安装的包导入

    # --- 设置配置路径和模式 ---
    # 假设您的配置文件放在项目根目录下的 'my_configs' 文件夹
    project_root = os.path.dirname(os.path.abspath(__file__)) # 获取当前脚本所在目录
    config_directory = os.path.join(project_root, 'my_configs') # 替换为您实际的配置文件夹名

    # 检查配置目录是否存在
    if not os.path.isdir(config_directory):
        raise FileNotFoundError(f"配置目录未找到: {config_directory}")

    Config.set_config_folder(config_directory)
    Config.set_mode(Mode.DEV) # 或者 Mode.PROD, Mode.TEST

    print(f"配置目录已设置为: {Config.config_folder}")
    print(f"运行模式已设置为: {Config.mode}")

    # --- 实例化 Config ---
    # 使用 reload=True 确保加载您刚才设置的路径和模式对应的文件
    cfg = Config(reload=True)
    print("Config 实例已创建。")

    # --- 使用配置 ---
    print(f"数据库路径: {cfg.db_path}")
    print(f"训练批次大小: {cfg.train.batch_size}")

    # 如果需要使用 CnnConfig (假设已在 __init__.py 中导出)
    # from config import CnnConfig
    # cnn_cfg = CnnConfig(reload=True)
    # print(f"CNN 模型名称: {cnn_cfg.model_name}") # 假设 CnnConfig 有 model_name 属性
    ```

**注意:** 上述推荐用法可以摆脱对特定 `temp/mode.txt` 和 `./config` 目录结构的依赖，使您的代码更清晰、更易于部署。