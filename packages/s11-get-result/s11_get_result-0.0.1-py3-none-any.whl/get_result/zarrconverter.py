# -*- coding: utf-8 -*-
# (c) Satelligence, see LICENSE.rst.
import itertools
import logging
import threading

import numpy as np
from osgeo import gdal
import xarray as xr

from get_result.resultconverter import ResultConverterBase
from get_result.lerccodec import register_lerc_codec

gdal.UseExceptions()
# try to minimize memory usage by gdal
gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
gdal.SetConfigOption("GDAL_CACHEMAX", "64")
gdal.SetConfigOption("GDAL_MAX_DATASET_POOL_RAM_USAGE", "64MB")
gdal.SetConfigOption("VSI_CACHE", "FALSE")
gdal.SetConfigOption("VSI_CACHE_SIZE", "0")


logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


register_lerc_codec()


THREAD_LOCAL = threading.local()


def pool_initializer(uri) -> None:
    """Initialize dataset in thread-local space.
    """
    logger.debug('starting pool init, opening zarr %s...', uri)
    THREAD_LOCAL.dataset = xr.open_zarr(
        uri,
        chunks=None, 
        consolidated=True,
        decode_coords="all",
    )['data']
    logger.debug('pool init done.')


class ZarrResultConverter(ResultConverterBase):

    input_ds: xr.DataArray

    def open_and_parse_input(self):
        logger.info('Opening zarr.')
        with xr.open_zarr(
                self.input_uri, chunks=None, consolidated=True, decode_coords="all"
        )['data'] as input_ds:
            other_dims = [d for d in input_ds.dims if d not in ['x', 'y']]
            if 'band' in other_dims:
                # make sure band is the first
                other_dims.remove('band')
                other_dims = ['band'] + other_dims
            other_coords = {dim: input_ds.coords[dim].values.tolist() for dim in other_dims}
            keys, values = zip(*other_coords.items())
            self.input_band_selectors = [dict(zip(keys, v)) for v in itertools.product(*values)]
            print(other_dims)
            print(other_coords)
            print(keys, values)
            print(self.input_band_selectors)
            self.output_band_names = ['_'.join([str(v) for v in d.values()])
                                      for d in self.input_band_selectors]
            self.output_nbands = len(self.output_band_names)
            self.input_height, self.input_width = input_ds.rio.shape
            ulx, lry, lrx, uly = input_ds.rio.bounds()
            self.input_bounds = [ulx, uly, lrx, lry]
            self.input_resolution = input_ds.rio.resolution()[0]
            self.nodata_values = [input_ds.rio.nodata.item()] * self.output_nbands
            self.input_projection = input_ds.rio.crs.to_wkt()
            self.input_geotransform = input_ds.rio.transform().to_gdal()
            self.input_blocksize = 512
            self.input_dtype = input_ds.dtype

        self.output_dtype = self.input_dtype
        self.output_projection = self.input_projection

    def read_block(self, x0: int, x1: int, y0: int, y1: int) -> np.ndarray:
        """Read a chunk from the dataset

        Args:
            x0: starting pixel
            x1: ending pixel
            y0: starting line
            y1: ending line

        Returns:
            np.ndarray: the data
        """
        x_slice = slice(x0, x1)
        y_slice = slice(y0, y1)
        h = y1 - y0
        w = x1 - x0
        result = np.empty((self.output_nbands, h, w))
        chunk_full_data = THREAD_LOCAL.dataset.isel(x=x_slice, y=y_slice)
        for band in range(self.output_nbands):
            result[band] = chunk_full_data.sel(**self.input_band_selectors[band]).to_numpy()
        logger.debug('reading done for %s: %s', (x0, x1, y0, y1), result.shape)
        return result

    def create_proxy_dataset(self):
        self.offset_x = round((self.output_bounds[0] - self.input_bounds[0]) / self.output_resolution)
        self.offset_y = round((self.input_bounds[1] - self.output_bounds[1]) / self.output_resolution)

        self.read_function = self.read_block
        self.pool_initializer = pool_initializer
        self.pool_initializer_args = [self.input_uri]
