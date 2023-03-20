from src.controller import * # the flask app with the API 
import argparse # for parsing command line arguments

# parses arguments
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="the community driver")

    start_api()
