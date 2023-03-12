using System.Data;
using System.Numerics;
using Unipi.Nancy.MinPlusAlgebra;
using Unipi.Nancy.NetworkCalculus;
using Unipi.Nancy.Numerics;

namespace CBS;

public record Link(CreditBasedShaper Cbs, string Name, string NodeI, string NodeJ, BigInteger LinkSpeed,
    BigInteger IdleSlopeA, BigInteger SendSlopeA, BigInteger IdleSlopeB, BigInteger SendSlopeB)
{
    public Rational ComputedDelayA { get; private set; } = -1;
    public Rational ComputedDelayB { get; private set; } = -1;
    public Curve? OutgoingArrivalCurveA { get; private set; }
    public Curve? OutgoingArrivalCurveB { get; private set; }


    public Curve ComputeIncomingArrivalCurve(AvbClass avbClass)
    {
        Curve accumulatedCurve = new ConstantCurve(0);
        foreach (var flow in StartingFlows(avbClass))
            accumulatedCurve += flow.ComputeSourceAc();

        foreach (var link in PreviousLinks())
        {
            accumulatedCurve += link.ComputeOutgoingArrivalCurve(avbClass);
        }

        return accumulatedCurve;
    }

    public Curve ComputeOutgoingArrivalCurve(AvbClass avbClass)
    {
        switch (avbClass)
        {
            case AvbClass.A when OutgoingArrivalCurveA != null:
                return OutgoingArrivalCurveA;
            case AvbClass.B when OutgoingArrivalCurveB != null:
                return OutgoingArrivalCurveB;
            case AvbClass.Nsr:
            default:
                return _ComputeOutgoingArrivalCurve(avbClass);
        }
    }

    private Curve _ComputeOutgoingArrivalCurve(AvbClass avbClass)
    {
        var acIn = ComputeIncomingArrivalCurve(avbClass);
        var maxServiceCurve = ComputeMaximalServiceCurve(avbClass);
        var minServiceCurve = ComputeMinimalServiceCurve(avbClass);
        Curve shaper = ComputeShapingCurve(avbClass);

        var curveConvoluted = acIn.Convolution(maxServiceCurve).Deconvolution(minServiceCurve);
        var shapedCurve = shaper.Minimum(curveConvoluted);

        if (avbClass == AvbClass.A)
            OutgoingArrivalCurveA = shapedCurve;
        if (avbClass == AvbClass.B)
            OutgoingArrivalCurveB = shapedCurve;
        return shapedCurve;
    }

    public SigmaRhoArrivalCurve ComputeShapingCurve(AvbClass avbClass)
    {
        switch (avbClass)
        {
            case AvbClass.A:
                return CreditBasedShaper.MakeShaperCurveA(this);
            case AvbClass.B:
                return CreditBasedShaper.MakeShaperCurveB(this);
            case AvbClass.Nsr:
            default:
                throw new ArgumentException("Invalid AVB Class:" + avbClass);
        }
    }

    public SigmaRhoArrivalCurve ComputeMaximalServiceCurve(AvbClass avbClass)
    {
        switch (avbClass)
        {
            case AvbClass.A:
                return CreditBasedShaper.MakeMaximalServiceCurveA(this);
            case AvbClass.B:
                return CreditBasedShaper.MakeMaximalServiceCurveB(this);
            case AvbClass.Nsr:
            default:
                throw new ArgumentException("Invalid AVB Class:" + avbClass);
        }
    }

    public RateLatencyServiceCurve ComputeMinimalServiceCurve(AvbClass avbClass) =>
        ComputeMinimalServiceCurve(avbClass, Cbs.IsStrict);

    public RateLatencyServiceCurve ComputeMinimalServiceCurve(AvbClass avbClass, bool isStrict)
    {
        if (avbClass == AvbClass.A)
        {
            return isStrict
                ? CreditBasedShaper.MakeStrictMinimalServiceCurveA(this, Cbs.MaxFrameSizeA, Cbs.MaxFrameSizeN)
                : CreditBasedShaper.MakeMinimalServiceCurveA(this, Cbs.MaxFrameSizeN);
        }

        return isStrict
            ? CreditBasedShaper.MakeStrictMinimalServiceCurveB(this, Cbs.MaxFrameSizeA, Cbs.MaxFrameSizeB,
                Cbs.MaxFrameSizeNsr)
            : CreditBasedShaper.MakeMinimalServiceCurveB(this, Cbs.MaxFrameSizeA, Cbs.MaxFrameSizeNsr,
                Cbs.MaxFrameSizeN);
    }

    public Rational ComputeBacklog(AvbClass avbClass)
    {
        var minimalService = ComputeMinimalServiceCurve(avbClass);
        var arrivalCurve = ComputeIncomingArrivalCurve(avbClass);
        return Curve.VerticalDeviation(arrivalCurve, minimalService);
    }

    public Rational ComputeDelay(AvbClass avbClass)
    {
        switch (avbClass)
        {
            case AvbClass.A when ComputedDelayA != -1:
                return ComputedDelayA;
            case AvbClass.B when ComputedDelayB != -1:
                return ComputedDelayB;
            case AvbClass.Nsr:
                throw new ArgumentException("Delay of NSR can not be computed.");
            default:
                return _ComputeDelay(avbClass);
        }
    }

    private Rational _ComputeDelay(AvbClass avbClass)
    {
        var minimalService = ComputeMinimalServiceCurve(avbClass);
        var arrivalCurve = ComputeIncomingArrivalCurve(avbClass);
        var delay = Curve.HorizontalDeviation(arrivalCurve, minimalService);
        if (delay == new Rational(1, 0))
        {
            Plot.plot(new[] { minimalService, arrivalCurve }, new[] { "min_sc", "ac" }, upTo: 0.01m);
            throw new ConstraintException("Infinite Delay");
        }

        if (avbClass == AvbClass.A)
            ComputedDelayA = delay;
        if (avbClass == AvbClass.B)
            ComputedDelayB = delay;
        return delay;
    }

    private List<Flow> PassingFlows() => Cbs.Flows.Where(flow => flow.Path.Contains(this)).ToList();

    private List<Link> PreviousLinks()
    {
        var prevLinks = new HashSet<Link>();
        var flows = PassingFlows();
        foreach (var flow in flows)
        {
            var index = Array.IndexOf(flow.Path, this);
            if (index > 0)
            {
                prevLinks.Add(flow.Path[index - 1]);
            }
        }

        return prevLinks.ToList();
    }

    private List<Flow> StartingFlows(AvbClass avbClass) =>
        Cbs.Flows.Where(flow => flow.Path[0] == this && flow.AvbClass == avbClass).ToList();
}