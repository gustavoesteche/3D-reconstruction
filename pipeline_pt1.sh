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

mkdir -p "$IMAGE_DIR"
mkdir -p "$PROJECT_DIR/sparse"
touch    "$DATABASE_PATH"

colmap feature_extractor \
    --database_path                       "$DATABASE_PATH" \
    --image_path                          "$IMAGE_DIR" \
    --descriptor_normalization            "l1_root"\
    --ImageReader.single_camera            1 \
    --FeatureExtraction.num_threads        4 \
    --FeatureExtraction.use_gpu            1 \
    --SiftExtraction.max_num_features      6000 \
    --SiftExtraction.estimate_affine_shape 1 \
    --SiftExtraction.domain_size_pooling   1
    # --SiftExtraction.first_octave arg    (=-1) \

colmap exhaustive_matcher \
    --database_path                        "$DATABASE_PATH" \
    --ExhaustiveMatching.block_size        2                \
    --SiftMatching.max_ratio               0.7              \
    --SiftMatching.max_distance            0.7              \
    --FeatureMatching.guided_matching      1 

#--FeatureMatching.type arg (=SIFT)    # Change when testing AKAZE 

# Ransac parameters for RANSAC Feature testing (Section 5 of the work)    
#    --TwoViewGeometry.min_num_inliers arg (=15)
#    --TwoViewGeometry.multiple_models arg (=0)
#    --TwoViewGeometry.compute_relative_pose arg (=0)
#    --TwoViewGeometry.detect_watermark arg (=1)
#    --TwoViewGeometry.multiple_ignore_watermark arg (=1)
#    --TwoViewGeometry.watermark_detection_max_error arg (=4)
#    --TwoViewGeometry.filter_stationary_matches arg (=0)
#    --TwoViewGeometry.stationary_matches_max_error arg (=4)
#    --TwoViewGeometry.max_error arg (=4)
#    --TwoViewGeometry.confidence arg (=0.999)
#    --TwoViewGeometry.max_num_trials arg (=10000)
#    --TwoViewGeometry.min_inlier_ratio arg (=0.25)
#    --TwoViewGeometry.random_seed arg (=-1)

colmap mapper \
    --database_path "$DATABASE_PATH" \
    --image_path "$IMAGE_DIR" \
    --output_path "$PROJECT_DIR/sparse" \
    --Mapper.num_threads 1 \
    --Mapper.ba_use_gpu 1 \
    --Mapper.max_model_overlap 1 \
    --Mapper.multiple_models 0 \
    --Mapper.max_num_models 1