"""
experiment_tracker/entry.py - Entry 类定义
"""

import time
from typing import Any, Dict, List, Optional

class Entry:
    """
    记录条目层，管理轮次中的细粒度记录，如batch指标、示例图、日志、事件标记等。
    """
    def __init__(self,
                 entry_id: str,
                 timestamp: Optional[float] = None,
                 scalar_metrics: Optional[Dict[str, float]] = None,
                 images: Optional[Dict[str, str]] = None,
                 model_snapshots: Optional[List[str]] = None,
                 logs: Optional[List[str]] = None,
                 custom_data: Optional[Any] = None,
                 event_markers: Optional[List[str]] = None,
                 eval_results: Optional[Dict[str, Any]] = None):
        self.entry_id = entry_id
        self.timestamp = timestamp if timestamp else time.time()
        self.scalar_metrics = scalar_metrics if scalar_metrics else {}
        self.images = images if images else {}
        self.model_snapshots = model_snapshots if model_snapshots else []
        self.logs = logs if logs else []
        self.custom_data = custom_data
        self.event_markers = event_markers if event_markers else []
        self.eval_results = eval_results if eval_results else {}

    @classmethod
    def create_with_auto(cls, entry_id: str, **kwargs):
        """创建Entry实例的工厂方法，自动填充默认值"""
        return cls(entry_id=entry_id, **kwargs)

    def to_dict(self) -> dict:
        """将Entry对象转换为字典，用于序列化"""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "scalar_metrics": self.scalar_metrics,
            "images": self.images,
            "model_snapshots": self.model_snapshots,
            "logs": self.logs,
            "custom_data": self.custom_data,
            "event_markers": self.event_markers,
            "eval_results": self.eval_results,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Entry":
        """从字典创建Entry对象，用于反序列化"""
        return cls(
            entry_id=data["entry_id"],
            timestamp=data.get("timestamp", None),
            scalar_metrics=data.get("scalar_metrics", None),
            images=data.get("images", None),
            model_snapshots=data.get("model_snapshots", None),
            logs=data.get("logs", None),
            custom_data=data.get("custom_data", None),
            event_markers=data.get("event_markers", None),
            eval_results=data.get("eval_results", None),
        )