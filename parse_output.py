import sys
import re
from math import floor
from dataclasses import dataclass
from typing import *

# DEFINING MY OWN SPEC FOR DAYS
# DAYS START AT 0 BOZO AND END AT 6
# BECAUSE GOD CREATED THE EARTH
# WITH 6 DAYS BECAUSE 6 IS A PERFECT NUMBER
DAYS = [
		'Sunday',
		'Monday',
		'Tuesday',
		'Wednesday',
		'Thursday',
		'Friday',
		'Saturday'
	]
def string_day(day: int) -> str:
	return DAYS[day]

@dataclass
class Point:
	# week, day, ftime
	time: Tuple[int, int, float]
	gym: int
	pool: int

	def gtime(self) -> float:
		return self.day() + self.ftime()

	def ftime(self) -> float:
		return self.time[2]

	def day(self) -> int:
		return self.time[1]

	def week(self) -> int:
		return self.time[0]

	def __lt__(self, other):
		if type(other) == str:
			return self.time[2] < parse_time(other)
		elif type(other) == Point:
			return self.gtime() < other.gtime()

	def __gt__(self, other):
		if type(other) == str:
			return self.time[2] > parse_time(other)
		elif type(other) == Point:
			return self.gtime() > other.gtime()

PointFilter = Callable[[Point], bool]

TIME_PATTERN = re.compile(r'(\d{2}):(\d{2}):(\d{2})') # HH:MM:SS
def parse_time(time_string: str) -> float:
	matches = TIME_PATTERN.match(time_string)
	hour = int(matches[1])
	minute = int(matches[2])
	second = int(matches[3])
	return (hour + (minute + second / 60) / 60) / 24

def _pad_0(n: int) -> str:
	return ('00' + str(n))[-2:]

Hour = int
Minute = int
Second = int

# float representing time of day between 0 and 1
fTime = float

def to_ftime(time: (Hour, Minute, Second)) -> fTime:
	(hour, minute, second) = time
	return (hour + (minute + second / 60) / 60) / 24

def unpack_time(time: float) -> (Hour, Minute, Second):
	hour = floor(time * 24)
	minute = floor(time * 24 * 60) % 60
	second = floor(time * 24 * 60 * 60) % 60
	return hour, minute, second

# d stands for delta
def add_time(time: float, d: (Hour, Minute, Second)) -> fTime:
	(hr, m, s) = unpack_time(time)
	s += d[2]
	while s > 60:
		m += 1
		s -= 60
	m += d[1]
	while m > 60:
		hr += 1
		m -= 60
	hr = (hr + d[0]) % 24
	return to_ftime((hr, m, s))

# inverse of parse_time
def string_time(time: float) -> str:
	(hour, minute, second) = unpack_time(time)
	return _pad_0(hour) + ':' + _pad_0(minute) + ':' + _pad_0(second)

def parse_data(file) -> List[Point]:
	lines = []
	for line in file:
		params = line.split(',')
		if len(params) < 6:
			# print(f'"{line}" does not have enough parameters! skipping!')
			continue

		# bozo days
		time = (int(params[0]), int(params[1]) - 1, parse_time(params[2]))
		upper = int(params[3])
		lower = int(params[4])
		pool = int(params[5])
		lines.append(Point(time=time, gym=upper + lower, pool=pool))
	return lines

def by_day(data: List[Point]) -> Dict[int, List[Point]]:
	out = {}
	for d in data:
		if d.time[1] in out:
			out[d.time[1]].append(d)
		else:
			out[d.time[1]] = [d]
	return out

def last_gym_point(day_data: List[Point]) -> Point:
	f = list(filter(lambda b: b < '22:00:00', day_data))
	f.sort()
	return f[-1]

# given all the data and a function to filter it (with bucket sizes)
# group data points into buckets and average them, and return them as a list of points
def summarize(data: List[Point], buckets_per_hour: int, f: PointFilter) -> List[dict]:

	h = list(filter(f, data))
	h.sort(key=Point.gtime)

	bph = buckets_per_hour 				# buckets / hour
	b_len = 60 / bph 					# minutes / bucket
	day_len = (bph * 24) 				# buckets / day 
	buckets = [(0, 0)] * day_len * 7

	for point in h:
		(hour, minute, _) = unpack_time(point.ftime())
		i = point.day() * day_len + \
			hour * bph + \
			floor(minute / b_len)
		(total, count) = buckets[i]
		# assume that we only want the points from the gym
		buckets[i] = (total + point.gym, count + 1)

	# do the average calculation
	buckets = list(map(lambda tup: tup[0] / tup[1] if tup[1] > 0 else 0, buckets))
	
	# create the simple points
	f_minute = to_ftime((0, 1, 0))
	for i in range(len(buckets)):
		buckets[i] = {
			'x': i * f_minute * b_len,
			'y': buckets[i]
		}

	return buckets


def main():
	args = sys.argv
	# print(args)
	# print('args are ', args)
	if len(args) < 2:
		print("need at least 1 argument! filename!")
		return
	with open(args[1]) as f:
		data = parse_data(f)
		# print('[%s]'%','.join(list(map(lambda i:str(i), summarize(data, 6, lambda _: True)))))
		summary = summarize(data, 6, lambda _: True)
		s = f"[%s]"%(','.join(list(map(lambda d: "{\"x\":%.3f,\"y\":%.3f}"%(d['x'],d['y']), summary))))
		print("{\"week_mode\":true,\"data\":%s}"%s)


if __name__ == '__main__':
	main()
