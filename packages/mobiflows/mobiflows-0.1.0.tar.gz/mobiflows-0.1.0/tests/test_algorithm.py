# pyright: reportCallIssue=false
# flake8: noqa: E501

from datetime import datetime

import geopandas as gpd
import polars as pl
import pytest
import shapely as sp

from mobiflows.algorithm import CellTrajectory, Trajectory

TDF = pl.DataFrame(
    dict(
        uid=[
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
        ],
        datetime=[
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
        ],
        lon=[
            0,
            0,
            0,
            1,
            2,
            3,
            3,
            3,
            3,
            0,
            0,
            0,
            0,
            0,
            0,
            6,
            7,
            8,
            0,
            0,
            0,
            3,
            3,
            3,
            80,
            80,
            80,
            60,
            50,
            40,
            30,
            30,
            30,
            30,
            20,
            10,
            0,
            0,
            0,
            5,
            6,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],
        lat=[
            3,
            3,
            3,
            4,
            5,
            6,
            6,
            6,
            6,
            3,
            3,
            3,
            3,
            3,
            3,
            16,
            17,
            18,
            3,
            3,
            3,
            6,
            6,
            6,
            8,
            8,
            8,
            6,
            5,
            4,
            3,
            3,
            3,
            3,
            2,
            1,
            3,
            3,
            3,
            8,
            9,
            6,
            6,
            6,
            6,
            6,
            6,
            6,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
        ],
        v_id=[
            1000,
            1000,
            1000,
            1001,
            1002,
            1003,
            1003,
            1003,
            1003,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1600,
            1700,
            1800,
            1000,
            1000,
            1000,
            1003,
            1003,
            1003,
            8000,
            8000,
            8000,
            7500,
            7000,
            6500,
            6000,
            6000,
            6000,
            6000,
            5500,
            5000,
            1000,
            1000,
            1000,
            1005,
            1006,
            1003,
            1003,
            1003,
            1003,
            1003,
            1003,
            1003,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
        ],
    )
)


def test_mapping():
    points = sp.MultiPoint(
        [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
    )
    V = sp.voronoi_polygons(points)
    sorted_V = sorted(V.geoms, key=lambda p: (p.centroid.x, p.centroid.y))

    point_list = list(points.geoms)
    tessellation = gpd.GeoDataFrame(
        dict(
            v_id=[str(i) for i in range(len(sorted_V))],
            lon=[pt.x for pt in point_list],
            lat=[pt.y for pt in point_list],
            geometry=list(sorted_V),
        ),
        crs=4326,
    )

    tdf = Trajectory(
        pl.DataFrame(
            dict(
                uid=[
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    3,
                    3,
                    3,
                    3,
                    3,
                    3,
                    4,
                    4,
                    4,
                    4,
                    4,
                    4,
                    5,
                    5,
                    5,
                    5,
                    5,
                    5,
                ],
                datetime=[
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                ],
                lon=[
                    0.0,
                    0.0,
                    0.5,
                    1.5,
                    2.0,
                    2.0,
                    2.0,
                    1.5,
                    1.5,
                    0.5,
                    0.5,
                    0.0,
                    0.0,
                    0.5,
                    1.0,
                    1.5,
                    1.5,
                    2.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                ],
                lat=[
                    0.0,
                    0.0,
                    0.5,
                    1.5,
                    2.0,
                    2.0,
                    0.0,
                    0.5,
                    0.5,
                    1.5,
                    1.5,
                    2.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    2.0,
                    2.0,
                    0.0,
                    0.5,
                    0.0,
                    1.0,
                    1.5,
                    2.0,
                ],
            )
        )
    )

    true_mapped_tdf = pl.DataFrame(
        dict(
            uid=[
                1,
                1,
                1,
                1,
                1,
                1,
                2,
                2,
                2,
                2,
                2,
                2,
                3,
                3,
                3,
                3,
                3,
                3,
                4,
                4,
                4,
                4,
                4,
                4,
                5,
                5,
                5,
                5,
                5,
                5,
            ],
            datetime=[
                1,
                2,
                3,
                4,
                5,
                6,
                1,
                2,
                3,
                4,
                5,
                6,
                1,
                2,
                3,
                4,
                5,
                6,
                1,
                2,
                3,
                4,
                5,
                6,
                1,
                2,
                3,
                4,
                5,
                6,
            ],
            v_id=[
                "0",
                "0",
                "4",
                "8",
                "8",
                "8",
                "6",
                "4",
                "4",
                "2",
                "2",
                "2",
                "1",
                "4",
                "4",
                "7",
                "7",
                "7",
                "0",
                "0",
                "1",
                "1",
                "2",
                "2",
                "3",
                "3",
                "3",
                "4",
                "5",
                "5",
            ],
        )
    )

    mapped_tdf = tdf.mapping(tessellation).get_tdf()
    assert true_mapped_tdf.equals(mapped_tdf)


def test_build_cell_flows():
    true_voronoi_flows = pl.DataFrame(
        dict(
            origin=[1000, 1000, 8000, 1003, 1000],
            dest=[1003, 1000, 6000, 1000, 1003],
            time=[3, 3, 3, 9, 9],
            count=[2, 1, 1, 1, 1],
        )
    ).sort(by=["time", "origin", "dest"])

    true_n_stayers = pl.DataFrame(
        dict(
            v_id=[
                1000,
                1000,
                1000,
                1000,
                1000,
                1000,
                1000,
                1000,
                1000,
                1000,
                1003,
                1003,
                1003,
                1003,
                1003,
                6000,
                6000,
                8000,
            ],
            datetime=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 8, 9, 10, 11, 12, 9, 10, 3],
            n_stayers=[4, 1, 1, 1, 1, 1, 2, 1, 1, 2, 2, 2, 1, 1, 2, 1, 1, 1],
        )
    )

    base_time = datetime(2025, 1, 1, 0, 0, 0)
    us = 30 * 60_000_000
    tdf = TDF.with_columns(
        datetime=pl.lit(base_time)
        + pl.col("datetime") * pl.lit(us).cast(pl.Duration("us"))
    )
    trajectory = CellTrajectory(tdf)

    with pytest.raises(ValueError) as val_err:
        v_flows = (
            trajectory.build_cell_flows(tau=30, w=40)[0]
            .with_columns(
                time=((pl.col("time") - pl.lit(base_time)) / us).cast(pl.Int64)
            )
            .sort(by=["time", "origin", "dest"])
        )

    assert "w must be a multiple of tau." in str(val_err.value)

    v_flows, n_stayers = trajectory.build_cell_flows(tau=30, w=60)
    v_flows = v_flows.with_columns(
        time=((pl.col("time") - pl.lit(base_time)) / us).cast(pl.Int64)
    ).sort(by=["time", "origin", "dest"])
    assert true_voronoi_flows.equals(v_flows)

    n_stayers = (
        n_stayers.filter(pl.col("n_stayers") > 0)
        .with_columns(
            datetime=((pl.col("datetime") - pl.lit(base_time)) / us).cast(pl.Int64)
        )
        .sort(["v_id", "datetime"])
    )
    assert true_n_stayers.equals(n_stayers)


def test_build_zipcode_flows():
    true_flows = pl.DataFrame(
        dict(
            origin=[1, 1, 2, 1, 1, 2],
            dest=[1, 2, 3, 1, 2, 1],
            time=[3, 3, 3, 9, 9, 9],
            count=[2, 1, 1, 1, 0, 0],
            n_origin=[4, 4, 1, 3, 3, 1],
        )
    ).sort(by=["origin", "dest", "time"])
    voronoi_zipcode_intersection_proportions = pl.DataFrame(
        dict(
            pcode=[1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3],
            v_id=[
                1000,
                1001,
                1002,
                1003,
                5500,
                1001,
                1003,
                8000,
                1600,
                1700,
                5000,
                1005,
                1006,
                6000,
                1800,
                6500,
                7000,
                7500,
            ],
            p=[
                1.0,
                1.0,
                0.2,
                0.5,
                0.2,
                0.8,
                0.5,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
            ],
        )
    )

    base_time = datetime(2025, 1, 1, 0, 0, 0)
    us = 60_000_000
    tdf = TDF.with_columns(
        datetime=pl.lit(base_time)
        + pl.col("datetime") * pl.lit(us).cast(pl.Duration("us"))
    )
    trajectory = CellTrajectory(tdf)

    v_flows, v_stayers = trajectory.build_cell_flows(tau=1, w=2)
    flows = (
        trajectory.build_zipcode_flows(
            v_flows,
            v_stayers,
            voronoi_zipcode_intersection_proportions,
            postcodes=[1, 2, 3],
            tau=1,
            w=2,
            self_loops=True,
        )
        .with_columns(time=((pl.col("time") - pl.lit(base_time)) / us).cast(pl.Int64))
        .sort(["origin", "dest", "time", "count"])
    )

    assert true_flows.join(flows, on=true_flows.columns, how="anti").is_empty()

    flows = (
        trajectory.build_zipcode_flows(
            v_flows,
            v_stayers,
            voronoi_zipcode_intersection_proportions,
            postcodes=[1, 2, 3],
            tau=1,
            w=2,
            self_loops=False,
        )
        .with_columns(time=((pl.col("time") - pl.lit(base_time)) / us).cast(pl.Int64))
        .sort(["origin", "dest", "time", "count"])
    )

    assert (
        true_flows.filter(pl.col("origin") != pl.col("dest"))
        .join(
            flows,
            on=true_flows.columns,
            how="anti",
        )
        .is_empty()
    )


def test_cell_trajectory_constructor():
    with pytest.raises(TypeError) as type_err:
        CellTrajectory(TDF, v_id_col="vid")

    assert """Cell trajectory dataframe does not contain
                cell IDs or cell IDs column does not match what was set.""" in str(
        type_err.value
    )

    with pytest.raises(TypeError) as type_err:
        CellTrajectory(TDF, time_col="time")

    assert """Cell trajectory dataframe does not contain a time
                column or time column does not match what was set.""" in str(
        type_err.value
    )

    with pytest.raises(TypeError) as type_err:
        CellTrajectory(TDF, uid_col="bla")

    assert """Cell trajectory dataframe does not contain a uid
                column or uid column does not match what was set.""" in str(
        type_err.value
    )


def test_mapping_with_invalid_tessellation():
    points = sp.MultiPoint(
        [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
    )
    V = sp.voronoi_polygons(points)
    sorted_V = sorted(V.geoms, key=lambda p: (p.centroid.x, p.centroid.y))

    point_list = list(points.geoms)
    tessellation = gpd.GeoDataFrame(
        dict(
            v_id=[str(i) for i in range(len(sorted_V))],
            lon=[pt.x for pt in point_list],
            lat=[pt.y for pt in point_list],
            geometry=list(sorted_V),
        ),
        crs=4326,
    )
    with pytest.raises(TypeError) as type_err:
        traj = Trajectory(TDF, v_id_col="vid")
        traj.mapping(tessellation)

    assert """Cell trajectory dataframe does not contain
                cell IDs or cell IDs column does not match what was set.""" in str(
        type_err.value
    )


def test_trajectory_constructor():
    with pytest.raises(TypeError) as type_err:
        Trajectory(TDF, longitude="lan")

    assert """Cell trajectory dataframe does not contain a longitude
                column or the longitude column does not match what was set.""" in str(
        type_err.value
    )

    with pytest.raises(TypeError) as type_err:
        Trajectory(TDF, latitude="lan")

    assert """Cell trajectory dataframe does not contain a latitude
                column or the latitude column does not match what was set.""" in str(
        type_err.value
    )

    with pytest.raises(TypeError) as type_err:
        Trajectory(TDF, time_col="time")

    assert """Cell trajectory dataframe does not contain a time
                column or time column does not match what was set.""" in str(
        type_err.value
    )

    with pytest.raises(TypeError) as type_err:
        Trajectory(TDF, uid_col="bla")

    assert """Cell trajectory dataframe does not contain a uid
                column or uid column does not match what was set.""" in str(
        type_err.value
    )
