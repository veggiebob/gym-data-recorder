import sys
import re
from math import floor
from dataclasses import dataclass
from typing import *
import json

import pandas as pd

import fetch_data
import combine_query

# DEFINING MY OWN SPEC FOR DAYS
# DAYS START AT 0 BOZO AND END AT 6
# BECAUSE GOD CREATED THE EARTH
# WITH 6 DAYS BECAUSE 6 IS A PERFECT NUMBER

def day_ftime(time):
	return (time.hour + (time.minute + time.second / 60) / 60) / 24


def summarize(data: pd.DataFrame):

	ps = []
	for (idx, r) in data.iterrows():
		# print(r)
		p = dict(x=round(r.day + day_ftime(r.time.time()), 3),
				 y=round(r.lower + r.upper, 3))
		ps.append(p)
	return ps

def main():
	args = sys.argv
	# print(args)
	# print('args are ', args)
	if len(args) < 2:
		print("Need at least 1 argument! filename!")
		return
	filename = args[1]
	data = fetch_data.read_csv_data(filename=filename)
	data = combine_query.combine_by_week(data, minute_bins=60)
	summary = summarize(data)
	summary.sort(key=lambda p: p['x'])
	# JSON Spec:
	#         {
	#             week_mode: bool,
	#             data: [
	#                 {
	#                     x: float, // [0, 1) if in day mode, [0, 7) if in week mode
	#                     y: float // population!
	#                 }
	#             ]
	#         }
	s = json.dumps(summary, separators=(',', ':'))
	print("{\"week_mode\":true,\"data\":%s}"%s)


if __name__ == '__main__':
	main()
