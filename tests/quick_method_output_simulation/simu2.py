from __future__ import division

import numpy as np
from scipy.optimize import minimize
import pandas as pd
from itertools import product
import math

LINK_CAPACITY = 10 
# Case 1: Mix input flow
case1 = {
    1: {'bw': 8, 'profit': 10},
    2: {'bw': 8, 'profit': 90},
    3: {'bw': 5, 'profit': 40},
    4: {'bw': 5, 'profit': 10},
    5: {'bw': 2, 'profit': 20},
}

# Case 2: Profit positively correlated with bw
case2 = {
    1: {'bw': 9, 'profit': 80},
    2: {'bw': 6, 'profit': 60},
    3: {'bw': 3, 'profit': 30},
    4: {'bw': 2, 'profit': 20},
    5: {'bw': 1, 'profit': 10},
}

# Case 3: Profit negatively correlated with bw
case3 = {
    1: {'bw': 9, 'profit': 10},
    2: {'bw': 6, 'profit': 30},
    3: {'bw': 3, 'profit': 50},
    4: {'bw': 2, 'profit': 60},
    5: {'bw': 1, 'profit': 80},
}


# Profit-Maximizing Bandwidth Allocation with Fairness

def profit_maximization_with_fairness_allocate_bw(flows, capacity=10.0, lam=10.0):
    """
    Allocate bandwidth to maximize profit minus fairness penalty.

    flows: dict of flow_id: {'bw': demand, 'profit': profit}
    capacity: total link capacity (Mbps)
    lam: fairness penalty weight (higher lam -> more fairness)
    Returns: allocation dict, profit_gain, profit_loss, percent_loss, Jain index.
    """
    N = len(flows)
    # Sort flows by ID
    ids = sorted(flows.keys())
    d = np.array([flows[i]['bw'] for i in ids], float)
    P = np.array([flows[i]['profit'] for i in ids], float)
    # Objective: maximize profit and fairness (minimize negative profit + penalty)
    # f_i = (d[i] - x[i]) / d[i] = percent loss (as fraction of profit)
    def obj(x):
        profit_term = np.dot(P, x/d)  # total profit gained
        f = (d - x) / d               # loss fraction vector
        fairness_penalty = np.sum(f**2)
        return -profit_term + lam*fairness_penalty
    # Constraints: sum x = capacity
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - capacity})
    # Bounds: 0 <= x[i] <= d[i]
    bounds = [(0, d[i]) for i in range(N)]
    # Initial guess: equal share
    x0 = np.minimum(d, capacity/N)
    res = minimize(obj, x0, bounds=bounds, constraints=cons)
    x = res.x
    # Compute results
    profit_gained = P * (x/d)
    profit_lost = P - profit_gained
    percent_loss = 100 * profit_lost / P
    # Jain's fairness on percent loss
    jain = (np.sum(percent_loss)**2) / (N * np.sum(percent_loss**2))
    result = {
        "alloc":dict(zip(ids, x)), "gain":profit_gained, "loss":profit_lost, "percent loss":percent_loss, "Jains":jain
    }
    # return dict(zip(ids, x)), profit_gained, profit_lost, percent_loss, jain
    return result

def profit_maximize_with_fairness_allocate_lamda_bw(flows, capacity=10.0, lam=10.0):
    """
    Python 2 compatible version.
    Maximize profit while minimizing fairness penalty.

    :param flows: dict of flow_id: {'bw': demand, 'profit': profit}
    :param capacity: link capacity
    :param lam: fairness weight
    :return: dict with allocation and metrics
    
    Returns: allocation dict, profit_gain, profit_loss, percent_loss, Jain index.
    """
    ids = sorted(flows.keys())
    N = len(ids)
    d = np.array([flows[i]['bw'] for i in ids])
    P = np.array([flows[i]['profit'] for i in ids])

    # Maximize profit - lambda * unfairness
    def obj(x):
        profit_term = np.dot(P, x / d)
        f = (1 - x / d)   # loss ratio
        fairness_penalty = np.sum(f ** 2)
        return -profit_term + lam * fairness_penalty  # minimize negative of objective
    
    # Constraint: total bandwidth == capacity
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - capacity})
    # Bound: 0 <= x[i] <= demand[i]
    bounds = [(0, d[i]) for i in range(N)]
    # Initial guess: equal share (clipped to demand)
    x0 = np.minimum(d, capacity / N)

    res = minimize(obj, x0, bounds=bounds, constraints=cons)

    x = res.x
    profit_gained = P * (x / d)
    profit_lost = P - profit_gained
    percent_loss = 100.0 * profit_lost / P

    # Jain's fairness index on percent loss
    total = np.sum(percent_loss)
    square_sum = np.sum(percent_loss ** 2)
    if square_sum == 0:
        jain = 1.0
    else:
        jain = (total ** 2) / (N * square_sum)

    result = {
        "alloc": dict(zip(ids, x)),
        "gain": dict(zip(ids, profit_gained)),
        "loss": dict(zip(ids, profit_lost)),
        "percent loss": dict(zip(ids, percent_loss)),
        "jains": jain
    }
    return result
# 1  max ( p_i *(x/d)^2) -  p_i *(1- x/d)^2)   )
# 2  max ( p_i *(x/d)) -  p_i *(1- x/d)^2)   )
# 3  max ( p_i *(x/d)^2) -  p_i *(1- x/d))   )
# 4  max ( p_i *(x/d)) -  p_i *(1- x/d))   )
def profit_maximize_with_fairness_allocate_minusPLR1(flows, capacity=10.0, obj_f = 0):
    """
    Python 2 compatible version.
    Maximize profit while minimizing fairness penalty.

    :param flows: dict of flow_id: {'bw': demand, 'profit': profit}
    :param capacity: link capacity
    :param lam: fairness weight
    :return: dict with allocation and metrics
    
    Returns: allocation dict, profit_gain, profit_loss, percent_loss, Jain index.
    """
    ids = sorted(flows.keys())
    N = len(ids)
    d = np.array([flows[i]['bw'] for i in ids])
    P = np.array([flows[i]['profit'] for i in ids])

    # Maximize profit - lambda * unfairness
    def obj1(x):
        # 1  max ( p_i *(x/d)^2) -  p_i *(1- x/d)^2)   )

        # profit_term = np.dot(P, x / d)
        profit_term = np.sum(P * (x / d)**2)

        #f = (1 - x / d)   # loss ratio
        fairness_penalty =  np.sum(P * (1 - x / d)**2)
        return - profit_term + fairness_penalty  # minimize negative of objective
    def obj2(x):
        # 2  max ( p_i *(x/d)) -  p_i *(1- x/d)^2)   )
        profit_term = np.sum(P * (x / d))
        fairness_penalty =  np.sum(P * (1 - x / d)**2)
        return - profit_term + fairness_penalty  # minimize negative of objective
    def obj3(x):
        # 3  max ( p_i *(x/d)^2) -  p_i *(1- x/d))   )
        profit_term = np.sum(P * (x / d)**2)
        fairness_penalty =  np.sum(P * (1 - x / d))
        return - profit_term + fairness_penalty  # minimize negative of objective
    def obj4(x):
        # profit_term = np.dot(P, x / d)
        # 4  max ( p_i *(x/d)) -  p_i *(1- x/d))   )  
        profit_term = np.sum(P * (x / d))
        fairness_penalty =  np.sum(P * (1 - x / d))
        return - profit_term + fairness_penalty  # minimize negative of objective
    
    def obj5(x):
        # 5  max ( p_i *(x/d)) -  [ p_i *(1- x/d) ])^2   )

        # profit_term = np.dot(P, x / d)
        profit_term = np.sum(P * (x / d))

        #f = (1 - x / d)   # loss ratio
        p_list = [ math.sqrt( p) for p in P]
        fairness_penalty =  np.sum(( p_list * (1 - x / d))**2)
        return - profit_term + fairness_penalty  # minimize negative of objective
    def obj6(x):
        # 6  max ( p_i *(x/d)^2) / p_i *(1- x/d)^2)   )
        profit_term = np.sum(P * (x / d)**2)
        fairness_penalty =  np.sum(P * (1 - x / d)**2)
        return - (profit_term / fairness_penalty )  # minimize negative of objective
    
    def obj7(x):
        # 7  max ( p_i *(x/d)) / p_i *(1- x/d)^2)   )
        profit_term = np.sum(P * (x / d))
        fairness_penalty =  np.sum(P * (1 - x / d)**2)
        return - (profit_term / fairness_penalty )  # minimize negative of objective
    def obj8(x):
        # 8  max ( p_i *(x/d)^2) / p_i *(1- x/d))   )
        profit_term = np.sum(P * (x / d)**2)
        fairness_penalty =  np.sum(P * (1 - x / d))
        return - (profit_term / fairness_penalty )  # minimize negative of objective
    def obj9(x):
        # 9  max ( p_i *(x/d)) / p_i *(1- x/d))   )
        profit_term = np.sum(P * (x / d))
        fairness_penalty =  np.sum(P * (1 - x / d))
        return - (profit_term / fairness_penalty )  # minimize negative of objective
    
    
    
    # Constraint: total bandwidth == capacity
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - capacity})
    # Bound: 0 <= x[i] <= demand[i]
    bounds = [(0, d[i]) for i in range(N)]
    # Initial guess: equal share (clipped to demand)
    x0 = np.minimum(d, capacity / N)
    objf = [obj1,obj2,obj3,obj4,obj5, obj6, obj7, obj8, obj9]
    res = minimize(objf[obj_f], x0, bounds=bounds, constraints=cons)

    x = res.x
    profit_gained = P * (x / d)
    profit_lost = P - profit_gained
    percent_loss = 100.0 * profit_lost / P
    

    # Jain's fairness index on percent loss
    total = np.sum(percent_loss)
    square_sum = np.sum(percent_loss ** 2)
    if square_sum == 0:
        jain = 1.0
    else:
        jain = (total ** 2) / (N * square_sum)

    result = {
        "alloc": dict(zip(ids, x)),
        "gain": dict(zip(ids, profit_gained)),
        "loss": dict(zip(ids, profit_lost)),
        "percent loss": dict(zip(ids, percent_loss)),
        "jains": jain,
        "obj_result": res.fun
    }
    return result


def calculate_jain_index(percent_loss):
    total = np.sum(percent_loss)
    square_sum = np.sum(percent_loss ** 2)
    if square_sum == 0:
        return 1.0
    return (total ** 2) / (len(percent_loss) * square_sum)

def profit_maximize_with_backlog_penalty(flows, backlog, capacity=10.0):
    ids = sorted(flows.keys())
    N = len(ids)
    d = np.array([flows[i]['bw'] for i in ids])
    P = np.array([flows[i]['profit'] for i in ids])
    B = np.array([backlog.get(i, 0.0) for i in ids])
    
    
    total_demand_bw = np.sum(d)
    def calculate_backlog ( x, d, total_demand_bw):
        # x = np.array(x)
        x = [max( 0, x[i]) for i in range(len(x))  ]
        unmet = [ d[i] - x[i] for i in range(len(x)) ]
        
        part1 = [  max(0.0, unmet[i] * total_demand_bw )/P[i] for i in range(len(unmet)) ]
        part2 = [  max(0.0, x[i] * total_demand_bw )/P[i] for i in range(len(unmet)) ]
        return [ (B[i] + max( 0, part1[i] / part2[i])/P[i] ) for i in range(len(unmet)) ]
    
    def calculate_unfairness(x, d) : # unmet bw / allocated bw
        unmet =  d - x
        nums=  [ unmet[i] / x[i]  for i in range(len(unmet))  ]
        res = [ max( 0, nums[i] ) for i in range(len(unmet)) ]
        return np.sum( res)
    def calculate_unfairness_2(x, d) : # whether divid by profit_i or not
        unmet =  d - x
        nums=  [ unmet[i] / x[i]  for i in range(len(unmet))  ]
        res = [ B[i] + max( 0, nums[i]/P[i] ) for i in range(len(unmet)) ]
        return np.sum( res)
    
    def obj(x):
        x = np.array(x)
        profit_term = np.sum(P * (x / d))
        fairness_penalty = calculate_unfairness(x, d)
        backlog_penalty =0
        return - (profit_term - fairness_penalty - backlog_penalty)
    bw_lower_bound = round( (1/total_demand_bw)*capacity ,4)
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - capacity})
    bounds = [(max(1e-6,bw_lower_bound), d[i]) for i in range(N)]
    x0 = np.minimum(d, capacity / N)

    res = minimize(obj, x0, bounds=bounds, constraints=cons)
    x = res.x
    
    #unmet = d - x
    #total_demand_bw =  np.sum( d)
    # new_backlog =[ B[i] +math.sqrt( unmet[i] * total_demand_bw) for i in range(len(unmet)) ]
    new_backlog = calculate_backlog( x, d, total_demand_bw)
    print ("D: ", d)
    print ("X: ", x)
    print ("backlog_penalty: ", np.sum(new_backlog))
    profit_gained = P * (x / d)
    profit_lost = P - profit_gained
    percent_loss = 100.0 * profit_lost / P

    jain = calculate_jain_index(percent_loss)

    result = {
        "alloc": dict(zip(ids, x)),
        "gain": dict(zip(ids, profit_gained)),
        "loss": dict(zip(ids, profit_lost)),
        "percent loss": dict(zip(ids, percent_loss)),
        "jains": jain,
        "obj_result": res.fun,
        "backlog": dict(zip(ids, new_backlog))
    }
    return result



def print_data(flows, data, case="case1"):
    alloc = data["alloc"]
    gain = data["gain"]
    loss = data["loss"]
    perc = data["percent loss"]
    fairness = data["jains"]
    obj_result = data["obj_result"]

    print(case)
    print(" Flow | Demand | Profit | Alloc | Profit Gained | Profit Lost | % Loss")
    print("-----:|-------:|-------:|------:|---------------:|-------------:|--------:")

    for i in sorted(flows.keys()):
        demand = flows[i]['bw']
        profit = flows[i]['profit']
        alloc_i = alloc[i]
        gain_i = gain[i]
        loss_i = loss[i]
        perc_i = perc[i]
        print("  {0:<3} |   {1:>2}    |   {2:>3}   | {3:>6.3f} |     {4:>9.3f}   |   {5:>9.3f}   |  {6:>6.1f}%".format(
            i, demand, profit, alloc_i, gain_i, loss_i, perc_i
        ))

    total_profit = sum(gain.values())
    total_loss = sum(loss.values())
    print("Total profit = {0:.3f}\nJain fairness = {1:.3f}".format(total_profit, fairness))
    print( "Objective Function Result: {0:.3f}".format (obj_result))

for i in range(5,9):
    print ("=========================")
    print ("Obj function: ", i)
    result = profit_maximize_with_fairness_allocate_minusPLR1(case1,10.0, i)
    print_data(case1, result, "case1")
    result = profit_maximize_with_fairness_allocate_minusPLR1(case2, 10.0, i)
    print_data(case2, result, "case2")
    result = profit_maximize_with_fairness_allocate_minusPLR1(case3, 10.0, i)
    print_data(case3, result, "case3")
# print first few rows of data
#print(df_all.head())

# export to CSV
#df_all.to_csv("allocation_results.csv", index=False)


# result = profit_maximization_with_fairness_allocate_bw(case1, capacity=10, lam= 130 )
# print_data (case1, result, "case1")
# result = profit_maximization_with_fairness_allocate_bw(case2, capacity=10, lam= 130 )
# print_data (case2, result, "case2")
# result = profit_maximization_with_fairness_allocate_bw(case3, capacity=10, lam= 130 )
# print_data (case3, result, "case3")
