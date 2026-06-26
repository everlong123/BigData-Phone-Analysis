from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, round, format_number
import matplotlib.pyplot as plt

spark = SparkSession.builder \
    .appName("Task2_RAM_ROM_Price") \
    .enableHiveSupport() \
    .getOrCreate()
df = spark.sql("""
SELECT *
FROM phone_db.phones
""")

result = (
    df.groupBy("ram", "storage")
      .agg(
          round(avg("sale_price"), 0).alias("avg_price")
      )
      .orderBy("avg_price", ascending=False)
)
print("===== RAM-ROM VS AVERAGE PRICE (VND) =====")
result.withColumn(
    "avg_price_vnd",
    format_number("avg_price", 0)
).show(100, False)
result.write.mode("overwrite") \
      .saveAsTable("phone_db.task2_ram_rom_price")

# Chuyển sang Pandas để vẽ
pdf = result.toPandas()
plt.figure(figsize=(12,6))
labels = pdf["ram"] + "-" + pdf["storage"]
plt.scatter(labels, pdf["avg_price"])
plt.title("RAM-ROM vs Average Price (VND)")
plt.xlabel("RAM-ROM")
plt.ylabel("Average Price (VND)")
plt.xticks(rotation=90)

plt.tight_layout()
plt.savefig("/home/hadoophai/task2_ram_rom_price.png")
spark.stop()
