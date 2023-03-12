from typing import overload, Union, Optional


class Rational:
    def __init__(self, numerator, denominator):
        _ = numerator, denominator


class BigInteger:
    def __init__(self, number):
        _ = number


class Curve:
    pass


class AvbClass:
    A = "A"
    B = "B"
    Nsr = "NSR"


class NancyCBS:

    def __init__(self, maxFrameSizeA: Union[BigInteger, int], maxFrameSizeB: Union[BigInteger, int],
                 maxFrameSizeNsr: Union[BigInteger, int], isStrict: bool):
        self.MaxFrameSizeA: BigInteger = maxFrameSizeA
        self.MaxFrameSizeB: BigInteger = maxFrameSizeB
        self.MaxFrameSizeNsr: BigInteger = maxFrameSizeNsr
        self.MaxFrameSizeN: BigInteger = maxFrameSizeNsr
        self.Flows: list['Flow'] = []
        self.IsStrict: bool = isStrict

    def SetFlows(self, flows: list['Flow']): ...

    @staticmethod
    def ComputeEndToEndDelay(flow: 'Flow') -> Rational: ...

    @staticmethod
    def ComputeLinkDelayA(link: 'Link') -> Rational: ...

    @staticmethod
    def ComputeLinkDelayB(link: 'Link') -> Rational: ...

    @staticmethod
    def ComputeLinkDelay(link: 'Link', avbClass: AvbClass) -> Rational: ...

    @staticmethod
    def ComputeLinkBacklogA(link: 'Link') -> Rational: ...

    @staticmethod
    def ComputeLinkBacklogB(link: 'Link') -> Rational: ...

    @staticmethod
    def ComputeLinkBacklog(link: 'Link', avbClass: AvbClass) -> Rational: ...

    @staticmethod
    def MakePeriodicArrivalCurve(flow: 'Flow') -> Curve: ...

    @staticmethod
    def MakePeriodicWorstCaseArrivalCurve(flow: 'Flow') -> Curve: ...

    @staticmethod
    def MakeNonPeriodicArrivalCurve(flow: 'Flow') -> Curve: ...

    @staticmethod
    def MakeNonPeriodicWorstCaseArrivalCurve(flow: 'Flow') -> Curve: ...

    @staticmethod
    @overload
    def MakeStrictMinimalServiceCurveA(link: 'Link', maxFrameSizeA: BigInteger,
                                       maxFrameSizeN: BigInteger) -> Curve: ...

    @staticmethod
    @overload
    def MakeStrictMinimalServiceCurveA(link: 'Link') -> Curve: ...

    @staticmethod
    @overload
    def MakeMinimalServiceCurveA(link: 'Link', maxFrameSizeN: BigInteger) -> Curve: ...

    @staticmethod
    @overload
    def MakeMinimalServiceCurveA(link: 'Link') -> Curve: ...

    @staticmethod
    @overload
    def MakeShaperCurveA(link: 'Link', maxFrameSizeA: BigInteger, maxFrameSizeN: BigInteger) -> Curve: ...

    @staticmethod
    @overload
    def MakeShaperCurveA(link: 'Link') -> Curve: ...

    @staticmethod
    @overload
    def MakeMaximalServiceCurveA(link: 'Link', maxFrameSizeA: BigInteger) -> Curve: ...

    @staticmethod
    @overload
    def MakeMaximalServiceCurveA(link: 'Link') -> Curve: ...

    @staticmethod
    @overload
    def MakeStrictMinimalServiceCurveB(link: 'Link', maxFrameSizeA: BigInteger, maxFrameSizeB: BigInteger,
                                       maxFrameSizeNsr: BigInteger) -> Curve: ...

    @staticmethod
    @overload
    def MakeStrictMinimalServiceCurveB(link: 'Link') -> Curve: ...

    @staticmethod
    @overload
    def MakeMinimalServiceCurveB(link: 'Link', maxFrameSizeA: BigInteger, maxFrameSizeNsr: BigInteger,
                                 maxFrameSizeN: BigInteger) -> Curve: ...

    @staticmethod
    @overload
    def MakeMinimalServiceCurveB(link: 'Link') -> Curve: ...

    @staticmethod
    @overload
    def MakeShaperCurveB(link: 'Link', maxFrameSizeA: BigInteger, maxFrameSizeB: BigInteger,
                         maxFrameSizeNsr: BigInteger) -> Curve: ...

    @staticmethod
    @overload
    def MakeShaperCurveB(link: 'Link') -> Curve: ...

    @staticmethod
    @overload
    def MakeMaximalServiceCurveB(link: 'Link', maxFrameSizeB: BigInteger) -> Curve: ...

    @staticmethod
    @overload
    def MakeMaximalServiceCurveB(link: 'Link') -> Curve: ...

    @staticmethod
    def PlotBasicCurves(): ...

    @staticmethod
    def PlotArrivalCurves(): ...

    @staticmethod
    def PlotServiceCurves(): ...

    @staticmethod
    def PlotShaperCurves(): ...


class Link:
    def __init__(self, cbs: NancyCBS, name: str, node_i: str, node_j: str, link_speed: Union[BigInteger, int],
                 idle_slope_a: Union[BigInteger, int], send_slope_a: Union[BigInteger, int],
                 idle_slope_b: Union[BigInteger, int], send_slope_b: Union[BigInteger, int]):
        self.Cbs: NancyCBS = cbs
        self.Name: str = name
        self.NodeI: str = node_i
        self.NodeJ: str = node_j
        self.LinkSpeed: BigInteger = link_speed
        self.IdleSlopeA: BigInteger = idle_slope_a
        self.SendSlopeA: BigInteger = send_slope_a
        self.IdleSlopeB: BigInteger = idle_slope_b
        self.SendSlopeB: BigInteger = send_slope_b
        self.ComputedDelayA: Rational = Rational(-1, 1)
        self.ComputedDelayB: Rational = Rational(-1, 1)
        self.OutgoingArrivalCurveA: Optional[Curve] = None
        self.OutgoingArrivalCurveB: Optional[Curve] = None

    def ComputeIncomingArrivalCurve(self, avbClass: AvbClass) -> Curve:
        pass

    def ComputeOutgoingArrivalCurve(self, avbClass: AvbClass) -> Curve:
        pass

    def ComputeShapingCurve(self, avbClass: AvbClass) -> Curve:
        pass

    def ComputeMaximalServiceCurve(self, avbClass: AvbClass) -> Curve:
        pass

    @overload
    def ComputeMinimalServiceCurve(self, avbClass: AvbClass) -> Curve:
        pass

    @overload
    def ComputeMinimalServiceCurve(self, avbClass: AvbClass, isStrict: bool) -> Curve:
        pass

    def ComputeBacklog(self, avbClass: AvbClass) -> Rational:
        pass

    def ComputeDelay(self, avbClass: AvbClass) -> Rational:
        pass


class Flow:

    def __init__(self, name: str, Path: list[Link], avb_class: 'AvbClass', is_periodic: bool, is_worst_case: bool,
                 max_frame_size: Union[BigInteger, int], class_measurement_interval: Rational,
                 max_interval_frame: Union[BigInteger, int]):
        self.Name: str = name
        self.Path: list[Link] = Path
        self.AvbClass: AvbClass = avb_class
        self.IsPeriodic: bool = is_periodic
        self.IsWorstCase: bool = is_worst_case
        self.MaxFrameSize: BigInteger = max_frame_size
        self.ClassMeasurementInterval: Rational = class_measurement_interval
        self.MaxIntervalFrame: BigInteger = max_interval_frame

    def ComputeEndToEndDelay(self) -> Rational: ...

    def ComputeSourceAc(self) -> Curve: ...


class Plot:

    @staticmethod
    @overload
    def PythonPlot(curves: list[Curve], names: list[str]): ...

    @staticmethod
    @overload
    def PythonPlot(curves: list[Curve], names: list[str], upTo: Rational): ...

    @staticmethod
    @overload
    def PythonPlot(curve: Curve, name: str): ...

    @staticmethod
    @overload
    def PythonPlot(curve: Curve, name: str, upTo: Rational): ...
