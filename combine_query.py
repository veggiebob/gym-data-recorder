
def combine_by_week(data, hour_bins=24, minute_bins=60):
    week_binner = vectorize(lambda t: get_week_time_bin(t, hour_bins=hour_bins, minute_bins=minute_bins))
    d = data.copy()
    d['week_bin'] = week_binner(d.time)
    return d.groupby(by='week_bin').mean(numeric_only=False)
    
def combine_by_day(data, minute_bins=60):
    day_binner = vectorize(lambda t: get_day_time_bin(t, minute_bins=minute_bins))
    d = data.copy()
    d['day_bin'] = day_binner(d.time)
    return d.groupby(by='day_bin').mean(numeric_only=False)

def vectorize(f):
    def vector_f(xs):
        return [f(x) for x in xs]
    return vector_f

def get_week_time_bin(t, hour_bins=24, minute_bins=60):
    v = (t.weekday() * hour_bins + int(t.hour / 24 * hour_bins)) * minute_bins + int(t.minute / 60 * minute_bins)
    return v

def get_week_time_from_bin(v, hour_bins=24, minute_bins=60):
    minute = int((v % minute_bins) / minute_bins * 60)
    hour = (int(v / minute_bins) % hour_bins) / hour_bins * 24
    day = int(v / minute_bins / hour_bins)
    return day, hour, minute

def get_day_time_bin(t, minute_bins=60):
    v = t.hour * minute_bins + int(t.minute / 60 * minute_bins)
    return v

def get_day_time_from_bin(v, minute_bins=60):
    minute = int((v % minute_bins) / minute_bins * 60)
    hour = int(v / minute_bins)
    return hour, minute