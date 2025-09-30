import numpy as np
from pathlib import Path
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
    images = {}
    with open(path, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            image_id = int(parts[0])
            qvec = np.array(list(map(float, parts[1:5])))
            tvec = np.array(list(map(float, parts[5:8])))
            camera_id = int(parts[8])
            name = " ".join(parts[9:])
            f.readline()  # skip 2D points
            images[image_id] = {"qvec": qvec, "tvec": tvec, "camera_id": camera_id, "name": name}
    return images

def qvec2rotmat(qvec):
    qw, qx, qy, qz = qvec
    return np.array([
        [1 - 2*qy*qy - 2*qz*qz,   2*qx*qy - 2*qw*qz,       2*qx*qz + 2*qw*qy],
        [2*qx*qy + 2*qw*qz,       1 - 2*qx*qx - 2*qz*qz,   2*qy*qz - 2*qw*qx],
        [2*qx*qz - 2*qw*qy,       2*qy*qz + 2*qw*qx,       1 - 2*qx*qx - 2*qy*qy]
    ])

def create_frustum_lines(qvec, tvec, cam, scale, color=[0,0,1]):
    R = qvec2rotmat(qvec)         # world-to-camera rotation
    C = -R.T @ tvec               # camera center in world coords

    w, h = cam["width"], cam["height"]
    params = cam["params"]

    if len(params) >= 4:
        fx, fy, cx, cy = params[:4]
    else:
        fx = fy = max(w, h) * 0.5
        cx, cy = w/2, h/2

    z = scale
    uv = np.array([[0,0],[w,0],[w,h],[0,h]], float)
    corners = np.zeros((4,3))
    corners[:,0] = (uv[:,0] - cx) * z / fx
    corners[:,1] = (uv[:,1] - cy) * z / fy
    corners[:,2] = z

    verts_cam = np.vstack([[0,0,0], corners])      # in camera coords
    verts_world = (R.T @ verts_cam.T).T + C        # transform to world

    lines = [[0,1],[0,2],[0,3],[0,4],[1,2],[2,3],[3,4],[4,1]]
    colors = [color for _ in lines]

    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(verts_world)
    line_set.lines = o3d.utility.Vector2iVector(lines)
    line_set.colors = o3d.utility.Vector3dVector(colors)
    return line_set



def main():
    model_dir = Path(f"{PROJECT_DIR}/sparse_txt/0")
    cameras = read_cameras_txt(model_dir/"cameras.txt")
    images = read_images_txt(model_dir/"images.txt")

    mesh = o3d.io.read_triangle_mesh(f"{PROJECT_DIR}/dense/mesh.ply")

    geometries = [mesh]
    for img in images.values():
        cam = cameras[img["camera_id"]]
        frustum = create_frustum_lines(img["qvec"], img["tvec"], cam, 1, color=[0,0,1])
        geometries.append(frustum)

    #o3d.visualization.draw(geometries)
    
    o3d.io.write_geometry("scene.glb", geometries)

    

if __name__ == "__main__":
    main()
