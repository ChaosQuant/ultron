# -*- coding: utf-8 -*-
import pandas as pd
def calc_ic(factor_df, return_df, factor_list, return_col_name='target_return', ic_type='spearman'):
    """
    计算因子IC值, 本月和下月因子值的秩相关
    params:
            factor_df: DataFrame, columns=['ticker', 'tradeDate', factor_list]
            return_df: DataFrame, colunms=['ticker, 'tradeDate'， return_col_name], 预先计算好的未来的收益率
            factor_list:　list， 需要计算IC的因子名list
            return_col_name: str, return_df中的收益率列名
            method: : {'spearman', 'pearson'}, 默认'spearman', 指定计算rank IC('spearman')或者Normal IC('pearson')
    return:
            DataFrame, 返回各因子的IC序列， 列为: ['tradeDate', factor_list]
    """
    merge_df = factor_df.merge(return_df, on=['code', 'trade_date'])
    # 遍历每个因子，计算对应的IC
    factor_ic_list = []
    for factor_name in factor_list:
        tmp_factor_ic = merge_df.groupby(['trade_date']).apply(
            lambda x: x[[factor_name, return_col_name]].corr(method=ic_type).values[0, 1])
        tmp_factor_ic.name = factor_name
        factor_ic_list.append(tmp_factor_ic)
    factor_ic_frame = pd.concat(factor_ic_list, axis=1)
    factor_ic_frame.reset_index(inplace=True)
    return factor_ic_frame
