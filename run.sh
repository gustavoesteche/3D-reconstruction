#!/bin/bash

while getopts ":p:" flag; do
  case "${flag}" in
    p) PROJECT_DIR=${OPTARG} ;;
    *) echo "Usage: $0 -p <project_path>" >&2; exit 1 ;;
  esac
done

if [ -z "$PROJECT_DIR" ]; then
  echo "Error: -p <project_path> is required."
  echo "Usage: $0 -p <project_path>"
  exit 1
fi

./pipeline_pt1.sh -p $PROJECT_DIR 

./visualize_ply.sh -p $PROJECT_DIR 

./pipeline_pt2.sh -p $PROJECT_DIR

./visualize_ply.sh -p $PROJECT_DIR -d 1

python3 mesh.py "$PROJECT_DIR"