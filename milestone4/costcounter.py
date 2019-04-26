import glob
import json

def compute_hdfs_costs():
    costs = 0    
    files = glob.glob('./*.tmp')
    for file in files:
        f = open(file, 'r')
        for line in f:
            key, value = line.split('\t')
            json_tuple = json.loads(value) # Makes sure it still can be loaded.

            costs += len(json.dumps(json_tuple))
        f.close()

    return costs
