import logging

from serde import serde
from pypostcard.types import f32, u8
from pypostcard.serde import from_postcard

from openhydroponics.net.msg import ActuatorOutput, EndpointClass
from openhydroponics.base import endpoint as EndpointBase

_LOG = logging.getLogger(__name__)


@serde
class ECConfigCalibration:
    value: f32


@serde
class ECConfigRaw:
    value: f32


@serde
class ECConfigCalibrationRaw:
    reference_low: f32
    raw_low: f32
    reference_high: f32
    raw_high: f32
    gain: u8


@serde
class ECConfigGain:
    value: u8


class ECEndpoint(EndpointBase.ECEndpoint):

    async def get_config(self, config: int):
        value = await self.node.get_config(self.endpoint_id, config)
        if not value:
            return {}
        if config == EndpointBase.ECConfigReadType.CALIBRATION:
            decoded: ECConfigCalibrationRaw = from_postcard(
                ECConfigCalibrationRaw, value
            )
            return {
                "reference_low": float(decoded.reference_low),
                "raw_low": float(decoded.raw_low),
                "reference_high": float(decoded.reference_high),
                "raw_high": float(decoded.raw_high),
                "gain": int(decoded.gain),
            }
        if config == EndpointBase.ECConfigReadType.RAW:
            decoded: ECConfigRaw = from_postcard(ECConfigRaw, value)
            return {"raw": float(decoded.value)}
        return {}

    async def set_config(self, config):
        if "high" in config and "low" in config:
            raise ValueError(
                "Cannot not set high and low at the same time, calibration will be wrong"
            )
        if (
            ("reference_low" in config)
            or ("raw_low" in config)
            or ("reference_high" in config)
            or ("raw_high" in config)
            or ("gain" in config)
        ):
            if (
                ("reference_low" not in config)
                or ("raw_low" not in config)
                or ("reference_high" not in config)
                or ("raw_high" not in config)
                or ("gain" not in config)
            ):
                raise ValueError(
                    "Missing configuration values. These must be set: reference_low, raw_low, reference_high, raw_high, and gain."
                )
            return await self.node.set_config(
                self.endpoint_id,
                EndpointBase.ECConfigWriteType.RAW,
                ECConfigCalibrationRaw(
                    reference_low=f32(config["reference_low"]),
                    raw_low=f32(config["raw_low"]),
                    reference_high=f32(config["reference_high"]),
                    raw_high=f32(config["raw_high"]),
                    gain=u8(config["gain"]),
                ),
            )
        if "high" in config:
            return await self.node.set_config(
                self.endpoint_id,
                EndpointBase.ECConfigWriteType.HIGH,
                ECConfigCalibration(value=f32(config["high"])),
            )
        if "low" in config:
            return await self.node.set_config(
                self.endpoint_id,
                EndpointBase.ECConfigWriteType.LOW,
                ECConfigCalibration(value=f32(config["low"])),
            )
        if "gain" in config:
            return await self.node.set_config(
                self.endpoint_id,
                EndpointBase.ECConfigWriteType.GAIN,
                ECConfigGain(value=u8(config["gain"])),
            )


@serde
class PHConfigCalibration:
    value: f32


class PHEndpoint(EndpointBase.PHEndpoint):

    async def set_config(self, config) -> bool:
        calibrations = 0
        if "high" in config:
            calibrations += 1
        if "low" in config:
            calibrations += 1
        if "mid" in config:
            calibrations += 1
        if calibrations > 1:
            raise ValueError(
                "Cannot not set high, low and mid at the same time, calibration will be wrong"
            )
        if "high" in config:
            return await self.node.set_config(
                self.endpoint_id,
                EndpointBase.PHConfigType.HIGH,
                PHConfigCalibration(value=f32(config["high"])),
            )
        if "low" in config:
            return await self.node.set_config(
                self.endpoint_id,
                EndpointBase.PHConfigType.LOW,
                PHConfigCalibration(value=f32(config["low"])),
            )
        if "mid" in config:
            return await self.node.set_config(
                self.endpoint_id,
                EndpointBase.PHConfigType.MID,
                PHConfigCalibration(value=f32(config["mid"])),
            )


class VariableOutputEndpoint(EndpointBase.VariableOutputEndpoint):
    async def set(self, value: float):
        self.node.send_msg(
            ActuatorOutput(endpoint_id=u8(self.endpoint_id), value=f32(value))
        )


def get_endpoint_input_class(
    endpoint_input_class: EndpointBase.EndpointInputClass,
) -> EndpointBase.InputEndpoint:
    if endpoint_input_class == EndpointBase.EndpointInputClass.Temperature:
        return EndpointBase.TemperatureEndpoint
    if endpoint_input_class == EndpointBase.EndpointInputClass.Humidity:
        return EndpointBase.HumidityEndpoint
    if endpoint_input_class == EndpointBase.EndpointInputClass.EC:
        return ECEndpoint
    if endpoint_input_class == EndpointBase.EndpointInputClass.PH:
        return PHEndpoint
    return EndpointBase.InputEndpoint


def get_endpoint_output_class(
    endpoint_output_class: EndpointBase.EndpointOutputClass,
) -> EndpointBase.OutputEndpoint:
    if endpoint_output_class == EndpointBase.EndpointOutputClass.Variable:
        return VariableOutputEndpoint
    return EndpointBase.OutputEndpoint


def get_endpoint_class(
    endpoint_class: EndpointBase.EndpointClass, endpoint_sub_class
) -> EndpointBase.Endpoint:
    if endpoint_class == EndpointClass.Input:
        return get_endpoint_input_class(endpoint_sub_class)
    if endpoint_class == EndpointClass.Output:
        return get_endpoint_output_class(endpoint_sub_class)
    return EndpointBase.Endpoint
