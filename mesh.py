import open3d as o3d
import numpy as np
import sys

# I want to go from the unstructured dense point cloud to the mesh
# Remove outliers and crop then applty the triangular poisson mesh

if len(sys.argv) > 1:
        PROJECT_DIR = sys.argv[1] 
else:
    raise("No argument provided")


def display_inlier_outlier(cloud, ind):
    inlier_cloud = cloud.select_by_index(ind)
    outlier_cloud = cloud.select_by_index(ind, invert=True)

    print("Showing outliers (red) and inliers (gray): ")
    outlier_cloud.paint_uniform_color([1, 0, 0])
    inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
    o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud],
                                      zoom=0.3412,
                                      front=[0.4257, -0.2125, -0.8795],
                                      lookat=[2.6172, 2.0475, 1.532],
                                      up=[-0.0694, -0.9768, 0.2024])

# Load the point cloud
pcd = o3d.io.read_point_cloud(f"{PROJECT_DIR}/dense/dense.ply")

pcd = pcd.voxel_down_sample(voxel_size=0.002)

# Remove statistical irrelevant points, again to avoid outliers
cl, ind = pcd.remove_statistical_outlier(
    nb_neighbors=200,
    std_ratio=2
)

# display_inlier_outlier(pcd, ind) 

# Poisson constructor of the mesh
with o3d.utility.VerbosityContextManager(
        o3d.utility.VerbosityLevel.Debug) as cm:
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, 
        depth=8,  # More depth more detail
        scale=0.9)  # Scale of the poisson reconstruction
    

densities = np.asarray(densities)

# Remove low-density vertices
vertices_to_remove = densities < np.quantile(densities, 0.01)
mesh.remove_vertices_by_mask(vertices_to_remove)


mesh.compute_vertex_normals()
mesh.compute_triangle_normals(normalized=True)

mesh = mesh.remove_non_manifold_edges()
mesh = mesh.remove_unreferenced_vertices()
mesh = mesh.remove_degenerate_triangles()
mesh = mesh.remove_duplicated_vertices()
mesh = mesh.remove_duplicated_triangles()

print(" ---------------------------------------------------------------------------- ")
print("                             MESH RECONSTRUCTION                              ")
print(" ---------------------------------------------------------------------------- ")
o3d.visualization.draw_geometries([mesh],
                                  zoom=2)

o3d.io.write_triangle_mesh(f"{PROJECT_DIR}/dense/mesh.ply", mesh)
o3d.io.write_triangle_mesh(f"{PROJECT_DIR}/dense/mesh.stl", mesh)
