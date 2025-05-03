from typing import Any, Dict

import lerc
import numpy as np
from numcodecs import abc, registry
from numcodecs.compat import ensure_ndarray, ndarray_copy


class LERC(abc.Codec):
    """Codec to compress data with the LERC algorithm

    Args:
        precision (float): precision to preserve in the data
    """

    codec_id = 'lerc'
    dtype = np.float32

    def __init__(self, precision: float) -> None:
        self._precision = precision

    def encode(self, buf: np.ndarray) -> np.ndarray:
        """Encode data

        Args:
            buf (np.ndarray): the data to encode

        Returns:
            np.ndarray: encoded data
        """
        buf = ensure_ndarray(buf)

        shape = buf.shape
        data = buf.reshape((-1, shape[-2], shape[-1]), order='A')

        lerc_encode_result = lerc.encode(
            data,
            nValuesPerPixel=1,
            npValidMask=~np.isnan(data),
            nBytesHint=1,
            maxZErr=self._precision,
            bHasMask=True,
        )
        compressed_data: np.ndarray = lerc_encode_result[2]
        return compressed_data

    def decode(self, buf: np.ndarray, out: np.ndarray | None = None) -> np.ndarray:
        """Decode data

        Args:
            buf (np.ndarray): the data to decode
            out (np.ndarray): the array to write the output to

        Returns:
            np.ndarray: the decoded data
        """
        decompressed_data = lerc.decode(buf)
        data = decompressed_data[1]
        valid_mask = decompressed_data[2]

        if valid_mask is None:
            decoded_data = data
        else:
            # Use mask if there is one
            decoded_data = np.where(valid_mask, data, np.nan)

        if out is None:
            return decoded_data
        else:
            ndarray_copy(decoded_data, out)
        return out

    def get_config(self) -> Dict[str, Any]:
        """Get configuration to reconstruct this codec

        Returns:
            dict: with configuration to reconstruct this codec with
        """
        return {
            "id": str(self),
            "precision": self._precision,
        }

    def __repr__(self) -> str:
        """String representation

        Returns:
            str: this codec's id
        """
        return self.codec_id


def register_lerc_codec():
    registry.register_codec(LERC)
