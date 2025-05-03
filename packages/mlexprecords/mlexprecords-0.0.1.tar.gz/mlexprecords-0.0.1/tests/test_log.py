import unittest
from pathlib import Path
import time
import shutil

from MLExpRecords.experiment import Experiment


# 假设你的 Experiment 类路径正确，导入它
# from experiment_tracker.experiment import Experiment

# 用纯Python模拟Dataset和Model等结构，仅提供必要的属性
class DummyDataset:
    def __init__(self, size=10):
        self.size = size
    def __len__(self):
        return self.size
    # 模拟部分属性
    classes = ["class0", "class1"]
    class_to_idx = {"class0": 0, "class1": 1}

class DummyModel:
    def __init__(self):
        self.name = "DummyModel"
        self.param_count = 12345
    def __class__(self):
        return self.__class__
    # 模拟必要属性
    def __class__(self):
        class DummyCls:
            __name__ = "DummyModelClass"
            __module__ = "dummy_module"
        return DummyCls

class DummyOptimizer:
    def __init__(self):
        self.param_groups = [
            {"lr": 0.01, "momentum": 0.9, "params": [1, 2, 3]},
            {"lr": 0.001, "params": [4, 5]}
        ]
    def __class__(self):
        class DummyCls:
            __name__ = "DummyOptimizer"
        return DummyCls

class DummyCriterion:
    def __init__(self):
        self.some_param = 42
    def __class__(self):
        class DummyCls:
            __name__ = "DummyCriterion"
        return DummyCls

class DummyScheduler:
    def __init__(self):
        self.step_size = 5
        self.gamma = 0.1
    def __class__(self):
        class DummyCls:
            __name__ = "DummyScheduler"
        return DummyCls

class TestExperimentNoTorch(unittest.TestCase):
    def setUp(self):
        self.exp = Experiment(
            name="NoTorchTest",
            description="Testing Experiment class without torch",
            auto_save=True,
            verbose=False
        )
        self.dataset = DummyDataset(size=8)
        self.model = DummyModel()
        self.optimizer = DummyOptimizer()
        self.criterion = DummyCriterion()
        self.scheduler = DummyScheduler()

        # 这里我们不传dataloader，因为无torch
        self.exp.set_training_config(
            dataset=self.dataset,
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion,
            scheduler=self.scheduler,
            hyperparameters={"lr": 0.01},
            training_parameters={"epochs": 1}
        )

    def test_logging(self):
        # 模拟一个epoch, 写入部分数据
        for epoch in range(1, 2):
            # 记录一个epoch情况
            round_obj = self.exp.log_epoch(
                epoch=epoch,
                train_metrics={"loss": 0.123},
                val_metrics={"val_loss": 0.110},
                message="Epoch 1 completed"
            )
            self.assertIsNotNone(round_obj)
            self.assertIn("loss", round_obj.train_metrics)

            # 记录批次
            for batch in range(1, 4):
                entry = self.exp.log_batch(
                    epoch=epoch,
                    batch=batch,
                    metrics={"batch_loss": 0.1 * batch},
                    message=f"batch {batch} processed"
                )
                self.assertIsNotNone(entry)
                self.assertIn("batch_loss", entry.scalar_metrics)

        # 等待自动保存完成
        time.sleep(1)

        # 验证yaml文件存在
        base_dir = Path.cwd() / self.exp.DEFAULT_BASE_DIR
        exp_dir = base_dir / self.exp._get_experiment_dir() /self.exp.stage._get_stage_dir_name()
        yaml_path = exp_dir/f'{self.exp.start_time.strftime("%Y%m%d_%H%M%S")}.yaml'
        self.assertTrue(yaml_path.exists())

        # 从yaml加载实验
        loaded_exp = Experiment.load_experiment_from_yaml(yaml_path)
        self.assertEqual(loaded_exp.name, self.exp.name)
        self.assertEqual(len(loaded_exp.stage.rounds), len(self.exp.stage.rounds))

    # def tearDown(self):
    #     # 清理保存目录
    #     base_dir = Path.cwd() / self.exp.DEFAULT_BASE_DIR
    #     if base_dir.exists():
    #         shutil.rmtree(base_dir)

if __name__ == "__main__":
    unittest.main()