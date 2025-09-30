import numpy as np
from pathlib import Path
import open3d as o3d
import sys

if len(sys.argv) > 1:
    PROJECT_DIR = sys.argv[1]
else:
    sys.exit("Error: No project directory provided. Usage: python your_script.py /path/to/project")

def read_cameras_txt(path):
    """Reads a COLMAP cameras.txt file."""
    cameras = {}
    with open(path, "r") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            cam_id = int(parts[0])
            model = parts[1]
            width = int(parts[2])
            height = int(parts[3])
            params = np.array(list(map(float, parts[4:])))
            cameras[cam_id] = {"model": model, "width": width, "height": height, "params": params}
    return cameras

def read_images_txt(path):
    """Reads a COLMAP images.txt file."""
    images = {}
    with open(path, "r") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            image_id = int(parts[0])
            qvec = np.array(list(map(float, parts[1:5])))
            tvec = np.array(list(map(float, parts[5:8])))
            camera_id = int(parts[8])
            # The next line in the file contains 2D points, which we skip
            next(f)
            images[image_id] = {"qvec": qvec, "tvec": tvec, "camera_id": camera_id}
    return images

def qvec2rotmat(qvec):
    """Converts a quaternion vector to a rotation matrix."""
    qw, qx, qy, qz = qvec
    return np.array([
        [1 - 2*qy*qy - 2*qz*qz,   2*qx*qy - 2*qw*qz,       2*qx*qz + 2*qw*qy],
        [2*qx*qy + 2*qw*qz,       1 - 2*qx*qx - 2*qz*qz,   2*qy*qz - 2*qw*qx],
        [2*qx*qz - 2*qw*qy,       2*qy*qz + 2*qw*qx,       1 - 2*qx*qx - 2*qy*qy]
    ])

def main():
    model_dir = Path(PROJECT_DIR) / "sparse_txt" / "0"
    mesh_path = Path(PROJECT_DIR) / "dense" / "mesh.ply"
    output_path = f"{PROJECT_DIR}/scene.glb"

    cameras = read_cameras_txt(model_dir / "cameras.txt")
    images = read_images_txt(model_dir / "images.txt")

    mesh = o3d.io.read_triangle_mesh(str(mesh_path))
    mesh.compute_vertex_normals()


    scene_bbox = mesh.get_axis_aligned_bounding_box()
    sphere_radius = np.mean(scene_bbox.get_extent()) * 0.01  

    camera_markers = []
    for img in images.values():
        R = qvec2rotmat(img["qvec"])
        tvec = img["tvec"]
        
        camera_center = -R.T @ tvec

        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=sphere_radius)
        sphere.translate(camera_center)
        sphere.paint_uniform_color([1.0, 0.0, 0.0]) 
        
        camera_markers.append(sphere)

    combined_mesh = mesh
    for marker in camera_markers:
        combined_mesh += marker
    
    o3d.io.write_triangle_mesh(output_path, combined_mesh, write_vertex_colors=True)
    o3d.visualization.draw(combined_mesh)
    
if __name__ == "__main__":
    main()
