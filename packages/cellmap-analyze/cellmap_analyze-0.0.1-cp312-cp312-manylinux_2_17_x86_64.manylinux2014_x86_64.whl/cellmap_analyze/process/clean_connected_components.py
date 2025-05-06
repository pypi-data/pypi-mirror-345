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
import itertools
import os
from cellmap_analyze.util.mask_util import MasksFromConfig
import fastremap


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class CleanConnectedComponents:
    def __init__(
        self,
        input_path,
        output_path=None,
        mask_config=None,
        roi=None,
        minimum_volume_nm_3=0,
        maximum_volume_nm_3=np.inf,
        num_workers=10,
        mask_connectivity=2,
        connectivity=2,
        fill_holes=False,
        delete_tmp=True,
    ):
        self.input_path = input_path
        self.input_idi = ImageDataInterface(self.input_path)
        if roi is None:
            self.roi = self.input_idi.roi
        else:
            self.roi = roi

        self.voxel_size = self.input_idi.voxel_size

        self.output_path = output_path
        if self.output_path is None:
            output_path = self.input_path
            output_ds_name = get_name_from_path(output_path)
            output_ds_basepath = split_dataset_path(self.input_path)[0]
            self.output_path = f"{output_ds_basepath}/{output_ds_name}_cleaned"

        self.temp_block_info_path = self.output_path + "_blocks_tmp"

        # evaluate minimum_volume_nm_3 voxels if it is a string
        if type(minimum_volume_nm_3) == str:
            minimum_volume_nm_3 = float(minimum_volume_nm_3)
        if type(maximum_volume_nm_3) == str:
            maximum_volume_nm_3 = float(maximum_volume_nm_3)

        self.minimum_volume_voxels = minimum_volume_nm_3 / np.prod(self.voxel_size)
        self.maximum_volume_voxels = maximum_volume_nm_3 / np.prod(self.voxel_size)

        self.mask = None
        if mask_config:
            self.mask = MasksFromConfig(
                mask_config,
                output_voxel_size=self.voxel_size,
                connectivity=mask_connectivity,
            )

        self.connectivity = connectivity
        self.fill_holes = fill_holes
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
    def volume_filter_connected_ids(
        connected_ids, id_to_volume_dict, minimum_volume_voxels
    ):
        kept_ids = []
        removed_ids = []
        for current_connected_ids in connected_ids:
            volume = sum([id_to_volume_dict[id] for id in current_connected_ids])
            if volume >= minimum_volume_voxels:
                kept_ids.append(current_connected_ids)
            else:
                removed_ids.append(current_connected_ids)
        return kept_ids, removed_ids

    @staticmethod
    def get_connected_component_information_blockwise(
        block_index,
        connected_components_blockwise_idi: ImageDataInterface,
        mask: MasksFromConfig = None,
    ):
        try:
            block = create_block_from_index(
                connected_components_blockwise_idi,
                block_index,
            )
            data = connected_components_blockwise_idi.to_ndarray_ts(
                block.read_roi,
            )
            # need to get these premask since during relabeling we have to assing em to zero
            unique_ids = fastremap.unique(data)
            if mask:
                mask_block = mask.process_block(roi=block.read_roi)
                data *= mask_block

            # get information only from actual block(not including padding)
            id_to_volume_dict = ConnectedComponents.get_object_sizes(data)
            block.relabeling_dict = {id: 0 for id in unique_ids}
        except:
            raise Exception(
                f"Error in get_connected_component_information_blockwise {block_index}, {connected_components_blockwise_idi.voxel_size}"
            )
        return [block], id_to_volume_dict, set()

    @staticmethod
    def combine_id_to_volume_dicts(dict1, dict2):
        # make dict1 the larger dict
        if len(dict1) < len(dict2):
            dict1, dict2 = dict2, dict1

        dict1 = dict1.copy()
        for id, volume in dict2.items():
            dict1[id] = dict1.get(id, 0) + volume
        return dict1

    def get_connected_component_information(self):
        num_blocks = dask_util.get_num_blocks(self.input_idi, self.roi)
        block_indexes = list(range(num_blocks))
        b = db.from_sequence(
            block_indexes,
            npartitions=guesstimate_npartitions(block_indexes, self.num_workers),
        ).map(
            CleanConnectedComponents.get_connected_component_information_blockwise,
            self.input_idi,
            self.mask,
        )

        with dask_util.start_dask(
            self.num_workers,
            "calculate connected component information",
            logger,
        ):
            with io_util.Timing_Messager(
                "Calculating connected component information", logger
            ):
                bagged_results = dask_computer(b, self.num_workers, **self.compute_args)

        # moved this out of dask, seems fast enough without having to daskify
        with io_util.Timing_Messager("Combining bagged results", logger):
            blocks_with_dict, self.id_to_volume_dict, _ = (
                ConnectedComponents._combine_results(bagged_results)
            )

        self.blocks = [None] * num_blocks
        for block in blocks_with_dict:
            self.blocks[block.index] = block

    def get_final_connected_components(self):
        # make it a list of list to be consistence with connectedcomponents volume filter
        old_ids = [[id] for id in self.id_to_volume_dict.keys()]
        if self.minimum_volume_voxels > 0 or self.maximum_volume_voxels < np.inf:
            with io_util.Timing_Messager("Volume filter connected", logger):
                old_ids, _ = ConnectedComponents.volume_filter_connected_ids(
                    old_ids,
                    self.id_to_volume_dict,
                    self.minimum_volume_voxels,
                    self.maximum_volume_voxels,
                )

        del self.id_to_volume_dict

        # sort connected_ids by the minimum id in each connected component
        new_ids = list(range(1, len(old_ids) + 1))
        old_ids = list(itertools.chain(*old_ids))

        if len(new_ids) == 0:
            self.new_dtype = np.uint8
        else:
            self.new_dtype = np.min_scalar_type(max(new_ids))
            relabeling_dict = dict(zip(old_ids, new_ids))
            # update blockwise relabeing dicts
            for block in self.blocks:
                block.relabeling_dict = {
                    id: relabeling_dict.get(id, 0)
                    for id in block.relabeling_dict.keys()
                }
            del relabeling_dict

    def clean_connected_components(self):
        # get blockwise connected component information
        self.get_connected_component_information()
        # get final connected components necessary for relabeling, including volume filtering
        self.get_final_connected_components()
        # write out block information
        ConnectedComponents.write_out_block_objects(
            self.temp_block_info_path,
            self.blocks,
            self.num_local_threads_available,
            self.local_config,
            self.num_workers,
            self.compute_args,
            use_new_temp_dir=True,
        )
        ConnectedComponents.relabel_dataset(
            self.input_idi,
            self.output_path,
            self.blocks,
            self.roi,
            self.new_dtype,
            self.num_workers,
            self.compute_args,
            block_info_basepath=self.temp_block_info_path,
            mask=self.mask,
        )
        if self.delete_tmp:
            ConnectedComponents.delete_tmp_dataset(
                self.temp_block_info_path,
                self.blocks,
                self.num_workers,
                self.compute_args,
            )

        if self.fill_holes:
            from .fill_holes import FillHoles

            fh = FillHoles(
                input_path=self.output_path + "/s0",
                output_path=self.output_path + "_filled",
                num_workers=self.num_workers,
                roi=self.roi,
                connectivity=self.connectivity,
                delete_tmp=self.delete_tmp,
            )
            fh.fill_holes()
