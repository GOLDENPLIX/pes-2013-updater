import argparse

parser = argparse.ArgumentParser(description="PES 2013 Update Bot")
parser.add_argument('--update-transfers', action='store_true', help="Update transfers")
parser.add_argument('--update-stats', action='store_true', help="Update player stats")
parser.add_argument('--update-kits', action='store_true', help="Update kits and logos")

args = parser.parse_args()

if args.update_transfers:
    print("Updating transfers...")
if args.update_stats:
    print("Updating stats...")
if args.update_kits:
    print("Updating kits...")
