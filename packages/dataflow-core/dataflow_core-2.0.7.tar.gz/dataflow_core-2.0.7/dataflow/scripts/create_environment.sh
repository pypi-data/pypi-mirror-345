#!/bin/bash
set -e

IFS=',' read -r -a  libraries <<< $1
conda_env_path=$2
py_version=$3

# Use an isolated conda package cache to avoid concurrency issues
export CONDA_PKGS_DIRS=$(mktemp -d)
# to delete conda package cache after script finishes
trap 'rm -rf "$CONDA_PKGS_DIRS"' EXIT

# 1. Creating conda environment
conda create --prefix ${conda_env_path} --yes python=${py_version}                         
${conda_env_path}/bin/pip install --root-user-action ignore ${libraries[@]}      

# 3. Install Dataflow Airflow to a separate path in environment 
${conda_env_path}/bin/pip install \
    --force-reinstall --root-user-action ignore \
    --no-warn-conflicts dataflow-airflow==2.10.5 \
    --target ${conda_env_path}/bin/airflow-libraries/ \
    --constraint https://raw.githubusercontent.com//apache/airflow/constraints-2.10.5/constraints-${py_version}.txt || true 

files=(
    ${conda_env_path}/lib/python${py_version}/site-packages/dbt/config/profile.py 
    ${conda_env_path}/lib/python${py_version}/site-packages/dbt/task/debug.py
)
for file in ${files[@]}
do      
    awk '{gsub("from dbt.clients.yaml_helper import load_yaml_text", "from dbt.dataflow_config.secrets_manager import load_yaml_text"); print}' $file > temp 
    mv temp $file
done

echo "Environment Creation Successful"