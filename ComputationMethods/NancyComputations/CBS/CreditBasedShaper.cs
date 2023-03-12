using System.Numerics;
using Unipi.Nancy.MinPlusAlgebra;
using Unipi.Nancy.NetworkCalculus;
using Unipi.Nancy.Numerics;

namespace CBS;

public class CreditBasedShaper
{
    public CreditBasedShaper(BigInteger maxFrameSizeA, BigInteger maxFrameSizeB, BigInteger maxFrameSizeNsr,
        bool isStrict)
    {
        MaxFrameSizeA = maxFrameSizeA * 8;
        MaxFrameSizeB = maxFrameSizeB * 8;
        MaxFrameSizeNsr = maxFrameSizeNsr * 8;
        MaxFrameSizeN = BigInteger.Max(MaxFrameSizeB, MaxFrameSizeNsr);
        Flows = Array.Empty<Flow>();
        IsStrict = isStrict;
    }

    public BigInteger MaxFrameSizeA { get; }
    public BigInteger MaxFrameSizeB { get; }
    public BigInteger MaxFrameSizeNsr { get; }
    public BigInteger MaxFrameSizeN { get; }
    public Flow[] Flows { get; private set; }
    public bool IsStrict { get; }

    public void SetFlows(Flow[] flows) => Flows = flows;

    public static Rational ComputeEndToEndDelay(Flow flow)
    {
        var delay = new Rational(0);
        foreach (var link in flow.Path)
        {
            delay += link.ComputeDelay(flow.AvbClass);
        }

        return delay;
    }

    public static Rational ComputeLinkDelayA(Link link) => ComputeLinkDelay(link, AvbClass.A);
    public static Rational ComputeLinkDelayB(Link link) => ComputeLinkDelay(link, AvbClass.B);
    public static Rational ComputeLinkDelay(Link link, AvbClass avbClass) => link.ComputeDelay(avbClass);


    public static Rational ComputeLinkBacklogA(Link link) => ComputeLinkBacklog(link, AvbClass.A);
    public static Rational ComputeLinkBacklogB(Link link) => ComputeLinkBacklog(link, AvbClass.B);
    public static Rational ComputeLinkBacklog(Link link, AvbClass avbClass) => link.ComputeBacklog(avbClass);


    public static Curve MakePeriodicArrivalCurve(Flow flow)
        //Theorem 1
    {
        var linkSpeed = flow.Path[0].LinkSpeed;
        var m = flow.MaxIntervalFrame * flow.MaxFrameSize * 8;
        var r = m / flow.ClassMeasurementInterval;
        var b = m * (1 - r / linkSpeed);
        var ac = new SigmaRhoArrivalCurve(b, r);
        var linkSpeedCurve = new SigmaRhoArrivalCurve(0, linkSpeed);
        return Curve.Minimum(linkSpeedCurve, ac);
    }

    public static Curve MakePeriodicWorstCaseArrivalCurve(Flow flow)
        //Theorem 1
    {
        var linkSpeed = flow.Path[0].LinkSpeed;
        var m = flow.MaxIntervalFrame * flow.MaxFrameSize * 8;
        var linkSpeedCurve = new SigmaRhoArrivalCurve(0, linkSpeed);
        var stair = new StairCurve(m, flow.ClassMeasurementInterval);
        return Curve.Convolution(stair, linkSpeedCurve);
    }

    public static Curve MakeNonPeriodicArrivalCurve(Flow flow)
        //Theorem 2
    {
        var linkSpeed = flow.Path[0].LinkSpeed;
        var m = flow.MaxIntervalFrame * flow.MaxFrameSize * 8;
        var r = m / flow.ClassMeasurementInterval;
        var b = m * (1 - r / linkSpeed);
        var ac = new SigmaRhoArrivalCurve(2 * b, r);
        var linkSpeedCurve = new SigmaRhoArrivalCurve(0, linkSpeed);
        return Curve.Minimum(linkSpeedCurve, ac);
    }

    public static Curve MakeNonPeriodicWorstCaseArrivalCurve(Flow flow)
        //Theorem 2
    {
        var linkSpeed = flow.Path[0].LinkSpeed;
        var m = flow.MaxIntervalFrame * flow.MaxFrameSize * 8;
        var basicStair = new StairCurve(1, flow.ClassMeasurementInterval);
        var addedStair = basicStair.Addition(new ConstantCurve(1)).WithZeroOrigin();
        var scaledStair = addedStair.Scale(m);
        var linkSpeedCurve = new SigmaRhoArrivalCurve(0, linkSpeed);
        return scaledStair.Convolution(linkSpeedCurve);
    }


    public static RateLatencyServiceCurve MakeStrictMinimalServiceCurveA(Link link) =>
        MakeStrictMinimalServiceCurveA(link, link.Cbs.MaxFrameSizeA, link.Cbs.MaxFrameSizeN);

    public static RateLatencyServiceCurve MakeStrictMinimalServiceCurveA(Link link, BigInteger maxFrameSizeA,
            BigInteger maxFrameSizeN)
        //Theorem 3
    {
        var rate = new Rational((link.IdleSlopeA * link.LinkSpeed), link.IdleSlopeA - link.SendSlopeA);
        var latency = new Rational(maxFrameSizeN, link.LinkSpeed) -
                      new Rational(maxFrameSizeA * link.SendSlopeA, link.IdleSlopeA * link.LinkSpeed);
        return new RateLatencyServiceCurve(rate, latency);
    }


    public static RateLatencyServiceCurve MakeMinimalServiceCurveA(Link link) =>
        MakeMinimalServiceCurveA(link, link.Cbs.MaxFrameSizeN);

    public static RateLatencyServiceCurve MakeMinimalServiceCurveA(Link link, BigInteger maxFrameSizeN)
        //Theorem 4
    {
        var rate = new Rational((link.IdleSlopeA * link.LinkSpeed), link.IdleSlopeA - link.SendSlopeA);
        var latency = new Rational(maxFrameSizeN, link.LinkSpeed);
        return new RateLatencyServiceCurve(rate, latency);
    }


    public static SigmaRhoArrivalCurve MakeShaperCurveA(Link link) =>
        MakeShaperCurveA(link, link.Cbs.MaxFrameSizeA, link.Cbs.MaxFrameSizeN);

    public static SigmaRhoArrivalCurve MakeShaperCurveA(Link link, BigInteger maxFrameSizeA, BigInteger maxFrameSizeN)
        //Theorem 5
    {
        var rate = new Rational(link.IdleSlopeA * link.LinkSpeed, link.IdleSlopeA - link.SendSlopeA);
        var burst = rate * (new Rational(maxFrameSizeN, link.LinkSpeed)
                            - new Rational(maxFrameSizeA * link.SendSlopeA, link.IdleSlopeA * link.LinkSpeed));
        return new SigmaRhoArrivalCurve(burst, rate);
    }


    public static SigmaRhoArrivalCurve MakeMaximalServiceCurveA(Link link) =>
        MakeMaximalServiceCurveA(link, link.Cbs.MaxFrameSizeA);

    public static SigmaRhoArrivalCurve MakeMaximalServiceCurveA(Link link, BigInteger maxFrameSizeA)
        //Theorem 6
    {
        var rate = new Rational(link.IdleSlopeA * link.LinkSpeed, link.IdleSlopeA - link.SendSlopeA);
        var burst = rate * -new Rational(maxFrameSizeA * link.SendSlopeA, link.IdleSlopeA * link.LinkSpeed);
        return new SigmaRhoArrivalCurve(burst, rate);
    }


    public static RateLatencyServiceCurve MakeStrictMinimalServiceCurveB(Link link) =>
        MakeStrictMinimalServiceCurveB(link, link.Cbs.MaxFrameSizeA, link.Cbs.MaxFrameSizeB, link.Cbs.MaxFrameSizeNsr);

    public static RateLatencyServiceCurve MakeStrictMinimalServiceCurveB(Link link, BigInteger maxFrameSizeA,
            BigInteger maxFrameSizeB, BigInteger maxFrameSizeNsr)
        //Theorem 7
    {
        var maxFrameSizeN = BigInteger.Max(maxFrameSizeB, maxFrameSizeNsr);
        var rate = new Rational((link.IdleSlopeB * link.LinkSpeed), link.IdleSlopeB - link.SendSlopeB);
        var latency = new Rational(maxFrameSizeNsr + maxFrameSizeA, link.LinkSpeed)
                      - new Rational(maxFrameSizeN * link.IdleSlopeA, link.LinkSpeed * link.SendSlopeA)
                      - new Rational(maxFrameSizeB * link.SendSlopeB, link.LinkSpeed * link.IdleSlopeB);
        return new RateLatencyServiceCurve(rate, latency);
    }


    public static RateLatencyServiceCurve MakeMinimalServiceCurveB(Link link) =>
        MakeMinimalServiceCurveB(link, link.Cbs.MaxFrameSizeA, link.Cbs.MaxFrameSizeNsr, link.Cbs.MaxFrameSizeN);

    public static RateLatencyServiceCurve MakeMinimalServiceCurveB(Link link, BigInteger maxFrameSizeA,
            BigInteger maxFrameSizeNsr, BigInteger maxFrameSizeN)
        //Theorem 8
    {
        var rate = new Rational((link.IdleSlopeB * link.LinkSpeed), link.IdleSlopeB - link.SendSlopeB);
        var latency = new Rational(maxFrameSizeNsr + maxFrameSizeA, link.LinkSpeed)
                      - new Rational(maxFrameSizeN * link.IdleSlopeA, link.LinkSpeed * link.SendSlopeA);
        return new RateLatencyServiceCurve(rate, latency);
    }


    public static SigmaRhoArrivalCurve MakeShaperCurveB(Link link) =>
        MakeShaperCurveB(link, link.Cbs.MaxFrameSizeA, link.Cbs.MaxFrameSizeB, link.Cbs.MaxFrameSizeNsr);

    public static SigmaRhoArrivalCurve MakeShaperCurveB(Link link, BigInteger maxFrameSizeA, BigInteger maxFrameSizeB,
            BigInteger maxFrameSizeNsr)
        //Theorem 9
    {
        var maxFrameSizeN = BigInteger.Max(maxFrameSizeB, maxFrameSizeNsr);
        var rate = new Rational(link.IdleSlopeB * link.LinkSpeed, link.IdleSlopeB - link.SendSlopeB);
        var burst = rate * (new Rational(maxFrameSizeNsr + maxFrameSizeA, link.LinkSpeed)
                            - new Rational(maxFrameSizeN * link.IdleSlopeA, link.LinkSpeed * link.SendSlopeA)
                            - new Rational(maxFrameSizeB * link.SendSlopeB, link.LinkSpeed * link.IdleSlopeB));
        return new SigmaRhoArrivalCurve(burst, rate);
    }


    public static SigmaRhoArrivalCurve MakeMaximalServiceCurveB(Link link) =>
        MakeMaximalServiceCurveB(link, link.Cbs.MaxFrameSizeB);

    public static SigmaRhoArrivalCurve MakeMaximalServiceCurveB(Link link, BigInteger maxFrameSizeB)
        //Theorem 10
    {
        var rate = new Rational(link.IdleSlopeB * link.LinkSpeed, link.IdleSlopeB - link.SendSlopeB);
        var burst = rate * -new Rational(maxFrameSizeB * link.SendSlopeB, link.LinkSpeed * link.IdleSlopeB);
        return new SigmaRhoArrivalCurve(burst, rate);
    }
}