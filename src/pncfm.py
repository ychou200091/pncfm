from scipy.optimize import minimize_scalar

def maximize_nbs(d_A, d_B, p_A, p_B, s, c):

    def v_A( x, d_A):
        """Normalized utility for Domain A."""
        # x: possible bw allocation to domain A
        return round( x/d_A, 8)
        # return round( p_A*x/d_A, 8)

    def v_B(x, d_A, d_B, p_A, p_B, s, c):
        """Normalized utility for Domain B."""

        '''
        parameteres:
        x: possible bw allocation to domain A
        d_A: domain A flow bw request.
        d_B: domain B current bw usage.
        p_A: domain A flow profit
        p_B: domain B flow profit
        s: domain A flow profit slice (portion of profit welling to give to domain B)
        c: link capacity
        '''
        x = c-d_B if c-x > d_B else x
        num = (c-x)/d_B + s*p_A*x/p_B/d_A
        return num - 1.0
        # num = p_B*(c-x)/d_B + s*p_A*x/d_A
        # return num - p_B


    def nbs_obj( x, d_A, d_B, p_A, p_B, s, c):
        if x < 0.0 or x > min(c, d_A):
            return float('-inf')
        
        return  -1.0* v_A(x, d_A) * v_B(x, d_A, d_B, p_A, p_B, s, c)

    # print("==========================")
    # print("NBS:")
    # print("d_A=%s, d_B=%s, p_A=%s, p_B=%s, s=%s, c=%s" % (d_A, d_B, p_A, p_B, s, c))

    '''
    parameteres:
    x: possible bw allocation to domain A
    d_A: domain A flow bw request.
    d_B: domain B current bw usage.
    p_A: domain A flow profit
    p_B: domain B flow profit
    s: domain A flow profit slice (portion of profit welling to give to domain B)
    c: link capacity
    '''
    """Find the x that maximizes the Nash product using scipy."""
    print "c:",c, "d_A:",d_A,"d_B:", d_B, "p_A:", p_A, "p_B:",p_B,"s:", s
    res = minimize_scalar(
        lambda x: nbs_obj(x, d_A, d_B, p_A, p_B, s,c),
        bounds=(0.0, min(c, d_A)),
        method='bounded'
    )
    # print("result: %.4f" %res.x)
    # print("==========================")
    if res.success:
        return round(res.x,6), -res.fun
    else:
        return 0.0, float('-inf')
