%% [1] J. A. R. De Azua and M. Boyer, “Complete modelling of AVB in network calculus framework” in Proceedings of the 22nd International Conference on Real-Time Networks and Systems. Versaille, France: ACM Press, Oct. 2014, pp. 55–64.
% [2] R. Queck. Analysis of Ethernet AVB for automotive networks using network calculus. In Proc. of IEEE Int. Conf. on Vehicular Electronics and Safety(ICVES 2012). IEEE, 2012

% Implementation of Case Study [1] with the help of RTC Toolbox

classdef Link < handle
   
    properties
        name
        i % Portname i of link (i, j)
        j % Portname j of link (i, j)
        c % transmission speed in bit/s
        idsl_A % idle slope of class A in bit/s
        idsl_B % idle slope of class B in bit/s
        sdsl_A % send slope of class A in bit/s
        sdsl_B % send slope of class B in bit/s
        delay_A % delay of class A
        delay_B % delay of class B
    end
    
    methods
        function obj = Link(name, i, j, c, idsl_A, sdsl_A, idsl_B, sdsl_B)
            obj.name = strcat(name);
            obj.i = strcat(i);
            obj.j = strcat(j);
            obj.c = double(c);
            obj.idsl_A = double(idsl_A);
            obj.sdsl_A = double(sdsl_A);
            obj.idsl_B = double(idsl_B);
            obj.sdsl_B = double(sdsl_B);
            delay_A = 0;
            delay_B = 0;
        end
        
        function result = get_i(self)
            result = self.i;
        end
    end
end