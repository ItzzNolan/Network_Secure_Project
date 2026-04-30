import argparse
def build_parser():
    parser = argparse.ArgumentParser(prog="battle")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_p = subparsers.add_parser("run")
    run_p.add_argument("scenario", type=str)
    run_p.add_argument("ais", nargs="*", default=None)
    run_p.add_argument("-t", action="store_true")
    run_p.add_argument("-d", type=str, default=None)
    run_p.add_argument("-m", "--map-size", type=int, default=30)
    run_p.add_argument("--network", action="store_true")
    run_p.add_argument("--player-id", type=int, default=0)
    return parser
def parse_args(args=None):
    return build_parser().parse_args(args)
