import re
import sys
from pyspark.sql import SparkSession, functions, types


spark = SparkSession.builder.appName('wikipedia popular').getOrCreate()
spark.sparkContext.setLogLevel('WARN')


assert sys.version_info >= (3, 8)
assert spark.version >= '3.2' 


schema = types.StructType([
    types.StructField('language', types.StringType()),
    types.StructField('title', types.StringType()),
    types.StructField('views', types.LongType()),
    types.StructField('bytes', types.LongType()),
])
 

def path_to_hour(path):
    
    filename = path.split('/')[-1]
    parts = filename.split('-')  
    date = parts[1]
    hour = parts[2][:2]
    return date + '-' + hour


path_to_hour_udf = functions.udf(path_to_hour, returnType=types.StringType())


def main(in_directory, out_directory):
   
    pagecounts = (
        spark.read.csv(
            in_directory,
            schema=schema,
            sep=' ',
        )
        .withColumn('filename', functions.input_file_name())
        .withColumn('hour', path_to_hour_udf(functions.col('filename')))
    )

    pages = (
        pagecounts
        .filter(functions.col('language') == 'en')
        .filter(functions.col('title') != 'Main_Page')
        .filter(~functions.col('title').startswith('Special:'))
        .select('hour', 'title', 'views')
        .cache()
    )

    max_views = (
        pages
        .groupBy('hour')
        .agg(functions.max('views').alias('views'))
    )


    most_popular = (
        pages
        .join(max_views, on=['hour', 'views'], how='inner')
        .select('hour' , 'title', 'views')
        .orderBy('hour' , 'title')
    )

    most_popular.write.csv(out_directory, mode='overwrite')

if __name__ =='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)