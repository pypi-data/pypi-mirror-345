# -*- coding: utf-8 -*-
# (c) Satelligence, see LICENSE.rst.
import argparse
from concurrent.futures import Future
from functools import partial
import logging
import math
import multiprocessing
import os
from pathlib import Path
import signal
import sys
import time
from typing import Any, List

import numpy as np
from osgeo import gdal, gdal_array
from pebble import ProcessPool
from tqdm import tqdm


logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def align_coord_to_block(coord, pixelsize, blocksize, ceil=True):
    block = blocksize * abs(pixelsize)
    if ceil:
        new = math.ceil(coord / block) * block
    else:
        new = math.floor(coord / block) * block
    if pixelsize < 0:
        new = -new
    return new

def prepare_block_grid(width, height, blocksize):
    blocks = []
    for y0 in range(0, height, blocksize):
        y1 = min(y0 + blocksize, height)
        for x0 in range(0, width, blocksize):
            x1 = min(x0 + blocksize, width)
            blocks.append((x0, x1, y0, y1))
    return blocks


class ResultConverterBase():

    input_resolution: float
    input_projection: str
    input_geotransform: list[float]
    input_blocksize: int
    input_bounds: list[float]
    input_dtype: np.dtype
    input_bandnames: list[str]
    proxy_ds: gdal.Dataset | None
    nodata_values: list[float]
    job_blocksize: int
    output_resolution: float
    output_height: int
    output_width: int
    output_nbands: int
    output_dtype: np.dtype
    output_projection: str
    output_geotransform: list[float]
    output_band_names: list[str | None]
    blocks: list[tuple[float, float, float, float]]
    offset_x: int = 0
    offset_y: int = 0

    def __init__(self, input_uri: str, args: argparse.Namespace):
        if args.debug:
            logger.setLevel(logging.DEBUG)
        self.input_uri = input_uri
        self.args = args
        self.open_and_parse_input()


    def __getstate__(self):
        # prevent gdal dataset objects to be pickled
        new_dict = {}
        for k, v in self.__dict__.items():
            if not isinstance(v, gdal.Dataset):
                new_dict[k] = v
        return new_dict

    def open_and_parse_input(self):
        raise NotImplementedError

    def read_block(self, x0, x1, y0, y1):
        raise NotImplementedError

    def get_optimal_output_blocksize(self):
        logger.debug('Determining optimal output blocksize.')
        # determine more efficient blocksize when up/downsampling, so that the ratio of
        # output blocks to input blocks is closer to 1

        # if self.args.resolution:
        #     self.output_resolution = self.args.resolution
        # else:
        #     self.output_resolution = self.input_resolution

        resolution_ratio = self.input_resolution / self.output_resolution

        blocksize = int(2**round(np.log2(np.clip(512 * resolution_ratio, 16, 1048))))
        logger.info(f'Input resolution: {self.input_resolution}. Output resolution: {self.output_resolution}')
        logger.info(f'Resolution from/to ratio: {resolution_ratio:.3f}. '
              f'Using output blocksize: {blocksize}')
        return blocksize

    def get_job_blocksize(self):
        blocks_per_job_sqrt = round(math.sqrt(self.args.blocks_per_job))
        job_blocksize = blocks_per_job_sqrt * self.blocksize
        logger.info(f'Using jobs of {blocks_per_job_sqrt}x{blocks_per_job_sqrt} chunks.')
        return job_blocksize

    def set_output_bounds(self):
        input_blocksize = self.input_blocksize
        input_resolution = self.input_resolution
        output_resolution = self.output_resolution
        if not self.args.bounds:
            ulx, uly, lrx, lry = self.input_bounds
        else:
            ulx, uly, lrx, lry = self.args.bounds
        # the previous version had bounds as ulx lry lrx uly. Because we only use latlon, let's
        # detect that and convert to ulx uly lrx lry.
        if uly < lry:
            uly, lry = lry, uly
        if self.args.align_to_blocks:
            # align to chunks
            new_ulx = align_coord_to_block(ulx, input_blocksize, input_resolution, ceil=False)
            new_uly = align_coord_to_block(uly, input_blocksize, -input_resolution, ceil=False)
            new_lrx = align_coord_to_block(lrx, input_blocksize, input_resolution, ceil=True)
            new_lry = align_coord_to_block(lry, input_blocksize, -input_resolution, ceil=True)
        else:
            logger.info('Not aligning to source blocks')
            new_ulx, new_uly, new_lrx, new_lry = ulx, uly, lrx, lry
        self.output_bounds = (new_ulx, new_uly, new_lrx, new_lry)
        self.output_width = round((new_lrx - new_ulx) / output_resolution)
        self.output_height = round((new_uly - new_lry) / output_resolution)
        self.output_geotransform = [new_ulx, output_resolution, 0, new_uly, 0, -output_resolution]

    def create_proxy_dataset(self):
        self.proxy_ds_path = self.input_uri
        self.proxy_ds = self.input_ds

    def prepare_output_dataset(self):
        if self.args.outdir:
            cwd = Path(self.args.outdir)
        else:
            cwd = Path.cwd()
        input_basename = self.input_uri.split('/')[-1]
        self.output_tif_tmp = (cwd / input_basename).with_suffix('.tif.tmp')
        self.output_tif = self.args.outname \
            if self.args.outname \
            else (cwd / input_basename).with_suffix('.tif')
        gdal_dtype = gdal_array.NumericTypeCodeToGDALTypeCode(self.output_dtype)
        gdal_driver = gdal.GetDriverByName('GTiff')
        options = [
            "tiled=yes",
            "compress=zstd",
            f"blockxsize={self.blocksize}",
            f"blockysize={self.blocksize}",
            "bigtiff=yes",
            "interleave=band",
        ]
        if np.issubdtype(self.output_dtype, np.floating):
            predictor = 3
        else:
            predictor = 2
        options.append(f'predictor={predictor}')

        logger.debug('Initializing output dataset...')
        print('Creating output file:',
            str(self.output_tif),
            self.output_width,
            self.output_height,
            self.output_nbands,
            gdal_dtype, options,
        )
        target_ds = gdal_driver.Create(
            str(self.output_tif_tmp),
            self.output_width,
            self.output_height,
            self.output_nbands,
            gdal_dtype,
            options,
        )
        target_ds.SetProjection(self.output_projection)
        target_ds.SetGeoTransform(self.output_geotransform)

        for bi in range(self.output_nbands):
            if self.nodata_values[bi] is not None:
                target_ds.GetRasterBand(bi + 1).SetNoDataValue(self.nodata_values[bi])
            if self.output_band_names[bi] is not None:
                target_ds.GetRasterBand(bi + 1).SetDescription(self.output_band_names[bi])

        return target_ds

    def save_or_resubmit_chunk(
            self,
            succeeded: List,
            errored: List,
            x0: int,
            x1: int,
            y0: int,
            y1: int,
            bar: tqdm,
            future: Future,
    ) -> None:
        """Callback to save a chunk to the target file. In case of error, append to errored list.

        Args:
            succeeded: the list where succesful chunks are stored
            errored: the list where errored chunks are stored
            x0: starting pixel
            x1: ending pixel
            y0: starting line
            y1: ending line
            bar: tqdm progress bar object
            future: the future to save the result from
        """
        if future.cancelled():
            return
        try:
            result = future.result()
        except Exception as e:
            logger.error('Exception: %s.', e)
            # actually we should distinguish here between retryable errors and fatal errors, and only
            # continue with the retryable group, and raise otherwise. Something for the future.
            errored.append((x0, x1, y0, y1))
            return
        if result is None:
            errored.append((x0, x1, y0, y1))
        else:
            self.output_ds.WriteArray(result, x0, y0)
            succeeded.append((x0, x1, y0, y1))
            logger.debug('Writing done.')
        future._result = None
        bar.update()

    def process_blocks_parallel(
            self,
            max_tries=10,
    ):
        counter = 0
        error_count = 0
        threads = self.args.threads
        chunk_timeout = self.args.chunk_timeout
        blocks_remaining = self.blocks.copy()
        pool_initializer_function = getattr(self, 'pool_initializer', None)
        pool_initializer_args = getattr(self, 'pool_initializer_args', [])

        while blocks_remaining and counter < max_tries:
            logger.info(f'Try {counter + 1}/{max_tries}')
            logger.debug(f'Starting process pool with {threads} workers.')
            ctx = multiprocessing.get_context('spawn')
            with ProcessPool(
                initializer=pool_initializer_function,
                initargs=pool_initializer_args,
                max_workers=threads,
                context=ctx,
            ) as pool:
                logger.debug('Pool ready.')

                def ctrl_c_handler(signum: int, frame: Any) -> None:
                    """Handle ctrl-c properly by shutting down the process pool

                    Args:
                        signum (int): signum
                        frame (any): frame
                    """
                    # only continue in the main process, not in child processes
                    if multiprocessing.parent_process() is not None:
                        return
                    print('CTRL-C DETECTED, SHUTTING DOWN WORKER POOL.', flush=True)
                    pool.stop()
                    pool.join(timeout=0)
                    bar.close()
                    print('Worker pool shutdown complete. Exiting.')
                    sys.exit(1)
                signal.signal(signal.SIGINT, ctrl_c_handler)

                submitted = 0

                logger.info(f'Submitting {len(blocks_remaining)} jobs.')
                bar = tqdm(total=len(blocks_remaining), dynamic_ncols=True, smoothing=0)
                errored = []
                succeeded = []

                for block in blocks_remaining:
                    x0, x1, y0, y1 = block
                    read_args = [
                        x0 + self.offset_x,
                        x1 + self.offset_x,
                        y0 + self.offset_y,
                        y1 + self.offset_y,
                    ]
                    logger.debug('scheduling %s', read_args)
                    future = pool.schedule(
                        self.read_function,
                        args=read_args,
                        timeout=chunk_timeout,
                    )
                    future.add_done_callback(
                        partial(
                            self.save_or_resubmit_chunk,
                            succeeded, errored, x0, x1, y0, y1, bar,
                        )
                    )
                    submitted += 1
                    pressure = submitted - (len(succeeded) + len(errored))
                    while pressure > threads * 2:
                        time.sleep(0.1)
                        pressure = submitted - (len(succeeded) + len(errored))

                # wait for all futures to be finished *and for all callbacks to have finished*
                while len(succeeded) < len(blocks_remaining):
                    pass
                bar.close()

                counter += 1
                error_count = len(errored)
                if errored and counter < max_tries:
                    logger.info(f'retrying {error_count} blocks...')

                blocks_remaining = errored.copy()
        return error_count

    def finalize(self):
        pass

    def convert(self):
        max_tries = 10
        if self.args.resolution:
            self.output_resolution = self.args.resolution
        else:
            self.output_resolution = self.input_resolution
        self.blocksize = self.get_optimal_output_blocksize()
        self.job_blocksize = self.get_job_blocksize()
        self.set_output_bounds()
        print(f'chunk-optimized output bounds: {self.output_bounds}')
        self.output_dtype = np.dtype(self.args.dtype) if self.args.dtype else self.input_dtype
        self.create_proxy_dataset()
        self.blocks = prepare_block_grid(self.output_width, self.output_height, self.job_blocksize)
        self.output_ds = self.prepare_output_dataset()

        error_count = self.process_blocks_parallel(
            max_tries=max_tries,
        )

        if error_count > 0:
            print(f'{error_count} blocks failed even after {max_tries} retries.')
            print('Something might be wrong on googles end.')
            print('Giving up.')
        else:
            os.rename(str(self.output_tif_tmp), str(self.output_tif))
            print(f"Finished {self.input_uri}.\n", flush=True)

        self.finalize()
