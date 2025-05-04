import sys
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
    p = argparse.ArgumentParser(
        prog="HiCPlot",
        description="Hi-C plotting utility (wrapper for individual tools)",
    )
    p.add_argument(
        "cmd",
        choices=_SUBCOMMANDS.keys(),
        help="Which plotting tool to run",
    )
    return p

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ns, remainder = _build_parser().parse_known_args(argv)
    _SUBCOMMANDS[ns.cmd](remainder or None)

if __name__ == "__main__":
    main()
