# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 15:56:38 2020

@author: wany105
"""

mdl = Model('model')
x1 = mdl.integer_var(name = 'x1')
x2 = mdl.integer_var(name = 'x2')

mdl.maximize(27*x1 + 21*x2 - 10*x1)

mdl.add_if_then(1 <= x1, x2 >= 2)
mdl.add_constraint(x1 > 1)
