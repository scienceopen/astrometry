#!/usr/bin/env python3
"""
Identify coordinates of cropped image in original image.
Handy for when you cropped visually or forgot the cropping parameters.

Template matching is used.
"""

from __future__ import annotations
import typing
import skimage.feature as skf
import imageio
import numpy as np
from pathlib import Path
import argparse
from matplotlib.pyplot import figure, show


def load_gray(fn1: Path, fn2: Path) -> tuple:
    """
    load images in grayscale and same bit depth
    """

    rgb2gray = [0.299, 0.587, 0.114]

    im1 = imageio.imread(fn1).dot(rgb2gray).astype(np.uint8)
    im2 = imageio.imread(fn2).dot(rgb2gray).astype(np.uint8)

    return im1, im2


def find_crop(im1, im2) -> tuple[int, ...]:
    res = skf.match_template(im1, im2)
    # values (-1, 1) and peak is at upper left corner of match.
    Ul = np.unravel_index(res.argmax(), res.shape)

    return Ul


def plot_overlay(im1, im2, Ul: typing.Sequence[int], fn1: Path, fn2: Path):
    overlay = np.zeros((*im1.shape, 3), dtype=im1.dtype)
    rows = slice(Ul[0], Ul[0] + im2.shape[0])
    cols = slice(Ul[1], Ul[1] + im2.shape[1])
    overlay[:, :, 0] = im1
    overlay[rows, cols, 2] = im2

    # the diff may not be precisely zero everywhere if the crop did filtering
    diff = overlay[rows, cols, 0] - overlay[rows, cols, 2]
    print("sum(im1-im2) over ROI is:", diff.sum())

    fg = figure()
    axs: typing.Any = fg.subplots(1, 2)
    h1 = axs[0].imshow(overlay, alpha=0.6)
    axs[0].set_title(f"overlay: original {fn1.name}:red   crop {fn2.name}:blue", wrap=True)
    fg.colorbar(h1, ax=axs[0])

    h2 = axs[1].imshow(diff)
    axs[1].set_title("im1 - im2 over ROI")
    fg.colorbar(h2, ax=axs[1])

    fg.suptitle(f"upper left corner of crop on original image: {Ul}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("fn1", help="original large image")
    p.add_argument("fn2", help="cropped smaller image")
    P = p.parse_args()

    fn1 = Path(P.fn1).expanduser()
    fn2 = Path(P.fn2).expanduser()

    im1, im2 = load_gray(fn1, fn2)

    Ul = find_crop(im1, im2)
    print(f"upper left corner (pixel indices) of {fn2.name} in {fn1.name} is {Ul}")

    plot_overlay(im1, im2, Ul, fn1, fn2)
    show()
