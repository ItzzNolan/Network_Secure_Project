import argparse

def build_parser():
    parser = argparse.ArgumentParser(prog="battle", description="MedievAIl BAIttle GenerAIl")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("scenario", type=str)
    run_parser.add_argument("ai1", type=str)
    run_parser.add_argument("ai2", type=str)
    run_parser.add_argument("-t", action="store_true")
    run_parser.add_argument("-d", type=str, default=None, metavar="DATAFILE")
    run_parser.add_argument("-m", "--map-size", type=int, default=30, metavar="SIZE",
                        help="Taille de la carte NxN (defaut: 30, min requis: 120)")
    
    load_parser = subparsers.add_parser("load")
    load_parser.add_argument("savefile", type=str)
    
    tourney_parser = subparsers.add_parser("tourney")
    tourney_parser.add_argument("-G", nargs="+", default=None, metavar="AI")
    tourney_parser.add_argument("-S", nargs="+", default=None, metavar="SCENARIO")
    tourney_parser.add_argument("-N", type=int, default=10)
    tourney_parser.add_argument("-na", action="store_true")
    tourney_parser.add_argument("-m", "--map-size", type=int, default=30, metavar="SIZE",
                            help="Taille de la carte NxN (defaut: 30)")
    
    plot_parser = subparsers.add_parser("plot")
    plot_parser.add_argument("ai", type=str)
    plot_parser.add_argument("plotter", type=str)
    plot_parser.add_argument("scenario_call", type=str)
    plot_parser.add_argument("range_arg", type=str)
    plot_parser.add_argument("-N", type=int, default=10)
    
    return parser

def parse_args(args=None):
    return build_parser().parse_args(args)