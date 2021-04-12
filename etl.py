# import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format
from pyspark.sql.types import TimestampType

# config = configparser.ConfigParser()
# config.read('dl.cfg')
#
# os.environ['AWS_ACCESS_KEY_ID'] = config['AWS_ACCESS_KEY_ID']
# os.environ['AWS_SECRET_ACCESS_KEY'] = config['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    # get filepath to song data file
    song_data = input_data + 'song_data/*/*/*/*.json'
    
    # read song data file
    df = spark.read.schema('''
    song_id             STRING,
    num_songs           INT,
    artist_id           STRING,
    artist_latitude     DOUBLE,
    artist_longitude    DOUBLE,
    artist_location     STRING,
    artist_name         STRING,
    title               STRING,
    duration            DOUBLE,
    year                INT
    ''').json(song_data)

    # extract columns to create songs table
    songs_table = df.select('song_id', 'title', 'artist_id', 'year', 'duration').distinct()
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.mode('overwrite').partitionBy('year', 'artist_id').parquet(output_data + 'dimensions.parquet/songs')

    # extract columns to create artists table
    artists_table = df.selectExpr('artist_id',
                                  'artist_name as name',
                                  'artist_location as location',
                                  'artist_latitude as latitude',
                                  'artist_longitude as longitude').distinct()
    
    # write artists table to parquet files
    artists_table.write.mode('overwrite').parquet(output_data + 'dimensions.parquet/artists')


def process_log_data(spark, input_data, output_data):
    # get filepath to log data file
    log_data = input_data + 'log_data/*/*/*-events.json'

    # read log data file
    df = spark.read.schema('''
    artist              STRING,
    auth                STRING,
    first_name          STRING,
    gender              STRING,
    item_in_session     INT,
    last_name           STRING,
    length              DOUBLE,
    level               STRING,
    location            STRING,
    method              STRING,
    page                STRING,
    registration        DOUBLE,
    session_id          LONG,
    song                STRING,
    status              INT,
    ts                  LONG,
    user_agent          STRING,
    user_id             LONG
    ''').json(log_data)
    
    # filter by actions for song plays
    df = df.filter("page = 'NextSong' AND status = 200")

    # extract columns for users table    
    users_table = df.select('user_id', 'first_name', 'last_name', 'gender', 'level').distinct()
    
    # write users table to parquet files
    users_table.write.mode('overwrite').parquet(output_data + 'dimensions.parquet/users')

    # create timestamp column from original timestamp column
    df = df.withColumn('event_ts', (col('ts') / 1000).cast('timestamp'))

    # extract columns to create time table
    time_table = df.selectExpr('event_ts as start_time',
                               'hour(event_ts) as hour',
                               'day(event_ts) as day',
                               'weekofyear(event_ts) as week',
                               'month(event_ts) as month',
                               'year(event_ts) as year',
                               'dayofweek(event_ts) as weekday').distinct()

    # write time table to parquet files partitioned by year and month
    time_table.write.mode('overwrite').partitionBy('year', 'month').parquet(output_data + 'dimensions.parquet/time')

    # read in song data to use for songplays table
    song_df = spark.read.parquet(output_data + 'dimensions.parquet/songs')

    # read in artist data to use for songplays table
    artist_df = spark.read.parquet(output_data + 'dimensions.parquet/artists')

    # create SQL table views over the song and artist data frames
    song_df.registerTempTable("song")
    artist_df.registerTempTable("artist")
    df.registerTempTable("events")

    # extract columns from joined song and log datasets to create songplays table
    songplays_table = spark.sql('''
    SELECT DISTINCT
        event_ts,
        year(event_ts) as year,
        month(event_ts) as month,
        user_id, 
        level, 
        session_id,
        ev.location, 
        user_agent,
        s.song_id,
        a.artist_id
    FROM    events AS ev,
            song AS s,
            artist AS a
    WHERE   ev.song = s.title
    AND     ev.artist = a.name
    ''')

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.mode('overwrite').partitionBy('year', 'month').parquet(output_data + 'facts.parquet/songplays')


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3n://data-lake-cluster/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)

    spark.stop()

if __name__ == "__main__":
    main()
