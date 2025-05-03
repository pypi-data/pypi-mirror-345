# wandas/io/wav_io.py

import os
from typing import TYPE_CHECKING, Optional

import numpy as np
from scipy.io import wavfile

if TYPE_CHECKING:
    from ..frames.channel import ChannelFrame


def read_wav(filename: str, labels: Optional[list[str]] = None) -> "ChannelFrame":
    """
    Read a WAV file and create a ChannelFrame object.

    Parameters
    ----------
    filename : str
        Path to the WAV file.
    labels : list of str, optional
        Labels for each channel.

    Returns
    -------
    ChannelFrame
        ChannelFrame object containing the audio data.
    """
    from wandas.frames.channel import ChannelFrame

    # データの読み込み
    sampling_rate, data = wavfile.read(filename, mmap=True)

    # データを(num_channels, num_samples)形状のNumPy配列に変換
    if data.ndim == 1:
        # モノラル：(samples,) -> (1, samples)
        data = np.expand_dims(data, axis=0)
    else:
        # ステレオ：(samples, channels) -> (channels, samples)
        data = data.T

    # NumPy配列からChannelFrameを作成
    channel_frame = ChannelFrame.from_numpy(
        data=data,
        sampling_rate=sampling_rate,
        label=os.path.basename(filename),
        ch_labels=labels,
    )

    return channel_frame


def write_wav(filename: str, target: "ChannelFrame") -> None:
    """
    Write a ChannelFrame object to a WAV file.

    Parameters
    ----------
    filename : str
        Path to the WAV file.
    target : ChannelFrame
        ChannelFrame object containing the data to write.

    Raises
    ------
    ValueError
        If target is not a ChannelFrame object.
    """
    from wandas.frames.channel import ChannelFrame

    if not isinstance(target, ChannelFrame):
        raise ValueError("target must be a ChannelFrame object.")

    # ChannelFrameのsaveメソッドを使用
    target.save(filename)
