"""Integration test for multiple tags."""
import random
import shutil
import sys
from copy import deepcopy

import pytest
import pytest_check as check

from cliconfig import (
    Config,
    create_processing_keep_property,
    create_processing_value,
    load_config,
    make_config,
    save_config,
)
from cliconfig.dict_routines import load_dict
from cliconfig.process_routines import merge_flat_processing


def test_multiple_tags() -> None:
    """Integration test for multiple tags."""
    sys_argv = sys.argv.copy()
    sys.argv = ["test_inte_multiple_tags.py"]
    config = make_config("tests/configs/integration/test1/main.yaml")
    expected_config = {
        "path_1": "tests/configs/integration/test1/sub1.yaml",
        "path_2": "tests/configs/integration/test1/sub2.yaml",
        "config1": {
            "param": 2,
            "param2": 1,
        },
        "config2": {
            "param": 2,
        },
        "config3": {
            "select": "config3.param1",
            "param1": 0,
        },
    }
    check.equal(config.dict, expected_config)
    config = merge_flat_processing(
        config,
        Config({"config2.param": 5.6}, []),
        preprocess_first=False,
    )
    with pytest.raises(
        ValueError, match="Key previously tagged with '@type:None|int'.*"
    ):
        config.process_list[3].endbuild(config)
    sys.argv = sys_argv


def test_multiple_tags2() -> None:
    """2nd integration test for multiple tags."""
    sys_argv = sys.argv.copy()
    sys.argv = [
        "test_inte_multiple_tags2.py",
        "--config",
        "[tests/configs/integration/test2/exp1.yaml, "
        "tests/configs/integration/test2/exp2.yaml]",
        "--train.n_epochs=20",
        "--train.optimizer.momentum=0",
        "--train.optimizer.type=Adam",
    ]

    def func_pos_enc_type(x: str) -> str:
        if x in ["absolute", "relative", "embed"]:
            return x
        raise ValueError(f"Invalid value for pos_enc_type: {x}")

    def func_optim_type(x: str) -> str:
        if x in ["SGD", "Adam"]:
            return x
        raise ValueError(f"Invalid value for optim_type: {x}")

    proc_pos_enc_type = create_processing_value(
        func_pos_enc_type,
        tag_name="pos_enc",
        order=20,
        persistent=True,
    )
    proc_optim_type = create_processing_value(
        func_optim_type,
        tag_name="optim_type",
        order=20,
        persistent=True,
    )
    proc_protect = create_processing_keep_property(
        func=lambda x: x,
        tag_name="protect",
        premerge_order=-15,
        postmerge_order=15,
    )
    proc_run_id = create_processing_value(
        lambda run_id: run_id if run_id is not None else random.randint(0, 1000000),
        regex="run_id.*",
    )
    config = make_config(
        "tests/configs/integration/test2/default.yaml",
        process_list=[proc_pos_enc_type, proc_optim_type, proc_protect, proc_run_id],
        add_default_processing=True,
    )
    expected_dict = {
        "project_name": "ImageClassif",
        "models": {
            "archi_name": "models.vit_b16",
            "vit_b16": {
                "pos_enc_type": "absolute",
                "attn_dropout": 0.2,
                "dropout": 0.1,
                "in_size": 512,
                "n_blocks": 12,
            },
        },
        "data": {
            "data_size": 512,
            "dataset_path": "../../mydata",
            "standardization": True,
            "augmentation": ["RandomHorizontalFlip", "RandomVerticalFlip"],
            "dataset_cfg_path": "tests/configs/integration/test2/data.yaml",
        },
        "train": {
            "n_epochs": 20,
            "optimizer": {
                "type": "Adam",
                "lr": 0.001,
                "momentum": 0,
            },
        },
        "metadata": {
            "exp_details": {
                "goal": "Test multiple processings",
                "config_folder": "tests/configs/integration/test2",
            }
        },
    }
    check.is_instance(config.dict["run_id"], int)
    config_dict = deepcopy(config.dict)
    del config_dict["run_id"]
    check.equal(config_dict, expected_dict)
    save_config(config, "tests/tmp/config.yaml")
    saved_dict = load_dict("tests/tmp/config.yaml")
    check.equal(
        saved_dict["data"]["augmentation@type:List[str]"],
        ["RandomHorizontalFlip", "RandomVerticalFlip"],
    )
    check.equal(
        saved_dict["models"]["archi_name@type:None|str@select"], "models.vit_b16"
    )
    check.equal(
        saved_dict["models"]["vit_b16"]["in_size@copy@type:int"], "data.data_size"
    )
    config = load_config(
        "tests/tmp/config.yaml",
        ["tests/configs/integration/test2/default.yaml"],
        config.process_list,
    )
    del config.dict["run_id"]
    check.equal(config.dict, expected_dict)
    with pytest.raises(ValueError, match="Key previously tagged with '@type:int.*"):
        config.process_list[7].endbuild(
            Config({"models.vit_b16.n_blocks": 5.6}, config.process_list)
        )
    with pytest.raises(
        ValueError, match="Found attempt to modify a key with '@copy' tag.*"
    ):
        merge_flat_processing(config, Config({"models.vit_b16.in_size": 224}, []))

    shutil.rmtree("tests/tmp")
    sys.argv = sys_argv
