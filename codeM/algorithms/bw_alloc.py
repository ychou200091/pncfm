import numpy as np
from scipy.optimize import minimize

def profit_maximize_with_ungivenbw_penalty(flows, capacity=10.0):
    ids = sorted(flows.keys())
    N = len(ids)
    d = np.array([flows[i]['bw'] for i in ids])
    P = np.array([flows[i]['profit'] for i in ids])
    total_demand_bw = np.sum(d)

    def calculate_penalty(x, d) : # whether divid by profit_i or not
        unmet =  d - x
        nums = [unmet[i] / x[i] if x[i] != 0 else unmet[i] / 1e-10 for i in range(len(unmet))]
        res = [ max( 0, nums[i]/P[i] ) for i in range(len(unmet)) ]
        return np.sum( res)

    def obj(x):
        x = np.array(x)
        profit_term = np.sum(P * (x / d))
        fairness_penalty = calculate_penalty(x, d)
        return - (profit_term - fairness_penalty)
    
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - capacity})
    bounds = [(0, d[i]) for i in range(N)]
    x0 = np.minimum(d, capacity / N)

    res = minimize(obj, x0, bounds=bounds, constraints=cons)
    x = res.x
    
    profit_gained = P * (x / d)
    profit_lost = P - profit_gained
    percent_loss =  profit_lost / P

    result = {
        "alloc": dict(zip(ids, x)),
        "gain": dict(zip(ids, profit_gained)),
        "loss": dict(zip(ids, profit_lost)),
        "percent loss": dict(zip(ids, percent_loss)),
        "obj_result": res.fun,
    }
    return result