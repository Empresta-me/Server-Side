from src.controller import * # the flask app with the API 
import argparse # for parsing command line arguments

# parses arguments
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="the community driver")

    # PEM pass
    parser.add_argument("--pem", type=str, help="the password for the PEM File")

    args = parser.parse_args()

    start_api(args.pem)
