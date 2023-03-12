%% [1] J. A. R. De Azua and M. Boyer, “Complete modelling of AVB in network calculus framework” in Proceedings of the 22nd International Conference on Real-Time Networks and Systems. Versaille, France: ACM Press, Oct. 2014, pp. 55–64.
% [2] R. Queck. Analysis of Ethernet AVB for automotive networks using network calculus. In Proc. of IEEE Int. Conf. on Vehicular Electronics and Safety(ICVES 2012). IEEE, 2012

% Implementation of Case Study [1] with the help of RTC Toolbox

classdef CBS < handle
   
    properties
       l_a_max % max frame size for class A in bit
       l_b_max % max frame size for class B in bit
       l_nsr_max % max frame size for class NSR in bit
       l_n_max % max{l_b_max, l_nsr_max} in bit
       is_strict % boolean, True = use strict_min_service_curve
       flows % array with every flow
    end
    
    methods
        %% Paper functions
        function obj = CBS(l_a_max, l_b_max, l_nsr_max, is_strict, flows)
            obj.l_a_max = double(l_a_max * 8);
            obj.l_b_max = double(l_b_max * 8);
            obj.l_nsr_max = double(l_nsr_max * 8);
            obj.l_n_max = max(obj.l_b_max, obj.l_nsr_max);
            obj.is_strict = is_strict;
            % arrays from Python are passed to matlab as a cell array
            if iscell(flows) 
                temp = Flow.empty;
                for i=1:length(flows) % loop through the cell array
                    temp(end+1) = flows{i}; %  add the flow i to a flow array
                end
                obj.flows = temp; % assign the array to the object
            else
                obj.flows = flows; % in case a flow array is given
            end
        end
        
        % Theorem 1
        function result = arrival_curve_periodic(~, flow)
            c = flow.path(1).c;
            m = flow.mif * flow.mfs * 8;
            r = m / flow.cmi;
            b = m *(1 - r / c);
           result = rtcmin(rtccurve([[0 b r]]),rtccurve([[0 0 c]])); 
        end
        
        % Theorem 1
        function result = arrival_curve_periodic_worst_case(~, flow)
           ct = rtccurve([[0 0 flow.path(1).c]]);
           m = flow.mif * flow.mfs * 8;
           result = rtcminconv(ct, rtctimes(m, rtcceil(rtccurve([[0 0 1/flow.cmi]]))));
        end
        
        % Theorem 2
        function result = arrival_curve_non_periodic(~, flow)
            c = flow.path(1).c;
            m = flow.mif * flow.mfs * 8;
            r = m / flow.cmi;
            b = m *(1 - r / c);
            result = rtcmin(rtccurve([[0 (2*b) r]]),rtccurve([[0 0 c]])); 
        end
        
        % Theorem 2
        function result = arrival_curve_non_periodic_worst_case(~, flow)
            ct = rtccurve([[0 0 flow.path(1).c]]);
            m = flow.mif * flow.mfs * 8;
            result = rtcminconv(ct, rtctimes(m, rtcceil(rtccurve([[0 1 1/flow.cmi]]))));
        end
        
        % Theorem 3, general formula
        function result = strict_minimal_service_curve_A(self, link)
            prod = (link.idsl_A * link.c ) / (link.idsl_A - link.sdsl_A);
            result = rtctimes(prod, rtcmax(0, rtccurve([[0 (-self.l_n_max / link.c - self.l_a_max *(link.c - link.idsl_A) / (link.idsl_A * link.c)) 1]])));
        end
        
        % Theorem 4, general formula
        function result = minimal_service_curve_A(self, link)
           prod = (link.idsl_A * link.c ) / (link.idsl_A - link.sdsl_A);
           result = rtctimes(prod, rtcmax(0, rtccurve([[0 (-self.l_n_max / link.c) 1]])));
        end
        
        % Theorem 5, general formula
        function result = shaper_curve_A(self, link)
            prod = (link.idsl_A * link.c ) / (link.idsl_A - link.sdsl_A);
            result = rtctimes(prod, rtccurve([[0 (self.l_n_max / link.c - self.l_a_max * link.sdsl_A / (link.idsl_A * link.c)) 1]]));
        end
        
        % Theorem 6, general formula
        function result = maximal_service_curve_A(self, link)
            prod = (link.idsl_A * link.c ) / (link.idsl_A - link.sdsl_A);
            result = rtctimes(prod, rtccurve([[0 (-self.l_a_max * link.sdsl_A / (link.idsl_A * link.c)) 1]]));
        end
        
        % Theorem 7, general formula
        function result = strict_minimal_service_curve_B(self, link)
            prod = (link.idsl_B * link.c) / (link.idsl_B - link.sdsl_B);
            sum = - (self.l_nsr_max + self.l_a_max) / link.c + (self.l_n_max * link.idsl_A )/ (link.c * link.sdsl_A) + (self.l_b_max * link.sdsl_B) / (link.c * link.idsl_B);
            result = rtctimes(prod, rtcmax(0, rtccurve([[0 sum 1]])));
        end
        
        % Theorem 8, general formula
        function result = minimal_service_curve_B(self, link)
            prod = (link.idsl_B * link.c) / (link.idsl_B - link.sdsl_B);
            result = rtctimes(prod, rtcmax(0, rtccurve([[0 (- (self.l_nsr_max + self.l_a_max) / link.c + (link.idsl_A * self.l_n_max) / (link.sdsl_A * link.c)) 1]])));
        end
        
        % Theorem 9, general formula
        function result = shaper_curve_B(self, link)
            prod = (link.idsl_B * link.c) / (link.idsl_B - link.sdsl_B);
            sum = (self.l_nsr_max + self.l_a_max) /link.c - (self.l_n_max * link.idsl_A) / (link.c * link.sdsl_A) - (self.l_b_max * link.sdsl_B) / (link.c * link.idsl_B);
            result = rtctimes(prod, rtccurve([[0 sum 1]]));
        end
        
        % Theorem 10, general formula
        function result = maximal_service_curve_B(self, link)
             prod = (link.idsl_B * link.c) / (link.idsl_B - link.sdsl_B);
             result = rtctimes(prod, rtccurve([[0 ((self.l_b_max * (link.c - link.idsl_B)) / (link.c * link.idsl_B)) 1]]));
        end
        
        %% Delay & Backlog functions
        
        % computes the index of a link in the flow
        function result = at_index( ~, flow, link_ )
            result = -1; % default value to indicate the link is not in the flow
            for cnt=1:length(flow.path) % loop through all the links in the path
                if flow.path(cnt) == link_ 
                    result = cnt;
                    break;
                end
            end
        end
        
        % computes all previous links for a given link
        % eg. a flow going from link i to link j. Link i is the previous
        % link of link j
        function result = previous_links(self, link, tr_type)
            result = Link.empty; % initialize the array with type link
            for flow=flows_link(self, link, tr_type)
                % get the index of link j in the path of the flow
                link_index = at_index(self, flow, link);
                if link_index == 1
                    continue
                end
                % get the link before link j (index -1)
                previous_link = flow.path(link_index-1);
                % check if the link is already saved in result
                if ~ismember(previous_link, result) % is not in list of previous links
                    result(end+1) = previous_link; % add to list of previous links
                end
            end
        end
        
        % get all flows passing through a link
        function result = flows_link( self, link_, tr_type)
            result = Flow.empty; % initialize a flow array
            for i=1:length(self.flows) % loop through all flows
                % check if link is part of flow -> -1 = not in the flow
                % and if link is of right traffic type
                if (at_index(self, self.flows(i), link_ ) ~= -1) & (self.flows(i).type == tr_type)
                    % link is on the flow's path -> add to result
                    result(end+1) = self.flows(i);
                end
            end
        end
        
        % computes the arrival curve of a flow in the source
        function result = arrival_curve_source(self, flow)
            % check if arrival curve is periodic
            if flow.periodic == "p"
                % check if arr_curve is worst case
                if flow.worst_case == "wc"
                    result = arrival_curve_periodic_worst_case(self, flow);
                else % not worst case
                    result = arrival_curve_periodic(self, flow);
                end
            else % arrival curve is non-periodic
                if flow.worst_case == "wc"
                    result = arrival_curve_non_periodic_worst_case(self, flow);
                else
                    result = arrival_curve_non_periodic(self, flow);
                end
            end
        end
        
        % compute the outgoing arrival curve of a link and a traffic class
        function result = arrival_curve_out( self, link_, tr_type )
            % get the incoming arrival curve
            arr_in = arrival_curve_in( self, link_, tr_type );
            
            % compute maximal service curve
            if tr_type == "A" % traffic type = A
                serv_max = maximal_service_curve_A(self, link_);
            else % traffic type = B
                serv_max = maximal_service_curve_B(self, link_);
            end
            
            % compute minimal service curve
            if self.is_strict % use strict minimal service curve
                if tr_type == "A" % traffic type = A
                    serv_min = strict_minimal_service_curve_A(self, link_);
                else % traffic type = B
                    serv_min = strict_minimal_service_curve_B(self, link_);
                end
            else
                if tr_type == "A" % traffic type = A
                    serv_min = minimal_service_curve_A(self, link_);
                else % traffic type = B
                    serv_min = minimal_service_curve_B(self, link_);
                end
            end
            
            % compute shaping_curve
             if tr_type == "A" % traffic type = A
                shaping_curve = shaper_curve_A(self, link_);
            else % traffic type = B
                shaping_curve = shaper_curve_B(self, link_);
             end
            
            try % convolution sometimes causes errors in the RTC toolbox
                arr_conv = rtcmindeconv(rtcminconv(arr_in, serv_max), serv_min); % compute convoluted curve
            catch % if error -> compute only mindeconvolution with minimal service
                warning('CUSTOM:Convolution', "Convolution is not possible, slightly inaccurate result at Link: %s", link_.name);
                arr_conv = rtcmindeconv(arr_in, serv_min); % compute convoluted curve
            end
            result = rtcmin(arr_conv, shaping_curve); %compute shaped curve
        end
        

        function result = flows_starting_at_link(self, link, traffic_type)
            result = Flow.empty;
            for flow=self.flows
                if flow.type == traffic_type && flow.path(1) == link
                    result(end+1) = flow;
                end
            end
        end


        % computes the incoming arrival curve of a link and a traffic class
        function result = arrival_curve_in( self, link_, tr_type)
            result = rtccurve([[0 0 0]]); % initialize result as a curve
            for flow = flows_starting_at_link(self, link_, tr_type)
                result = rtcplus(result, arrival_curve_source( self, flow));
            end
            % get all the previous links
            previous_links_ = previous_links(self, link_, tr_type); % list of previous links i (i->j, j->k)
            for i=1:length(previous_links_) % for each previous link
                % compute the outgoing arrival curve for each previous
                % link 
                result = rtcplus(result, arrival_curve_out( self, previous_links_(i), tr_type )); % sum of arrival_curves of links(i) out
            end
        end
        
        % computes the delay for a link and a traffic class
        function result = delay_link(self, link, tr_type, path_folder, net_name)
            % check if delay was already computed and saved to the link
            if tr_type == 'A' & link.delay_A ~= 0
                result = link.delay_A; % retrieve value if saved
            % check if delay was already computed and saved to the link
            elseif tr_type == 'B' & link.delay_B ~= 0
                result = link.delay_B; % retrieve value if saved
            else % compute if not computed before
                % get the incoming arrival curve
                arrival_curve_in_ = arrival_curve_in(self, link, tr_type);
                
                if self.is_strict % use strict minimal service curve
                    if tr_type == "A" % traffic type = A
                        serv_min = strict_minimal_service_curve_A(self, link);
                    else % traffic type = B
                        serv_min = strict_minimal_service_curve_B(self, link);
                    end
                else % use the minimal service curve
                    if tr_type == "A" % traffic type = A
                        serv_min = minimal_service_curve_A(self, link);
                    else % traffic type = B
                        serv_min = minimal_service_curve_B(self, link);
                    end
                end

                % plot the arrival curve in and the service curve using rtc toolbox
                % the value before 'LineWidth' defines the plotting range
                rtcplot(arrival_curve_in_, 'b--', serv_min, 'r--', 0.1, 'LineWidth', 1.5);
                result = rtcploth(arrival_curve_in_, serv_min);
                % name the plot
                title("Delay " + link.name + " Class " + tr_type);
                xlabel('Time in s');
                ylabel('Size in bit');
                % choose the correct service curve name
                if self.is_strict
                    serv_curve = "strict\_minimal\_service\_curve";
                else
                    serv_curve = "minimal\_service\_curve";
                end
                % add a legend to the plot
                legend({'arrival\_curve', serv_curve, "delay"}, 'Location', 'northwest');
                
                % save the computed delay to the link
                if tr_type == 'A'
                    link.delay_A = result;
                else % traffic is class B
                    link.delay_B = result;
                end

                % create the folder path for the plots, input from python
                path_plots = path_folder + "/" + net_name;
                path_fig = path_plots + "/Delay " + link.name + " Class " + tr_type;
                % save the plot as matlab .fig datatype
                savefig( path_fig )
            end
        end
        
        % computes the end to end delay for a flow
        function result = end_to_end_delay(self, flow, path_folder, net_name)
            % get all links the flow is passing
            links = flow.path;
            result = 0;
            for i=1:length(links) % loop through each link
                % compute the delay at the link and add the delays up
                result = result + delay_link(self, links(i), flow.type, path_folder, net_name);
            end
        end
        
        % computes the backlog at a link for a traffic class
        function result = backlog_link(self, link, tr_type, path_folder, net_name)
            % get the incoming arrival curve
            arrival_curve_in_ = arrival_curve_in(self, link, tr_type);
            
            
            if self.is_strict % use strict minimal service curve
                if tr_type == "A" % traffic type = A
                    serv_min = strict_minimal_service_curve_A(self, link);
                else % traffic type = B
                    serv_min = strict_minimal_service_curve_B(self, link);
                end
            else
                if tr_type == "A" % traffic type = A
                    serv_min = minimal_service_curve_A(self, link);
                else % traffic type = B
                    serv_min = minimal_service_curve_B(self, link);
                end
            end
            
            rtcplot(arrival_curve_in_, 'b--', serv_min, 'r--', 0.1, 'LineWidth', 1.5);
            result = rtcplotv(arrival_curve_in_, serv_min);
            title("Backlog " + link.name + " Class " + tr_type);
            xlabel('Time in s');
            ylabel('Size in bit');
            if self.is_strict
                serv_curve = "strict\_minimal\_service\_curve";
            else
                serv_curve = "minimal\_service\_curve";
            end
            legend({'arrival\_curve', serv_curve, "backlog"}, 'Location', 'northwest');

            % create path
            path_plots = path_folder + "/" + net_name;
            path_fig = path_plots + "/Backlog " + link.name + " Class " + tr_type;
            savefig( path_fig )
        end
        
    end
end