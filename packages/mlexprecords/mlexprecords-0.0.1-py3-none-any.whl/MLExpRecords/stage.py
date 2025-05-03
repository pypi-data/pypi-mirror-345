"""
experiment_tracker/stage.py - Stage 类定义
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
from .round import Round

class Stage:
    """
    阶段层，管理实验中的各项训练相关信息和轮次数据。
    包含Git版本详细信息、运行脚本路径、数据集信息、模型信息等。
    """
    def __init__(self,
                 stage_id: str,
                 description: Optional[str] = None,
                 local_env_versions: Optional[Dict[str, str]] = None,
                 git_info: Optional[Dict[str, Any]] = None,  # Git版本信息
                 script_path: Optional[str] = None,  # 运行脚本路径
                 dataset_info: Optional[Dict[str, Any]] = None,  # 数据集信息
                 model_info: Optional[Dict[str, Any]] = None,  # 模型信息
                 optimizer_info: Optional[Dict[str, Any]] = None,  # 优化器信息
                 hyperparameters: Optional[Dict[str, Any]] = None,  # 超参数信息
                 training_parameters: Optional[Dict[str, Any]] = None,  # 训练参数
                 remarks: Optional[str] = None):
        self.stage_id = stage_id
        self.description = description if description else ""
        self.local_env_versions = local_env_versions if local_env_versions else {}
        self.git_info = git_info if git_info else {}
        self.script_path = script_path
        self.dataset_info = dataset_info if dataset_info else {}
        self.model_info = model_info if model_info else {}
        self.optimizer_info = optimizer_info if optimizer_info else {}
        self.hyperparameters = hyperparameters if hyperparameters else {}
        self.training_parameters = training_parameters if training_parameters else {}
        self._get_stage_dir_name()
        self.remarks = remarks
        self.rounds: List[Round] = []

    @classmethod
    def create_with_auto(cls, stage_id: str, **kwargs) -> "Stage":
        """创建Stage实例的工厂方法"""
        return cls(stage_id=stage_id, **kwargs)

    def get_round(self, round_id: str) -> Optional[Round]:
        """根据ID获取轮次对象"""
        for r in self.rounds:
            if r.round_id == round_id:
                return r
        return None

    def add_round(self, round_obj: Round):
        """添加轮次对象到当前阶段"""
        self.rounds.append(round_obj)

    def to_dict(self) -> dict:
        """将Stage对象转换为字典，用于序列化"""
        return {
            "stage_id": self.stage_id,
            "description": self.description,
            "local_env_versions": self.local_env_versions,
            "git_info": self.git_info,
            "script_path": self.script_path,
            "dataset_info": self.dataset_info,
            "model_info": self.model_info,
            "optimizer_info": self.optimizer_info,
            "hyperparameters": self.hyperparameters,
            "training_parameters": self.training_parameters,
            "remarks": self.remarks,
            "rounds": [r.to_dict() for r in self.rounds],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Stage":
        """从字典创建Stage对象，用于反序列化"""
        from .round import Round  # 避免循环导入

        inst = cls(
            stage_id=data.get("stage_id", "main"),
            description=data.get("description", ""),
            local_env_versions=data.get("local_env_versions", None),
            git_info=data.get("git_info", None),
            script_path=data.get("script_path", None),
            dataset_info=data.get("dataset_info", None),
            model_info=data.get("model_info", None),
            optimizer_info=data.get("optimizer_info", None),
            hyperparameters=data.get("hyperparameters", None),
            training_parameters=data.get("training_parameters", None),
            remarks=data.get("remarks", None),
        )
        rounds_data = data.get("rounds", [])
        for r_data in rounds_data:
            inst.add_round(Round.from_dict(r_data))
        return inst


    def _get_stage_dir_name(self) -> str:
        """
        返回实验根目录路径，使用对用户友好的描述信息作为文件夹名，
        替换不合法文件名字符。

        路径格式：
            base_dir / friendly_experiment_name

        直接返回目录路径，不负责创建目录。
        """
        if not getattr(self,'dir_name',None):
            desc = getattr(self, "description", "default_stage").strip()
            desc_str = f'{self.model_info.get("name","None")}-{self.dataset_info.get("name","None")}-{desc}'
            desc_clean = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in desc_str)
            self.dir_name = desc_clean
        return self.dir_name