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

IMAGE_DIR="$PROJECT_DIR/images"
DATABASE_PATH="$PROJECT_DIR/database.db"

# --- 4. Image undistortion ---
colmap image_undistorter \
    --image_path "$IMAGE_DIR" \
    --input_path "$PROJECT_DIR/sparse/0" \
    --output_path "$PROJECT_DIR/dense" \
    --output_type COLMAP

# --- 5. PatchMatch stereo ---
colmap patch_match_stereo \
    --workspace_path "$PROJECT_DIR/dense" \
    --workspace_format COLMAP \
    --PatchMatchStereo.num_iterations 2 \
    --PatchMatchStereo.window_step 2    \
    --PatchMatchStereo.num_samples 2 \
    --PatchMatchStereo.geom_consistency 1 \
    --PatchMatchStereo.max_image_size 1000 \
    --PatchMatchStereo.cache_size 8

# --- 6. Stereo fusion ---
colmap stereo_fusion \
    --workspace_path "$PROJECT_DIR/dense" \
    --workspace_format COLMAP \
    --input_type geometric \
    --StereoFusion.num_threads 4 \
    --output_path "$PROJECT_DIR/dense/dense.ply" \
    --output_type PLY