#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：auto_nep
@File ：spend_time.py
@Author ：RongYi
@Date ：2025/5/2 12:59
@E-mail ：2071914258@qq.com
"""
import re


def spend_time(task_path):
    """
    读取当前任务所花费时间
    :param task_path: 任务路径
    :return: step time: h m s
    """
    with open(task_path + "/out.log", encoding='utf-8') as f:
        content = f.read()
        time_pattern = re.compile(r" CU\d+\s+.*\s+(\d+\.\d+)$", re.MULTILINE)
        time_match = time_pattern.findall(content)
        spend_time = 0
        for time in time_match:
            spend_time += float(time)
        step_pattern = re.compile(r" CU\d+\s+.*\s+\d+\.\d+$", re.MULTILINE)
        step_match = step_pattern.findall(content)
        return step_match[-1], str(int(spend_time // 3600)), str(int(spend_time // 60 % 60)), str(round(spend_time % 60))

