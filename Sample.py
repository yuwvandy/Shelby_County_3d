# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 15:56:38 2020

@author: wany105
"""

from docplex.mp.model import Model
mdl = Model('modelo')
x1 = mdl.integer_var(name = 'x1')
x2 = mdl.integer_var(name = 'x2')
X = [x1, x2]
A=[1, 2]
mdl.maximize(27*x1 + 21*x2 - 10*x1 - 9*x2 - 14*x1 - 10*x2 + 100*x2)
mdl.add_constraint(A[0]*x1 + A[1]*x2 <= 80)
mdl.add_constraint(2*x1 + x2 <= 100)
mdl.add_constraint(2*x1 + x2 = 100)
mdl.add_constraint(x1 >= 20)
mdl.add_constraint(x1 <= 20)
mdl.add_constraint(mdl.sum(X) <= 50)
mdl.add_constraint(mdl.sum(X) >= 50)
mdl.add_constraint((x1 <= 30) == (x2 == 10))
mdl.add_constraint((x1 >= 60) == (x2 == 20))
print(mdl.export_to_string())
solution = mdl.solve(log_output = True)
solution.display()
