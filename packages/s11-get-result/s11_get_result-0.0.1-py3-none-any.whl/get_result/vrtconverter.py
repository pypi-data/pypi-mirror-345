# -*- coding: utf-8 -*-
# (c) Satelligence, see LICENSE.rst.
import logging
import os
from pathlib import Path
import threading

import numpy as np
from osgeo import gdal, gdal_array

from get_result.resultconverter import ResultConverterBase


logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


THREAD_LOCAL = threading.local()


def pool_initializer(filename: str) -> None:
    """Initialize dataset in thread-local space.

    Args:
        filename: the filename to open
    """
    gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    gdal.SetConfigOption("GDAL_CACHEMAX", "64")
    gdal.SetConfigOption("GDAL_MAX_DATASET_POOL_RAM_USAGE", "64MB")
    gdal.SetConfigOption("VSI_CACHE", "FALSE")
    gdal.SetConfigOption("VSI_CACHE_SIZE", "0")

    logger.info('Opening dataset in subprocess (this can take a while).')
    THREAD_LOCAL.dataset = gdal.Open(filename)

def read_block(x0: int, x1: int, y0: int, y1: int) -> np.ndarray:
    """Read a chunk from the dataset

    Args:
        x0: starting pixel
        x1: ending pixel
        y0: starting line
        y1: ending line

    Returns:
        np.ndarray: the data
    """
    logger.debug('Read started: %s', (x0, y0, x1 - x0, y1 - y0))
    result = THREAD_LOCAL.dataset.ReadAsArray(x0, y0, x1 - x0, y1 - y0)
    logger.debug('Read finished: %s', (x0, y0, x1 - x0, y1 - y0))
    return result


class VrtResultConverter(ResultConverterBase):

    input_ds: gdal.Dataset

    def open_and_parse_input(self):
        logger.info('Opening dataset (this might take a while with large vrts).')
        self.input_ds = gdal.Open(f'/vsigs/{self.input_uri}')

        logger.debug('Fetching nodata values.')
        if self.args.nodata_per_band:
            self.nodata_values = [self.input_ds.GetRasterBand(bi + 1).GetNoDataValue()
                             for bi in range(self.input_ds.RasterCount)]
        else:
            self.nodata_values = ([self.input_ds.GetRasterBand(1).GetNoDataValue()]
                                  * self.input_ds.RasterCount)
        self.input_geotransform = self.input_ds.GetGeoTransform()
        self.input_projection = self.input_ds.GetProjection()
        self.input_resolution = self.input_geotransform[1]
        self.input_dtype = gdal_array.GDALTypeCodeToNumericTypeCode(
            self.input_ds.GetRasterBand(1).DataType)
        self.input_height = self.input_ds.RasterYSize
        self.input_width = self.input_ds.RasterXSize
        self.input_blocksize = 512
        input_ulx = self.input_geotransform[0]
        input_uly = self.input_geotransform[3]
        input_lrx = input_ulx + self.input_width * self.input_resolution
        input_lry = input_uly + self.input_height * -self.input_resolution
        self.input_bounds = [input_ulx, input_uly, input_lrx, input_lry]

    def create_proxy_dataset(self):
        logger.info('Creating intermediate VRT.')
        tmp_intermediate_vrt = str(Path.cwd() / f'tmp_intermediate_{self.input_uri.split("/")[-1]}')
        new_ulx, new_uly, new_lrx, new_lry = self.output_bounds
        vrt_opts = {}
        vrt_opts['outputBounds'] = new_ulx, new_lry, new_lrx, new_uly
        if self.args.resolution:
            vrt_opts['resolution'] = 'user'
            vrt_opts['xRes'] = self.output_resolution
            vrt_opts['yRes'] = self.output_resolution
        if self.args.resampling:
            vrt_opts['resampleAlg'] = self.args.resampling
        vrt_opts = gdal.BuildVRTOptions(**vrt_opts)
        self.proxy_ds = gdal.BuildVRT('', self.input_ds, options=vrt_opts)
        vrt = self.proxy_ds.GetMetadata('xml:VRT')[0]
        with open(tmp_intermediate_vrt, 'wt') as i_vrt:
            i_vrt.write(vrt)
        self.proxy_ds_path = tmp_intermediate_vrt
        self.output_height = self.proxy_ds.RasterYSize
        self.output_width = self.proxy_ds.RasterXSize
        self.output_nbands = self.proxy_ds.RasterCount
        self.output_geotransform = self.proxy_ds.GetGeoTransform()
        self.output_projection = self.proxy_ds.GetProjection()
        self.output_band_names = [None] * self.output_nbands

        self.read_function = read_block
        self.pool_initializer = pool_initializer
        self.pool_initializer_args = [self.proxy_ds_path]

    def finalize(self):
        os.remove(str(self.proxy_ds_path))
