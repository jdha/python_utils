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
Created on Mon Apr 29 18:39:56 2019

Infill missing data: iteratively taking the geometric mean of surrounding 
points until all NaNs are removed.

@author James Harle

$Last commit on:$
'''

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import ListedColormap

sns.set()

def infill

function [data_out] = infill(data_in,N,bathy)

%  INFILL returns a matrix where all NaNs have been filled in
%     [DATA_OUT] = INFILL(DATA_IN) returns data with any NaNs replaced by 
%     iteratively taking the geometric mean of surrounding points until
%     all NaNs are romved. Input data must be 1D or 2D.
%
%     In:   data_in   (real arr)
%
%     Out:  data_out  (real arr)          
%
%     Author: J Harle (jdha) 19-10-08
%
%     See also 

% check number of dims

if ndims(data_in)>2
    error('INFILL can only take a 1D or 2D matrix')
end

% intial setup 

ind   = find(isnan(data_in) & bathy>0) ; % just to kick start while loop
s_din = size(data_in) ;

% continue to infill until all NaNs are removed
n=0;
while ~isempty(ind) && n<N
    
    [i,j] = find(isnan(data_in) & bathy>0) ;
    
    % create indices of neighbouring points
    
    jp1 = j+1 ; ip1 = i+1 ; im1 = i-1 ; jm1 = j-1 ;
    
    % correct for out of bounds
    
    jp1(jp1>length(data_in(1,:))) = j(jp1>length(data_in(1,:))) ;
    jm1(jm1==0) = j(jm1==0) ;
    ip1(ip1>length(data_in(:,1))) = i(ip1>length(data_in(:,1))) ;
    im1(im1==0) = i(im1==0) ;

    % create 1D indices as quicker than looping over i and j
    
    ind_e = sub2ind(s_din,im1,j);
    ind_w = sub2ind(s_din,ip1,j);
    ind_s = sub2ind(s_din,i,jm1);
    ind_n = sub2ind(s_din,i,jp1);

    % replace NaNs
                   
    data_in(ind) = nanmean([data_in(ind_e), data_in(ind_w), ... 
                            data_in(ind_s), data_in(ind_n)],2) ;
                        
                      
    % find new indices for next loop
    
    ind   = find(isnan(data_in) & bathy>0);
    
    n=n+1;  
end

data_out = data_in ;