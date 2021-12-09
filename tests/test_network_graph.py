import os
#import pyopencl as cl

#os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
#os.environ['PYOPENCL_CTX'] = '1'

os.environ["OMP_NUM_THREADS"] = '1'
os.environ["OPENBLAS_NUM_THREADS"] = '1'
os.environ["MKL_NUM_THREADS"] = '1'
os.environ["VECLIB_MAXIMUM_THREADS"] = '1'
os.environ["NUMEXPR_NUM_THREADS"] = '1'

#os.system("taskset -c 0-11 -p %d" % os.getpid())
from multiprocessing import set_start_method
set_start_method('forkserver')
from multiprocessing import Pool, Queue
from datetime import datetime, timedelta
from functools import partial
import pickle
import time
import cProfile

import numpy as np

from aisdb import *
from aisdb.gis import Domain, ZoneGeomFromTxt
from aisdb.track_gen import trackgen, segment_tracks_timesplits, segment_tracks_dbscan, fence_tracks, concat_tracks
from aisdb.network_graph import serialize_network_edge
from aisdb.merge_data import merge_tracks_hullgeom, merge_tracks_shoredist, merge_tracks_bathymetry







def test_network_graph():

    # query db for points in domain 
    args = qrygen(
            start   = start,
            end     = end,
            #end     = start + timedelta(hours=24),
            xmin    = domain.minX, 
            xmax    = domain.maxX, 
            ymin    = domain.minY, 
            ymax    = domain.maxY,
            callback = rtree_in_validmmsi_bbox,
            #callback = rtree_in_time_bbox_hasmmsi,
            #mmsi=258084000,
        )
    rowgen=args.gen_qry(fcn=crawl, dbpath=dbpath)

    fpath = os.path.join(output_dir, 'rowgen_year_test2.pickle')

    #with open(fpath, 'wb') as f:
    #    for row in rowgen:
    #        pickle.dump(row, f)

        
    def picklegen(fpath):
        with open(fpath, 'rb') as f:
            while True:
                try:
                    #rows = pickle.load(f)
                    yield pickle.load(f)
                except EOFError as e:
                    break

    async def getval(gen):
        async for val in gen:
            print(val)

    gen = picklegen(fpath)
    getval(gen).send(None)


    #merged = list(merge_layers(rowgen))

    #next(merged)

    timesplit = partial(segment_tracks_timesplits,  maxdelta=timedelta(hours=2))
    distsplit = partial(segment_tracks_dbscan,      max_cluster_dist_km=50)
    geofenced = partial(fence_tracks,               domain=domain)
    serialize = partial(serialize_network_edge,     domain=domain)

    rowgen = picklegen(fpath)
    gen = trackgen(rowgen)
    cProfile.run('test = gen.__anext__().send(None)', sort='tottime')




    timesplit = partial(segment_tracks_timesplits,  maxdelta=timedelta(hours=2))
    distsplit = partial(segment_tracks_dbscan,      max_cluster_dist_km=50)
    geofenced = partial(fence_tracks,               domain=domain)
    serialize = partial(serialize_network_edge,     domain=domain)

    rowgen = picklegen(fpath)
    pipeline = serialize(merge_tracks_bathymetry(merge_tracks_shoredist(merge_tracks_hullgeom(geofenced(distsplit(timesplit(trackgen(rowgen))))))))
    
    rowgen = picklegen(fpath)
    async def run(pipeline):
        try:
            #run_parallel(piped)
            #pipeline.send(None)
            return await pipeline
        except StopIteration as err:
            return err.value

    test = run(rowgen)
    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe()
    loop.run_in_executor()

    future = asyncio.run_coroutine_threadsafe(run(pipeline), loop)

    while True:
        test = loop.run_until_complete(rowgen.__anext__())
        print(test[0][0])
        pipeline = serialize(merge_tracks_bathymetry(merge_tracks_shoredist(merge_tracks_hullgeom(geofenced(distsplit(timesplit(trackgen([test]))))))))


    cProfile.run('test = next(scheduler)', sort='tottime')
    processor = concat_tracks(distsplit(timesplit(geofenced(trackgen(rowgen)))))

    #rowgen = picklegen(fpath)
    #processor = serialize(merge_tracks_bathymetry(merge_tracks_shoredist(merge_tracks_hullgeom(concat_tracks(geofenced(distsplit(timesplit(trackgen(rowgen)))))))))
    #test = next(processor)


    #rowgen = picklegen(fpath)
    #test = next(processor(rowgen))
    from tests.importtest import run_parallel, domain

    rowgen = picklegen(fpath)
    with Pool(processes=8) as p:
        #results = p.map(run_parallel, rowgen)
        multiple_results = [p.apply_async(run_parallel, piped) for piped in picklegen(fpath)]
        print([res.get(timeout=1) for res in multiple_results])
        print('close')
        p.close()
        p.join()

    filters = [
            #lambda rowdict: rowdict['velocity_knots_max'] == 'NULL' or float(rowdict['velocity_knots_max']) > 50,
            lambda rowdict: rowdict['src_zone'] == 'Z0' and rowdict['rcv_zone'] == 'NULL',
            lambda rowdict: rowdict['minutes_spent_in_zone'] == 'NULL' or rowdict['minutes_spent_in_zone'] <= 1,
        ]
    aggregate_output(filters=filters)



    ''' step-through
        

        colnames = [
                'mmsi', 'time', 'lon', 'lat', 
                'cog', 'sog', 'msgtype',
                'imo', 'vessel_name',  
                'dim_bow', 'dim_stern', 'dim_port', 'dim_star',
                'ship_type', 'ship_type_txt',
                'deadweight_tonnage', 'submerged_hull_m^2',
                'km_from_shore', 'depth_metres',
            ]
        kwargs = dict(filters=filters)
        kwargs = {}
        parallel=12

        track_merged = next(trackgen(merged, colnames))

        track_merged = next(trackgen([merged[0]], colnames))


        track_merged = next(trackgen(merged, colnames))
        while track_merged['mmsi'] < 262006976:
            track_merged = next(trackgen(merged, colnames))

        for rows in merged:
            if len(np.unique(rows[:,1])) != len(rows[:,1]): break
        # track = next(trackgen(rows))

    '''


if False:  # testing

    with open('output/testrows', 'wb') as f:
        #assert len(rows) > 1000
        for row in rowgen:
            pickle.dump(row, f)

    with open('output/mergedrows', 'wb') as f:
        #assert len(list(merged)) > 1000
        #pickle.dump(merged, f)
        for row in merged:
            pickle.dump(row, f)
        
    rowgen = []
    with open('tests/output/testrows', 'rb') as f:
        while True:
            try:
                rows = pickle.load(f)
            except EOFError as e:
                break
            rowgen.append(rows)

    merged = []
    with open('tests/output/mergedrows', 'rb') as f:
        while True:
            try:
                rows = pickle.load(f)
            except EOFError as e:
                break
            merged.append(rows)

    colnames = [
            'mmsi', 'time', 'lon', 'lat', 
            'cog', 'sog', 'msgtype',
            'imo', 'vessel_name',  
            'dim_bow', 'dim_stern', 'dim_port', 'dim_star',
            'ship_type', 'ship_type_txt',
            'deadweight_tonnage', 'submerged_hull_m^2',
            'km_from_shore', 'depth_metres',
        ]


    from importlib import reload
    import track_gen
    reload(track_gen)
    from track_gen import *

    tracks = np.array(list(trackgen(merged, colnames=colnames)))
    filters = [
            lambda track, rng: compute_knots(track, rng) < 50,
        ]
    
    # step into loops
    track = tracks[0]

    gen = trackgen([rows], colnames=colnames[0:rows.shape[1]])
    for track in gen:

    gen = trackgen(merged, colnames=colnames[0:merged.shape[1]])
    for track in gen:
        if track['mmsi'] == 246770976: break

    rng = list(segment(track, maxdelta=timedelta(hours=3), minsize=1))[0]
    mask = filtermask(track, rng, filters)
    n = sum(mask)
    c = 0
    chunksize=500000

    from shore_dist import shore_dist_gfw
    from gebco import Gebco
    from webdata import marinetraffic
    from wsa import wsa
    sdist = shore_dist_gfw()
    bathymetry = Gebco()
    hullgeom = marinetraffic.scrape_tonnage()

    sdist.__enter__()
    bathymetry.__enter__()
    hullgeom.__enter__()
    sdist.__exit__(None, None, None)
    bathymetry.__exit__(None, None, None)
    hullgeom.__exit__(None, None, None)


"""
db query 1 month: 41 min

maxdelta = timedelta(hours=1)

filters=[lambda track, rng: [True for _ in rng[:-1]]]

filters = [
    lambda track, rng: delta_knots(track, rng) < 50,
    lambda track, rng: delta_meters(track, rng) < 10000,
    lambda track, rng: delta_seconds(track, rng) > 0,
]

for mmsirows in merged:
    if mmsirows[0][0] == 316001408: 
        track_merged = next(trackgen(mmsirows, colnames=colnames))
        break

aggregator = agg_transits_per_segment(track_merged, filters)
transit_window, in_zones, zoneID = next(aggregator)

geofence(track_merged, domain, colnames, filters=None, maxdelta=timedelta(hours=1))

geofence_test2(track_merged, domain)

    backup_track_merged = track_merged.copy()

maxdelta = timedelta(hours=1)

mmsirows = next(merged)
track_merged = next(trackgen(mmsirows, colnames=colnames))
list(geofence(track_merged, domain, colnames, filters=filters))

"""
