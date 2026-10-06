# -*- coding: utf-8 -*-
"""
按冻结技能词典（src/skill_dictionary.json）把各时期岗位数据打成「岗位×技能」矩阵。

输入：data/processed/ 下各时期的标准化表
输出：data/processed/skill_matrix_<年份>.csv 与汇总 skill_matrix_all.csv
      列为：记录ID、来源、数据年份、层级、薪资中位k、城市，
           每个技能一列（0/1），每个分组一列（组内任一技能命中为 1）

用法：
    python src/build_skill_matrix.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
DICT_PATH = Path(__file__).resolve().parent / "skill_dictionary.json"

# ---------------------------------------------------------------------------
# 词典加载与匹配器编译
# ---------------------------------------------------------------------------

def 加载词典(path: Path = DICT_PATH) -> dict:
    """读取词典，把每个技能的别名编译成一条正则。返回 {组名: {技能名: 正则}}。"""
    原始 = json.loads(path.read_text(encoding="utf-8"))
    编译结果: dict[str, dict[str, re.Pattern]] = {}
    for 组名, 组 in 原始["分组"].items():
        编译结果[组名] = {}
        for 技能 in 组["技能"]:
            片段 = []
            for 别名 in 技能["别名"]:
                词 = re.escape(别名["词"])
                if 别名.get("匹配") == "边界":
                    # 前后不允许紧跟字母/数字/+#. ，防止 java 命中 javascript
                    片段.append(rf"(?<![A-Za-z0-9+#.]){词}(?![A-Za-z0-9+#.])")
                else:
                    片段.append(词)
            大小写敏感 = any(a.get("大小写敏感") for a in 技能["别名"])
            标志 = 0 if 大小写敏感 else re.IGNORECASE
            编译结果[组名][技能["标准名"]] = re.compile("|".join(片段), 标志)
    return 编译结果


# ---------------------------------------------------------------------------
# 岗位层级判定（统一规则，见 docs/research_design.md 第 3 节）
# ---------------------------------------------------------------------------

def 判定层级(经验) -> str | None:
    """按经验要求的最小年数划分：≤1 年初级，2-4 年中级，≥5 年高级。
    应届/在校/无需经验归为初级；'不限' 等无法判定的返回 None。"""
    if pd.isna(经验):
        return None
    s = str(经验)
    if re.search(r"应届|在校|实习|无需经验", s):
        return "初级"
    if "不限" in s:
        return None
    年数 = re.findall(r"(\d+)\s*年", s)
    if not 年数:
        return None
    最小年 = min(int(y) for y in 年数)
    if 最小年 <= 1:
        return "初级"
    if 最小年 >= 5:
        return "高级"
    return "中级"


# ---------------------------------------------------------------------------
# 各时期数据装载：统一为 (meta DataFrame, 技能文本 Series)
# ---------------------------------------------------------------------------

def 装载_2017() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(PROC / "position_2017_薪资解析.csv")
    meta = pd.DataFrame({
        "记录ID": "p2017_" + df["positionId"].astype(str),
        "来源": "lagou_2017_全国",
        "数据年份": 2017,
        "层级": df["workYear"].map(判定层级),
        "薪资中位k": df["薪资中位k"],
        "城市": df["city"],
    })
    文本 = df["positionName"].fillna("") + " " + df["positionLables"].fillna("")
    return meta, 文本


def 装载_2018() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(PROC / "lagou_hz_2018_日期薪资解析.csv")
    经验 = df["work_year"].str.replace("经验", "", regex=False).str.replace("/", "", regex=False).str.strip()
    meta = pd.DataFrame({
        "记录ID": "p2018_" + df.index.astype(str),
        "来源": "lagou_2018_杭州",
        "数据年份": 2018,
        "层级": 经验.map(判定层级),
        "薪资中位k": df["薪资中位k"],
        "城市": "杭州",
    })
    文本 = df["job_title"].fillna("") + " " + df["job_desc"].fillna("")
    return meta, 文本


def 装载_2020() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(PROC / "cd_cq_xa_2020_标准化.csv")
    meta = pd.DataFrame({
        "记录ID": "p2020_" + df.index.astype(str),
        "来源": "kaggle_2020_成渝西安",
        "数据年份": 2020,
        "层级": None,  # 该数据集无经验字段
        "薪资中位k": pd.NA,
        "城市": df["城市"],
    })
    return meta, df["岗位名称"].fillna("")


def 装载_2023() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(PROC / "nc2023_标准化.csv")
    meta = pd.DataFrame({
        "记录ID": "p2023_" + df.index.astype(str),
        "来源": "kaggle_2023_南昌",
        "数据年份": 2023,
        "层级": df["经验要求"].map(判定层级),
        "薪资中位k": (df["薪资下限k"] + df["薪资上限k"]) / 2,
        "城市": df["城市"],
    })
    文本 = df["岗位名称"].fillna("") + " " + df["技能文本"].fillna("")
    return meta, 文本


def 装载_2025() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(PROC / "it_jobs_2025_标准化.csv")
    meta = pd.DataFrame({
        "记录ID": "p2025_" + df.index.astype(str),
        "来源": "kaggle_2025_全国IT",
        "数据年份": 2025,
        "层级": df["经验要求"].map(判定层级),
        "薪资中位k": (df["薪资下限k"] + df["薪资上限k"]) / 2,
        "城市": df["城市"],
    })
    文本 = (df["岗位名称"].fillna("") + " " + df["岗位大类"].fillna("")
            + " " + df["技能文本"].fillna(""))
    return meta, 文本


# ---------------------------------------------------------------------------
# 矩阵构建
# ---------------------------------------------------------------------------

def 构建矩阵(meta: pd.DataFrame, 文本: pd.Series, 词典: dict) -> pd.DataFrame:
    """对每个技能做正则匹配（0/1 列），再聚合出分组命中列。"""
    结果 = meta.copy()
    for 组名, 技能表 in 词典.items():
        组命中 = pd.Series(False, index=文本.index)
        for 技能名, 正则 in 技能表.items():
            命中 = 文本.str.contains(正则, regex=True).fillna(False)
            结果[f"S_{技能名}"] = 命中.astype(int)
            组命中 = 组命中 | 命中
        结果[f"G_{组名}"] = 组命中.astype(int)
    return 结果


def main() -> None:
    词典 = 加载词典()
    装载器 = {"2017": 装载_2017, "2018": 装载_2018, "2020": 装载_2020,
              "2023": 装载_2023, "2025": 装载_2025}
    全部 = []
    for 年份, 函数 in 装载器.items():
        meta, 文本 = 函数()
        矩阵 = 构建矩阵(meta, 文本, 词典)
        矩阵.to_csv(PROC / f"skill_matrix_{年份}.csv", index=False)
        print(f"{年份}: {矩阵.shape[0]} 行 x {矩阵.shape[1]} 列 -> skill_matrix_{年份}.csv")
        全部.append(矩阵)
    汇总 = pd.concat(全部, ignore_index=True)
    汇总.to_csv(PROC / "skill_matrix_all.csv", index=False)
    print(f"汇总: {汇总.shape[0]} 行 -> skill_matrix_all.csv")


if __name__ == "__main__":
    main()
