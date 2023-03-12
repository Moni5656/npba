import math

from ComputationMethods.CBS_CDT_ATS import components

# import components


"""
    Implementation of CBS NC models according to:

    [1]:  E. Mohammadpour, E. Stai, M. Mohiuddin, and J.-Y. Le Boudec. Latency and Backlog Bounds in Time-Sensitive 
          Networking with Credit Based Shapers and Asynchronous Traffic Shaping. In 2018 30th International Teletraffic 
          Congress (ITC 30), volume 2, pages 1–6. IEEE, 2018.
"""


class CBS:
    """
          Implementation of CBS_CDT_ATS Network Calculus Model [1], defined by:

          :param f: array of flows

      """

    def __init__(self, f):
        self.f = f

    # (1) & (3)
    def t_i_j(self, flow, link):
        r = 0
        b = 0
        cdt_flows = filter(lambda x: x.t == "CDT", self.f)
        for f in cdt_flows:
            if link in f.p:
                r = r + f.r
                b = b + f.l_max

        l_max_f = filter(lambda x: link in x.p and (x.t != "CDT"), self.f)
        l_max = 0
        for f in l_max_f:
            if f.l_max > l_max:
                l_max = f.l_max
        l_a_max = 0
        l_a_max_f = filter(lambda x: x.t != "A" and x.t != "CDT", self.f)
        for f in l_a_max_f:
            if f.l_max > l_a_max:
                l_a_max = f.l_max
        if flow.t == "A":
            return 1 / (link.c - r) * (l_a_max + b + (r * l_max) / link.c)
        elif flow.t == "B":
            l_be_max_f = filter(lambda x: x.t == "BE", self.f)
            l_be_max = 0
            for f in l_be_max_f:
                if f.l_max > l_be_max:
                    l_be_max = f.l_max
            l_a_f = filter(lambda x: x.t == "A", self.f)
            l_a = 0
            for f in l_a_f:
                if f.l_max > l_a:
                    l_a = f.l_max
            return 1 / (link.c - r) * (l_be_max + l_a - (l_a_max * link.idsl_a) / link.sdsl_a + b +
                                       (r * l_max) / link.c)

    # (2) & (4)
    def r_i_j(self, flow, link):
        r = -1
        cdt_flows = filter(lambda x: x.t == "CDT", self.f)
        for f in cdt_flows:
            if link in f.p:
                r = f.r
        if flow.t == "A":
            return link.idsl_a * (link.c - r) / (link.idsl_a - link.sdsl_a)
        elif flow.t == "B":
            return link.idsl_b * (link.c - r) / (link.idsl_b - link.sdsl_b)

    # (5)
    def s_i_j(self, flow, link):
        if flow.at == "LRQ":
            ψ_f = flow.l_max
        else:
            ψ_f = flow.l_min
        f_x = filter(lambda x: x.t == flow.t and link in x.p, self.f)
        b_tot = 0
        for f in f_x:
            b_tot += f.l_max
        t = self.t_i_j(flow, link)
        return t + (b_tot - ψ_f) / self.r_i_j(flow, link) + ψ_f / link.c + link.t_var_max

    # (7)
    def c_i_j_k(self, flow, link_ij, link_jk):
        f_x = filter(lambda x: x.t == flow.t and link_ij in x.p, self.f)
        b_tot = 0
        for f in f_x:
            b_tot += f.l_max
        sup = []
        for f in self.f:
            if link_ij in f.p:
                if f.t == flow.t and f.p.index(link_ij) + 1 < len(f.p):
                    if f.p[f.p.index(link_ij) + 1] == link_jk:
                        if f.at == "LRQ":
                            sup.append(f.l_max / link_ij.c - f.l_max / self.r_i_j(flow, link_ij))
                        else:
                            sup.append(f.l_min / link_ij.c - f.l_min / self.r_i_j(flow, link_ij))
        return self.t_i_j(flow, link_ij) + b_tot / self.r_i_j(flow, link_ij) + link_ij.t_var_max + max(sup) + \
               link_ij.t_proc_max

    # (9)
    def end_to_end_delay(self, flow):
        sum_c = 0
        for link in flow.p:
            if flow.p.index(link) == len(flow.p) - 1:
                break
            sum_c += self.c_i_j_k(flow, link, flow.p[flow.p.index(link) + 1])
        return sum_c + self.s_i_j(flow, flow.p[-1])

    # (8)
    def h_i_j_k(self, flow, link_ij, link_jk):
        return self.c_i_j_k(flow, link_ij, link_jk) - flow.l_max / link_ij.c - link_ij.t_var_min - link_jk.t_proc_min

    # (11)
    def backlog_interleaved_regulator(self, flow, link_ij, link_jk):
        sup = []
        bs = 0
        rs = 0
        bw = 0
        d_i_j_k = []
        for f in self.f:
            if link_ij in f.p:
                if f.t == flow.t and f.p.index(link_ij) + 1 < len(f.p):
                    if f.p[f.p.index(link_ij) + 1] == link_jk:
                        sup.append(f.l_max)
                        bs += f.l_max
                        rs += f.r
                        d_i_j_k.append(self.h_i_j_k(flow, link_ij, link_jk))

        return min(link_ij.c * max(d_i_j_k) + max(sup), rs * max(d_i_j_k) + bs + rs *
                   (self.t_i_j(flow, link_ij) + bw / self.r_i_j(flow, link_ij)))

    # (12)
    def backlog_cbfs(self, t, link_ij):
        b = 0
        r_t = 0
        for f in self.f:
            if link_ij in f.p and f.t == t:
                b += f.l_max
                r_t += f.r * self.t_i_j(f, link_ij)
        return b + r_t


# recreate case study
if __name__ == '__main__':
    idsl = 50 * math.pow(10, 6)
    sdsl = -50 * math.pow(10, 6)
    c = 100 * math.pow(10, 6)

    f1 = components.Flow(20 * math.pow(10, 6), 1000, 1000,
                         [components.Link("H1", "1", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("1", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("2", "3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("3", "4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("4", "H4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0)]
                         , "A", "LRQ")

    f2 = components.Flow(20 * math.pow(10, 6), 2000, 2000,
                         [components.Link("H1", "1", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("1", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("2", "H2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0)]
                         , "A", "LRQ")

    f3 = components.Flow(20 * math.pow(10, 6), 2000, 2000,
                         [components.Link("H3", "3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("3", "4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("4", "5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("5", "H5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0)]
                         , "A", "LRQ")

    f4 = components.Flow(20 * math.pow(10, 6), 2000, 2000,
                         [components.Link("H4", "4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("4", "5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("5", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("2", "H2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0)]
                         , "A", "LRQ")

    f5 = components.Flow(20 * math.pow(10, 6), 2000, 2000,
                         [components.Link("H5", "5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("5", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("2", "3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("3", "H3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0)]
                         , "A", "LRQ")

    cdt = components.Flow(20 * math.pow(10, 6), 4000, 4000,
                          [components.Link("H1", "1", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("1", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("2", "3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("3", "H3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("H3", "3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("3", "4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("4", "H4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("H4", "4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("4", "5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("5", "H5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("H5", "5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("5", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("2", "H2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                           components.Link("H2", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0)
                           ], "CDT", "LB")

    be = components.Flow(20 * math.pow(10, 6), 2000, 2000,
                         [components.Link("H1", "1", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("1", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("2", "3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("3", "H3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("H3", "3", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("3", "4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("4", "H4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("H4", "4", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("4", "5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("5", "H5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("H5", "5", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("5", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("2", "H2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0),
                          components.Link("H2", "2", c, idsl, sdsl, 0, 0, 0, 0, 0, 0)]
                         , "BE", "LB")
    flows = [f1, f2, f3, f4, f5, cdt, be]
    cbs = CBS(flows)
    print("Response time for f1 in H1: " + str(cbs.s_i_j(f1, f1.p[0])) + "s")
    print("Response time for f1 in 4: " + str(cbs.s_i_j(f1, f1.p[4])) + "s")
    print("End to end delay for f1: " + str(cbs.end_to_end_delay(f1)) + "s")
    print("Backlog for interleaved regulator at 1 for f1: " + str(
        cbs.backlog_interleaved_regulator(f1, f1.p[0], f1.p[1])) + " bit")
    print("Backlog for CBFS in H1 for class A: " + str(cbs.backlog_cbfs("A", f1.p[0])) + " bit")
    print("Response time in interleaved regulator at 1 for f1: " + str(cbs.h_i_j_k(f1, f1.p[0], f1.p[1])) + "s")
