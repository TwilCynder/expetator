#! /usr/bin/python3

import sys
import os

from expetator.benchmarks import SleepBench, alumet, NpbBench, MpiBench
from expetator.monitors import mojitos, power, kwollect, lperf
from expetator.leverages import Dvfs, Nodeepsleep

import expetator.experiment as experiment

if len(sys.argv) != 3:
    print("Usage: %s target_dir bench_name" % sys.argv[0])
    sys.exit(0)

target = sys.argv[1]
bench = sys.argv[2]


MONITORS = [ mojitos.Mojitos(sensor_set = {'dram0', 'rxp', 'irxp', 'gpu',
                                           'cache_misses','cache_references',
                                           'instructions','branch_instructions'}),
            kwollect.Power(metric=kwollect.get_g5k_target_metric())
           ]

fast =   {'is':'E', 'cg':'B', 'lu':'D', 'ep':'E', 'mg':'E', 'ft':'D', 'sp':'D', 'bt':'D'}
fast =   {'is':'D', 'cg':'B', 'lu':'C', 'ep':'D', 'mg':'D', 'ft':'C', 'sp':'C', 'bt':'C'}

if bench in fast:
    BENCHMARKS = [
        #SleepBench(default_time=duration),
        alumet.AlumetBench(NpbBench(names=[bench], options=fast), "1s"),
    ]
    LEVERAGES = [
    ]
elif bench == 'idle':
    BENCHMARKS = [
        alumet.AlumetBench(SleepBench(default_time=5*60), "1s"),
    ]
    LEVERAGES = [
    ]
elif bench == 'random':
    BENCHMARKS = [
        #SleepBench(default_time=duration),
        alumet.AlumetBench(MpiBench(params=[(64, 0, 0, 0)]), "1s"),
    ]
    LEVERAGES = [
    ]

    
experiment.run_experiment('%s/%s' %(target, os.getenv('OAR_JOB_ID')),
                          benchmarks = BENCHMARKS,
                          leverages = LEVERAGES,
                          monitors = MONITORS,
                         )
                          
with open('%s/%s_finished' %(target, os.getenv('OAR_JOB_ID')), 'w'):
    pass