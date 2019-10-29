# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
# 固定顺序的施密特正交 (正交 + 归一)
'''
确定因子正交顺序，正交顺序不同，最终得到的因子不同.
'''
def schmidt(factors, class_col):
    class_mkt = factors[class_col]
    factors1 = factors.drop(class_col,axis = 1)
    col_name = factors1.columns
    factors1 = factors1.values
    R = np.zeros((factors1.shape[1], factors1.shape[1]))
    Q = np.zeros(factors1.shape)
    for k in range(0, factors1.shape[1]):
        R[k, k] = np.sqrt(np.dot(factors1[:, k], factors1[:, k]))
        Q[:, k] = factors1[:, k]/R[k, k]
        for j in range(k+1, factors1.shape[1]):
            R[k, j] = np.dot(Q[:, k], factors1[:, j])
            factors1[:, j] = factors1[:, j] - R[k, j]*Q[:, k]

    Q = pd.DataFrame(Q,columns = col_name,index = factors.index)
    Q = pd.concat([Q,class_mkt],axis = 1)
    return Q

# 规范正交
'''
 与主成分分析一样，相对主成分分析，规范正交即可用在截面上，但用在时间序列上就会出现对应关系不一致的问题
 确定因子正交顺序，正交顺序不同，最终得到的因子不同.
'''
def canonial(factors, class_col):
    class_mkt = factors[class_col]
    factors1 = factors.drop(class_col,axis = 1)
    col_name = factors1.columns     
    D,U=np.linalg.eig(np.dot(factors1.T,factors1))
    S = np.dot(U,np.diag(D**(-0.5)))
        
    fhat = np.dot(factors1,S)
    fhat = pd.DataFrame(fhat,columns = col_name,index = factors.index)
    fhat = pd.concat([fhat,class_mkt],axis = 1)        

    return fhat

# 对称正交
def symmetry(factors, class_col):
    class_mkt = factors[class_col]
    factors1 = factors.drop(class_col,axis = 1)
    col_name = factors1.columns
    D,U=np.linalg.eig(np.dot(factors1.T,factors1))
    S = np.dot(U,np.diag(D**(-0.5)))
        
    fhat = np.dot(factors1,S)
    fhat = np.dot(fhat,U.T)
    fhat = pd.DataFrame(fhat,columns = col_name,index = factors.index)
    fhat = pd.concat([fhat,class_mkt],axis = 1)        
    
    return fhat