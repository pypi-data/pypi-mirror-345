"""Initialises TensorFlow, monkey-patching if necessary."""

from packaging.version import Version

__all__ = ["init"]


def init():
    """Initialises tensorflow, monkey-patching if necessary."""

    import tensorflow
    import sys

    tf_ver = Version(tensorflow.__version__)

    if tf_ver < Version("2.8"):
        raise ImportError(
            f"The minimum TF version that mttf supports is 2.8. Your TF is {tf_ver}. "
            "Please upgrade."
        )

    # add mobilenet_v3_split module
    from mt.keras.applications import mobilenet_v3_split, mobilevit

    setattr(tensorflow.keras.applications, "mobilenet_v3_split", mobilenet_v3_split)
    setattr(tensorflow.keras.applications, "mobilevit", mobilevit)
    sys.modules["tensorflow.keras.applications.mobilenet_v3_split"] = mobilenet_v3_split
    sys.modules["tensorflow.keras.applications.mobilevit"] = mobilevit
    setattr(
        tensorflow.keras.applications,
        "MobileNetV3Split",
        mobilenet_v3_split.MobileNetV3Split,
    )

    from mt.keras.layers import Identical, Upsize2D, Downsize2D

    setattr(tensorflow.keras.layers, "Identical", Identical)
    setattr(tensorflow.keras.layers, "Upsize2D", Upsize2D)
    setattr(tensorflow.keras.layers, "Downsize2D", Downsize2D)

    return tensorflow


init()
