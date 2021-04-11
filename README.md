# Apache Spark Data Lake

## Introduction

Sparkify use this database to analyse how users interact with their service, 
and with their growing collection of music.

## Design

This section covers the design of the Sparkify data lake. Key features are:

* an Apache Spark cluster is used to extract, load, transform and store the data
* the cluster resides on Amazon Web Services EC2 (Elastic Cloud) and uses S3 storage
* input files are read as collections of JSON files, within directories, in an S3 bucket
* output files are written to another S3 bucket, using Parquet which is a columnar file format
* Spark dataframes and SQL are used to transform the data

The design and development approach followed is to validate local design in a Jupyter Notebook, 
then transfer the working code into a Python ETL script.

### AWS Setup

In the first instance, you want to create the EMR cluster to run Spark, as is explained in the course notes.
However, there are two approaches that can be followed:

1. Create a cluster as described in the course notes (look at the `create_emr_cluster.sh` script in the project directory)
2. Create a Jupyter Notebook, and as part of this create a new cluster to be associated with the notebook

In the end I went for option 2, as the clusters I got using option one did not appear as eligible, when trying to bind
my notebook to an existing cluster.

### Database Schema

The database schema reflect that used in previous projects, with fact and dimension tables retained, specifically:

| Table | Usage |
| ----- | ----- |
| `users` | Records each user of the streaming service, including if they are paying for the service. |
| `songs` | Records iformation about the songs that users choose to listen to. |
| `artists` | Records information about the artists that perform the songs. |
| `time` | Records information related to the event in time at which users choose to play songs. |

### ETL Pipeline

The ETL pipeline is implemented in a single Python script, which is deployed onto the EMR cluster where it is run.

## Diagnosing errors

Spark errors are hard to diagnose. Here are a few possibilities:

* use of full SQL appears to require Hive to be installed, which the default Spark installation seems to no include, when
defining the cluster, set the options described in the course notes, then switch to Go to advanced options and add Hive
  
* if while executing the notebook you get a reference to a missing session, you will need to restart your kernel and run
the notebook from the top again
  

