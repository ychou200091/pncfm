"""
Bandwidth allocation algorithms focusing on profit maximization with penalties for unmet demand.
This is the main algorithm file for bandwidth allocation strategies.
"""
import numpy as np
from scipy.optimize import minimize

def profit_maximize_with_ungivenbw_penalty(flows, capacity=10.0):
    # print ("Inside profit_maximize_with_ungivenbw_penalty")
    # print ("processing flows:",flows )
    ids = sorted(flows.keys())
    N = len(ids)
    d = np.array([flows[i]['bw'] for i in ids])
    P = np.array([flows[i]['profit'] for i in ids])
    total_demand_bw = np.sum(d)

    def calculate_penalty(x, d) : # whether divid by profit_i or not
        unmet =  d - x
        nums = [unmet[i] / x[i] if x[i] != 0 else unmet[i] / 1e-10 for i in range(len(unmet))]
        res = [ max( 0, nums[i]/P[i] ) for i in range(len(unmet)) ]
        # res = [ max( 0, nums[i] ) for i in range(len(unmet)) ]
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
    x = [round( i,6) for i in x]
    result = {
        "alloc": dict(zip(ids, x)),
        "gain": dict(zip(ids, profit_gained)),
        "loss": dict(zip(ids, profit_lost)),
        "percent loss": dict(zip(ids, percent_loss)),
        "obj_result": res.fun,
    }
    return result



def profit_proportional_alloc(flow_bw_profit_dict, c):

    sum_profit = 0
    alloc_result ={}
    dic = flow_bw_profit_dict
    for flow in dic:
        sum_profit += dic[flow]["profit"]
    for flow in dic:
        alloc_result[flow] = round(dic[flow]["profit"]/sum_profit * float(c), 5)

    return alloc_result 

def profit_proportional_with_equal_distribution(flow_bw_profit_dict, flow_times, link_capacity):
    """
    Method 2: Profit Proportional Allocation + Equal Redistribution of Remaining Bandwidth

    Args:
        flows (dict): {flow_id: {'bw': float, 'profit': float}}
        link_capacity (float): total link bandwidth available in Mbps

    Returns:
        dict: {
            flow_id: {
                'allocated_bw': float,
                'profit_gain': float,
                'profit_loss': float,
                'percent_profit_loss': float
            },
            'jain_index': float
        }
    """
    print "Inside: profit_proportional_with_equal_distribution"
    print "flow_bw_profit_dict: ", flow_bw_profit_dict
    
    # Step 1: Initial profit proportional allocation
    total_profit = sum([flow_bw_profit_dict[flow]['profit'] for flow in flow_bw_profit_dict.keys()])
    print "total_profit: ", total_profit
    alloc = {}
    remaining_bw = link_capacity

    for flow in flow_bw_profit_dict.keys():
        print "flow: ", flow
        if total_profit > 0:
            alloc[flow] = (flow_bw_profit_dict[flow]['profit'] / total_profit) * link_capacity
        else:
            alloc[flow] = 0

    # Step 2: Cap to flow demand and track unused bandwidth
    satisfied = set()
    while True:
        
        leftover = 0
        new_alloc = {}

        for flow in flow_bw_profit_dict.keys():
            demand = flow_bw_profit_dict[flow]['bw']
            previous_alloc = alloc[flow]
            capped_alloc = min(demand, previous_alloc)
            new_alloc[flow] = capped_alloc

            if capped_alloc >= demand:
                satisfied.add(flow)
                leftover += max(0, previous_alloc - demand)

        alloc = new_alloc.copy()

        # Step 3: Redistribute leftover equally among unsatisfied flows
        unsatisfied_flows = [flow for flow in flow_bw_profit_dict.keys() if flow not in satisfied]
        if not unsatisfied_flows or leftover == 0:
            break

        equal_share = leftover / len(unsatisfied_flows)
        for flow in unsatisfied_flows:
            alloc[flow] += equal_share
        print "remaining_bw: ", remaining_bw, "leftover:", leftover
        print "Current allocation: ", alloc

    print {"alloc": alloc}
    return {"alloc": alloc}

