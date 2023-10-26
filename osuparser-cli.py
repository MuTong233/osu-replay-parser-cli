#!/usr/bin/env python3
from osrparse import Replay, parse_replay_data
from urllib.request import urlopen
import time
import argparse
import os
import json
import csv
import sys
import urllib

# Copyright information
print("osu! Replay Data parser by MuTong233")
print("Special thanks to kszlim for library support!\n")

# Arguments to be parsed
parser = argparse.ArgumentParser(
    prog="osuparser-cli",
    description="example: osuparser-cli -f my_replay.osr -a API_KEY -e -p result.csv",
    epilog="Please be aware that only STD is currently supported, other modes are not guaranteed to be correct.",
    add_help=True,
)

# Basic Functions
parser_basic = parser.add_argument_group("Basics", "The core part of this program")
parser_files = parser.add_mutually_exclusive_group(required=True)
parser_mode = parser.add_mutually_exclusive_group(required=True)
# Files
parser_files.add_argument(
    "-f",
    "--file",
    help="A Single Replay file to be parsed",
    nargs="?",
    type=str,
    const="false",
    default="false",
)
parser_files.add_argument(
    "-d",
    "--directory",
    help="An Directory of Replay File to be parsed",
    nargs="?",
    type=str,
    const="false",
    default="false",
)
# Network Functions
parser_files.add_argument(
    "-lo",
    "--load-online",
    help="[UNIMPLEMENTED]Load Online Replay Data by Beatmap ID and User ID(require API key)",
    action="store",
    dest="online_req",
    nargs=2,
    type=str,
    default="false",
    metavar=("[BEATMAP_ID]", "[USER_ID]"),
)
parser_files.add_argument(
    "-ls",
    "--load-online-score",
    help="[UNIMPLEMENTED]Load Online Replay Data by Score ID(require API key)",
    const="bruh",
    nargs="?",
    type=str,
    default="false",
    metavar="SCORE_ID",
)
parser_files.add_argument(
    "-lm",
    "--load-match",
    help="[UNIMPLEMENTED]Load Online Match Data by Match ID(require API key)",
    const="bruh",
    nargs="?",
    type=str,
    default="false",
    metavar="MATCH_ID",
)
# Modes
parser_mode.add_argument(
    "-a",
    "--apikey",
    help="Your osu! API Key, this MUST exists if you do not apply OFFLINE MODE",
    const="bruh",
    nargs="?",
    type=str,
    metavar="YOUR_API_KEY",
)
parser_mode.add_argument(
    "-o",
    "--offline",
    help="Use OFFLINE mode, User ID, Beatmap ID and Beatmapset ID will not be presented.",
    action="count",
    default=0,
)
parser_basic.add_argument(
    "-p",
    "--print",
    help="The CSV file you want to save the results to",
    const="bruh",
    nargs="?",
    type=str,
    default="new_data.csv",
    metavar="CSV_FILE",
)
parser_basic.add_argument(
    "-s",
    "--silent",
    help="Don't print the analysis result out, directly write into CSV file",
    action="count",
    default=0,
)

# Advanced Functions
parser_adv = parser.add_argument_group("Advanced", "Design your own replay data art.")
parser_adv.add_argument(
    "-in",
    "--ignore-nf",
    help="Ignore NoFail in Final Result",
    action="count",
    default=0,
)
parser_adv.add_argument(
    "-iv",
    "--ignore-v2",
    help="Ignore ScoreV2 in Final Result",
    action="count",
    default=0,
)
parser_adv.add_argument(
    "-im",
    "--ignore-nm",
    help="Ignore NoMod in Final Result",
    action="count",
    default=0,
)
parser_adv.add_argument(
    "-e",
    "--experiment",
    help="Try Experiment Method of Mods Outputting (Shortname instead of fullname)",
    action="count",
    default=0,
)

# Not implemented functions
unimplemented_parser = parser.add_argument_group(
    "Unimplemented", "These functions are not implemented yet"
)
unimplemented_parser.add_argument(
    "-wr",
    "--write-replay",
    help="[UNIMPLEMENTED]Add Replay Stream to the Result(dangerous)",
    action="count",
    default=0,
)

# osu! API URL Declaration
url_bm = "https://osu.ppy.sh/api/get_beatmaps?k="
url_usr = "https://osu.ppy.sh/api/get_user?k="

# Check if everything is correct
try:
    args = parser.parse_args()
except Exception:
    print("[!] Something went wrong, please try again!")
    sys.exit(0)
repfile = args.file
reppath = args.directory
apikey = args.apikey
if apikey == "bruh":
    print("[!] Please give an API key! exiting...")
    sys.exit(8)
if args.print == "bruh":
    print("[!] Please give an output CSV filename! exiting...")
    sys.exit(8)
if args.offline != 0:
    print("[!] Running in OFFLINE MODE, bid, setid and uid will be 0.")
else:
    # Pre-check of API key to prevent loop
    print("[-] Checking API key availablity...")
    try:
        url = url_usr + apikey + "&u=peppy"
        response = urlopen(url)
        data_json = json.loads(response.read())
        peppy = str(data_json[0]["user_id"])
        print("[-] Looks like the API key is good, continuing...")
    except Exception:
        print(
            "[!] Looks like Network is unavailable or API key is incorrect, exiting..."
        )
        sys.exit(8)

# Basic arguments
file_ls = []
condition_pass = 0
condition_now = 0

# Try open logfile
try:
    newfile = open(args.print, "a+", newline="")
except Exception:
    print("[!] Open CSV Failed! Please check if you have write permission!")
    sys.exit(1)

# Initialize CSV with Headers
# Must be the same structure with later data.
writer = csv.writer(newfile)
data = [
    "Mode",
    "Version",
    "Username",
    "Misscount",
    "Score",
    "Accuracy",
    "Combo",
    "IsPerfect",
    "Mods",
    "Grade",
    "BeatmapsetID",
    "BeatmapID",
    "UserID",
    "Played",
]
writer.writerow(data)


# Repeat parser
def process_file():
    for i in file_ls:
        print("[-] File:", i)
        try:
            replay = Replay.from_path(i)
        except Exception:
            print("[!] This is not a valid replay file!")
            print("[!] Please confirm that you have read permission to the file.")
            break
        r = replay

        # Objects Total
        totalcount = r.count_miss + r.count_100 + r.count_50 + r.count_300

        # Grade Determination
        if (
            r.count_300 / totalcount >= 0.9
            and r.count_miss == 0
            and r.count_50 / totalcount <= 0.01
        ):
            grade = "S"
        elif r.count_300 / totalcount == 1:
            grade = "SS"
        elif r.count_300 / totalcount >= 0.8 and r.count_miss == 0:
            grade = "A"
        elif r.count_300 / totalcount >= 0.9:
            grade = "A"
        elif r.count_300 / totalcount >= 0.7 and r.count_miss == 0:
            grade = "B"
        elif r.count_300 / totalcount >= 0.8:
            grade = "B"
        elif r.count_300 / totalcount >= 0.6:
            grade = "C"
        else:
            grade = "D"

        # Accuracy Calculation
        acc = round(
            (50 * r.count_50 + 100 * r.count_100 + 300 * r.count_300)
            / (300 * totalcount),
            4,
        )
        accdata = format(acc, ".2%")

        # Online Beatmap Data Gathering
        if args.offline != 0:
            condition_now = 1
            bsid = 0
            bid = 0
        while condition_now == condition_pass:
            try:
                print("[-] Retriving Beatmap Data")
                url = url_bm + apikey + "&h=" + r.beatmap_hash
                response = urlopen(url)
                data_json = json.loads(response.read())
                try:
                    bsid = str(data_json[0]["beatmapset_id"])
                    bid = str(data_json[0]["beatmap_id"])
                    condition_now = 1
                except Exception:
                    print("[!] Failed to gain beatmap data")
                    print(
                        "[!] Error while parsing json, assuming the beatmap does not exist."
                    )
                    bsid = 0
                    bid = 0
                    time.sleep(3)
                    condition_now = 1
            except Exception:
                print("[!] Failed to gain beatmap data")
                print(
                    "[!] Error while executing network request. Will try again in 3 seconds."
                )
                time.sleep(3)
        condition_now = 0

        # Online User Data Gathering
        if args.offline != 0:
            condition_now = 1
            onlinename = r.username
            uid = 0
        while condition_now == condition_pass:
            try:
                print("[-] Retriving User Data based on username")
                realname = urllib.parse.quote(r.username)
                onlinename = realname
                url = url_usr + apikey + "&u=" + realname
                response = urlopen(url)
                data_json = json.loads(response.read())
                try:
                    uid = str(data_json[0]["user_id"])
                    onlinename = str(data_json[0]["username"])
                    condition_now = 1
                except Exception:
                    print("[!] Failed to gain userdata")
                    print(
                        "[!] Error while parsing json, assuming the user does not exist."
                    )
                    uid = 0
                    time.sleep(3)
                    condition_now = 1
            except Exception:
                print("[!] Failed to gain userdata")
                print(
                    "[!] Error while executing network request. Will try again in 3 seconds."
                )
                time.sleep(3)
        condition_now = 0

        # Mods formatting
        formatted_mods = str(r.mods)
        if args.ignore_nf != 0:
            formatted_mods = formatted_mods.replace("NoFail", "")
        if args.ignore_v2 != 0:
            formatted_mods = formatted_mods.replace("ScoreV2", "")
        if args.ignore_nm != 0:
            formatted_mods = formatted_mods.replace("NoMod", "")
        if args.experiment != 0:
            formatted_mods = formatted_mods.replace("Mod.", "")
            formatted_mods = formatted_mods.replace("|", "")
            formatted_mods = formatted_mods.replace("Hidden", "HD")
            formatted_mods = formatted_mods.replace("HardRock", "HR")
            formatted_mods = formatted_mods.replace("Easy", "EZ")
            formatted_mods = formatted_mods.replace("Flashlight", "FL")
            formatted_mods = formatted_mods.replace("HalfTime", "HT")
            formatted_mods = formatted_mods.replace("DoubleTime", "DT")
            formatted_mods = formatted_mods.replace("SuddenDeath", "SD")
            formatted_mods = formatted_mods.replace("Perfect", "PF")
            formatted_mods = formatted_mods.replace("Nightcore", "NC")
            formatted_mods = formatted_mods.replace("TouchDevice", "TD")
            formatted_mods = formatted_mods.replace("Autoplay", "AT")
            formatted_mods = formatted_mods.replace("SpunOut", "SO")
            formatted_mods = formatted_mods.replace("Autopilot", "AP")
            formatted_mods = formatted_mods.replace("NoMod", "NM")
            formatted_mods = formatted_mods.replace("ScoreV2", "V2")
            formatted_mods = formatted_mods.replace("NoFail", "NF")

        # Data Outputting
        # This Output can be arranged in any way that you prefer
        if args.silent == 0:
            print(
                "\n=>Mode:",
                r.mode,
                "\n=>Version:",
                r.game_version,
                "\n=>Username:",
                onlinename,
                "\n=>Misscount:",
                r.count_miss,
                "\n=>Score:",
                r.score,
                "\n=>Accuracy:",
                accdata,
                "\n=>Combo:",
                r.max_combo,
                "\n=>IsPerfect:",
                r.perfect,
                "\n=>Mods:",
                formatted_mods,
                "\n=>Grade:",
                grade,
                "\n=>Beatmapset ID:",
                bsid,
                "\n=>Beatmap ID:",
                bid,
                "\n=>User ID:",
                uid,
                "\n=>Played:",
                r.timestamp,
                "\n",
            )

        # Write data to CSV
        # The data structure must match the header to avoid confusion
        data = [
            r.mode,
            r.game_version,
            onlinename,
            r.count_miss,
            r.score,
            accdata,
            r.max_combo,
            r.perfect,
            formatted_mods,
            grade,
            bsid,
            bid,
            uid,
            r.timestamp,
        ]
        writer.writerow(data)
        print("[-] Successfully parsed the file.")
        time.sleep(1)


def process_online():
    print("[!] Not Implemented yet.")


def process_onlinemp():
    print("[!] Not implemented yet.")


# Check if directory has access permission
if reppath != "false":
    try:
        for root, dirs, files in os.walk(reppath):
            root_file_ls = [os.path.join(root, file) for file in files]
            file_ls.append(root_file_ls)
        file_ls = [file for file in file_ls[0] if file.endswith(".osr")]
        process_file()
    except Exception:
        print("[!] Error while loading directory, exiting...")
        sys.exit(255)
# No Directory found, try file
elif repfile != "false":
    file_ls = [repfile]
    process_file()
# No file found, try bid uid matching
elif args.online_req != "false":
    if args.offline != 0:
        print("[!] Offline mode is activate while trying to get information online!")
        print("[!] Error Occured while loading score information, exiting...")
        sys.exit(255)
    bid = args.online_req[0]
    uid = args.online_req[1]
    process_online()
# No bid uid found, try score matching
elif args.load_online_score != "false":
    if args.offline != 0:
        print("[!] Offline mode is activate while trying to get information online!")
        print("[!] Error Occured while loading score information, exiting...")
        sys.exit(255)
    scoreid = args.load_online_score
    process_online()
elif args.load_match != "false":
    if args.offline != 0:
        print("[!] Offline mode is activate while trying to get information online!")
        print("[!] Error Occured while loading score information, exiting...")
        sys.exit(255)
    matchid = args.load_match
    process_online()
else:
    print("[!] Error Occured while loading score information, exiting...")

# Close file and exit
newfile.close()
print("[!] Parsed all files. Exiting...")
sys.exit(0)
