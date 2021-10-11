## --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6,io.delta:delta-core_2.11:0.6.1 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"


df = spark \
      .readStream \
      .format("kafka") \
      .option("kafka.bootstrap.servers", "localhost:9092") \
      .option("subscribe", "postgres.nimble.image") \
     .load()

ds = df \
    .selectExpr('CAST(value AS STRING)') \
    .writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/delta") \
    .start('/tmp/delta/events')


# console
ds = df \
    .selectExpr('CAST(value AS STRING)') \
    .writeStream \
    .outputMode("append") \
    .format('console')\
    .start()
