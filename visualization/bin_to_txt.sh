#!/bin/bash
while getopts ":p:d:" flag; do
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

mkdir -p "$PROJECT_DIR/sparse_txt"
mkdir -p "$PROJECT_DIR/sparse_txt/0"

colmap model_converter \
    --input_path "$PROJECT_DIR/sparse/0" \
    --output_path "$PROJECT_DIR/sparse_txt/0" \
    --output_type TXT

exit 0
