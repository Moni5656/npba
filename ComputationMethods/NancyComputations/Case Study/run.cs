using CBS;
using Unipi.Nancy.Numerics;

RunCaseStudy();

void RunCaseStudy()
{
    const int maxFrameSizeA = 64;
    const int maxFrameSizeB = 1522;
    const int maxFrameSizeNsr = 1522;
    var cbs = new CreditBasedShaper(maxFrameSizeA, maxFrameSizeB, maxFrameSizeNsr, false);
    const int linkSpeed = 100_000_000;
    var link1 = new Link(cbs, "FC-FS", "FC", "FS", linkSpeed, 65_000_000, -35_000_000, 0, 0);
    var link2 = new Link(cbs, "FS-BS", "FS", "BS", linkSpeed, 65_000_000, -35_000_000, 0, 0);
    var link3 = new Link(cbs, "HU-BS", "HU", "BS", linkSpeed, 75_000_000, -25_000_000, 0, 0);
    var link4 = new Link(cbs, "BS-RU", "BS", "RU", linkSpeed, 75_000_000, -25_000_000, 0, 0);

    var path1 = new[] { link1, link2, link4 };
    var path2 = new[] { link3, link4 };

    var isPeriodic = true;
    var isWorstCase = false;
    var flows = new List<Flow>();
    flows.Add(new Flow("flow0", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow1", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow2", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow3", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow4", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow5", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow6", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow7", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow8", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow9", path1, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));

    flows.Add(new Flow("flow10", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow11", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow12", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow13", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow14", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow15", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow16", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow17", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow18", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    flows.Add(new Flow("flow19", path2, AvbClass.A, isPeriodic, isWorstCase, 64, new Rational(1, 100), 10));
    cbs.SetFlows(flows.ToArray());

    var endToEnd = cbs.Flows[0].ComputeEndToEndDelay();
    var endToEndNano = (endToEnd * 1000000000).Ceil();
    Console.WriteLine("End-To-End Delay:\t" + endToEnd + " s");
    Console.WriteLine("\t\t\t" + endToEndNano / 1000 + " μs");

    var linkDelay = link4.ComputeDelay(AvbClass.A);
    var linkDelayNano = (linkDelay * 1000000000).Ceil();
    Console.WriteLine("Link Delay Class A:\t" + linkDelay + " s");
    Console.WriteLine("\t\t\t" + linkDelayNano / 1000 + " μs");


    var linkBacklog = link4.ComputeBacklog(AvbClass.A);
    Console.WriteLine("Link Backlog Class A:\t" + linkBacklog + " bit");
    Console.WriteLine("\t\t\t" + linkBacklog.Ceil() + " bit");
}