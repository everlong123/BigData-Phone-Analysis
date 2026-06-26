from pyspark.sql import SparkSession
from pyspark.sql.functions import countDistinct
import matplotlib.pyplot as plt
import os

spark = SparkSession.builder \
    .appName("Task1_Product_Diversity") \
    .enableHiveSupport() \
    .getOrCreate()

df = spark.sql("""
SELECT *
FROM phone_db.phones
""")
result = (
    df.groupBy("brand")
      .agg(
          countDistinct("product_name")
          .alias("total_products")
      )
      .orderBy("total_products", ascending=False)
)
print("===== PRODUCT DIVERSITY =====")
result.show(100, False)
result.write.mode("overwrite") \
      .saveAsTable("phone_db.task1_product_diversity")
pdf = result.toPandas()
plt.figure(figsize=(10,5))
plt.bar(pdf["brand"], pdf["total_products"])
plt.title("Product Diversity by Brand")
plt.xlabel("Brand")
plt.ylabel("Number of Products")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("/home/hadoophai/task1_product_diversity.png")
spark.stop()
