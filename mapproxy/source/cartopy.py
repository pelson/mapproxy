# This file is part of the MapProxy project.
# Copyright (C) 2011 Omniscale <http://omniscale.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import with_statement, absolute_import

import io
import sys
import time
import threading

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from mapproxy.grid import tile_grid
from mapproxy.image import ImageSource
from mapproxy.image.opts import ImageOptions
from mapproxy.layer import MapExtent, DefaultMapExtent, BlankImage, MapLayer
from mapproxy.source import  SourceError
from mapproxy.client.log import log_request
from mapproxy.util.py import reraise_exception
from mapproxy.util.async import run_non_blocking
from mapproxy.compat import BytesIO

import logging
log = logging.getLogger(__name__)

class CartopySource(MapLayer):
    supports_meta_tiles = False
    def __init__(self, layers=None, image_opts=None, coverage=None,
        res_range=None, lock=None, reuse_map_objects=False, scale_factor=None):
        MapLayer.__init__(self, image_opts=image_opts)
        self.coverage = coverage
        self.res_range = res_range
        self.layers = set(layers) if layers else None
        self.scale_factor = scale_factor
        self.lock = lock
        if self.coverage:
            self.extent = MapExtent(self.coverage.bbox, self.coverage.srs)
        else:
            self.extent = DefaultMapExtent()

    def get_map(self, query):
        if self.res_range and not self.res_range.contains(query.bbox, query.size,
                                                          query.srs):
            raise BlankImage()
        if self.coverage and not self.coverage.intersects(query.bbox, query.srs):
            raise BlankImage()

        try:
            resp = self.render(query)
        except RuntimeError as ex:
            log.error('could not render Mapnik map: %s', ex)
            reraise_exception(SourceError(ex.args[0]), sys.exc_info())
        resp.opacity = self.opacity
        return resp

    def render(self, query):
        if self.lock:
            with self.lock():
                return self.render_non_blocking(query)
        else:
            return self.render_non_blocking(query)

    def render_non_blocking(self, query):
        return run_non_blocking(self._render, (query, ))

    def _is_compatible(other, query):
        print('COMAT? ', other, query)
        return True

    def _render(self, query):
        start_time = time.time()
        fig = plt.figure(figsize=(query.size[0]/100, query.size[1]/100), dpi=100)
        proj_code = '+init=%s' % str(query.srs.srs_code.lower())
        if proj_code in ['+init=crs:84', '+init=epsg:4326']:
            #            crs = ccrs.PlateCarree(globe=ccrs.Globe())
            crs = ccrs.PlateCarree()
        elif proj_code in ['+init=epsg:3857', '+init=epsg:3785', '+init=epsg:900913']:
            # TODO: I'm not sure this it correct.
            crs = ccrs.Mercator.GOOGLE
        else:
            raise ValueError('Unsupported projection {}'.format(proj_code))

        envelope = query.bbox

        ax = fig.add_axes([0, 0, 1, 1], projection=crs)
        ax.set_aspect('auto')
        ax.outline_patch.set_visible(False)
        ax.background_patch.set_visible(False)
        ax.set_xlim(envelope[0], envelope[2])
        ax.set_ylim(envelope[1], envelope[3])

        data = None
        reasonable_layers = []
        try:
            if self.layers:
                raise ValueError('layers?')

            ax.coastlines('10m')

            if self.scale_factor:
                raise ValueError('Scale factor not yet handled.')
            else:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=100, transparent=True)
                buf.seek(0)
                data = buf
              # Convert using PIL?
##            data = img.tostring(str(query.format))
        finally:
            log_request('%s:%s:%s:%s' % (proj_code, query.bbox, query.srs.srs_code, query.size),
                status='200' if data else '500', method='API', duration=time.time()-start_time)

        return ImageSource(data, size=query.size,
            image_opts=ImageOptions(transparent=self.transparent, format=query.format))
