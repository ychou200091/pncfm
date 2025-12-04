import pncfm

''' 
********************************************************
Nash Bargaining Siumulation
********************************************************
'''

def nash_bargaining_simu():
    c = 10.0      # Link capacity
    d_a = 8     # Domain A flow demand
    d_b = 7.0     # Domain B existing flow demand
    p_a = 80.0    # Domain A flow profit
    p_b = 80.0   # Domain B total profit
    s = 0.75       # Slice ratio

    x_star, nbs_val = pncfm.maximize_nbs(d_a, d_b, p_a, p_b, s ,c)

    print("Optimal bandwidth to allocate to Domain A's flow: %.4f Mbps" % x_star)
    print("Maximum Nash Bargaining value: %.6f" % nbs_val)
    gain_a = p_a*(1.0-s)*x_star/d_a
    print("Profit Gain for domain A: %.4f" %  gain_a)
    print("Profit Gain of flow A for domain B: %.4f" % (p_a*(s)*x_star/d_a))
    gain_b = min((c - x_star),d_b)/d_b * p_b +  p_a*(s)*x_star/d_a
    print("Profit Gain for domain B: %.4f" % (gain_b))
    print("domain a + domain b gain = %.6f"%(gain_a + gain_b))


if __name__ == "__main__":
    
    nash_bargaining_simu()
    