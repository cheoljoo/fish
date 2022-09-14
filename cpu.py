import psutil

print(psutil.cpu_percent())
print(psutil.cpu_stats())
print(psutil.cpu_freq())

import os
import psutil

l1, l2, l3 = psutil.getloadavg()
CPU_use = (l3/os.cpu_count()) * 100

print("cpu count:",os.cpu_count())
print("CPU usage:",CPU_use)
