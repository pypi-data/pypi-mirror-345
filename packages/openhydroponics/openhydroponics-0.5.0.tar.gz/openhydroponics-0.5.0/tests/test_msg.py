from pypostcard.types import List, deserialize, i16, i8, serialize, u16, u8
import pytest

from openhydroponics.msg import ArbitrationId


@pytest.mark.parametrize(
    "raw, arb",
    [
        (
            0x01800000,
            ArbitrationId(
                prio=False,
                dst=12,
                master=False,
                src=0,
                multiframe=False,
                msg_type=0,
                msg_id=0,
            ),
        ),
        (
            0x05000000,
            ArbitrationId(
                prio=False,
                dst=40,
                master=False,
                src=0,
                multiframe=False,
                msg_type=0,
                msg_id=0,
            ),
        ),
        (
            0x06800000,
            ArbitrationId(
                prio=False,
                dst=52,
                master=False,
                src=0,
                multiframe=False,
                msg_type=0,
                msg_id=0,
            ),
        ),
        (
            0x00004801,
            ArbitrationId(
                prio=False,
                dst=0,
                master=False,
                src=2,
                multiframe=False,
                msg_type=2,
                msg_id=1,
            ),
        ),
    ],
)
def test_arbitration(raw: int, arb: ArbitrationId):
    decoded_arb = ArbitrationId.decode(raw)
    assert decoded_arb == arb
    assert arb.encode() == raw
