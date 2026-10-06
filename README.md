# AI 浪潮下的技能需求变迁：基于招聘文本的实证分析（skill-shift-analysis）

## 项目简介

本项目以公开招聘文本为研究对象，考察人工智能（AI）技术浪潮对劳动力市场技能需求结构的影响。通过对中国在线招聘平台公开数据集（合规获取）的文本挖掘与词频统计，回答技能需求随时间的变迁规律，并比较不同资历层级岗位之间的分化。

本项目为数字社会科学方向本科研究项目（硕士申请作品集），当前处于**第一阶段：项目搭建与数据获取**。

## 研究问题

1. 招聘岗位描述中「AI 相关技能」的词频随时间如何变化？
2. 初级岗位与高级岗位的技能要求变化是否出现分化？
3. 哪些传统技能在「贬值」、哪些新兴技能在「升值」？

## 数据来源

- **合规原则**：仅使用公开授权的研究数据集（如 Kaggle 公开数据集、学术机构发布的数据），**不爬取** BOSS 直聘、前程无忧、智联招聘等商业招聘平台（其服务条款禁止爬取，且存在法律风险）。
- **已获取数据**（详见 `docs/data_profile.md`）：

  | 时间点 | 来源 | 样本量 |
  |---|---|---|
  | 2017 年中 / 2018-05 | GitHub 公开仓库（拉勾网历史数据） | 5,031 + 431 |
  | 2020.7-9 | Kaggle `cdcqxaitjobmarket`（成渝西安，CC0） | 519 |
  | 2023 | Kaggle `nc2023`（MIT） | 437 |
  | 2025-02 ~ 2025-08 | Kaggle `it-position-info`（全国 IT 岗位） | 110,176 |

- `data/raw/` 下存放原始数据，**不做任何修改**；所有清洗产物写入 `data/processed/`。

## 目录结构

```
skill-shift-analysis/
├── README.md                # 项目说明（本文件）
├── requirements.txt         # Python 依赖清单
├── data/
│   ├── raw/                 # 原始数据（只读，不修改）
│   └── processed/           # 清洗/加工后的数据
├── notebooks/               # 探索性分析与可复现实验 notebook
├── src/                     # 可复用的 Python 模块与脚本
├── figures/                 # 输出的图表
└── docs/                    # 研究设计、数据探查报告等文档
```

## 环境搭建

```bash
cd skill-shift-analysis
python -m venv .venv
# Windows (Git Bash): source .venv/Scripts/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 进度记录

- [x] 第一阶段：项目搭建与数据获取（已完成：2017/2018 基线数据 + 探查报告 + 研究设计）
- [x] 数据补充：Kaggle 2020 / 2023 / 2025 三个时间点的数据集（已完成，见 notebook 02）
- [x] 第二阶段：文本清洗与技能词典构建（已完成：词典 v1.0 冻结 + 116,594 条岗位×技能矩阵，见 notebook 03）
- [x] 第三阶段：词频时间序列与岗位层级分化分析（已完成：RQ1 趋势 + RQ2 层级分化与薪资溢价回归 + RQ3 技能贬升值双证据，见 notebook 04/05/06）
- [x] 第四阶段：结果整合与研究报告（已完成：`docs/research_report.md` + Word 版 `docs/AI浪潮下的技能需求变迁_研究报告.docx`）

## 最终交付物

- **研究报告**：`docs/research_report.md`（Markdown 主稿）/ `docs/AI浪潮下的技能需求变迁_研究报告.docx`（Word 版，已通过结构校验）
- **分析流水线**：`notebooks/01`（数据探查）→ `02`（Kaggle 数据）→ `03`（词典与矩阵）→ `04`（RQ1 趋势）→ `05`（RQ2 分化）→ `06`（RQ3 贬升值）
- **图表**：`figures/01`–`15` 共 15 张
