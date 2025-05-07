# Get raster data from google cloud storage 


## Prerequisites

* GDAL library
* GCLOUD SDK activated
* gcsfs, tqdm, pebble, numpy, and a few more packages. `pip install -r requirements.txt` will install everything for you.

**NOTE ON GDAL** 
You need to install gdal using `pip install gdal`. Perhaps you get an error that
the installation did not go ok. That's most likely due to a mismatch of the binaries of 
gdal that you have and the python version. Check the version of the binaries you 
have by running `gdalinfo --version`. Then fill in that version in the pip install:
`pip install gdal==<version>`


## TL;DR: how to run

You can use this tool to download any type of gdal readable file (vrt, tif, etc) from google
cloud storage. In addition, you can also use it to download zarr's (those that we use in dprof),
and there is a shortcut to easily download dprof results.

In general, usage is `python get_result.py <url>`.

`<url>` should start with the bucket name, without the "gs://" prefix.


### Examples:

#### .vrt (or other gdal-readable formats)

Get any kind of gdal-readable file, e.g. the 2015 V6.1 FBL from the vrt:
```commandline
python get_result.py s11-base-data/landcover/forest_baselines/FBL_V6.1/2015/FBL_V6.1_2015.vrt 
```

#### .zarr

Get the deforestation zarr:
```commandline
python get_result.py s11-production-dprof-cache/Deforestation/deforestation/deforestation.zarr
```
Note that you don't need to append the "/result" part to the zarr url if you want to read from the /result group.
If you want to read from a different group, just append that to the zarr url, e.g. "s11-bucket/some.zarr/some_group".

#### dprof results

The shortcut to download results (will download every vrt for that result) is: `python get_result.py <bucket>/<resultnumber>`
E.g.:
```commandline
python get_result.py s11-production-dprof-result/13883
```

For more options, see below.


## Usage

**get_result.py** [-h] [--threads THREADS] [--bounds ULX ULY LRX LRY] [--resolution RESOLUTION] [--dtype DTYPE] [--resampling RESAMPLING] [--nodata-per-band] [--list] [--outname OUTNAME] [--align-to-blocks | --no-align-to-blocks] [--chunk-timeout TIMEOUT] [--debug] source_url


positional arguments:
:  source_url:            url to the dataset, see above for examples.

options:
:  -h, --help:            show this help message and exit.
:  --threads THREADS:     number of simultaneous download threads to use (default=3).
:  --bounds ULX ULY LRX LRY:
                        output bounds (minx miny maxx maxy).
:  --resolution RESOLUTION:
                        output resolution (in decimal degrees). **(NOT APPLICABLE TO ZARR)**
:  --resampling RESAMPLING:
                        resampling algorithm (any of: nearest (default), bilinear, cubic, cubicspline, lanczos, average, mode). **(NOT APPLICABLE TO ZARR)**
:  --nodata-per-band:
                        propagate a separate nodata value for each band, instead of using the nodata value from the first band for all bands, assuming that it is the same for the whole file. This is slightly slower with result vrts with many bands. **(NOT APPLICABLE TO ZARR)**
:  --list:                print a list of vrts of the Result, then exit. **(NOT APPLICABLE TO ZARR)**
:  --dtype:             override datatype for output tif (defaults to the input datatype).
:  --outname:           output file name (if not given, uses the source name).
:  --no-align-to-blocks:    don't optimize reading by extending the output bounds, such
                        that these align to the internal blocks of the source dataset (will slightly 
                        extend the output bounds).
                        The default is to align to input blocks, because it is better for performance.
                        If you want the exact bounds as specified, use --no-align-to-blocks.
:  --chunk-timeout:     Timeout for handling a single (output) chunk job, in seconds. Default = 300 (5 minutes).
                        You might need to increase this when resampling to a much coarser resolution.
:  --blocks-per-job:    the amount of chunks to read in a single job. For zarr, it makes sense to set this higher; for vrt usually not.
:  --debug:             enable debug logging.

**Note that the options related to sub/resampling do not apply to zarr sources!**
Because the zarr's are not read by gdal, we cannot use gdal's resampling implementation. Zarr inputs
will always be read at their full input resolution.


## Example with options

To download result 011605 in the Production bucket, but only an area in South Borneo, resampled to 0.01x0.01 DD per pixel using average resampling:

```commandline
python get_result.py s11-production-dprof-results/11605 --bounds 113 -1 114 -2 --resolution 0.0001 --resampling average
```

NB. this example will run quite slow due to the much larger output pixel size (0.0001 output vs 0.00006 input).
You might need to add `--chunk-timeout` with a larger value than the default (300) option to allow for longer chunk job processing times.

## Caveats

* the output file will be named the same as the input VRT, but the ".vrt" extension replaced with ".tif"
* the script is trying to use an optimal chunk size for the output tif, within the 16-1048 range, so that a single output chunk maps approx. to a single input chunk
* the output will be written to the folder where the script is invoked
* the script will download each vrt first, because opening the vrt remotely is extremely slow for bigger vrts. The vrt is removed again when the download is finished.
* specifying a significantly lower output resolution than the input resolution will cause the chunks to take a lot of time per chunk (because for each output chunk, a lot of input data needs to be read). If you get errors like `Exception: [Errno Task timeout]`, you should increase the --chunk-timeout value (the default is 300) * chunks that error will be retried max 10 times. Getting a few error is quite normal, but if you get many errors, there probably is an issue with gcs at google's side.
* for some reason, the performance for zarrs (e.g. the deforestation zarr, maybe it is because of the sparseness) is much lower than for vrt's. Often it helps to specify a higher value for --blocks-per-job, e.g. 16 or even 64. Ymmv.
* you should be able to kill the script with ctrl-c. However, this does not always correctly cancel chunks that were already downloading, so it might take some time before it really stops. If you really need to stop it now, after hitting ctrl-c, use `pkill -f get_result.py` which will kill it immediately (if you have pkill installed).
