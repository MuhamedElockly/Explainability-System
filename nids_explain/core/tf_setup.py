"""TensorFlow / Keras global setup (must be imported before model loading)."""

import builtins
import os
import warnings

import keras
import tensorflow as tf

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.filterwarnings("ignore")
builtins.tf = tf
keras.config.enable_unsafe_deserialization()
