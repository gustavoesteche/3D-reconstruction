import numpy as np
from pathlib import Path
import argparse
from plyfile import PlyData
import viser
import open3d as o3d
import sys

if len(sys.argv) > 1:
        PROJECT_DIR = sys.argv[1] 
else:
    raise("No argument provided")


def read_cameras_txt(path):
    cameras = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            cam_id = int(parts[0])
            model = parts[1]
            width = int(parts[2])
            height = int(parts[3])
            params = list(map(float, parts[4:]))
            cameras[cam_id] = {
                "model": model,
                "width": width,
                "height": height,
                "params": np.array(params, dtype=float)
            }
    return cameras

def read_images_txt(path):
    images = {}
    with open(path, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            image_id = int(parts[0])
            qvec = np.array(list(map(float, parts[1:5])), dtype=float)   # qw qx qy qz
            tvec = np.array(list(map(float, parts[5:8])), dtype=float)
            camera_id = int(parts[8])
            name = " ".join(parts[9:]) if len(parts) > 9 else ""
            # skip the next line (POINTS2D)
            pts2d_line = f.readline()
            images[image_id] = {
                "qvec": qvec,
                "tvec": tvec,
                "camera_id": camera_id,
                "name": name
            }
    return images

def create_camera_frame(R, t, camera, scale=1.0):
    """
    Create frustum vertices that match the camera image plane dimensions.
    R: 3x3 rotation matrix (camera->world)
    t: translation vector
    camera: dictionary with model, params, width, height
    scale: depth of frustum
    """
    w = camera["width"]
    h = camera["height"]
    params = camera["params"]

    # Get focal lengths and principal point
    if len(params) >= 4:
        fx, fy, cx, cy = params[:4]
    else:
        fx = fy = max(w, h) * 0.5
        cx = w / 2
        cy = h / 2

    z = scale  # distance from camera center to image plane
    corners_cam = np.zeros((4, 3))
    # top-left
    corners_cam[0, 0] = (0 - cx) * z / fx
    corners_cam[0, 1] = (0 - cy) * z / fy
    corners_cam[0, 2] = z
    # top-right
    corners_cam[1, 0] = (w - cx) * z / fx
    corners_cam[1, 1] = (0 - cy) * z / fy
    corners_cam[1, 2] = z
    # bottom-right
    corners_cam[2, 0] = (w - cx) * z / fx
    corners_cam[2, 1] = (h - cy) * z / fy
    corners_cam[2, 2] = z
    # bottom-left
    corners_cam[3, 0] = (0 - cx) * z / fx
    corners_cam[3, 1] = (h - cy) * z / fy
    corners_cam[3, 2] = z

    # Add camera origin
    verts_cam = np.vstack([np.zeros((1,3)), corners_cam])  # origin + 4 corners
    verts_world = (R @ verts_cam.T).T + t.reshape(1,3)

    # Define edges for the frame (lines connecting origin to corners + rectangle around image plane)
    edges = [
        [0,1],[0,2],[0,3],[0,4],
        [1,2],[2,3],[3,4],[4,1]
    ]
    return verts_world, edges


def read_points3d_txt(path):
    points = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            pid = int(parts[0])
            xyz = np.array(list(map(float, parts[1:4])), dtype=float)
            rgb = np.array(list(map(int, parts[4:7])), dtype=np.uint8)
            error = float(parts[7])
            track = list(map(int, parts[8:])) if len(parts) > 8 else []
            points[pid] = {"xyz": xyz, "rgb": rgb, "error": error, "track": track}
    return points

def qvec2rotmat(qvec):
    qw, qx, qy, qz = qvec
    R = np.array([
        [1 - 2*qy*qy - 2*qz*qz,     2*qx*qy - 2*qw*qz,     2*qx*qz + 2*qw*qy],
        [2*qx*qy + 2*qw*qz,     1 - 2*qx*qx - 2*qz*qz,     2*qy*qz - 2*qw*qx],
        [2*qx*qz - 2*qw*qy,     2*qy*qz + 2*qw*qx,     1 - 2*qx*qx - 2*qy*qy]
    ], dtype=float)
    return R

def create_frustum_mesh(R, t, camera, scale=0.5):
    model = camera["model"].upper()
    params = camera["params"]
    w = camera["width"]
    h = camera["height"]

    if model.startswith("PINHOLE") or model.startswith("OPENCV") or model.startswith("OPENCV_FISHEYE"):
        if params.size >= 4:
            fx, fy, cx, cy = float(params[0]), float(params[1]), float(params[2]), float(params[3])
        elif params.size == 3:
            fx = fy = float(params[0]); cx = float(params[1]); cy = float(params[2])
        else:
            fx = fy = max(w, h) * 0.5; cx = w*0.5; cy = h*0.5
    elif model.startswith("SIMPLE_PINHOLE") or model.startswith("SIMPLE_RADIAL"):
        fx = float(params[0]) if params.size >= 1 else max(w, h) * 0.5
        fy = fx
        cx = float(params[1]) if params.size >= 2 else w*0.5
        cy = float(params[2]) if params.size >= 3 else h*0.5
    else:
        fx = fy = params[0] if params.size >= 1 else max(w, h) * 0.5
        cx = params[1] if params.size >= 2 else w*0.5
        cy = params[2] if params.size >= 3 else h*0.5

    z = float(scale)
    uv = np.array([[0.0, 0.0], [w, 0.0], [w, h], [0.0, h]], dtype=float)
    corners_cam = np.zeros((4,3), dtype=float)
    corners_cam[:,0] = (uv[:,0] - cx) * z / fx
    corners_cam[:,1] = (uv[:,1] - cy) * z / fy
    corners_cam[:,2] = z
    center_cam = np.array([0.0, 0.0, 0.0], dtype=float)
    verts_cam = np.vstack([center_cam, corners_cam])   # (5,3)
    verts_world = (R @ verts_cam.T).T + t.reshape(1,3)
    faces = np.array([
        [0,1,2],
        [0,2,3],
        [0,3,4],
        [0,4,1],
        [1,2,3],
        [1,3,4]
    ], dtype=int)
    return verts_world, faces


def load_ply_points(ply_path):
    mesh = o3d.io.read_point_cloud(str(ply_path))
    points = np.asarray(mesh.points, dtype=float)
    colors = None
    if mesh.has_colors():
        colors = np.asarray(mesh.colors, dtype=float)
    return points, colors

def main():
    model_dir = Path(f"{PROJECT_DIR}/sparse_txt/0")
    cameras_txt = model_dir / "cameras.txt"
    images_txt = model_dir / "images.txt"

    cameras = read_cameras_txt(cameras_txt)
    images = read_images_txt(images_txt)

    points, colors = load_ply_points(Path(f"{PROJECT_DIR}/dense/dense.ply"))

    server = viser.ViserServer(port=8080)

    server.scene.add_point_cloud(
        "/dense_cloud",
        points= points,
        colors=(colors),
        point_size=float(0.002),
    )

    for img_id, img in images.items():
        cam = cameras[img["camera_id"]]
        
        w = cam["width"]
        h = cam["height"]
        f = cam["params"][0]
        
        qvec = img["qvec"].astype(float)   # [qw, qx, qy, qz] from COLMAP
        tvec = img["tvec"].astype(float)   # t from COLMAP (part of world->cam)

        # 1) compute R (world->camera) and camera center C in world coords
        R_world2cam = qvec2rotmat(qvec)
        C = -R_world2cam.T @ tvec   # camera center (world coordinates)

        # 2) quaternion for camera->world is the conjugate of qvec
        qw, qx, qy, qz = qvec.tolist()
        q_cam2world = np.array([qw, -qx, -qy, -qz], dtype=float)

        server.scene.add_camera_frustum(
            f"/cameras/{img['name']}",
            fov=2*np.arctan(h/(2*f)),
            aspect=w/h,
            color=[0,0,255],
            wxyz=q_cam2world,
            position=C,
            scale=float(1),
            line_width = 1.0
        )

    
    print("Viewer running at http://localhost:8080")
    server.sleep_forever()

if __name__ == "__main__":
    main()
