''' methods 
1. Profit Proportional Allocation 
2. Profit Proportional Allocation + remaining bw equal distribution. 
3. Max-min fair allcation. 
4. Same profit loss rate allocation.
'''
from tabulate import tabulate
import numpy as np
import copy
from pprint import pprint


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

def detect_bw_profit_correlation(flows):
    bws = [f["bw"] for f in flows.values()]
    profits = [f["profit"] for f in flows.values()]
    r = np.corrcoef(bws, profits)[0, 1]
   
    if r >= 0.7:
        relation = "positive"
    elif r <= 0.4:
        relation = "negative"
    else:
        relation = "none"
    return relation, r

def profit_proportional_allocation(flows: dict, link_capacity: float):
    """
    Method 1: Profit Proportional Allocation
    Allocates bandwidth proportionally to profit values under link capacity constraint.

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
    total_profit = sum(flow['profit'] for flow in flows.values())

    result = {}
    loss_rates = []

    for flow_id, flow in flows.items():
        profit = flow['profit']
        original_bw = flow['bw']
        profit_ratio = profit / total_profit if total_profit > 0 else 0

        # Allocate bandwidth based on profit proportion
        allocated_bw = profit_ratio * link_capacity
        delivered_ratio = min(1.0, allocated_bw / original_bw)

        profit_gain = delivered_ratio * profit
        profit_loss = profit - profit_gain
        percent_loss = 1 - delivered_ratio

        loss_rates.append(percent_loss)

        result[flow_id] = {
            'allocated_bw': round(allocated_bw, 4),
            'profit_gain': round(profit_gain, 4),
            'profit_loss': round(profit_loss, 4),
            'percent_profit_loss': round(percent_loss, 4)
        }

    # Calculate Jain's Fairness Index on profit loss rate
    n = len(loss_rates)
    sum_loss = sum(loss_rates)
    sum_loss_sq = sum(lr ** 2 for lr in loss_rates)
    jain_index = (sum_loss ** 2) / (n * sum_loss_sq) if sum_loss_sq != 0 else 1.0

    result['jain_index'] = round(jain_index, 4)
    return result

def profit_proportional_with_equal_distribution(flows: dict, link_capacity: float):
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
    # Step 1: Initial profit proportional allocation
    total_profit = sum(flow['profit'] for flow in flows.values())
    alloc = {}
    remaining_bw = link_capacity

    for fid, flow in flows.items():
        if total_profit > 0:
            alloc[fid] = (flow['profit'] / total_profit) * link_capacity
        else:
            alloc[fid] = 0

    # Step 2: Cap to flow demand and track unused bandwidth
    satisfied = set()
    while True:
        leftover = 0
        new_alloc = {}

        for fid, flow in flows.items():
            demand = flow['bw']
            previous_alloc = alloc[fid]
            capped_alloc = min(demand, previous_alloc)
            new_alloc[fid] = capped_alloc

            if capped_alloc >= demand:
                satisfied.add(fid)
                leftover += max(0, previous_alloc - demand)

        alloc = new_alloc.copy()

        # Step 3: Redistribute leftover equally among unsatisfied flows
        unsatisfied_flows = [fid for fid in flows if fid not in satisfied]
        if not unsatisfied_flows or leftover == 0:
            break

        equal_share = leftover / len(unsatisfied_flows)
        for fid in unsatisfied_flows:
            alloc[fid] += equal_share

    # Step 4: Calculate results
    result = {}
    loss_rates = []
    for fid, flow in flows.items():
        bw = flow['bw']
        profit = flow['profit']
        allocated = alloc[fid]
        delivered_ratio = min(1.0, allocated / bw)

        profit_gain = delivered_ratio * profit
        profit_loss = profit - profit_gain
        percent_loss = 1 - delivered_ratio
        loss_rates.append(percent_loss)

        result[fid] = {
            'allocated_bw': round(allocated, 4),
            'profit_gain': round(profit_gain, 4),
            'profit_loss': round(profit_loss, 4),
            'percent_profit_loss': round(percent_loss, 4)
        }

    # Jain's fairness index on loss rates
    n = len(loss_rates)
    sum_loss = sum(loss_rates)
    sum_loss_sq = sum(lr ** 2 for lr in loss_rates)
    jain_index = (sum_loss ** 2) / (n * sum_loss_sq) if sum_loss_sq != 0 else 1.0

    result['jain_index'] = round(jain_index, 4)
    return result

def profit_proportional_equal_distribution_with_loss_guarantee(flows: dict, link_capacity: float, cap: float):
    """
    Method 7: Profit Proportional Allocation + Equal Redistribution of Remaining Bandwidth + Loss guarantee
    When jain's indicate not fair, set soft max percent PLR on the bw a flow can get.
    When continue not fair, make the percent larger.

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
    # Step 1: Initial profit proportional allocation
    total_profit = sum(flow['profit'] for flow in flows.values())
    alloc = {}
    remaining_bw = link_capacity

    for fid, flow in flows.items():
        if total_profit > 0:
            alloc[fid] = (flow['profit'] / total_profit) * link_capacity
        else:
            alloc[fid] = 0

    current_max_bw = {}
    for fid, flow in flows.items(): # limit allocation to avoid unfairness.
        current_max_bw[fid] = flow["bw"] *(1-cap)
        if alloc[fid] > current_max_bw[fid]:
            alloc[fid] = current_max_bw[fid]
        

    # Step 2: Cap to flow demand and track unused bandwidth
    satisfied = set()
    while True:
        leftover = 0
        new_alloc = {}

        for fid, flow in flows.items():
            demand = flow['bw']
            previous_alloc = alloc[fid]
            capped_alloc = min(demand*(1-cap), previous_alloc)
            new_alloc[fid] = capped_alloc

            if capped_alloc >= demand*(1-cap):
                satisfied.add(fid)
                leftover += max(0, previous_alloc - new_alloc[fid])

        alloc = new_alloc.copy()

        # Step 3: Redistribute leftover equally among unsatisfied flows
        unsatisfied_flows = [fid for fid in flows if fid not in satisfied]
        if not unsatisfied_flows or leftover == 0:
            break

        equal_share = leftover / len(unsatisfied_flows)
        for fid in unsatisfied_flows:
            alloc[fid] += equal_share

    # Step 4: Calculate results
    result = {}
    loss_rates = []
    for fid, flow in flows.items():
        bw = flow['bw']
        profit = flow['profit']
        allocated = alloc[fid]
        delivered_ratio = min(1.0, allocated / bw)

        profit_gain = delivered_ratio * profit
        profit_loss = profit - profit_gain
        percent_loss = 1 - delivered_ratio
        loss_rates.append(percent_loss)

        result[fid] = {
            'allocated_bw': round(allocated, 4),
            'profit_gain': round(profit_gain, 4),
            'profit_loss': round(profit_loss, 4),
            'percent_profit_loss': round(percent_loss, 4)
        }

    # Jain's fairness index on loss rates
    n = len(loss_rates)
    sum_loss = sum(loss_rates)
    sum_loss_sq = sum(lr ** 2 for lr in loss_rates)
    jain_index = (sum_loss ** 2) / (n * sum_loss_sq) if sum_loss_sq != 0 else 1.0

    result['jain_index'] = round(jain_index, 4)
    if jain_index <= 0.8:
        print (f"Old cap: {cap}, New Cap: {cap + 0.03}")
        cap += 0.03
        result = profit_proportional_equal_distribution_with_loss_guarantee(flows, link_capacity, cap)

    return result

def max_min_fair_allocation(flows: dict, link_capacity: float):
    """
    Method 3: Max-Min Fair Allocation

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
    # Step 1: Initialize
    allocated = {fid: 0.0 for fid in flows}
    remaining_bw = link_capacity
    remaining_flows = set(flows.keys())

    while remaining_flows and remaining_bw > 0:
        fair_share = remaining_bw / len(remaining_flows)
        new_remaining_flows = set()

        for fid in remaining_flows:
            demand = flows[fid]['bw']
            already_alloc = allocated[fid]
            needed = demand - already_alloc

            # Allocate either what's needed or fair share
            alloc = min(fair_share, needed)
            allocated[fid] += alloc
            remaining_bw -= alloc

            # If not fully satisfied, keep for next round
            if allocated[fid] < demand:
                new_remaining_flows.add(fid)

        # Update the set of flows to be processed
        remaining_flows = new_remaining_flows

        # Edge case: if no bandwidth left, break early
        if remaining_bw <= 1e-6:
            break

    # Step 2: Compute results
    result = {}
    loss_rates = []
    for fid, flow in flows.items():
        demand = flow['bw']
        profit = flow['profit']
        alloc = allocated[fid]
        delivered_ratio = min(1.0, alloc / demand) if demand > 0 else 1.0

        profit_gain = delivered_ratio * profit
        profit_loss = profit - profit_gain
        percent_loss = 1 - delivered_ratio
        loss_rates.append(percent_loss)

        result[fid] = {
            'allocated_bw': round(alloc, 4),
            'profit_gain': round(profit_gain, 4),
            'profit_loss': round(profit_loss, 4),
            'percent_profit_loss': round(percent_loss, 4)
        }

    # Step 3: Jain's fairness index over profit loss rates
    n = len(loss_rates)
    sum_loss = sum(loss_rates)
    sum_sq = sum(l ** 2 for l in loss_rates)
    jain_index = (sum_loss ** 2) / (n * sum_sq) if sum_sq != 0 else 1.0

    result['jain_index'] = round(jain_index, 4)
    return result

def same_profit_loss_rate_allocation(flows: dict, link_capacity: float):
    """
    Method 4: Same Profit Loss Rate Allocation (equal loss ratio across flows)

    Args:
        flows (dict): {flow_id: {'bw': float, 'profit': float}}
        link_capacity (float): total available bandwidth in Mbps

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
    # Total demand
    total_demand = sum(flow['bw'] for flow in flows.values())
    
    # Loss rate: all flows will lose the same % of profit, i.e., same packet loss rate
    if total_demand == 0:
        r = 1.0  # fully satisfied trivially
    else:
        r = min(1.0, link_capacity / total_demand)

    result = {}
    loss_rates = []

    for fid, flow in flows.items():
        demand = flow['bw']
        profit = flow['profit']
        alloc = r * demand

        delivered_ratio = min(1.0, alloc / demand) if demand > 0 else 1.0
        profit_gain = delivered_ratio * profit
        profit_loss = profit - profit_gain
        percent_loss = 1 - delivered_ratio

        result[fid] = {
            'allocated_bw': round(alloc, 4),
            'profit_gain': round(profit_gain, 4),
            'profit_loss': round(profit_loss, 4),
            'percent_profit_loss': round(percent_loss, 4)
        }

        loss_rates.append(percent_loss)

    # Jain's fairness index on profit loss rates
    n = len(loss_rates)
    sum_loss = sum(loss_rates)
    sum_sq = sum(l ** 2 for l in loss_rates)
    jain_index = (sum_loss ** 2) / (n * sum_sq) if sum_sq != 0 else 1.0

    result['jain_index'] = round(jain_index, 4)
    return result

def same_profit_loss_allocation(flows: dict, link_capacity: float, reserved_portion: float=0.3):
    """
    Method 5: Same Profit Loss Method (updated)
    - All flows lose the same absolute amount of profit (up to their limit).
    - Ensures bandwidth allocation does not exceed demand.
    - Jain's fairness index is calculated on profit loss *rate* (percentage).
    """    
    # 1. calculate reserved_allocation_bw
    # 2. deduct from link_capacity and each flows demanding bw.
    # 3. calculate same p loss and calculate each allocation bw
    # 4. calculate the percentage of each allocate bw
    # 5. add back reserved bw to allocation
    # 6. calculate Jain's based on fully allocated numbers
    
    
    # 1. calculate reserved_allocation_bw
    
    c = link_capacity * 1.00001  # small epsilon to avoid float precision issues
    org_link_capacity = link_capacity
    org_flows = copy.deepcopy(flows) # does operation on flows_op
    reserved_allocation_bw = link_capacity * reserved_portion
    
    # 2. deduct from link_capacity and each flows demanding bw.
    
    pre_alloc = round( reserved_allocation_bw/len(flows) , 4)
    c = c - reserved_allocation_bw
    for fid in flows.keys():
        if  flows[fid]["bw"]  > pre_alloc:
            flows[fid]["bw"] = flows[fid]["bw"]  - pre_alloc
            flows[fid]["profit"] = flows[fid]["profit"]*(1- round(pre_alloc/flows[fid]["bw"],4))
        else:
            flows[fid]["bw"] = 0
            flows[fid]["profit"] = 0
    
    def calculate_loss(c, flows):
        sum_bw = 0.0
        denominator = 0.0
        for flow in flows.values():
            bw = flow["bw"]
            profit = flow["profit"]
            sum_bw += bw
            if profit > 0:
                denominator += bw / profit
        if denominator == 0:
            return 0.0
        return max(0.0, (sum_bw - c) / denominator)

    
    raw_loss = calculate_loss(c, flows)

    result = {}
    tmp_result = {}
    loss_rates = []
    total_allocated_bw = 0.0

    for fid, flow in flows.items():
        # 3. calculate same p loss and calculate each allocation bw
        # 4. calculate the percentage of each allocate bw
        bw = flow["bw"]
        profit = flow["profit"]

        # Cap the loss at the profit value
        loss = min(raw_loss, profit)
        alloc_ratio = max(0.0, min(1.0, 1.0 - (loss / profit))) if profit > 0 else 0.0
        allocated_bw = min(bw, round(bw * alloc_ratio, 4))

        profit_gain = max(0.0, round(profit - loss, 4))
        profit_loss = round(profit - profit_gain, 4)
        percent_loss = round(profit_loss / profit, 4) if profit > 0 else 1.0

        tmp_result[fid] = {
            "allocated_bw": allocated_bw,
            "profit_gain": profit_gain,
            "profit_loss": profit_loss,
            "percent_profit_loss": percent_loss
        }

        loss_rates.append(percent_loss)
        total_allocated_bw += allocated_bw

    # Correct Jain's Index on profit loss *rate*
    n = len(loss_rates)
    sum_r = sum(loss_rates)
    sum_r_sq = sum(r ** 2 for r in loss_rates)
    jain_index = round((sum_r ** 2) / (n * sum_r_sq), 4) if sum_r_sq != 0 else 1.0
    result["jain_index"] = jain_index

    # Print debug info
    extra_bw = round(link_capacity - total_allocated_bw, 4)
    print(f"[DEBUG] Total allocated bandwidth: {total_allocated_bw} Mbps")
    print(f"[DEBUG] Extra bandwidth remaining: {extra_bw} Mbps")
    print(f"[DEBUG] Jain's fairness index (on loss rate): {jain_index}")

    return result

def same_profit_loss_allocation_2(flows, link_capacity, reserved_portion = 0.333):
    """
    Same Profit Loss Allocation Algorithm (Python 2 Compatible)
    Args:
        flows: {flow_id: {'bw': float, 'profit': float}}
        link_capacity: float (total link capacity in Mbps)
    Returns:
        result dict (with allocation and Jain's fairness index)
    """
    print ("Running: same_profit_loss_allocation_2")
    # ---------- Phase 1 ----------
    portion1 = link_capacity * reserved_portion
    num_flows = len(flows)
    per_flow_alloc = portion1 / num_flows
    allocated_phase1 = {}
    remaining_link_capacity = link_capacity * (1 - reserved_portion)
    remaining_flows = {}

    for fid in flows:
        f = flows[fid]
        demand_bw = f["bw"]
        profit = f["profit"]
        alloc = min(per_flow_alloc, demand_bw)
        allocated_phase1[fid] = alloc

        if per_flow_alloc > demand_bw:
            remaining_link_capacity += per_flow_alloc - demand_bw

        remaining_bw = max(0.0, demand_bw - alloc)
        remaining_profit = (remaining_bw / demand_bw) * profit if demand_bw > 0 else 0.0
        
        remaining_flows[fid] = {
            'remaining_bw': remaining_bw,
            'remaining_profit': remaining_profit,
            'original_bw': demand_bw,
            'original_profit': profit
        }

    # ---------- Phase 2 ----------
    # Calculate_same loss
    sum_remain_bw = sum([remaining_flows[fid]['remaining_bw'] for fid in remaining_flows])
    sum_bw_over_profit = sum([
        remaining_flows[fid]['remaining_bw'] / remaining_flows[fid]['original_profit']
        for fid in remaining_flows if remaining_flows[fid]['original_profit'] > 0
    ])
    if sum_bw_over_profit > 0:
        L = (sum_remain_bw - remaining_link_capacity) / sum_bw_over_profit
    else:
        L = 0.0

    phase2_alloc = {}
    total_loss_bw = 0.0

    for fid in remaining_flows:
        f = remaining_flows[fid]
        rem_bw = f['remaining_bw']
        profit = f['original_profit']
        if profit <= L: 
            # fair profit loss L larger than profit of flow.
            # need to let other flows loss this portion of bw.
            phase2_alloc[fid] = 0.0
            extra_loss = L - profit
            if profit > 0:
                total_loss_bw += (extra_loss / profit) * f['remaining_bw']
        else:
            alloc = rem_bw * (1.0 - L / profit)
            phase2_alloc[fid] = alloc

    # ---------- Redistribute total_loss_bw ----------
    redistributable = dict((fid, bw) for fid, bw in phase2_alloc.items() if bw > 0)
    sum_redistributable = sum(redistributable.values())
    for fid in redistributable:
        if sum_redistributable > 0:
            share = redistributable[fid] / sum_redistributable
        else:
            share = 0.0
        phase2_alloc[fid] = phase2_alloc[fid] - share * total_loss_bw

    # ---------- Combine Phase 1 + Phase 2 ----------
    result = {}
    percent_loss_list = []

    for fid in flows:
        bw1 = allocated_phase1.get(fid, 0.0)
        bw2 = max(0.0, phase2_alloc.get(fid, 0.0))
        total_alloc = round(bw1 + bw2, 4)
        demand = flows[fid]["bw"]
        profit = flows[fid]["profit"]
        if demand > 0:
            delivered_ratio = total_alloc / demand
        else:
            delivered_ratio = 1.0
        percent_loss = max(0.0, 1.0 - delivered_ratio)
        profit_gain = profit * delivered_ratio
        profit_loss = profit - profit_gain
        percent_loss_list.append(percent_loss)

        result[fid] = {
            "allocated_bw": total_alloc,
            "profit_gain": round(profit_gain, 4),
            "profit_loss": round(profit_loss, 4),
            "percent_profit_loss": round(percent_loss, 4)
        }

    # ---------- Jain's Fairness Index ----------
    n = len(percent_loss_list)
    sum_x = sum(percent_loss_list)
    sum_x_sq = sum([x ** 2 for x in percent_loss_list])
    if sum_x_sq > 0:
        jain_index = (sum_x ** 2) / (n * sum_x_sq)
    else:
        jain_index = 1.0
    result["jain_index"] = round(jain_index, 4)

    return result

# Fixing iteritems for Python 3 compatibility
def same_profit_loss_allocation_3(flows, link_capacity,reserved_portion = 0.333):
    # ---------- Phase 1: Equal Initial Allocation ----------
    portion1 = link_capacity * reserved_portion 
    per_flow_alloc = portion1 / len(flows)
    allocated_phase1 = {}
    remaining_link_capacity = link_capacity * (1 - reserved_portion)
    remaining_flows = {}

    for fid, f in flows.items():
        demand_bw = f["bw"]
        profit = f["profit"]
        alloc = min(per_flow_alloc, demand_bw)
        allocated_phase1[fid] = alloc

        if per_flow_alloc > demand_bw:
            remaining_link_capacity += per_flow_alloc - demand_bw

        remaining_bw = max(0.0, demand_bw - alloc)
        remaining_profit = (remaining_bw / demand_bw) * profit if demand_bw > 0 else 0.0

        remaining_flows[fid] = {
            'remaining_bw': remaining_bw,
            'remaining_profit': remaining_profit,
            'original_bw': demand_bw,
            'original_profit': profit
        }

    # ---------- Phase 2: Calculate Equal Profit Loss L ----------
    sum_remain_bw = sum([f['remaining_bw'] for f in remaining_flows.values()])
    sum_bw_over_profit = sum(
        f['remaining_bw'] / f['original_profit']
        for f in remaining_flows.values()
        if f['original_profit'] > 0
    )

    L = (sum_remain_bw - remaining_link_capacity) / sum_bw_over_profit if sum_bw_over_profit > 0 else 0.0

    phase2_alloc = {}
    total_loss_bw = 0.0

    for fid, f in remaining_flows.items():
        rem_bw = f['remaining_bw']
        profit = f['original_profit']
        if profit <= L:
            phase2_alloc[fid] = 0.0
            extra_loss = L - profit
            if profit > 0:
                total_loss_bw += (extra_loss / profit) * f['remaining_bw']
        else:
            alloc = rem_bw * (1 - L / profit)
            phase2_alloc[fid] = alloc

    # ---------- Phase 2.1: Redistribute Loss using reverse-efficiency while loop ----------
    while total_loss_bw > 1e-6:
        redistributable = dict((fid, bw) for fid, bw in phase2_alloc.items() if bw > 1e-6)
        if not redistributable:
            break

        reverse_efficiency = {}
        total_inverse_eff = 0.0

        # calculate reverse bw profit efficiency for each flow.
        for fid in redistributable:
            profit = flows[fid]["profit"]
            bw = flows[fid]["bw"]
            eff = profit / bw if bw > 0 else 1e-6
            rev_eff = 1.0 / eff  
            reverse_efficiency[fid] = rev_eff
            total_inverse_eff += rev_eff

        # distribute bw loss to flows using reverse importance of bw-profit efficiency 
        # lower bw-profit efficient flow is deducted more bw.
        to_deduct = {}
        for fid in redistributable:
            ratio = reverse_efficiency[fid] / total_inverse_eff if total_inverse_eff > 0 else 0.0
            deduction = ratio * total_loss_bw
            actual_deducted = min(phase2_alloc[fid], deduction)
            phase2_alloc[fid] -= actual_deducted
            to_deduct[fid] = deduction - actual_deducted

        total_loss_bw = sum(to_deduct.values())

    # ---------- Combine Results ----------
    result = {}
    percent_loss_list = []
    for fid in flows:
        bw1 = allocated_phase1.get(fid, 0)
        bw2 = max(0.0, phase2_alloc.get(fid, 0))
        total_alloc = round(bw1 + bw2, 4)
        demand = flows[fid]["bw"]
        profit = flows[fid]["profit"]
        delivered_ratio = total_alloc / demand if demand > 0 else 1.0
        percent_loss = max(0.0, 1 - delivered_ratio)
        profit_gain = profit * delivered_ratio
        profit_loss = profit - profit_gain
        percent_loss_list.append(percent_loss)

        result[fid] = {
            "allocated_bw": round(total_alloc, 4),
            "profit_gain": round(profit_gain, 4),
            "profit_loss": round(profit_loss, 4),
            "percent_profit_loss": round(percent_loss, 4)
        }

    # ---------- Jain Fairness Index ----------
    n = len(percent_loss_list)
    sum_x = sum(percent_loss_list)
    sum_x_sq = sum([x ** 2 for x in percent_loss_list])
    jain_index = (sum_x ** 2) / (n * sum_x_sq) if sum_x_sq != 0 else 1.0
    result["jain_index"] = round(jain_index, 4)

    return result




def print_data(data):
    # Extract Jain index and remove it from main dict

    jain_index = data.pop('jain_index')

    # Prepare data for tabulation
    table_data = []
    for flow_id, metrics in data.items():
        table_data.append([flow_id] + list(metrics.values()))

    headers = ['Flow_ID', 'Allocated_BW','Profit_Gain', 'Profit/Loss','Percent_Profit/Loss' ]
    print(tabulate(table_data, headers=headers, floatfmt=".4f"))
    print(f"\nJain Index: {jain_index:.4f}")

if __name__ == "__main__":
    
    # result = profit_proportional_allocation(case3, LINK_CAPACITY)
    # result2 = profit_proportional_with_equal_distribution(case3,LINK_CAPACITY)
    # data = same_profit_loss_allocation(case1, LINK_CAPACITY)

    # pprint(maxmin1)
    # pprint(maxmin2)
    # pprint(maxmin3)
    # pprint(same_profit_loss_rate_allocation(case1, LINK_CAPACITY))
    # pprint(same_profit_loss_rate_allocation(case2, LINK_CAPACITY))
    # pprint(same_profit_loss_rate_allocation(case3, LINK_CAPACITY))
        #result = profit_proportional_allocation(case3, LINK_CAPACITY)
    # profit_proportional_equal_distribution_with_loss_guarantee(case1, LINK_CAPACITY , 0)
    

    data = same_profit_loss_allocation_2(case1, LINK_CAPACITY,0.333)
    print_data(data)
    data = same_profit_loss_allocation_2(case2, LINK_CAPACITY,0.333)
    print_data(data)
    data = same_profit_loss_allocation_2(case3, LINK_CAPACITY,0.333)
    print_data(data)
    