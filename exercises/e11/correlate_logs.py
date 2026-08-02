import sys
assert sys.version_info >= (3, 8) # make sure we have Python 3.8+
from pyspark.sql import SparkSession, functions, types, Row
import re


line_re = re.compile(r"^(\S+) - - \[\S+ [+-]\d+\] \"[A-Z]+ \S+ HTTP/\d\.\d\" \d+ (\d+)$")


def line_to_row(line):
    """
    Take a logfile line and return a Row object with hostname and bytes transferred.
    Return None if regex doesn't match.
    """
    m = line_re.match(line)
    if m:
        # TODO
        return Row(hostname=m.group(1) , bytes=int(m.group(2)))
    else:
        return None


def not_none(row):
    """
    Is this None? Hint: .filter() with it.
    """
    return row is not None


def create_row_rdd(in_directory):
    log_lines = spark.sparkContext.textFile(in_directory)
    # TODO: return an RDD of Row() objects
    return log_lines.map(line_to_row).filter(not_none)


def main(in_directory):
    logs = spark.createDataFrame(create_row_rdd(in_directory))

    # TODO: calculate r.

    totals = logs.groupBy('hostname').agg(
        functions.count('*').alias('count'),
        functions.sum('bytes').alias('bytes'),)


    cnt = totals['count'].cast('double')
    byt = totals['bytes'].cast('double')

    values = totals.select(
        functions.lit(1).alias('n'),
        cnt.alias('x'), (cnt * cnt).alias('x2'),
        byt.alias('y'), (byt * byt).alias('y2'),
        (cnt * byt).alias('xy'),
    )

    sums = values.groupBy().agg(
        functions.sum('n').alias('n'), functions.sum('x').alias('x'),
        functions.sum('x2').alias('x2'), functions.sum('y').alias('y'),
        functions.sum('y2').alias('y2'), functions.sum('xy').alias('xy'),
    )

    n, x, x2, y, y2, xy = sums.first()

    r = (n*xy - x*y) / ((n*x2 - x**2)**0.5 * (n*y2 - y**2)**0.5) # TODO: it isn't zero.
    print(f"r = {r}\nr^2 = {r*r}")
    # Built-in function should get the same results.
    #print(totals.corr('count', 'bytes'))


if __name__=='__main__':
    in_directory = sys.argv[1]
    spark = SparkSession.builder.appName('correlate logs').getOrCreate()
    assert spark.version >= '3.2' # make sure we have Spark 3.2+
    spark.sparkContext.setLogLevel('WARN')

    main(in_directory)
