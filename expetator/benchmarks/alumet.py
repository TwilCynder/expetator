import os
from collections.abc import Iterable
from itertools import product
import signal

def to_iter(v):
    return v if (isinstance(v, Iterable) and not isinstance(v, (str))) else [v]

DEFAULT_PATH = os.path.expanduser("~/.local/tmp/alumet/target/release/alumet-agent")
PREFIX_TEMP = os.path.expanduser('~/.local/tmp/')

class AlumetBench :
    def __init__(self, benchmark, frequencies):
        self.bench = benchmark
        self.frequencies = frequencies

        self.names = { 'alumoj-'+name  for name in benchmark.names}

    def build(self, executor):
        os.makedirs(PREFIX_TEMP, exist_ok=True)

        self.alumet_path = os.environ.get("ALUMET_PATH") or DEFAULT_PATH
        if not os.path.isfile(self.alumet_path):
            basedir = os.path.dirname(os.path.abspath(__file__))
            executor.local('%s/alumet/install_alumet.sh %s' % (basedir, PREFIX_TEMP))
            self.alumet_path = DEFAULT_PATH

        print("Frequencies : ", self.frequencies)
        #executor.local("%s config regen" % alumet_path)
        print(to_iter(self.frequencies))
        build = self.bench.build(executor)
        print("allo : " ,{ 
            'alumoj-%s' % key: list(product(to_iter(val), to_iter(self.frequencies)))
                for key,val in build.items()
        })

        return { 
            'alumoj-%s' % key: list(product(to_iter(val), to_iter(self.frequencies)))
                for key,val in build.items()
        }

    def run(self, bench, params_, executor):
        _, initial_bench = bench.split('-', maxsplit=1)

        (params, freq) = params_

        print(params, freq)

        basedir = os.path.dirname(os.path.abspath(__file__))

        pid = executor.local(executor.sudo + " " + self.alumet_path + ' --plugins mojitos,csv --config %s/alumet/alumet-config.toml --config-override plugins.mojitos.poll_interval=\\"%s\\" --config-override plugins.csv.output_path=\\"%s/alumet-output.csv\\" & echo $!' % (basedir, freq, PREFIX_TEMP))
        print("Pid", pid)
        value, name = self.bench.run(initial_bench, params, executor)
        os.kill(int(pid), signal.SIGTERM)
        print("Value;name", value, name)
        return value, 'alumoj-%s-%s' % (freq, name)


