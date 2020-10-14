#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 19:59:38 2020

@author: jdha
"""

from netCDF4 import Dataset
import numpy as np

def nc_subset(root_url, root_fname, lon_lim, lat_lim):

    """
    You could also attempt this using NCO but it would require DAP 
    dependance to work
    
    example usage:
    
        root_url='http://opendap4gws.jasmin.ac.uk/thredds/nemo/dodsC/grid_T/2005/'
        root_fname='ORCA0083-N06_20050105d05T.nc'
        nc_subset(root_url, root_fname, (0,70), (65,80))
    """
    
    # Lets just set the output filename to the input filename for now
    file_out = root_fname
    file_in  = root_url+'/'+root_fname

    # create output file
    ncfile = Dataset(file_out, 'w', format="NETCDF4")
    print(ncfile)
    
    # open input file
    rootgrp = Dataset(file_in, "r")
    
    # grab variable list
    variables  = rootgrp.variables
    dimensions = rootgrp.dimensions
    
    nav_lat = variables['nav_lat'][:,:]
    nav_lon = variables['nav_lon'][:,:]
    
    # sub set lengths
    ind = np.where((nav_lat>=lat_lim[0]) & (nav_lat<=lat_lim[1]) & 
                   (nav_lon >=lon_lim[0]) & (nav_lon<=lon_lim[1]) )
    
    i_coords = (np.min(ind[1]),np.max(ind[1]))
    j_coords = (np.min(ind[0]),np.max(ind[0]))
    
    
    nx = i_coords[1] - i_coords[0] + 1
    ny = j_coords[1] - j_coords[0] + 1
           
    # create the x, y and other dimensions in the outout file
    dim_len={}
    for d in dimensions.keys():
        if d == 'x':
            ncfile.createDimension('x', nx)
            dim_len['x'] = nx
        elif d == 'y':
            ncfile.createDimension('y',ny)
            dim_len['y'] = ny
        else:
            ncfile.createDimension(d, dimensions[d].size)
            dim_len[d] = dimensions[d].size

    # create variables for output
    for v in variables.keys():
        print(v)
        new_var = ncfile.createVariable(v, 
                                        variables[v].dtype.str[1:], 
                                        variables[v].dimensions)
        var_dim_out = []
        var_dim_in  = []
    
        for dim in variables[v].dimensions:
            if dim == 'x':
                var_dim_in.append(slice(i_coords[0],i_coords[1]+1))
                var_dim_out.append(slice(0,nx))
            elif dim =='y':
                var_dim_in.append(slice(j_coords[0],j_coords[1]+1))
                var_dim_out.append(slice(0,ny))
            else:
                if dim_len[dim]>0:
                    var_dim_in.append(slice(0, dim_len[dim]))
                    var_dim_out.append(slice(0, dim_len[dim]))
                else:
                    var_dim_in.append(0)
                    var_dim_out.append(0)
        print(var_dim_out)
        print(var_dim_in)
        # Not too sure why this fix has to be used
        if (var_dim_in[0]==0 and len(var_dim_in)==1):
            var_dim_in=(0,)
            
        # Subset data
        new_var[var_dim_out] = rootgrp.variables[v][var_dim_in]
        
    # close files       
    ncfile.close()
    try: # for some reason I can't close the pointer to the remote data!!
        rootgrp.close() 
    except:
        print('remote file not closed')
            
            