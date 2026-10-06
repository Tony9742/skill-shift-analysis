# -*- coding: utf-8 -*-
"""
把 Kaggle 下载的原始数据标准化为统一结构，写入 data/processed/。

涉及数据集（均位于 data/raw/kaggle/，原始文件不修改）：
  1. it-position-info/it.csv        2024-04 ~ 2025-08 全国 IT 岗位（约 11 万行，无表头）
  2. nc2023/nc2023.xlsx             2023 年行业招聘信息（437 行，含职位描述）
  3. cdcqxaitjobmarket/data1.xlsx   2020.7-9 成渝西安 IT 招聘（519 行，字段较少）

统一输出字段：岗位名称、城市、经验要求、学历要求、薪资下限k、薪资上限k、
              发布时间、技能文本、数据来源、数据年份

用法：
    python src/prepare_kaggle_data.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "kaggle"
OUT = ROOT / "data" / "processed"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. it-position-info（2024-04 ~ 2025-08，110,176 行，无表头）
#    列含义根据数据内容逐一核对确定，详见 docs/data_profile.md
# ---------------------------------------------------------------------------
IT_COLUMNS = [
    "岗位ID", "城市", "岗位大类", "岗位子类", "编号2", "公司ID",
    "岗位名称", "联系人", "联系人职务", "工作地", "公司名称",
    "标签串", "备用12", "标签串重复", "工作地重复", "省", "市", "区",
    "薪资文本", "薪资上限", "薪资下限", "发布时间", "经验要求", "学历要求",
    "行业", "公司性质", "公司规模", "纬度", "经度", "工作性质",
    "备用30", "备用31",
]


def 提取技能文本(标签串) -> str:
    """标签串形如 '3年及以上|大专|计算机|oracle|数据库'，
    前两项是经验/学历，其余才是技能关键词；无法识别时原样返回。"""
    if pd.isna(标签串):
        return ""
    片段 = str(标签串).split("|")
    技能 = [
        p for p in 片段
        if not re.match(r"^(\d+年|无需经验|在校生|应届|经验)", p)
        and p not in {"本科", "大专", "硕士", "博士", "高中", "中技/中专",
                      "初中及以下", "学历不限", "不限"}
    ]
    return "|".join(技能)


def 处理_it() -> pd.DataFrame:
    df = pd.read_csv(RAW / "it-position-info" / "it.csv", header=None,
                     low_memory=False, names=IT_COLUMNS)
    结果 = pd.DataFrame({
        "岗位名称": df["岗位名称"],
        "城市": df["城市"],
        "经验要求": df["经验要求"],
        "学历要求": df["学历要求"],
        # 原始单位为元/月，换算为千元/月，与 2017/2018 基线一致
        "薪资下限k": pd.to_numeric(df["薪资下限"], errors="coerce") / 1000,
        "薪资上限k": pd.to_numeric(df["薪资上限"], errors="coerce") / 1000,
        "发布时间": pd.to_datetime(df["发布时间"], errors="coerce"),
        "技能文本": df["标签串"].map(提取技能文本),
        "岗位大类": df["岗位大类"],
        "数据来源": "kaggle:it-position-info",
        "数据年份": pd.to_datetime(df["发布时间"], errors="coerce").dt.year,
    })
    return 结果


# ---------------------------------------------------------------------------
# 2. nc2023（2023 年，437 行，含职位描述全文）
# ---------------------------------------------------------------------------
def 解析薪资k(文本):
    """把 '7k-10k' 解析为 (下限, 上限)，单位千元/月。"""
    if pd.isna(文本):
        return (None, None)
    nums = re.findall(r"(\d+(?:\.\d+)?)\s*[kK]", str(文本))
    if len(nums) >= 2:
        return (float(nums[0]), float(nums[1]))
    if len(nums) == 1:
        return (float(nums[0]), float(nums[0]))
    return (None, None)


def 处理_nc2023() -> pd.DataFrame:
    df = pd.read_excel(RAW / "nc2023" / "nc2023.xlsx")
    薪资 = df["salary"].map(解析薪资k)
    结果 = pd.DataFrame({
        "岗位名称": df["job"],
        "城市": "南昌",  # area 字段均为南昌各区县（红谷滩区等）
        "经验要求": df["experience"].str.replace("经验", "", regex=False),
        "学历要求": df["education"].str.replace("及以上", "", regex=False),
        "薪资下限k": [s[0] for s in 薪资],
        "薪资上限k": [s[1] for s in 薪资],
        "发布时间": pd.NaT,  # 该数据集无发布时间字段，仅有整体年份 2023
        "技能文本": df["description"],  # 职位描述全文，第二阶段再做分词提取
        "岗位大类": None,
        "数据来源": "kaggle:nc2023",
        "数据年份": 2023,
    })
    return 结果


# ---------------------------------------------------------------------------
# 3. cdcqxaitjobmarket（2020.7-9 成渝西安，519 行，字段较少，仅保留可用列）
# ---------------------------------------------------------------------------
def 处理_成渝西安() -> pd.DataFrame:
    df = pd.read_excel(RAW / "cdcqxaitjobmarket" / "data1.xlsx")
    # d 列形如 '西安  |  本科  |  招6人'，拆出城市与学历
    拆分 = df["d"].astype(str).str.split("|", expand=True)
    结果 = pd.DataFrame({
        "岗位名称": df["标题"],
        "城市": 拆分[0].str.strip(),
        "经验要求": None,  # 原始数据无经验字段
        "学历要求": 拆分[1].str.strip() if 拆分.shape[1] > 1 else None,
        "薪资下限k": None,
        "薪资上限k": None,
        "发布时间": pd.NaT,  # 仅知整体时间范围 2020.7-9
        "技能文本": df["标题"],  # 无描述字段，只能利用标题
        "岗位大类": None,
        "数据来源": "kaggle:cdcqxaitjobmarket",
        "数据年份": 2020,
    })
    return 结果


def main() -> None:
    for 名称, 函数 in [("it_jobs_2025", 处理_it), ("nc2023", 处理_nc2023),
                       ("cd_cq_xa_2020", 处理_成渝西安)]:
        df = 函数()
        路径 = OUT / f"{名称}_标准化.csv"
        df.to_csv(路径, index=False)
        print(f"{名称}: {df.shape[0]} 行 -> {路径.name}")


if __name__ == "__main__":
    main()
