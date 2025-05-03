"""
experiment_tracker/experiment.py - Experiment 类定义
"""
import hashlib
import os
import time
import platform
import psutil
import subprocess
import concurrent.futures
import threading
import sys
import yaml
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from MLExpRecords.entry import Entry
from .round import Round
from .stage import Stage

class Experiment:
    """
    实验层，管理整个实验的全局配置和环境信息。
    只保存元数据（时间、硬件信息、ID、描述、Git版本等），
    训练相关信息保存在Stage中。
    """
    DEFAULT_BASE_DIR = Path("experiment_records")  # 默认保存根目录

    def __init__(self,
                 name: str = "未命名实验",  # 实验名称
                 description: Optional[str] = None,
                 stage_description: Optional[str] = None,  # 阶段描述
                 auto_save: bool = True,
                 auto_save_path: Optional[Path] = None,
                 env_dependency:bool = False,
                 verbose: bool = False):

        # 用户提供的基本信息
        self.name = name
        self.description = description if description else ""
        # 生成唯一实验ID
        self.experiment_id = self._generate_experiment_id()

        # 自动获取的环境信息（元数据）
        self.start_time = datetime.datetime.now()
        self.code_version = self._gather_code_version()
        self.env_config = self._gather_env_config()
        if env_dependency:
            self.dependencies = self._gather_dependencies()
        else:
            self.dependencies = []
        self._get_experiment_dir()
        # 异步保存配置
        self.auto_save = auto_save
        self._auto_save_path = auto_save_path
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._auto_save_lock = threading.Lock()
        self._auto_save_future = None

        # 日志配置
        self.verbose = verbose
        self._configure_logger()

        # 创建单一阶段并自动获取Git信息和脚本路径
        stage_desc = stage_description if stage_description else f"实验'{self.name}'的主阶段"
        self.hardware = self._get_hardware_info()
        self.stage = self._create_stage(stage_desc)

        self.status = "success"  # 状态，默认挂起

        # 新增：保存异常信息
        self._exception_info = None
        # 保存原始的异常钩子，防止覆盖
        self._original_excepthook = sys.excepthook

        # 安装自定义异常钩子
        self._install_exception_hook()

        # 初始化时自动保存一次
        if self.auto_save:
            self._auto_save()

        logger.info(f"创建实验 '{self.name}' (ID: {self.experiment_id})")

    def get_last_exception(self) -> Optional[dict]:
        """
        获取最近捕获的未处理异常信息，返回字典或None。
        """
        return self._exception_info

    def _install_exception_hook(self):
        """
        安装全局未捕获异常钩子，捕获未处理异常自动标记实验失败
        """

        def excepthook(exc_type, exc_value, exc_traceback):
            # 记录异常信息字符串
            import traceback
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

            self._exception_info = {
                "exception_type": str(exc_type),
                "exception_value": str(exc_value),
                "traceback": tb_str,
                "time": datetime.datetime.now().isoformat(),
            }

            # 自动标记失败
            self.status = "failure"

            logger.error(f"检测到未捕获异常，自动将实验状态标记为失败:\n{tb_str}")

            # 保存当前状态
            if self.auto_save:
                self._auto_save()

            # 继续调用之前的异常钩子以保证后续处理
            if self._original_excepthook:
                self._original_excepthook(exc_type, exc_value, exc_traceback)

        sys.excepthook = excepthook

    def _create_stage(self, description: str) -> Stage:
        """创建实验的单一阶段，自动获取Git信息和脚本路径"""
        # 获取Git版本信息
        git_info = self._get_git_info()

        # 获取当前运行脚本路径
        script_path = self._get_script_path()

        # 创建阶段
        stage = Stage(
            stage_id="main",
            description=description,
            git_info=git_info,
            script_path=script_path
        )

        logger.info(f"创建实验阶段并自动获取环境信息")
        return stage

    def set_training_config(self,
                            # PyTorch对象参数
                            dataset=None,
                            dataloader=None,
                            model=None,
                            optimizer=None,
                            criterion=None,
                            scheduler=None,

                            # 手动配置参数
                            dataset_info: Optional[Dict[str, Any]] = None,
                            model_info: Optional[Dict[str, Any]] = None,
                            optimizer_info: Optional[Dict[str, Any]] = None,
                            criterion_info: Optional[Dict[str, Any]] = None,
                            scheduler_info: Optional[Dict[str, Any]] = None,
                            hyperparameters: Optional[Dict[str, Any]] = None,
                            training_parameters: Optional[Dict[str, Any]] = None,

                            # 其他配置
                            **kwargs) -> None:
        """
        集成函数：设置训练配置信息，支持从PyTorch对象自动提取或手动传入

        参数:
            # PyTorch对象参数（自动提取配置）
            dataset: PyTorch数据集实例 (torch.utils.data.Dataset)
            dataloader: PyTorch数据加载器实例 (torch.utils.data.DataLoader)
            model: PyTorch模型实例 (nn.Module)
            optimizer: PyTorch优化器实例 (torch.optim.Optimizer)
            criterion: PyTorch损失函数 (nn.Module或callable)
            scheduler: PyTorch学习率调度器

            # 手动配置参数（直接使用）
            dataset_info: 数据集信息字典
            model_info: 模型信息字典
            optimizer_info: 优化器信息字典
            criterion_info: 损失函数信息字典
            scheduler_info: 学习率调度器信息字典
            hyperparameters: 超参数信息字典
            training_parameters: 训练参数信息字典

            **kwargs: 其他自定义配置
        """
        # ----- 提取数据集信息 -----
        auto_dataset_info = {}
        if dataset is not None:
            # 获取数据集类名
            auto_dataset_info["name"] = dataset.__class__.__name__
            # 获取数据集大小
            try:
                auto_dataset_info["size"] = len(dataset)
            except TypeError:
                auto_dataset_info["size"] = None

            # 尝试获取更多属性（如果存在）
            for attr in ["classes", "class_to_idx", "root", "transform", "targets"]:
                if hasattr(dataset, attr):
                    attr_value = getattr(dataset, attr)
                    # 如果是可调用对象（如transform），获取其字符串表示
                    if callable(attr_value) and not isinstance(attr_value, type):
                        attr_value = str(attr_value)
                    auto_dataset_info[attr] = attr_value

            # 尝试获取子数据集信息（如torchvision中的datasets.ImageFolder等）
            if hasattr(dataset, "dataset"):
                sub_dataset = dataset.dataset
                auto_dataset_info["subset"] = True
                auto_dataset_info["parent_dataset"] = sub_dataset.__class__.__name__
                try:
                    if hasattr(sub_dataset, "size"):
                        auto_dataset_info["parent_size"] = sub_dataset.size
                    elif hasattr(sub_dataset, "__len__"):
                        auto_dataset_info["parent_size"] = len(sub_dataset)
                except TypeError:
                    auto_dataset_info["parent_size"] = None

        # 如果提供了dataloader对象，提取相关信息
        if dataloader is not None:
            dataloader_info = {
                "batch_size": getattr(dataloader, "batch_size", None),
                "num_workers": getattr(dataloader, "num_workers", None),
                "pin_memory": getattr(dataloader, "pin_memory", None),
                "shuffle": getattr(dataloader, "shuffle", None),
                "sampler": str(dataloader.sampler.__class__.__name__) if getattr(dataloader, "sampler", None) else None,
                "drop_last": getattr(dataloader, "drop_last", None)
            }
            auto_dataset_info["dataloader"] = dataloader_info

        # 确定最终的dataset_info
        final_dataset_info = {}
        if dataset_info:
            final_dataset_info.update(dataset_info)
        if auto_dataset_info:
            for key, value in auto_dataset_info.items():
                if key not in final_dataset_info:
                    final_dataset_info[key] = value

        if final_dataset_info:
            self.stage.dataset_info = final_dataset_info

        # ----- 提取模型信息 -----
        auto_model_info = {}
        if model is not None:
            try:
                import torch
            except ModuleNotFoundError:
                logger.warning("torch is not installed, 跳过模型信息自动提取")
            else:
                # 获取模型类名和架构
                auto_model_info["name"] = model.__class__.__name__
                auto_model_info["architecture"] = str(model.__class__.__module__).split(".")[0]

                # 计算参数数量
                try:
                    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
                    total_params = sum(p.numel() for p in model.parameters())
                except Exception:
                    trainable_params = None
                    total_params = None
                auto_model_info["trainable_params"] = trainable_params
                auto_model_info["total_params"] = total_params

                # 获取设备信息
                try:
                    if next(model.parameters(), None) is not None:
                        auto_model_info["device"] = str(next(model.parameters()).device)
                except Exception:
                    auto_model_info["device"] = None

                # 尝试获取更多信息
                if hasattr(model, "training"):
                    auto_model_info["training_mode"] = model.training

                if hasattr(model, "pretrained"):
                    auto_model_info["pretrained"] = model.pretrained

                # 提取模型输入/输出大小（如果模型有这些信息）
                for attr in ["in_channels", "out_channels", "in_features", "out_features",
                             "embedding_dim", "num_layers", "num_classes"]:
                    if hasattr(model, attr):
                        auto_model_info[attr] = getattr(model, attr)

                # 尝试保存模型摘要
                try:
                    from torchinfo import summary
                    model_summary = summary(model, depth=2, verbose=0)
                    auto_model_info["summary"] = str(model_summary)
                except ImportError:
                    auto_model_info["summary"] = str(model)
                except Exception as e:
                    auto_model_info["summary"] = f"Failed to get model summary: {e}"

        # 确定最终的model_info（手动优先）
        final_model_info = {}
        if model_info:
            final_model_info.update(model_info)
        if auto_model_info:
            for key, value in auto_model_info.items():
                if key not in final_model_info:
                    final_model_info[key] = value

        if final_model_info:
            self.stage.model_info = final_model_info

        # ----- 提取优化器信息 -----
        auto_optimizer_info = {}
        if optimizer is not None:
            auto_optimizer_info["name"] = optimizer.__class__.__name__

            param_groups = []
            for i, group in enumerate(getattr(optimizer, "param_groups", [])):
                group_info = {}
                for k, v in group.items():
                    if k != "params":
                        group_info[k] = v
                param_groups.append(group_info)
            auto_optimizer_info["param_groups"] = param_groups

            try:
                params_count = sum(len(g.get("params", [])) for g in optimizer.param_groups)
            except Exception:
                params_count = None
            auto_optimizer_info["params_count"] = params_count

        # 提取scheduler信息
        auto_scheduler_info = {}
        if scheduler is not None:
            auto_scheduler_info["name"] = scheduler.__class__.__name__

            if hasattr(scheduler, "__dict__"):
                scheduler_params = {}
                for k, v in scheduler.__dict__.items():
                    if not k.startswith("_") and k != "optimizer":
                        # 处理特殊属性
                        if k == "milestones" and hasattr(v, "tolist"):
                            scheduler_params[k] = v.tolist()
                        else:
                            # 如果是torch类型tensorflow缺少 torch 判断，用导入封装判断
                            try:
                                import torch
                                is_torch_obj = str(type(v)).startswith("<class 'torch.")
                            except Exception:
                                is_torch_obj = False

                            if is_torch_obj:
                                if hasattr(v, "item"):
                                    try:
                                        scheduler_params[k] = v.item()
                                    except Exception:
                                        scheduler_params[k] = str(v)
                                elif hasattr(v, "tolist"):
                                    try:
                                        scheduler_params[k] = v.tolist()
                                    except Exception:
                                        scheduler_params[k] = str(v)
                                else:
                                    scheduler_params[k] = str(v)
                            else:
                                scheduler_params[k] = v
                auto_scheduler_info["params"] = scheduler_params

        # 将自动提取的scheduler_info合并到optimizer_info中
        if auto_scheduler_info:
            auto_optimizer_info["scheduler"] = auto_scheduler_info

        # 确定最终的optimizer_info（手动优先）
        final_optimizer_info = {}
        if optimizer_info:
            final_optimizer_info.update(optimizer_info)
        if auto_optimizer_info:
            for key, value in auto_optimizer_info.items():
                if key not in final_optimizer_info:
                    final_optimizer_info[key] = value

        # 单独处理scheduler_info
        if scheduler_info and "scheduler" not in final_optimizer_info:
            final_optimizer_info["scheduler"] = scheduler_info

        if final_optimizer_info:
            self.stage.optimizer_info = final_optimizer_info

        # ----- 提取损失函数信息 -----
        auto_criterion_info = {}
        if criterion is not None:
            if hasattr(criterion, "__class__"):
                auto_criterion_info["name"] = criterion.__class__.__name__
            else:
                try:
                    auto_criterion_info["name"] = criterion.__name__
                except AttributeError:
                    auto_criterion_info["name"] = str(criterion)

            if hasattr(criterion, "__dict__"):
                criterion_params = {}
                for k, v in criterion.__dict__.items():
                    if not k.startswith("_"):
                        criterion_params[k] = v
                auto_criterion_info["params"] = criterion_params

        # 确定最终的criterion_info（手动优先）
        final_criterion_info = {}
        if criterion_info:
            final_criterion_info.update(criterion_info)
        if auto_criterion_info:
            for key, value in auto_criterion_info.items():
                if key not in final_criterion_info:
                    final_criterion_info[key] = value

        if final_criterion_info:
            self.stage.criterion_info = final_criterion_info

        # ----- 保存超参数和训练参数信息 -----
        if hyperparameters:
            self.stage.hyperparameters = hyperparameters.copy()

        if training_parameters:
            self.stage.training_parameters = training_parameters.copy()

        # ----- 处理其他自定义配置 -----
        for key, value in kwargs.items():
            setattr(self.stage, key, value)

        logger.info(f"设置训练配置信息完成")
        if self.auto_save:
            self._auto_save()

    def _get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息（CPU、内存、GPU）"""
        try:
            import torch

            gpu_info = []
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    desc = {
                        "gpu_index": i,
                        "name": torch.cuda.get_device_name(i),
                        "total_memory_GB": round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 2)
                    }
                    gpu_info.append(desc)
            else:
                gpu_info = []

            cpu_count = psutil.cpu_count(logical=True)
            mem_total = round(psutil.virtual_memory().total / (1024**3), 2)

            hw_info = {
                "gpus": gpu_info,
                "cpu_count": cpu_count,
                "memory_total_GB": mem_total,
            }
            return hw_info
        except ImportError:
            cpu_count = psutil.cpu_count(logical=True)
            mem_total = round(psutil.virtual_memory().total / (1024**3), 2)
            return {
                "gpus": [],
                "cpu_count": cpu_count,
                "memory_total_GB": mem_total,
            }

    def _run_git_cmd(self, args: List[str]) -> Optional[str]:
        """运行Git命令并返回输出结果"""
        try:
            return subprocess.check_output(["git"] + args, stderr=subprocess.STDOUT).decode().strip()
        except Exception as e:
            logger.debug(f"运行Git命令失败: {e}")
            return None

    def _get_git_info(self) -> Dict[str, Any]:
        """
        获取详细的Git版本信息，包括：
        - commit_hash: 当前提交的哈希值
        - branch: 当前分支名
        - tag: 当前标签（如果有）
        - dirty: 是否有未提交的变更
        - diff: 未提交变更的差异内容
        """
        git_info = {}
        # 获取commit hash
        git_info["commit_hash"] = self._run_git_cmd(["rev-parse", "HEAD"])
        # 获取当前分支
        git_info["branch"] = self._run_git_cmd(["rev-parse", "--abbrev-ref", "HEAD"])
        # 获取当前标签（如果直接在标签上）
        git_info["tag"] = self._run_git_cmd(["describe", "--tags", "--exact-match"])
        # 检查是否有未提交的变更（工作目录是否干净）
        dirty_status = self._run_git_cmd(["status", "--porcelain"])
        git_info["dirty"] = bool(dirty_status)
        return git_info

    def _get_script_path(self) -> str:
        """获取当前运行脚本的绝对路径"""
        try:
            # 获取当前执行的脚本文件路径
            script_path = os.path.abspath(sys.argv[0])
            return script_path
        except Exception as e:
            logger.debug(f"获取脚本路径失败: {e}")
            return ""

    def _configure_logger(self):
        """配置日志记录器"""
        logger.remove()
        logger.add("experiment_log.log", rotation="10 MB", retention="10 days", level="DEBUG", encoding="utf-8")
        if self.verbose:
            logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO", colorize=True)

    def _get_experiment_dir(self) -> Path:
        """
        返回实验根目录路径，使用对用户友好的描述信息作为文件夹名，
        替换不合法文件名字符。

        路径格式：
            base_dir / friendly_experiment_name

        直接返回目录路径，不负责创建目录。
        """
        if not getattr(self, "experiment_dir", None):
            base_dir = Path.cwd() / self.DEFAULT_BASE_DIR

            desc = getattr(self, "name", "experiment").strip()
            desc_clean = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in desc)

            self.experiment_dir = base_dir / desc_clean

        return self.experiment_dir

    def _auto_save(self):
        """
        异步触发自动保存，提交后台线程执行写文件动作。
        如果前一次写入任务还没完成，等待其完成后重新提交，确保最新状态保存。

        保存路径规则：
            - 最外层为 experiment_id 文件夹
            - 第二层为 stage_id 文件夹
            - 相同 experiment_id 和 stage_id 的数据保存到相同目录
            - 保存的yaml文件名自动避免覆盖，若存在则增加数字后缀防止覆盖
        保存内容：
            - 保存当前对象的全部内容（调用 self.to_dict()）
        """

        def save_task():
            try:
                # 根目录和实验目录
                experiment_dir = self._get_experiment_dir()
                experiment_dir.mkdir(parents=True, exist_ok=True)

                # 获取stage_id字符串，若无则用默认，确保有目录
                stage_dir = experiment_dir / self.stage._get_stage_dir_name()
                stage_dir.mkdir(parents=True, exist_ok=True)

                # 生成带时间戳和描述的文件名，避免覆盖
                timestamp =self.start_time.strftime("%Y%m%d_%H%M%S")
                base_file_name = f"{timestamp}.yaml"
                save_path = stage_dir / base_file_name

                # 写入yaml文件
                with save_path.open("w", encoding="utf-8") as f:
                    yaml.safe_dump(self.to_dict(), f, allow_unicode=True, sort_keys=False)

                logger.info(
                    f"Experiment '{self.name}' (ID: {self.experiment_id}, Stage: {self.stage._get_stage_dir_name()}) 异步自动保存到 YAML 文件: {save_path}")

            except Exception as e:
                logger.error(f"自动保存 Experiment '{self.name}' 失败: {e}")

        with self._auto_save_lock:
            if self._auto_save_future is not None and not self._auto_save_future.done():
                try:
                    self._auto_save_future.result()  # 等待完成，防止同时并发写文件
                except Exception as e:
                    logger.error(f"等待前一次保存任务完成时出错: {e}")

            self._auto_save_future = self._executor.submit(save_task)

    def _generate_experiment_id(self) -> str:
        """
        根据描述信息生成唯一且稳定的实验ID。
        相同描述信息生成的ID保持一致，格式示例：desc_{hash}。

        参数:
            description: 实验描述字符串

        返回:
            生成的实验ID字符串
        """
        # 使用描述信息的hash作为唯一标识，截取前8位
        description = self.name if self.name else 'default_exp'
        desc_hash = hashlib.md5(description.encode('utf-8')).hexdigest()[:8]
        # 格式化描述去除空白并限制长度
        desc_clean = ''.join(c if c.isalnum() else '_' for c in description.strip())[:20]
        experiment_id = f"{desc_clean}_{desc_hash}"
        return experiment_id

    def set_verbose(self, verbose: bool):
        """动态控制是否打印日志到控制台"""
        if self.verbose == verbose:
            return
        self.verbose = verbose
        self._configure_logger()
        logger.info(f"Set verbose to {verbose}")

    def _gather_code_version(self) -> Dict[str, Any]:
        """收集代码版本信息"""
        commit_hash = self._run_git_cmd(["rev-parse", "HEAD"])
        branch = self._run_git_cmd(["rev-parse", "--abbrev-ref", "HEAD"])
        tag = self._run_git_cmd(["describe", "--tags", "--exact-match"])
        dirty = self._run_git_cmd(["status", "--porcelain"])
        is_dirty = bool(dirty)
        return {
            "commit_hash": commit_hash,
            "branch": branch,
            "tag": tag,
            "dirty": is_dirty,
        }

    def _gather_env_config(self) -> Dict[str, Any]:
        """收集环境配置信息"""
        import importlib.util

        torch_spec = importlib.util.find_spec("torch")
        cuda_available = False
        gpu_count = 0
        gpus = []
        torch_version = None
        if torch_spec is not None:
            import torch

            cuda_available = torch.cuda.is_available()
            gpu_count = torch.cuda.device_count() if cuda_available else 0
            if cuda_available:
                for i in range(gpu_count):
                    gpus.append(torch.cuda.get_device_name(i))
            torch_version = torch.__version__

        env = {
            "python_version": platform.python_version(),
            "os": platform.platform(),
            "cpu_count": psutil.cpu_count(logical=True),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "cuda_available": cuda_available,
            "gpu_count": gpu_count,
            "gpu_names": gpus,
            "torch_version": torch_version,
        }
        return env

    def _gather_dependencies(self) -> Dict[str, str]:
        """收集依赖包信息"""
        try:
            result = subprocess.check_output(["pip", "freeze"], stderr=subprocess.STDOUT).decode()
            deps = {}
            for line in result.splitlines():
                if "==" in line:
                    pkg, ver = line.split("==", 1)
                    deps[pkg.lower()] = ver
            return deps
        except Exception:
            return {}

    def log_epoch(self, epoch: int,
                 train_metrics: Optional[Dict[str, float]] = None,
                 val_metrics: Optional[Dict[str, float]] = None,
                 dataset_info: Optional[Dict[str, Any]] = None,
                 model_path: Optional[str] = None,
                 message: Optional[str] = None,
                 **kwargs) -> Round:
        """
        记录一个训练轮次(epoch)，使用epoch作为轮次ID

        参数:
            epoch: 轮次编号
            train_metrics: 训练指标，如 {'loss': 0.123, 'accuracy': 0.98}
            val_metrics: 验证指标，如 {'val_loss': 0.234, 'val_accuracy': 0.96}
            dataset_info: 数据集信息，如 {'name': 'CIFAR-10', 'split': 'train', 'samples': 50000}
            model_path: 模型保存路径
            message: 附加消息
            **kwargs: 其他参数，会保存到custom_data中

        返回:
            创建或更新的轮次对象
        """
        # 使用epoch作为round_id
        round_id = f"epoch_{epoch}"

        # 查找已存在的轮次或创建新轮次
        round_obj = self.stage.get_round(round_id)
        if round_obj is None:
            # 构建轮次参数
            round_params = {}
            if dataset_info:
                round_params['dataset_info'] = dataset_info

            # 创建新的轮次
            round_obj = Round.create_with_auto(
                round_id=round_id,
                **round_params
            )
            self.stage.add_round(round_obj)
            logger.info(f"创建新轮次 '{round_id}'")

        # 更新轮次数据
        if train_metrics:
            round_obj.train_metrics = train_metrics
        if val_metrics:
            round_obj.val_metrics = val_metrics
        if model_path:
            round_obj.model_weight_path = model_path
        if dataset_info and not round_obj.dataset_info:
            round_obj.dataset_info = dataset_info

        # 处理其他自定义参数
        if kwargs:
            if not round_obj.custom_data:
                round_obj.custom_data = {}
            round_obj.custom_data.update(kwargs)

        # 设置结束时间
        round_obj.end_time = time.time()

        logger.info(f"记录轮次 '{round_id}'")
        if self.auto_save:
            self._auto_save()

        return round_obj

    def log_batch(self, epoch: int, batch: int,
                 metrics: Optional[Dict[str, float]] = None,
                 images: Optional[Dict[str, str]] = None,
                 message: Optional[str] = None,
                 **kwargs) -> Entry:
        """
        记录一个训练批次，关联到对应epoch

        参数:
            epoch: 轮次编号，自动关联到对应的epoch轮次
            batch: 批次编号
            metrics: 批次度量值字典，如 {'loss': 0.123, 'accuracy': 0.96}
            images: 图像路径字典，如 {'input': '/path/to/input.png', 'output': '/path/to/output.png'}
            message: 附加消息
            **kwargs: 其他参数，会保存到custom_data中

        返回:
            创建的条目对象
        """
        # 生成轮次ID和条目ID
        round_id = f"epoch_{epoch}"
        entry_id = f"batch_{batch}"

        # 确保对应的轮次存在
        round_obj = self.stage.get_round(round_id)
        if round_obj is None:
            # 如果轮次不存在，自动创建
            round_obj = Round.create_with_auto(round_id=round_id)
            self.stage.add_round(round_obj)
            logger.info(f"自动创建轮次 '{round_id}' 用于批次记录")

        # 构建条目参数
        entry_params = {}
        if metrics:
            entry_params['scalar_metrics'] = metrics
        if images:
            entry_params['images'] = images
        if message:
            entry_params['logs'] = [message]

        # 处理其他自定义参数
        custom_data = kwargs.copy()
        custom_data['batch'] = batch  # 添加批次编号到自定义数据
        entry_params['custom_data'] = custom_data

        # 创建并添加条目
        entry = Entry.create_with_auto(entry_id=entry_id, **entry_params)
        round_obj.add_entry(entry)

        logger.info(f"记录批次 '{entry_id}' 到轮次 '{round_id}'")
        if self.auto_save:
            self._auto_save()

        return entry

    def log_metric(self, name: str, value: float, epoch: int,
                  batch: Optional[int] = None, message: Optional[str] = None) -> Entry:
        """
        记录单个度量指标，关联到指定epoch和可选的batch

        参数:
            name: 指标名称
            value: 指标值
            epoch: 轮次编号
            batch: 批次编号，如果提供则关联到特定批次，否则只关联到轮次
            message: 附加消息

        返回:
            创建的条目对象
        """
        # 如果指定了batch，使用log_batch
        if batch is not None:
            return self.log_batch(
                epoch=epoch,
                batch=batch,
                metrics={name: value},
                message=message
            )

        # 否则直接关联到epoch轮次
        round_id = f"epoch_{epoch}"
        entry_id = f"metric_{name}_{int(time.time() * 1000)}"

        # 确保轮次存在
        round_obj = self.stage.get_round(round_id)
        if round_obj is None:
            round_obj = Round.create_with_auto(round_id=round_id)
            self.stage.add_round(round_obj)
            logger.info(f"自动创建轮次 '{round_id}' 用于指标记录")

        # 创建并添加条目
        entry = Entry.create_with_auto(
            entry_id=entry_id,
            scalar_metrics={name: value},
            logs=[message] if message else None,
            custom_data={'metric_name': name}
        )
        round_obj.add_entry(entry)

        logger.info(f"记录指标 '{name}': {value} 到轮次 '{round_id}'")
        if self.auto_save:
            self._auto_save()

        return entry

    def log_image(self, name: str, path: str, epoch: int,
                 batch: Optional[int] = None, message: Optional[str] = None) -> Entry:
        """
        记录图像，关联到指定epoch和可选的batch

        参数:
            name: 图像名称
            path: 图像路径
            epoch: 轮次编号，必须指定以关联到特定训练阶段
            batch: 批次编号，如果提供则关联到特定批次，否则只关联到轮次
            message: 附加消息

        返回:
            创建的条目对象
        """
        # 如果指定了batch，使用log_batch
        if batch is not None:
            return self.log_batch(
                epoch=epoch,
                batch=batch,
                images={name: path},
                message=message
            )

        # 否则直接关联到epoch轮次
        round_id = f"epoch_{epoch}"
        entry_id = f"image_{name}_{int(time.time() * 1000)}"

        # 确保轮次存在
        round_obj = self.stage.get_round(round_id)
        if round_obj is None:
            round_obj = Round.create_with_auto(round_id=round_id)
            self.stage.add_round(round_obj)
            logger.info(f"自动创建轮次 '{round_id}' 用于图像记录")

        # 创建并添加条目
        entry = Entry.create_with_auto(
            entry_id=entry_id,
            images={name: path},
            logs=[message] if message else None,
            custom_data={'image_name': name}
        )
        round_obj.add_entry(entry)

        logger.info(f"记录图像 '{name}' 到轮次 '{round_id}'")
        if self.auto_save:
            self._auto_save()

        return entry

    def to_dict(self) -> dict:
        """将实验对象转换为字典，用于序列化"""
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "description": self.description,
            "hardware": self.hardware,
            "start_time": self.start_time,
            "code_version": self.code_version,
            "env_config": self.env_config,
            "dependencies": self.dependencies,
            "stage": self.stage.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Experiment":
        """从字典创建实验对象，用于反序列化"""
        inst = cls(
            name=data.get("name", "未命名实验"),
            description=data.get("description", None),
            auto_save=False,  # 加载时不自动保存
        )
        # 恢复原始ID和时间戳
        inst.experiment_id = data.get("experiment_id", inst.experiment_id)
        inst.start_time = data.get("start_time", inst.start_time)

        # 恢复配置信息
        inst.code_version = data.get("code_version", {})
        inst.env_config = data.get("env_config", {})
        inst.dependencies = data.get("dependencies", {})

        # 恢复阶段信息
        if "stage" in data:
            inst.stage = Stage.from_dict(data["stage"])

        return inst

    @classmethod
    def load_experiment_from_yaml(cls, yaml_path: Path):
        """
        从指定路径的yaml文件加载实验对象（类实例）。

        参数:
            cls: 当前experiment类，用于构造实例
            yaml_path: yaml文件的完整路径，Path对象或字符串

        返回:
            实例化的experiment对象，失败返回None
        """
        try:
            yaml_path = Path(yaml_path)
            if not yaml_path.is_file():
                logger.error(f"指定的yaml文件不存在: {yaml_path}")
                return None

            with yaml_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            exp_instance = cls()
            if hasattr(exp_instance, "from_dict") and callable(getattr(exp_instance, "from_dict")):
                exp_instance = exp_instance.from_dict(data)
            else:
                exp_instance.__dict__.update(data)

            logger.info(f"成功从文件加载 Experiment 实例: {yaml_path}")
            return exp_instance

        except Exception as e:
            logger.error(f"从文件加载 Experiment 失败: {e}")
            return None