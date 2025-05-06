# %%
import numpy as np
from cellmap_analyze.process.connected_components import ConnectedComponents
from cellmap_analyze.util import dask_util
from cellmap_analyze.util import io_util
from cellmap_analyze.util.dask_util import (
    create_block_from_index,
    dask_computer,
    guesstimate_npartitions,
)
from cellmap_analyze.util.image_data_interface import ImageDataInterface
from cellmap_analyze.util.io_util import (
    get_name_from_path,
    split_dataset_path,
)

import logging
import dask.bag as db
import os
from cellmap_analyze.util.mask_util import MasksFromConfig
from cellmap_analyze.util.zarr_util import create_multiscale_dataset
import cc3d

from scipy import ndimage
import mwatershed as mws
import fastremap
import fastmorph

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class MutexWatershed:
    def __init__(
        self,
        affinities_path,
        output_path,
        adjacent_edge_bias=-0.4,
        lr_bias_ratio=-0.08,
        filter_val=0.5,
        neighborhood=[
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [3, 0, 0],
            [0, 3, 0],
            [0, 0, 3],
            [9, 0, 0],
            [0, 9, 0],
            [0, 0, 9],
        ],
        mask_config=None,
        roi=None,
        minimum_volume_nm_3=0,
        maximum_volume_nm_3=np.inf,
        num_workers=10,
        connectivity=2,
        do_opening=False,
        delete_tmp=False,
    ):
        self.neighborhood = neighborhood
        self.affinities_idi = ImageDataInterface(affinities_path)

        # affinities information
        self.neighborhood = neighborhood
        self.adjacent_edge_bias = adjacent_edge_bias
        self.lr_bias_ratio = lr_bias_ratio
        self.filter_val = filter_val
        self.do_opening = do_opening

        if roi is None:
            self.roi = self.affinities_idi.roi
        else:
            self.roi = roi

        self.voxel_size = self.affinities_idi.voxel_size
        self.do_full_connected_components = False
        output_ds_name = get_name_from_path(output_path)
        output_ds_basepath = split_dataset_path(output_path)[0]
        os.makedirs(output_ds_basepath, exist_ok=True)

        self.connected_components_blockwise_path = (
            output_ds_basepath + "/" + output_ds_name + "_blockwise"
        )
        create_multiscale_dataset(
            self.connected_components_blockwise_path,
            dtype=np.uint64,
            voxel_size=self.voxel_size,
            total_roi=self.roi,
            write_size=np.array(self.affinities_idi.chunk_shape[1:]) * self.voxel_size,
        )
        self.connected_components_blockwise_idi = ImageDataInterface(
            self.connected_components_blockwise_path + "/s0",
            mode="r+",
        )

        self.output_path = output_path

        # evaluate minimum_volume_nm_3 voxels if it is a string
        if type(minimum_volume_nm_3) == str:
            minimum_volume_nm_3 = float(minimum_volume_nm_3)
        if type(maximum_volume_nm_3) == str:
            maximum_volume_nm_3 = float(maximum_volume_nm_3)
        self.minimum_volume_nm_3 = minimum_volume_nm_3
        self.maximum_volume_nm_3 = maximum_volume_nm_3
        self.minimum_volume_voxels = minimum_volume_nm_3 / np.prod(self.voxel_size)
        self.maximum_volume_voxels = maximum_volume_nm_3 / np.prod(self.voxel_size)

        self.mask = None
        if mask_config:
            self.mask = MasksFromConfig(
                mask_config,
                output_voxel_size=self.voxel_size,
                connectivity=connectivity,
            )

        self.connectivity = connectivity
        self.delete_tmp = delete_tmp

        self.num_workers = num_workers
        self.compute_args = {}
        if self.num_workers == 1:
            self.compute_args = {"scheduler": "single-threaded"}
            self.num_local_threads_available = 1
            self.local_config = None
        else:
            self.num_local_threads_available = len(os.sched_getaffinity(0))
            self.local_config = {
                "jobqueue": {
                    "local": {
                        "ncpus": self.num_local_threads_available,
                        "processes": self.num_local_threads_available,
                        "cores": self.num_local_threads_available,
                        "log-directory": "job-logs",
                        "name": "dask-worker",
                    }
                }
            }

    @staticmethod
    def filter_fragments(
        affs_data: np.ndarray, fragments_data: np.ndarray, filter_val: float
    ) -> None:
        """Allows filtering of MWS fragments based on mean value of affinities & fragments. Will filter and update the fragment array in-place.

        Args:
            aff_data (``np.ndarray``):
                An array containing affinity data.

            fragments_data (``np.ndarray``):
                An array containing fragment data.

            filter_val (``float``):
                Threshold to filter if the average value falls below.
        """

        average_affs: float = np.mean(affs_data.data, axis=0)

        filtered_fragments: list = []

        fragment_ids: np.ndarray = np.unique(fragments_data)

        for fragment, mean in zip(
            fragment_ids, ndimage.mean(average_affs, fragments_data, fragment_ids)
        ):
            if mean < filter_val:
                filtered_fragments.append(fragment)

        filtered_fragments: np.ndarray = np.array(
            filtered_fragments, dtype=fragments_data.dtype
        )
        # replace: np.ndarray = np.zeros_like(filtered_fragments)
        fastremap.mask(fragments_data, filtered_fragments, in_place=True)

    @staticmethod
    def mutex_watershed(
        affinities, neighborhood, adjacent_edge_bias, lr_bias_ratio, filter_val
    ):
        if affinities.dtype == np.uint8:
            # logger.info("Assuming affinities are in [0,255]")
            max_affinity_value: float = 255.0
            affinities = affinities.astype(np.float64)
        else:
            affinities = affinities.astype(np.float64)
            max_affinity_value: float = 1.0

        affinities /= max_affinity_value

        if affinities.max() < 1e-3:
            segmentation = np.zeros(affinities.shape[1:], dtype=np.uint64)
            return segmentation

        random_noise = np.random.randn(*affinities.shape) * 0.001
        smoothed_affs = (
            ndimage.gaussian_filter(
                affinities, sigma=(0, *(np.amax(neighborhood, axis=0) / 3))
            )
            - 0.5
        ) * 0.01
        shift: np.ndarray = np.array(
            [
                (
                    adjacent_edge_bias
                    if max(offset) <= 1
                    else np.linalg.norm(offset) * lr_bias_ratio
                )
                for offset in neighborhood
            ]
        ).reshape((-1, *((1,) * (len(affinities.shape) - 1))))

        # filter fragments
        segmentation = mws.agglom(
            affinities + shift + random_noise + smoothed_affs,
            offsets=neighborhood,
        )

        if filter_val > 0.0:
            MutexWatershed.filter_fragments(affinities, segmentation, filter_val)
        # fragment_ids = fastremap.unique(segmentation[segmentation > 0])
        # fastremap.mask_except(segmentation, filtered_fragments, in_place=True)
        fastremap.renumber(segmentation, in_place=True)
        return segmentation

    @staticmethod
    def instancewise_instance_segmentation(segmentation, connectivity, do_opening):
        ids = fastremap.unique(segmentation[segmentation > 0])
        output = np.zeros_like(segmentation, dtype=np.uint64)
        for id in ids:
            segmentation_for_id = segmentation == id
            if do_opening:
                segmentation_for_id = fastmorph.erode(segmentation_for_id)

            cc = cc3d.connected_components(
                segmentation_for_id,
                connectivity=6 + 12 * (connectivity >= 2) + 8 * (connectivity >= 3),
                binary_image=True,
                out_dtype=np.uint64,
            )
            if do_opening:
                cc = fastmorph.dilate(cc)
            cc[cc > 0] += np.max(output)
            output += cc
        return output

    def calculate_block_connected_components(
        block_index,
        affinities_idi: ImageDataInterface,
        connected_components_blockwise_idi: ImageDataInterface,
        neighborhood,
        adjacent_edge_bias,
        lr_bias_ratio,
        filter_val,
        mask: MasksFromConfig = None,
        connectivity=2,
        do_opening=True,
    ):
        padding_voxels = max(
            len(neighborhood),
            connected_components_blockwise_idi.chunk_shape[0] // 2,
        )
        padding = padding_voxels * connected_components_blockwise_idi.voxel_size[0]
        # add half a block of padding
        block = create_block_from_index(
            connected_components_blockwise_idi,
            block_index,
            padding=padding,
        )
        affinities = affinities_idi.to_ndarray_ts(block.read_roi)
        if mask:
            mask_block = mask.process_block(roi=block.read_roi)
            affinities &= mask_block[None, :, :, :]

        segmentation = MutexWatershed.mutex_watershed(
            affinities=affinities,
            neighborhood=neighborhood,
            adjacent_edge_bias=adjacent_edge_bias,
            lr_bias_ratio=lr_bias_ratio,
            filter_val=filter_val,
        )
        segmentation = MutexWatershed.instancewise_instance_segmentation(
            segmentation, connectivity=connectivity, do_opening=do_opening
        )

        global_id_offset = block_index * np.prod(
            block.full_block_size / connected_components_blockwise_idi.voxel_size[0],
            dtype=np.uint64,
        )
        segmentation[segmentation > 0] += global_id_offset
        connected_components_blockwise_idi.ds[block.write_roi] = segmentation[
            padding_voxels:-padding_voxels,
            padding_voxels:-padding_voxels,
            padding_voxels:-padding_voxels,
        ]

    def calculate_connected_components_blockwise(self):
        num_blocks = dask_util.get_num_blocks(self.affinities_idi, roi=self.roi)
        block_indexes = list(range(num_blocks))
        b = db.from_sequence(
            block_indexes,
            npartitions=guesstimate_npartitions(block_indexes, self.num_workers),
        ).map(
            MutexWatershed.calculate_block_connected_components,
            self.affinities_idi,
            self.connected_components_blockwise_idi,
            self.neighborhood,
            self.adjacent_edge_bias,
            self.lr_bias_ratio,
            self.filter_val,
            self.mask,
            self.connectivity,
            self.do_opening,
        )
        with dask_util.start_dask(
            self.num_workers,
            "calculate connected components",
            logger,
        ):
            with io_util.Timing_Messager("Calculating connected components", logger):
                dask_computer(b, self.num_workers, **self.compute_args)

    def get_connected_components(self):
        self.calculate_connected_components_blockwise()
        cc = ConnectedComponents(
            connected_components_blockwise_path=self.connected_components_blockwise_path
            + "/s0",
            output_path=self.output_path,
            num_workers=self.num_workers,
            minimum_volume_nm_3=self.minimum_volume_nm_3,
            maximum_volume_nm_3=self.maximum_volume_nm_3,
            delete_tmp=self.delete_tmp,
            connectivity=self.connectivity,
        )
        cc.merge_connected_components_across_blocks()
