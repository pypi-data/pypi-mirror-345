import binascii
import json
import lzma
import struct
from typing import Any, Iterable

import asphodel


def decode_header(header_bytes: bytes) -> dict[str, Any]:
    try:
        header_str = header_bytes.decode("UTF-8")
        header = json.loads(header_str)
    except Exception:
        raise Exception("Could not parse file header!")

    # convert the JSON info back into an actual Asphodel structure
    all_streams = [asphodel.AsphodelStreamInfo.from_json_obj(s)
                   for s in header['streams']]
    all_channels = [asphodel.AsphodelChannelInfo.from_json_obj(c)
                    for c in header['channels']]

    header['streams'] = all_streams
    header['channels'] = all_channels

    # stream rate info
    stream_rate_info = []
    for values in header.get('stream_rate_info', []):
        # fix floats getting converted to strings in older files
        rate_values: list[Any] = [
            float(v) if isinstance(v, str) else v for v in values]

        if rate_values is not None:
            stream_rate_info.append(asphodel.StreamRateInfo(*rate_values))
        else:
            stream_rate_info.append(None)
    header['stream_rate_info'] = stream_rate_info

    # supplies
    supplies = []
    for name, values in header.get('supplies', []):
        # fix floats getting converted to strings in older files
        supply_values: list[Any] = [
            float(v) if isinstance(v, str) else v for v in values]

        supplies.append((name, asphodel.SupplyInfo(*supply_values)))
    header['supplies'] = supplies

    # control variables
    ctrl_vars = []
    for name, values, setting in header.get('ctrl_vars', []):
        # fix floats getting converted to strings in older files
        ctrl_values: list[Any] = [
            float(v) if isinstance(v, str) else v for v in values]

        ctrl_vars.append((name, asphodel.CtrlVarInfo(*ctrl_values), setting))
    header['ctrl_vars'] = ctrl_vars

    # nvm
    header['nvm'] = binascii.a2b_hex(header['nvm'])

    # custom enums: need to convert keys back from strings to ints
    custom_enums = {int(k): v for k, v in header['custom_enums'].items()}
    header['custom_enums'] = custom_enums

    # settings
    settings = []
    for setting_str in header['settings']:
        try:
            setting = asphodel.AsphodelSettingInfo.from_str(setting_str)
        except Exception:
            setting = None
        settings.append(setting)
    header['settings'] = settings

    return header


def load_batch(
        files: Iterable[str]) -> tuple[dict[float, str], dict[str, Any]]:
    """
    returns (file_times, header) where file_times is a dictonary of
    timestamp:filename
    * header is the dictionary loaded from the file's JSON data, with
      appropriate conversions applied to Asphodel struct data.
    * filename is the absolute path to the file location.
    * timestamp is the floating point time of the first packet in the file
    """

    first_file = True

    file_times: dict[float, str] = {}

    for filename in files:
        with lzma.LZMAFile(filename, "rb") as f:
            # read the header
            header_leader = struct.unpack(">dI", f.read(12))
            header_timestamp = header_leader[0]
            header_bytes = f.read(header_leader[1])

            if len(header_bytes) == 0:
                raise Exception("Empty header in {}!".format(filename))

            # read the first packet's datetime
            first_packet_timestamp: float = struct.unpack(">d", f.read(8))[0]

            if first_file:
                first_file = False
                first_header_bytes = header_bytes
                first_header_timestamp = header_timestamp

                header = decode_header(header_bytes)
            else:
                if (first_header_bytes != header_bytes or
                        first_header_timestamp != header_timestamp):
                    # error
                    raise Exception(
                        "Headers do not match on {}!".format(filename))

            if first_packet_timestamp in file_times:
                f2 = file_times[first_packet_timestamp]
                m = f"Timestamps overlap between files {filename} and {f2}"
                raise Exception(m)

            file_times[first_packet_timestamp] = filename

    return (file_times, header)


def load_batches(
        files: Iterable[str]) -> list[tuple[dict[float, str], dict[str, Any]]]:
    """
    returns [(file_times, header)] where file_times is a dictonary of
    timestamp:filename
    * header is the dictionary loaded from the file's JSON data, with
      appropriate conversions applied to Asphodel struct data.
    * filename is the absolute path to the file location.
    * timestamp is the floating point time of the first packet in the file
    """

    batches = {}  # (header_timestamp, header_bytes):file_times

    for filename in files:
        with lzma.LZMAFile(filename, "rb") as f:
            # read the header
            header_leader = struct.unpack(">dI", f.read(12))
            header_timestamp: float = header_leader[0]
            header_bytes = f.read(header_leader[1])

            if len(header_bytes) == 0:
                raise Exception("Empty header in {}!".format(filename))

            # read the first packet's datetime
            first_packet_timestamp = struct.unpack(">d", f.read(8))[0]

            header_key = (header_timestamp, header_bytes)
            if header_key not in batches:
                # first file in this batch
                file_times = {first_packet_timestamp: filename}
                batches[header_key] = file_times
            else:
                file_times = batches[header_key]
                if first_packet_timestamp in file_times:
                    f2 = file_times[first_packet_timestamp]
                    m = f"Timestamps overlap between files {filename} and {f2}"
                    raise Exception(m)
                file_times[first_packet_timestamp] = filename

    results: list[tuple[dict[float, str], dict[str, Any]]] = []
    for (_timestamp, header_bytes), file_times in sorted(batches.items()):
        header = decode_header(header_bytes)
        results.append((file_times, header))

    return results


def parse_packets(filename: str) -> Iterable[tuple[bytes, float]]:
    """
    yields (packet_bytes, timestamp) for each group of packet_bytes in
    the file
    * packet_bytes is a group of packets collected at the same time, always a
      multiple of the device's stream packet size
    * timestamp is the floating point time for when the bytes were collected
    """

    packet_leader = struct.Struct(">dI")

    with lzma.LZMAFile(filename, "rb") as f:
        # read the header
        header_leader = struct.unpack(">dI", f.read(12))
        f.read(header_leader[1])

        while True:
            leader_bytes = f.read(packet_leader.size)

            if not leader_bytes:
                return  # file is finished

            leader = packet_leader.unpack(leader_bytes)
            packet_timestamp: float = leader[0]
            packet_bytes = f.read(leader[1])

            yield (packet_bytes, packet_timestamp)


def create_decoder(
        header: dict[str, Any]) -> asphodel.AsphodelNativeDeviceDecoder:
    info_list = []
    for stream_id in header['streams_to_activate']:
        stream = header['streams'][stream_id]
        indexes = stream.channel_index_list[0:stream.channel_count]

        if len(indexes) > 0:
            channel_list = [header['channels'][ch_id] for ch_id in indexes]
            info_list.append((stream_id, stream, channel_list))

    # create the device decoder
    decoder = asphodel.nativelib.create_device_decoder(
        info_list, header['stream_filler_bits'], header['stream_id_bits'])

    return decoder
