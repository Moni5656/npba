%% [1] J. A. R. De Azua and M. Boyer, “Complete modelling of AVB in network calculus framework” in Proceedings of the 22nd International Conference on Real-Time Networks and Systems. Versaille, France: ACM Press, Oct. 2014, pp. 55–64.
% [2] R. Queck. Analysis of Ethernet AVB for automotive networks using network calculus. In Proc. of IEEE Int. Conf. on Vehicular Electronics and Safety(ICVES 2012). IEEE, 2012

% Implementation of Case Study [1] with the help of RTC Toolbox

classdef Flow < handle
   
    properties
        name 
        path % Array with links
        type % Flow type (A / B / NSR)
        periodic % periodic ("p") or non_periodic ("np")
        worst_case % worst case ("wc") or standard("nwc")
        mfs % frame size in byte for flow
        cmi % class measurement interval in s
        mif % max number of frames sent during one cmi
    end
    
    methods
        function obj = Flow(name, mfs, cmi, mif, path, type, periodic, worst_case)
            obj.name = strcat(name);
            obj.mfs = double(mfs);
            obj.cmi = double(cmi);
            obj.mif = double(mif);
            % Python hands over arguments through cell array
            if iscell(path)
                % convert from cell array to 'Link' array
                temp = Link.empty;
                for i=1:length(path)
                    temp(end+1) = path{i};
                end
                obj.path = temp;
            else
               obj.path = path; 
            end
            obj.type = type;
            obj.periodic = periodic;
            obj.worst_case = worst_case;
        end
        
        function result = get_type(self)
            result = self.type;
        end
    end
end