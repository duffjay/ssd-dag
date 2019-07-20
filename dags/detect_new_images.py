"""
### process new images 
- pull tarballs from s3
- extract
- run images through SSD (generating XML annotations)
- tarball annotations
- push to S3
- move new images to s3
"""

from datetime import timedelta
import os
from os import path

import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2),
    'email': ['jay.duff@cfacorp.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),

    # --- DATA ----,
    # pull tarballs from s3,
    's3_new_jpeg_tarballs': 's3://sagemaker-us-east-1-366734301438/datasets/cfa_product_images/new_images/',
    # local destination for tarballs,
    'new_jpeg_tarballs': '/home/jay/projects/ssd-dag/data/new_jpeg_tarballs',
    # extract to this directory,
    'new_jpeg_tarball_extract': '/home/jay/projects/ssd-dag/data/new_jpeg_tarball_extract/',
    # new images directory that will be fed into the model,
    'new_jpeg_images': '/home/jay/projects/ssd-dag/data/new_jpeg_images/',

    # --- MODEL ---,
    # s3 model location,
    's3_model': 's3://sagemaker-us-east-1-366734301438/models-trained/mobilenet/cfa_prod/20190711_hand_products/',
    # local model location,
    'model_path': '/home/jay/projects/ssd-dag/model/',
    # model name
    'model_name': ''
}




dag = DAG(
    'detect_new_images',
    default_args=default_args,
    description='generate cfa product detection annotations from new images'
)

# -- task --
# get the new image tarballs from S3
pull_new_jpeg_tarballs = BashOperator(
    task_id='pull_s3',
    bash_command="aws s3 cp {{params.source}} {{params.dest}} --exclude {{params.exc}} --include {{params.inc}} --recursive",
    params={ 'source': default_args['s3_new_jpeg_tarballs'], 'dest': default_args["new_jpeg_tarballs"], 'exc': "*.*", 'inc':"*.tar.gz"},
    dag=dag
)

# -- task --
# extract the tarballs to the extract directory

templated_extract = """
for filename in {{params.tarball_dir}}
do
  echo $filename
  tar -xvf $filename -C {{params.tarball_extract}}
done
"""
extract_path = os.path.join(default_args['new_jpeg_tarballs'], "*.tar.gz")

extract_tarballs = BashOperator(
    task_id='extract_tarballs',
    bash_command=templated_extract,
    params={'tarball_dir': extract_path, 'tarball_extract': default_args['new_jpeg_tarball_extract']},
    dag=dag

)

# -- task --
# move  all jpegs (regardless of subdirectories used in the tarballs) to a single directory
templated_move = """
find {{params.tarball_extract}} -mindepth 2 -type f -name *.jpg -print -exec mv {} {{params.images}} \;
"""
move_images = BashOperator(
    task_id='move_images',
    bash_command=templated_move,
    params={ 'tarball_extract': default_args['new_jpeg_tarball_extract'], 'images': default_args['new_jpeg_images']},
    dag=dag
)

# -- task --
# get model
pull_model = BashOperator(
    task_id='pull_model',
    bash_command="aws s3 cp {{params.source}} {{params.dest}} --exclude {{params.exc}} --include {{params.inc}} --recursive",
    params={ 'source': default_args['s3_model'], 'dest': default_args['model_path'], 'exc': "*.*", 'inc':"*.*"},
    dag=dag
)

# -- task -- 
# get
# python code/training/detect.py --image_dir ${LOCAL_NEW_IMAGES} --model_name 'tf_lite'\
#	 --model_path ${LOCAL_MODEL_DIR}output_tflite_graph.tflite --label_map_path ${LOCAL_LABEL_MAP} \
#	 --display no --annotation_dir ${LOCAL_NEW_UNVERIFIED_ANNOTATIONS}



# Assemble the DAG
pull_new_jpeg_tarballs >> extract_tarballs >> move_images >> pull_model