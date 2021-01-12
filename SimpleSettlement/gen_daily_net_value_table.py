# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 16:21
# @Author  : Jeffery Paul
# @File    : gen_daily_net_value_table.py


"""
将base数据（DailyEquity.csv，OtherAsset.csv, OpenDay.csv）
转换为main数据（DailyNetValueTable.csv）
"""

import os
import shutil
import datetime
from collections import defaultdict

PATH_PROJECT = os.path.abspath(os.path.join(__file__, './../..'))
PATH_DATA_BASE = os.path.join(PATH_PROJECT, 'Data', 'Base')
PATH_DATA_MAIN = os.path.join(PATH_PROJECT, 'Data', 'Main')


def _gen(path, path_output):
    # 读取 daily_equity_file.csv
    def _parse_daily_equity_file() -> dict:
        if not os.path.isfile(path_daily_equity):
            print('不存在此文件: %s' % path_daily_equity)
            raise FileExistsError
        with open(path_daily_equity, encoding='utf-8') as f:
            l_lines = f.readlines()
        if len(l_lines) < 2:
            print('数据行不足或有误: %s' % path_daily_equity)
            raise ValueError
        d_daily_equity = {}
        for n, line in enumerate(l_lines[1:]):
            line = line.strip()
            try:
                date = datetime.datetime.strptime(line.split(',')[0], '%Y%m%d')
                equity = float(line.split(',')[1])
            except:
                print('数据行有误: %s （第%s行）' % (line, n))
                raise ValueError
            if date not in d_daily_equity:
                d_daily_equity[date] = equity
            else:
                print('存在相同的日期: %s' % line)
                raise ValueError
        d_daily_equity = dict(sorted(d_daily_equity.items()))
        return d_daily_equity

    def _parse_other_asset() -> dict:
        if not os.path.isfile(path_other_asset):
            print('不存在此文件: %s' % path_other_asset)
            return {}
        with open(path_other_asset, encoding='utf-8') as f:
            l_lines = f.readlines()
        if len(l_lines) < 2:
            # 允许为空
            return {}
        d_other_asset = defaultdict(float)
        for n, line in enumerate(l_lines[1:]):
            line = line.strip()
            try:
                date = datetime.datetime.strptime(line.split(',')[0], '%Y%m%d')
                other_asset = float(line.split(',')[1])
                d_other_asset[date] += other_asset
            except:
                print('数据行有误: %s （第%s行）' % (line, n))
                raise ValueError
        return d_other_asset

    def _parse_open_day() -> dict:
        if not os.path.isfile(path_open_day):
            print('不存在此文件: %s' % path_open_day)
            return {}
        with open(path_open_day, encoding='utf-8') as f:
            l_lines = f.readlines()
        if len(l_lines) < 2:
            print('数据行不足或有误: %s' % path_open_day)
            raise ValueError
        d_open_day = {}
        for n, line in enumerate(l_lines[1:]):
            line = line.strip()
            try:
                date = datetime.datetime.strptime(line.split(',')[0], '%Y%m%d')
                try:
                    shares = float(line.split(',')[1])
                except:
                    shares = 0
                try:
                    values = float(line.split(',')[2])
                except:
                    values = 0
                try:
                    reference_nv = float(line.split(',')[3])
                except:
                    reference_nv = None
                try:
                    new_shares = float(line.split(',')[4])
                except:
                    new_shares = None

                if date in d_open_day:
                    d_open_day[date]['shares'] += shares
                    d_open_day[date]['values'] += values
                else:
                    d_open_day[date] = {
                        'shares': shares,
                        'values': values,
                        'reference_nv': reference_nv,
                        'new_shares': new_shares
                    }
            except:
                print('数据行有误: %s （第%s行）' % (line, n))
                raise ValueError
        return d_open_day

    # 读取数据
    path_daily_equity = os.path.join(path, 'DailyEquity.csv')
    path_other_asset = os.path.join(path, 'OtherAsset.csv')
    path_open_day = os.path.join(path, 'OpenDay.csv')

    d_daily_equity = _parse_daily_equity_file()
    d_other_asset = _parse_other_asset()
    d_open_day = _parse_open_day()

    # 计算
    # total_equity = equity + other_asset
    d_net_value_table = {}
    if d_other_asset:
        for date, equity in d_daily_equity.items():
            other_asset_date = [
                d for d in d_other_asset.keys()
                if date >= d
            ]
            if not other_asset_date:
                d_net_value_table[date] = {
                    'TotalEquity': equity
                }
            else:
                d_net_value_table[date] = {
                    'TotalEquity': equity + d_other_asset[min(other_asset_date)]
                }
    else:
        for date, equity in d_daily_equity.items():
            d_net_value_table[date] = {
                'TotalEquity': equity
            }

    # 计算每日 份额、净值
    last_date = None
    for date in sorted(list(d_net_value_table.keys())):
        if last_date is None:
            last_nv = 1
            last_shares = 0
        else:
            last_nv = d_net_value_table[last_date]['NetValue']
            last_shares = d_net_value_table[last_date]['Shares']

        # 份额
        match_open_day = [open_day for open_day in d_open_day.keys() if date > open_day]
        if match_open_day:
            _d = d_open_day.pop(min(match_open_day))
            shares = _d['shares']
            values = _d['values']
            reference_nv = _d['reference_nv']
            new_shares = _d['new_shares']

            if new_shares:
                # （1）直接给定 最新份额
                d_net_value_table[date]['Shares'] = new_shares
            else:
                # （2）给定 申购赎回所参照的净值；如果每至
                if reference_nv is None:
                    reference_nv = last_nv
                # 金额
                if values != 0:
                    d_net_value_table[date]['Shares'] = last_shares + shares + values / reference_nv
                # shares数值
                else:
                    d_net_value_table[date]['Shares'] = last_shares + shares
        else:
            d_net_value_table[date]['Shares'] = last_shares

        # 净值
        net_value = d_net_value_table[date]['TotalEquity'] / d_net_value_table[date]['Shares']
        d_net_value_table[date]['NetValue'] = round(net_value, 4)
        d_net_value_table[date]['RoR'] = round(net_value / last_nv - 1, 5)

        last_date = date

    if not os.path.isdir(os.path.dirname(path_output)):
        os.makedirs(os.path.dirname(path_output))
    with open(path_output, 'w') as f:
        f.write('Date,Shares,TotalEquity,NetValue,RoR\n')
        for date in sorted(d_net_value_table.keys()):
            shares = d_net_value_table[date]['Shares']
            total_equity = d_net_value_table[date]['TotalEquity']
            net_value = d_net_value_table[date]['NetValue']
            ror = d_net_value_table[date]['RoR']
            s_date = date.strftime('%Y%m%d')
            f.write(f'{s_date},{shares},{total_equity},{net_value},{ror}\n')
    print('wrote: %s' % path_output)
    return d_net_value_table


def main():
    for fund_name in os.listdir(PATH_DATA_BASE):
        path_fund_base_data = os.path.join(PATH_DATA_BASE, fund_name)
        if not os.path.isdir(path_fund_base_data):
            continue

        # 生成 net value 数据
        path_output = os.path.join(PATH_DATA_MAIN, fund_name, 'DailyNetValueTable.csv')
        d_net_value_table: dict = _gen(path=path_fund_base_data, path_output=path_output)


if __name__ == '__main__':
    print('Started...')
    main()
    print('Finished.')
