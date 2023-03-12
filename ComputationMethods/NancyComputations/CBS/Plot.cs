using Unipi.Nancy.MinPlusAlgebra;
using Unipi.Nancy.Numerics;
using XPlot.Plotly;

namespace CBS;

public static class Plot
/*
 *Taken from Github https://github.com/rzippo/nancy/blob/604500be004ddc89985b8705e2f563db972b6b26/examples/iwrr-tandem-study-example.dib
 */
{
    // the plot method, and its overloads, uses XPlot to plot the given curves
    // there is no particular reason in the choice of XPlot, only that it works well in this context - it can be replaced with other libraries in other context
    public static void plot(IEnumerable<Curve> curves, IEnumerable<string> names, Rational? upTo = null)
    {
        Rational t;
        if (upTo is not null)
            t = (Rational)upTo;
        else
            t = curves.Max(c => c.SecondPseudoPeriodEnd);
        t = t == 0 ? 10 : t;
        //Console.WriteLine(t);

        var cuts = curves
            .Select(c => c.Cut(0, t, isEndInclusive: true))
            .ToList();

        plot(cuts, names);
    }

    public static void plot(Curve curve, string name, Rational? upTo = null)
    {
        plot(new[] { curve }, new[] { name }, upTo);
    }

    public static void plot(IEnumerable<Curve> curves, Rational? upTo = null)
    {
        var names = curves.Select((_, i) => $"{(char)('a' + i)}");
        plot(curves, names, upTo);
    }

    public static void plot(Curve curve, Rational? upTo = null)
    {
        plot(new[] { curve }, new[] { "a" }, upTo);
    }

    public static void plot(params Curve[] curves)
    {
        plot(curves, upTo: null);
    }


    public static void plot(IEnumerable<Sequence> sequences, IEnumerable<string> names)
    {
        //Console.WriteLine("plot(IEnumerable<(Sequence sequence, string name)> namedSequences)");
        var colors = new List<string>
        {
            "#636EFA",
            "#EF553B",
            "#00CC96",
            "#AB63FA",
            "#FFA15A",
            "#19D3F3",
            "#FF6692",
            "#B6E880",
            "#FF97FF",
            "#FECB52"
        };

        var traces = Enumerable.Zip(sequences, names)
            .SelectMany((ns, i) => getTrace(ns.First, ns.Second, i));

        var chart = Chart.Plot(traces);

        chart.WithLayout(
            new Layout.Layout
            {
                xaxis = new Xaxis { zeroline = true, showgrid = true, title = "time" },
                yaxis = new Yaxis { zeroline = true, showgrid = true, title = "data" },
                showlegend = true,
                hovermode = "closest"
            }
        );

        chart.Show();

        IEnumerable<Scattergl> getTrace(Sequence sequence, string name, int index)
        {
            var color = colors[index % colors.Count];

            if (sequence.IsContinuous)
            {
                var points = sequence.Elements
                    .Where(e => e is Point)
                    .Select(e => (Point)e)
                    .Select(p => (x: (decimal)p.Time, y: (decimal)p.Value))
                    .ToList();

                if (sequence.IsRightOpen)
                {
                    var tail = sequence.Elements.Last() as Segment;
                    if (tail == null)
                    {
                        throw new ArgumentNullException("tail");
                    }

                    points.Add((x: (decimal)tail.EndTime, y: (decimal)tail.LeftLimitAtEndTime));
                }

                var trace = new Scattergl
                {
                    x = points.Select(p => p.x).ToArray(),
                    y = points.Select(p => p.y).ToArray(),
                    name = name,
                    fillcolor = color,
                    mode = "lines+markers",
                    line = new Line
                    {
                        color = color
                    },
                    marker = new Marker
                    {
                        symbol = "circle",
                        color = color
                    }
                };
                yield return trace;
            }
            else
            {
                var segments = new List<((decimal x, decimal y) a, (decimal x, decimal y) b)>();
                var points = new List<(decimal x, decimal y)>();
                var discontinuities = new List<(decimal x, decimal y)>();

                var breakpoints = sequence.EnumerateBreakpoints();
                foreach (var (left, center, right) in breakpoints)
                {
                    points.Add((x: (decimal)center.Time, y: (decimal)center.Value));
                    if (left is not null && left.LeftLimitAtEndTime != center.Value)
                    {
                        discontinuities.Add((x: (decimal)center.Time, y: (decimal)left.LeftLimitAtEndTime));
                    }

                    if (right is not null)
                    {
                        segments.Add((
                            a: (x: (decimal)right.StartTime, y: (decimal)right.RightLimitAtStartTime),
                            b: (x: (decimal)right.EndTime, y: (decimal)right.LeftLimitAtEndTime)
                        ));
                        if (right.RightLimitAtStartTime != center.Value)
                        {
                            discontinuities.Add((x: (decimal)center.Time, y: (decimal)right.RightLimitAtStartTime));
                        }
                    }
                }

                if (sequence.IsRightOpen)
                {
                    var tail = sequence.Elements.Last() as Segment;
                    if (tail == null)
                    {
                        throw new ArgumentNullException("tail");
                    }

                    segments.Add((
                        a: (x: (decimal)tail.StartTime, y: (decimal)tail.RightLimitAtStartTime),
                        b: (x: (decimal)tail.EndTime, y: (decimal)tail.LeftLimitAtEndTime)
                    ));
                }

                var segmentsLegend = segments.Any();

                bool isFirst = true;
                foreach (var (a, b) in segments)
                {
                    var trace = new Scattergl
                    {
                        x = new[] { a.x, b.x },
                        y = new[] { a.y, b.y },
                        name = name,
                        legendgroup = name,
                        fillcolor = color,
                        mode = "lines",
                        line = new Line
                        {
                            color = color
                        },
                        showlegend = segmentsLegend && isFirst
                    };
                    yield return trace;
                    isFirst = false;
                }

                var pointsTrace = new Scattergl
                {
                    x = points.Select(p => p.x).ToArray(),
                    y = points.Select(p => p.y).ToArray(),
                    name = name,
                    legendgroup = name,
                    fillcolor = color,
                    mode = "markers",
                    line = new Line
                    {
                        color = color
                    },
                    marker = new Marker
                    {
                        symbol = "circle",
                        color = color
                    },
                    showlegend = !segmentsLegend
                };
                yield return pointsTrace;

                var discontinuitiesTrace = new Scattergl
                {
                    x = discontinuities.Select(p => p.x).ToArray(),
                    y = discontinuities.Select(p => p.y).ToArray(),
                    name = name,
                    legendgroup = name,
                    fillcolor = color,
                    mode = "markers",
                    line = new Line
                    {
                        color = color
                    },
                    marker = new Marker
                    {
                        symbol = "circle-open",
                        color = color,
                        line = new Line
                        {
                            color = color
                        }
                    },
                    showlegend = false,
                };
                yield return discontinuitiesTrace;
            }
        }
    }

    public static void plot(Sequence sequence, string name)
    {
        plot(new[] { sequence }, new[] { name });
    }

    public static void plot(IEnumerable<Sequence> sequences)
    {
        var names = sequences.Select((_, i) => $"{(char)('a' + i)}");
        plot(sequences, names);
    }

    public static void plot(Sequence sequence)
    {
        plot(new[] { sequence }, new[] { "a" });
    }


    public static void PythonPlot(Curve[] curves, String[] names, Rational upTo)
    {
        plot(curves, names, upTo: upTo);
    }

    public static void PythonPlot(Curve[] curves, String[] names)
    {
        plot(curves, names, upTo: null);
    }

    public static void PythonPlot(Curve curve, String name)
    {
        plot(curve, name, upTo: null);
    }

    public static void PythonPlot(Curve curve, String name, Rational upTo)
    {
        plot(curve, name, upTo: upTo);
    }
}