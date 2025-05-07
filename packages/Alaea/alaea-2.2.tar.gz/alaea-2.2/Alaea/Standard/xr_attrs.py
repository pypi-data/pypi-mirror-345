#!/Users/christmas/opt/anaconda3/bin/python3
# -*- coding: utf-8 -*-
#  日期 : 2023/9/18 15:38
#  作者 : Christmas
#  邮箱 : 273519355@qq.com
#  项目 : Project
#  版本 : python 3
#  摘要 :
"""

"""
import numpy as np
from .. import new_filename

__all__ = ['add_coors_attrs', 'add_lon_attrs', 'add_lat_attrs', 'add_time_attrs', 'add_TIME_attrs',
           'add_wind_attrs', 'add_temperature_attrs', 'add_precipitation_attrs', 'add_slp_attrs', 'fixed_encoding']


def add_coors_attrs(ds):
    """
    给xarray.Dataset添加经纬度、时间等的属性
    :param ds: xarray.Dataset
    :return: xarray.Dataset
    """
    lon_name, lat_name, time_name, TIME_name = 'longitude', 'latitude', 'time', 'TIME'
    for i in ds.sizes.keys():  # ds.dims.keys(): --> FutureWarning
        if i in ['lon', 'longitude']:
            lon_name = i
        elif i in ['lat', 'latitude']:
            lat_name = i
        elif i in ['time']:
            time_name = i
        elif i in ['TIME']:
            TIME_name = i
    add_lon_attrs(ds, lon_name)
    add_lat_attrs(ds, lat_name)
    add_time_attrs(ds, time_name)
    add_TIME_attrs(ds, TIME_name, dim_name='DateStr')
    return ds
    

def add_lon_attrs(_ds, lon_name):
    """
    给经度添加属性
    :param _ds: xarray.Dataset
    :param lon_name: 经度维度名
    """
    _ds[lon_name].attrs = {
        'units': 'degrees_east',
        'long_name': 'longitude',
        'standard_name': 'longitude',
        'axis': 'X',
        'westernmost': np.round(_ds[lon_name].data.min(), 2),
        'easternmost': np.round(_ds[lon_name].data.max(), 2),
    }
    _ds[lon_name].encoding = {'_FillValue': None}
    return _ds


def add_lat_attrs(_ds, lat_name):
    """
    给纬度添加属性
    :param _ds: xarray.Dataset
    :param lat_name: 纬度维度名
    """
    _ds[lat_name].attrs = {
        'units': 'degrees_north',
        'long_name': 'latitude',
        'standard_name': 'latitude',
        'axis': 'Y',
        'southernmost': np.round(_ds[lat_name].data.min(), 2),
        'northernmost': np.round(_ds[lat_name].data.max(), 2)
    }
    _ds[lat_name].encoding = {'_FillValue': None}
    return _ds


def add_time_attrs(_ds, time_name):
    """
    给时间添加属性
    :param _ds: xarray.Dataset
    :param time_name: 时间维度名
    """
    _ds[time_name].attrs = {
        'units': 'seconds since 1970-01-01 00:00:00',
        'long_name': 'UTC time',
        'standard_name': 'UTC_time',
        'axis': 'T',
        'calendar': 'gregorian',
    }
    _ds[time_name].encoding = {'_FillValue': None, 'dtype': 'float64', 'unlimited_dims': 'time'}
    return _ds


def add_TIME_attrs(_ds, TIME_name, dim_name='DateStr'):
    """
    给TIME添加属性
    :param _ds: xarray.Dataset
    :param TIME_name: TIME名
    :param dim_name: TIME维度名
    """
    _ds[TIME_name].attrs = {
        'reference_time': ''.join(_ds[TIME_name].data[0].astype(str))[:10],
        'long_name': 'UTC time',
        'standard_name': 'UTC_time',
        'calendar': 'gregorian',
        'start_time': ''.join(_ds[TIME_name].data[0].astype(str)),
        'end_time': ''.join(_ds[TIME_name].data[-1].astype(str))
    }
    _ds[TIME_name].encoding['char_dim_name'] = dim_name
    return _ds


def add_wind_attrs(_ds):
    """
    给xarray.Dataset添加全局属性
    :param _ds: xarray.Dataset
    """
    U10_name, V10_name = 'U10', 'V10'
    for i in list(_ds.data_vars.keys()):
        if i in ['wind_U10', 'U10', 'u10']:
            U10_name = i
        elif i in ['wind_V10', 'V10', 'v10']:
            V10_name = i
    _ds[U10_name].attrs = {
        'units': 'm s-1',
        'long_name': '10 meter U wind component',
        'standard_name': 'eastward_wind',
    }
    _ds[V10_name].attrs = {
        'units': 'm s-1',
        'long_name': '10 meter V wind component',
        'standard_name': 'northward_wind',
    }
    _ds[U10_name].encoding = dict(_FillValue=9.962100e+36, dtype='single', zlib=True)
    _ds[V10_name].encoding = dict(_FillValue=9.962100e+36, dtype='single', zlib=True)
    return _ds


def add_temperature_attrs(_ds):
    """
    给xarray.Dataset添加全局属性
    :param _ds: xarray.Dataset
    """
    T2_name = 'temperature'
    for i in list(_ds.data_vars.keys()):
        if i in ['temperature', 'T2', 't2']:
            T2_name = i
    _ds[T2_name].attrs = {
        'units': 'K',
        'long_name': 'temperature at 2m',
        'standard_name': 'temperature_at_2m'
    }
    _ds[T2_name].encoding = dict(_FillValue=9.962100e+36, dtype='single', zlib=True)
    return _ds


def add_precipitation_attrs(_ds):
    """
    给xarray.Dataset添加全局属性
    :param _ds: xarray.Dataset
    """
    precipitation_name = 'precipitation'
    for i in list(_ds.data_vars.keys()):
        if i in ['precipitation', 'Precipitation']:
            precipitation_name = i
    _ds[precipitation_name].attrs = {
        'units': 'mm',
        'long_name': 'precipitation, positive for ocean gaining water',
        'standard_name': 'precipitation_positive_ocean_gaining_water'
    }
    _ds[precipitation_name].encoding = dict(_FillValue=9.962100e+36, dtype='single', zlib=True)
    return _ds


def add_slp_attrs(_ds):
    """
    给xarray.Dataset添加全局属性
    :param _ds: xarray.Dataset
    """
    slp_name = 'slp'
    for i in list(_ds.data_vars.keys()):
        if i in ['slp', 'SLP']:
            slp_name = i
    _ds[slp_name].attrs = {
        'units': 'Pa',
        'long_name': 'sea level pressure',
        'standard_name': 'sea_level_pressure'
    }
    _ds[slp_name].encoding = dict(_FillValue=9.962100e+36, dtype='single', zlib=True)
    return _ds


def fixed_encoding(_ds, **kwargs):
    """
    修正xarray.Dataset的encoding
    """
    _ds.encoding['unlimited_dims'] = 'time'
    _ds.encoding['format'] = 'NETCDF4'
    _ds.encoding['engine'] = 'h5netcdf'
    _ds.encoding['dtype'] = 'float32'
    _ds.encoding['complevel'] = 4
    _ds.encoding['zlib'] = True
    _ds.encoding['shuffle'] = True
    _ds.encoding['fletcher32'] = True
    _ds.encoding['contiguous'] = True
    _ds.encoding.update(kwargs)
    return _ds
