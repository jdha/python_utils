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

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
sns.set()

def sort_areas(msk, val, ew_wrap):
    """ 
    Identify isolated areas within a mask array and rank in order
    according to size: largest = 1.

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
        
        msk = np.pad(msk, ((0,0),(1,1)), 'constant', constant_values=(np.nan))
        
    else:
        
        nx += 2
        msk = np.pad(msk, ((1,1),(1,1)), 'constant', constant_values=(np.nan))

    ny += 2

    # Initialise array and starting value
    area = np.zeros((ny,nx), dtype=int) 
    numb = 1 

    # Identify active points to evaluate
    iy, ix = np.nonzero(msk==val)
        
    # Determine unique areas and rank
    while len(iy) > 0:
        
        iy, ix      = iy[0:1], ix[0:1]
        area[iy,ix] = numb   
        
        while len(iy) > 0:
            
            # Identify neighbouring points
            iy = np.concatenate((iy, iy+1, iy+1, iy  , iy  ))
            ix = np.concatenate((ix, ix  , ix  , ix+1, ix-1))
            
            np.where(iy>=ny, iy-ny, iy)
            np.where(ix>=nx, ix-nx, ix)
            
            np.where(iy<0  , iy+ny, iy)
            np.where(ix<0  , ix+nx, ix)
            
            ind = np.logical_and(msk[(iy,ix)]==val,area[(iy,ix)]==0)
            
            iy, ix = iy[ind], ix[ind]

            area[(iy,ix)] = numb 
 
        # Increment counter
        numb += 1
        
        # Start new search with new set of indices
        ind    = np.logical_and(msk==val,area==0)
        iy, ix = np.nonzero(ind)
        
        
    # Now to rank the identified areas
    cover = np.zeros((numb-1,1), dtype=int)

    for n in np.arange(1,numb):
        
        cover[n-1,] = np.sum(area==n)
        
    # Sort the areas according to their size, from the largest to the smallest
    ind    = np.argsort(-cover,axis=None)
    area_s = np.zeros((ny,nx), dtype=int)

    for n in np.arange(1,numb):

        numb_ind         = np.nonzero(area==ind[n-1]+1)
        area_s[numb_ind] = n
        
    # Remove padding before returning values
    if ew_wrap:
        
        area = area_s[:,1:-1]
    
    else:
        
        area = area_s[1:-1,1:-1]

    return area

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
    cmap = ListedColormap(sns.color_palette("Paired", nmax))
    
    # Mask unwanted values
    area = np.ma.masked_where((area < 1), area)
    
    # Plot map
    plt.sca(ax0)
    sns.heatmap(area, cmap=cmap, mask=area.mask, cbar=None, 
                vmin=1, vmax=np.max(area))
    
    ax0.set_title('Ranked Area')
    plt.ylim((0,ny-1)), plt.xlim((0,nx-1))

    # Generate some sequential data
    x = np.arange(1, nmax+1)
    y = np.histogram(area[area>0], bins=nmax)[0]
    sns.barplot(x=x, y=y, palette="Paired", ax=ax1)
    ax1.set_ylabel("Coverage")

    # Make sure spacing is ok
    fig.tight_layout()

    plt.show()


