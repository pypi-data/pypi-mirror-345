"""
Demo app to deform an image by hand. Hold shift and click-n-drag.
"""

import visvis as vv
import imageio

from pirt.apps.deform_by_hand import DeformByHand

im = imageio.imread("imageio:astronaut.png")[:, :, 2].astype("float32")
d = DeformByHand(im, grid_sampling=40)

vv.use().Run()
