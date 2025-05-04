import argparse
from HiCPlot.SquHeatmap import main as _run_squ
from HiCPlot.SquHeatmapTrans import main as _run_squTrans
from HiCPlot.TriHeatmap import main as _run_tri
from HiCPlot.DiffSquHeatmap import main as _run_diff
from HiCPlot.DiffSquHeatmapTrans import main as _run_diffTrans
from HiCPlot.upper_lower_triangle_heatmap import main as _run_ul
from HiCPlot.NGStrack import main as _run_track

_SUBCOMMANDS = {
    "SquHeatmap": _run_squ,
    "SquHeatmapTrans": _run_squTrans,
    "TriHeatmap": _run_tri,
    "DiffSquHeatmap": _run_diff,
    "DiffSquHeatmapTrans": _run_diffTrans,
    "upper_lower_triangle_heatmap": _run_ul,
    "NGStrack": _run_track,
}

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="HiCPlot",
                                description="Hi‑C plotting utility (wrapper)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in _SUBCOMMANDS:
        sp = sub.add_parser(name)          # default add_help=True
        sp.add_argument("args", nargs=argparse.REMAINDER)
    return p

def main(argv=None):
    ns = _build_parser().parse_args(argv)
    func = _SUBCOMMANDS.get(ns.cmd)
    if func is None:                       # ultra‑defensive
        raise SystemExit(f"Unknown sub‑command: {ns.cmd}")
    func(ns.args or None)                  # allow empty remainder

if __name__ == "__main__":
    main()
