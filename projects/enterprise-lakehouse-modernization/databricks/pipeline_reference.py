"""Databricks Auto Loader and PySpark Silver processing examples.

Requires a configured Databricks workspace, Delta tables, and access controls.
This reference is syntax-checked but does not run in the offline test suite.
"""
from pyspark.sql import Window
from pyspark.sql import functions as F


def ingest_bronze(spark, input_path, schema_path, checkpoint_path, table):
    """Ingest JSON files incrementally into a Bronze Delta table."""
    source = (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", schema_path)
        .load(input_path)
    )
    return (
        source.writeStream.format("delta")
        .option("checkpointLocation", checkpoint_path)
        .trigger(availableNow=True)
        .toTable(table)
    )


def prepare_silver(bronze):
    """Filter and deduplicate one batch; persistent merges require Delta MERGE."""
    clean = (
        bronze
        .withColumn("order_id", F.trim("order_id"))
        .withColumn("customer_id", F.trim("customer_id"))
        .withColumn("amount", F.col("amount").cast("decimal(18, 2)"))
        .withColumn("event_time", F.to_timestamp("event_time"))
        .withColumn("ingested_at", F.to_timestamp("ingested_at"))
        .filter(F.col("order_id").isNotNull() & (F.length("order_id") > 0))
        .filter(F.col("customer_id").isNotNull() & (F.length("customer_id") > 0))
        .filter(F.col("amount").isNotNull() & (F.col("amount") >= 0))
        .filter(F.col("event_time").isNotNull() & F.col("ingested_at").isNotNull())
    )
    window = Window.partitionBy("order_id").orderBy(F.col("ingested_at").desc())
    return (
        clean.withColumn("rn", F.row_number().over(window))
        .filter(F.col("rn") == 1)
        .drop("rn")
    )
