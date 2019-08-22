# -*- coding: utf-8 -*-

from . combine_method import equal_combine, hist_ret_combine, hist_ic_combine, max_icir_combine, max_ic_combine

func_dict = {'equal_combine':equal_combine,
                'hist_ret_combine':hist_ret_combine,
                'hist_ic_combine':hist_ic_combine,
                'max_icir_combine':max_icir_combine,
                'max_ic_combine':max_ic_combine}
    
    
class CombineEngine(object):
    @classmethod
    def create_engine(cls, ce_name):
        return func_dict[ce_name]