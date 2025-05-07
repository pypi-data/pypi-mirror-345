import geopandas as gpd
import pandas as pd
import requests
import json
import numpy as np
import os
import osmnx as ox

from shapely.ops import orient


class PipeNetwork:
    def __init__(self, api_key, pipe_gdf):
        """
        Initialize the PipeNetwork class with a GeoDataFrame.
        :param geodataframe: GeoDataFrame containing pipe network data.
        """
        if not isinstance(pipe_gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame.")
        if pipe_gdf.empty:
            raise ValueError("The provided GeoDataFrame is empty.")
        self.api_key = api_key
        self.network = pipe_gdf.to_crs('epsg:4326')

    def get_lof(self, id_col, construction_col, renovation_col, material_col, dimension_col, length_col):
        """
        Uses the API endpoint to get a Likelihood-of-failure estimation
        :return: geodataframe with LoF column.
        """
        pipe_network_ = self.network.drop(['geometry'], axis=1)
        pipe_network_[construction_col] = pd.to_numeric(pipe_network_[construction_col],
                      errors='coerce').fillna(0)
        if renovation_col is not None:
            pipe_network_[renovation_col] = pd.to_numeric(pipe_network_[renovation_col],
                                                        errors='coerce').fillna(0)
        x = requests.post('https://www.waterworks.ai/api/pipenetwork/lof',
                          json={'df': pipe_network_.to_json(orient='records', date_format='iso'), 'api_key': self.api_key,
                                'id': id_col,
                                'construction': construction_col, 'renovation': renovation_col,
                                'material': material_col,
                                'dimension': dimension_col, 'length': length_col})
        js = x.json()
        df_lof = pd.read_json(json.dumps(js), orient='records')
        df_lof = df_lof.set_index(id_col)
        gdf_lof = self.network.set_index(id_col)
        gdf_lof['RUL'] = df_lof['RUL']
        gdf_lof['LoF'] = df_lof['LoF']
        gdf_lof = gdf_lof.reset_index()

        return gdf_lof

    def get_cof(self, id_col, dimension_col):
        """
        Uses the API endpoint to get a Consequence-of-failure estimation
        :return: geodataframe with CoF column.
        """
        pipe_network_ = self.network
        pipe_network_[dimension_col] = pd.to_numeric(pipe_network_[dimension_col],
                                                      errors='coerce').fillna(0)
        cof = requests.post('https://www.waterworks.ai/api/pipenetwork/cof',
                            json={'bounds': pipe_network_.total_bounds.tolist(), 'api_key': self.api_key})
        js = cof.json()
        gdf_cof = gpd.GeoDataFrame.from_features(js['features'])
        join = gpd.sjoin(pipe_network_, gdf_cof)
        join = join[[id_col, 'CoF']].groupby(id_col).max()
        pipe_network_ = pipe_network_.set_index(id_col)
        pipe_network_['CoF'] = join['CoF']
        pipe_network_ = pipe_network_.reset_index()
        pipe_network_['CoF'] = pipe_network_['CoF'].fillna(0) # 0 where no environmental risks exist
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        pipe_network_[['dim_scaled']] = scaler.fit_transform(
            pipe_network_[[dimension_col]])
        pipe_network_['CoF'] = pipe_network_['CoF'] + (0.5*pipe_network_['dim_scaled']) # add dimension as CoF-parameter
        pipe_network_[['CoF']] = scaler.fit_transform(
            pipe_network_[['CoF']])

        return pipe_network_

    def get_rof(self, gdf_lof, gdf_cof, id_col):
        """
        Takes (prior) LoF and CoF calculations (geodataframes) and calculates risk-of-failure (RoF).
        :return: geodataframe with RoF column.
        """
        gdf_rof = gdf_lof.set_index(id_col)
        gdf_cof = gdf_cof.set_index(id_col)

        gdf_rof['CoF'] = gdf_cof['CoF']
        gdf_rof['RoF'] = gdf_rof['LoF']*gdf_rof['CoF']
        gdf_rof = gdf_rof.reset_index()

        return gdf_rof

    def get_renewal_need(self, renewal_rate, gdf_lof, gdf_rof, id_col, material_col, length_col):
        """
        Takes LoF and RoF calculations (geodataframes), a renewal rate (%) and names for id, material and length columns.
        :return: geodataframes with annual renewal need (per material) and pipes to be included in 5-year plan.
        """
        df = gdf_lof.copy()
        tot_len = df[length_col].sum()
        rr = 0.01 * renewal_rate
        renewal = round(rr * tot_len)
        years = np.arange(1, 50, 1)
        ids = []
        df_all = pd.DataFrame(columns=['Year', 'Material', 'Renewal Need (km)'])
        for mat in df[material_col].unique().tolist():
            renewal_needs = []
            for yr in years:
                df = df.sort_values(by=['RUL'])
                df['cs'] = df[length_col].cumsum()
                df['RUL'] = df['RUL'] - 1
                need = df.loc[df['RUL'] <= 0]  # [length_col].sum() / 1000
                rel_need = need.loc[need[material_col] == mat][length_col].sum() / 1000
                renewal_needs.append(rel_need)
                df.loc[df['cs'] < renewal, 'RUL'] = 100
                #if yr <= 5:
                #    ids.extend(need[id_col].tolist())

            df_plot = pd.DataFrame()
            df_plot['Year'] = years
            df_plot['Year'] = 2024 + df_plot['Year']
            df_plot['Material'] = mat
            df_plot['Renewal Need (km)'] = renewal_needs

            df_all = pd.concat([df_all, df_plot])

        gdf_rof = gdf_rof.sort_values(by=['RoF'], ascending=False)
        gdf_rof['cs'] = gdf_rof[length_col].cumsum()
        five_year_plan = gdf_rof.loc[gdf_rof['cs'] <= 5*renewal]

        return df_all, five_year_plan

class Flow:
    def __init__(self, api_key, flow_tags):
        """
        Initialize the Flow class with an API-key and a flow_tags dict.
        """

        self.api_key = api_key
        self.flow_tags = flow_tags

    def forecast(self, tag_name, weather=None):
        """
                Uses the API endpoint to generate a forecast
                """
        if weather is not None:
            lat = weather['lat']
            lon = weather['lon']
        else:
            lat = None
            lon = None
        df = self.flow_tags[tag_name]
        x = requests.post('https://www.waterworks.ai/api/forecast',
                          json={'df': df.to_json(orient='records', date_format='iso'), 'api_key': self.api_key, 'lat': lat,
                                'lon': lon})
        js = x.json()
        # fig = plotly.io.from_json(json.dumps(js))
        fcst = pd.read_json(json.dumps(js), orient='records')

        return fcst


    def detect_leak(self, tag_name, unit, mode='anomaly'): #modes='anomaly','night'
        """
        Uses the API endpoint to detect leaks
        """
        df = self.flow_tags[tag_name]
        x = requests.post('https://www.waterworks.ai/api/leakage',
                          json={'df': df.to_json(orient='records', date_format='iso'), 'unit': unit,
                                'mode': mode, 'api_key':self.api_key})
        js = x.json()
        if mode == 'night':
            fcst = pd.read_json(js['df'], orient='records')
            trend = json.dumps(js['trend'])
            avg = fcst['night'].mean()/fcst['y'].mean()

            return fcst, avg, trend
        else:
            fcst = pd.read_json(json.dumps(js), orient='records')
            df['ds'] = pd.to_datetime(df['ds'])
            fcst['ds'] = pd.to_datetime(fcst['ds'])
            df = df.set_index('ds')
            fcst = fcst.set_index('ds')
            df['Alarm'] = fcst['anomaly']
            active = fcst.iloc[-3:]['anomaly'].sum()

            df.loc[df['Alarm'] == 1, 'Alarm'] = df['y']
            df.loc[df['Alarm'] == 0, 'Alarm'] = None
            df = df.reset_index()

            if active > 0:
                active = True
            else:
                active = False

            return df, active


    def detect_blockage(self, tag_name):
        """
        Uses the API endpoint to detect blockages
        """
        df = self.flow_tags[tag_name]
        x = requests.post('https://www.waterworks.ai/api/blockage',
                          json={'df': df.to_json(orient='records', date_format='iso'), 'api_key': self.api_key})
        js = x.json()
        # fig = plotly.io.from_json(json.dumps(js))
        fcst = pd.read_json(json.dumps(js), orient='records')
        df['ds'] = pd.to_datetime(df['ds'])
        fcst['ds'] = pd.to_datetime(fcst['ds'])
        df = df.set_index('ds')
        fcst = fcst.set_index('ds')
        df['Alarm'] = fcst['anomaly']
        active = fcst.iloc[-3:]['anomaly'].sum()
        df.loc[df['Alarm'] == 1, 'Alarm'] = df['y']
        df.loc[df['Alarm'] == 0, 'Alarm'] = None
        df = df.reset_index()

        if active > 0:
            active = True
        else:
            active = False

        return df, active

    def inflow_infiltration(self, tag_name, infil_mode='pe', person_equivalents=None): #infil_mode='pe','night'
        """Uses the API endpoint to derive inflow & infiltration volumes in sewage flows"""
        df = self.flow_tags[tag_name]
        x = requests.post('https://www.waterworks.ai/api/inflow',
                          json={'df': df.to_json(orient='records', date_format='iso'), 'infil_mode':infil_mode, 'api_key': self.api_key})
        js = x.json()
        fcst = pd.read_json(json.dumps(js), orient='records')

        if infil_mode == 'pe' and person_equivalents is not None:
            unit = person_equivalents['unit']
            population = person_equivalents['population']
            personal_daily_volume = person_equivalents['personal_daily_volume']
            u = unit.split('/')[-1]
            if u == 's':
                vol = (population * personal_daily_volume) / 86400
            elif u == 'h':
                vol = (population * personal_daily_volume) / 24
            elif u == 'd':
                vol = population * personal_daily_volume
            share = vol / fcst['DWF'].mean()
            fcst['ds'] = pd.to_datetime(fcst['ds'])
            fcst = fcst.set_index('ds')
            daily_mean = fcst['DWF'].resample('D').mean().rename('mean')
            fcst = fcst.join(daily_mean, on=fcst.index.floor('D'))
            fcst = fcst.reset_index()
            fcst['mean'] = fcst['mean'].ffill()
            fcst['Usage'] = share * fcst['mean']
            fcst['BF'] = fcst['Usage']

            vol = pd.DataFrame()
            vol['Type'] = ['Inflow', 'Sewage', 'Infiltration']
            vol['Volume'] = [fcst['y'].sum() - fcst['DWF'].sum(), fcst['DWF'].sum() - fcst['BF'].sum(),
                             fcst['BF'].sum()]
        elif infil_mode == 'night':

            fcst['BF'] = fcst['night']

            vol = pd.DataFrame()
            vol['Type'] = ['Inflow', 'Sewage', 'Infiltration']
            vol['Volume'] = [fcst['y'].sum() - fcst['DWF'].sum(), fcst['DWF'].sum() - fcst['BF'].sum(),
                             fcst['BF'].sum()]
        else:
            vol = pd.DataFrame()
            vol['Type'] = ['Inflow', 'Sewage']
            vol['Volume'] = [fcst['y'].sum() - fcst['DWF'].sum(), fcst['DWF'].sum()]

        fcst['ds'] = pd.to_datetime(fcst['ds'])
        fcst['month'] = fcst.ds.dt.month
        fcst_summer = fcst.loc[fcst['month'].isin([5, 6, 7, 8, 9, 10])]
        fcst_winter = fcst.loc[fcst['month'].isin([11, 12, 1, 2, 3, 4])]
        inflow_rainfall = fcst_summer['y'].sum() - fcst_summer['DWF'].sum()
        inflow_snowmelt = fcst_winter['y'].sum() - fcst_winter['DWF'].sum()

        return fcst, vol, inflow_rainfall, inflow_snowmelt

class EO:
    def __init__(self, api_key, municipality, dem=None, band_red_current=None, band_red_past=None, band_nir_current=None, band_nir_past=None, pipe_network_path=None):
        """
        Initialize the PipeNetwork class with a GeoDataFrame.
        :param geodataframe: GeoDataFrame containing pipe network data.
        """
        if pipe_network_path is not None:
            self.pipe_network = gpd.read_file(pipe_network_path).to_crs('epsg:4326')
        self.api_key = api_key
        self.municipality = municipality
        self.dem = dem
        self.band_red_current = band_red_current
        self.band_red_past = band_red_past
        self.band_nir_current = band_nir_current
        self.band_nir_past = band_nir_past
        self.aoi = ox.geocode_to_gdf(municipality)


    def impervious(self):
        import rasterio
        with rasterio.open(
                self.band_red_current) as src:
            red = src.read(1).astype('float32')  # assuming Band 3 = Red
            transform = src.transform
            crs = src.crs

        with rasterio.open(
                self.band_nir_current) as src:
            nir = src.read(1).astype('float32')  # assuming Band 3 = Red
            transform = src.transform
            crs = src.crs

        # NDVI = (NIR - Red) / (NIR + Red)
        ndvi = (nir - red) / (nir + red + 1e-5)  # small value to avoid div-by-zero
        ndvi[ndvi < 0] = np.nan

        # impervious_mask = (ndvi < 0.2).astype('uint8')
        with rasterio.open(
                self.band_red_past) as src:
            red = src.read(1).astype('float32')  # assuming Band 3 = Red
            transform = src.transform
            crs = src.crs

        with rasterio.open(
                self.band_nir_past) as src:
            nir = src.read(1).astype('float32')  # assuming Band 3 = Red
            transform = src.transform
            crs = src.crs

        ndvi_past = (nir - red) / (nir + red + 1e-5)  # small value to avoid div-by-zero
        ndvi_past[ndvi_past < 0] = np.nan

        from rasterio.features import shapes
        import geopandas as gpd
        from shapely.geometry import shape

        results = (
            {'geometry': shape(geom), 'ndvi': value}
            for geom, value in shapes(ndvi, transform=transform)
        )
        gdf = gpd.GeoDataFrame(results, geometry='geometry')
        gdf = gdf.loc[(gdf['ndvi'] < 0.1) & (gdf['ndvi'] > 0)]
        ndvi[ndvi >= 0.1] = np.nan
        ndvi[(ndvi > 0) & (ndvi < 0.1)] = 1

        ndvi_past[ndvi_past >= 0.1] = np.nan
        ndvi_past[(ndvi_past > 0) & (ndvi_past < 0.1)] = 1

        area_past = np.nansum(ndvi_past)
        area = np.nansum(ndvi)
        x = requests.post('https://www.waterworks.ai/api/impervious',
                          json={'results': gdf.to_json(), 'crs': crs.to_string(), 'area': str(area),
                                'area_past': str(area_past),
                                'api_key': self.api_key})
        js = x.json()
        # Build GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(json.loads(js['gdf'])['features'])
        gdf = gdf.set_crs('epsg:4326')
        percent_change = js['percent_change']

        return gdf, percent_change

    def depressions(self):
        from pysheds.grid import Grid
        import numpy as np
        import geopandas as gpd
        from rasterio.features import shapes
        from shapely.geometry import shape

        grid = Grid.from_raster(self.dem)
        dem = grid.read_raster(self.dem)
        # Condition DEM
        # ----------------------

        pits = grid.detect_pits(dem)

        # Fill pits
        pit_filled_dem = grid.fill_pits(dem)
        pits = grid.detect_pits(pit_filled_dem)
        assert not pits.any()

        # Detect depressions
        depressions = grid.detect_depressions(pit_filled_dem)

        # Assume `depressions` is a 2D NumPy array
        depressions_int = depressions.astype(np.int32)
        depressions_array = np.array(depressions_int)

        # Assume this is the transform from your grid
        results = (
            {'properties': {'val': v}, 'geometry': s}
            for s, v in shapes(depressions_array, transform=grid.affine)
            if v != 0
        )
        gdf = gpd.GeoDataFrame.from_features(results, crs='EPSG:4326')
        x = requests.post('https://www.waterworks.ai/api/depressions',
                          json={'results': gdf.to_json(), 'crs': dem.crs.to_string(), 'aoi': self.aoi.to_json(),
                                'api_key': self.api_key})
        js = x.json()
        # Build GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(json.loads(js['gdf'])['features'])
        gdf = gdf.set_crs('epsg:4326')
        return gdf

    def water(self):
        tags = {
            "natural": ["water"],
            "water": True,  # this can include features like rivers, lakes
            "waterway": ["riverbank", "canal", "dock", "reservoir"]
        }

        # Step 4: Download all matching geometries within the area boundary
        water_gdf = ox.geometries_from_polygon(self.aoi.geometry.iloc[0], tags)

        # This clips each geometry to the boundary polygon
        water_gdf = gpd.clip(water_gdf, self.aoi)

        water_gdf = water_gdf.reset_index()
        return water_gdf