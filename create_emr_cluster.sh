#!/bin/sh

aws emr create-cluster \
        --name 'data-lake-cluster' \
        --use-default-roles \
        --release-label emr-5.28.0 \
        --instance-count 3 \
        --applications Name=Spark Name=JupyterHub Name=Livy Name=Hive \
        --ec2-attributes KeyName='spark-cluster' \
        --instance-type m5.xlarge \
        --region us-west-2
