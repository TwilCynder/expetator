import os
from collections.abc import Iterable
from itertools import product

def to_iter(v):
    return v if isinstance(v, Iterable) else [v]

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
            executor.local('%s/install_alumet.sh %s' % (basedir, PREFIX_TEMP))
            self.alumet_path = DEFAULT_PATH

        #executor.local("%s config regen" % alumet_path)
        return { 
            'alumoj-' % key: list(product(to_iter(val), to_iter(self.frequencies)))
                for key,val in self.bench.build(executor).items()
        }

    def run(self, bench, params_, executor):
        _, initial_bench = bench.split('-', maxsplit=1)

        (params, freq) = params_

        print(params, freq)

        basedir = os.path.dirname(os.path.abspath(__file__))

        pid = executor.local(self.alumet_path + "--plugins mojitos,csv --config %s/alumet/alumet-config.toml --config-override plugins.mojitos.poll_interval=\"%s\" --config-override plugins.csv.output_path=\"%s/alumet-output.csv\" & echo $!" % (basedir, freq, PREFIX_TEMP))
        print(pid)
        value, name = self.bench.run(initial_bench, params, executor)
        os.kill(int(pid))
        print(value, name)
        return value, 'alumoj-%s-%s' % (freq, name)


