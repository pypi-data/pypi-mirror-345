# src/common/config.py

"""
应用程序的配置模块。

该模块定义了 Config 类及其相关的训练、数据处理和优化配置。
它支持基于运行模式 (TEST, DEV, PROD) 和类继承的层级化配置加载 (YAML)。
使用单例模式，通过 Config() 或 SubClass() 获取实例。
"""

import os
import warnings
from enum import Enum
from typing import ClassVar, Optional, Type
import sys

import torch
import yaml


# 自定义 Dumper 类，用于处理多维数组的输出格式
class MyDumper(yaml.Dumper):
    """
    自定义 YAML Dumper，用于以紧凑的流式样式表示嵌套列表（如二维数组）。
    """

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow=True, indentless=False)

    def represent_list(self, data):
        """
        确保嵌套列表以紧凑的流式样式表示。

        参数:
            data (list): 要表示的列表。
        """
        return self.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


yaml.add_representer(list, MyDumper.represent_list, Dumper=MyDumper)


class Mode(Enum):
    """
    操作模式的枚举。
    """

    TEST = "test"
    DEV = "dev"
    PROD = "prod"


class TrainConfig:
    """
    训练的配置参数。
    """

    def __init__(
        self,
        batch_size: int = 256 * 8,
        num_epochs: int = 1000,
        num_workers: int = 0,
        shuffle: bool = True,
        log_mode: bool = True,
        graph_rate: int = 10,
    ):
        """
        初始化训练配置。

        参数:
            batch_size (int): 每批样本的数量。
            num_epochs (int): 训练的轮数。
            num_workers (int): 数据加载的工作线程数。
            shuffle (bool): 是否打乱数据。
            log_mode (bool): 是否启用日志记录。
            graph_rate (int): 图形日志记录的频率。
        """
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.num_workers = num_workers
        self.shuffle = shuffle
        self.log_mode = log_mode
        self.graph_rate = graph_rate


class DataConfig:
    """
    数据处理的配置参数。
    """

    def __init__(
        self,
        window_size: int = 20,
        label_size: int = 1,
        label_exclude_days: int = 1,
        label_mode: int = 2,
        train_days: int = 0,
        validate_days: int = 240,
        test_days: int = 30,
        feature_size: int = 12,
        feature_mode: list = None,
        label_bins: list = None,
        feature_bins: list = None,
        loss_weight: list = None,
        max_stop_rate: float = 0.3,  # 停盘天数占比超过，则该样本无效
    ):
        """
        初始化数据配置。

        参数:
            window_size (int): 如果是滑动窗口，这里定义窗口的长度。
            label_size (int): 标签的长度，如果是2，表示表示是一个2元素的向量。
            label_exclude_days (int): 标签的排除天数，如果是2，表示滑动窗口之后的2天用来计算标签，则滑动窗口样本应该去掉最后的两天。
            label_mode (int): 标签的模式，即使用原始值、相对值、分类值还是多维嵌入层。
            train_days (int): 训练天数。
            validate_days (int): 验证天数。
            test_days (int): 测试天数。
            feature_size (int): 特征向量的大小。
            feature_mode (list): 特征选择模式。
            label_bins (list): 标注的区间。
            feature_bins (list): 特征的区间。
            loss_weight (list): 损失计算的权重。
            max_stop_rate (float): 停盘天数占比超过，则该样本无效。
        """
        self.window_size = window_size
        self.label_size = label_size
        self.label_exclude_days = label_exclude_days
        self.label_mode = label_mode
        self.train_days = train_days
        self.validate_days = validate_days
        self.test_days = test_days
        self.feature_size = feature_size
        # feature_mode: List indicating which feature groups are active (e.g., 1 for active). Default is 10 active groups.
        self.feature_mode = feature_mode if feature_mode else [1] * 10

        default_feature_bins = [
            [-0.08, -0.03, -0.01, 0.01, 0.03, 0.08],  # Example bin for one feature
            [0.01, 0.05, 0.2, 0.5, 2, 10],  # Example bin for another
        ]  # Adjust structure as needed
        # Repeat the pattern or define specific bins for all feature_size features
        num_bin_patterns = len(default_feature_bins)
        self.feature_bins = [
            default_feature_bins[i % num_bin_patterns] for i in range(feature_size)
        ]
        # Allow override from YAML
        if feature_bins is not None:
            self.feature_bins = feature_bins

        self.label_bins = (
            label_bins if label_bins else [-0.12, -0.07, -0.01, 0.01, 0.07, 0.12]
        )
        self.loss_weight = (
            loss_weight
            if loss_weight
            else [0.2357, 0.1966, 0.025, 0.0284, 0.0266, 0.1852, 0.3026]
        )
        self.max_stop_rate = max_stop_rate


class OptimizerConfig:
    """
    优化器的配置参数。
    """

    def __init__(
        self,
        lr: float = 0.02,
        min_lr: float = 0.0001,
        patience: int = 30,
        min_delta: float = 0.000,
        optimizers_threshold: float = 0.000,
        optimizers_patience: int = 10,
        optimizers_factor: float = 0.5,
    ):
        """
        初始化优化器配置。

        参数:
            lr (float): 学习率。
            min_lr (float): 最小学习率。
            patience (int): 学习率调度器的耐心。
            min_delta (float): 提前停止的最小变化。
            optimizers_threshold (float): 优化器调整的阈值。
            optimizers_patience (int): 优化器调整的耐心。
            optimizers_factor (float): 优化器调整的因子。
        """
        self.lr = lr
        self.min_lr = min_lr
        self.patience = patience
        self.min_delta = min_delta
        self.optimizers_threshold = optimizers_threshold
        self.optimizers_patience = optimizers_patience
        self.optimizers_factor = optimizers_factor


class Config:
    """
    主要的配置类。

    处理层级化配置加载 (默认 -> 模式 -> 模型 -> 模型模式)。
    使用单例模式，通过 Config() 或 SubClass() 获取/创建实例。
    """

    # --- Class Variables ---
    mode: ClassVar[Optional[Mode]] = None
    config_folder: ClassVar[str] = "config"
    prefix: ClassVar[str] = ""
    _instance: ClassVar[Optional["Config"]] = None # 每个类管理自己的实例
    _print_initialized: ClassVar[bool] = False

    def __new__(cls: Type["Config"], *args, **kwargs) -> "Config":
        """
        实现单例模式，确保每个具体类只有一个实例。
        """
        # 每个类管理自己的 _instance 类变量
        if getattr(cls, '_instance', None) is None:
            instance = super().__new__(cls)
            instance._initialized = False
            instance._loaded_mode = None
            cls._instance = instance # 分配给特定的类变量
        return cls._instance

    @classmethod
    def set_mode(cls, mode: Mode):
        """
        设置全局运行模式，并将其持久化到 temp/mode.txt。
        此方法只更改类级别的模式状态，不影响现有实例。
        """
        current_mode = Config.mode
        if current_mode == mode:
            return

        if current_mode is not None:
            warnings.warn(f"Config mode changing from {current_mode} to {mode}")

        Config.mode = mode

        try:
            if not os.path.exists("temp"):
                os.makedirs("temp")
            with open("temp/mode.txt", "w", encoding="utf-8") as f:
                f.write(mode.name)
        except IOError as e:
            print(f"无法写入temp/mode.txt: {e}")
        
        # 移除遍历注册表和调用 reload_config 的逻辑

    @classmethod
    def set_config_folder(cls, folder: str):
        """
        设置全局配置文件夹路径。
        """
        Config.config_folder = folder

    def __init__(self, reload: bool = False):
        """
        初始化 Config 实例 (如果尚未初始化或强制刷新)。
        加载默认配置和特定于模式/子类的配置。
        记录加载时使用的模式。

        参数:
            reload (bool): 如果为 True，则强制重新加载配置，即使实例已存在。
        """
        # 强制打印入口信息
        sys.stdout.write(f"\nDEBUG [Config __init__ ENTER] id:{id(self)}, reload={reload}, _initialized={getattr(self, '_initialized', False)}\n")
        sys.stdout.flush()

        # 仅在首次初始化或强制 reload 时执行完整逻辑
        if getattr(self, "_initialized", False) and not reload:
            sys.stdout.write(f"DEBUG [Config]: Skipping init for already initialized instance {id(self)}\n")
            sys.stdout.flush()
            return

        self._loaded_mode = None

        # 确定模式 (仅在全局模式未设置时)
        if Config.mode is None:
            try:
                with open("temp/mode.txt", "r", encoding="utf-8") as f:
                    mode_text = f.read().strip().upper()
                    if mode_text in [m.name for m in Mode]:
                        if Config.mode is None:
                           Config.mode = Mode[mode_text]
                    else:
                        if Config.mode is None:
                           Config.mode = Mode.TEST
            except (FileNotFoundError, IOError):
                if Config.mode is None:
                   Config.mode = Mode.TEST
        
        sys.stdout.write(f"DEBUG [Config]: Mode determined as: {Config.mode}\n")
        sys.stdout.flush()

        # --- (重新)设置基本属性和默认配置对象 --- 
        self.prefix = type(self).prefix
        self.device = self._determine_device()
        sys.stdout.write(f"DEBUG [Config]: Resetting Train/Data/Optimizer Config objects for {id(self)}\n")
        sys.stdout.flush()
        self.train = TrainConfig()
        self.data = DataConfig()
        self.optimizer = OptimizerConfig()
        
        # 如果是子类，可能需要重置子类定义的属性到代码默认值
        # (这部分比较tricky，取决于子类的实现方式，暂时省略)

        # --- 加载层级化配置 --- (基于当前 Config.mode)
        sys.stdout.write(f"DEBUG [Config]: Calling _load_hierarchical_config for {id(self)} with mode {Config.mode}\n")
        sys.stdout.flush()
        self._load_hierarchical_config()
        self._loaded_mode = Config.mode   # 记录加载时使用的模式

        # --- 设置模式特定属性 --- (基于当前 Config.mode)
        sys.stdout.write(f"DEBUG [Config]: Setting mode-specific attributes for {id(self)} with mode {Config.mode}\n")
        sys.stdout.flush()
        self.db_path = self._get_db_path()
        self.code_filter = self._get_code_filter()

        # --- 标记为已初始化 ---
        self._initialized = True
        sys.stdout.write(f"DEBUG [Config __init__ EXIT] id:{id(self)}, Loaded mode: {self._loaded_mode}\n")
        sys.stdout.flush()

    def _determine_device(self) -> str:
        """确定可用的计算设备 (cuda, mps, cpu)。"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_built():
            return "mps"
        else:
            return "cpu"

    def _load_hierarchical_config(self):
        """加载层级化配置文件：default -> default_{mode} -> {prefix} -> {prefix}_{mode}"""
        mode = Config.mode
        sys.stdout.write(f"DEBUG [Config]: _load_hierarchical_config ENTER - Mode='{mode.name if mode else 'None'}', Prefix='{self.prefix}', InstanceID={id(self)}\n")
        sys.stdout.flush()

        # Base default file
        self._load_from_file("default.yaml")

        # Base mode-specific file
        if mode and mode != Mode.TEST:
            sys.stdout.write(f"DEBUG [Config]: _load_hierarchical_config - Attempting base mode file default_{mode.value}.yaml\n")
            sys.stdout.flush()
            self._load_from_file(f"default_{mode.value}.yaml")
        else:
            sys.stdout.write(f"DEBUG [Config]: _load_hierarchical_config - Skipping base mode file for mode {mode.name if mode else 'None'}\n")
            sys.stdout.flush()

        # Subclass default file
        if self.prefix:
             sys.stdout.write(f"DEBUG [Config]: _load_hierarchical_config - Attempting prefix file {self.prefix}.yaml\n")
             sys.stdout.flush()
             self._load_from_file(f"{self.prefix}.yaml")

        # Subclass mode-specific file
        if self.prefix and mode and mode != Mode.TEST:
             sys.stdout.write(f"DEBUG [Config]: _load_hierarchical_config - Attempting prefix mode file {self.prefix}_{mode.value}.yaml\n")
             sys.stdout.flush()
             self._load_from_file(f"{self.prefix}_{mode.value}.yaml")
        else:
            sys.stdout.write(f"DEBUG [Config]: _load_hierarchical_config - Skipping prefix mode file for prefix '{self.prefix}' and mode {mode.name if mode else 'None'}\n")
            sys.stdout.flush()

        sys.stdout.write(f"DEBUG [Config]: _load_hierarchical_config EXIT - Final batch_size={getattr(getattr(self,'train', None),'batch_size','N/A')}, InstanceID={id(self)}\n")
        sys.stdout.flush()

    def _load_from_file(self, filename: str):
        file_path = os.path.join(Config.config_folder, filename)
        if os.path.exists(file_path):
            sys.stdout.write(f"DEBUG [Config]: _load_from_file - Loading: {filename} (InstanceID={id(self)})\n")
            sys.stdout.flush()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    yaml_data = yaml.safe_load(f)
                    if yaml_data:
                        self._override_attributes(self, yaml_data)
                    else:
                        sys.stdout.write(f"DEBUG [Config]: _load_from_file - Skipped empty file: {filename}\n")
                        sys.stdout.flush()
            except yaml.YAMLError as e:
                 warnings.warn(f"Error loading configuration from {file_path}: YAML parsing error: {e}", RuntimeWarning)
            except Exception as e:
                 warnings.warn(f"Error loading configuration from {file_path}: {e}", RuntimeWarning)
        else:
             # 文件未找到, 发出 UserWarning
             warnings.warn(f"Configuration file not found: {file_path}", UserWarning)
             # 保留调试打印
             sys.stdout.write(f"DEBUG [Config]: _load_from_file - File not found, skipping: {filename}\n")
             sys.stdout.flush()

    def _override_attributes(self, obj, data: dict):
        for key, value in data.items():
            if hasattr(obj, key):
                target_attr = getattr(obj, key)
                if isinstance(value, dict) and hasattr(target_attr, '__dict__'):
                     self._override_attributes(target_attr, value)
                else:
                     try:
                         setattr(obj, key, value)
                     except AttributeError as e:
                         warnings.warn(f"Could not set attribute '{key}' on {type(obj).__name__}: {e}", RuntimeWarning)
            else:
                setattr(obj, key, value)

    def _get_db_path(self) -> str:
        """
        根据模式获取数据库路径。
        """
        if Config.mode == Mode.TEST:
            return "stock.db"
        elif Config.mode == Mode.DEV:
            return "stock_dev.db"
        # elif Config.mode == Mode.PROD: # Make PROD explicit if needed
        #     return "stock_prod.db"
        return "stock_prod.db"  # Default to PROD path otherwise

    def _get_code_filter(self) -> callable:
        """
        根据模式获取代码过滤器函数。
        注意：返回的是 lambda 函数，可能无法被 YAML 序列化。
        """
        if Config.mode == Mode.TEST:
            # TEST: 仅加载 3 个特定代码
            return lambda codes: codes[
                codes["code"].apply(lambda x: "sz.301000" <= x < "sz.301003")
            ]
        elif Config.mode == Mode.DEV:
            # DEV: 加载所有 301 开头的代码
            return lambda codes: codes[codes.code.str.startswith("sz.301")]
        # PROD (and default): 加载所有 30 开头的代码
        return lambda codes: codes[codes.code.str.startswith("sz.30")]

    # --- Version Management Methods ---

    def save_version(self, version: str):
        """
        将当前配置状态保存到一个特定版本的文件中。
        文件名格式: {prefix}_{version}.yaml (基础 Config 为 default_{version}.yaml)。
        此操作独立于当前的全局模式。

        参数:
            version (str): 配置版本标识符 (例如 'v1.0', 'best_run')。
        """
        prefix_part = self.prefix or 'default'
        file_name = f"{prefix_part}_{version}.yaml"
        file_path = os.path.join(Config.config_folder, file_name)

        # 检查文件是否存在，避免覆盖
        if os.path.exists(file_path):
            print(f"版本文件 {file_path} 已存在。跳过保存。")
            return

        # 获取可序列化的配置字典
        config_data = self._to_serializable_dict()

        # 保存到 YAML 文件
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                yaml.dump(
                    config_data,
                    file,
                    Dumper=MyDumper,
                    default_flow_style=False,
                    allow_unicode=True,
                )
            print(f"配置快照已保存到: {file_path}")
        except Exception as e:
            warnings.warn(f"无法保存版本文件 {file_path}: {e}", RuntimeWarning)

    def load_version(self, version: str):
        """
        加载指定版本的配置快照，直接覆盖当前实例状态。
        此操作独立于当前的全局模式。
        文件名格式: {prefix}_{version}.yaml (基础 Config 为 default_{version}.yaml)。

        参数:
            version (str): 要加载的版本标识符。

        返回:
            bool: 如果加载成功则返回 True，否则返回 False。
        """
        prefix_part = self.prefix or 'default'
        file_name = f"{prefix_part}_{version}.yaml"
        file_path = os.path.join(Config.config_folder, file_name)

        print(f"加载版本快照: {file_path}")

        if not os.path.exists(file_path):
            warnings.warn(f"版本文件未找到: {file_path}", UserWarning)
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
                if yaml_data:
                    # 直接覆盖实例属性
                    self._override_attributes(self, yaml_data)
                    print(f"  - 实例状态已从 {os.path.basename(file_path)} 恢复。")
                    return True
                else:
                    # 处理空文件情况
                    print(f"  - 版本文件 {os.path.basename(file_path)} 为空，未做更改。")
                    return True # 认为加载空文件成功
        except yaml.YAMLError as e:
            warnings.warn(f"加载版本文件时出错 {file_path}: YAML 解析错误: {e}", UserWarning)
            return False
        except Exception as e:
            warnings.warn(f"加载版本文件时发生未知错误 {file_path}: {e}", UserWarning)
            return False

    def _to_serializable_dict(self) -> dict:
        """
        递归地将当前配置实例转换为可序列化的字典，排除状态属性并处理循环引用。
        """
        exclusions = {
            "prefix",
            "device",
            "db_path",
            "code_filter",
            "_initialized",
            "_loaded_mode", # 内部状态
            # 添加其他你不想保存的内部或非序列化属性
        }

        def clean_recursive(item, visited_ids: set):
            item_id = id(item)
            if item_id in visited_ids:
                return "<Circular Reference>"  # 检测到循环

            # 添加到访问集合
            visited_ids.add(item_id)

            cleaned_item = None # 初始化返回值
            try:
                if isinstance(item, dict):
                    # 处理字典
                    cleaned_item = {
                        k: clean_recursive(v, visited_ids)
                        for k, v in item.items()
                        if k not in exclusions
                    }
                elif hasattr(item, "__dict__") and not isinstance(item, type):
                    # 处理对象实例 (排除类对象本身)
                    cleaned_item = {
                        k: clean_recursive(v, visited_ids)
                        for k, v in vars(item).items()
                        if k not in exclusions and not k.startswith('__') # 排除魔法方法和 exclusions
                    }
                elif isinstance(item, list):
                    # 处理列表
                    cleaned_item = [clean_recursive(sub_item, visited_ids) for sub_item in item]
                elif isinstance(item, (str, int, float, bool, type(None))):
                    # 保留基本类型
                    cleaned_item = item
                elif isinstance(item, Enum):
                    # 存储枚举名称
                    cleaned_item = item.name
                else:
                    # 对未知类型发出警告并跳过
                    warnings.warn(
                        f"Skipping non-serializable type {type(item)} in config serialization."
                    )
                    cleaned_item = f"<Skipped Type: {type(item).__name__}>"
            finally:
                 # 完成对此对象的处理，从访问集合中移除，以便其他分支可以正确处理它
                 visited_ids.remove(item_id)

            return cleaned_item

        # 从实例的 __dict__ 开始清理，传入一个新的空集合用于跟踪访问过的 ID
        return clean_recursive(vars(self), set())


# ---------------------------------------------------------------------------
# 移除了 get_instance 方法，请使用 Config() 或 SubClass()
# 移除了 update_default_config, update_config, get_yaml_file (逻辑合并到 _load_hierarchical_config)
# 移除了对 temp/mode.txt 的读写 (现在由 set_mode 和 __init__ 处理)
# 添加了 save_version, load_version, _to_serializable_dict
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # --- 设置演示用配置文件夹 ---
    DEMO_CONFIG_FOLDER = os.path.join("tests", "config_demo")
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
        Config.mode = None
        mode_file_path = os.path.join("temp", "mode.txt")
        if os.path.exists(mode_file_path):
            os.remove(mode_file_path)
        print("\n--- 基础配置演示 --- (", end="")
        print(f"使用配置: {Config.config_folder}")

        # 用于存储上一个模式的配置，以便对比
        previous_cfg_dict = {}

        def capture_config_state(cfg):
            """捕获当前配置的关键值用于对比"""
            state = {
                "train.batch_size": cfg.train.batch_size,
                "data.window_size": cfg.data.window_size,
                "optimizer.lr": cfg.optimizer.lr,
                # 可以添加更多需要对比的配置项
            }
            return state

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

        def demonstrate_mode(mode_to_set: Mode, prev_cfg_dict: dict):
            print(f"\n--- 演示模式: {mode_to_set.name} ---")
            # Reset instance to force re-init and load files for the new mode in demo
            # Config._instance = None # 移除这行
            Config.set_mode(mode_to_set)  # 设置模式 (会写temp/mode.txt)
            print(f"设置模式为: {mode_to_set.name}")

            # 获取/创建基础 Config 单例 (使用 reload=True 确保加载新模式)
            print("获取 Config 实例 (将触发配置加载)... ")
            cfg = Config(reload=True) # <-- 添加 reload=True
            print("实例已获取。当前配置值:")

            print(f"  - 全局模式 (Config.mode): {Config.mode.name}")
            print(f"  - 实例前缀 (cfg.prefix): '{cfg.prefix}' (基础配置为空)")
            print(f"  - 设备 (cfg.device): {cfg.device}")
            print(f"  - 数据库路径 (cfg.db_path): {cfg.db_path} (根据模式变化)")
            print("\n  --- 通用配置节对比 ---")
            current_state = capture_config_state(cfg)
            compare_and_print(
                "train.batch_size",
                current_state["train.batch_size"],
                prev_cfg_dict,
                mode_to_set.name,
            )
            compare_and_print(
                "data.window_size",
                current_state["data.window_size"],
                prev_cfg_dict,
                mode_to_set.name,
            )
            compare_and_print(
                "optimizer.lr",
                current_state["optimizer.lr"],
                prev_cfg_dict,
                mode_to_set.name,
            )
            print("--- 模式演示结束 ---")
            return current_state  # 返回当前状态供下一次对比

        # 演示不同模式下的基础配置加载
        previous_cfg_dict = demonstrate_mode(Mode.TEST, previous_cfg_dict)
        previous_cfg_dict = demonstrate_mode(Mode.DEV, previous_cfg_dict)
        demonstrate_mode(Mode.PROD, previous_cfg_dict)

    finally:
        # --- 恢复原始配置文件夹路径 ---
        if use_demo_folder:
            Config.set_config_folder(original_config_folder)
            print(f"\n*** 演示结束，已恢复配置文件夹为: {Config.config_folder} ***")
        # --- 清理模式文件 ---
        mode_file_path = os.path.join("temp", "mode.txt")
        if os.path.exists(mode_file_path):
            os.remove(mode_file_path)
