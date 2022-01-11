import os
from datetime import datetime

from aisdb.common import data_dir
from aisdb.database.dbconn import DBConn
from aisdb.database.qrygen import DBQuery
from aisdb.database.lambdas import in_timerange_validmmsi
from aisdb.database.create_tables import (
    aggregate_static_msgs,
    sqlite_createtable_dynamicreport,
    sqlite_createtable_staticreport,
)

start = datetime(2020, 9, 1)
end = datetime(2020, 10, 1)

if not os.path.isdir(data_dir):
    os.mkdir(data_dir)

#if not os.path.isdir(os.path.join(data_dir, 'testdb')):
#    os.mkdir(os.path.join(data_dir, 'testdb'))

dbpath = os.path.join(data_dir, 'test1.db')

aisdatabase = DBConn(dbpath=dbpath)
conn, cur = aisdatabase.conn, aisdatabase.cur


def test_create_static_table():
    sqlite_createtable_staticreport(cur, month="202009")
    conn.commit()


def test_create_dynamic_table():

    sqlite_createtable_dynamicreport(cur, month="202009")
    conn.commit()


def test_create_static_aggregate_table():
    _ = sqlite_createtable_staticreport(cur, "202009")
    conn.commit()
    aggregate_static_msgs(dbpath, ["202009"])
    conn.commit()


def test_query_emptytable():

    dt = datetime.now()
    rowgen = DBQuery(
        start=start,
        end=end,
        callback=in_timerange_validmmsi,
    )
    #rowgen.run_qry(dbpath=dbpath, qryfcn=static)
    rows = rowgen.run_qry()
    delta = datetime.now() - dt
    print(f'query time: {delta.total_seconds():.2f}s')


os.remove(dbpath)
