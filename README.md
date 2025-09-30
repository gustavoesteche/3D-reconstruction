# 3D Reconstruction Pipeline (COLMAP + Open3D)

This repository provides a complete pipeline for **Structure-from-Motion (SfM)**, **Multi-View Stereo (MVS)**, and **Mesh generation** using COLMAP and Open3D.

---

## 🚀 Prerequisites

1. **Build COLMAP with CUDA support**
   A **CUDA build is required** to enable the `patch_match` stereo algorithm.
   Follow the official COLMAP build instructions here:
   👉 [COLMAP: Build from Source](https://colmap.github.io/install.html)

2. **Set up a Python environment**
   Create and activate a Python virtual environment (conda or venv), then install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your project directory**
   Your project folder must follow the structure below:

   ```
   project_dir/
   └── images/
       ├── img1.jpg
       ├── img2.jpg
       ├── ...
       └── imgN.jpg
   ```

   ⚠️ Ensure you have enough **disk space**:

   * SfM + MVS + Mesh reconstruction can consume **tens of GBs**, depending on the dataset size.

---

## ▶️ Running the Pipeline

To run the **entire pipeline (SfM + MVS + Mesh)**:

```bash
./run.sh -p <PROJECT_DIR>
```

* `-p <PROJECT_DIR>` is **mandatory** and must point to a directory structured like the example above.
* Outputs (sparse model, dense reconstruction, and final mesh) will be saved inside the project directory.

### Brief pipeline overview

* `pipeline_pt1.sh -p <PROJECT_PATH>`: Performs SfM to construct the sparse point cloud.
* `pipeline_pt2.sh -p <PROJECT_PATH>`: Performs densification of the sparse point cloud using patch match to construct the dense point cloud.
* `python3 mesh.py <PROJECT_PATH>`: Generates the mesh from the dense point cloud using Poisson reconstruction.

---

## 🖼️ Visualizing the Results

When running the pipeline, the results will automatically be generated in the Open3D visualizer. If visualization is not the focus, comment out the `visualization_ply.sh` calls in `run.sh`.

The paths for generating each result file are standardized. For a quick guide:

* To see the sparse point cloud: `visualize_ply.sh -p <PROJECT_DIR>`
* To see the dense point cloud: `visualize_ply.sh -p <PROJECT_DIR> -d 1`
* To see the mesh: `visualize_ply.sh -p <PROJECT_DIR> -d 2`

In the visualization folder, there are 3 files. To use them, follow these instructions:

* First, run `./bin_to_txt.sh -p <PROJECT_PATH>` to convert the camera and image information from binary to text.
* To create a server with the point cloud and camera frustums, run `python3 vis_camera.py <PROJECT_PATH>` and 
to run only local, run `python3 vis_camera_local.py <PROJECT_PATH>`.
* To generate the OBJ file with only the camera 3D points, run `python3 vis_camera_obj.py <PROJECT_PATH>`.

---

## 📌 Notes

* Make sure your GPU drivers and CUDA toolkit are properly installed and match your hardware.
* For large datasets, consider running on a machine with **≥8GB RAM** and **ample storage**.
* If you encounter issues, verify that COLMAP is correctly compiled with CUDA (`colmap --help` should list GPU options), since this is the most common problem.

---

Inside the project folder, the pipeline generates `dense` and `sparse` folders along with many files. The most important ones are:

* `sparse/0` or `sparse.ply` → SfM reconstruction
* `dense/dense.ply` → MVS reconstruction
* `dense/mesh.ply` → Final mesh
* `dense/mesh.stl` → Conversion from PLY to STL

Additional files are also generated, containing camera and image depth information. For more details on these, consult the official COLMAP documentation.

If you want to test your setup with some images, you may use this [dataset](https://drive.google.com/drive/folders/1NNXDdetofmA7FE3KZeeFTfxA7B_B58PT?usp=sharing), 
the results of one 3D reconstruction of the angel is presented in the folder `results`, with the visualization video presented in the folder `navigation`.

---

## 🙏 Acknowledgments

* [COLMAP](https://colmap.github.io/) – for providing a powerful Structure-from-Motion and Multi-View Stereo pipeline.
* [Open3D](http://www.open3d.org/) – for its excellent 3D data processing, surface reconstruction, meshing, and visualization tools.
* [Viser](https://github.com/nerfstudio-project/viser) – for providing a server interface to visualize the point cloud alongside the camera frustums.
