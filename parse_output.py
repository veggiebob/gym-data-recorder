import sys
import re
from math import floor
from dataclasses import dataclass
from typing import Callable


@dataclass
class Point:
	time: tuple[int, int, float]
	gym: int
	pool: int

	def gtime(self) -> float:
		return self.day() + self.ftime()

	def ftime(self) -> float:
		return self.time[2]

	def day(self) -> int:
		return self.time[1]

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
def unpack_time(time: float) -> (Hour, Minute, Second):
	hour = floor(time * 24)
	minute = floor(time * 24 * 60) % 24
	second = floor(time * 24 * 60 * 60) % 60
	return hour, minute, second

# inverse of parse_time
def string_time(time: float) -> str:
	(hour, minute, second) = unpack_time(time)
	return _pad_0(hour) + ':' + _pad_0(minute) + ':' + _pad_0(second)

def parse_data(file) -> list[Point]:
	lines = []
	for line in file:
		params = line.split(',')
		if len(params) < 5:
			print('skipped one!')
			continue
		time = (int(params[0]), int(params[1]), parse_time(params[2]))
		upper = int(params[3])
		lower = int(params[4])
		pool = int(params[5])
		lines.append(Point(time=time, gym=upper + lower, pool=pool))
	return lines

def by_day(data: list[Point]) -> dict[int, list[Point]]:
	out = {}
	for d in data:
		if d.time[1] in out:
			out[d.time[1]].append(d)
		else:
			out[d.time[1]] = [d]
	return out

def last_gym_point(day_data: list[Point]) -> Point:
	f = list(filter(lambda b: b < '22:00:00', day_data))
	f.sort()
	return f[-1]

def summarize(data: list[Point], buckets_per_hour: int, f: PointFilter) -> list[int]:

	h = list(filter(f, data))
	h.sort(key=Point.gtime)

	bph = buckets_per_hour
	b_len = 60 / bph # bucket length (in minutes)
	day_len = (bph * 24)
	buckets = [(0, 0)] * day_len * 7

	for point in h:
		(hour, minute, _) = unpack_time(point.ftime())
		i = point.day() * day_len + \
			hour * bph + \
			floor(minute / b_len) * bph
		(total, count) = buckets[i]
		buckets[i] = (total + point.gym, count + 1)

	buckets = list(map(lambda tup: tup[0] / tup[1] if tup[1] > 0 else 0, buckets))
	return buckets

if __name__ == '__main__':
	args = sys.argv
	# print(args)
	with open(args[1]) as f:
		data = parse_data(f)
		print('[%s]'%','.join(list(map(lambda i:str(i), summarize(data, 6, lambda _: True)))))

