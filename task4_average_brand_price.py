from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, round
import matplotlib.pyplot as plt
 
spark = SparkSession.builder \
    .appName("Task4_Average_Brand_Price") \
    .enableHiveSupport() \
    .getOrCreate()
 
df = spark.sql("""
SELECT *
FROM phone_db.phones
""")
 
result = (
    df.groupBy("brand")
      .agg(
          round(avg("sale_price"), 0)
          .alias("avg_price")
      )
      .orderBy("avg_price", ascending=False)
)
 
print("===== AVERAGE BRAND PRICE (VND) =====")
result.show(100, False)
 
result.write.mode("overwrite") \
      .saveAsTable("phone_db.task4_average_brand_price")
 
pdf = result.toPandas()
 
# Đổi sang triệu VNĐ
pdf["avg_price_million"] = pdf["avg_price"] / 1000000
 
plt.figure(figsize=(12,6))
 
plt.barh(
    pdf["brand"],
    pdf["avg_price_million"]
) 
plt.title("Average Brand Price Ranking")
plt.xlabel("Average Price (Million VND)")
plt.ylabel("Brand") 
plt.tight_layout()
plt.savefig("task4_average_brand_price.png") 
spark.stop()
