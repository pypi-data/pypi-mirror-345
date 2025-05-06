text = '''#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split()
    if len(parts) == 3:
        year, min_temp, max_temp = parts
        print(f"{year} {min_temp} {max_temp}")



reducer.py

#!/usr/bin/env python3
import sys
from collections import defaultdict

temps = defaultdict(list)

for line in sys.stdin:
    parts = line.strip().split()
    if len(parts) == 3:
        # try:
        year, tmin, tmax = parts
        temps[year].append((int(tmin), int(tmax)))
        # except ValueError:
        #     pass

coolest = min(((min(t[0] for t in v), y) for y, v in temps.items()))
hottest = max(((max(t[1] for t in v), y) for y, v in temps.items()))

print(f"Coolest Year: {coolest[1]} with {coolest[0]}°C")
print(f"Hottest Year: {hottest[1]} with {hottest[0]}°C")'''

print(text)