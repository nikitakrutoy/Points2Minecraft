import pymclevel.mclevel as mclevel
import pymclevel.box as box
import pickle
import numpy as np
import click
from skimage import io, color
from tqdm.auto import tqdm


@click.command()
@click.argument('voxel_data', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.argument('color_map_png', type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.argument('color_map_pkl', type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.argument('map_path', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option("-p", "--postion", type=float, nargs=2, default=None)
def add2mc(voxel_data, color_map_png, color_map_pkl, map_path, position):
    indeces = np.load(f"{voxel_data}/indeces.npy")
    box_size = np.load(f"{voxel_data}/icolors.npy")
    colors = np.load(f"{voxel_data}/bb.npy")
    
    map_rgb = io.imread(color_map_png)
    map_lab = color.rgb2lab(map_rgb)
    with open(color_map_pkl, "rb") as f:
        color_map = pickle.load(f)

    level = mclevel.fromFile(map_path)
    if position is None:
        spawn = np.array(level.playerSpawnPosition())
        offset = np.array((10, 0, 10))
        position = spawn + offset
    else:
        position = np.array(list(position))

    bb = box.BoundingBox((position).tolist(), box_size)


    def color2block(c):
        distance = 300
        voxel_color = color.rgb2lab([[c]])[0][0]
        for k, map_column in enumerate(map_lab):
            for l, map_pixel in enumerate(map_column):
                delta = color.deltaE_cie76(voxel_color,map_pixel)
                if delta < distance:
                    distance = delta
                    blockID, data = color_map[(k,l)]
        return blockID, data

    print("Cleaning")
    blockID = 0
    data = 0
    blockInfo = level.materials.blockWithID(blockID, data)
    level.fillBlocks(bb, blockInfo)

    print("Cleared")
    print("Building")
    blockID = 1
    data = 0
    blockInfo = level.materials.blockWithID(blockID, data)
    for pos, c in tqdm(zip(indeces, colors)):
        blockInfo = level.materials.blockWithID(*color2block(c))
        bb_ = box.BoundingBox((position + pos).tolist(), (1, 1, 1))
        level.fillBlocks(bb_, blockInfo)
    level.saveInPlace()
    print("Done!")

def main():
    add2mc()

