#!/usr/bin/env python3
"""
original frontend to fits2azel (requires fits input)
Consider using the more general PlateScale.py
"""

from argparse import ArgumentParser
from numpy import datetime64
import astrometry_azel as ael
import astrometry_azel.plots as aep
from matplotlib.pyplot import show


def main():
    p = ArgumentParser(description="converts fits starfield image to RA/Dec and az/el")
    p.add_argument("infile", help=".fits or .wcs filename with path", type=str)
    p.add_argument(
        "-c", "--latlon", help="tuple of WGS-84 (lat,lon) [degrees]", nargs=2, type=float
    )
    p.add_argument("-t", "--time", help="override UTC time yyyy-mm-ddThh:mm:ss")
    p.add_argument(
        "-s", "--solve", help="run solve-field step of astrometry.net", action="store_true"
    )
    p.add_argument(
        "--clim",
        help="clim of preview images (no effect on computation)",
        nargs=2,
        default=None,
        type=float,
    )
    p.add_argument("-a", "--args", help="arguments to pass through to solve-field")
    P = p.parse_args()

    # %% actually run program
    scale = ael.fits2azel(P.infile, latlon=P.latlon, time=P.time, solve=P.solve, args=P.args)
    # %% write to file
    outfn = scale.filename.with_suffix(".nc")
    print("saving", outfn)
    scale["filename"] = str(scale.filename)
    scale["time"] = datetime64(scale.time)
    scale.to_netcdf(outfn)

    # %% plot
    if show is not None:
        aep.plotradec(scale)
        aep.plotazel(scale)

        show()


if __name__ == "__main__":
    main()
