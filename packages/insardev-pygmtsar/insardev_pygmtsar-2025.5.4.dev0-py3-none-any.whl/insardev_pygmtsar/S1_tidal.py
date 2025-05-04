# ----------------------------------------------------------------------------
# insardev_pygmtsar
#
# This file is part of the InSARdev project: https://github.com/AlexeyPechnikov/InSARdev
#
# Copyright (c) 2025, Alexey Pechnikov
#
# See the LICENSE file in the insardev_pygmtsar directory for license terms.
# ----------------------------------------------------------------------------
from .S1_gmtsar import S1_gmtsar

class S1_tidal(S1_gmtsar):

    def tidal_los_rad(self, stack):
        """
        Calculate tidal LOS displacement [rad] for data dates and spatial extent
        """
        return 1000*self.tidal_los(stack)/self.los_displacement_mm(1)

    def tidal_los(self, stack):
        """
        Interpolate pre-calculated tidal displacement for data pairs dates on the specified grid
        and convert to LOS displacement in meters
        """
        import pandas as pd
        import dask
        import xarray as xr
        import numpy as np

        # extract pairs
        if len(stack.dims) == 3:
            pairs, dates = self.get_pairs(stack, dates=True)
            pairs = pairs[['ref', 'rep']].astype(str).values
            grid = stack[0]
        else:
            dates = [stack[key].dt.date.astype(str).item() for key in ['ref', 'rep']]
            pairs = [dates]
            grid = stack
        #return (pairs, dates)

        solid_tide = self.get_tidal().sel(date=dates)
        # satellite look vector
        sat_look = self.get_satellite_look_vector()

        def interp_block(pair, ys_block, xs_block):
            # use outer variables
            date1, date2 = pair
            # interpolate on the data_pairs 2D grid
            coords = {'y': ys_block, 'x': xs_block}
            block_tidal1 = solid_tide.sel(date=date1).interp(coords, method='linear', assume_sorted=True)\
                .compute(n_workers=1)
            block_tidal2 = solid_tide.sel(date=date2).interp(coords, method='linear', assume_sorted=True)\
                .compute(n_workers=1)
            block_look = sat_look.interp(coords, method='linear', assume_sorted=True)\
                .compute(n_workers=1)
            block_tidal = block_tidal2 - block_tidal1
            los = xr.dot(xr.concat([block_look.look_E, block_look.look_N, block_look.look_U], dim='dim'),
                      xr.concat([block_tidal.dx, block_tidal.dy, block_tidal.dz], dim='dim'),
                      dims=['dim'])
            del block_tidal, block_tidal2, block_tidal1, block_look, coords
            return los.data[None,].astype(np.float32)

        # define output radar coordinates grid and split to equal chunks and rest
        ys_blocks = np.array_split(grid.y, np.arange(0, grid.y.size, self.chunksize)[1:])
        xs_blocks = np.array_split(grid.x, np.arange(0, grid.x.size, self.chunksize)[1:])

        # per-block processing
        blocks3d  = []
        for pair in pairs:
            #print ('pair', pair)
            blocks2d  = []
            for ys_block in ys_blocks:
                blocks = []
                for xs_block in xs_blocks:
                    block = dask.array.from_delayed(dask.delayed(interp_block)(pair, ys_block, xs_block),
                                                    shape=(1, ys_block.size, xs_block.size), dtype=np.float32)
                    blocks.append(block)
                    del block
                blocks2d.append(blocks)
                del blocks
            blocks3d.append(blocks2d)
            del blocks2d
        dask_block = dask.array.block(blocks3d)
        del blocks3d

        if len(stack.dims) == 3:
            out = xr.DataArray(dask_block, coords=stack.coords)
        else:
            out = xr.DataArray(dask_block[0], coords=stack.coords)
        del dask_block
        return out.rename(stack.name)

    def tidal_los_rad(self, stack):
        """
        Calculate tidal LOS displacement [rad] for data_pairs pairs and spatial extent
        """
        return 1000*self.tidal_los(stack)/self.los_displacement_mm(1)

    def tidal_correction_wrap(self, stack):
        """
        Apply tidal correction to wrapped phase pairs [rad] and wrap the result.
        """
        return self.wrap(stack - self.tidal_los_rad(stack)).rename(stack.name)
    
    def get_tidal(self):
        return self.open_cube('tidal')

    def _tidal(self, date, grid):
        import xarray as xr
        import pandas as pd
        import numpy as np
        from io import StringIO, BytesIO
        import subprocess

        coords = np.column_stack([grid.ll.values.ravel(), grid.lt.values.ravel()])
        buffer = BytesIO()
        np.savetxt(buffer, coords, delimiter=' ', fmt='%.6f')
        stdin_data = buffer.getvalue()
        #print ('stdin_data', stdin_data)

        SC_clock_start, SC_clock_stop = self.PRM(date).get('SC_clock_start', 'SC_clock_stop')
        dt = (SC_clock_start + SC_clock_stop)/2
        argv = ['solid_tide', str(dt)]
        #cwd = os.path.dirname(self.filename) if self.filename is not None else '.'
        cwd = self.workdir
        p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwd, bufsize=10*1000*1000)
        stdout_data, stderr_data = p.communicate(input=stdin_data)
        stderr_data = stderr_data.decode('utf8')
        if stderr_data is not None and len(stderr_data):
            #print ('DEBUG: solid_tide', stderr_data)
            assert 0, f'DEBUG: solid_tide: {stderr_data}'
        out = np.fromstring(stdout_data, dtype=np.float32, sep=' ').reshape(grid.y.size, grid.x.size, 5)[None,]
        coords = {'date': pd.to_datetime([date]), 'y': grid.y, 'x': grid.x}
        das = {v: xr.DataArray(out[...,idx], coords=coords) for (idx, v) in enumerate(['lon', 'lat', 'dx', 'dy', 'dz'])}
        ds = xr.Dataset(das)
        return ds

    def compute_tidal(self, dates=None, coarsen=32, n_jobs=-1, interactive=False):
        import xarray as xr
        import numpy as np
        from tqdm.auto import tqdm
        import joblib

        if dates is None:
            dates = self.df.index.unique()

        # expand simplified definition
        if not isinstance(coarsen, (list,tuple, np.ndarray)):
            coarsen = (coarsen, coarsen)

        trans_inv = self.get_trans_inv()
        dy, dx = np.diff(trans_inv.y)[0], np.diff(trans_inv.x)[0]
        #print ('dy, dx', dy, dx)
        #step_y, step_x = int(np.round(coarsen[0]*dy)), int(np.round(coarsen[1]*dx))
        # define target grid spacing
        step_y, step_x = int(coarsen[0]/dy), int(coarsen[1]/dx)
        #print ('step_y, step_x', step_y, step_x)
        # fix zero step when specified coarsen is larger than the transform grid coarsen
        if step_y < 1:
            step_y = 1
        if step_x < 1:
            step_x = 1
        grid = trans_inv.sel(y=trans_inv.y[step_y//2::step_y], x=trans_inv.x[step_x//2::step_x])

        def tidal(date):
            return self._tidal(date, grid)

        with self.progressbar_joblib(tqdm(desc='Tidal Computation', total=len(dates))) as progress_bar:
            outs = joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(tidal)(date) for date in dates)

        ds = xr.concat(outs, dim='date')
        if interactive:
            return ds
        self.save_cube(ds, 'tidal', 'Solid Earth Tides Saving')
