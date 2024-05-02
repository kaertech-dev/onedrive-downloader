import os
import argparse
import json
from od_connector import *

ENV_ACCESS_TOKEN = "ONEDRIVE_ACCESS_TOKEN"
ENV_REFRESH_TOKEN = "ONEDRIVE_REFRESH_TOKEN"

def argparser() -> argparse.Namespace:
    """ Parses command line arguments """
    parser = argparse.ArgumentParser(description='OneDrive access tool command line parser')
    parser.add_argument('-c', '--client', help='application client id', required=True)
    parser.add_argument('-s', '--secret', help='application client secret', required=True)
    parser.add_argument('-t', '--tenant', help='application tenant id', required=True)
    parser.add_argument('-i', '--items', help='path to JSON itmes list to download', default='items_template.json')
    parser.add_argument('-o', '--output', help="output directory for files to be downloaded", default='.')
    return parser.parse_args()

def main():
    # Read saved tokens
    tokens = {
        "access_token": os.environ.get(ENV_ACCESS_TOKEN),
        "refresh_token": os.environ.get(ENV_REFRESH_TOKEN)
    }
    # Parse arguments and create OD connector
    args = argparser()
    od = OneDriveConnector(args.client, args.tenant, args.secret, tokens)
    # Check if there are tokens
    if not od.check_tokens():
        od.get_new_tokens()
    # Check if access token is not expired
    if not od.check_access_token():
        od.update_access_token()
    # Save tokens
    tokens = od.get_tokens()
    os.environ[ENV_ACCESS_TOKEN] = tokens["access_token"]
    os.environ[ENV_REFRESH_TOKEN] = tokens["refresh_token"]
    # Get driveitems' list and download them
    driveitems = []
    driveitems_dict = {}
    with open(args.items, "r") as f:
        driveitems_dict = json.load(f)
    for i in driveitems_dict['items']:
        driveitems.append(driveitems_dict['drive'] + i)
    od.download_items(driveitems, args.output)

if __name__ == "__main__":
    main()
