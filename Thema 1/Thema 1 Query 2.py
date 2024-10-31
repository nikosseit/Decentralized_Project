# Databricks notebook source
#Importing everything required for spark sql

import pyspark
from pyspark.sql.functions import *

# COMMAND ----------

#Making the dataframe from the table that was created from the file

df_temp = spark.read.option("header",True).csv("/FileStore/tables/tempm-5.csv")

# COMMAND ----------

#Transform column date from String type to Date type

df_temp = df_temp.withColumn('Date',to_date('Date'))

# COMMAND ----------

#Transform column value from String type to Double type

df_temp = df_temp.withColumn("Value",col("Value").cast('double'))

# COMMAND ----------

#Extract minimum and maximum values for each day and produce a dataframe that contains them

df_min = df_temp.groupBy("Date").min("Value")
df_min = df_min.withColumn("Minimum",col("min(Value)"))
df_max = df_temp.groupBy("Date").max("Value")
df_max = df_max.withColumn("Maximum",col("max(Value)"))
df = (df_min.join(df_max, "Date").orderBy("Date")).drop("min(Value)","max(Value)")

# COMMAND ----------

#Make two new dataframes one for the coldest days and one for the hottest
#The two new dfs are generated through the dataframe that contains the minimum and maximum for each date
#The coldest are ordered by minimum and the hottest are ordered by maximum in descending order 
#By limiting to 10 the df contain only the 10 coldest and 10 hottest dates

df_cold = df.orderBy("Minimum").drop("Maximum").limit(10)
df_hot = df.orderBy(desc("Maximum")).drop("Minimum").limit(10)

# COMMAND ----------

#Print the dataframes that contain the results

print("Dataframe that contains the 10 coldest dates: ")
df_cold.printSchema()
df_cold.show()

print("Dataframe that contains the 10 hottest dates: ")
df_hot.printSchema()
df_hot.show()

