import argparse
import glob
import luigi
import os
import radb
import sqlparse

import costcounter
import sql2ra
import raopt
import ra2mr

# You may want to add your own imports here.

def clear_local_tmpfiles():
    files = glob.glob('./*.tmp')
    for f in files:
        os.remove(f)

def eval(sf, env, query, optimize):

    dd = {}
    dd["PART"] = {"P_PARTKEY": "int", "P_NAME": "string", "P_MFGR": "string",
                  "P_BRAND": "string", "P_TYPE": "string", "P_SIZE": "int", "P_CONTAINER": "string",
                  "P_RETAILPRICE": "float", "P_COMMENT": "STRING"}
    dd["CUSTOMER"] = {"C_CUSTKEY": "int", "C_NAME": "string", "C_ADDRESS": "string",
                      "C_NATIONKEY": "int", "C_PHONE": "string", "C_ACCTBAL": "float",
                      "C_MKTSEGMENT": "string", "C_COMMENT": "string"}

    dd["REGION"] = {"R_REGIONKEY": "int", "R_NAME" : "string", "R_COMMENT": "string"}
    dd["ORDERS"] = {"O_ORDERKEY": "int", "O_CUSTKEY": "int", "O_ORDERSTATUS": "string",
                    "O_TOTALPRICE": "float", "O_ORDERDATE": "string", "O_ORDERPRIORITY": "string",
                    "O_CLERK": "string", "O_SHIPPRIORITY": "int", "O_COMMENT": "string"}
    dd["LINEITEM"] = {"L_ORDERKEY": "int", "L_PARTKEY": "int", "L_SUPPKEY": "int",
                      "L_LINENUMBER": "int", "L_QUANTITY": "int", "L_EXTENDEDPRICE": "float",
                      "L_DISCOUNT": "float", "L_TAX": "float", "L_RETURNFLAG": "string",
                      "L_LINESTATUS": "string", "L_SHIPDATE": "string", "L_COMMITDATE": "string",
                      "L_RECEIPTDATE": "string", "L_SHIPINSTRUCT": "string", "L_SHIPMODE": "string",
                      "L_COMMENT": "string"}
    dd["NATION"] = {"N_NATIONKEY": "int", "N_NAME": "string", "N_REGIONKEY": "int", "N_COMMENT": "string"}
    dd["SUPPLIER"] = {"S_SUPPKEY": "int", "S_NAME": "string", "S_ADDRESS": "string", "S_NATIONKEY": "int",
                      "S_PHONE": "string", "S_ACCTBAL": "float", "S_COMMENT": "string"}

    dd["PARTSUPP"] = {"PS_PARTKEY": "int", "PS_SUPPKEY": "int", "PS_AVAILQTY": "int",
                      "PS_SUPPLYCOST": "float", "PS_COMMENT": "string"}
    
    ''' ...................... you may edit code below ........................'''

    stmt = sqlparse.parse(query)[0]
    ra0 = sql2ra.translate(stmt)
    
    ra1 = raopt.rule_break_up_selections(ra0)
    ra2 = raopt.rule_push_down_selections(ra1, dd)
    ra3 = raopt.rule_merge_selections(ra2)
    ra4 = raopt.rule_introduce_joins(ra3)

    task = ra2mr.task_factory(ra4, env=env, optimize=optimize)

    luigi.build([task], local_scheduler=True)    
    
    ''' ...................... you may edit code above ........................'''
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calling miniHive.')
    parser.add_argument('--O',  action='store_true',  help='toggle optimization on')
    parser.add_argument('--SF', type=int, default=0,
                        help='the TPC-H scale factor')
    parser.add_argument('--env', choices=['HDFS', 'LOCAL'], default='HDFS',
                        help='execution environment')                        
    parser.add_argument('query', help='SQL query')

    args = parser.parse_args()

    # Assuming the default environment.
    env = ra2mr.ExecEnv.HDFS

    if args.env == 'LOCAL':
        clear_local_tmpfiles()
        env = ra2mr.ExecEnv.LOCAL

    eval(args.SF, env, args.query, args.O)

    if args.env == 'LOCAL':
        print(str(costcounter.compute_hdfs_costs()))
