import bow_data
import logging
from typing import Any, Tuple, Type, Union,  List, Optional

def create_logger(name, level) -> logging.Logger:
    logger = logging.getLogger(name)
    if not len(logger.handlers):
        formatter = logging.Formatter('[ %(levelname)-5s - {:10} ] %(asctime)s - %(message)s'.format(name))
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)

        logger.addHandler(ch)
        logger.setLevel(level)

    return logger

codec_log = create_logger("Codec", logging.INFO)

def decode_data(sample: bow_data.DataMessage) -> (Union[
            bow_data.ImageSamples,
            bow_data.AudioSamples,
            bow_data.MotorSample,
            bow_data.ProprioceptionSample,
            bow_data.StringSample,
            bow_data.BlobSample,
            bow_data.Float32Array,
            bow_data.Int64Array,
            bow_data.InteroceptionSample,
            bow_data.ExteroceptionSample,
            None,
    ]):

    if sample.data_type == bow_data.DataMessage.IMAGE:
        return bow_data.ImageSamples().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.AUDIO:
        return bow_data.AudioSamples().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.STRING:
        return bow_data.StringSample().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.FLOAT32ARR:
        return bow_data.Float32Array().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.INT64ARR:
        return bow_data.Int64Array().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.COMMAND:
        return bow_data.Command().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.MOTOR:
        return bow_data.MotorSample().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.BLOB:
        return bow_data.BlobSample().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.PROPRIOCEPTION:
        return bow_data.ProprioceptionSample().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.TACTILE:
        tactile_samples = bow_data.TactileSamples().FromString(sample.data)
        tactile_list = []
        for frame in tactile_samples.Samples:
            tactile_list.append(frame)
        return tactile_list

    elif sample.data_type == bow_data.DataMessage.EXTEROCEPTION:
        return bow_data.ExteroceptionSample().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.INTEROCEPTION:
        return bow_data.InteroceptionSample().FromString(sample.data)

    else:
        codec_log.info("decoding {} datatype unhandled".format(sample.data_type))
        return None


def encode_data(sample: Union[
                                bow_data.ImageSample,
                                bow_data.ImageSamples,
                                List[bow_data.ImageSample],
                                bow_data.AudioSample,
                                bow_data.AudioSamples,
                                List[bow_data.AudioSample],
                                bow_data.TactileSamples,
                                bow_data.TactileSample,
                                List[bow_data.TactileSample],
                                bow_data.ProprioceptionSample,
                                bow_data.MotorSample,
                                bow_data.StringSample,
                                bow_data.BlobSample,
                                bow_data.Int64Array,
                                bow_data.Float32Array,
                                bow_data.Command,
                                bow_data.InteroceptionSample,
                                bow_data.ExteroceptionSample,
                                str,
                                List[float],
                                List[int]]
                ):
    encoded_dtype=None
    encoded_sample=None
    if isinstance(sample, list):
        if isinstance(sample[0], float):
            encoded_sample = bow_data.Float32Array(Data=sample).SerializeToString()
            encoded_dtype = bow_data.DataMessage.FLOAT32ARR

        elif isinstance(sample[0], int):
            encoded_sample = bow_data.Int64Array(Data=sample).SerializeToString()
            encoded_dtype = bow_data.DataMessage.INT64ARR

        elif isinstance(sample[0], bow_data.ImageSample):
            image_samples = bow_data.ImageSamples()
            for s in sample:
                image_samples.Samples.append(s)

            encoded_sample = image_samples.SerializeToString()
            encoded_dtype = bow_data.DataMessage.IMAGE

        elif isinstance(sample[0], bow_data.AudioSamples):
            audio_samples = bow_data.AudioSamples()
            for s in sample:
                audio_samples.Samples.append(s)

            encoded_sample = audio_samples.SerializeToString()
            encoded_dtype = bow_data.DataMessage.AUDIO

        elif isinstance(sample[0], bow_data.TactileSamples):
            tactile_samples = bow_data.TactileSamples()
            for s in sample:
                tactile_samples.Samples.append(s)

            encoded_sample = tactile_samples.SerializeToString()
            encoded_dtype = bow_data.DataMessage.AUDIO

        else:
            codec_log.error("Encode Data: list of {} data type is unsupported".format(type(sample[0])))
            return None, None, 0

    elif isinstance(sample, bow_data.ImageSample):
        image_samples = bow_data.ImageSamples()
        image_samples.Samples.append(sample)

        encoded_sample = image_samples.SerializeToString()
        encoded_dtype = bow_data.DataMessage.IMAGE

    elif isinstance(sample, bow_data.ImageSamples):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.IMAGE

    elif isinstance(sample, bow_data.AudioSample):
        audio_samples = bow_data.AudioSamples()
        audio_samples.Samples.append(sample)

        encoded_sample = audio_samples.SerializeToString()
        encoded_dtype = bow_data.DataMessage.AUDIO

    elif isinstance(sample, bow_data.AudioSamples):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.AUDIO

    elif isinstance(sample, str):
        encoded_sample = bow_data.StringSample(Data=sample).SerializeToString()
        encoded_dtype = bow_data.DataMessage.STRING

    elif isinstance(sample, bow_data.MotorSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.MOTOR

    elif isinstance(sample, bow_data.BlobSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.BLOB

    elif isinstance(sample, bow_data.ProprioceptionSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.PROPRIOCEPTION

    elif isinstance(sample, bow_data.TactileSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.TACTILE

    elif isinstance(sample, bow_data.Command):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.COMMAND

    elif isinstance(sample, bow_data.Int64Array):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.INT64ARR

    elif isinstance(sample, bow_data.Float32Array):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.FLOAT32ARR

    elif isinstance(sample, bow_data.StringSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.STRING

    elif isinstance(sample, bow_data.InteroceptionSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.INTEROCEPTION

    elif isinstance(sample, bow_data.ExteroceptionSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.EXTEROCEPTION

    else:
        codec_log.error("Encode Data: {} data type is unsupported".format(type(sample)))
        return None, None, 0

    # type: (Tuple[Optional[bow_data.DataMessage.DataType], Optional[str], int])
    return encoded_dtype, encoded_sample, len(encoded_sample)

class BaseChannel:
    def __init__(self, name: str, get_func: Any, set_func: Any) -> None:
        self.open = False
        self.channel_name = name
        self.get_func = get_func
        self.set_func = set_func

    def is_open(self) -> bool:
        return self.open

    def get(self, blocking: bool) -> Tuple[Union[Any, None], bow_data.Error]:
        if self.open:
            return self.get_func(self.channel_name, blocking)
        else:
            err = bow_data.Error()
            err.Success = False
            err.Code = -1
            err.Description = "Channel not open"
            return None, err

    def set(self, sample: Any) -> bow_data.Error:
        return self.set_func(self.channel_name, sample)

class ChannelImageSamples(BaseChannel):
    def get(self, blocking: bool) -> Tuple[Union[bow_data.ImageSamples, None], bow_data.Error]:
        return super().get(blocking)

    def set(self, sample: bow_data.ImageSamples) -> bow_data.Error:
        return super().set(sample)

class ChannelAudioSamples(BaseChannel):
    def get(self, blocking: bool) -> Tuple[Union[bow_data.AudioSamples, None], bow_data.Error]:
        return super().get(blocking)

    def set(self, sample: bow_data.AudioSamples) -> bow_data.Error:
        return super().set(sample)

class ChannelTactileSamples(BaseChannel):
    def get(self, blocking: bool) -> Tuple[Union[bow_data.TactileSamples, None], bow_data.Error]:
        return super().get(blocking)

    def set(self, sample: bow_data.TactileSamples) -> bow_data.Error:
        return super().set(sample)

class ChannelProprioceptionSample(BaseChannel):
    def get(self, blocking: bool) -> Tuple[Union[bow_data.ProprioceptionSample, None], bow_data.Error]:
        return super().get(blocking)

    def set(self, sample: bow_data.ProprioceptionSample) -> bow_data.Error:
        return super().set(sample)

class ChannelMotorSample(BaseChannel):
    def get(self, blocking: bool) -> Tuple[Union[bow_data.MotorSample, None], bow_data.Error]:
        return super().get(blocking)

    def set(self, sample: bow_data.MotorSample) -> bow_data.Error:
        return super().set(sample)

class ChannelStringSample(BaseChannel):
    def get(self, blocking: bool) -> Tuple[Union[bow_data.StringSample, None], bow_data.Error]:
        return super().get(blocking)

    def set(self, sample: bow_data.StringSample) -> bow_data.Error:
        return super().set(sample)

class ChannelInteroceptionSample(BaseChannel):
    def get(self, blocking: bool) -> Tuple[Union[bow_data.InteroceptionSample, None], bow_data.Error]:
        return super().get(blocking)

    def set(self, sample: bow_data.InteroceptionSample) -> bow_data.Error:
        return super().set(sample)

class ChannelExteroceptionSample(BaseChannel):
    def get(self, blocking: bool) -> Tuple[Union[bow_data.ExteroceptionSample, None], bow_data.Error]:
        return super().get(blocking)

    def set(self, sample: bow_data.ExteroceptionSample) -> bow_data.Error:
        return super().set(sample)