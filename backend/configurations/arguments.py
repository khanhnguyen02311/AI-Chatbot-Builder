import argparse
from dotenv import load_dotenv

stage = None
debug = None


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", help="specify the development stage (dev/staging/prod)", type=str, default="dev")
    parser.add_argument("--debug", help="application debug mode (True/False), default: True", type=str2bool, nargs="?", const=True, default=False)
    args = parser.parse_args()

    if args.stage not in ["dev", "staging", "prod"]:
        parser.error("--stage: Invalid argument value (dev/staging/prod).")

    load_dotenv(dotenv_path=f'.env.{args.stage}', verbose=True)

    # print(args.stage, args.debug)

    global stage
    global debug
    stage = args.stage
    debug = args.debug

    return args
