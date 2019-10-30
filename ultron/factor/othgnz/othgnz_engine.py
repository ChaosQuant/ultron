# -*- coding: utf-8 -*-

from . othgnz_method import schmidt, canonial, symmetry 

func_dict = {'schmidt':schmidt, 'canonial':canonial, 'symmetry':symmetry}
   
class OthgnzEngine(object):
    @classmethod
    def create_engine(cls, ce_name):
        return func_dict[ce_name]