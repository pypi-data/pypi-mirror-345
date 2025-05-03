#!/usr/bin/env python

import argparse
import logging
from pathlib import Path
import sys

import gcsfs

from get_result.vrtconverter import VrtResultConverter
from get_result.zarrconverter import ZarrResultConverter


logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# todo:
#  - error on unsuported args for zarr
#  - don't overwrite output file
#  - set bandnames
#  - s11-production-dprof-cache/Deforestation/deforestation_filtered/deforestation_filtered_v2.zarr does not work as input


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, nargs='+',
                        help='bucket + uri where the result is stored; format: "bucket/uri/to/data" or "bucket/resultnumber"')
    # parser.add_argument('dataset', type=str,
    #                     help='number of the dprof result, or key to zarr')
    parser.add_argument('--threads', type=int, required=False, default=3,
                        help='number of simultaneous download threads to use')
    parser.add_argument('--bounds', type=float, nargs=4, required=False,
                        help='output bounds (minx miny maxx maxy)')
    parser.add_argument('--resolution', type=float, required=False,
                        help='output resolution (in decimal degrees')
    parser.add_argument('--dtype', type=str, required=False,
                        help='output dtype')
    parser.add_argument('--resampling', type=str, required=False,
                        help='resampling algorithm (any of nearest, bilinear, cubic, cubicspline, '
                             'lanczos, average, mode)')
    parser.add_argument('--nodata-per-band', action='store_true',
                        help='when true, propagate a separate nodata value for each band, instead '
                             'of using the nodata value from the first band for all bands, '
                             'assuming that it is the same for the whole file. This is slightly '
                             'slower with result vrts with many bands.')
    parser.add_argument('--list', action='store_true',
                        help='print a list of vrts of this result, then exit')
    parser.add_argument('--outdir', type=str, required=False,
                        help='output folder. Cannot be used together with --outname; '
                             'default output filename(s) are used.')
    parser.add_argument('--outname', type=str, required=False,
                        help='output file name. Cannot be used together with --outdir.')
    parser.add_argument('--align-to-blocks', default=True, action=argparse.BooleanOptionalAction,
                        help='align output bounds to source blocks (faster but bounds might change)')
    parser.add_argument('--chunk-timeout', type=int, default=300,
                        help='timeout to read a single output chunk (in seconds).')
    parser.add_argument('--blocks-per-job', type=int, default=1, required=False,
                        help='approximate number of blocks per job. Default: 1')
    parser.add_argument('--debug', action='store_true',
                        help='enable debug logging.')

    args = parser.parse_args()
    list_vrts = args.list
    threads = args.threads
    sources = args.source
    resolution = args.resolution
    resampling = args.resampling
    nodata_per_band = args.nodata_per_band

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.outdir and args.outname:
        raise RuntimeError('Cannot specify both --outdir and --outname.')

    for source in sources:
        bucket, uri = source.split('/', maxsplit=1)

        if '.zarr' in uri:
            # if no group specified, use the defaul 'result' group
            if uri.endswith('.zarr'):
                uri = f'{uri}/result'
            zarr_converter = ZarrResultConverter(f'gs://{bucket}/{uri}', args)
            zarr_converter.convert()

        else:
            try:
                result_number = f'{int(uri):06d}'
            except ValueError:
                # last part cannot be parsed as int, so it's not a dprof deliverable result
                vrt_converter = VrtResultConverter(f'{bucket}/{uri}', args)
                vrt_converter.convert()
            else:
                gcs = gcsfs.GCSFileSystem(requester_pays=True)

                vrts = [Path(f) for f in gcs.ls(f'{bucket}/{result_number}/', detail=False)
                        if f.endswith('.vrt')]

                print(f'Found {len(vrts)} vrts:')
                for vrt in vrts:
                    print(vrt)

                if list_vrts:
                    sys.exit()

                for vrt in vrts:
                    vrt_converter = VrtResultConverter(str(vrt), args)
                    vrt_converter.convert()


if __name__ == "__main__":
    main()
