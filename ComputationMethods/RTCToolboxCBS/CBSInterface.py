class CBSInterface:
    def CBS(self, max_frame_size_a: float, max_frame_size_b: float, max_frame_size_nsr: float, is_strict: bool,
            flows: list['Flow']) -> 'CBS':
        ...

    # CBS
    def delay_link(self, cbs: 'CBS', link: 'Link', avb_class: str, path_folder: str, network_name: str) -> float: ...

    def backlog_link(self, cbs: 'CBS', link: 'Link', avb_class: str, path_folder: str, network_name: str) -> float: ...

    def end_to_end_delay(self, cbs: 'CBS', flow: 'Flow', path_folder: str, network_name: str) -> float: ...

    # Flow
    def Flow(self, name: str, max_frame_size: int, class_measurement_interval: float, max_interval_frame: int,
             path: list['Link'], avb_class: str, is_periodic: str, is_worst_case: str) -> 'Flow': ...

    # Link
    def Link(self, name: str, node_i: str, node_j: str, c: float, idle_slope_a: float, send_slope_a: float,
             idle_slope_b: float, send_slope_b: float) -> 'Link': ...


class CBS:
    pass


class Flow:
    pass


class Link:
    pass
