# src/config/cnn_config.py
import os
import warnings
from typing import ClassVar, Optional
from src.config.config import Config, Mode, TrainConfig, DataConfig, OptimizerConfig
import sys


class CnnConfig(Config):
    """
    CNN 配置类。

    继承自 Config，添加了用于卷积神经网络的特定配置参数。
    同样采用单例模式，通过 CnnConfig() 获取实例。
    """

    prefix: ClassVar[str] = "cnn"  # 定义类变量 prefix
    _instance: ClassVar[Optional["CnnConfig"]] = None  # 管理自己的实例

    # --- Instance Variables (Type Hinting) ---
    num_layers: int
    fc1_out_size: int
    kernel_size: int

    def __init__(self, reload: bool = False):
        """
        初始化 CnnConfig 实例。
        """
        # 强制打印入口信息
        sys.stdout.write(f"\nDEBUG [CnnConfig __init__ ENTER] id:{id(self)}, reload={reload}, _initialized={getattr(self, '_initialized', False)}\n")
        sys.stdout.flush()
        sys.stdout.write(f"  - BEFORE Deletion: hasattr fc1_out_size = {hasattr(self, 'fc1_out_size')}\n")
        sys.stdout.flush()

        is_first_initialization = not getattr(self, "_initialized", False)

        if reload and not is_first_initialization:
            sys.stdout.write(f"  - Reloading instance. Clearing CNN attrs.\n") # Debug
            sys.stdout.flush()
            for attr in ["num_layers", "fc1_out_size", "kernel_size"]:
                if hasattr(self, attr):
                    sys.stdout.write(f"    - Deleting '{attr}'...\n") # Debug
                    sys.stdout.flush()
                    try:
                        delattr(self, attr)
                        sys.stdout.write(f"      - Deleted. hasattr now = {hasattr(self, attr)}\n") # Debug
                        sys.stdout.flush()
                    except AttributeError:
                        sys.stdout.write(f"      - AttributeError during deletion (should not happen if hasattr was True)\n") # Debug
                        sys.stdout.flush()
                        pass
                else:
                     sys.stdout.write(f"    - Attribute '{attr}' not found, skipping deletion.\n") # Debug
                     sys.stdout.flush()
        else:
             sys.stdout.write(f"  - Not clearing CNN attrs (first_init={is_first_initialization}, reload={reload})\n") # Debug
             sys.stdout.flush()

        sys.stdout.write(f"  - AFTER Deletion (if any): hasattr fc1_out_size = {hasattr(self, 'fc1_out_size')}\n") # Debug
        sys.stdout.flush()
        sys.stdout.write(f"  - Calling super().__init__(reload={reload})...\n") # Debug
        sys.stdout.flush()

        super().__init__(reload=reload)

        sys.stdout.write(f"  - Returned from super().__init__.\n") # Debug
        sys.stdout.flush()
        sys.stdout.write(f"  - AFTER super(): hasattr fc1_out_size = {hasattr(self, 'fc1_out_size')}\n") # Debug
        sys.stdout.flush()

        if is_first_initialization:
            sys.stdout.write(f"  - First initialization: Setting defaults if needed.\n") # Debug
            sys.stdout.flush()
            if not hasattr(self, "num_layers"):
                 self.num_layers = 1
            if not hasattr(self, "fc1_out_size"):
                 sys.stdout.write(f"    - Setting default fc1_out_size=128\n") # Debug
                 sys.stdout.flush()
                 self.fc1_out_size = 128
            else:
                 sys.stdout.write(f"    - fc1_out_size already exists ({getattr(self, 'fc1_out_size', 'ERROR')}), NOT setting default.\n") # Debug
                 sys.stdout.flush()
            if not hasattr(self, "kernel_size"):
                 self.kernel_size = 3
        else:
             sys.stdout.write(f"  - Not first initialization, skipping default settings block.\n") # Debug
             sys.stdout.flush()

        sys.stdout.write(f"DEBUG [CnnConfig __init__ EXIT] id:{id(self)}, hasattr fc1_out_size = {hasattr(self, 'fc1_out_size')}\n") # Debug
        sys.stdout.flush()

    def __repr__(self) -> str:
        """
        返回 CnnConfig 实例的字符串表示。
        """
        # 更新 repr 以反映可能的属性缺失
        parts = [
            f"CnnConfig(prefix='{self.prefix}', mode='{Config.mode.value if Config.mode else None}', "
            f"db_path='{getattr(self, 'db_path', 'N/A')}', device='{getattr(self, 'device', 'N/A')}'"
        ]
        for attr_name in [
            "num_layers",
            "num_filters",
            "kernel_size",
            "padding",
            "fc1_out_size",
        ]:
            parts.append(f"{attr_name}={getattr(self, attr_name, 'N/A')}")
        # 添加配置节信息
        for section_name in ["train", "data", "optimizer"]:
            section = getattr(self, section_name, None)
            section_repr = (
                repr(section.__dict__) if hasattr(section, "__dict__") else "N/A"
            )
            parts.append(f"{section_name}={section_repr}")

        return ", ".join(parts) + ")"


if __name__ == "__main__":
    # --- 设置演示用配置文件夹 ---
    DEMO_CONFIG_FOLDER = os.path.join("tests", "config_demo")  # 指向 tests/config_demo
    original_config_folder = Config.config_folder
    use_demo_folder = False
    if os.path.isdir(DEMO_CONFIG_FOLDER):
        print(f"*** 检测到演示配置文件夹: {DEMO_CONFIG_FOLDER} ***")
        print("*** 演示将使用此文件夹中的配置文件 ***")
        Config.set_config_folder(DEMO_CONFIG_FOLDER)
        use_demo_folder = True
    else:
        print(f"*** 未检测到演示配置文件夹: {DEMO_CONFIG_FOLDER} ***")
        print(f"*** 演示将使用默认配置文件夹: {original_config_folder} ***")

    try:
        # --- 清理可能存在的旧实例和模式文件 ---
        Config.instance = None
        CnnConfig._instance = None  # 清理子类实例
        Config.mode = None
        mode_file_path = os.path.join("temp", "mode.txt")
        if os.path.exists(mode_file_path):
            os.remove(mode_file_path)
        print("\n--- CNN 配置演示 --- (", end="")
        print(f"使用配置: {Config.config_folder}")

        # 用于存储上一个模式的配置，以便对比
        previous_cfg_dict = {}

        def capture_cnn_config_state(cfg):
            """捕获当前 CNN 配置的关键值用于对比"""
            state = {
                # 通用配置项
                "train.batch_size": getattr(
                    getattr(cfg, "train", None), "batch_size", None
                ),
                "data.window_size": getattr(
                    getattr(cfg, "data", None), "window_size", None
                ),
                "optimizer.lr": getattr(getattr(cfg, "optimizer", None), "lr", None),
                # CNN 特定配置项
                "num_layers": getattr(cfg, "num_layers", None),
                "num_filters": getattr(cfg, "num_filters", None),
                "kernel_size": getattr(cfg, "kernel_size", None),
                "fc1_out_size": getattr(cfg, "fc1_out_size", None),
            }
            # Filter out None values if attribute or section doesn't exist
            return {k: v for k, v in state.items() if v is not None}

        def compare_and_print(key, current_value, previous_dict, current_mode_name):
            """比较并打印配置项的变化"""
            previous_value = previous_dict.get(key)
            if previous_value is None:  # 第一次演示 (TEST)
                print(f"    {key}: {current_value}")
            elif current_value == previous_value:
                print(f"    {key}: {current_value} (保留自上个模式)")
            else:
                print(
                    f"    {key}: {current_value} (由 {current_mode_name} 文件覆盖, 原值: {previous_value})"
                )

        def demonstrate_cnn_mode(mode_to_set: Mode, prev_cfg_dict: dict):
            print(f"\n--- 演示模式: {mode_to_set.name} ---")
            # Reset instance to force re-init and load files for the new mode in demo
            CnnConfig._instance = None
            Config.set_mode(mode_to_set)  # 设置模式 (会写temp/mode.txt)
            print(f"设置模式为: {mode_to_set.name}")

            # 获取/创建 CNN Config 单例
            print("获取 CnnConfig 实例 (将触发配置加载)... ")
            cfg = CnnConfig()
            print("实例已获取。当前配置值:")

            print(f"  - 全局模式 (Config.mode): {Config.mode.name}")
            print(f"  - 实例前缀 (cfg.prefix): '{cfg.prefix}'")
            print(f"  - 设备 (cfg.device): {cfg.device}")
            print(f"  - 数据库路径 (cfg.db_path): {cfg.db_path}")

            current_state = capture_cnn_config_state(cfg)

            print("\n  --- 继承/覆盖的通用配置节对比 ---")
            compare_and_print(
                "train.batch_size",
                current_state.get("train.batch_size", "N/A"),
                prev_cfg_dict,
                mode_to_set.name,
            )
            compare_and_print(
                "data.window_size",
                current_state.get("data.window_size", "N/A"),
                prev_cfg_dict,
                mode_to_set.name,
            )
            compare_and_print(
                "optimizer.lr",
                current_state.get("optimizer.lr", "N/A"),
                prev_cfg_dict,
                mode_to_set.name,
            )

            print("\n  --- CNN 特定配置对比 ---")
            compare_and_print(
                "num_layers",
                current_state.get("num_layers", "N/A"),
                prev_cfg_dict,
                mode_to_set.name,
            )
            compare_and_print(
                "num_filters",
                current_state.get("num_filters", "N/A"),
                prev_cfg_dict,
                mode_to_set.name,
            )
            compare_and_print(
                "kernel_size",
                current_state.get("kernel_size", "N/A"),
                prev_cfg_dict,
                mode_to_set.name,
            )
            compare_and_print(
                "fc1_out_size",
                current_state.get("fc1_out_size", "N/A"),
                prev_cfg_dict,
                mode_to_set.name,
            )

            # print("Code Filter (Example output):") # Commented out
            print("--- 模式演示结束 ---")
            return current_state  # 返回当前状态供下一次对比

        # 演示不同模式下的 CNN 配置加载
        previous_cfg_dict = demonstrate_cnn_mode(Mode.TEST, previous_cfg_dict)
        previous_cfg_dict = demonstrate_cnn_mode(Mode.DEV, previous_cfg_dict)
        demonstrate_cnn_mode(Mode.PROD, previous_cfg_dict)

    finally:
        # --- 恢复原始配置文件夹路径 ---
        if use_demo_folder:
            Config.set_config_folder(original_config_folder)
            print(f"\n*** 演示结束，已恢复配置文件夹为: {Config.config_folder} ***")
        # --- 清理模式文件 ---
        mode_file_path = os.path.join("temp", "mode.txt")
        if os.path.exists(mode_file_path):
            os.remove(mode_file_path)
