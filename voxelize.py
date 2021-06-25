from sklearn.preprocessing import MinMaxScaler
import numpy as np
import click
import open3d as o3d
import os
import laspy


Scaler = MinMaxScaler()


@click.command()
@click.option('-f', '--filename', type=click.Path(exists=True, dir_okay=False), 
    help="Path to .las point cloud")
@click.option('-o', '--output_path', type=click.Path(exists=False, dir_okay=True, file_okay=False), 
    help="Where voxel data will be stored")
@click.option('-s', '--scale', default=1000, type=int, 
    help="A variable to scale points coords")
@click.option('-v', '--voxel', 'voxel_size', default=0.1, type=float, 
    help="How big are voxels gonna be")
def voxelize(filename, output_path, scale, voxel_size, ):
    '''Turns point cloud into voxel grid'''
    f = laspy.file.File(filename)
    points = f.points["point"][["X", "Y", "Z"]]
    colors = f.points["point"][["red", "green", "blue"]]

    points = np.array(points.tolist())
    colors = np.array(colors.tolist())

    points = points / scale
    colors_fit = Scaler.fit_transform(colors)


    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors_fit)
    pcd.estimate_normals()
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd,
                                                            voxel_size=voxel_size)
    voxels = voxel_grid.get_voxels()
    box_size = ((voxel_grid.get_max_bound() - voxel_grid.get_min_bound()) / voxel_size).astype(int)
    indeces_dump = np.array(list(v.grid_index[[0, 2, 1]] for v in tqdm(voxel_grid.get_voxels())))
    colors_dump = np.array(list(v.color for v in tqdm(voxel_grid.get_voxels())))

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    np.save(f"{output_path}/indeces.npy", indeces_dump)
    np.save(f"{output_path}/icolors.npy", colors_dump)
    np.save(f"{output_path}/bb.npy", box_size[[0, 2, 1]])

    print("Done))")


def main():
    voxelize()

if __name__ == "__main__":
    main()