import os
from datetime import datetime

from aisdb import dbpath
from aisdb.database.dbconn import DBConn
from aisdb.database.qrygen import DBQuery
from aisdb.database.lambdas import in_timerange_validmmsi
from aisdb.database.create_tables import (sqlite_createtable_staticreport,
                                          sqlite_createtable_dynamicreport,
                                          aggregate_static_msgs)

# import shapely.wkt
# from gis import Domain
# from tests.create_testing_data import zonegeoms_or_randompoly

# zonegeoms = zonegeoms_or_randompoly(randomize=True)
# domain = Domain('testing', zonegeoms, cache=False)

start = datetime(2020, 9, 1)
end = datetime(2020, 10, 1)

if not os.path.isfile(dbpath):
    dbpath == ":memory:"

aisdb = DBConn(dbpath)
conn, cur = aisdb.conn, aisdb.cur


def test_create_static_table():
    sqlite_createtable_staticreport(cur, month="202009")
    conn.commit()


def test_create_dynamic_table():

    sqlite_createtable_dynamicreport(cur, month="202009")
    conn.commit()


def test_create_static_aggregate_table():
    aggregate_static_msgs(dbpath, ["202009"])


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
