# pyright: reportCallIssue=false, reportOperatorIssue=false, reportArgumentType=false, reportAttributeAccessIssue=false
# flake8: noqa: E501

from datetime import timedelta
from typing import List, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
import polars as pl


class CellTrajectory:
    def __init__(
        self,
        tdf: pl.DataFrame,
        v_id_col: str = "v_id",
        time_col: str = "datetime",
        uid_col: str = "uid",
    ) -> None:
        """
        Parameters
        ----------
        tdf : pandas.DataFrame
            Trajectory data with columns [uid, datetime, longitude, latitude]
            with regular observations for every users (interval τ,
            a balanced panel)
        v_id_col : str, optional
            The name of the column in the data containing the cell ID
            (default is "v_id")
        time_col : str, optional
            Time column name (default "time")
        uid_col : str, optional
            User ID column name (default "uid")
        """

        super().__init__()
        self.v_id = v_id_col
        self.time = time_col
        self.uid = uid_col

        if self.v_id not in tdf.columns:
            raise TypeError(
                """Cell trajectory dataframe does not contain
                cell IDs or cell IDs column does not match what was set."""
            )
        if self.time not in tdf.columns:
            raise TypeError(
                """Cell trajectory dataframe does not contain a time
                column or time column does not match what was set."""
            )
        if self.uid not in tdf.columns:
            raise TypeError(
                """Cell trajectory dataframe does not contain a uid
                column or uid column does not match what was set."""
            )

        self.tdf = tdf.sort(by=[uid_col, time_col])

    def get_tdf(self) -> pl.DataFrame:
        """getter"""
        return self.tdf

    def build_cell_flows(
        self, tau: int = 30, w: int = 60
    ) -> Tuple[pl.DataFrame, pl.DataFrame]:
        """build cell flows

        Parameters
        ----------
        tau : int
            Time resolution of data in minutes
            (default is 30 minutes)
        w : int
            Duration at a location used to define a trip in minutes
            (default is 60 minutes, must be a multiple of tau)

        Returns
        -------
        Tuple[polars.DataFrame, polars.DataFrame]
            First polars dataframe with the columns
            [origin, dest, time] are flows between cells.
            The second polars dataframe contains the number of stayers at each
            possible stay time period
        """

        if w % tau != 0:
            raise ValueError("w must be a multiple of tau.")

        tdf = self.tdf.sort(["uid", "datetime"])
        d = w // tau + 1

        def detect_stays(df: pl.DataFrame) -> pl.DataFrame:
            stays = df.select(
                [
                    pl.col(self.v_id),
                    pl.col(self.v_id)
                    .rolling_min(window_size=d)
                    .eq(pl.col(self.v_id).rolling_max(window_size=d))
                    .alias("is_stayer"),
                    pl.col(self.time),
                ]
            )

            return df.with_columns(stays["is_stayer"])

        tdf = (
            tdf.group_by(self.uid, maintain_order=True)
            .map_groups(detect_stays)
            .filter(pl.col("is_stayer"))
        )
        stayers = tdf.select([self.uid, self.v_id, self.time])

        movers = (
            stayers.with_columns(
                [
                    pl.col(self.v_id).shift(-1).over(self.uid).alias("next_v_id"),
                    pl.col(self.time).shift(-1).over(self.uid).alias("next_datetime"),
                ]
            )
            .filter(
                (pl.col(self.v_id) != pl.col("next_v_id"))
                | (
                    pl.col("next_datetime")
                    != pl.col(self.time) + pl.duration(minutes=tau)
                )
                & (pl.col("next_datetime").is_not_null())
            )
            .select(
                [
                    pl.col("uid"),
                    pl.col("v_id").alias("origin"),
                    pl.col("datetime").alias("start_time"),
                ]
            )
        )

        min_time = self.tdf[self.time].min()
        max_time = self.tdf[self.time].max()
        stay_start = min_time + (d - 1) * timedelta(minutes=tau)
        time_range = pl.datetime_range(
            start=stay_start, end=max_time, interval=f"{tau}m", eager=True
        ).sort()
        v_ids = self.tdf[self.v_id].unique().to_list()
        n_stayers = pl.DataFrame(
            {
                self.v_id: v_ids * len(time_range),
                self.time: np.repeat(time_range, len(v_ids)),
            }
        )
        n_stayers = (
            n_stayers.join(
                stayers.group_by([self.v_id, self.time]).agg(n_stayers=pl.len()),
                on=[self.v_id, self.time],
                how="left",
            )
            .with_columns(pl.col("n_stayers").fill_null(0))
            .sort([self.v_id, self.time])
        )

        stayers = stayers.rename({self.v_id: "dest", self.time: "stay_time"})

        candidates = movers.join(stayers, on=self.uid, how="inner")
        # h' > h
        candidates = candidates.filter(pl.col("stay_time") > pl.col("start_time"))

        # no intermediate stay between t_h and t_{h'}
        # (i.e., no stay_time between start_time and stay_time_stayer)
        first_arrival = candidates.group_by([self.uid, "origin", "start_time"]).agg(
            arrival_time=pl.col("stay_time").min()
        )

        first_arrival = first_arrival.join(
            stayers,
            left_on=[self.uid, "arrival_time"],
            right_on=[self.uid, "stay_time"],
            how="inner",
        )
        trips = first_arrival.select(
            [pl.col("origin"), pl.col("dest"), pl.col("start_time").alias("time")]
        )

        v_flows = (
            trips.group_by(["origin", "dest", "time"])
            .agg(count=pl.len())
            .sort(["origin", "dest", "time"])
        )

        return v_flows, n_stayers

    def build_zipcode_flows(
        self,
        cell_flows: pl.DataFrame,
        cell_stayers: pl.DataFrame,
        cell_zipcode_intersection_proportions: pl.DataFrame,
        postcodes: List[int],
        tau: int = 30,
        self_loops: bool = False,
    ) -> pl.DataFrame:
        """build zipcode flows

        Parameters
        ----------
        cell_flows : polars.DataFrame
            Cell Flows (e.g. flows between voronoi cells)
        cell_stayers : polars.DataFrame
            Number of stayers at each possible stay time period
        cell_zipcode_intersection_proportions : polars.DataFrame
            Proportion of intersection between cells and zipcodes
            with columns [pcode, v_id, p], where p is the proportion
            of intersection of the pcode and cell (v_id)
        postcodes : List[int]
            List of postcodes
        tau : int
            Time resolution of data in minutes
            (default is 30 minutes)
        self_loops : bool
            To remove or not to remove loops (default is False)

        Returns
        -------
        polars.DataFrame
            Polars dataframe with the columns
            [origin, dest, time, n_origin]
        """

        cell_stayers = (
            cell_stayers.join(
                cell_zipcode_intersection_proportions,
                on=self.v_id,
                suffix="_origin",
                how="left",
                coalesce=True,
            )
            .rename({"pcode": "origin"})
            .with_columns(np=((pl.col("n_stayers") * pl.col("p"))))
            .group_by([self.time, "origin"])
            .agg(count_avg=pl.sum("np"))
            .with_columns(n_origin=(((pl.col("count_avg")).floor()).cast(pl.Int64)))
            .select(["origin", self.time, "n_origin"])
            .sort(["origin", self.time])
        )

        flows = (
            (
                cell_flows.join(
                    cell_zipcode_intersection_proportions,
                    left_on="origin",
                    right_on="v_id",
                    suffix="_origin",
                    how="left",
                )
                .join(
                    cell_zipcode_intersection_proportions,
                    left_on="dest",
                    right_on="v_id",
                    suffix="_dest",
                    how="left",
                )
                .rename({"p": "p_origin", "pcode": "pcode_origin"})
                .with_columns(p=pl.col("p_origin") * pl.col("p_dest"))
                .with_columns(count_avg=pl.col("p") * pl.col("count"))
                .select(
                    origin=pl.col("pcode_origin"),
                    dest=pl.col("pcode_dest"),
                    time=pl.col("time"),
                    p=pl.col("p"),
                    count_avg=pl.col("count_avg"),
                )
            )
            .group_by(["origin", "dest", "time"])
            .agg(count_avg=pl.sum("count_avg"))
            .with_columns(count=pl.col("count_avg").floor().cast(pl.Int64))
            .select(["origin", "dest", "time", "count"])
        )

        flows_start = cell_flows["time"].min()
        flows_end = cell_flows["time"].max()

        time_range = pl.datetime_range(
            start=flows_start, end=flows_end, interval=f"{tau}m", eager=True
        ).sort()

        # structural zero flows
        df = pl.DataFrame(
            dict(
                origin=np.repeat(postcodes, len(postcodes) * len(time_range)),
                dest=postcodes * len(postcodes) * len(time_range),
                time=np.repeat(time_range.to_list(), len(postcodes)).tolist()
                * len(postcodes),
            ),
            schema={"origin": pl.Int64, "dest": pl.Int64, "time": pl.Datetime},
        )

        flows = df.join(flows, on=["origin", "dest", "time"], how="left", coalesce=True)
        flows = flows.with_columns(pl.col("count").fill_null(0))

        flows = flows.join(
            cell_stayers,
            left_on=["origin", "time"],
            right_on=["origin", self.time],
            how="left",
        ).sort(["origin", "dest", "time"])

        if not self_loops:
            flows = flows.filter(pl.col("origin") != pl.col("dest"))

        return flows


class Trajectory(pl.DataFrame):
    def __init__(
        self,
        tdf: pl.DataFrame,
        longitude: str = "lon",
        latitude: str = "lat",
        v_id_col: str = "v_id",
        time_col: str = "datetime",
        uid_col: str = "uid",
    ) -> None:
        """
        Parameters
        ----------
        tdf : pandas.DataFrame
            Trajectory data with columns [uid, datetime, longitude, latitude]
            with regular observations for every users (interval τ,
            a balanced panel)
        longitude : str, optional
            The name of the column in the data containing the longitude
            (default is "lon")
        latitude : str, optional
            The name of the column in the data containing the latitude
            (default is "lat")
        v_id_col : str, optional
            Column identifying tile IDs in the tessellation dataframe
            (default is "v_id")
        time_col : str, optional
            Time column name (default "time")
        uid_col : str, optional
            User ID column name (default "uid")
        """

        super().__init__()
        self.lon = longitude
        self.lat = latitude
        self.v_id = v_id_col
        self.time = time_col
        self.uid = uid_col

        if self.lon not in tdf.columns:
            raise TypeError(
                """Cell trajectory dataframe does not contain a longitude
                column or the longitude column does not match what was set."""
            )
        if self.lat not in tdf.columns:
            raise TypeError(
                """Cell trajectory dataframe does not contain a latitude
                column or the latitude column does not match what was set."""
            )

        if self.time not in tdf.columns:
            raise TypeError(
                """Cell trajectory dataframe does not contain a time
                column or time column does not match what was set."""
            )
        if self.uid not in tdf.columns:
            raise TypeError(
                """Cell trajectory dataframe does not contain a uid
                column or uid column does not match what was set."""
            )

        self.tdf = tdf.sort(by=[uid_col, time_col])

    def mapping(self, tessellation: gpd.GeoDataFrame) -> CellTrajectory:
        """Map (pseudo-)locations to coverage cells

        Parameters
        ----------
        tessellation : geopandas.GeoDataFrame
            Tessellation, e.g., Voronoi tessellation and any coverage
            tessellation with columns [v_id, longitude, latitude, geometry]

        Returns
        -------
        polars.DataFrame
            Polars dataframe with the columns
            [uid, datetime, longitude, latitude, v_id]
        """

        if self.v_id not in tessellation.columns:
            raise TypeError(
                """Cell trajectory dataframe does not contain
                cell IDs or cell IDs column does not match what was set."""
            )

        gdf = gpd.GeoDataFrame(
            self.tdf.to_pandas(),
            geometry=gpd.points_from_xy(self.tdf[self.lon], self.tdf[self.lat]),
            crs=tessellation.crs,
        )
        joined = gpd.sjoin(
            gdf, tessellation[[self.v_id, "geometry"]], how="left", predicate="within"
        )
        gdf[self.v_id] = joined[self.v_id]

        matched = gdf[~gdf[self.v_id].isna()]
        unmatched = gdf[gdf[self.v_id].isna()].copy()

        if not unmatched.empty:
            # build a lookup of future assigned regions per user
            tessellation = tessellation.copy()
            tessellation["rep"] = gpd.points_from_xy(
                tessellation[self.lon], tessellation[self.lat]
            )

            matched_sorted = matched.sort_values(by=[self.uid, self.time])
            future_region_lookup = matched_sorted.groupby(self.uid).apply(
                lambda df: df.set_index(self.time)[self.v_id], include_groups=False
            )

            # find candidate cells for all unmatched points (intersection test)
            unmatched["candidates"] = unmatched.geometry.apply(
                lambda geom: tessellation[tessellation.geometry.intersects(geom)][
                    [self.v_id, "rep"]
                ]
            )

            fallback_ids = []
            for _, row in unmatched.iterrows():
                uid = row[self.uid]
                time = row[self.time]

                # candidate cells at current time
                candidates = row["candidates"]
                if candidates.empty:
                    raise ValueError(
                        f"""tdf not proper: trajectory point for user {uid} at time
                            {time} intersects no tessellation cell."""
                    )

                # find user's next assigned cell
                if uid not in future_region_lookup:
                    raise ValueError(
                        f"""tdf not proper: uid {uid} does not have any point
                            assigned to a cell to a cell."""
                    )

                user_future = future_region_lookup[uid]
                future_times = user_future[user_future.index > time]

                if future_times.empty:
                    raise ValueError(
                        f"""tdf not proper: no future point for uid {uid} at time
                            {time}."""
                    )

                future_id = future_times.iloc[0]
                future_geom = tessellation.loc[
                    tessellation[self.v_id] == future_id, "rep"
                ].values[0]

                # choose closest candidate cell to the future one
                candidates["dist"] = candidates["rep"].distance(future_geom)
                fallback_id = candidates.sort_values(by="dist").iloc[0][self.v_id]
                fallback_ids.append(fallback_id)

            unmatched[self.v_id] = fallback_ids

            gdf = pd.concat(
                [matched, unmatched.drop(columns=["candidates"])], ignore_index=True
            )

        gdf.drop(columns=[self.lon, self.lat, "geometry"], inplace=True)

        return CellTrajectory(pl.DataFrame(gdf.sort_values(by=[self.uid, self.time])))
