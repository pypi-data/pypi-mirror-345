import os
import hashlib
from _hashlib import HASH
from typing import Dict, Optional, Union, Callable, Tuple

import numpy as np

import jax.numpy as jnp
from jax import Array
from bintensors import numpy, safe_open


def save(tensors: Dict[str, Array], metadata: Optional[Dict[str, str]] = None) -> bytes:
    """
    Saves a dictionary of tensors into raw bytes in bintensors format.

    Args:
        tensors (`Dict[str, Array]`):
            The incoming tensors. Tensors need to be contiguous and dense.
        metadata (`Dict[str, str]`, *optional*, defaults to `None`):
            Optional text only metadata you might want to save in your header.
            For instance it can be useful to specify more about the underlying
            tensors. This is purely informative and does not affect tensor loading.

    Returns:
        `bytes`: The raw bytes representing the format

    Example:

    ```python
    from bintensors.flax import save
    from jax import numpy as jnp

    tensors = {"embedding": jnp.zeros((512, 1024)), "attention": jnp.zeros((256, 256))}
    byte_data = save(tensors)
    ```
    """
    np_tensors = _jnp2np(tensors)
    return numpy.save(np_tensors, metadata=metadata)


def save_file(
    tensors: Dict[str, Array],
    filename: Union[str, os.PathLike],
    metadata: Optional[Dict[str, str]] = None,
) -> None:
    """
    Saves a dictionary of tensors into raw bytes in bintensors format.

    Args:
        tensors (`Dict[str, Array]`):
            The incoming tensors. Tensors need to be contiguous and dense.
        filename (`str`, or `os.PathLike`)):
            The filename we're saving into.
        metadata (`Dict[str, str]`, *optional*, defaults to `None`):
            Optional text only metadata you might want to save in your header.
            For instance it can be useful to specify more about the underlying
            tensors. This is purely informative and does not affect tensor loading.

    Returns:
        `None`

    Example:

    ```python
    from bintensors.flax import save_file
    from jax import numpy as jnp

    tensors = {"embedding": jnp.zeros((512, 1024)), "attention": jnp.zeros((256, 256))}
    save_file(tensors, "model.bintensors")
    ```
    """
    np_tensors = _jnp2np(tensors)
    return numpy.save_file(np_tensors, filename, metadata=metadata)


def load(data: bytes) -> Dict[str, Array]:
    """
    Loads a bintensors file into flax format from pure bytes.

    Args:
        data (`bytes`):
            The content of a bintensors file

    Returns:
        `Dict[str, Array]`: dictionary that contains name as key, value as `Array` on cpu

    Example:

    ```python
    from bintensors.flax import load

    file_path = "./my_folder/bert.bintensors"
    with open(file_path, "rb") as f:
        data = f.read()

    loaded = load(data)
    ```
    """
    flat = numpy.load(data)
    return _np2jnp(flat)


def load_file(filename: Union[str, os.PathLike]) -> Dict[str, Array]:
    """
    Loads a bintensors file into flax format.

    Args:
        filename (`str`, or `os.PathLike`)):
            The name of the file which contains the tensors

    Returns:
        `Dict[str, Array]`: dictionary that contains name as key, value as `Array`

    Example:

    ```python
    from bintensors.flax import load_file

    file_path = "./my_folder/bert.bt"
    loaded = load_file(file_path)
    ```
    """
    result = {}
    with safe_open(filename, framework="flax") as f:
        for k in f.offset_keys():
            result[k] = f.get_tensor(k)
    return result

def save_with_checksum(
    tensor_dict: Dict[str, Array],
    metadata: Optional[Dict[str, str]] = None,
    hasher: Callable[[bytes], HASH] = hashlib.sha1,
) -> Tuple[bytes, bytes]:
    """
    Saves a dictionary of tensors into raw bytes in bintensors format.

    Args:
        tensors (`Dict[str, np.ndarray]`):
            The incoming tensors. Tensors need to be contiguous and dense.
        metadata (`Dict[str, str]`, *optional*, defaults to `None`):
            Optional text only metadata you might want to save in your header.
            For instance it can be useful to specify more about the underlying
            tensors. This is purely informative and does not affect tensor loading.
        hasher (`Callable[[bytes], HASH]`):
            A hash is an object used to calculate a checksum of a string of information.


    Returns:
        `bytes`: The raw bytes representing the format

    Example:

    ```python
    from bintensors.flax import save_with_checksum
    import jax.numpy as jnp

    tensors = {"embedding": jnp.zeros((512, 1024)), "attention": jnp.zeros((256, 256))}
    checksum, byte_data = save_with_checksum(tensors)
    ```
    """
    np_tensors = _jnp2np(tensor_dict)
    return numpy.save_with_checksum(np_tensors, metadata, hasher)



def _np2jnp(numpy_dict: Dict[str, np.ndarray]) -> Dict[str, Array]:
    """
    Preform conversion from numpy storage backend to jax storage backend.

    Args:
        tensors (`Dict[str, np.ndarray]`):
            The incoming tensors. Tensors need to be contiguous and dense.

    Returns:
          `Dict[str, Array]`: dictionary that contains name as key, value as `Array`
    """
    for k, v in numpy_dict.items():
        numpy_dict[k] = jnp.array(v)
    return numpy_dict


def _jnp2np(jnp_dict: Dict[str, Array]) -> Dict[str, np.ndarray]:
    """
    Preform conversion from jax storage backend to numpy storage backend.

    Args:
        tensors (`Dict[str, Array]`):
            The incoming tensors. Tensors need to be contiguous and dense.
    Returns:
          `Dict[str, np.ndarray]`: dictionary that contains name as key, value as `np.ndarray`
    """
    for k, v in jnp_dict.items():
        jnp_dict[k] = np.asarray(v)
    return jnp_dict
