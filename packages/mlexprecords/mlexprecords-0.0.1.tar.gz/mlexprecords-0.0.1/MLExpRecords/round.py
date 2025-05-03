"""
experiment_tracker/round.py - Round 类定义
"""

import time
from typing import Any, Dict, List, Optional

from MLExpRecords.entry import Entry

class Round:
    """
    轮次/任务层，管理训练轮次的参数与指标信息。
    """
    def __init__(self,
                 round_id: str,
                 start_time: Optional[float] = None,
                 end_time: Optional[float] = None,
                 train_params: Optional[Dict[str, Any]] = None,
                 train_metrics: Optional[Dict[str, float]] = None,
                 val_metrics: Optional[Dict[str, float]] = None,
                 model_weight_path: Optional[str] = None,
                 resource_usage: Optional[Dict[str, Any]] = None,
                 communication_info: Optional[Dict[str, Any]] = None,
                 status: Optional[str] = "success",
                 error_info: Optional[str] = None,
                 remarks: Optional[str] = None,
                 dataset_info: Optional[Dict[str, Any]] = None,
                 custom_data: Optional[Dict[str, Any]] = None):
        self.round_id = round_id
        self.start_time = start_time if start_time else 'None'
        self.end_time = end_time
        self.train_params = train_params if train_params else {}
        self.train_metrics = train_metrics if train_metrics else {}
        self.val_metrics = val_metrics if val_metrics else {}
        self.model_weight_path = model_weight_path
        self.resource_usage = resource_usage if resource_usage else {}
        self.communication_info = communication_info if communication_info else {}
        self.status = status
        self.error_info = error_info
        self.remarks = remarks
        self.dataset_info = dataset_info if dataset_info else {}
        self.custom_data = custom_data if custom_data else {}
        self.entries: List[Entry] = []

    @classmethod
    def create_with_auto(cls, round_id: str, **kwargs) -> "Round":
        """创建Round实例的工厂方法，自动填充默认值"""
        return cls(round_id=round_id, start_time=time.time(), **kwargs)

    def add_entry(self, entry: Entry):
        """添加一个Entry对象到当前轮次"""
        self.entries.append(entry)

    def get_entry(self, entry_id: str) -> Optional[Entry]:
        """根据ID获取条目对象"""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def to_dict(self) -> dict:
        """将Round对象转换为字典，用于序列化"""
        return {
            "round_id": self.round_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "train_params": self.train_params,
            "train_metrics": self.train_metrics,
            "val_metrics": self.val_metrics,
            "model_weight_path": self.model_weight_path,
            "resource_usage": self.resource_usage,
            "communication_info": self.communication_info,
            "status": self.status,
            "error_info": self.error_info,
            "remarks": self.remarks,
            "dataset_info": self.dataset_info,
            "custom_data": self.custom_data,
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Round":
        """从字典创建Round对象，用于反序列化"""
        from MLExpRecords.entry import Entry  # 避免循环导入

        inst = cls(
            round_id=data["round_id"],
            start_time=data.get("start_time", None),
            end_time=data.get("end_time", None),
            train_params=data.get("train_params", None),
            train_metrics=data.get("train_metrics", None),
            val_metrics=data.get("val_metrics", None),
            model_weight_path=data.get("model_weight_path", None),
            resource_usage=data.get("resource_usage", None),
            communication_info=data.get("communication_info", None),
            status=data.get("status", "success"),
            error_info=data.get("error_info", None),
            remarks=data.get("remarks", None),
            dataset_info=data.get("dataset_info", None),
            custom_data=data.get("custom_data", None),
        )
        entries_data = data.get("entries", [])
        for e_data in entries_data:
            inst.add_entry(Entry.from_dict(e_data))
        return inst