#!/bin/bash
while getopts ":p:d:" flag; do
  case "${flag}" in
    p) PROJECT_DIR=${OPTARG} ;;
    d) DENSE=${OPTARG} ;;
    *) echo "Usage: $0 -p <project_path> -d <dense_value>" >&2; exit 1 ;;
  esac
done

if [ -z "$PROJECT_DIR" ]; then
  echo "Error: -p <project_path> is required."
  echo "Usage: $0 -p <project_path> -d <dense_value>"
  exit 1
fi



if [ "$DENSE" = "1" ]; then
  echo " ---------------------------------------------------------------------------- "
  echo "                          DENSE RECONSTRUCTION                                "
  echo " ---------------------------------------------------------------------------- "
  open3d draw "$PROJECT_DIR/dense/dense.ply"
  exit 0
fi

if [ "$DENSE" = "2" ]; then
  echo " ---------------------------------------------------------------------------- "
  echo "                          MESH RECONSTRUCTION                                "
  echo " ---------------------------------------------------------------------------- "
  open3d draw "$PROJECT_DIR/dense/mesh.ply"
  exit 0
fi

colmap model_converter \
    --input_path "$PROJECT_DIR/sparse/0" \
    --output_path "$PROJECT_DIR/sparse.ply" \
    --output_type PLY

echo " ---------------------------------------------------------------------------- "
echo "                            SPARSE RECONSTRUCTION                             "
echo " ---------------------------------------------------------------------------- "
open3d draw "$PROJECT_DIR/sparse.ply"
exit 0
