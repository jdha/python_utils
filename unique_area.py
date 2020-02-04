# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

'''
Created on Thur Mar 7 07:39:56 2019

Identify and rank isolated areas within a mask array.

@author James Harle

$Last commit on:$
'''

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import ListedColormap

sns.set()

def sort_areas(msk, val, ew_wrap):
    """
    Identify isolated areas within a mask array and rank in order
    according to size: largest = 1. Input array should be orientated
    with axis 0 => latitude, axis 1 => longitude if dealing with 
    geographic data.

    Args:
        msk     (numpy.ndarray): input array with isolated areas
        val               (int): value associated with isolated areas
        ew_wrap       (logical): zonally continuous domain?

    Returns:
        area    (numpy.ndarray): output array with ranked areas
    """

    # Gather dimension of input array
    ny, nx = msk.shape

    # Make sure we are dealing with floating point numbers
    msk = msk.astype(float)

    if ew_wrap:

        msk = np.pad(msk, ((1, 1), (0, 0)), 'constant',
                     constant_values=(np.nan))

    else:

        nx += 2
        msk = np.pad(msk, ((1, 1), (1, 1)), 'constant',
                     constant_values=(np.nan))

    ny += 2

    print msk.shape, ny, nx
    # Initialise array and starting value
    area = np.zeros((ny, nx), dtype=int)
    numb = 1

    # Identify active points to evaluate
    iy, ix = np.nonzero(msk == val)

    # Determine unique areas and rank
    while len(iy) > 0:
        print(len(iy))
        iy, ix       = iy[0:1], ix[0:1]
        area[iy, ix] = numb

        while len(iy) > 0:

            # Identify neighbouring points
            iy = np.concatenate((iy, iy+1, iy-1, iy  , iy  ))
            ix = np.concatenate((ix, ix  , ix  , ix+1, ix-1))

            iy = np.where(iy>=ny, iy-ny, iy)
            ix = np.where(ix>=nx, ix-nx, ix)

            iy = np.where(iy<0  , iy+ny, iy)
            ix = np.where(ix<0  , ix+nx, ix)

            ind = np.logical_and(msk[(iy, ix)]==val, area[(iy, ix)]==0)

            iy, ix = iy[ind], ix[ind]

            area[(iy, ix)] = numb

        # Increment counter
        numb += 1

        # Start new search with new set of indices
        ind    = np.logical_and(msk==val, area==0)
        iy, ix = np.nonzero(ind)

    # Now to rank the identified areas
    cover = np.zeros((numb-1, 1), dtype=int)

    for n in np.arange(1, numb):

        cover[n-1,] = np.sum(area == n)

    # Sort the areas according to their size, from the largest to the smallest
    ind    = np.argsort(-cover, axis=None)
    area_s = np.zeros((ny, nx), dtype=int)

    for n in np.arange(1, numb):

        numb_ind         = np.nonzero(area == ind[n-1]+1)
        area_s[numb_ind] = n

    # Remove padding before returning values
    if ew_wrap:

        area = area_s[1:-1 , :   ]

    else:

        area = area_s[1:-1 , 1:-1]

    return area

def test():
    """
    Simple test function to check things are working as they should
    be and to provide an example.

    Args:
    """

    mask_noc = np.zeros((10,28))
    
    mask_noc[1:9,0],   mask_noc[1:9,7],  mask_noc[8,1],     mask_noc[7,2]     = 1, 1, 1, 1
    mask_noc[6,3],     mask_noc[5,4],    mask_noc[4,5],     mask_noc[5,6]     = 1, 1, 1, 1
    mask_noc[2,7],     mask_noc[3,6],    mask_noc[2,6],     mask_noc[1,7]     = 1, 1, 1, 1
    mask_noc[3,5],     mask_noc[4,4],    mask_noc[5,3],     mask_noc[6,2]     = 1, 1, 1, 1
    mask_noc[7,1],     mask_noc[1:9,10], mask_noc[1:9,17],  mask_noc[1,10:17] = 1, 1, 1, 1
    mask_noc[8,10:17], mask_noc[1:9,20], mask_noc[1,20:28], mask_noc[8,20:28] = 1, 1, 1, 1
    
    area_1 = sort_areas(mask_noc,1.,False)
    area_2 = sort_areas(mask_noc,1.,True)
    
    # Create figure handle
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=1, ncols=3, figsize=(12, 5))
    
    # Plot map
    ax0.set_title('Mask Array')
    plt.sca(ax0)
    plt.pcolormesh(mask_noc)
    plt.colorbar()
    
    ax1.set_title('Without EW wrap')
    plt.sca(ax1)
    plt.pcolormesh(area_1)
    plt.colorbar()
    
    ax2.set_title('With EW wrap')
    plt.sca(ax2)
    plt.pcolormesh(area_2)
    plt.colorbar()
    
                    
def plot_areas(area):
    """
    Simple plotting of the area array created by sort_areas

    Args:
        area    (numpy.ndarray): output array with ranked areas
    """

    # Gather dimensions
    ny, nx = area.shape
    y      = np.arange(ny)
    x      = np.arange(nx)
    nmax   = np.max(area)

    # Create figure handle
    fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1, figsize=(8, 12))

    # Set colourmap using seaborn
    cmap = ListedColormap(sns.color_palette("deep", nmax))

    # Mask unwanted values
    area = np.ma.masked_where((area < 1), area)

    # Plot map
    plt.sca(ax0)
    sns.heatmap(area, cmap=cmap, mask=area.mask, cbar=None,
                vmin=1, vmax=np.max(area))

    ax0.set_title('Ranked Area')
    plt.ylim((0, ny-1)), plt.xlim((0, nx-1))

    # Generate some sequential data
    x = np.arange(1, nmax+1)
    y = np.histogram(area[area > 0], bins=nmax)[0]
    sns.barplot(x=x, y=y, palette="deep", ax=ax1)
    ax1.set_ylabel("Coverage")

    # Make sure spacing is ok
    fig.tight_layout()

    plt.show()
