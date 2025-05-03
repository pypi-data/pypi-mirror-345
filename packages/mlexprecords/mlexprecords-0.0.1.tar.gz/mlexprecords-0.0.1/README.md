# Experiment 类文档

## 概述

`Experiment` 类是实验跟踪系统的核心类，用于管理整个实验的全局配置和环境信息。

## 功能特性

### 1. 初始化方法

```python
def __init__(self,
             name: str = "未命名实验",
             description: Optional[str] = None,
             stage_description: Optional[str] = None,
             auto_save: bool = True,
             auto_save_path: Optional[Path] = None,
             env_dependency: bool = False,
             verbose: bool = False):
```

**参数说明：**
- `name`: 实验名称
- `description`: 实验描述
- `stage_description`: 阶段描述
- `auto_save`: 是否自动保存
- `auto_save_path`: 自定义保存路径
- `env_dependency`: 是否收集依赖信息
- `verbose`: 是否显示详细日志

### 2. 训练配置设置

```python
def set_training_config(self,
                       dataset=None,
                       dataloader=None,
                       model=None,
                       optimizer=None,
                       criterion=None,
                       scheduler=None,
                       dataset_info: Optional[Dict[str, Any]] = None,
                       model_info: Optional[Dict[str, Any]] = None,
                       optimizer_info: Optional[Dict[str, Any]] = None,
                       criterion_info: Optional[Dict[str, Any]] = None,
                       scheduler_info: Optional[Dict[str, Any]] = None,
                       hyperparameters: Optional[Dict[str, Any]] = None,
                       training_parameters: Optional[Dict[str, Any]] = None,
                       **kwargs):
```

### 3. 日志记录方法

```python
记录训练轮次
def log_epoch(self, epoch: int,
             train_metrics: Optional[Dict[str, float]] = None,
             val_metrics: Optional[Dict[str, float]] = None,
             dataset_info: Optional[Dict[str, Any]] = None,
             model_path: Optional[str] = None,
             message: Optional[str] = None,
             **kwargs) -> Round:

记录训练批次
def log_batch(self, epoch: int, batch: int,
             metrics: Optional[Dict[str, float]] = None,
             images: Optional[Dict[str, str]] = None,
             message: Optional[str] = None,
             **kwargs) -> Entry:

记录指标
def log_metric(self, name: str, value: float, epoch: int,
              batch: Optional[int] = None, message: Optional[str] = None) -> Entry:

记录图像
def log_image(self, name: str, path: str, epoch: int,
             batch: Optional[int] = None, message: Optional[str] = None) -> Entry:
```

### 4. 序列化方法

```python
转换为字典
def to_dict(self) -> dict:

从字典创建实例
@classmethod
def from_dict(cls, data: dict) -> "Experiment":

从YAML文件加载
@classmethod
def load_experiment_from_yaml(cls, yaml_path: Path):
```

## 使用示例

### 基础用法

```python
from experiment_tracker.experiment import Experiment

初始化实验
exp = Experiment(name="MNIST分类实验", description="测试不同模型在MNIST上的表现")

设置训练配置
exp.set_training_config(
    dataset=train_dataset,
    dataloader=train_loader,
    model=model,
    optimizer=optimizer,
    criterion=criterion
)

记录训练过程
for epoch in range(epochs):
    # ... 训练代码 ...
    exp.log_epoch(
        epoch=epoch,
        train_metrics={"loss": train_loss, "accuracy": train_acc},
        val_metrics={"val_loss": val_loss, "val_accuracy": val_acc}
    )
```

## 数据存储结构

```
experiment_records/
    ├── 实验名称_哈希ID/
    │   ├── stage_主阶段ID/
    │   │   ├── 时间戳.yaml
    │   │   └── ...
    │   └── ...
    └── ...
```

## 注意事项

1. 自动保存功能默认开启
2. 实验ID基于实验名称生成
