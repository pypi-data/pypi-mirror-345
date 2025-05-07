import binascii
import struct
from typing import Any, Iterable

import asphodel

from .device_info import DeviceInfo


def convert_unit_type(unit_type: int) -> str:
    try:
        return asphodel.unit_type_names[unit_type]
    except IndexError:
        return str(unit_type)


def convert_setting(setting: asphodel.AsphodelSettingInfo,
                    nvm: bytes) -> dict[str, Any]:
    try:
        t = asphodel.setting_type_names[setting.setting_type]
    except IndexError:
        t = str(setting.setting_type)

    result = {
        'name': setting.name.decode("UTF-8"),
        'setting_type': t,
    }

    length = setting.default_bytes_length
    default_bytes = bytes(setting.default_bytes[0:length])

    if t in ("SETTING_TYPE_BYTE", "SETTING_TYPE_CHANNEL_TYPE",
             "SETTING_TYPE_UNIT_TYPE"):
        s_byte = setting.u.byte_setting
        if len(default_bytes) == 1:
            result['default'] = default_bytes[0]
        else:
            result['default'] = None
        byte_offset = s_byte.nvm_word * 4 + s_byte.nvm_word_byte
        result['value'] = struct.unpack_from(">B", nvm, byte_offset)[0]
    elif t == "SETTING_TYPE_BOOLEAN":
        s_byte = setting.u.byte_setting
        if len(default_bytes) == 1:
            result['default'] = bool(default_bytes[0])
        else:
            result['default'] = None
        byte_offset = s_byte.nvm_word * 4 + s_byte.nvm_word_byte
        result['value'] = struct.unpack_from(">?", nvm, byte_offset)[0]
    elif t == "SETTING_TYPE_BYTE_ARRAY":
        s_barray = setting.u.byte_array_setting
        result['default'] = default_bytes.hex(sep=",")
        length_byte_offset = (s_barray.length_nvm_word * 4 +
                              s_barray.length_nvm_word_byte)
        length = struct.unpack_from(">B", nvm, length_byte_offset)[0]
        if length > s_barray.maximum_length:
            length = s_barray.maximum_length
        result['maximum_length'] = s_barray.maximum_length
        fmt = ">{}s".format(length)
        value = struct.unpack_from(fmt, nvm, s_barray.nvm_word * 4)[0]
        result['value'] = value.hex(sep=",")
    elif t == "SETTING_TYPE_STRING":
        s_str = setting.u.string_setting
        try:
            result['default'] = default_bytes.decode("UTF-8")
        except UnicodeDecodeError:
            result['default'] = None
        result['maximum_length'] = s_str.maximum_length
        fmt = ">{}s".format(s_str.maximum_length)
        raw = struct.unpack_from(fmt, nvm, s_str.nvm_word * 4)[0]
        raw = raw.split(b'\x00', 1)[0]
        raw = raw.split(b'\xff', 1)[0]
        try:
            result['value'] = raw.decode("UTF-8")
        except UnicodeDecodeError:
            result['value'] = None
    elif t == "SETTING_TYPE_INT32":
        s_int32 = setting.u.int32_setting
        if len(default_bytes) == 4:
            result['default'] = struct.unpack_from(">i", default_bytes, 0)[0]
        else:
            result['default'] = None
        result['minimum'] = s_int32.minimum
        result['maximum'] = s_int32.maximum
        result['value'] = struct.unpack_from(
            ">i", nvm, s_int32.nvm_word * 4)[0]
    elif t == "SETTING_TYPE_INT32_SCALED":
        s_scaled = setting.u.int32_scaled_setting
        if len(default_bytes) == 4:
            result['default'] = struct.unpack_from(">i", default_bytes, 0)[0]
        else:
            result['default'] = None
        result['minimum'] = s_scaled.minimum
        result['maximum'] = s_scaled.maximum
        result['unit_type'] = convert_unit_type(s_scaled.unit_type)
        result['scale'] = s_scaled.scale
        result['offset'] = s_scaled.offset
        result['value'] = struct.unpack_from(
            ">i", nvm, s_scaled.nvm_word * 4)[0]
    elif t == "SETTING_TYPE_FLOAT":
        s_float = setting.u.float_setting
        if len(default_bytes) == 4:
            result['default'] = struct.unpack_from(">f", default_bytes, 0)[0]
        else:
            result['default'] = None
        result['minimum'] = s_float.minimum
        result['maximum'] = s_float.maximum
        result['unit_type'] = convert_unit_type(s_float.unit_type)
        result['scale'] = s_float.scale
        result['offset'] = s_float.offset
        result['value'] = struct.unpack_from(
            ">f", nvm, s_float.nvm_word * 4)[0]
    elif t == "SETTING_TYPE_FLOAT_ARRAY":
        s_farray = setting.u.float_array_setting

        if len(default_bytes) % 4 == 0:
            fmt = ">{}f".format(len(default_bytes) // 4)
            result['default'] = struct.unpack_from(fmt, default_bytes, 0)
        else:
            result['default'] = None
        result['minimum'] = s_farray.minimum
        result['maximum'] = s_farray.maximum
        result['unit_type'] = convert_unit_type(s_farray.unit_type)
        result['scale'] = s_farray.scale
        result['offset'] = s_farray.offset

        length_byte_offset = (s_farray.length_nvm_word * 4 +
                              s_farray.length_nvm_word_byte)
        length = struct.unpack_from(">B", nvm,
                                    length_byte_offset)[0]
        if length > s_farray.maximum_length:
            length = s_farray.maximum_length
        result['maximum_length'] = s_farray.maximum_length
        fmt = ">{}f".format(length)
        result['value'] = struct.unpack_from(fmt, nvm, s_farray.nvm_word * 4)
    elif t == "SETTING_TYPE_CUSTOM_ENUM":
        s_ce = setting.u.custom_enum_setting

        if len(default_bytes) == 1:
            result['default'] = default_bytes[0]
        else:
            result['default'] = None
        byte_offset = s_ce.nvm_word * 4 + s_ce.nvm_word_byte
        result['value'] = struct.unpack_from(">B", nvm, byte_offset)[0]

        result['custom_enum_index'] = s_ce.custom_enum_index
    else:
        # fallback
        result['default'] = default_bytes.hex(sep=",")

    return result


def convert_ctrl_var(name: str, ctrl_var: asphodel.CtrlVarInfo,
                     value: int) -> dict[str, Any]:
    return {
        "name": name,
        "unit_type": convert_unit_type(ctrl_var.unit_type),
        "minimum": ctrl_var.minimum,
        "maximum": ctrl_var.maximum,
        "scale": ctrl_var.scale,
        "offset": ctrl_var.offset,
        "value": value,
    }


def configure_setting(setting: asphodel.AsphodelSettingInfo, value: Any,
                      device_info: DeviceInfo, nvm: bytearray) -> None:
    if setting.setting_type in (asphodel.SETTING_TYPE_BYTE,
                                asphodel.SETTING_TYPE_CHANNEL_TYPE,
                                asphodel.SETTING_TYPE_UNIT_TYPE):
        s_byte = setting.u.byte_setting
        byte_offset = s_byte.nvm_word * 4 + s_byte.nvm_word_byte
        struct.pack_into(">B", nvm, byte_offset, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_BOOLEAN:
        s_byte = setting.u.byte_setting
        byte_offset = s_byte.nvm_word * 4 + s_byte.nvm_word_byte
        struct.pack_into(">?", nvm, byte_offset, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_BYTE_ARRAY:
        s_barray = setting.u.byte_array_setting
        length_byte_offset = (s_barray.length_nvm_word * 4 +
                              s_barray.length_nvm_word_byte)
        b = binascii.a2b_hex(value.replace(",", ""))
        if len(b) > s_barray.maximum_length:
            b = b[0:s_barray.maximum_length]
        struct.pack_into(">B", nvm, length_byte_offset, len(b))
        fmt = ">{}s".format(len(b))
        struct.pack_into(fmt, nvm, s_barray.nvm_word * 4, b)
    elif setting.setting_type == asphodel.SETTING_TYPE_STRING:
        s_str = setting.u.string_setting
        fmt = ">{}s".format(s_str.maximum_length)
        b = value.encode("UTF-8")
        struct.pack_into(fmt, nvm, s_str.nvm_word * 4, b)
    elif setting.setting_type == asphodel.SETTING_TYPE_INT32:
        s_int32 = setting.u.int32_setting
        struct.pack_into(">i", nvm, s_int32.nvm_word * 4, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_INT32_SCALED:
        s_scaled = setting.u.int32_scaled_setting
        struct.pack_into(">i", nvm, s_scaled.nvm_word * 4, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_FLOAT:
        s = setting.u.float_setting
        struct.pack_into(">f", nvm, s.nvm_word * 4, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_FLOAT_ARRAY:
        s_farray = setting.u.float_array_setting
        length_byte_offset = (s_farray.length_nvm_word * 4 +
                              s_farray.length_nvm_word_byte)
        if len(value) > s_farray.maximum_length:
            value = value[0:s_farray.maximum_length]
        struct.pack_into(">B", nvm, length_byte_offset, len(value))
        fmt = ">{}f".format(len(value))
        struct.pack_into(fmt, nvm, s_farray.nvm_word * 4, *value)
    elif setting.setting_type == asphodel.SETTING_TYPE_CUSTOM_ENUM:
        s_ce = setting.u.custom_enum_setting
        byte_offset = s_ce.nvm_word * 4 + s_ce.nvm_word_byte
        if isinstance(value, str):
            # look up the value
            e = device_info.custom_enums.get(s_ce.custom_enum_index, [])
            value = e.index(value)
        struct.pack_into(">B", nvm, byte_offset, value)
    else:
        raise ValueError("Bad setting type {}".format(setting.setting_type))


def configure_nvm(device_config: Iterable[tuple[str, Any]],
                  device_info: DeviceInfo,
                  nvm: bytes) -> bytes:
    nvm_array = bytearray(nvm)

    for key, value in device_config:
        setting_name = key.encode("UTF-8")
        for setting in device_info.settings:
            if setting.name == setting_name:
                configure_setting(setting, value, device_info, nvm_array)
        else:
            raise KeyError("No setting {}".format(key))

    return bytes(nvm_array)
