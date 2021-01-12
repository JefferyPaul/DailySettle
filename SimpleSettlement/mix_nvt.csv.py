# -*- coding: utf-8 -*-
# @Time    : 2021/1/12 13:49
# @Author  : Jeffery Paul
# @File    : mix_nvt.csv.py


"""

"""

import os
import datetime
from collections import defaultdict


PATH_PROJECT = os.path.abspath(os.path.join(__file__, './../..'))
PATH_DATA_MAIN = os.path.join(PATH_PROJECT, 'Data', 'Main')
PATH_OUTPUT = os.path.join(PATH_PROJECT, 'Output')


def main():

    # 读
    d_fund_nvt = defaultdict(list)
    for fund_name in os.listdir(PATH_DATA_MAIN):
        path_fund_nvt = os.path.join(PATH_DATA_MAIN, fund_name, 'DailyNetValueTable.csv')
        if not os.path.isfile(path_fund_nvt):
            print('找不到此文件: %s' % path_fund_nvt)
            raise FileExistsError
        with open(path_fund_nvt) as f:
            l_lines = f.readlines()
        if len(l_lines) < 2:
            print('此文件为空: %s' % path_fund_nvt)
            continue
        for line in l_lines[1:]:
            line = line.strip()
            if line == '':
                continue
            else:
                d_fund_nvt[fund_name].append(line)

    # 写
    if not os.path.isdir(PATH_OUTPUT):
        os.makedirs(PATH_OUTPUT)
    path_output_file = os.path.join(
        PATH_OUTPUT, 'NetValueTable_%s.csv' % datetime.datetime.now().strftime('%Y%m%d'))
    l_lines_write = []
    for fund_name, l_lines in d_fund_nvt.items():
        l_lines_write += [
            '%s,%s\n' % (fund_name, line)
            for line in l_lines
        ]
    with open(path_output_file, 'w', encoding='utf-8') as f:
        f.write('Fund,Date,Shares,TotalEquity,NetValue,RoR\n')
        f.writelines(l_lines_write)


if __name__ == '__main__':
    print('Started...')
    main()
    print('Finished.')
