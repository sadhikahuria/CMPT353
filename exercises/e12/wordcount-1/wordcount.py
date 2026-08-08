import sys
import string
import re

from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName('wordcount').getOrCreate()

input_dir = sys.argv[1]
output_dir = sys.argv[2]

wordbreak = r'[\s%s]+' % (re.escape(string.punctuation), )

lines = spark.read.text(input_dir)

words = lines.select(
    F.explode(
        F.split(F.lower(F.col('value')), wordbreak)
    ).alias('word')
)

counts = (
    words
    .filter(F.col('word') != '')
    .groupBy('word')
    .count()
    .orderBy(F.desc('count'), F.asc('word'))
)

counts.write.mode('overwrite').option('compression', 'none').csv(output_dir)

spark.stop()