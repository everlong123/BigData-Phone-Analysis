from pyspark.sql import SparkSession
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, count, sum, round
import matplotlib.pyplot as plt

spark = SparkSession.builder \
    .appName("Task3_Discount_Analysis") \
    .enableHiveSupport() \
    .getOrCreate()

df = spark.sql("""
SELECT *
FROM phone_db.phones
""")

result = (
    df.groupBy("brand")
      .agg(
          count("*").alias("total_products"),
          sum(
              when(
                  df.original_price > df.sale_price,
                  1
              ).otherwise(0)
          ).alias("discount_products")
      )
)

result = result.withColumn(
    "discount_rate",
    round(
        result.discount_products
        *100
        / result.total_products,
        2
    )
)

result.show(100, False)

result.write.mode("overwrite") \
      .saveAsTable("phone_db.task3_discount_analysis")

pdf = result.toPandas()

plt.figure(figsize=(10,5))
plt.bar(
    pdf["brand"],
    pdf["discount_rate"]
)

plt.title("Discount Rate by Brand")
plt.xlabel("Brand")
plt.ylabel("Discount Rate (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("/home/hadoophai/task3_discount_analysis.png")

spark.stop()
