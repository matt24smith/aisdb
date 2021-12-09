import os
import zipfile

import requests
from tqdm import tqdm
import rasterio
import numpy as np

from common import *


class Gebco():

    def fetch_bathymetry_grid(self):
        """ download geotiff zip archive and extract it """

        zipf = os.path.join(data_dir, "gebco_2020_geotiff.zip")

        # download the file if necessary
        if not os.path.isfile(zipf):
            print('downloading gebco bathymetry (geotiff ~8GB decompressed)... ')
            url = 'https://www.bodc.ac.uk/data/open_download/gebco/gebco_2020/geotiff/'
            with requests.get(url, stream=True) as payload:
                assert payload.status_code == 200, 'error fetching file'
                with open(zipf, 'wb') as f:
                    with tqdm(total=3730631664, desc=zipf, unit='B', unit_scale=True) as t:
                        for chunk in payload.iter_content(chunk_size=8192): 
                            _ = t.update(f.write(chunk))

            # unzip the downloaded file
            with zipfile.ZipFile(zipf, 'r') as zip_ref:
                print('extracting bathymetry data...')
                zip_ref.extractall(path=data_dir)

        return


    def __enter__(self):
        self.fetch_bathymetry_grid()

        self.rasterfiles = { k : None for k in sorted([f for f in os.listdir(data_dir) if f[-4:] == '.tif' and 'gebco' in f ]) }

        filebounds = lambda fpath: { f[0]: float(f[1:]) for f in fpath.split('gebco_2020_', 1)[1].rsplit('.tif', 1)[0].split('_') }

        self.rasterfiles = { f : filebounds(f) for f in self.rasterfiles }

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        for filepath, bounds in self.rasterfiles.items():
            if 'dataset' in bounds.keys():
                bounds['dataset'].close()
                bounds['dataset'].stop()
                del bounds['dataset']
                del bounds['band1']


    def getdepth(self, lon, lat):
        ''' get grid cell elevation value for given coordinate. negative values are below sealevel '''
        for filepath, bounds in self.rasterfiles.items():
            if bounds['w'] <= lon <=  bounds['e'] and bounds['s'] <= lat <= bounds['n']: 
                if not 'band1' in bounds.keys(): 
                    bounds.update({'dataset': rasterio.open(os.path.join(data_dir, filepath))})
                    bounds.update({'band1': bounds['dataset'].read(1)})
                ixlon, ixlat = bounds['dataset'].index(lon, lat)
                return bounds['band1'][ixlon-1 , ixlat-1 ]


    def getdepth_cellborders_nonnegative_avg(self, lon, lat):
        ''' get the average depth of surrounding grid cells from the given coordinate
            the absolute value of depths below sea level will be averaged 
        ''' 

        for filepath, bounds in self.rasterfiles.items():
            if bounds['w'] <= lon <=  bounds['e'] and bounds['s'] <= lat <= bounds['n']: 
                if not 'band1' in bounds.keys(): 
                    bounds.update({'dataset': rasterio.open(os.path.join(data_dir, filepath))})
                    bounds.update({'band1': bounds['dataset'].read(1)})

                ixlon, ixlat = bounds['dataset'].index(lon, lat)
                depths = np.array([ bounds['band1'][xlon-1, xlat-1] 
                    for xlon in range(ixlon-1, ixlon+2) 
                    for xlat in range(ixlat-1, ixlat+2) 
                    if (xlon!=ixlon and xlat!=ixlat) 
                    and (0 <= xlon <= bounds['dataset'].width) 
                    and (0 <= xlat <= bounds['dataset'].height)])
                mask = depths < 0

                if sum(mask) == 0: 
                    return 0

                return np.average(depths[mask] * -1)


'''
with Gebco() as bathymetry:
    bathymetry.getdepth_cellborders_nonnegative_avg(lon=-63.3, lat=44.5)

'''