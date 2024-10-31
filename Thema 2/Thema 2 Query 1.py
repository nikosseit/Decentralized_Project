# Databricks notebook source
#Importing everything required for spark sql

import pyspark
from pyspark.sql.functions import *

# COMMAND ----------

#Making the dataframes from the tables that were created from each file

df_agn = spark.read.option("header",True).csv("/FileStore/tables/agn_us.txt")
df_ainv = spark.read.option("header",True).csv("/FileStore/tables/ainv_us.txt")
df_ale = spark.read.option("header",True).csv("/FileStore/tables/ale_us.txt")

# COMMAND ----------

#Transform column date from String type to Date type

df_agn = df_agn.withColumn('Date',to_date('Date'))
df_ainv = df_ainv.withColumn('Date',to_date('Date'))
df_ale = df_ale.withColumn('Date',to_date('Date'))

# COMMAND ----------

#Transforming each column that has double type values from String type to Double type

columns = ['Open','High','Low','Close']
for x in columns:
    df_agn = df_agn.withColumn(x,col(x).cast('double'))
    df_ainv = df_ainv.withColumn(x,col(x).cast('double'))
    df_ale = df_ale.withColumn(x,col(x).cast('double'))

# COMMAND ----------

#Transform each column that has integer type values from String type to Int type

columns = ['Volume','OpenInt']
for x in columns:
    df_agn = df_agn.withColumn(x,col(x).cast('int'))
    df_ainv = df_ainv.withColumn(x,col(x).cast('int'))
    df_ale = df_ale.withColumn(x,col(x).cast('int'))

# COMMAND ----------

#Create a new column where the values are the months extracted from the Date column

df_agn = df_agn.withColumn("Month",month("Date"))
df_ainv = df_ainv.withColumn("Month",month("Date"))
df_ale = df_ale.withColumn("Month",month("Date"))

# COMMAND ----------

#Query that returns a dataframe where the average values of columns open, close and volume are calculated and ordered by its month

q_agn = df_agn.groupBy("Month").avg('Open','Close','Volume').orderBy('Month')
q_ainv = df_ainv.groupBy("Month").avg('Open','Close','Volume').orderBy('Month')
q_ale = df_ale.groupBy("Month").avg('Open','Close','Volume').orderBy('Month')

# COMMAND ----------

#Print the schema for each dataframe and show the results

print("Values for AGN:")
q_agn.printSchema()
q_agn.show()

print("Values for AINV:")
q_ainv.printSchema()
q_ainv.show()

print("Values for ALE:")
q_ale.printSchema()
q_ale.show()
