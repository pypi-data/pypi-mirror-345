"""Utility functions for SCD type 1 and type 2."""
import os
import uuid
from datetime import datetime
from typing import List

import pyspark.sql.functions as F
from delta import DeltaTable
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import SparkSession
from pyspark.sql.column import Column
from pyspark.sql.types import StringType
from pyspark.sql.window import Window
from kedro_sumz.utils import get_catalog

TIME_ZONE = "America/Bogota"


def get_current_timestamp(time_zone: str = TIME_ZONE) -> Column:
    """Get current timestamp"""
    return F.from_utc_timestamp(F.current_timestamp(), time_zone)


@F.udf(returnType=StringType())
def create_uuid():
    """Create uuid udf"""
    return str(uuid.uuid4())


@F.udf(returnType=StringType())
def create_static_uuid(value: str):
    """Create uuid udf"""
    return str(uuid.uuid5(uuid.NAMESPACE_OID, value))


def incremental_audit_cols(
    source: SparkDataFrame,
):
    """Add audit columns for incremental loads
    Args:
        source: dataframe to add columns
    Returns:
        a spark dataframe with the required columns
    """
    source = source.select(
        F.col("*"),
        get_current_timestamp().alias("FECHA_CREACION_LAGO_DATOS"),
        get_current_timestamp().alias("FECHA_MODIFICACION_LAGO_DATOS"),
    )
    return source


def partial_incremental_overwrites(
    source: SparkDataFrame,
    target: DeltaTable,
    condition: str,
    target_catalog: str,
    add_new_cols: bool = False,
):
    """Perform a partial incremental overwrite of a DeltaTable
    Args:
        source: dataframe to overwrite
        target: DeltaTable to overwrite
        condition: condition to use for the overwrite
        target_catalog: catalog name of the target table
        add_new_cols: if True, add new columns to the target table
    """
    catalog = get_catalog()
    # pylint: disable=protected-access
    target_catalog = catalog._get_dataset(target_catalog)
    # pylint: disable=protected-access
    target_catalog._save_args["replaceWhere"] = condition
    source = incremental_audit_cols(source.where(F.expr(condition)))
    if not add_new_cols:
        source_cols = [c.upper() for c in source.columns]
        target_cols = [c.upper() for c in target.toDF().columns]
        columns = [c for c in source_cols if c in target_cols]
        source = source.select(columns)
    else:
        # pylint: disable=protected-access
        target_catalog._save_args["mergeSchema"] = "true"
    target_catalog.save(source)


def scd1_audit_cols(
    source: SparkDataFrame,
    key_cols: List[str],
    filter_cols: List = None,
):
    """Add required columns for SCD type 1 first load
    Args:
        source: dataframe to add columns
        key_cols: columns to use as key
        filter_cols: cols to ignore when building the ETLSHA
    Returns:
        a spark dataframe with the required columns
    """
    key_cols = [c.upper() for c in key_cols]
    filter_cols = [c.upper() for c in filter_cols] if filter_cols else []

    source_cols = [
        c.upper()
        for c in source.columns
        if (c.upper() not in key_cols) and (c.upper() not in filter_cols)
    ]
    source = incremental_audit_cols(source)
    source = source.select(
        F.col("*"),
        F.sha2(
            F.concat(
                *[F.coalesce(F.col(c).cast("String"), F.lit("")) for c in source_cols]
            ),
            256,
        ).alias("ETLSHA"),
    )
    return source


def scd2_audit_cols(
    source: SparkDataFrame,
    key_cols: List[str],
    s_key_name: str = "CLAVE_SUB",
    date_col: str = None,
    start_col: str = None,
    gen_uuid: bool = True,
    filter_cols: List = None,
):
    """Add required columns for SCD type 2 first load
    Args:
        source: dataframe to add columns
        key_cols: columns to use as key
        s_key_name: name of the surrogate key column
        date_col: column to use as date
        start_col: column to use as start date when date_col is None
        gen_uuid: if True, generate an uuid column
        filter_cols: cols to ignore when building the ETLSHA
    Returns:
        a spark dataframe with the required columns
    """
    key_cols = [c.upper() for c in key_cols]
    filter_cols = [c.upper() for c in filter_cols] if filter_cols else []
    start_col = start_col if start_col is not None else F.lit("1900-01-01")
    start_col = F.expr(start_col) if isinstance(start_col, str) else start_col

    source_cols = [
        c.upper()
        for c in source.columns
        if (c.upper() not in key_cols) and (c.upper() not in filter_cols)
    ]
    if gen_uuid:
        source = source.select(F.expr("uuid()").alias(s_key_name), F.col("*"))
    source = source.alias("src").select(
        F.col("*"),
        F.coalesce(
            F.col(f"src.{date_col}")
            if date_col and date_col in source.columns
            else F.lit(None),
            start_col,
        )
        .cast("timestamp")
        .alias("FECHA_INICIO_VIGENCIA"),
        F.lit("9999-12-31").cast("timestamp").alias("FECHA_FIN_VIGENCIA"),
        F.lit(True).alias("REGISTRO_ACTIVO"),
        get_current_timestamp().alias("FECHA_CREACION_LAGO_DATOS"),
        get_current_timestamp().alias("FECHA_MODIFICACION_LAGO_DATOS"),
        F.sha2(
            F.concat(
                *[F.coalesce(F.col(c).cast("String"), F.lit("")) for c in source_cols]
            ),
            256,
        ).alias("ETLSHA"),
    )
    return source


def scd1_delta_write(
    source: SparkDataFrame,
    target: DeltaTable,
    key_cols: List[str],
    filter_cols: List[str] = None,
    skip_update_cols: List[str] = None,
    add_new_cols: bool = False,
    partition_filter: str = None,
    delete_not_in_source=True,
):
    """Write a dataframe to a delta table using SCD type 1
    Args:
        source: dataframe to write
        target: delta table to write to
        key_cols: columns to use as key
        filter_cols: cols to ignore when building the ETLSHA
        skip_update_cols: cols to ignore when updating
        add_new_cols: if True, add new columns to the target table
        partition_filter: partition filter to use
        delete_not_in_source: if True, delete rows not in the source table
    """
    if skip_update_cols:
        add_new_cols = False
    else:
        skip_update_cols = []

    key_cols = [c.upper() for c in key_cols]
    filter_cols = [c.upper() for c in filter_cols] if filter_cols else []
    skip_update_cols = [c.upper() for c in skip_update_cols]

    source_cols = [
        c.upper()
        for c in source.columns
        if (c.upper() not in key_cols) and (c.upper() not in filter_cols)
    ]

    source = scd1_audit_cols(source, key_cols, filter_cols)  # .persist()

    merge_builder = target.alias("tg").merge(
        source.alias("src"),
        (f"({partition_filter}) AND " if partition_filter else "")
        + " AND ".join([f"src.{c}<=>tg.{c}" for c in key_cols]),
    )
    if add_new_cols:
        merge_builder = merge_builder.whenMatchedUpdateAll(
            condition="src.ETLSHA <> tg.ETLSHA"
        ).whenNotMatchedInsertAll()
    else:
        merge_builder = merge_builder.whenMatchedUpdate(
            condition="src.ETLSHA <> tg.ETLSHA",
            set=dict(
                **{
                    c: f"src.{c}"
                    for c in [t.upper() for t in target.toDF().columns]
                    if (c in source_cols or c in filter_cols)
                    and (c not in skip_update_cols)
                },
                **{
                    "FECHA_MODIFICACION_LAGO_DATOS": "src.FECHA_MODIFICACION_LAGO_DATOS",
                    "ETLSHA": "src.ETLSHA",
                },
            ),
        ).whenNotMatchedInsert(
            values={
                c: f"src.{c}"
                for c in [t.upper() for t in target.toDF().columns]
                if c in [s.upper() for s in source.columns] or c in filter_cols
            }
        )
    if delete_not_in_source:
        merge_builder = merge_builder.whenNotMatchedBySourceDelete(
            condition=partition_filter
        )

    merge_builder.execute()


def scd2_delta_write(
    source: SparkDataFrame,
    target: DeltaTable,
    key_cols: List[str],
    s_key_name: str = "CLAVE_SUB",
    date_col: str = None,
    start_col: str = None,
    use_date_col_for_updates: bool = False,
    gen_uuid: bool = True,
    filter_cols: List = None,
    partition_cols: List = None,
    add_new_cols: bool = False,
    delete_not_in_source=False,
    restore_deleted: bool = False,
    partition_filter: str = None,
):
    """Delta SCD type 2 write
    Args:
        source: source dataframe to write
        target: target delta table to write into
        key_cols: columns to use as key
        s_key_name: name of the surrogate key column
        date_col: name of the date column for the merge
        start_col: column to use as start date when date_col is None
            for new records
        use_date_col_for_updates: if True, use date column for updates
        gen_uuid: decide if generate new uuid when inserting
        filter_cols: cols to ignore when building the ETLSHA
        partition_cols: cols to use as partition
        add_new_cols: if True, add new columns to target
        delete_not_in_source: if True, delete records not in source
        restore_deleted: if True, restore deleted records when they appear in source
        partition_filter: partition filter to use
    """
    spark = SparkSession.getActiveSession()

    key_cols = [c.upper() for c in key_cols]
    filter_cols = [c.upper() for c in filter_cols] if filter_cols else []
    partition_cols = [c.upper() for c in partition_cols] if partition_cols else []
    start_col = start_col if start_col is not None else get_current_timestamp()
    start_col = F.expr(start_col) if isinstance(start_col, str) else start_col

    source_cols = [
        c.upper()
        for c in source.columns
        if (c.upper() not in key_cols) and (c.upper() not in filter_cols)
    ]
    audit_cols = [
        "FECHA_INICIO_VIGENCIA",
        "FECHA_FIN_VIGENCIA",
        "REGISTRO_ACTIVO",
        "FECHA_CREACION_LAGO_DATOS",
        "FECHA_MODIFICACION_LAGO_DATOS",
        "ETLSHA",
    ]
    if gen_uuid:
        source = source.select(F.expr("uuid()").alias(s_key_name), F.col("*"))
        partitions = {}
        keys = {}
        type_map = {
            "string": "NA",
            "date": datetime.strptime("1900-01-01", "%Y-%m-%d").date(),
            "timestamp": datetime.strptime("1900-01-01", "%Y-%m-%d"),
        }
        for col in partition_cols:
            # string, date, timestamp
            type_ = source.select(col).schema[0].jsonValue()["type"]
            partitions[col] = type_map.get(type_, -1)

        for col in key_cols:
            # string, date, timestamp
            type_ = source.select(col).schema[0].jsonValue()["type"]
            keys[col] = type_map.get(type_, -1)

        data = [dict(**{s_key_name: str(uuid.uuid4())}, **keys, **partitions)]
        empty_source = spark.createDataFrame(
            data=data,
            schema=target.toDF()
            .select(*[c.upper() for c in target.toDF().columns if c.upper() not in audit_cols])
            .schema,
        )
        source = source.unionByName(empty_source, allowMissingColumns=True)
    source = source.select(
        F.col("*"),
        F.lit("9999-12-31").cast("timestamp").alias("FECHA_FIN_VIGENCIA"),
        F.lit(True).alias("REGISTRO_ACTIVO"),
        get_current_timestamp().alias("FECHA_CREACION_LAGO_DATOS"),
        get_current_timestamp().alias("FECHA_MODIFICACION_LAGO_DATOS"),
        F.sha2(
            F.concat(
                *[F.coalesce(F.col(c).cast("String"), F.lit("")) for c in source_cols]
            ),
            256,
        ).alias("ETLSHA"),
    )  # .persist()

    source_cols = [
        c.upper() for c in source.columns if c.upper() not in audit_cols
    ] + audit_cols

    updates = (
        source.alias("src")
        .join(
            target.toDF().alias("tg"),
            on=F.expr(
                (f"({partition_filter}) AND " if partition_filter else "")
                + " AND ".join([f"src.{c}<=>tg.{c}" for c in key_cols])
            ),
        )
        .where("tg.REGISTRO_ACTIVO = TRUE AND src.ETLSHA <> tg.ETLSHA")
    )

    if restore_deleted:
        restores = (
            source.alias("src")
            .join(
                target.toDF().withColumn(
                    "rn",
                    F.row_number().over(
                        Window.partitionBy(key_cols).orderBy(F.desc("FECHA_FIN_VIGENCIA"))
                    ),
                ).where(
                    (F.col("rn") == 1) & (~F.col("REGISTRO_ACTIVO"))
                ).drop("rn").alias("tg"),
                on=F.expr(
                    (f"({partition_filter}) AND " if partition_filter else "")
                    + " AND ".join([f"src.{c}<=>tg.{c}" for c in key_cols])
                )
            ).where(
                "tg.REGISTRO_ACTIVO = FALSE"
            )
        )
        updates = updates.unionByName(restores)

    staging = updates.select(
        F.lit(0).alias("__key__"),
        F.col("src.*"),
        F.coalesce(
            (
                F.col(f"src.{date_col}")
                if use_date_col_for_updates
                and date_col
                and date_col.upper() in [s.upper() for s in source.columns]
                else F.lit(None)
            ),
            get_current_timestamp(),
        )
        .cast("timestamp")
        .alias("FECHA_INICIO_VIGENCIA"),
    ).unionByName(
        source.alias("src").select(
            F.lit(1).alias("__key__"),
            F.col("src.*"),
            F.coalesce(
                (
                    F.col(f"src.{date_col}")
                    if date_col
                    and date_col.upper() in [s.upper() for s in source.columns]
                    else F.lit(None)
                ),
                start_col,
            )
            .cast("timestamp")
            .alias("FECHA_INICIO_VIGENCIA"),
        )
    )
    if "DATABRICKS_RUNTIME_VERSION" not in os.environ:
        staging = staging.localCheckpoint(eager=False)

    merge_builder = (
        target.alias("tg")
        .merge(
            staging.alias("st"),
            (f"({partition_filter}) AND " if partition_filter else "")
            + "st.__key__=1 AND "
            + " AND ".join([f"st.{c}<=>tg.{c}" for c in key_cols]),
        )
        .whenMatchedUpdate(
            condition="tg.REGISTRO_ACTIVO = TRUE AND st.ETLSHA <> tg.ETLSHA",
            set={
                "REGISTRO_ACTIVO": "false",
                "FECHA_FIN_VIGENCIA": (
                    "st.FECHA_INICIO_VIGENCIA"
                    if use_date_col_for_updates and date_col
                    else get_current_timestamp()
                ),
                "FECHA_MODIFICACION_LAGO_DATOS": "st.FECHA_MODIFICACION_LAGO_DATOS",
            },
        )
    )
    if add_new_cols:
        merge_builder = merge_builder.whenNotMatchedInsert(
            values={c: f"st.{c}" for c in source_cols}
        )
    else:
        merge_builder = merge_builder.whenNotMatchedInsert(
            values={c: f"st.{c.upper()}" for c in target.toDF().columns}
        )
    if delete_not_in_source:
        merge_builder = merge_builder.whenNotMatchedBySourceUpdate(
            condition=(f"({partition_filter}) AND " if partition_filter else "")
            + "tg.REGISTRO_ACTIVO = TRUE",
            set={
                "REGISTRO_ACTIVO": "false",
                "FECHA_FIN_VIGENCIA": get_current_timestamp(),
                "FECHA_MODIFICACION_LAGO_DATOS": get_current_timestamp(),
            },
        )

    merge_builder.execute()
