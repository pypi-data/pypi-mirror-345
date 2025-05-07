#!/usr/bin/env python3
import ast
import binascii
from collections import namedtuple
from ctypes import (
    addressof, byref, c_char_p, c_double, c_float, c_int, c_int8, c_int16,
    c_int32, c_uint, c_uint8, c_uint16, c_uint32, c_uint64, c_size_t, c_void_p,
    cast, cdll, CFUNCTYPE, create_string_buffer, POINTER, pointer, Structure,
    Union,
)
from ctypes.util import find_library
import functools
import os
import string
import sys
import time
import threading
from typing import Optional
import weakref


try:
    from .version import version as __version__
except ImportError:
    __version__ = "UNKNOWN"


# defines from the protocol header file that don't fit elsewhere
ASPHODEL_PROTOCOL_TYPE_BASIC = 0x00
ASPHODEL_PROTOCOL_TYPE_RF_POWER = 0x01
ASPHODEL_PROTOCOL_TYPE_RADIO = 0x02
ASPHODEL_PROTOCOL_TYPE_REMOTE = 0x04
ASPHODEL_PROTOCOL_TYPE_BOOTLOADER = 0x08
GPIO_PIN_MODE_HI_Z = 0
GPIO_PIN_MODE_PULL_DOWN = 1
GPIO_PIN_MODE_PULL_UP = 2
GPIO_PIN_MODE_LOW = 3
GPIO_PIN_MODE_HIGH = 4
SPI_CS_MODE_LOW = 0
SPI_CS_MODE_HIGH = 1
SPI_CS_MODE_AUTO_TRANSFER = 2
SPI_CS_MODE_AUTO_BYTE = 3
ASPHODEL_SUPPLY_LOW_BATTERY = 0x01
ASPHODEL_SUPPLY_TOO_LOW = 0x02
ASPHODEL_SUPPLY_TOO_HIGH = 0x04
ASPHODEL_TCP_FILTER_DEFAULT = 0x0
ASPHODEL_TCP_FILTER_PREFER_IPV6 = 0x0
ASPHODEL_TCP_FILTER_PREFER_IPV4 = 0x1
ASPHODEL_TCP_FILTER_ONLY_IPV6 = 0x2
ASPHODEL_TCP_FILTER_ONLY_IPV4 = 0x3
ASPHODEL_TCP_FILTER_RETURN_ALL = 0x4


class AsphodelError(IOError):
    pass


StreamFormat = namedtuple("StreamFormat", ["filler_bits", "counter_bits",
                                           "rate", "rate_error",
                                           "warm_up_delay"])
ChannelInfo = namedtuple("ChannelInfo", ["channel_type", "unit_type",
                                         "filler_bits", "data_bits", "samples",
                                         "bits_per_sample", "minimum",
                                         "maximum", "resolution",
                                         "chunk_count"])
ChannelCalibration = namedtuple("ChannelCalibration",
                                ["base_setting_index",
                                 "resolution_setting_index", "scale", "offset",
                                 "minimum", "maximum"])
SupplyInfo = namedtuple("SupplyInfo", ["unit_type", "is_battery", "nominal",
                                       "scale", "offset"])
CtrlVarInfo = namedtuple("CtrlVarInfo", ["unit_type", "minimum", "maximum",
                                         "scale", "offset"])
ExtraScanResult = namedtuple("ExtraScanResult",
                             ["serial_number", "asphodel_type", "device_mode"])
GPIOPortInfo = namedtuple("GPIOPortInfo", ["input_pins", "output_pins",
                                           "floating_pins", "loaded_pins",
                                           "overridden_pins"])
BridgeValues = namedtuple("BridgeValues", ["pos_sense", "neg_sense", "nominal",
                                           "minimum", "maximum"])
SelfTestLimits = namedtuple("SelfTestLimits", ["x_min", "x_max", "y_min",
                                               "y_max", "z_min", "z_max"])
StreamRateInfo = namedtuple("StreamRateInfo", ["available", "channel_index",
                                               "invert", "scale", "offset"])
TCPAdvInfo = namedtuple("TCPAdvInfo", ["tcp_version", "connected",
                                       "max_incoming_param_length",
                                       "max_outgoing_param_length",
                                       "stream_packet_length", "protocol_type",
                                       "serial_number", "board_rev",
                                       "board_type", "build_info",
                                       "build_date", "user_tag1", "user_tag2",
                                       "remote_max_incoming_param_length",
                                       "remote_max_outgoing_param_length",
                                       "remote_stream_packet_length"])


class AsphodelStreamInfo(Structure):  # declared at top level for pickling
    _fields_ = [("channel_index_list", POINTER(c_uint8)),
                ("channel_count", c_uint8),
                ("filler_bits", c_uint8),
                ("counter_bits", c_uint8),
                ("rate", c_float),
                ("rate_error", c_float),
                ("warm_up_delay", c_float)]

    __reduce__ = object.__reduce__  # remove ctypes's __reduce__

    def __del__(self):
        try:
            self._free_func(self)
        except AttributeError:
            pass

    def __repr__(self):
        channel_index_list = self.channel_index_list[:self.channel_count]
        items = [("channel_index_list", channel_index_list),
                 ("channel_count", self.channel_count),
                 ("filler_bits", self.filler_bits),
                 ("counter_bits", self.counter_bits),
                 ("rate", self.rate),
                 ("rate_error", self.rate_error),
                 ("warm_up_delay", self.warm_up_delay)]
        contents = ", ".join(("{}={}".format(*i) for i in items))
        return "<AsphodelStreamInfo {" + contents + "}>"

    def __getstate__(self):
        return {"_channel_array": self.channel_index_list[:self.channel_count],
                "channel_count": self.channel_count,
                "filler_bits": self.filler_bits,
                "counter_bits": self.counter_bits,
                "rate": self.rate,
                "rate_error": self.rate_error,
                "warm_up_delay": self.warm_up_delay}

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)
        channel_array_type = (c_uint8 * len(self._channel_array))
        self._channel_array = channel_array_type(*self._channel_array)
        self.channel_index_list = self._channel_array

    def to_json_obj(self):
        # no unserializable objects in the state dict
        return self.__getstate__()

    @classmethod
    def from_json_obj(cls, obj):
        # no unserializable objects in the state dict
        instance = cls.__new__(cls)
        instance.__setstate__(obj)
        return instance


class AsphodelChannelInfo(Structure):  # declared at top level for pickling
    _fields_ = [("name", c_char_p),
                ("name_length", c_uint8),
                ("channel_type", c_uint8),
                ("unit_type", c_uint8),
                ("filler_bits", c_uint16),
                ("data_bits", c_uint16),
                ("samples", c_uint8),
                ("bits_per_sample", c_int16),
                ("minimum", c_float),
                ("maximum", c_float),
                ("resolution", c_float),
                ("coefficients", POINTER(c_float)),
                ("coefficients_length", c_uint8),
                ("chunks", POINTER(POINTER(c_uint8))),
                ("chunk_lengths", POINTER(c_uint8)),
                ("chunk_count", c_uint8)]

    __reduce__ = object.__reduce__  # remove ctypes's __reduce__

    def __getattribute__(self, name):
        # This is a hack to prevent name being None instead of empty bytes
        value = super().__getattribute__(name)
        if name == "name" and value is None:
            return b''
        return value

    def __del__(self):
        try:
            self._free_func(self)  # type: ignore
        except AttributeError:
            pass

    def __repr__(self):
        if self.channel_type < len(channel_type_names):
            s = channel_type_names[self.channel_type]
            channel_type_str = "{} ({})".format(self.channel_type, s)
        else:
            channel_type_str = "{}".format(self.channel_type)

        if self.unit_type < len(unit_type_names):
            s = unit_type_names[self.unit_type]
            unit_type_str = "{} ({})".format(self.unit_type, s)
        else:
            unit_type_str = "{}".format(self.unit_type)

        coefficients = self.coefficients[:self.coefficients_length]
        chunk_lengths = self.chunk_lengths[:self.chunk_count]
        chunks = []
        for i, ptr in enumerate(self.chunks[:self.chunk_count]):
            length = chunk_lengths[i]
            chunk = bytes(ptr[:length])
            chunks.append(chunk)
        items = [("name", self.name),
                 ("name_length", self.name_length),
                 ("channel_type", channel_type_str),
                 ("unit_type", unit_type_str),
                 ("filler_bits", self.filler_bits),
                 ("data_bits", self.data_bits),
                 ("samples", self.samples),
                 ("bits_per_sample", self.bits_per_sample),
                 ("minimum", self.minimum),
                 ("maximum", self.maximum),
                 ("resolution", self.resolution),
                 ("coefficients", coefficients),
                 ("coefficients_length", self.coefficients_length),
                 ("chunks", chunks),
                 ("chunk_lengths", chunk_lengths),
                 ("chunk_count", self.chunk_count)]
        contents = ", ".join(("{}={}".format(*i) for i in items))
        return "<AsphodelChannelInfo {" + contents + "}>"

    def __getstate__(self):
        coefficients = self.coefficients[:self.coefficients_length]
        chunk_lengths = self.chunk_lengths[:self.chunk_count]
        chunks = []
        for i, ptr in enumerate(self.chunks[:self.chunk_count]):
            length = chunk_lengths[i]
            chunk = ptr[:length]
            chunks.append(chunk)
        return {"_name_array": self.name,
                "name_length": self.name_length,
                "channel_type": self.channel_type,
                "unit_type": self.unit_type,
                "filler_bits": self.filler_bits,
                "data_bits": self.data_bits,
                "samples": self.samples,
                "bits_per_sample": self.bits_per_sample,
                "minimum": self.minimum,
                "maximum": self.maximum,
                "resolution": self.resolution,
                "_coefficients_array": coefficients,
                "coefficients_length": self.coefficients_length,
                "_chunk_list": chunks,
                "_chunk_length_array": chunk_lengths,
                "chunk_count": self.chunk_count}

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)

        self._name_array = c_char_p(self._name_array)
        self.name = self._name_array

        cf_array_type = (c_float * len(self._coefficients_array))
        self._coefficients_array = cf_array_type(*self._coefficients_array)
        self.coefficients = self._coefficients_array

        self._chunk_list = [(c_uint8 * len(c))(*c) for c in self._chunk_list]

        cl_array_type = (c_uint8 * self.chunk_count)
        self._chunk_length_array = cl_array_type(*self._chunk_length_array)
        self.chunk_lengths = self._chunk_length_array

        chunk_pointer_array_type = (POINTER(c_uint8) * self.chunk_count)
        chunk_pointer_array = chunk_pointer_array_type(*self._chunk_list)
        self._chunk_pointer_array = chunk_pointer_array
        self.chunks = chunk_pointer_array

    def to_json_obj(self):
        def to_hex(b):
            return binascii.b2a_hex(b).decode('ascii')

        d = self.__getstate__()
        d['_name_array'] = to_hex(d['_name_array'])

        return d

    @classmethod
    def from_json_obj(cls, obj):
        def from_hex(h):
            return binascii.a2b_hex(h)

        d = obj.copy()
        d['_name_array'] = from_hex(d['_name_array'])

        instance = cls.__new__(cls)
        instance.__setstate__(d)
        return instance


class SettingStructure(Structure):
    def __repr__(self):
        items = [(f[0], getattr(self, f[0])) for f in self._fields_]

        for i, (name, value) in enumerate(items):
            if name == "unit_type":
                if value < len(unit_type_names):
                    s = unit_type_names[self.unit_type]
                    unit_type_str = "{} ({})".format(value, s)
                    items[i] = (name, unit_type_str)

        contents = ", ".join(("{}={}".format(*x) for x in items))
        return "<" + self.__class__.__name__ + " {" + contents + "}>"


class AsphodelByteSetting(SettingStructure):
    _fields_ = [("nvm_word", c_uint16),
                ("nvm_word_byte", c_uint8)]


class AsphodelByteArraySetting(SettingStructure):
    _fields_ = [("nvm_word", c_uint16),
                ("maximum_length", c_uint8),
                ("length_nvm_word", c_uint16),
                ("length_nvm_word_byte", c_uint8)]


class AsphodelStringSetting(SettingStructure):
    _fields_ = [("nvm_word", c_uint16),
                ("maximum_length", c_uint8)]


class AsphodelInt32Setting(SettingStructure):
    _fields_ = [("nvm_word", c_uint16),
                ("minimum", c_int32),
                ("maximum", c_int32)]


class AsphodelInt32ScaledSetting(SettingStructure):
    _fields_ = [("nvm_word", c_uint16),
                ("minimum", c_int32),
                ("maximum", c_int32),
                ("unit_type", c_uint8),
                ("scale", c_float),
                ("offset", c_float)]


class AsphodelFloatSetting(SettingStructure):
    _fields_ = [("nvm_word", c_uint16),
                ("minimum", c_float),
                ("maximum", c_float),
                ("unit_type", c_uint8),
                ("scale", c_float),
                ("offset", c_float)]


class AsphodelFloatArraySetting(SettingStructure):
    _fields_ = [("nvm_word", c_uint16),
                ("minimum", c_float),
                ("maximum", c_float),
                ("unit_type", c_uint8),
                ("scale", c_float),
                ("offset", c_float),
                ("maximum_length", c_uint8),
                ("length_nvm_word", c_uint16),
                ("length_nvm_word_byte", c_uint8)]


class AsphodelCustomEnumSetting(SettingStructure):
    _fields_ = [("nvm_word", c_uint16),
                ("nvm_word_byte", c_uint8),
                ("custom_enum_index", c_uint8)]


class AsphodelSettingUnion(Union):
    _fields_ = [("byte_setting", AsphodelByteSetting),
                ("byte_array_setting", AsphodelByteArraySetting),
                ("string_setting", AsphodelStringSetting),
                ("int32_setting", AsphodelInt32Setting),
                ("int32_scaled_setting", AsphodelInt32ScaledSetting),
                ("float_setting", AsphodelFloatSetting),
                ("float_array_setting", AsphodelFloatArraySetting),
                ("custom_enum_setting", AsphodelCustomEnumSetting)]


class AsphodelSettingInfo(Structure):
    _fields_ = [("name", c_char_p),
                ("name_length", c_uint8),
                ("default_bytes", POINTER(c_uint8)),
                ("default_bytes_length", c_uint8),
                ("setting_type", c_uint8),
                ("u", AsphodelSettingUnion)]

    __reduce__ = object.__reduce__  # remove ctypes's __reduce__

    def __repr__(self):
        if self.setting_type < len(setting_type_names):
            s = setting_type_names[self.setting_type]
            setting_type_str = "{} ({})".format(self.setting_type, s)

            if (s == "SETTING_TYPE_BYTE" or
                    s == "SETTING_TYPE_BOOLEAN" or
                    s == "SETTING_TYPE_UNIT_TYPE" or
                    s == "SETTING_TYPE_CHANNEL_TYPE"):
                u_str = repr(self.u.byte_setting)
            elif s == "SETTING_TYPE_BYTE_ARRAY":
                u_str = repr(self.u.byte_array_setting)
            elif s == "SETTING_TYPE_STRING":
                u_str = repr(self.u.string_setting)
            elif s == "SETTING_TYPE_INT32":
                u_str = repr(self.u.int32_setting)
            elif s == "SETTING_TYPE_INT32_SCALED":
                u_str = repr(self.u.int32_scaled_setting)
            elif s == "SETTING_TYPE_FLOAT":
                u_str = repr(self.u.float_setting)
            elif s == "SETTING_TYPE_FLOAT_ARRAY":
                u_str = repr(self.u.float_array_setting)
            elif s == "SETTING_TYPE_CUSTOM_ENUM":
                u_str = repr(self.u.custom_enum_setting)
            else:
                u_str = "UNKNOWN TYPE"
        else:
            setting_type_str = "{}".format(self.setting_type)
            u_str = "UNKNOWN TYPE"

        default_bytes = self.default_bytes[:self.default_bytes_length]
        default_bytes_str = ",".join(map("0x{:02x}".format, default_bytes))

        items = [("name", self.name),
                 ("name_length", self.name_length),
                 ("default_bytes", default_bytes_str),
                 ("default_bytes_length", self.default_bytes_length),
                 ("setting_type", setting_type_str),
                 ("u", u_str)]
        contents = ", ".join(("{}={}".format(*i) for i in items))
        return "<AsphodelSettingInfo {" + contents + "}>"

    def __getstate__(self):
        default_bytes = self.default_bytes[:self.default_bytes_length]
        return {"_name_array": self.name,
                "name_length": self.name_length,
                "_default_bytes": default_bytes,
                "default_bytes_length": self.default_bytes_length,
                "setting_type": self.setting_type,
                "u": self.u}

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)

        self._name_array = c_char_p(self._name_array)
        self.name = self._name_array

        array_type = (c_uint8 * self.default_bytes_length)
        self._default_bytes = array_type(*self._default_bytes)
        self.default_bytes = self._default_bytes

    @classmethod
    def from_str(cls, s):

        def trim_prefix(s, prefix):
            if not s.startswith(prefix):
                raise AsphodelError('Invalid string prefix "{}"'.format(
                    prefix))
            return s[len(prefix):]

        def trim_suffix(s, suffix):
            if not s.endswith(suffix):
                raise AsphodelError('Invalid string suffix "{}"'.format(
                    suffix))
            return s[:-len(suffix)]

        s = trim_prefix(s, "<AsphodelSettingInfo {")
        s = trim_suffix(s, "}>")

        # note we parse backwards because the name=b"..." may have other chars

        # u
        u = AsphodelSettingUnion()
        if not s.endswith("UNKNOWN TYPE"):
            s = trim_suffix(s, "}>")
            s, u_vals = s.rsplit(" {", 1)
            s, u_type = s.rsplit(", u=<")

            u_dict = dict(map(lambda s: s.split("=", 1), u_vals.split(", ")))
            if "unit_type" in u_dict:
                # remove "(UNIT_TYPE_X)" from the string
                u_dict['unit_type'] = u_dict['unit_type'].split(" ", 1)[0]
            for k, v in u_dict.items():
                try:
                    u_dict[k] = int(v)
                except ValueError:
                    u_dict[k] = float(v)

            for field_name, field_type in AsphodelSettingUnion._fields_:
                if field_type.__name__ == u_type:
                    u_struct = getattr(u, field_name)
                    # set the struct members
                    for name, value in u_dict.items():
                        setattr(u_struct, name, value)
                    break

        # setting_type
        s, setting_type_str = s.rsplit(", setting_type=", 1)
        setting_type = int(setting_type_str.split(" (", 1)[0])

        # default_bytes_length
        s, default_bytes_length_str = s.rsplit(", default_bytes_length=", 1)
        default_bytes_length = int(default_bytes_length_str)

        # default_bytes
        s, default_bytes_str = s.rsplit(", default_bytes=", 1)
        b = "".join(map(lambda x: x[2:], default_bytes_str.split(",")))
        default_bytes = binascii.a2b_hex(b)

        if len(default_bytes) != default_bytes_length:
            raise AsphodelError("Bad default_bytes_length")

        # name_length
        s, name_length_str = s.rsplit(", name_length=", 1)
        name_length = int(name_length_str)

        # name
        name_str = trim_prefix(s, "name=")
        name = ast.literal_eval(name_str)

        if not isinstance(name, bytes):
            raise AsphodelError("Bad name")

        if len(name) != name_length:
            raise AsphodelError("Bad name_length")

        instance = cls.__new__(cls)
        instance.__setstate__({"_name_array": name,
                               "name_length": name_length,
                               "_default_bytes": default_bytes,
                               "default_bytes_length": default_bytes_length,
                               "setting_type": setting_type,
                               "u": u})

        return instance


class AsphodelNative:
    # void (*)(int status, uint8_t *params, size_t param_length,
    #          void * closure)
    AsphodelTransferCallback = CFUNCTYPE(None, c_int, POINTER(c_uint8),
                                         c_size_t, c_void_p)

    # void (*)(int status, uint8_t *stream_data, size_t packet_size,
    #          size_t packet_count, void * closure)
    AsphodelStreamingCallback = CFUNCTYPE(None, c_int, POINTER(c_uint8),
                                          c_size_t, c_size_t, c_void_p)

    # void (*)(int status, int connected, void * closure)
    AsphodelConnectCallback = CFUNCTYPE(None, c_int, c_int, c_void_p)

    # void (*)(int status, void * closure)
    AsphodelCommandCallback = CFUNCTYPE(None, c_int, c_void_p)

    # void (*)(uint64_t counter, double *data, size_t samples,
    #          size_t subchannels, void * closure)
    AsphodelDecodeCallback = CFUNCTYPE(None, c_uint64, POINTER(c_double),
                                       c_size_t, c_size_t, c_void_p)

    # uint64_t (*)(uint8_t *buffer, uint64_t last)
    AsphodelCounterDecoderFunc = CFUNCTYPE(c_uint64, POINTER(c_uint8),
                                           c_uint64)

    # void (*)(uint64_t current, uint64_t last, void * closure)
    AsphodelLostPacketCallback = CFUNCTYPE(None, c_uint64, c_uint64, c_void_p)

    # uint8_t (*)(uint8_t *buffer)
    AsphodelIDDecoderFunc = CFUNCTYPE(c_uint8, POINTER(c_uint8))

    # void (*)(uint8_t id, void * closure)
    AsphodelUnknownIDCallback = CFUNCTYPE(None, c_uint8, c_void_p)

    class AsphodelDeviceStruct(Structure):
        pass  # need a forward declaration for the recursive structure
    AsphodelDeviceStruct._fields_ = [
        # int
        ("protocol_type", c_int),
        # const char *
        ("location_string", c_char_p),
        # int (*)(struct AsphodelDevice_t * device)
        ("open_device", CFUNCTYPE(c_int, POINTER(AsphodelDeviceStruct))),
        # void (*)(struct AsphodelDevice_t *device)
        ("close_device", CFUNCTYPE(None, POINTER(AsphodelDeviceStruct))),
        # void (*)(struct AsphodelDevice_t *device)
        ("free_device", CFUNCTYPE(None, POINTER(AsphodelDeviceStruct))),
        # int (*)(struct AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size)
        ("get_serial_number", CFUNCTYPE(c_int, POINTER(AsphodelDeviceStruct),
                                        c_char_p, c_size_t)),
        # int (*)(struct AsphodelDevice_t *device, uint8_t command,
        #         uint8_t *params, size_t param_length,
        #         AsphodelTransferCallback_t callback, void * closure)
        ("do_transfer", CFUNCTYPE(c_int, POINTER(AsphodelDeviceStruct),
                                  c_uint8, POINTER(c_uint8), c_size_t,
                                  AsphodelTransferCallback, c_void_p)),
        # int (*)(struct AsphodelDevice_t *device, uint8_t command,
        #         uint8_t *params, size_t param_length,
        #         AsphodelTransferCallback_t callback, void * closure)
        ("do_transfer_reset", CFUNCTYPE(c_int, POINTER(AsphodelDeviceStruct),
                                        c_uint8, POINTER(c_uint8), c_size_t,
                                        AsphodelTransferCallback, c_void_p)),
        # int (*)(struct AsphodelDevice_t *device, int packet_count,
        #         int transfer_count, unsigned int timeout,
        #         AsphodelStreamingCallback_t callback, void * closure)
        ("start_streaming_packets", CFUNCTYPE(c_int,
                                              POINTER(AsphodelDeviceStruct),
                                              c_int, c_int, c_uint,
                                              AsphodelStreamingCallback,
                                              c_void_p)),
        # int (*)(struct AsphodelDevice_t *device)
        ("stop_streaming_packets", CFUNCTYPE(None,
                                             POINTER(AsphodelDeviceStruct))),
        # int (*)(struct AsphodelDevice_t *device, uint8_t *buffer,
        #         int *count, unsigned int timeout)
        ("get_stream_packets_blocking", CFUNCTYPE(
            c_int, POINTER(AsphodelDeviceStruct), POINTER(c_uint8),
            POINTER(c_int), c_uint)),
        # size_t (*)(struct AsphodelDevice_t * device)
        ("get_max_incoming_param_length", CFUNCTYPE(
            c_size_t, POINTER(AsphodelDeviceStruct))),
        # size_t (*)(struct AsphodelDevice_t * device)
        ("get_max_outgoing_param_length", CFUNCTYPE(
            c_size_t, POINTER(AsphodelDeviceStruct))),
        # size_t (*)(struct AsphodelDevice_t * device)
        ("get_stream_packet_length", CFUNCTYPE(
            c_size_t, POINTER(AsphodelDeviceStruct))),
        # int (*)(struct AsphodelDevice_t * device, int milliseconds,
        #         int *completed)
        ("poll_device", CFUNCTYPE(c_int, POINTER(AsphodelDeviceStruct),
                                  c_int, POINTER(c_int))),
        # int (*)(struct AsphodelDevice_t * device,
        #         AsphodelConnectCallback_t callback, void * closure)
        ("set_connect_callback", CFUNCTYPE(
            c_int, POINTER(AsphodelDeviceStruct), AsphodelConnectCallback,
            c_void_p)),
        # int (*)(struct AsphodelDevice_t * device, unsigned int timeout)
        ("wait_for_connect", CFUNCTYPE(c_int, POINTER(AsphodelDeviceStruct),
                                       c_uint)),
        # int (*)(struct AsphodelDevice_t * device,
        #         struct AsphodelDevice_t **remote_device)
        ("get_remote_device", CFUNCTYPE(
            c_int, POINTER(AsphodelDeviceStruct),
            POINTER(POINTER(AsphodelDeviceStruct)))),
        # int (*)(struct AsphodelDevice_t * device,
        #         struct AsphodelDevice_t **reconnected_device)
        ("reconnect_device", CFUNCTYPE(
            c_int, POINTER(AsphodelDeviceStruct),
            POINTER(POINTER(AsphodelDeviceStruct)))),
        # void (*)(struct AsphodelDevice_t * device, int status,
        #          void *closure)
        ("error_callback", CFUNCTYPE(None, POINTER(AsphodelDeviceStruct),
                                     c_int, c_void_p)),
        # void *
        ("error_closure", c_void_p),
        # void *
        # int (*)(struct AsphodelDevice_t * device,
        #         struct AsphodelDevice_t **reconnected_device)
        ("reconnect_device_bootloader", CFUNCTYPE(
            c_int, POINTER(AsphodelDeviceStruct),
            POINTER(POINTER(AsphodelDeviceStruct)))),
        # int (*)(struct AsphodelDevice_t * device,
        #         struct AsphodelDevice_t **reconnected_device)
        ("reconnect_device_application", CFUNCTYPE(
            c_int, POINTER(AsphodelDeviceStruct),
            POINTER(POINTER(AsphodelDeviceStruct)))),
        ("implementation_info", c_void_p),
        # const char *
        ("transport_type", c_char_p),
        # void * reserved[9]
        ("_reserved", c_void_p * 9)]

    class AsphodelChannelCalibration(Structure):
        _fields_ = [("base_setting_index", c_int),
                    ("resolution_setting_index", c_int),
                    ("scale", c_float),
                    ("offset", c_float),
                    ("minimum", c_float),
                    ("maximum", c_float)]

    class AsphodelSupplyInfo(Structure):
        _fields_ = [("name", c_char_p),
                    ("name_length", c_uint8),
                    ("unit_type", c_uint8),
                    ("is_battery", c_uint8),
                    ("nominal", c_int32),
                    ("scale", c_float),
                    ("offset", c_float)]

    class AsphodelCtrlVarInfo(Structure):
        _fields_ = [("name", c_char_p),
                    ("name_length", c_uint8),
                    ("unit_type", c_uint8),
                    ("minimum", c_int32),
                    ("maximum", c_int32),
                    ("scale", c_float),
                    ("offset", c_float)]

    class AsphodelExtraScanResult(Structure):
        _fields_ = [("serial_number", c_uint32),
                    ("asphodel_type", c_uint8),
                    ("device_mode", c_uint8),
                    ("_reserved", c_uint16)]

    class AsphodelGPIOPortInfo(Structure):
        _fields_ = [("name", c_char_p),
                    ("name_length", c_uint8),
                    ("input_pins", c_uint32),
                    ("output_pins", c_uint32),
                    ("floating_pins", c_uint32),
                    ("loaded_pins", c_uint32),
                    ("overridden_pins", c_uint32)]

    class AsphodelStreamAndChannels(Structure):
        _fields_ = [("stream_id", c_uint8),
                    ("stream_info", POINTER(AsphodelStreamInfo)),
                    ("channel_info", POINTER(POINTER(AsphodelChannelInfo)))]

    class AsphodelChannelDecoder(Structure):
        pass  # need a forward declaration for the recursive structure
    AsphodelChannelDecoder._fields_ = [
        ("decode", CFUNCTYPE(None, POINTER(AsphodelChannelDecoder), c_uint64,
                             POINTER(c_uint8))),
        ("free_decoder", CFUNCTYPE(None, POINTER(AsphodelChannelDecoder))),
        ("reset", CFUNCTYPE(None, POINTER(AsphodelChannelDecoder))),
        ("set_conversion_factor", CFUNCTYPE(None,
                                            POINTER(AsphodelChannelDecoder),
                                            c_double, c_double)),
        ("channel_bit_offset", c_uint16),
        ("samples", c_size_t),
        ("channel_name", c_char_p),
        ("subchannels", c_size_t),
        ("subchannel_names", POINTER(c_char_p)),
        ("callback", AsphodelDecodeCallback),
        ("closure", c_void_p)]

    class AsphodelStreamDecoder(Structure):
        pass  # need a forward declaration for the recursive structure
    AsphodelStreamDecoder._fields_ = [
        ("decode", CFUNCTYPE(None, POINTER(AsphodelStreamDecoder),
                             POINTER(c_uint8))),
        ("free_decoder", CFUNCTYPE(None, POINTER(AsphodelStreamDecoder))),
        ("reset", CFUNCTYPE(None, POINTER(AsphodelStreamDecoder))),
        ("last_count", c_uint64),
        ("counter_byte_offset", c_size_t),
        ("counter_decoder", AsphodelCounterDecoderFunc),
        ("channels", c_size_t),
        ("decoders", POINTER(POINTER(AsphodelChannelDecoder))),
        ("lost_packet_callback", AsphodelLostPacketCallback),
        ("lost_packet_closure", c_void_p),
        ("used_bits", c_uint16)]

    class AsphodelDeviceDecoder(Structure):
        pass  # need a forward declaration for the recursive structure
    AsphodelDeviceDecoder._fields_ = [
        ("decode", CFUNCTYPE(None, POINTER(AsphodelDeviceDecoder),
                             POINTER(c_uint8))),
        ("free_decoder", CFUNCTYPE(None, POINTER(AsphodelDeviceDecoder))),
        ("reset", CFUNCTYPE(None, POINTER(AsphodelDeviceDecoder))),
        ("id_byte_offset", c_size_t),
        ("id_decoder", AsphodelIDDecoderFunc),
        ("streams", c_size_t),
        ("stream_ids", POINTER(c_uint8)),
        ("decoders", POINTER(POINTER(AsphodelStreamDecoder))),
        ("unknown_id_callback", AsphodelUnknownIDCallback),
        ("unknown_id_closure", c_void_p),
        ("used_bits", c_uint16)]

    class AsphodelTCPAdvInfo(Structure):
        _fields_ = [("tcp_version", c_uint8),
                    ("connected", c_uint8),
                    ("max_incoming_param_length", c_size_t),
                    ("max_outgoing_param_length", c_size_t),
                    ("stream_packet_length", c_size_t),
                    ("protocol_type", c_int),
                    ("serial_number", c_char_p),
                    ("board_rev", c_uint8),
                    ("board_type", c_char_p),
                    ("build_info", c_char_p),
                    ("build_date", c_char_p),
                    ("user_tag1", c_char_p),
                    ("user_tag2", c_char_p),
                    ("remote_max_incoming_param_length", c_size_t),
                    ("remote_max_outgoing_param_length", c_size_t),
                    ("remote_stream_packet_length", c_size_t)]

    class AsphodelUnitFormatter(Structure):
        pass  # need a forward declaration for the recursive structure
    AsphodelUnitFormatter._fields_ = [
        ("format_bare", CFUNCTYPE(c_int, POINTER(AsphodelUnitFormatter),
                                  c_char_p, c_size_t, c_double)),
        ("format_ascii", CFUNCTYPE(c_int, POINTER(AsphodelUnitFormatter),
                                   c_char_p, c_size_t, c_double)),
        ("format_utf8", CFUNCTYPE(c_int, POINTER(AsphodelUnitFormatter),
                                  c_char_p, c_size_t, c_double)),
        ("format_html", CFUNCTYPE(c_int, POINTER(AsphodelUnitFormatter),
                                  c_char_p, c_size_t, c_double)),
        ("free", CFUNCTYPE(None, POINTER(AsphodelUnitFormatter))),
        ("unit_ascii", c_char_p),
        ("unit_utf8", c_char_p),
        ("unit_html", c_char_p),
        ("conversion_scale", c_double),
        ("conversion_offset", c_double)]

    def __init__(self):
        self.lib = None

        # list of names of functions that couldn't be loaded
        self.missing_funcs = []

        # list of devices to close before freeing the library
        self.device_list = weakref.WeakSet()

        if sys.platform == "win32":
            is_64bit = sys.maxsize > (2 ** 32)
            if is_64bit:
                library_name = 'Asphodel64'
                library_dir = os.path.join(os.path.dirname(__file__), "lib64")
            else:
                library_name = 'Asphodel32'
                library_dir = os.path.join(os.path.dirname(__file__), "lib32")
            library_path = os.path.join(library_dir, library_name + ".dll")
            os.environ['PATH'] = (
                library_dir + os.pathsep + os.path.dirname(sys.executable) +
                os.pathsep + os.environ['PATH'])
        elif sys.platform == "darwin":
            library_name = "asphodel"
            library_path = os.path.join(os.path.dirname(__file__),
                                        "lib/libasphodel.dylib")
        else:
            # probably linux, but could be anything
            library_name = "asphodel"
            library_path = os.path.join(os.path.dirname(__file__),
                                        "lib/libasphodel.so")

        if not os.path.isfile(library_path):
            library_path = find_library(library_name)
            if library_path is None:
                raise AsphodelError(0, "Could not find asphodel library!")
        try:
            self.lib = cdll.LoadLibrary(library_path)
        except Exception as e:
            raise AsphodelError(0, "Could not load asphodel library!") from e

        self.setup_api_h_prototypes()
        self.setup_bootloader_h_prototypes()
        self.setup_channel_specific_h_prototypes()
        self.setup_ctrl_var_h_prototypes()
        self.setup_decode_h_prototypes()
        self.setup_device_h_prototypes()
        self.setup_device_type_h_prototypes()
        self.setup_low_level_h_prototypes()
        self.setup_mem_test_h_prototypes()
        self.setup_radio_h_prototypes()
        self.setup_rf_power_h_prototypes()
        self.setup_setting_h_prototypes()
        self.setup_stream_h_prototypes()
        self.setup_supply_h_prototypes()
        self.setup_tcp_h_prototypes()
        self.setup_unit_format_h_prototypes()
        self.setup_usb_h_prototypes()
        self.setup_version_h_prototypes()

        # initialize USB
        if self.usb_devices_supported:
            self.lib.asphodel_usb_init()

        # initialize TCP
        if self.tcp_devices_supported:
            self.lib.asphodel_tcp_init()

        unit_type_count = self.lib.asphodel_get_unit_type_count()
        self.unit_type_names = [self.lib.asphodel_unit_type_name(i)
                                for i in range(unit_type_count)]
        channel_type_count = self.lib.asphodel_get_channel_type_count()
        self.channel_type_names = [self.lib.asphodel_channel_type_name(i)
                                   for i in range(channel_type_count)]
        setting_type_count = self.lib.asphodel_get_setting_type_count()
        self.setting_type_names = [self.lib.asphodel_setting_type_name(i)
                                   for i in range(setting_type_count)]

        # get library version strings
        ver_bcd = self.lib.asphodel_get_library_protocol_version()
        self.protocol_version = ver_bcd
        b = self.lib.asphodel_get_library_protocol_version_string()
        self.protocol_version_string = b.decode("UTF-8")
        b = self.lib.asphodel_get_library_build_info()
        self.build_info = b.decode("UTF-8")
        b = self.lib.asphodel_get_library_build_date()
        self.build_date = b.decode("UTF-8")
        try:
            b = self.lib.asphodel_usb_get_backend_version()
            self.usb_backend_version = b.decode("UTF-8")
        except Exception:
            self.usb_backend_version = "<UNKNOWN>"

    def free(self):
        if self.device_list:
            for device in self.device_list:
                device.free()
            self.device_list = None

        if self.lib:
            if self.usb_devices_supported:
                self.lib.asphodel_usb_deinit()
            if self.tcp_devices_supported:
                self.lib.asphodel_tcp_deinit()
            self.lib = None

    def __del__(self):
        self.free()

    def asphodel_error_check(self, result, func=None, arguments=None):
        if result != 0:
            error_name = self.lib.asphodel_error_name(result)
            raise AsphodelError(result, error_name)

    def asphodel_string_decode_check(self, result, func, arguments):
        return result.decode("UTF-8")

    def load_library_function(self, name, restype, argtypes, errcheck,
                              ignore_missing=True):
        try:
            func = getattr(self.lib, name)
        except AttributeError:
            if ignore_missing:
                self.missing_funcs.append(name)

                def missing_func(*args, **kwargs):
                    msg = "Library missing {}()".format(name)
                    raise AsphodelError(0, msg)
                setattr(self.lib, name, missing_func)
                return
            else:
                raise
        func.restype = restype
        if errcheck is not None:
            func.errcheck = errcheck
        func.argtypes = argtypes

    def load_device_function(self, base_name, argtypes):
        non_blocking_name = base_name
        blocking_name = base_name + "_blocking"

        blocking_argtypes = [POINTER(self.AsphodelDeviceStruct)]
        blocking_argtypes.extend(argtypes)

        non_blocking_argtypes = list(blocking_argtypes)
        non_blocking_argtypes.append(self.AsphodelCommandCallback)
        non_blocking_argtypes.append(c_void_p)

        self.load_library_function(non_blocking_name, c_int,
                                   non_blocking_argtypes,
                                   self.asphodel_error_check)
        self.load_library_function(blocking_name, c_int, blocking_argtypes,
                                   self.asphodel_error_check)

    def setup_api_h_prototypes(self):
        string_decode = self.asphodel_string_decode_check

        # const char * asphodel_error_name(int error_code)
        self.load_library_function("asphodel_error_name",
                                   c_char_p, [c_int], string_decode)

        # const char * asphodel_unit_type_name(uint8_t unit_type)
        self.load_library_function("asphodel_unit_type_name",
                                   c_char_p, [c_uint8], string_decode)

        # uint8_t asphodel_get_unit_type_count(void)
        self.load_library_function("asphodel_get_unit_type_count",
                                   c_uint8, [], None)

        # const char * asphodel_channel_type_name(uint8_t channel_type)
        self.load_library_function("asphodel_channel_type_name",
                                   c_char_p, [c_uint8], string_decode)

        # uint8_t asphodel_get_channel_type_count(void)
        self.load_library_function("asphodel_get_channel_type_count",
                                   c_uint8, [], None)

        # const char * asphodel_setting_type_name(uint8_t setting_type)
        self.load_library_function("asphodel_setting_type_name",
                                   c_char_p, [c_uint8], string_decode)

        # uint8_t asphodel_get_setting_type_count(void)
        self.load_library_function("asphodel_get_setting_type_count",
                                   c_uint8, [], None)

    def setup_bootloader_h_prototypes(self):
        # int asphodel_bootloader_start_program(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_bootloader_start_program", [])

        # int asphodel_get_bootloader_page_info(AsphodelDevice_t *device,
        #         uint32_t *page_info, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_bootloader_page_info",
                                  [POINTER(c_uint32), POINTER(c_uint8)])

        # int asphodel_get_bootloader_block_sizes(AsphodelDevice_t *device,
        #         uint16_t *block_sizes, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_bootloader_block_sizes",
                                  [POINTER(c_uint16), POINTER(c_uint8)])

        # int asphodel_start_bootloader_page(AsphodelDevice_t *device,
        #         uint32_t page_number, uint8_t *nonce, size_t length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_start_bootloader_page",
                                  [c_uint32, POINTER(c_uint8), c_size_t])

        # int asphodel_write_bootloader_code_block(AsphodelDevice_t *device,
        #         uint8_t *data, size_t length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_write_bootloader_code_block",
                                  [POINTER(c_uint8), c_size_t])

        # int asphodel_write_bootloader_page(AsphodelDevice_t *device,
        #         uint8_t *data, size_t data_length, uint16_t *block_sizes,
        #         uint8_t block_sizes_length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_write_bootloader_page",
                                  [POINTER(c_uint8), c_size_t,
                                   POINTER(c_uint16), c_uint8])

        # int asphodel_finish_bootloader_page(AsphodelDevice_t *device,
        #         uint8_t *mac_tag, size_t length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_finish_bootloader_page",
                                  [POINTER(c_uint8), c_size_t])

        # int asphodel_verify_bootloader_page(AsphodelDevice_t *device,
        #         uint8_t *mac_tag, size_t length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_verify_bootloader_page",
                                  [POINTER(c_uint8), c_size_t])

    def setup_channel_specific_h_prototypes(self):
        # int asphodel_get_strain_bridge_count(
        #         AsphodelChannelInfo_t *channel_info, int *bridge_count)
        self.load_library_function(
            "asphodel_get_strain_bridge_count", c_int,
            [POINTER(AsphodelChannelInfo), POINTER(c_int)],
            self.asphodel_error_check)

        # int asphodel_get_strain_bridge_subchannel(
        #         AsphodelChannelInfo_t *channel_info, int bridge_index,
        #         size_t *subchannel_index)
        self.load_library_function(
            "asphodel_get_strain_bridge_subchannel", c_int,
            [POINTER(AsphodelChannelInfo), c_int, POINTER(c_size_t)],
            self.asphodel_error_check)

        # int asphodel_get_strain_bridge_values(
        #         AsphodelChannelInfo_t *channel_info, int bridge_index,
        #         float *values)
        self.load_library_function(
            "asphodel_get_strain_bridge_values", c_int,
            [POINTER(AsphodelChannelInfo), c_int, c_float * 5],
            self.asphodel_error_check)

        # int asphodel_set_strain_outputs(AsphodelDevice_t *device,
        #         int channel_index, int bridge_index, int positive_side,
        #         int negative_side, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_set_strain_outputs",
                                  [c_int, c_int, c_int, c_int])

        # int asphodel_check_strain_resistances(
        #         AsphodelChannelInfo_t *channel_info, int bridge_index,
        #         double baseline, double positive_high, double negative_high,
        #         double *positive_resistance, double *negative_resistance,
        #         int *passed)
        self.load_library_function(
            "asphodel_check_strain_resistances", c_int,
            [POINTER(AsphodelChannelInfo), c_int, c_double, c_double, c_double,
             POINTER(c_double), POINTER(c_double), POINTER(c_int)],
            self.asphodel_error_check)

        # int asphodel_get_accel_self_test_limits(
        #         AsphodelChannelInfo_t *channel_info, float *limits)
        self.load_library_function(
            "asphodel_get_accel_self_test_limits", c_int,
            [POINTER(AsphodelChannelInfo), c_float * 6],
            self.asphodel_error_check)

        # int asphodel_enable_accel_self_test(AsphodelDevice_t *device,
        #         int channel_index, int enable,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_enable_accel_self_test",
                                  [c_int, c_int])

        # int asphodel_check_accel_self_test(
        #         AsphodelChannelInfo_t *channel_info, double *disabled,
        #         double *enabled, int *passed)
        self.load_library_function(
            "asphodel_check_accel_self_test", c_int,
            [POINTER(AsphodelChannelInfo), c_double * 3, c_double * 3,
             POINTER(c_int)], self.asphodel_error_check)

    def setup_ctrl_var_h_prototypes(self):
        # int asphodel_get_ctrl_var_count(AsphodelDevice_t *device,
        #         int *count, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_ctrl_var_count",
                                  [POINTER(c_int)])

        # int asphodel_get_ctrl_var_name(AsphodelDevice_t *device,
        #         int index, char *buffer, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_ctrl_var_name",
                                  [c_int, c_char_p, POINTER(c_uint8)])

        # int asphodel_get_ctrl_var_info(AsphodelDevice_t *device,
        #         int index, AsphodelCtrlVarInfo_t *ctrl_var_info,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_ctrl_var_info",
                                  [c_int, POINTER(self.AsphodelCtrlVarInfo)])

        # int asphodel_get_ctrl_var(AsphodelDevice_t *device, int index,
        #         int32_t *value, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_ctrl_var",
                                  [c_int, POINTER(c_int32)])

        # int asphodel_set_ctrl_var(AsphodelDevice_t *device, int index,
        #         int32_t value, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_set_ctrl_var", [c_int, c_int32])

    def setup_decode_h_prototypes(self):
        # int asphodel_create_channel_decoder(AsphodelChannelInfo_t *ch_info,
        #         uint16_t bit_offset, AsphodelChannelDecoder_t **decoder)
        self.load_library_function(
            "asphodel_create_channel_decoder", c_int,
            [POINTER(AsphodelChannelInfo), c_uint16,
             POINTER(POINTER(self.AsphodelChannelDecoder))],
            self.asphodel_error_check)

        # int asphodel_create_stream_decoder(AsphodelStreamAndChannels_t *info,
        #         uint16_t stream_bit_offset,
        #         AsphodelStreamDecoder_t **decoder)
        self.load_library_function(
            "asphodel_create_stream_decoder", c_int,
            [POINTER(self.AsphodelStreamAndChannels), c_uint16,
             POINTER(POINTER(self.AsphodelStreamDecoder))],
            self.asphodel_error_check)

        # int asphodel_create_device_decoder(
        #         AsphodelStreamAndChannels_t *info_array,
        #         uint8_t info_array_size, uint8_t filler_bits,
        #         uint8_t id_bits, AsphodelDeviceDecoder_t **decoder)
        self.load_library_function(
            "asphodel_create_device_decoder", c_int,
            [POINTER(self.AsphodelStreamAndChannels), c_uint8, c_uint8,
             c_uint8, POINTER(POINTER(self.AsphodelDeviceDecoder))],
            self.asphodel_error_check)

        # int asphodel_get_streaming_counts(
        #         AsphodelStreamAndChannels_t *info_array,
        #         uint8_t info_array_size, double response_time,
        #         double buffer_time, int *packet_count, int *transfer_count,
        #         unsigned int *timeout)
        self.load_library_function(
            "asphodel_get_streaming_counts", c_int,
            [POINTER(self.AsphodelStreamAndChannels), c_uint8, c_double,
             c_double, POINTER(c_int), POINTER(c_int), POINTER(c_uint)],
            self.asphodel_error_check)

    def setup_device_h_prototypes(self):
        # int asphodel_get_protocol_version(AsphodelDevice_t *device,
        #         uint16_t *version, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_protocol_version",
                                  [POINTER(c_uint16)])

        # int asphodel_get_protocol_version_string(AsphodelDevice_t *device,
        #         char *buffer, size_t buffer_size,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_protocol_version_string",
                                  [c_char_p, c_size_t])

        # int asphodel_get_board_info(AsphodelDevice_t *device, uint8_t *rev,
        #         char *buffer, size_t buffer_size,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_board_info",
                                  [POINTER(c_uint8), c_char_p, c_size_t])

        # int asphodel_get_user_tag_locations(AsphodelDevice_t *device,
        #         size_t *locations, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_user_tag_locations",
                                  [c_size_t * 6])

        # int asphodel_get_build_info(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_build_info",
                                  [c_char_p, c_size_t])

        # int asphodel_get_build_date(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_build_date",
                                  [c_char_p, c_size_t])

        # int asphodel_get_commit_id(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_commit_id",
                                  [c_char_p, c_size_t])

        # int asphodel_get_repo_branch(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_repo_branch",
                                  [c_char_p, c_size_t])

        # int asphodel_get_repo_name(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_repo_name",
                                  [c_char_p, c_size_t])

        # int asphodel_get_chip_family(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_chip_family",
                                  [c_char_p, c_size_t])

        # int asphodel_get_chip_model(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_chip_model",
                                  [c_char_p, c_size_t])

        # int asphodel_get_chip_id(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_chip_id", [c_char_p, c_size_t])

        # int asphodel_get_nvm_size(AsphodelDevice_t *device, size_t *size,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_nvm_size", [POINTER(c_size_t)])

        # int asphodel_erase_nvm(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_erase_nvm", [])

        # int asphodel_write_nvm_raw(AsphodelDevice_t *device,
        #         size_t start_address, uint8_t *data, size_t length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_write_nvm_raw",
                                  [c_size_t, POINTER(c_uint8), c_size_t])

        # int asphodel_write_nvm_section(AsphodelDevice_t *device,
        #         size_t start_address, uint8_t *data, size_t length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_write_nvm_section",
                                  [c_size_t, POINTER(c_uint8), c_size_t])

        # int asphodel_read_nvm_raw(AsphodelDevice_t *device,
        #         size_t start_address, uint8_t *data, size_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_read_nvm_raw",
                                  [c_size_t, POINTER(c_uint8),
                                   POINTER(c_size_t)])

        # int asphodel_read_nvm_section(AsphodelDevice_t *device,
        #         size_t start_address, uint8_t *data, size_t length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_read_nvm_section",
                                  [c_size_t, POINTER(c_uint8), c_size_t])

        # int asphodel_read_user_tag_string(AsphodelDevice_t *device,
        #         size_t offset, size_t length, char *buffer,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_read_user_tag_string",
                                  [c_size_t, c_size_t, c_char_p])

        # int asphodel_write_user_tag_string(AsphodelDevice_t *device,
        #         size_t offset, size_t length, char *buffer,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_write_user_tag_string",
                                  [c_size_t, c_size_t, c_char_p])

        # int asphodel_get_nvm_modified(AsphodelDevice_t *device,
        #         uint8_t *modified, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_nvm_modified",
                                  [POINTER(c_uint8)])

        # int asphodel_get_nvm_hash(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_nvm_hash",
                                  [c_char_p, c_size_t])

        # int asphodel_get_setting_hash(AsphodelDevice_t *device, char *buffer,
        #         size_t buffer_size, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_setting_hash",
                                  [c_char_p, c_size_t])

        # int asphodel_flush(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_flush", [])

        # int asphodel_reset(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_reset", [])

        # int asphodel_get_bootloader_info(AsphodelDevice_t *device,
        #         char *buffer, size_t buffer_size,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_bootloader_info",
                                  [c_char_p, c_size_t])

        # int asphodel_bootloader_jump(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_bootloader_jump", [])

        # int asphodel_get_reset_flag(AsphodelDevice_t *device, uint8_t *flag,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_reset_flag",
                                  [POINTER(c_uint8)])

        # int asphodel_clear_reset_flag(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_clear_reset_flag", [])

        # int asphodel_get_rgb_count(AsphodelDevice_t *device, int *count,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_rgb_count", [POINTER(c_int)])

        # int asphodel_get_rgb_values(AsphodelDevice_t *device, int index,
        #         uint8_t *values, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_rgb_values",
                                  [c_int, c_uint8 * 3])

        # int asphodel_set_rgb_values(AsphodelDevice_t *device, int index,
        #         uint8_t *values, int instant,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_set_rgb_values",
                                  [c_int, c_uint8 * 3, c_int])

        # int asphodel_set_rgb_values_hex(AsphodelDevice_t *device, int index,
        #         uint32_t color, int instant,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_set_rgb_values_hex",
                                  [c_int, c_uint32, c_int])

        # int asphodel_get_led_count(AsphodelDevice_t *device, int *count,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_led_count", [POINTER(c_int)])

        # int asphodel_get_led_value(AsphodelDevice_t *device, int index,
        #         uint8_t *value, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_led_value",
                                  [c_int, POINTER(c_uint8)])

        # int asphodel_set_led_value(AsphodelDevice_t *device, int index,
        #         uint8_t value, int instant,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_set_led_value",
                                  [c_int, c_uint8, c_int])

        # int asphodel_set_device_mode(AsphodelDevice_t *device, uint8_t mode,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_set_device_mode", [c_uint8])

        # int asphodel_get_device_mode(AsphodelDevice_t *device, uint8_t mode,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_device_mode",
                                  [POINTER(c_uint8)])

    def setup_device_type_h_prototypes(self):
        # int asphodel_supports_rf_power_commands(AsphodelDevice_t *device)
        self.load_library_function("asphodel_supports_rf_power_commands",
                                   c_int, [POINTER(self.AsphodelDeviceStruct)],
                                   None)

        # int asphodel_supports_radio_commands(AsphodelDevice_t *device)
        self.load_library_function("asphodel_supports_radio_commands",
                                   c_int, [POINTER(self.AsphodelDeviceStruct)],
                                   None)

        # int asphodel_supports_remote_commands(AsphodelDevice_t *device)
        self.load_library_function("asphodel_supports_remote_commands",
                                   c_int, [POINTER(self.AsphodelDeviceStruct)],
                                   None)

        # int asphodel_supports_bootloader_commands(AsphodelDevice_t *device)
        self.load_library_function("asphodel_supports_bootloader_commands",
                                   c_int, [POINTER(self.AsphodelDeviceStruct)],
                                   None)

    def setup_low_level_h_prototypes(self):
        # int asphodel_get_gpio_port_count(AsphodelDevice_t *device,
        #         int *count, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_gpio_port_count",
                                  [POINTER(c_int)])

        # int asphodel_get_gpio_port_name(AsphodelDevice_t *device, int index,
        #         char *buffer, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_gpio_port_name",
                                  [c_int, c_char_p, POINTER(c_uint8)])

        # int asphodel_get_gpio_port_info(AsphodelDevice_t *device, int index,
        #         AsphodelGPIOPortInfo_t *gpio_port_info,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_gpio_port_info",
                                  [c_int, POINTER(self.AsphodelGPIOPortInfo)])

        # int asphodel_get_gpio_port_values(AsphodelDevice_t *device,
        #         int index, uint32_t *pin_values,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_gpio_port_values",
                                  [c_int, POINTER(c_uint32)])

        # int asphodel_set_gpio_port_modes(AsphodelDevice_t *device, int index,
        #         uint8_t mode, uint32_t pins,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_set_gpio_port_modes",
                                  [c_int, c_uint8, c_uint32])

        # int asphodel_disable_gpio_overrides(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_disable_gpio_overrides", [])

        # int asphodel_get_bus_counts(AsphodelDevice_t *device, int *spi_count,
        #         int *i2c_count, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_bus_counts",
                                  [POINTER(c_int), POINTER(c_int)])
        # int asphodel_set_spi_cs_mode(AsphodelDevice_t *device, int index,
        #         uint8_t cs_mode, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_set_spi_cs_mode",
                                  [c_int, c_uint8])

        # int asphodel_do_spi_transfer(AsphodelDevice_t *device, int index,
        #         uint8_t *tx_data, uint8_t *rx_data, uint8_t data_length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_do_spi_transfer",
                                  [c_int, POINTER(c_uint8), POINTER(c_uint8),
                                   c_uint8])

        # int asphodel_do_i2c_write(AsphodelDevice_t *device, int index,
        #         uint8_t addr, uint8_t *tx_data, uint8_t write_length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_do_i2c_write",
                                  [c_int, c_uint8, POINTER(c_uint8), c_uint8])

        # int asphodel_do_i2c_read(AsphodelDevice_t *device, int index,
        #         uint8_t addr, uint8_t *rx_data, uint8_t read_length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_do_i2c_read",
                                  [c_int, c_uint8, POINTER(c_uint8), c_uint8])

        # int asphodel_do_i2c_write_read(AsphodelDevice_t *device, int index,
        #         uint8_t addr, uint8_t *tx_data, uint8_t write_length,
        #         uint8_t *rx_data, uint8_t read_length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_do_radio_fixed_test",
                                  [c_int, c_uint8, POINTER(c_uint8), c_uint8,
                                   POINTER(c_uint8), c_uint8])

        # int asphodel_do_radio_fixed_test(AsphodelDevice_t *device,
        #         uint16_t channel, uint16_t duration, uint8_t mode,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_do_radio_fixed_test",
                                  [c_uint16, c_uint16, c_uint8])

        # int asphodel_do_radio_sweep_test(AsphodelDevice_t *device,
        #         uint16_t start_channel, uint16_t stop_channel,
        #         uint16_t hop_interval, uint16_t hop_count, uint8_t mode,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_do_radio_sweep_test",
                                  [c_uint16, c_uint16, c_uint16, c_uint16,
                                   c_uint8])

        # int asphodel_get_info_region_count(AsphodelDevice_t *device,
        #         int *count, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_info_region_count",
                                  [POINTER(c_int)])

        # int asphodel_get_info_region_name(AsphodelDevice_t *device,
        #         int index, char *buffer, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_info_region_name",
                                  [c_int, c_char_p, POINTER(c_uint8)])

        # int asphodel_get_info_region(AsphodelDevice_t *device, int index,
        #         uint8_t *data, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_info_region",
                                  [c_int, POINTER(c_uint8), POINTER(c_uint8)])

        # int asphodel_get_stack_info(AsphodelDevice_t *device,
        #         uint32_t *stack_info, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_stack_info", [c_uint32 * 2])

        # int asphodel_echo_raw(AsphodelDevice_t *device, uint8_t *data,
        #         size_t data_length, uint8_t *reply, size_t *reply_length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_echo_raw",
                                  [POINTER(c_uint8), c_size_t,
                                   POINTER(c_uint8), POINTER(c_size_t)])

        # int asphodel_echo_transaction(AsphodelDevice_t *device,
        #         uint8_t *data, size_t data_length, uint8_t *reply,
        #         size_t *reply_length, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_echo_transaction",
                                  [POINTER(c_uint8), c_size_t,
                                   POINTER(c_uint8), POINTER(c_size_t)])

        # int asphodel_echo_params(AsphodelDevice_t *device, uint8_t *data,
        #         size_t data_length, uint8_t *reply, size_t *reply_length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_echo_params",
                                  [POINTER(c_uint8), c_size_t,
                                   POINTER(c_uint8), POINTER(c_size_t)])

    def setup_mem_test_h_prototypes(self):
        try:
            # int asphodel_mem_test_supported(void)
            self.load_library_function("asphodel_mem_test_supported", c_int,
                                       [], None, ignore_missing=False)

            self.mem_test_supported = self.lib.asphodel_mem_test_supported()
        except AttributeError:
            self.mem_test_supported = False

        # void asphodel_mem_test_set_limit(int limit)
        self.load_library_function("asphodel_mem_test_set_limit", None,
                                   [c_int], None)

        # int asphodel_mem_test_get_limit(void)
        self.load_library_function("asphodel_mem_test_get_limit", c_int, [],
                                   None)

    def setup_radio_h_prototypes(self):
        # int asphodel_stop_radio(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_stop_radio", [])

        # int asphodel_start_radio_scan(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_start_radio_scan", [])

        # int asphodel_get_raw_radio_scan_results(AsphodelDevice_t *device,
        #         uint32_t *serials, size_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_raw_radio_scan_results",
                                  [POINTER(c_uint32), POINTER(c_size_t)])

        # int asphodel_get_radio_scan_results(AsphodelDevice_t *device,
        #         uint32_t **serials, size_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function(
            "asphodel_get_radio_scan_results",
            [POINTER(POINTER(c_uint32)), POINTER(c_size_t)])

        # void asphodel_free_radio_scan_results(uint32_t *serials)
        self.load_library_function("asphodel_free_radio_scan_results", None,
                                   [POINTER(c_uint32)], None)

        # int asphodel_get_raw_radio_extra_scan_results(
        #         AsphodelDevice_t *device, AsphodelExtraScanResult_t *results,
        #         size_t *length, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_raw_radio_extra_scan_results",
                                  [POINTER(self.AsphodelExtraScanResult),
                                   POINTER(c_size_t)])

        # int asphodel_get_radio_extra_scan_results(AsphodelDevice_t *device,
        #         AsphodelExtraScanResult_t **results, size_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function(
            "asphodel_get_radio_extra_scan_results",
            [POINTER(POINTER(self.AsphodelExtraScanResult)),
             POINTER(c_size_t)])

        # void asphodel_free_radio_extra_scan_results(
        #         AsphodelExtraScanResult_t *results)
        self.load_library_function(
            "asphodel_free_radio_extra_scan_results", None,
            [POINTER(self.AsphodelExtraScanResult)], None)

        # int asphodel_get_radio_scan_power(AsphodelDevice_t *device,
        #         const uint32_t *serials, int8_t *powers, size_t length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_radio_scan_power",
                                  [POINTER(c_uint32), POINTER(c_int8),
                                   c_size_t])

        # int asphodel_connect_radio(AsphodelDevice_t *device,
        #         uint32_t serial_number, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_connect_radio", [c_uint32])

        # int asphodel_get_radio_status(AsphodelDevice_t *device,
        #         int *connected, uint32_t *serial_number,
        #         uint8_t *protocol_type, int *scanning,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function(
            "asphodel_get_radio_status", [POINTER(c_int), POINTER(c_uint32),
                                          POINTER(c_uint8), POINTER(c_int)])

        # int asphodel_get_radio_ctrl_vars(AsphodelDevice_t *device,
        #         uint8_t *ctrl_var_indexes, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_radio_ctrl_vars",
                                  [POINTER(c_uint8), POINTER(c_uint8)])

        # int asphodel_get_radio_default_serial(AsphodelDevice_t *device,
        #         uint32_t *serial_number, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_radio_default_serial",
                                  [POINTER(c_uint32)])

        # int asphodel_start_radio_scan_boot(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_start_radio_scan_boot", [])

        # int asphodel_connect_radio_boot(AsphodelDevice_t *device,
        #         uint32_t serial_number, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_connect_radio_boot", [c_uint32])

        # int asphodel_stop_remote(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_stop_remote", [])

        # int asphodel_restart_remote(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_restart_remote", [])

        # int asphodel_get_remote_status(AsphodelDevice_t *device,
        #         int *connected, uint32_t *serial_number,
        #         uint8_t *protocol_type, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_remote_status",
                                  [POINTER(c_int), POINTER(c_uint32),
                                   POINTER(c_uint8)])

        # int asphodel_restart_remote_app(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_restart_remote_app", [])
        # int asphodel_restart_remote_boot(AsphodelDevice_t *device,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_restart_remote_boot", [])

    def setup_rf_power_h_prototypes(self):
        # int asphodel_enable_rf_power(AsphodelDevice_t *device, int enable,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_enable_rf_power", [c_int])

        # int asphodel_get_rf_power_status(AsphodelDevice_t *device,
        #         int *enabled, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_rf_power_status",
                                  [POINTER(c_int)])

        # int asphodel_get_rf_power_ctrl_vars(AsphodelDevice_t *device,
        #         uint8_t *ctrl_var_indexes, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_rf_power_ctrl_vars",
                                  [POINTER(c_uint8), POINTER(c_uint8)])

        # int asphodel_reset_rf_power_timeout(AsphodelDevice_t *device,
        #         uint32_t timeout, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_reset_rf_power_timeout",
                                  [c_uint32])

    def setup_setting_h_prototypes(self):
        # int asphodel_get_setting_count(AsphodelDevice_t *device, int *count,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_setting_count",
                                  [POINTER(c_int)])

        # int asphodel_get_setting_name(AsphodelDevice_t *device, int index,
        #         char *buffer, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_setting_name",
                                  [c_int, c_char_p, POINTER(c_uint8)])

        # int asphodel_get_setting_info(AsphodelDevice_t *device, int index,
        #         AsphodelSettingInfo_t *setting_info,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_setting_info",
                                  [c_int, POINTER(AsphodelSettingInfo)])

        # int asphodel_get_setting_default(AsphodelDevice_t *device, int index,
        #         uint8_t *default_bytes, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_setting_default",
                                  [c_int, POINTER(c_uint8), POINTER(c_uint8)])

        # int asphodel_get_custom_enum_counts(AsphodelDevice_t *device,
        #         uint8_t *counts, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_custom_enum_counts",
                                  [POINTER(c_uint8), POINTER(c_uint8)])

        # int asphodel_get_custom_enum_value_name(AsphodelDevice_t *device,
        #         int index, int value, char *buffer, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_custom_enum_value_name",
                                  [c_int, c_int, c_char_p, POINTER(c_uint8)])

        # int asphodel_get_setting_category_count(AsphodelDevice_t *device,
        #         int *count, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_setting_category_count",
                                  [POINTER(c_int)])

        # int asphodel_get_setting_category_name(AsphodelDevice_t *device,
        #         int index, char *buffer, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_setting_category_name",
                                  [c_int, c_char_p, POINTER(c_uint8)])

        # int asphodel_get_setting_category_settings(AsphodelDevice_t *device,
        #         int index, uint8_t *settings, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_setting_category_settings",
                                  [c_int, POINTER(c_uint8), POINTER(c_uint8)])

    def setup_stream_h_prototypes(self):
        # int asphodel_get_stream_count(AsphodelDevice_t *device, int *count,
        #         uint8_t *filler_bits, uint8_t *id_bits,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_stream_count",
                                  [POINTER(c_int), POINTER(c_uint8),
                                   POINTER(c_uint8)])

        # int asphodel_get_stream(AsphodelDevice_t *device, int index,
        #         AsphodelStreamInfo_t **stream_info,
        #         AsphodelCommandCallback_t callback, void * closure)

        self.load_device_function("asphodel_get_stream",
                                  [c_int,
                                   POINTER(POINTER(AsphodelStreamInfo))])

        # void asphodel_free_stream(AsphodelStreamInfo_t *stream_info)
        self.load_library_function("asphodel_free_stream", None,
                                   [POINTER(AsphodelStreamInfo)], None)

        # int asphodel_get_stream_channels(AsphodelDevice_t *device, int index,
        #         uint8_t *channels, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)

        self.load_device_function("asphodel_get_stream_channels",
                                  [c_int, POINTER(c_uint8), POINTER(c_uint8)])

        # int asphodel_get_stream_format(AsphodelDevice_t *device, int index,
        #         AsphodelStreamInfo_t *stream_info,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_stream_format",
                                  [c_int, POINTER(AsphodelStreamInfo)])

        # int asphodel_enable_stream(AsphodelDevice_t *device, int index,
        #         int enable, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_enable_stream", [c_int, c_int])

        # int asphodel_warm_up_stream(AsphodelDevice_t *device, int index,
        #         int enable, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_warm_up_stream", [c_int, c_int])

        # int asphodel_get_stream_status(AsphodelDevice_t *device, int index,
        #         int *enable, int *warm_up,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_stream_status",
                                  [c_int, POINTER(c_int), POINTER(c_int)])

        # int asphodel_get_stream_rate_info(AsphodelDevice_t *device,
        #         int index, int *available, int *channel_index, int *invert,
        #         float *scale, float *offset,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_stream_rate_info",
                                  [c_int, POINTER(c_int), POINTER(c_int),
                                   POINTER(c_int), POINTER(c_float),
                                   POINTER(c_float)])

        # int asphodel_get_channel_count(AsphodelDevice_t *device, int *count,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_channel_count",
                                  [POINTER(c_int)])

        # int asphodel_get_channel(AsphodelDevice_t *device, int index,
        #         AsphodelChannelInfo_t **channel_info,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_channel",
                                  [c_int,
                                   POINTER(POINTER(AsphodelChannelInfo))])

        # void asphodel_free_channel(AsphodelChannelInfo_t *channel_info)
        self.load_library_function("asphodel_free_channel", None,
                                   [POINTER(AsphodelChannelInfo)], None)

        # int asphodel_get_channel_name(AsphodelDevice_t *device, int index,
        #         char *buffer, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_channel_name",
                                  [c_int, c_char_p, POINTER(c_uint8)])

        # int asphodel_get_channel_info(AsphodelDevice_t *device, int index,
        #         AsphodelChannelInfo_t *channel_info,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_channel_info",
                                  [c_int, POINTER(AsphodelChannelInfo)])

        # int asphodel_get_channel_coefficients(AsphodelDevice_t *device,
        #         int index, float *coefficients, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_channel_coefficients",
                                  [c_int, POINTER(c_float), POINTER(c_uint8)])

        # int asphodel_get_channel_chunk(AsphodelDevice_t *device,
        #         int index, uint8_t chunk_number, uint8_t *chunk,
        #         uint8_t *length, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_get_channel_chunk",
                                  [c_int, c_uint8, POINTER(c_uint8),
                                   POINTER(c_uint8)])

        # int asphodel_channel_specific(AsphodelDevice_t *device, int index,
        #         uint8_t *data, uint8_t data_length, uint8_t *reply,
        #         uint8_t *reply_length, AsphodelCommandCallback_t callback,
        #         void * closure)
        self.load_device_function("asphodel_channel_specific",
                                  [c_int, POINTER(c_uint8), c_uint8,
                                   POINTER(c_uint8), POINTER(c_uint8)])

        # int asphodel_get_channel_calibration(AsphodelDevice_t *device,
        #         int index, int *available,
        #         AsphodelChannelCalibration_t *calibration,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_channel_calibration",
                                  [c_int, POINTER(c_int),
                                   POINTER(self.AsphodelChannelCalibration)])

    def setup_supply_h_prototypes(self):
        # int asphodel_get_supply_count(AsphodelDevice_t *device, int *count,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_supply_count",
                                  [POINTER(c_int)])

        # int asphodel_get_supply_name(AsphodelDevice_t *device, int index,
        #         char *buffer, uint8_t *length,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_supply_name",
                                  [c_int, c_char_p, POINTER(c_uint8)])

        # int asphodel_get_supply_info(AsphodelDevice_t *device, int index,
        #         AsphodelSupplyInfo_t *supply_info,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_get_supply_info",
                                  [c_int, POINTER(self.AsphodelSupplyInfo)])

        # int asphodel_check_supply(AsphodelDevice_t *device, int index,
        #         int32_t *measurement, uint8_t *result, int tries,
        #         AsphodelCommandCallback_t callback, void * closure)
        self.load_device_function("asphodel_check_supply",
                                  [c_int, POINTER(c_int32), POINTER(c_uint8),
                                   c_uint])

    def setup_tcp_h_prototypes(self):
        try:
            # int asphodel_tcp_devices_supported(void)
            self.load_library_function("asphodel_tcp_devices_supported", c_int,
                                       [], None, ignore_missing=False)

            s = self.lib.asphodel_tcp_devices_supported()
            self.tcp_devices_supported = s
        except AttributeError:
            self.tcp_devices_supported = False

        # int asphodel_tcp_init(void)
        self.load_library_function("asphodel_tcp_init", c_int, [],
                                   self.asphodel_error_check)

        # void asphodel_tcp_deinit(void)
        self.load_library_function("asphodel_tcp_deinit", None, [], None)

        # int asphodel_tcp_find_devices(AsphodelDevice_t **device_list,
        #         size_t *list_size)
        self.load_library_function(
            "asphodel_tcp_find_devices", c_int,
            [POINTER(POINTER(self.AsphodelDeviceStruct)), POINTER(c_size_t)],
            self.asphodel_error_check)

        # int asphodel_tcp_find_devices_filter(AsphodelDevice_t **device_list,
        #         size_t *list_size, uint32_t flags)
        self.load_library_function(
            "asphodel_tcp_find_devices_filter", c_int,
            [POINTER(POINTER(self.AsphodelDeviceStruct)), POINTER(c_size_t),
             c_uint32], self.asphodel_error_check)

        # Asphodel_TCPAdvInfo_t* asphodel_tcp_get_advertisement(
        #         AsphodelDevice_t* device)
        self.load_library_function(
            "asphodel_tcp_get_advertisement", POINTER(self.AsphodelTCPAdvInfo),
            [POINTER(self.AsphodelDeviceStruct)], None)

        # int asphodel_tcp_create_device(const char* host, uint16_t port,
        #         int timeout, const char* serial, AsphodelDevice_t **device)
        self.load_library_function(
            "asphodel_tcp_create_device", c_int,
            [c_char_p, c_uint16, c_int, c_char_p,
             POINTER(POINTER(self.AsphodelDeviceStruct))],
            self.asphodel_error_check)

    def setup_unit_format_h_prototypes(self):
        # AsphodelUnitFormatter_t* asphodel_create_unit_formatter(
        #         uint8_t unit_type, double minimum, double maximum,
        #         double resolution, int use_metric)
        self.load_library_function(
            "asphodel_create_unit_formatter",
            POINTER(self.AsphodelUnitFormatter),
            [c_uint8, c_double, c_double, c_double, c_int], None)

        # AsphodelUnitFormatter_t* asphodel_create_custom_unit_formatter(
        #         double scale, double offset, double resolution,
        #         const char *unit_ascii, const char *unit_utf8,
        #         const char *unit_html)
        self.load_library_function(
            "asphodel_create_custom_unit_formatter",
            POINTER(self.AsphodelUnitFormatter),
            [c_double, c_double, c_double, c_char_p, c_char_p, c_char_p], None)

        # int asphodel_format_value_ascii(char *buffer, size_t buffer_size,
        #         uint8_t unit_type, double resolution, int use_metric,
        #         double value)
        self.load_library_function("asphodel_format_value_ascii", c_int,
                                   [c_char_p, c_size_t, c_uint8, c_double,
                                    c_int, c_double], None)

        # int asphodel_format_value_utf8(char *buffer, size_t buffer_size,
        #         uint8_t unit_type, double resolution, int use_metric,
        #         double value)
        self.load_library_function("asphodel_format_value_utf8", c_int,
                                   [c_char_p, c_size_t, c_uint8, c_double,
                                    c_int, c_double], None)

        # int asphodel_format_value_html(char *buffer, size_t buffer_size,
        #         uint8_t unit_type, double resolution, int use_metric,
        #         double value)
        self.load_library_function("asphodel_format_value_html", c_int,
                                   [c_char_p, c_size_t, c_uint8, c_double,
                                    c_int, c_double], None)

    def setup_usb_h_prototypes(self):
        try:
            # int asphodel_usb_devices_supported(void)
            self.load_library_function("asphodel_usb_devices_supported", c_int,
                                       [], None, ignore_missing=False)

            s = self.lib.asphodel_usb_devices_supported()
            self.usb_devices_supported = s
        except AttributeError:
            # NOTE: any DLL too old to support this check will support USB
            # and we can continue loading the rest of the functions
            self.usb_devices_supported = True

        # int asphodel_usb_init(void)
        self.load_library_function("asphodel_usb_init", c_int, [],
                                   self.asphodel_error_check)

        # void asphodel_usb_deinit(void)
        self.load_library_function("asphodel_usb_deinit", None, [], None)

        # int asphodel_usb_find_devices(AsphodelDevice_t **device_list,
        #         size_t *list_size)
        self.load_library_function(
            "asphodel_usb_find_devices", c_int,
            [POINTER(POINTER(self.AsphodelDeviceStruct)), POINTER(c_size_t)],
            self.asphodel_error_check)

        # const char * asphodel_usb_get_backend_version(void)
        self.load_library_function(
            "asphodel_usb_get_backend_version", c_char_p, [], None)

    def setup_version_h_prototypes(self):
        # uint16_t asphodel_get_library_protocol_version(void)
        self.load_library_function(
            "asphodel_get_library_protocol_version", c_uint16, [], None)

        # const char * asphodel_get_library_protocol_version_string(void)
        self.load_library_function(
            "asphodel_get_library_protocol_version_string", c_char_p, [], None)

        # const char * asphodel_get_library_build_info(void)
        self.load_library_function(
            "asphodel_get_library_build_info", c_char_p, [], None)

        # const char * asphodel_get_library_build_date(void)
        self.load_library_function(
            "asphodel_get_library_build_date", c_char_p, [], None)

    def find_usb_devices(self):
        count = c_size_t(0)

        # first get a count of how many devices are on the system:
        self.lib.asphodel_usb_find_devices(None, byref(count))

        array_size = count.value

        if array_size == 0:
            return []

        array = (POINTER(self.AsphodelDeviceStruct) * array_size)()

        array_ptr = cast(byref(array),
                         POINTER(POINTER(self.AsphodelDeviceStruct)))
        self.lib.asphodel_usb_find_devices(array_ptr, byref(count))

        array_entries = min(array_size, count.value)

        device_list = []
        for i in range(array_entries):
            device_list.append(AsphodelNativeDevice(self, (array[i].contents)))
        return device_list

    def find_tcp_devices(self, flags=None):
        if flags is None:
            flags = ASPHODEL_TCP_FILTER_DEFAULT

        # provide an array of 10 for the first attempt
        array_size = 100
        count = c_size_t(array_size)
        array = (POINTER(self.AsphodelDeviceStruct) * array_size)()
        array_ptr = cast(byref(array),
                         POINTER(POINTER(self.AsphodelDeviceStruct)))

        # first try
        self.lib.asphodel_tcp_find_devices_filter(
            array_ptr, byref(count), flags)

        if count.value > array_size:
            # there are too many devices for the initial array.

            # free the original list
            for i in range(array_size):
                device = array[i].contents
                device.free_device(device)

            array_size = count.value
            array = (POINTER(self.AsphodelDeviceStruct) * array_size)()
            array_ptr = cast(byref(array),
                             POINTER(POINTER(self.AsphodelDeviceStruct)))

            # try again
            self.lib.asphodel_tcp_find_devices_filter(
                array_ptr, byref(count), flags)

            device_count = min(count.value, array_size)
        else:
            device_count = count.value

        device_list = []
        for i in range(device_count):
            device_list.append(AsphodelNativeDevice(self, (array[i].contents)))
        return device_list

    def create_tcp_device(self, host, port, timeout, serial=None):
        device_ptr = POINTER(self.AsphodelDeviceStruct)()

        if serial:
            serial_bytes = serial.encode("UTF-8")
        else:
            serial_bytes = None

        self.lib.asphodel_tcp_create_device(
            host.encode("UTF-8"), port, timeout, serial_bytes,
            byref(device_ptr))

        return AsphodelNativeDevice(self, device_ptr.contents)

    def tcp_get_advertisement(self, device):
        adv_ptr = self.lib.asphodel_tcp_get_advertisement(device)
        adv = adv_ptr.contents

        def decode_safe(b):
            try:
                return b.decode("UTF-8")
            except UnicodeDecodeError:
                return "ERROR"

        return TCPAdvInfo(
            adv.tcp_version, bool(adv.connected),
            adv.max_incoming_param_length, adv.max_outgoing_param_length,
            adv.stream_packet_length, adv.protocol_type,
            decode_safe(adv.serial_number), adv.board_rev,
            decode_safe(adv.board_type), decode_safe(adv.build_info),
            decode_safe(adv.build_date), decode_safe(adv.user_tag1),
            decode_safe(adv.user_tag2), adv.remote_max_incoming_param_length,
            adv.remote_max_outgoing_param_length,
            adv.remote_stream_packet_length)

    def create_channel_decoder(self, channel_info, bit_offset):
        decoder_ptr = POINTER(self.AsphodelChannelDecoder)()
        self.lib.asphodel_create_channel_decoder(channel_info, bit_offset,
                                                 byref(decoder_ptr))
        return AsphodelNativeChannelDecoder(self, decoder_ptr.contents,
                                            channel_info)

    def create_stream_decoder(self, stream_info, channel_info_list,
                              bit_offset):
        decoder_ptr = POINTER(self.AsphodelStreamDecoder)()
        array_type = POINTER(AsphodelChannelInfo) * len(channel_info_list)
        channel_array = array_type(*(pointer(c) for c in channel_info_list))
        stream_and_channels = self.AsphodelStreamAndChannels()
        stream_and_channels.stream_info = pointer(stream_info)
        stream_and_channels.channel_info = cast(
            channel_array, POINTER(POINTER(AsphodelChannelInfo)))
        self.lib.asphodel_create_stream_decoder(byref(stream_and_channels),
                                                bit_offset, byref(decoder_ptr))
        return AsphodelNativeStreamDecoder(self, decoder_ptr.contents,
                                           stream_info, channel_info_list,
                                           bit_offset)

    def create_device_decoder(self, info_list, filler_bits, id_bits):
        """
        info_list is a sequence of tuples of (stream_id, stream_info,
        channel_info_list).
        """
        decoder_ptr = POINTER(self.AsphodelDeviceDecoder)()
        array_size = len(info_list)
        info_array = (self.AsphodelStreamAndChannels * array_size)()
        for i, (stream_id, stream_info, ch_info_list) in enumerate(info_list):
            info_array[i].stream_id = stream_id
            info_array[i].stream_info = pointer(stream_info)
            array_type = POINTER(AsphodelChannelInfo) * len(ch_info_list)
            ch_array = array_type(*(pointer(c) for c in ch_info_list))
            info_array[i].channel_info = cast(
                ch_array, POINTER(POINTER(AsphodelChannelInfo)))
        self.lib.asphodel_create_device_decoder(
            cast(info_array, POINTER(self.AsphodelStreamAndChannels)),
            array_size, filler_bits, id_bits, byref(decoder_ptr))
        return AsphodelNativeDeviceDecoder(self, decoder_ptr.contents,
                                           info_list[:], filler_bits, id_bits)

    def get_streaming_counts(self, streams, response_time, buffer_time,
                             timeout):
        """
        returns (packet_count, transfer_count, timeout)
        """
        packet_count = c_int()
        transfer_count = c_int()
        timeout = c_uint(timeout)
        array_size = len(streams)
        info_array = (self.AsphodelStreamAndChannels * array_size)()
        for i, stream_info in enumerate(streams):
            info_array[i].stream_info = pointer(stream_info)
        self.lib.asphodel_get_streaming_counts(
            cast(info_array, POINTER(self.AsphodelStreamAndChannels)),
            array_size, response_time, buffer_time, byref(packet_count),
            byref(transfer_count), byref(timeout))
        return (packet_count.value, transfer_count.value, timeout.value)

    def create_unit_formatter(self, unit_type, minimum, maximum, resolution,
                              use_metric=True):
        use_metric_int = 1 if use_metric else 0
        formatter = self.lib.asphodel_create_unit_formatter(unit_type, minimum,
                                                            maximum,
                                                            resolution,
                                                            use_metric_int)
        if not formatter:
            raise AsphodelError(
                0, "asphodel_create_unit_formatter returned NULL")
        recreate = (recreate_unit_formatter, (unit_type, minimum, maximum,
                                              resolution, use_metric))
        return AsphodelNativeUnitFormatter(self, formatter.contents, recreate)

    def create_custom_unit_formatter(self, scale, offset, resolution,
                                     unit_ascii, unit_utf8, unit_html):
        formatter = self.lib.asphodel_create_custom_unit_formatter(
            scale, offset, resolution, unit_ascii.encode("ascii"),
            unit_utf8.encode("UTF-8"), unit_html.encode("ascii"))
        if not formatter:
            raise AsphodelError(
                0, "asphodel_create_custom_unit_formatter returned NULL")
        recreate = (recreate_custom_unit_formatter, (scale, offset, resolution,
                                                     unit_ascii, unit_utf8,
                                                     unit_html))
        return AsphodelNativeUnitFormatter(self, formatter.contents, recreate)

    def _format_value(self, lib_func, unit_type, resolution, value,
                      use_metric):
        use_metric_int = 1 if use_metric else 0
        buffer = create_string_buffer(256)
        lib_func(buffer, len(buffer), unit_type, resolution, use_metric_int,
                 value)
        return buffer.value

    def format_value_ascii(self, unit_type, resolution, value,
                           use_metric=True):
        b = self._format_value(self.lib.asphodel_format_value_ascii, unit_type,
                               resolution, value, use_metric)
        return b.decode("ascii")

    def format_value_utf8(self, unit_type, resolution, value, use_metric=True):
        b = self._format_value(self.lib.asphodel_format_value_utf8, unit_type,
                               resolution, value, use_metric)
        return b.decode("UTF-8")

    def format_value_html(self, unit_type, resolution, value, use_metric=True):
        b = self._format_value(self.lib.asphodel_format_value_html, unit_type,
                               resolution, value, use_metric)
        return b.decode("ascii")

    def mem_test_set_limit(self, limit):
        self.lib.asphodel_mem_test_set_limit(limit)

    def mem_test_get_limit(self):
        return self.lib.asphodel_mem_test_get_limit()


def asphodel_command(func_base):
    def decorator(f):
        @functools.wraps(f)
        def function(self, *args, callback=None, **kwargs):
            gen = f(self, *args, **kwargs)
            args = next(gen)  # call the initialization

            if callback is None:
                # want the blocking method
                lib_func = getattr(self.lib.lib, func_base + "_blocking")
                lib_func(*args)
                try:
                    return next(gen)
                except StopIteration as e:
                    return e.value
            else:
                # want the non-blocking method
                if callback is False:
                    # want no callback
                    callback = None
                lib_func = getattr(self.lib.lib, func_base)

                def function_callback(status, closure):
                    try:
                        try:
                            value = next(gen)
                        except StopIteration as e:
                            value = e.value
                        if callback:
                            callback(status, value)
                    except Exception:
                        pass  # nothing can be done about it here
                    self._callbacks.remove(c_cb)
                c_cb = self.lib.AsphodelCommandCallback(function_callback)
                self._callbacks.append(c_cb)

                new_args = list(args)
                new_args.append(c_cb)
                new_args.append(None)

                try:
                    lib_func(*new_args)
                except Exception:
                    self._callbacks.remove(c_cb)
                    raise
        return function
    return decorator


class AsphodelNativeDevice:
    MAX_STRING_LENGTH = 128

    def __init__(self, lib, device):
        self.lib = lib
        self.device = device
        self._callbacks = []
        self._remote = None

        if self.get_transport_type() == "usb":
            self.reconnect_time = 5.0
        else:
            self.reconnect_time = 10.0

        if self.lib:
            self.lib.device_list.add(self)

    def open(self):
        ret = self.device.open_device(self.device)
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)

    def close(self):
        if self.device:
            self.device.close_device(self.device)

    def free(self):
        self.close()
        if self.device:
            self.device.free_device(self.device)
        self.device = None
        self.lib = None

    def __del__(self):
        self.free()

    def get_location_string(self):
        return self.device.location_string.decode("UTF-8")

    def get_transport_type(self):
        if self.lib.protocol_version >= 0x203:
            return self.device.transport_type.decode("UTF-8")
        else:
            # library is too old to support transport type; must be USB
            return "usb"

    def get_serial_number(self):
        buffer = create_string_buffer(64)
        ret = self.device.get_serial_number(self.device, buffer, len(buffer))
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)
        return buffer.value.decode("UTF-8")

    def do_transfer(self, cmd, params, callback):
        if params is None:
            params = []
        param_array_type = c_uint8 * len(params)
        param_array = param_array_type.from_buffer_copy(bytes(params))

        def cb(status, params, param_length, closure):
            if params:
                array_type = POINTER(c_uint8 * param_length)
                param_bytes = bytes(cast(params, array_type).contents)
            else:
                param_bytes = None
            try:
                callback(status, param_bytes)
            except Exception:
                pass  # nothing can be done about it here
            self._callbacks.remove(c_callback)

        c_callback = self.lib.AsphodelTransferCallback(cb)
        self._callbacks.append(c_callback)

        ret = self.device.do_transfer(self.device, cmd, param_array,
                                      len(param_array), c_callback, None)
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)

    def do_transfer_blocking(self, cmd, params=None):
        """
        This function is for testing purposes only!
        """
        finished = threading.Event()
        result = None

        def callback(status, param_bytes):
            nonlocal result
            result = (status, param_bytes)
            finished.set()
        self.do_transfer(cmd, params, callback)

        while not finished.is_set():
            self.poll_device(100)

        ret, params = result

        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)
        else:
            return params

    def do_transfer_reset(self, cmd, params, callback):
        if params is None:
            params = []
        param_array_type = c_uint8 * len(params)
        param_array = param_array_type.from_buffer_copy(bytes(params))

        def cb(status, params, param_length, closure):
            try:
                callback(status)
            except Exception:
                pass  # nothing can be done about it here
            self._callbacks.remove(c_callback)

        c_callback = self.lib.AsphodelTransferCallback(cb)
        self._callbacks.append(c_callback)

        ret = self.device.do_transfer_reset(self.device, cmd, param_array,
                                            len(param_array), c_callback, None)
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)

    def do_transfer_reset_blocking(self, cmd, params=None):
        """
        This function is for testing purposes only!
        """
        finished = threading.Event()
        ret = None

        def callback(status):
            nonlocal ret
            ret = status
            finished.set()
        self.do_transfer_reset(cmd, params, callback)

        while not finished.is_set():
            self.poll_device(100)

        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)

    def start_streaming_packets(self, packet_count, transfer_count, timeout,
                                callback):
        if callback:
            def cb(status, stream_data, packet_size, packet_count, closure):
                if stream_data:
                    array_type = POINTER((c_uint8 * packet_size) *
                                         packet_count)
                    array = cast(stream_data, array_type).contents
                    stream_packets = [bytes(a) for a in array]
                else:
                    stream_packets = []
                try:
                    callback(status, stream_packets)
                except Exception:
                    pass  # nothing can be done about it here

            c_callback = self.lib.AsphodelStreamingCallback(cb)
            ret = self.device.start_streaming_packets(self.device,
                                                      packet_count,
                                                      transfer_count, timeout,
                                                      c_callback, None)
            self._streaming_callback = c_callback
            if ret != 0:
                error_name = self.lib.lib.asphodel_error_name(ret)
                raise AsphodelError(ret, error_name)
        else:
            try:
                del self._streaming_callback
            except AttributeError:
                pass
            c_callback = self.lib.AsphodelStreamingCallback()
            ret = self.device.start_streaming_packets(self.device,
                                                      packet_count,
                                                      transfer_count, timeout,
                                                      c_callback, None)
            if ret != 0:
                error_name = self.lib.lib.asphodel_error_name(ret)
                raise AsphodelError(ret, error_name)

    def stop_streaming_packets(self):
        self.device.stop_streaming_packets(self.device)
        try:
            del self._streaming_callback
        except AttributeError:
            pass

    def get_stream_packets_blocking(self, byte_count, timeout):
        buffer = (c_uint8 * byte_count)()
        count_int = c_int(byte_count)
        ret = self.device.get_stream_packets_blocking(self.device, buffer,
                                                      byref(count_int),
                                                      timeout)
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)
        return bytes(buffer[0:count_int.value])

    def get_max_incoming_param_length(self):
        v = self.device.get_max_incoming_param_length(self.device)
        return v

    def get_max_outgoing_param_length(self):
        v = self.device.get_max_outgoing_param_length(self.device)
        return v

    def get_stream_packet_length(self):
        v = self.device.get_stream_packet_length(self.device)
        return v

    def poll_device(self, milliseconds):
        ret = self.device.poll_device(self.device, milliseconds, None)
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)

    def set_connect_callback(self, callback):
        if callback:
            # void (*)(int status, int connected, void * closure)
            def cb(status, connected, closure):
                try:
                    callback(status, connected)
                except Exception:
                    pass  # nothing can be done about it here

            c_callback = self.lib.AsphodelConnectCallback(cb)
            self._connect_callback = c_callback
        else:
            c_callback = self.lib.AsphodelConnectCallback()
            self._connect_callback = None

        ret = self.device.set_connect_callback(self.device, c_callback, None)
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)

    def wait_for_connect(self, timeout):
        ret = self.device.wait_for_connect(self.device, timeout)
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)

    def _get_raw_remote_device(self):
        remote_ptr = POINTER(self.lib.AsphodelDeviceStruct)()
        ret = self.device.get_remote_device(self.device, byref(remote_ptr))
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)
        return remote_ptr.contents

    def get_remote_device(self):
        if self._remote is None:
            remote = None
        else:
            remote = self._remote()

        if remote is None:
            remote_dev = self._get_raw_remote_device()
            remote = AsphodelNativeDevice(self.lib, remote_dev)
            self._remote = weakref.ref(remote)

        return remote

    def reconnect(self, bootloader=False, application=False,
                  serial_number=None):
        if bootloader and application:
            raise ValueError("cannot set both application and bootloader")
        elif bootloader:
            reconnect_func = self.reconnect_device_bootloader
        elif application:
            reconnect_func = self.reconnect_device_application
        else:
            reconnect_func = self.reconnect_device

        if not serial_number:
            try:
                serial_number = self.get_serial_number()
            except AsphodelError:
                pass

        end_time = time.monotonic() + self.reconnect_time

        # give the device some time to process
        time.sleep(0.5)

        while True:
            try:
                # try a reconnect
                reconnect_func(reopen=True)
                break
            except AsphodelError:
                if time.monotonic() >= end_time:
                    raise

            if serial_number:
                # scan for an identical serial number
                device = find_device_by_serial(serial_number)
                if device:
                    # give the device some time to process
                    time.sleep(0.5)

                    # try 1/2 reconnect
                    try:
                        reconnect_func(reopen=True)
                        break
                    except AsphodelError:
                        pass

                    # give the device some time to process
                    time.sleep(0.5)

                    # try 2/2 reconnect
                    try:
                        reconnect_func(reopen=True)
                        break
                    except AsphodelError:
                        pass

                    # use the device we found
                    native_device = device.device
                    device.device = None
                    self._reconnect_helper(native_device, reopen=True)
                    break

            # wait a bit to not hog resources
            time.sleep(0.25)

        self.wait_for_connect(int(self.reconnect_time * 1000))

    def _reconnect_helper(self, new_device, reopen):
        if addressof(new_device) == addressof(self.device):
            return

        self.close()
        if self.device:
            self.device.free_device(self.device)
        self.device = new_device
        if reopen:
            self.open()

        if self._remote is not None:
            remote = self._remote()
            if remote:
                try:
                    remote_dev = self._get_raw_remote_device()
                    remote.close()
                    remote.device.free_device(remote.device)
                    remote.device = remote_dev
                    if reopen:
                        remote.open()
                except AsphodelError:
                    pass

        self._callbacks.clear()

    def reconnect_device(self, reopen=False):
        reconnected_ptr = POINTER(self.lib.AsphodelDeviceStruct)()
        ret = self.device.reconnect_device(self.device, byref(reconnected_ptr))
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)
        self._reconnect_helper(reconnected_ptr.contents, reopen)

    def reconnect_device_bootloader(self, reopen=False):
        reconnected_ptr = POINTER(self.lib.AsphodelDeviceStruct)()
        ret = self.device.reconnect_device_bootloader(
            self.device, byref(reconnected_ptr))
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)
        self._reconnect_helper(reconnected_ptr.contents, reopen)

    def reconnect_device_application(self, reopen=False):
        reconnected_ptr = POINTER(self.lib.AsphodelDeviceStruct)()
        ret = self.device.reconnect_device_application(
            self.device, byref(reconnected_ptr))
        if ret != 0:
            error_name = self.lib.lib.asphodel_error_name(ret)
            raise AsphodelError(ret, error_name)
        self._reconnect_helper(reconnected_ptr.contents, reopen)

    def supports_rf_power_commands(self):
        v = self.lib.lib.asphodel_supports_rf_power_commands(self.device)
        return bool(v)

    def supports_radio_commands(self):
        v = self.lib.lib.asphodel_supports_radio_commands(self.device)
        return bool(v)

    def supports_remote_commands(self):
        v = self.lib.lib.asphodel_supports_remote_commands(self.device)
        return bool(v)

    def supports_bootloader_commands(self):
        v = self.lib.lib.asphodel_supports_bootloader_commands(self.device)
        return bool(v)

    def set_error_callback(self, callback):
        error_cb_type = CFUNCTYPE(
            None, POINTER(self.lib.AsphodelDeviceStruct), c_int, c_void_p)

        if callback:
            def cb(device, error_code, closure):
                try:
                    callback(self, error_code)
                except Exception:
                    pass  # nothing can be done about it here

            c_callback = error_cb_type(cb)
            self.device.error_callback = c_callback
            self._error_callback = c_callback
        else:
            self.device.error_callback = error_cb_type()
            self._error_callback = None

    def tcp_get_advertisement(self):
        return self.lib.tcp_get_advertisement(self.device)

    @asphodel_command("asphodel_get_protocol_version")
    def get_protocol_version(self):
        version = c_uint16()
        yield (self.device, byref(version))
        return version.value

    @asphodel_command("asphodel_get_protocol_version_string")
    def get_protocol_version_string(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_board_info")
    def get_board_info(self):
        rev = c_uint8()
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, byref(rev), cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return (buffer.value.decode("UTF-8"), rev.value)

    @asphodel_command("asphodel_get_user_tag_locations")
    def get_user_tag_locations(self):
        array = (c_size_t * 6)()
        yield (self.device, array)
        values = tuple(array)
        return tuple(zip(values[0::2], values[1::2]))

    @asphodel_command("asphodel_get_build_info")
    def get_build_info(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_build_date")
    def get_build_date(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_commit_id")
    def get_commit_id(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_repo_branch")
    def get_repo_branch(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_repo_name")
    def get_repo_name(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_chip_family")
    def get_chip_family(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_chip_model")
    def get_chip_model(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_chip_id")
    def get_chip_id(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_nvm_size")
    def get_nvm_size(self):
        size = c_size_t()
        yield (self.device, byref(size))
        return size.value

    @asphodel_command("asphodel_erase_nvm")
    def erase_nvm(self):
        yield (self.device,)

    @asphodel_command("asphodel_write_nvm_raw")
    def write_nvm_raw(self, address, values):
        data = (c_uint8 * len(values)).from_buffer_copy(bytes(values))
        yield (self.device, address, cast(byref(data), POINTER(c_uint8)),
               len(values))

    @asphodel_command("asphodel_write_nvm_section")
    def write_nvm_section(self, address, values):
        data = (c_uint8 * len(values)).from_buffer_copy(bytes(values))
        yield (self.device, address, cast(byref(data), POINTER(c_uint8)),
               len(values))

    @asphodel_command("asphodel_read_nvm_raw")
    def read_nvm_raw(self, address):
        max_length = self.get_max_incoming_param_length()
        data = (c_uint8 * max_length)()
        data_length = c_size_t(max_length)
        yield (self.device, address, cast(byref(data), POINTER(c_uint8)),
               byref(data_length))
        actual_length = min(max_length, data_length.value)
        return bytes(data[0:actual_length])

    @asphodel_command("asphodel_read_nvm_section")
    def read_nvm_section(self, address, length):
        data = (c_uint8 * length)()
        data_length = c_size_t(length)
        yield (self.device, address, cast(byref(data), POINTER(c_uint8)),
               data_length)
        return bytes(data)

    @asphodel_command("asphodel_read_user_tag_string")
    def read_user_tag_string(self, offset, length):
        buffer = create_string_buffer(length + 1)
        yield (self.device, offset, length, cast(byref(buffer), c_char_p))
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_write_user_tag_string")
    def write_user_tag_string(self, offset, length, string):
        buffer = create_string_buffer(string.encode("UTF-8"))
        yield (self.device, offset, length, cast(byref(buffer), c_char_p))

    @asphodel_command("asphodel_get_nvm_modified")
    def get_nvm_modified(self):
        modified = c_uint8()
        yield (self.device, byref(modified))
        return bool(modified.value)

    @asphodel_command("asphodel_get_nvm_hash")
    def get_nvm_hash(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_get_setting_hash")
    def get_setting_hash(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_flush")
    def flush(self):
        yield (self.device,)

    @asphodel_command("asphodel_reset")
    def reset(self):
        yield (self.device,)

    @asphodel_command("asphodel_get_bootloader_info")
    def get_bootloader_info(self):
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        yield (self.device, cast(byref(buffer), c_char_p),
               self.MAX_STRING_LENGTH)
        return buffer.value.decode("UTF-8")

    @asphodel_command("asphodel_bootloader_jump")
    def bootloader_jump(self):
        yield (self.device,)

    @asphodel_command("asphodel_get_reset_flag")
    def get_reset_flag(self):
        flag = c_uint8()
        yield (self.device, byref(flag))
        return flag.value

    @asphodel_command("asphodel_clear_reset_flag")
    def clear_reset_flag(self):
        yield (self.device,)

    @asphodel_command("asphodel_get_rgb_count")
    def get_rgb_count(self):
        count = c_int()
        yield (self.device, byref(count))
        return count.value

    @asphodel_command("asphodel_get_rgb_values")
    def get_rgb_values(self, index):
        values = (c_uint8 * 3)()
        yield (self.device, index, values)
        return tuple(values)

    @asphodel_command("asphodel_set_rgb_values")
    def set_rgb_values(self, index, values, instant=False):
        array = (c_uint8 * 3).from_buffer_copy(bytes(values))
        yield (self.device, index, array, instant)

    @asphodel_command("asphodel_set_rgb_values_hex")
    def set_rgb_values_hex(self, index, hex_color, instant=False):
        yield (self.device, index, hex_color, instant)

    @asphodel_command("asphodel_get_led_count")
    def get_led_count(self):
        count = c_int()
        yield (self.device, byref(count))
        return count.value

    @asphodel_command("asphodel_get_led_value")
    def get_led_value(self, index):
        value = c_uint8()
        yield (self.device, index, byref(value))
        return value.value

    @asphodel_command("asphodel_set_led_value")
    def set_led_value(self, index, value, instant=False):
        yield (self.device, index, value, instant)

    @asphodel_command("asphodel_set_device_mode")
    def set_device_mode(self, mode):
        yield (self.device, mode)

    @asphodel_command("asphodel_get_device_mode")
    def get_device_mode(self):
        mode = c_uint8()
        yield (self.device, byref(mode))
        return mode.value

    @asphodel_command("asphodel_get_stream_count")
    def get_stream_count(self):
        count = c_int()
        filler_bits = c_uint8()
        id_bits = c_uint8()
        yield (self.device, byref(count), byref(filler_bits), byref(id_bits))
        return (count.value, filler_bits.value, id_bits.value)

    @asphodel_command("asphodel_get_stream")
    def get_stream(self, index):
        ptr = POINTER(AsphodelStreamInfo)()
        yield (self.device, index, byref(ptr))
        stream = ptr.contents
        stream._free_func = self.lib.lib.asphodel_free_stream
        return stream

    @asphodel_command("asphodel_get_stream_channels")
    def get_stream_channels(self, index):
        channels = (c_uint8 * 255)()
        channels_length = c_uint8(255)
        yield (self.device, index, cast(byref(channels), POINTER(c_uint8)),
               byref(channels_length))
        return tuple(channels[0:channels_length.value])

    @asphodel_command("asphodel_get_stream_format")
    def get_stream_format(self, index):
        """
        Return (filler_bits, counter_bits, rate, rate_error, warm_up_delay)
        for a specific stream.
        """
        info = AsphodelStreamInfo()
        yield (self.device, index, byref(info))
        return StreamFormat(info.filler_bits, info.counter_bits,
                            info.rate, info.rate_error, info.warm_up_delay)

    @asphodel_command("asphodel_enable_stream")
    def enable_stream(self, index, enable=True):
        yield (self.device, index, enable)

    @asphodel_command("asphodel_warm_up_stream")
    def warm_up_stream(self, index, enable=True):
        yield (self.device, index, enable)

    @asphodel_command("asphodel_get_stream_status")
    def get_stream_status(self, index):
        enable = c_int()
        warm_up = c_int()
        yield (self.device, index, byref(enable), byref(warm_up))
        return (bool(enable.value), bool(warm_up.value))

    @asphodel_command("asphodel_get_stream_rate_info")
    def get_stream_rate_info(self, index):
        """
        Return (available, channel_index, invert, scale, offset) for a
        specific stream.
        """
        available = c_int()
        channel_index = c_int()
        invert = c_int()
        scale = c_float()
        offset = c_float()
        yield (self.device, index, byref(available), byref(channel_index),
               byref(invert), byref(scale), byref(offset))
        return StreamRateInfo(bool(available.value), channel_index.value,
                              invert.value, scale.value, offset.value)

    @asphodel_command("asphodel_get_channel_count")
    def get_channel_count(self):
        count = c_int()
        yield (self.device, byref(count))
        return count.value

    @asphodel_command("asphodel_get_channel")
    def get_channel(self, index):
        ptr = POINTER(AsphodelChannelInfo)()
        yield (self.device, index, byref(ptr))
        channel = ptr.contents
        channel._free_func = self.lib.lib.asphodel_free_channel
        return channel

    @asphodel_command("asphodel_get_channel_name")
    def get_channel_name(self, index):
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        yield (self.device, index, cast(byref(buffer), c_char_p),
               byref(buffer_length))
        return buffer[0:buffer_length.value].decode("UTF-8")

    @asphodel_command("asphodel_get_channel_info")
    def get_channel_info(self, index):
        """
        Return (channel_type, unit_type, filler_bits, data_bits, samples,
        bits_per_sample, minimum, maximum, resolution, chunk_count) for a
        specific channel.
        """
        info = AsphodelChannelInfo()
        yield (self.device, index, byref(info))
        return ChannelInfo(info.channel_type, info.unit_type, info.filler_bits,
                           info.data_bits, info.samples, info.bits_per_sample,
                           info.minimum, info.maximum, info.resolution,
                           info.chunk_count)

    @asphodel_command("asphodel_get_channel_coefficients")
    def get_channel_coefficients(self, index):
        coefficients = (c_float * 255)()
        coefficients_length = c_uint8(255)
        yield (self.device, index, cast(byref(coefficients), POINTER(c_float)),
               byref(coefficients_length))
        return tuple(coefficients[0:coefficients_length.value])

    @asphodel_command("asphodel_get_channel_chunk")
    def get_channel_chunk(self, index, chunk_number):
        chunk = (c_uint8 * 255)()
        chunk_length = c_uint8(255)
        yield (self.device, index, chunk_number,
               cast(byref(chunk), POINTER(c_uint8)), byref(chunk_length))
        return bytes(chunk[0:chunk_length.value])

    @asphodel_command("asphodel_channel_specific")
    def channel_specific(self, index, values):
        reply = (c_uint8 * 255)()
        reply_length = c_uint8(255)
        data = (c_uint8 * len(values))()
        for i in range(len(values)):
            data[i] = values[i]
        yield (self.device, index, cast(byref(data), POINTER(c_uint8)),
               len(values), cast(byref(reply), POINTER(c_uint8)),
               byref(reply_length))
        return bytes(reply[0:reply_length.value])

    @asphodel_command("asphodel_get_channel_calibration")
    def get_channel_calibration(self, index):
        """
        Return (base_setting_index, resolution_setting_index, scale_offset,
        minimum, maximum) for a specific channel. If no calibration is
        available for that channel then None in returned instead
        """
        available = c_int()
        cal = self.lib.AsphodelChannelCalibration()
        yield (self.device, index, byref(available), byref(cal))
        if not bool(available.value):
            return None
        else:
            return ChannelCalibration(
                cal.base_setting_index, cal.resolution_setting_index,
                cal.scale, cal.offset, cal.minimum, cal.maximum)

    @asphodel_command("asphodel_get_supply_count")
    def get_supply_count(self):
        count = c_int()
        yield (self.device, byref(count))
        return count.value

    @asphodel_command("asphodel_get_supply_name")
    def get_supply_name(self, index):
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        yield (self.device, index, cast(byref(buffer), c_char_p),
               byref(buffer_length))
        return buffer[0:buffer_length.value].decode("UTF-8")

    @asphodel_command("asphodel_get_supply_info")
    def get_supply_info(self, index):
        """
        Return (unit_type, is_battery, nominal, scale, offset)
        """
        info = self.lib.AsphodelSupplyInfo()
        yield (self.device, index, byref(info))
        return SupplyInfo(info.unit_type, info.is_battery, info.nominal,
                          info.scale, info.offset)

    @asphodel_command("asphodel_check_supply")
    def check_supply(self, index, tries=20):
        """
        Return (measurement, result) for a specific supply. If tries is
        positive & non-zero, then no more than this number of transfers will be
        sent before raising an exception. Otherwise, an unlimited number of
        transfers may be performed.
        """
        measurement = c_int32()
        result = c_uint8()
        yield (self.device, index, byref(measurement), byref(result), tries)
        return (measurement.value, result.value)

    @asphodel_command("asphodel_get_ctrl_var_count")
    def get_ctrl_var_count(self):
        count = c_int()
        yield (self.device, byref(count))
        return count.value

    @asphodel_command("asphodel_get_ctrl_var_name")
    def get_ctrl_var_name(self, index):
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        yield (self.device, index, cast(byref(buffer), c_char_p),
               byref(buffer_length))
        return buffer[0:buffer_length.value].decode("UTF-8")

    @asphodel_command("asphodel_get_ctrl_var_info")
    def get_ctrl_var_info(self, index):
        """
        Return (unit_type, minimum, maximum, scale, offset)
        """
        info = self.lib.AsphodelCtrlVarInfo()
        yield (self.device, index, byref(info))
        return CtrlVarInfo(info.unit_type, info.minimum, info.maximum,
                           info.scale, info.offset)

    @asphodel_command("asphodel_get_ctrl_var")
    def get_ctrl_var(self, index):
        value = c_int32()
        yield (self.device, index, byref(value))
        return value.value

    @asphodel_command("asphodel_set_ctrl_var")
    def set_ctrl_var(self, index, value):
        yield (self.device, index, value)

    @asphodel_command("asphodel_get_setting_count")
    def get_setting_count(self):
        count = c_int()
        yield (self.device, byref(count))
        return count.value

    @asphodel_command("asphodel_get_setting_name")
    def get_setting_name(self, index):
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        yield (self.device, index, cast(byref(buffer), c_char_p),
               byref(buffer_length))
        return buffer[0:buffer_length.value].decode("UTF-8")

    @asphodel_command("asphodel_get_setting_info")
    def get_setting_info(self, index):
        info = AsphodelSettingInfo()
        yield (self.device, index, byref(info))
        return info

    @asphodel_command("asphodel_get_setting_default")
    def get_setting_default(self, index):
        default = (c_uint8 * 255)()
        default_length = c_uint8(255)
        yield (self.device, index, cast(byref(default), POINTER(c_uint8)),
               byref(default_length))
        return bytes(default[0:default_length.value])

    @asphodel_command("asphodel_get_custom_enum_counts")
    def get_custom_enum_counts(self):
        counts = (c_uint8 * 255)()
        counts_length = c_uint8(255)
        yield (self.device, cast(byref(counts), POINTER(c_uint8)),
               byref(counts_length))
        return tuple(counts[0:counts_length.value])

    @asphodel_command("asphodel_get_custom_enum_value_name")
    def get_custom_enum_value_name(self, index, value):
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        yield (self.device, index, value, cast(byref(buffer), c_char_p),
               byref(buffer_length))
        return buffer[0:buffer_length.value].decode("UTF-8")

    @asphodel_command("asphodel_get_setting_category_count")
    def get_setting_category_count(self):
        count = c_int()
        yield (self.device, byref(count))
        return count.value

    @asphodel_command("asphodel_get_setting_category_name")
    def get_setting_category_name(self, index):
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        yield (self.device, index, cast(byref(buffer), c_char_p),
               byref(buffer_length))
        return buffer[0:buffer_length.value].decode("UTF-8")

    @asphodel_command("asphodel_get_setting_category_settings")
    def get_setting_category_settings(self, index):
        settings = (c_uint8 * 255)()
        settings_length = c_uint8(255)
        yield (self.device, index, cast(byref(settings), POINTER(c_uint8)),
               byref(settings_length))
        return tuple(settings[0:settings_length.value])

    @asphodel_command("asphodel_get_gpio_port_count")
    def get_gpio_port_count(self):
        count = c_int()
        yield (self.device, byref(count))
        return count.value

    @asphodel_command("asphodel_get_gpio_port_name")
    def get_gpio_port_name(self, index):
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        yield (self.device, index, cast(byref(buffer), c_char_p),
               byref(buffer_length))
        return buffer[0:buffer_length.value].decode("UTF-8")

    @asphodel_command("asphodel_get_gpio_port_info")
    def get_gpio_port_info(self, index):
        """
        Return (input_pins, output_pins, floating_pins, loaded_pins,
        overridden_pins)
        """
        info = self.lib.AsphodelGPIOPortInfo()
        yield (self.device, index, byref(info))
        return GPIOPortInfo(info.input_pins, info.output_pins,
                            info.floating_pins, info.loaded_pins,
                            info.overridden_pins)

    @asphodel_command("asphodel_get_gpio_port_values")
    def get_gpio_port_values(self, index):
        pin_values = c_uint32()
        yield (self.device, index, byref(pin_values))
        return pin_values.value

    @asphodel_command("asphodel_set_gpio_port_modes")
    def set_gpio_port_modes(self, index, mode, pins):
        yield (self.device, index, mode, pins)

    @asphodel_command("asphodel_disable_gpio_overrides")
    def disable_gpio_overrides(self):
        yield (self.device,)

    @asphodel_command("asphodel_get_bus_counts")
    def get_bus_counts(self):
        spi_count = c_int()
        i2c_count = c_int()
        yield (self.device, byref(spi_count), byref(i2c_count))
        return (spi_count.value, i2c_count.value)

    @asphodel_command("asphodel_set_spi_cs_mode")
    def set_spi_cs_mode(self, index, mode):
        yield (self.device, index, mode)

    @asphodel_command("asphodel_do_spi_transfer")
    def do_spi_transfer(self, index, write_bytes):
        data_length = len(write_bytes)
        tx_data = (c_uint8 * data_length).from_buffer_copy(bytes(write_bytes))
        rx_data = (c_uint8 * data_length)()
        yield (self.device, index, cast(byref(tx_data), POINTER(c_uint8)),
               cast(byref(rx_data), POINTER(c_uint8)), data_length)
        return bytes(rx_data[0:data_length])

    @asphodel_command("asphodel_do_i2c_write")
    def do_i2c_write(self, index, addr, write_bytes):
        data_length = len(write_bytes)
        tx_data = (c_uint8 * data_length).from_buffer_copy(bytes(write_bytes))
        yield (self.device, index, addr,
               cast(byref(tx_data), POINTER(c_uint8)), data_length)

    @asphodel_command("asphodel_do_i2c_read")
    def do_i2c_read(self, index, addr, read_length):
        rx_data = (c_uint8 * read_length)()
        yield (self.device, index, addr,
               cast(byref(rx_data), POINTER(c_uint8)), read_length)
        return bytes(rx_data[0:read_length])

    @asphodel_command("asphodel_do_i2c_write_read")
    def do_i2c_write_read(self, index, addr, write_bytes, read_length):
        tx_len = len(write_bytes)
        tx_data = (c_uint8 * tx_len).from_buffer_copy(bytes(write_bytes))
        rx_data = (c_uint8 * read_length)()
        yield (self.device, index, addr,
               cast(byref(tx_data), POINTER(c_uint8)), tx_len,
               cast(byref(rx_data), POINTER(c_uint8)), read_length)
        return bytes(rx_data[0:read_length])

    @asphodel_command("asphodel_do_radio_fixed_test")
    def do_radio_fixed_test(self, channel, duration, mode):
        yield (self.device, channel, duration, mode)

    @asphodel_command("asphodel_do_radio_sweep_test")
    def do_radio_sweep_test(self, start, stop, hop_interval, hop_count, mode):
        yield (self.device, start, stop, hop_interval, hop_count, mode)

    @asphodel_command("asphodel_get_info_region_count")
    def get_info_region_count(self):
        count = c_int()
        yield (self.device, byref(count))
        return count.value

    @asphodel_command("asphodel_get_info_region_name")
    def get_info_region_name(self, index):
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        yield (self.device, index, cast(byref(buffer), c_char_p),
               byref(buffer_length))
        return buffer[0:buffer_length.value].decode("UTF-8")

    @asphodel_command("asphodel_get_info_region")
    def get_info_region(self, index):
        data = (c_uint8 * 255)()
        data_length = c_uint8(255)
        yield (self.device, index, cast(byref(data), POINTER(c_uint8)),
               byref(data_length))
        return tuple(data[0:data_length.value])

    @asphodel_command("asphodel_get_stack_info")
    def get_stack_info(self):
        array = (c_uint32 * 2)()
        yield (self.device, array)
        values = tuple(array)
        return values

    @asphodel_command("asphodel_echo_raw")
    def echo_raw(self, values):
        max_length = self.get_max_incoming_param_length()
        reply = (c_uint8 * max_length)()
        reply_length = c_size_t(max_length)
        data = (c_uint8 * len(values)).from_buffer_copy(bytes(values))
        yield (self.device, cast(byref(data), POINTER(c_uint8)),
               len(values), cast(byref(reply), POINTER(c_uint8)),
               byref(reply_length))
        actual_length = min(max_length, reply_length.value)
        return bytes(reply[0:actual_length])

    @asphodel_command("asphodel_echo_transaction")
    def echo_transaction(self, values):
        max_length = self.get_max_incoming_param_length()
        reply = (c_uint8 * max_length)()
        reply_length = c_size_t(max_length)
        data = (c_uint8 * len(values)).from_buffer_copy(bytes(values))
        yield (self.device, cast(byref(data), POINTER(c_uint8)),
               len(values), cast(byref(reply), POINTER(c_uint8)),
               byref(reply_length))
        actual_length = min(max_length, reply_length.value)
        return bytes(reply[0:actual_length])

    @asphodel_command("asphodel_echo_params")
    def echo_params(self, values):
        max_length = self.get_max_incoming_param_length()
        reply = (c_uint8 * max_length)()
        reply_length = c_size_t(max_length)
        data = (c_uint8 * len(values)).from_buffer_copy(bytes(values))
        yield (self.device, cast(byref(data), POINTER(c_uint8)),
               len(values), cast(byref(reply), POINTER(c_uint8)),
               byref(reply_length))
        actual_length = min(max_length, reply_length.value)
        return bytes(reply[0:actual_length])

    @asphodel_command("asphodel_enable_rf_power")
    def enable_rf_power(self, enable=True):
        yield (self.device, enable)

    @asphodel_command("asphodel_get_rf_power_status")
    def get_rf_power_status(self):
        enabled = c_int()
        yield (self.device, byref(enabled))
        return bool(enabled.value)

    @asphodel_command("asphodel_get_rf_power_ctrl_vars")
    def get_rf_power_ctrl_vars(self):
        ctrl_var_indexes = (c_uint8 * 255)()
        length = c_uint8(255)
        yield (self.device, cast(byref(ctrl_var_indexes), POINTER(c_uint8)),
               byref(length))
        return tuple(ctrl_var_indexes[0:length.value])

    @asphodel_command("asphodel_reset_rf_power_timeout")
    def reset_rf_power_timeout(self, timeout):
        yield (self.device, timeout)

    @asphodel_command("asphodel_stop_radio")
    def stop_radio(self):
        yield (self.device,)

    @asphodel_command("asphodel_start_radio_scan")
    def start_radio_scan(self):
        yield (self.device,)

    @asphodel_command("asphodel_get_raw_radio_scan_results")
    def get_raw_radio_scan_results(self):
        serials = (c_uint32 * 255)()
        serials_length = c_size_t(255)
        yield (self.device, cast(byref(serials), POINTER(c_uint32)),
               byref(serials_length))
        return tuple(serials[0:serials_length.value])

    @asphodel_command("asphodel_get_radio_scan_results")
    def get_radio_scan_results(self):
        serials_ptr = POINTER(c_uint32)()
        serials_length = c_size_t()
        yield (self.device, byref(serials_ptr), byref(serials_length))
        serials = set(serials_ptr[0:serials_length.value])
        self.lib.lib.asphodel_free_radio_scan_results(serials_ptr)
        return serials

    @asphodel_command("asphodel_get_raw_radio_extra_scan_results")
    def get_raw_radio_extra_scan_results(self):
        results = (self.lib.AsphodelExtraScanResult * 255)()
        results_length = c_size_t(255)
        yield (self.device,
               cast(byref(results), POINTER(self.lib.AsphodelExtraScanResult)),
               byref(results_length))
        result_list = []
        for result_struct in results[0:results_length.value]:
            result_list.append(ExtraScanResult(result_struct.serial_number,
                                               result_struct.asphodel_type,
                                               result_struct.device_mode))
        return result_list

    @asphodel_command("asphodel_get_radio_extra_scan_results")
    def get_radio_extra_scan_results(self):
        results_ptr = POINTER(self.lib.AsphodelExtraScanResult)()
        results_length = c_size_t()
        yield (self.device, byref(results_ptr), byref(results_length))
        result_list = []
        for result_struct in results_ptr[0:results_length.value]:
            result_list.append(ExtraScanResult(result_struct.serial_number,
                                               result_struct.asphodel_type,
                                               result_struct.device_mode))
        self.lib.lib.asphodel_free_radio_extra_scan_results(results_ptr)
        return result_list

    @asphodel_command("asphodel_get_radio_scan_power")
    def get_radio_scan_power(self, serial_numbers):
        sn_array = (c_uint32 * len(serial_numbers))(*serial_numbers)
        powers = (c_int8 * len(serial_numbers))()
        yield (self.device, cast(byref(sn_array), POINTER(c_uint32)),
               cast(byref(powers), POINTER(c_int8)), len(serial_numbers))
        return list(powers[0:len(serial_numbers)])

    @asphodel_command("asphodel_connect_radio")
    def connect_radio(self, serial_number):
        yield (self.device, serial_number)

    @asphodel_command("asphodel_get_radio_status")
    def get_radio_status(self):
        connected = c_int()
        serial_number = c_uint32()
        protocol_type = c_uint8()
        scanning = c_int()
        yield (self.device, byref(connected), byref(serial_number),
               byref(protocol_type), byref(scanning))
        return (bool(connected.value), serial_number.value,
                protocol_type.value, bool(scanning.value))

    @asphodel_command("asphodel_get_radio_ctrl_vars")
    def get_radio_ctrl_vars(self):
        ctrl_var_indexes = (c_uint8 * 255)()
        length = c_uint8(255)
        yield (self.device, cast(byref(ctrl_var_indexes), POINTER(c_uint8)),
               byref(length))
        return tuple(ctrl_var_indexes[0:length.value])

    @asphodel_command("asphodel_get_radio_default_serial")
    def get_radio_default_serial(self):
        serial_number = c_uint32()
        yield (self.device, byref(serial_number))
        return serial_number.value

    @asphodel_command("asphodel_start_radio_scan_boot")
    def start_radio_scan_boot(self):
        yield (self.device,)

    @asphodel_command("asphodel_connect_radio_boot")
    def connect_radio_boot(self, serial_number):
        yield (self.device, serial_number)

    @asphodel_command("asphodel_stop_remote")
    def stop_remote(self):
        yield (self.device,)

    @asphodel_command("asphodel_restart_remote")
    def restart_remote(self):
        yield (self.device,)

    @asphodel_command("asphodel_get_remote_status")
    def get_remote_status(self):
        connected = c_int()
        serial_number = c_uint32()
        protocol_type = c_uint8()
        yield (self.device, byref(connected), byref(serial_number),
               byref(protocol_type))
        return (bool(connected.value), serial_number.value,
                protocol_type.value)

    @asphodel_command("asphodel_restart_remote_app")
    def restart_remote_app(self):
        yield (self.device,)

    @asphodel_command("asphodel_restart_remote_boot")
    def restart_remote_boot(self):
        yield (self.device,)

    @asphodel_command("asphodel_bootloader_start_program")
    def bootloader_start_program(self):
        yield (self.device,)

    @asphodel_command("asphodel_get_bootloader_page_info")
    def get_bootloader_page_info(self):
        page_info = (c_uint32 * 255)()
        length = c_uint8(255)
        yield (self.device, cast(byref(page_info), POINTER(c_uint32)),
               byref(length))
        values = page_info[0:length.value]
        return tuple(zip(values[0::2], values[1::2]))

    @asphodel_command("asphodel_get_bootloader_block_sizes")
    def get_bootloader_block_sizes(self):
        block_sizes = (c_uint16 * 255)()
        length = c_uint8(255)
        yield (self.device, cast(byref(block_sizes), POINTER(c_uint16)),
               byref(length))
        return tuple(block_sizes[0:length.value])

    @asphodel_command("asphodel_start_bootloader_page")
    def start_bootloader_page(self, page_number, nonce):
        nonce_length = len(nonce)
        nonce_array = (c_uint8 * nonce_length).from_buffer_copy(nonce)
        yield (self.device, page_number,
               cast(byref(nonce_array), POINTER(c_uint8)), nonce_length)

    @asphodel_command("asphodel_write_bootloader_code_block")
    def write_bootloader_code_block(self, data):
        data_length = len(data)
        data_array = (c_uint8 * data_length).from_buffer_copy(data)
        yield (self.device, cast(byref(data_array), POINTER(c_uint8)),
               data_length)

    @asphodel_command("asphodel_write_bootloader_page")
    def write_bootloader_page(self, data, block_sizes):
        data_length = len(data)
        data_array = (c_uint8 * data_length).from_buffer_copy(data)
        block_sizes_length = len(block_sizes)
        block_sizes_array = (c_uint16 * block_sizes_length)()
        for i in range(block_sizes_length):
            block_sizes_array[i] = block_sizes[i]
        yield (self.device, cast(byref(data_array), POINTER(c_uint8)),
               data_length, cast(byref(block_sizes_array), POINTER(c_uint16)),
               block_sizes_length)

    @asphodel_command("asphodel_finish_bootloader_page")
    def finish_bootloader_page(self, mac_tag=None):
        if mac_tag is None:
            mac_tag = b""
        mac_tag_length = len(mac_tag)
        mac_tag_array = (c_uint8 * mac_tag_length).from_buffer_copy(mac_tag)
        yield (self.device, cast(byref(mac_tag_array), POINTER(c_uint8)),
               mac_tag_length)

    @asphodel_command("asphodel_verify_bootloader_page")
    def verify_bootloader_page(self, mac_tag=None):
        if mac_tag is None:
            mac_tag = b""
        mac_tag_length = len(mac_tag)
        mac_tag_array = (c_uint8 * mac_tag_length).from_buffer_copy(mac_tag)
        yield (self.device, cast(byref(mac_tag_array), POINTER(c_uint8)),
               mac_tag_length)

    def get_strain_bridge_count(self, channel_info):
        count = c_int()
        self.lib.lib.asphodel_get_strain_bridge_count(channel_info,
                                                      byref(count))
        return count.value

    def get_strain_bridge_subchannel(self, channel_info, bridge_index):
        subchannel = c_size_t()
        self.lib.lib.asphodel_get_strain_bridge_subchannel(channel_info,
                                                           bridge_index,
                                                           byref(subchannel))
        return subchannel.value

    def get_strain_bridge_values(self, channel_info, bridge_index):
        array = (c_float * 5)()
        self.lib.lib.asphodel_get_strain_bridge_values(channel_info,
                                                       bridge_index, array)
        return BridgeValues(*array)

    @asphodel_command("asphodel_set_strain_outputs")
    def set_strain_outputs(self, channel_index, bridge_index, pos, neg):
        yield (self.device, channel_index, bridge_index, pos, neg)

    def check_strain_resistances(self, channel_info, bridge_index, baseline,
                                 pos_high, neg_high):
        """
        Return (passed, pos_res, neg_res)
        """
        passed = c_int(0)
        pos_res = c_double()
        neg_res = c_double()
        self.lib.lib.asphodel_check_strain_resistances(channel_info,
                                                       bridge_index, baseline,
                                                       pos_high, neg_high,
                                                       byref(pos_res),
                                                       byref(neg_res),
                                                       byref(passed))
        return (bool(passed.value), pos_res.value, neg_res.value)

    def get_accel_self_test_limits(self, channel_info):
        array = (c_float * 6)()
        self.lib.lib.asphodel_get_accel_self_test_limits(channel_info, array)
        return SelfTestLimits(*array)

    @asphodel_command("asphodel_enable_accel_self_test")
    def enable_accel_self_test(self, channel_index, enable=True):
        yield (self.device, channel_index, enable)

    def check_accel_self_test(self, channel_info, disabled, enabled):
        """
        Return passed
        """
        dis_array = (c_double * 3)(*disabled)
        en_array = (c_double * 3)(*enabled)
        passed = c_int(0)
        self.lib.lib.asphodel_check_accel_self_test(channel_info, dis_array,
                                                    en_array, byref(passed))
        return bool(passed.value)

    def get_channel_decoder(self, index, bit_offset):
        channel_info = self.get_channel(index)

        return self.lib.create_channel_decoder(channel_info, bit_offset)

    def get_stream_decoder(self, index, bit_offset):
        # get the stream struct
        stream_info = self.get_stream(index)

        # get the channel struct
        channel_info_list = []
        indexes = stream_info.channel_index_list[0:stream_info.channel_count]
        for ch_index in indexes:
            channel_info_list.append(self.get_channel(ch_index))

        return self.lib.create_stream_decoder(stream_info, channel_info_list,
                                              bit_offset)

    def get_device_decoder(self):
        stream_count, filler_bits, id_bits = self.get_stream_count()

        info_list = []
        for i in range(stream_count):
            stream_struct = self.get_stream(i)
            channel_info_list = []
            channels = stream_struct.channel_count
            indexes = stream_struct.channel_index_list[0:channels]
            for ch_index in indexes:
                channel_info_list.append(self.get_channel(ch_index))
            info_list.append((i, stream_struct, channel_info_list))

        return self.lib.create_device_decoder(info_list, filler_bits, id_bits)

    def get_streaming_counts(self, response_time, buffer_time, timeout):
        stream_count, _filler_bits, _id_bits = self.get_stream_count()
        streams = [self.get_stream(i) for i in range(stream_count)]

        return self.lib.get_streaming_counts(streams, response_time,
                                             buffer_time, timeout)

    def get_channel_unit_formatter(self, index, use_metric):
        info = self.get_channel_info(index)
        return self.lib.create_unit_formatter(info.unit_type, info.minimum,
                                              info.maximum, info.resolution,
                                              use_metric)

    def get_ctrl_var_unit_formatter(self, index, use_metric):
        info = self.get_ctrl_var_info(index)
        unit_type, minimum, maximum, scale, offset = info
        return self.lib.create_unit_formatter(unit_type,
                                              minimum * scale + offset,
                                              maximum * scale + offset,
                                              scale, use_metric)

    def get_setting(self, index):
        info = self.get_setting_info(index)
        name = self.get_setting_name(index)
        default = self.get_setting_default(index)
        name_bytes = name.encode("UTF-8")
        info.name = name_bytes
        info.name_length = len(name_bytes)

        info.default_bytes = (c_uint8 * len(default))(*default)
        info.default_bytes_length = len(default)
        return info


def recreate_channel_decoder(*args, **kwargs):
    return nativelib.create_channel_decoder(*args, **kwargs)


class AsphodelNativeChannelDecoder:
    def __init__(self, lib, decoder, channel_info, stream_decoder=None):
        self.lib = lib
        self._decoder = decoder
        self.channel_info = channel_info
        self.stream_decoder = stream_decoder  # keep a reference
        self.auto_free = False if stream_decoder else True

        # copy settings out of the decoder
        self.channel_bit_offset = self._decoder.channel_bit_offset
        self.samples = self._decoder.samples
        try:
            self.channel_name = self._decoder.channel_name.decode("UTF-8")
        except UnicodeDecodeError:
            self.channel_name = "<ERROR>"
        self.subchannels = self._decoder.subchannels
        self.subchannel_names = []
        for i in range(self.subchannels):
            try:
                s = self._decoder.subchannel_names[i].decode("UTF-8")
                self.subchannel_names.append(s)
            except UnicodeDecodeError:
                self.subchannel_names.append("<ERROR>")

    def __del__(self):
        if self.auto_free:
            self.free()

    def __reduce__(self):
        if self._decoder.callback:
            raise Exception("Cannot reduce channel decoder with callback")
        args = (self.channel_info, self._decoder.channel_bit_offset)
        return (recreate_channel_decoder, args)

    def free(self):
        if self._decoder:
            self._decoder.free_decoder(self._decoder)
            self._decoder = None

    def reset(self):
        self._decoder.reset(self._decoder)

    def decode(self, counter, buffer):
        b = (c_uint8 * len(buffer)).from_buffer_copy(buffer)
        self._decoder.decode(self._decoder, counter, cast(b, POINTER(c_uint8)))

    def set_conversion_factor(self, scale, offset):
        self._decoder.set_conversion_factor(self._decoder, scale, offset)

    def set_callback(self, cb):
        # void (*)(uint64_t counter, double *data, size_t samples,
        #          size_t subchannels, void * closure)
        def callback(counter, data, samples, subchannels, closure):
            data_size = samples * subchannels
            d = data[0:data_size]
            try:
                cb(counter, d, samples, subchannels)
            except Exception:
                pass  # nothing can be done about it here
        c_cb = self.lib.AsphodelDecodeCallback(callback)
        self._callback = c_cb  # save a reference
        self._decoder.callback = c_cb


def recreate_stream_decoder(*args, **kwargs):
    return nativelib.create_stream_decoder(*args, **kwargs)


class AsphodelNativeStreamDecoder:
    def __init__(self, lib, decoder, stream_info, channel_info_list,
                 bit_offset, device_decoder=None):
        self.lib = lib
        self._decoder = decoder
        self.stream_info = stream_info
        self._channel_info_list = channel_info_list[:]
        self.bit_offset = bit_offset
        self.device_decoder = device_decoder  # keep a reference
        self.auto_free = False if device_decoder else True

        # copy some values out
        self.counter_byte_offset = self._decoder.counter_byte_offset
        self.used_bits = self._decoder.used_bits
        self.channels = self._decoder.channels
        self.decoders = []
        for i in range(self.channels):
            d = AsphodelNativeChannelDecoder(
                self.lib, self._decoder.decoders[i].contents,
                channel_info_list[i], self)
            self.decoders.append(d)

    def __del__(self):
        if self.auto_free:
            self.free()

    def __reduce__(self):
        if self._decoder.lost_packet_callback:
            raise Exception("Cannot reduce stream decoder with callback")
        for d in self.decoders:
            if d._decoder.callback:
                raise Exception("Cannot reduce channel decoder with callback")
        args = (self.stream_info, self._channel_info_list, self.bit_offset)
        return (recreate_stream_decoder, args)

    def free(self):
        if self._decoder:
            self._decoder.free_decoder(self._decoder)
            self._decoder = None

    def reset(self):
        self._decoder.reset(self._decoder)

    @property
    def last_count(self):
        return self._decoder.last_count

    def decode(self, buffer):
        b = (c_uint8 * len(buffer)).from_buffer_copy(buffer)
        self._decoder.decode(self._decoder, cast(b, POINTER(c_uint8)))

    def set_lost_packet_callback(self, cb):
        def callback(current, last, closure):
            try:
                cb(current, last)
            except Exception:
                pass  # nothing can be done about it here
        c_cb = self.lib.AsphodelLostPacketCallback(callback)
        self._callback = c_cb  # save a reference
        self._decoder.lost_packet_callback = c_cb


def recreate_device_decoder(*args, **kwargs):
    return nativelib.create_device_decoder(*args, **kwargs)


class AsphodelNativeDeviceDecoder:
    def __init__(self, lib, decoder, info_list, filler_bits, id_bits):
        self.lib = lib
        self._decoder = decoder
        self._info_list = info_list
        self._filler_bits = filler_bits
        self._id_bits = id_bits
        bit_offset = self._filler_bits + self._id_bits

        # copy some values out
        self.id_byte_offset = self._decoder.id_byte_offset
        self.used_bits = self._decoder.used_bits
        self.streams = self._decoder.streams
        self.stream_ids = self._decoder.stream_ids[0:self.streams]

        self.decoders = []
        for i in range(self.streams):
            d = AsphodelNativeStreamDecoder(self.lib,
                                            self._decoder.decoders[i].contents,
                                            info_list[i][1], info_list[i][2],
                                            bit_offset, self)
            self.decoders.append(d)

    def __del__(self):
        self.free()

    def __reduce__(self):
        if self._decoder.unknown_id_callback:
            raise Exception("Cannot reduce device decoder with callback")
        for d in self.decoders:
            if d._decoder.lost_packet_callback:
                raise Exception("Cannot reduce stream decoder with callback")
            for cd in d.decoders:
                if cd._decoder.callback:
                    raise Exception(
                        "Cannot reduce channel decoder with callback")
        args = (self._info_list, self._filler_bits, self._id_bits)
        return (recreate_device_decoder, args)

    def free(self):
        if self._decoder:
            self._decoder.free_decoder(self._decoder)
            self._decoder = None

    def reset(self):
        self._decoder.reset(self._decoder)

    def decode(self, buffer):
        b = (c_uint8 * len(buffer)).from_buffer_copy(buffer)
        self._decoder.decode(self._decoder, cast(b, POINTER(c_uint8)))

    def set_unknown_id_callback(self, cb):
        def callback(lost_id, closure):
            try:
                cb(lost_id)
            except Exception:
                pass  # nothing can be done about it here
        c_cb = self.lib.AsphodelUnknownIDCallback(callback)
        self._callback = c_cb  # save a reference
        self._decoder.unknown_id_callback = c_cb


def recreate_unit_formatter(*args, **kwargs):
    return nativelib.create_unit_formatter(*args, **kwargs)


def recreate_custom_unit_formatter(*args, **kwargs):
    return nativelib.create_custom_unit_formatter(*args, **kwargs)


class AsphodelNativeUnitFormatter:
    def __init__(self, lib, formatter, recreate):
        self.lib = lib
        self.formatter = formatter
        self._recreate = recreate

        # copy some values out
        self.unit_ascii = self.formatter.unit_ascii.decode("ascii")
        self.unit_utf8 = self.formatter.unit_utf8.decode("UTF-8")
        self.unit_html = self.formatter.unit_html.decode("ascii")
        self.conversion_scale = self.formatter.conversion_scale
        self.conversion_offset = self.formatter.conversion_offset

    def __del__(self):
        self.free()

    def __reduce__(self):
        return self._recreate

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            self_tuple = (self.unit_ascii, self.unit_utf8, self.unit_html,
                          self.conversion_scale, self.conversion_offset)
            other_tuple = (other.unit_ascii, other.unit_utf8, other.unit_html,
                           other.conversion_scale, other.conversion_offset)
            return self_tuple == other_tuple
        else:
            return NotImplemented

    def free(self):
        if self.formatter:
            self.formatter.free(self.formatter)
            self.formatter = None

    def format_bare(self, value):
        buffer = create_string_buffer(256)
        self.formatter.format_bare(self.formatter, buffer, len(buffer), value)
        return buffer.value.decode("ascii")

    def format_ascii(self, value):
        buffer = create_string_buffer(256)
        self.formatter.format_ascii(self.formatter, buffer, len(buffer), value)
        return buffer.value.decode("ascii")

    def format_utf8(self, value):
        buffer = create_string_buffer(256)
        self.formatter.format_utf8(self.formatter, buffer, len(buffer), value)
        return buffer.value.decode("UTF-8")

    def format_html(self, value):
        buffer = create_string_buffer(256)
        self.formatter.format_html(self.formatter, buffer, len(buffer), value)
        return buffer.value.decode("ascii")


def format_nvm_data(data, size=16):
    def to_ascii(c):
        c = chr(c)
        if c in string.whitespace:
            return " "
        elif c in string.printable:
            return c
        else:
            return '.'
    output = []
    for i in range(0, len(data), size):
        data_chunk = data[i:min(len(data), i + size)]
        hex_values = " ".join(map("{:02x}".format, data_chunk))
        filler = "   " * (size - len(data_chunk))
        ascii_values = "".join(map(to_ascii, data_chunk))
        output.append(hex_values + filler + " " + ascii_values)
    return output


def find_devices():
    usb_devices = find_usb_devices()
    tcp_devices = find_tcp_devices()
    return usb_devices + tcp_devices


def find_device_by_serial(serial: str) -> Optional[AsphodelNativeDevice]:
    for device in nativelib.find_tcp_devices():
        adv = device.tcp_get_advertisement()
        if adv.serial_number == serial:
            return device

    for device in nativelib.find_usb_devices():
        try:
            device.open()
            if device.get_serial_number() == serial:
                return device
        except AsphodelError:
            continue
        finally:
            device.close()

    return None


nativelib = AsphodelNative()

asphodel_error_name = nativelib.lib.asphodel_error_name

protocol_version = nativelib.protocol_version
protocol_version_string = nativelib.protocol_version_string
build_info = nativelib.build_info
build_date = nativelib.build_date
usb_backend_version = nativelib.usb_backend_version

find_usb_devices = nativelib.find_usb_devices
find_tcp_devices = nativelib.find_tcp_devices
create_tcp_device = nativelib.create_tcp_device
unit_type_names = nativelib.unit_type_names
for type_index, type_name in enumerate(unit_type_names):
    globals()[type_name] = type_index
channel_type_names = nativelib.channel_type_names
for type_index, type_name in enumerate(channel_type_names):
    globals()[type_name] = type_index
setting_type_names = nativelib.setting_type_names
for type_index, type_name in enumerate(setting_type_names):
    globals()[type_name] = type_index

format_value_ascii = nativelib.format_value_ascii
format_value_utf8 = nativelib.format_value_utf8
format_value_html = nativelib.format_value_html
