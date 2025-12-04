import numpy as np
from scipy.optimize import minimize

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

def calculate_jain_index(percent_loss):
    total = np.sum(percent_loss)
    square_sum = np.sum(percent_loss ** 2)
    if square_sum == 0:
        return 1.0
    return (total ** 2) / (len(percent_loss) * square_sum)


def profit_maximize_with_ungivenbw_penalty(flows, capacity=10.0, equ=0):
    ids = sorted(flows.keys())
    N = len(ids)
    d = np.array([flows[i]['bw'] for i in ids])
    P = np.array([flows[i]['profit'] for i in ids])
    total_demand_bw = np.sum(d)

    def calculate_unfairness(x, d) : # unmet bw / allocated bw
        unmet =  d - x
        nums = [unmet[i] / x[i] if x[i] != 0 else unmet[i] / 1e-10 for i in range(len(unmet))]
        res = [ max( 0, nums[i] ) for i in range(len(unmet)) ]
        return np.sum( res)
    def calculate_unfairness_2(x, d) : # whether divid by profit_i or not
        unmet =  d - x
        nums = [unmet[i] / x[i] if x[i] != 0 else unmet[i] / 1e-10 for i in range(len(unmet))]
        res = [ max( 0, nums[i]/P[i] ) for i in range(len(unmet)) ]
        return np.sum( res)
    equations = [calculate_unfairness, calculate_unfairness_2]
    def obj(x):
        x = np.array(x)
        profit_term = np.sum(P * (x / d))
        fairness_penalty = equations[equ](x, d)
        return - (profit_term - fairness_penalty)
    
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - capacity})
    bounds = [(0, d[i]) for i in range(N)]
    x0 = np.minimum(d, capacity / N)

    res = minimize(obj, x0, bounds=bounds, constraints=cons)
    x = res.x
    
    profit_gained = P * (x / d)
    profit_lost = P - profit_gained
    percent_loss =  profit_lost / P
    jain = calculate_jain_index(percent_loss)
    result = {
        "alloc": dict(zip(ids, x)),
        "gain": dict(zip(ids, profit_gained)),
        "loss": dict(zip(ids, profit_lost)),
        "percent loss": dict(zip(ids, percent_loss)),
        "jains": jain,
        "obj_result": res.fun,
    }
    return result

def print_round(t, flows, alloc, loss, gain, obj_result, total_profit, jain):
    print("\nRound {}:".format(t + 1))
    print("Flow\t,Alloc\t,Loss% \t,Gain\t")
    for k in flows:
        print("{}\t,{:.4f}\t,{:.4f}\t,{:.4f}\t".format(k, alloc[k], loss[k], gain[k]))
    print("Jain's Index: {:.4f}, Total Profit Gain: {:.4f}".format(jain,total_profit))

def run_one_time(flows, capacity,eqa):
    # eqa: 0: equation1 more fair, 1: equation2  maximize profit.
    result = profit_maximize_with_ungivenbw_penalty(flows,capacity,eqa)
    alloc = result["alloc"]
    loss = result["percent loss"]
    gain = result["gain"]
    total_profit = sum(gain.values())
    jain = result["jains"]
    obj_result = result["obj_result"]
    print_round(0,flows, alloc, loss, gain, obj_result,total_profit, jain)

    
if __name__ == "__main__":
    run_one_time( case1,LINK_CAPACITY,0)
    run_one_time( case2,LINK_CAPACITY,0)
    run_one_time( case3,LINK_CAPACITY,0)

    # run_one_time( case1,LINK_CAPACITY,1)
    # run_one_time( case2,LINK_CAPACITY,1)
    # run_one_time( case3,LINK_CAPACITY,1)