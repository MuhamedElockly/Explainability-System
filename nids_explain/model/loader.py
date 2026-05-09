"""Load Keras model from .keras zip with Lambda-layer workaround."""

import json
import zipfile

import keras
import tensorflow as tf

# Caller must import nids_explain.core.tf_setup first (builtins.tf, unsafe deserialization).


def reduce_sum_axis1(x):
    return tf.reduce_sum(x, axis=1)


def load_and_patch_model(model_path):
    with zipfile.ZipFile(model_path, "r") as archive:
        config_data = json.loads(archive.read("config.json"))
        inner_config = config_data.get("config", config_data)
        for layer in inner_config.get("layers", []):
            if layer.get("class_name") == "Lambda":
                layer["config"]["output_shape"] = [128]
                function_cfg = layer["config"].get("function", {})
                if isinstance(function_cfg, dict) and function_cfg.get("class_name") == "__lambda__":
                    layer["config"]["function"] = {
                        "module": "builtins",
                        "class_name": "function",
                        "config": "reduce_sum_axis1",
                        "registered_name": "function",
                    }
                for key in ("output_shape_type", "module", "output_shape_module"):
                    layer["config"].pop(key, None)
    model = keras.Model.from_config(
        inner_config,
        custom_objects={"tf": tf, "reduce_sum_axis1": reduce_sum_axis1},
    )
    model.load_weights(model_path)
    return model
