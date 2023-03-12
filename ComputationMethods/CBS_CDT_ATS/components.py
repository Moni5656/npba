"""
    Useful components.
    [1]:  E. Mohammadpour, E. Stai, M. Mohiuddin, and J.-Y. Le Boudec. Latency and Backlog Bounds in Time-Sensitive 
          Networking with Credit Based Shapers and Asynchronous Traffic Shaping. In 2018 30th International Teletraffic 
          Congress (ITC 30), volume 2, pages 1–6. IEEE, 2018.
          
"""


class Flow:
    def __init__(self, r, l_min, l_max, p, t, at):
        """
        Constructor of a Flow for [1] defined by:

        :param r: regulation rate of every flow in bit/s
        :param l_min: minimum packet length in bit
        :param l_max: maximum packet length in bit
        :param p: path array with links
        :param t: type CDT / A / B / BE
        :param at: arrival curve type LRQ / LB
        """
        self.r = r
        self.p = p
        self.l_min = l_min
        self.l_max = l_max
        self.t = t
        self.at = at


class Link:
    def __init__(self, i, j, c, idsl_a, sdsl_a, idsl_b, sdsl_b, t_var_min, t_var_max, t_proc_min, t_proc_max):
        """
        Constructor of a Link for [1] defined by:

        :param i: port of node i
        :param j: port of node j
        :param c: transmission rate in bit/s
        :param idsl_a: idle slope of class A in bit
        :param sdsl_a: send slope of class A in bit
        :param idsl_b: idle slope of class B in bit
        :param sdsl_b: send slope of class B in bit
        :param t_var_min: minimal ? time in s
        :param t_var_max: maximal ? time in s
        :param t_proc_min: minimal switch processing time in s
        :param t_proc_max: maximal switch processing time in s
        """
        self.i = str(i)
        self.j = str(j)
        self.c = float(c)
        self.idsl_a = float(idsl_a)
        self.sdsl_a = float(sdsl_a)
        self.idsl_b = float(idsl_b)
        self.sdsl_b = float(sdsl_b)
        self.t_var_min = float(t_var_min)
        self.t_var_max = float(t_var_max)
        self.t_proc_min = float(t_proc_min)
        self.t_proc_max = float(t_proc_max)

    def __eq__(self, other):
        if not isinstance(other, Link):
            raise Exception("Can't be compared with other classes")
        # According to [1] a link (i,j) is the same as (j,i) to get the same results as the case study
        return ((self.i == other.i and self.j == other.j) or (self.i == other.j and self.j == other.i)) and self.c == \
               other.c and self.idsl_a == other.idsl_a and self.sdsl_a == other.sdsl_a and self.idsl_b == other.idsl_b \
               and self.sdsl_b == other.sdsl_b and self.t_proc_max == other.t_proc_max and \
               self.t_var_min == other.t_var_min and self.t_proc_min == other.t_proc_min and \
               self.t_var_max == other.t_var_max
