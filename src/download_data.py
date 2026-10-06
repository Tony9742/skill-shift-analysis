# -*- coding: utf-8 -*-
"""
下载第一阶段使用的公开数据集。

数据说明：
    数据集来自 GitHub 公开仓库 xucoolboy/Data_job_in_lagou（MIT 场景下
    公开可获取的教学项目数据），包含：
      - position_sql.csv : 2017 年年中拉勾网全国「数据相关岗位」职位表
      - company_sql.csv  : 与职位表配套的公司表
      - lagou_hz_2.csv   : 2018 年 5 月拉勾网杭州站「数据分析」岗位表

    国内网络环境下 raw.githubusercontent.com 不可达，因此通过
    api.github.com 的 contents 接口（raw Accept 头）下载。

用法：
    python src/download_data.py
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

# GitHub API 的 contents 接口，Accept 头为 raw 时直接返回文件内容
API_BASE = (
    "https://api.github.com/repos/xucoolboy/Data_job_in_lagou/contents"
)
RAW_ACCEPT = {"Accept": "application/vnd.github.raw"}

# 需要下载的文件：API 路径 -> 本地保存路径
FILES = {
    "dataset/company_sql.csv": "company_sql.csv",
    "dataset/position_sql.csv": "position_sql.csv",
    "dataset/lagou_hz_2.csv": "lagou_hz_2.csv",
    "README.md": "README_数据来源说明.md",
}


def download(url_path: str, dest: Path) -> None:
    """从 GitHub API 下载单个文件到 dest。"""
    req = urllib.request.Request(f"{API_BASE}/{url_path}", headers=RAW_ACCEPT)
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())
    print(f"已下载 {url_path} -> {dest} ({dest.stat().st_size} 字节)")


def main() -> None:
    # 原始数据统一保存到 data/raw/lagou_2017/
    out_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "lagou_2017"
    out_dir.mkdir(parents=True, exist_ok=True)
    for url_path, local_name in FILES.items():
        download(url_path, out_dir / local_name)
    print("全部文件下载完成。")


if __name__ == "__main__":
    main()
