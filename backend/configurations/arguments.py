import argparse

# Global variables to store the parsed arguments from main
APP_STAGE = "dev"
APP_DEBUG = True
APP_API_PORT = 8000


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
    parser.add_argument("--stage", help="specify the development stage (dev/staging/prod). Default: dev", type=str, default="dev")
    parser.add_argument("--debug", help="application debug mode (True/False), default: True", type=str2bool, default=True)
    parser.add_argument("--port", help="specify the port number for the API server", type=int, default=8000)
    args = parser.parse_args()

    if args.stage not in ["dev", "staging", "prod"]:
        raise argparse.ArgumentTypeError("Invalid stage. Please specify one of the following: dev, staging, prod")

    global APP_STAGE
    global APP_DEBUG
    global APP_API_PORT
    
    APP_STAGE = args.stage
    APP_DEBUG = args.debug
    APP_API_PORT = args.port
