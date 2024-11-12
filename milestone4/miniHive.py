import argparse
import glob
import luigi
import os
import radb
import radb.ast
import radb.parse
import sqlparse

import costcounter
import sql2ra
import raopt
import ra2mr


def clear_local_tmpfiles():
    files = glob.glob('./*.tmp')
    for f in files:
        os.remove(f)


def eval(sf, env, query, dd, optimize):
    stmt = sqlparse.parse(query)[0]

    ''' ...................... you may edit code below ........................'''

    ra0 = sql2ra.translate(stmt)

    ra1 = raopt.rule_break_up_selections(ra0)
    ra2 = raopt.rule_push_down_selections(ra1, dd)
    ra3 = raopt.rule_merge_selections(ra2)
    ra4 = raopt.rule_introduce_joins(ra3)

    task = ra2mr.task_factory(ra4, env=env, optimize=optimize)

    ''' ...................... you may edit code above ........................'''

    luigi.build([task], local_scheduler=True)
    return task


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calling miniHive.')
    parser.add_argument('--O', action='store_true', help='toggle optimization on')
    parser.add_argument('--SF', type=float, default=0,
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

    dd = {}
    dd["PART"] = {"P_PARTKEY": "integer", "P_NAME": "string", "P_MFGR": "string",
                  "P_BRAND": "string", "P_TYPE": "string", "P_SIZE": "integer", "P_CONTAINER": "string",
                  "P_RETAILPRICE": "float", "P_COMMENT": "string"}
    dd["CUSTOMER"] = {"C_CUSTKEY": "integer", "C_NAME": "string", "C_ADDRESS": "string",
                      "C_NATIONKEY": "integer", "C_PHONE": "string", "C_ACCTBAL": "float",
                      "C_MKTSEGMENT": "string", "C_COMMENT": "string"}
    dd["REGION"] = {"R_REGIONKEY": "integer", "R_NAME": "string", "R_COMMENT": "string"}
    dd["ORDERS"] = {"O_ORDERKEY": "integer", "O_CUSTKEY": "integer", "O_ORDERSTATUS": "string",
                    "O_TOTALPRICE": "float", "O_ORDERDATE": "string", "O_ORDERPRIORITY": "string",
                    "O_CLERK": "string", "O_SHIPPRIORITY": "string", "O_COMMENT": "string"}
    dd["LINEITEM"] = {"L_ORDERKEY": "integer", "L_PARTKEY": "integer", "L_SUPPKEY": "integer",
                      "L_LINENUMBER": "integer", "L_QUANTITY": "integer", "L_EXTENDEDPRICE": "float",
                      "L_DISCOUNT": "float", "L_TAX": "float", "L_RETURNFLAG": "string",
                      "L_LINESTATUS": "string", "L_SHIPDATE": "string", "L_COMMITDATE": "string",
                      "L_RECEIPTDATE": "string", "L_SHIPINSTRUCT": "string", "L_SHIPMODE": "string",
                      "L_COMMENT": "string"}
    dd["NATION"] = {"N_NATIONKEY": "integer", "N_NAME": "string", "N_REGIONKEY": "integer", "N_COMMENT": "string"}
    dd["SUPPLIER"] = {"S_SUPPKEY": "integer", "S_NAME": "string", "S_ADDRESS": "string", "S_NATIONKEY": "integer",
                      "S_PHONE": "string", "S_ACCTBAL": "float", "S_COMMENT": "string"}
    dd["PARTSUPP"] = {"PS_PARTKEY": "integer", "PS_SUPPKEY": "integer", "PS_AVAILQTY": "integer",
                      "PS_SUPPLYCOST": "float", "PS_COMMENT": "string"}

    eval(args.SF, env, args.query, dd, args.O)

    if args.env == 'LOCAL':
        print(str(costcounter.compute_hdfs_costs()))
