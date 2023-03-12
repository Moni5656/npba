from typing import Optional

from Model.Network.Flow import Flow
from Model.Network.Node import Node
from View.GUI.Windows.GraphWindow.FlowView.FlowPartView import FlowPartView
from View.GUI.Windows.GraphWindow.FlowView.GroupedFlowPartView import GroupedFlowPartView
from View.Observer import Observer


class FlowPartManager(Observer):
    active_flow_manager = {}
    GROUPED_FLOW_INDEX = 4

    def __init__(self, canvas, start: Node, end: Node):
        FlowPartManager.active_flow_manager[(canvas, start, end)] = self
        self.start_node = start
        self.end_node = end
        self.canvas = canvas
        self.flow_parts = {}
        self.slots: list[Optional[FlowPartView, GroupedFlowPartView]] = [None] * FlowPartManager.GROUPED_FLOW_INDEX

        Observer.__init__(self, start)
        end.subscribe(self)

    def update_(self, updated_component):
        if isinstance(updated_component[0], Node):
            if updated_component[1] == "set_parameter":
                for flow_part_view in self.slots:
                    if flow_part_view is None:
                        continue
                    flow_part_view.draw_flow()

    def add_flow(self, flow: Flow):
        """
        Adds a flow to the manager drawing and managing it.

        :param flow: flow object
        """
        radius = self.get_next_free_radius()
        if radius == FlowPartManager.GROUPED_FLOW_INDEX - 1:
            slot = self.slots[radius]
            if slot is None:
                flow_part_view = FlowPartView(self.canvas, flow, self.start_node, self.end_node, radius)
                self.flow_parts[flow] = flow_part_view
                self.slots[radius] = flow_part_view
            elif isinstance(slot, FlowPartView):
                flow_to_move = slot.flow
                slot.delete_from_canvas()
                grouped_view = GroupedFlowPartView(self.canvas, self.start_node, self.end_node, radius)
                grouped_view.add(flow_to_move)
                self.flow_parts[flow_to_move] = grouped_view
                self.slots[radius] = grouped_view

                grouped_view.add(flow)
                self.flow_parts[flow] = grouped_view
            elif isinstance(slot, GroupedFlowPartView):
                slot.add(flow)
                self.flow_parts[flow] = slot
        else:
            flow_part_view = FlowPartView(self.canvas, flow, self.start_node, self.end_node, radius)
            self.flow_parts[flow] = flow_part_view
            self.slots[radius] = flow_part_view

    def redraw_flow(self, flow: Flow):
        """
        Redraws a flow.

        :param flow: flow object
        """
        self.flow_parts[flow].draw_flow()

    def reconfigure_flow(self, flow: Flow):
        """
        Reconfigures the attributes (e.g., line width and color) of a drawn flow.

        :param flow: flow object
        """
        self.flow_parts[flow].configure_line()

    def remove_flow(self, flow: Flow):
        """
        Removes a flow from the manager.

        :param flow: flow object
        """
        flow_part = self.flow_parts[flow]
        del self.flow_parts[flow]
        slot_index = self.slots.index(flow_part)

        if isinstance(flow_part, FlowPartView):
            flow_part.delete_from_canvas()
            self.slots[slot_index] = None
            self.restructure_flows()
        elif isinstance(flow_part, GroupedFlowPartView):
            flow_part.remove(flow)
            if len(flow_part.managed_flows) == 1:
                flow_to_move = flow_part.remove_first()
                self.slots[slot_index] = None
                self.add_flow(flow_to_move)

        if len(self.flow_parts) == 0:
            del FlowPartManager.active_flow_manager[(self.canvas, self.start_node, self.end_node)]

    def restructure_flows(self):
        """
        Restructures flows if empty slots can be filled.
        """
        self.slots = list(filter(lambda x: x is not None, self.slots))
        if len(self.slots) == 0:
            return
        last = self.slots[-1]
        free_slots = FlowPartManager.GROUPED_FLOW_INDEX - len(self.slots)
        if isinstance(last, GroupedFlowPartView):
            for i in range(free_slots):
                self.slots.insert(-1, None)
            for i in range(free_slots):
                if len(last.managed_flows) > 2:
                    flow = last.remove_first()
                    self.add_flow(flow)
                elif len(last.managed_flows) == 2:
                    flow = last.remove_first()
                    self.add_flow(flow)
                    self.slots[-1] = None
                    flow = last.remove_first()
                    self.add_flow(flow)
                    break
        else:
            for i in range(free_slots):
                self.slots.append(None)

        self.redraw_flows()

    def redraw_flows(self):
        """
        Redraws every managed flow.
        """
        for radius, slot in enumerate(self.slots):
            if slot is None:
                break
            slot.radius = radius
            slot.draw_flow()

    def get_next_free_radius(self) -> int:
        """
        Returns the next free slot.

        :return: next free slot index
        """
        index = FlowPartManager.GROUPED_FLOW_INDEX - 1
        for i, slot in enumerate(self.slots):
            if slot is None:
                return i
        return index
