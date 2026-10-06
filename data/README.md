# 数据目录说明

本仓库**不包含数据文件**（许可限制与体积考虑），按以下步骤即可完整复现：

1. **2017/2018 基线数据**（GitHub 公开仓库，无需登录）：
   ```bash
   python src/download_data.py
   ```
2. **Kaggle 数据**（2020 / 2023 / 2025，需 Kaggle 账号与 API 令牌）：
   按 `docs/data_acquisition_plan.md` 中的数据集清单下载，放入 `data/raw/kaggle/` 对应子目录。
3. **标准化与技能矩阵**：
   ```bash
   python src/prepare_kaggle_data.py
   python src/build_skill_matrix.py
   ```

各数据集的来源、时间范围、字段与许可见 `docs/data_profile.md`。
