from distutils.core import setup
from osrparse import Replay, parse_replay_data
from urllib.request import urlopen
import py2exe # py2exe
import time
import argparse
import os
import json
import csv
import sys
import urllib

sys.argv.append('py2exe')

setup(
	options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
	console = ['osuparser-cli.py'],
	zipfile = None
)
