using System.Numerics;
using Unipi.Nancy.MinPlusAlgebra;
using Unipi.Nancy.Numerics;

namespace CBS;

public record Flow(string Name, Link[] Path, AvbClass AvbClass, bool IsPeriodic, bool IsWorstCase,
    BigInteger MaxFrameSize, Rational ClassMeasurementInterval, BigInteger MaxIntervalFrame)
{
    public Rational ComputeEndToEndDelay() => CreditBasedShaper.ComputeEndToEndDelay(this);

    public Curve ComputeSourceAc()
    {
        if (IsPeriodic)
            return IsWorstCase
                ? CreditBasedShaper.MakePeriodicWorstCaseArrivalCurve(this)
                : CreditBasedShaper.MakePeriodicArrivalCurve(this);
        return IsWorstCase
            ? CreditBasedShaper.MakeNonPeriodicWorstCaseArrivalCurve(this)
            : CreditBasedShaper.MakeNonPeriodicArrivalCurve(this);
    }
}

public enum AvbClass
{
    A,
    B,
    Nsr
}