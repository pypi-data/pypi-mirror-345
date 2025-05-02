import argparse
from pathlib import Path
import json
from joblib import Parallel, delayed
from antelop.load_connection import *
from antelop.utils.analysis_utils import find_function
from antelop.utils.analysis_base import save_result
import pandas as pd

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--save")
parser.add_argument("-l", "--funclocation")
parser.add_argument("-f", "--funcfolder")
parser.add_argument("-n", "--funcname")
parser.add_argument("-r", "--restriction")
parser.add_argument("-a", "--args")
parser.add_argument("-c", "--numcpus")
args = parser.parse_args()

# load function
location = args.funclocation
folder = args.funcfolder
name = args.funcname
save = Path(args.save)
restriction = json.loads(args.restriction)
arguments = json.loads(args.args)
numcpus = int(args.numcpus)
format = save.suffix.lstrip('.')

# load function
function = find_function(analysis_functions, name, location, folder)

# form query to find keys
if isinstance(function.query, str):
    query = tables[function.query].proj()
elif isinstance(function.query, list):
    query = tables[function.query[0]]
    for q in function.query[1:]:
        query = query * tables[q].proj()
query = query.proj() & restriction
keys = query.fetch(as_dict=True)

# split keys into jobs
num_keys = len(keys)
job_length = num_keys // numcpus
if num_keys % numcpus != 0:
    job_length += 1
split_keys = [
    keys[i * job_length : None if i == numcpus-1 else (i + 1) * job_length] 
    for i in range(numcpus)
]

# runs in each process
def worker(keys_batch):
    from antelop.load_connection import analysis_functions
    function = find_function(analysis_functions, name, location, folder)
    
    try:
        results = function(keys_batch, *arguments)
        if isinstance(results, list):
            return {'success': True, 'results': results}
        else:
            return {'success': True, 'results': [results]}
    except Exception as e:
        return {
            'success': False,
            'keys': keys_batch,
            'error': str(e),
            'error_type': type(e).__name__
        }

# run in parallel
job_results = Parallel(n_jobs=numcpus)(delayed(worker)(keys) for keys in split_keys)

# clean output
results = []
failures = []
for job_result in job_results:
    if job_result['success']:
        results.extend(job_result['results'])
    else:
        failures.append(job_result)
        print(f"Failed batch: {job_result['error_type']}: {job_result['error']}")
        print(f"Failed keys: {job_result['keys']}")

results = pd.DataFrame(results)

# perform reproducibility hashes
function.save_reproducibility(save.with_suffix('.json'), restriction, *arguments)

save_result(results, save, format, function.returns)

print("\n")
print("Analysis complete.")
print(f"Results saved to {save}")