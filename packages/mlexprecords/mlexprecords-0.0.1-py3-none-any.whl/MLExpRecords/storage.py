from pathlib import Path
import yaml
from typing import Optional
from core import Experiment

DEFAULT_BASE_DIR = Path("experiment_records")  # 相对路径，默认根目录

def save_experiment_to_yaml(exp: Experiment, file_path: Optional[Path] = None):
    """
    保存实验对象为yaml文件。
    如果未传入 file_path，则自动保存到 当前工作目录/experiment_records/实验ID/experiment_info.yaml

    :param exp: Experiment 实例
    :param file_path: 目标文件完整路径（Path或字符串）。若为None，则使用默认路径。
    """
    if file_path is None:
        base_dir = Path.cwd() / DEFAULT_BASE_DIR
        experiment_dir = base_dir / exp.experiment_id
        experiment_dir.mkdir(parents=True, exist_ok=True)
        file_path = experiment_dir / "experiment_info.yaml"
    else:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(exp.to_dict(), f, allow_unicode=True, sort_keys=False)

def load_experiment_from_yaml(file_path: Optional[Path] = None, experiment_id: Optional[str] = None) -> Experiment:
    """
    从yaml文件加载实验对象。
    若未传入 file_path，则必须传入 experiment_id，自动加载默认路径 ./experiment_records/{experiment_id}/experiment_info.yaml

    :param file_path: 目标yaml文件完整路径（Path或字符串）
    :param experiment_id: 实验ID，若file_path未传入则必须指定，用于定位默认文件路径
    :return: Experiment实例
    """
    if file_path is None:
        if not experiment_id:
            raise ValueError("必须指定 experiment_id，或传入 file_path")
        file_path = Path.cwd() / DEFAULT_BASE_DIR / experiment_id / "experiment_info.yaml"
    else:
        file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"Yaml file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return Experiment.from_dict(data)