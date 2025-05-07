import time
from pymodaq_plugins_bnc.hardware.device import AsyncDevice
import asyncio

class BNC575(AsyncDevice):

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.channel_label = "A"
        self.slot = 1

    async def connect(self):
        await super().connect()

    async def idn(self):
        return (await self.query("*IDN")).strip()

    def set_channel(self):
        return {"A": 1, "B": 2, "C": 3, "D": 4}.get(self.channel_label, 1)

    async def reset(self):
        await self.send("*RST")

    async def save_state(self):
        await self.set("*SAV", str(self.slot))

    async def restore_state(self):
        await self.set("*RCL", str(self.slot))

    async def trig(self):
        await self.send("*TRG")

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self, value):
        self._slot = value

    @property
    def channel_label(self):
        return self._channel_label

    @channel_label.setter
    def channel_label(self, value):
        self._channel_label = value

    async def get_label(self):
        return (await self.query("*LBL")).strip()

    async def set_label(self, value):
        await self.set("*LBL", f'"{value}"')

    async def get_global_state(self):
        state = (await self.query(":INST:STATE")).strip()
        return "ON" if state == "1" else "OFF"

    async def set_global_state(self, state):
        await self.set(":INST:STATE", state)

    async def get_global_mode(self):
        return await self.query(":PULSE0:MODE")

    async def set_global_mode(self, mode):
        await self.set(":PULSE0:MODE", mode)

    async def get_channel_mode(self):
        ch = self.set_channel()
        return (await self.query(f":PULSE{ch}:CMOD")).strip()

    async def set_channel_mode(self, mode):
        ch = self.set_channel()
        await self.set(f":PULSE{ch}:CMOD", mode)

    async def get_channel_state(self):
        ch = self.set_channel()
        state = (await self.query(f":PULSE{ch}:STATE")).strip()
        return "ON" if state == "1" else "OFF"

    async def set_channel_state(self, state):
        ch = self.set_channel()
        await self.set(f":PULSE{ch}:STATE", state)

    async def get_trig_mode(self):
        return (await self.query(":PULSE0:TRIG:MODE")).strip()

    async def set_trig_mode(self, mode):
        await self.set(":PULSE0:TRIG:MODE", mode)

    async def get_trig_thresh(self):
        return float((await self.query(":PULSE0:TRIG:LEV")).strip())

    async def set_trig_thresh(self, val):
        await self.set(":PULSE0:TRIG:LEV", str(val))

    async def get_trig_edge(self):
        edge = (await self.query(":PULSE0:TRIG:EDGE")).strip()
        return "RISING" if edge == "RIS" else "FALLING"

    async def set_trig_edge(self, edge):
        await self.set(":PULSE0:TRIG:EDGE", edge)

    async def get_gate_mode(self):
        return (await self.query(":PULSE0:GATE:MODE")).strip()

    async def set_gate_mode(self, mode):
        await self.set(":PULSE0:GATE:MODE", mode)

    async def get_gate_thresh(self):
        return float((await self.query(":PULSE0:GATE:LEV")).strip())

    async def set_gate_thresh(self, thresh):
        await self.set(":PULSE0:GATE:LEV", str(thresh))

    async def get_gate_logic(self):
        mode = (await self.query(":PULSE0:GATE:MODE")).strip()
        if mode == "CHAN":
            ch = self.set_channel()
            return (await self.query(f":PULSE{ch}:CLOGIC")).strip()
        return (await self.query(":PULSE0:GATE:LOGIC")).strip()

    async def set_gate_logic(self, logic):
        mode = (await self.query(":PULSE0:GATE:MODE")).strip()
        ch = self.set_channel()
        if mode == "CHAN":
            await self.set(f":PULSE{ch}:CLOGIC", logic)
        else:
            await self.set(":PULSE0:GATE:LOGIC", logic)

    async def get_channel_gate_mode(self):
        mode = (await self.query(":PULSE0:GATE:MODE")).strip()
        if mode == "CHAN":
            ch = self.set_channel()
            return (await self.query(f":PULSE{ch}:CGATE")).strip()
        return "DIS"

    async def set_channel_gate_mode(self, mode):
        ch = self.set_channel()
        cur_mode = (await self.query(":PULSE0:GATE:MODE")).strip()
        if cur_mode != "CHAN":
            await self.set(":PULSE0:GATE:MODE", "CHAN")
        await self.set(f":PULSE{ch}:CGATE", mode)

    async def get_period(self):
        return float((await self.query(":PULSE0:PER")).strip())

    async def set_period(self, val):
        await self.set(":PULSE0:PER", str(val))

    async def get_delay(self):
        ch = self.set_channel()
        return float((await self.query(f":PULSE{ch}:DELAY")).strip())

    async def set_delay(self, val):
        ch = self.set_channel()
        await self.set(f":PULSE{ch}:DELAY", f"{val:.9f}")

    async def get_width(self):
        ch = self.set_channel()
        return float((await self.query(f":PULSE{ch}:WIDT")).strip())

    async def set_width(self, val):
        ch = self.set_channel()
        await self.set(f":PULSE{ch}:WIDT", f"{val:.9f}")

    async def get_amplitude_mode(self):
        ch = self.set_channel()
        return (await self.query(f":PULSE{ch}:OUTP:MODE")).strip()

    async def set_amplitude_mode(self, mode):
        ch = self.set_channel()
        await self.set(f":PULSE{ch}:OUTP:MODE", mode)

    async def get_amplitude(self):
        ch = self.set_channel()
        return float((await self.query(f":PULSE{ch}:OUTP:AMPL")).strip())

    async def set_amplitude(self, val):
        if (await self.get_amplitude_mode()) == "ADJ":
            ch = self.set_channel()
            await self.set(f":PULSE{ch}:OUTP:AMPL", str(val))
        else:
            return "In TTL mode. First, switch to ADJ mode."

    async def get_polarity(self):
        ch = self.set_channel()
        return (await self.query(f":PULSE{ch}:POL")).strip()

    async def set_polarity(self, pol):
        ch = self.set_channel()
        await self.set(f":PULSE{ch}:POL", pol)

    async def output(self):
        return [
            {
                'title': 'Connection', 'name': 'connection', 'type': 'group', 'children': [
                    {'title': 'Controller', 'name': 'id', 'type': 'str', 'value': await self.idn(), 'readonly': True},
                    {'title': 'IP', 'name': 'ip', 'type': 'str', 'value': self.ip, 'default': self.ip},
                    {'title': 'Port', 'name': 'port', 'type': 'int', 'value': self.port, 'default': 2001}
                ]
            },
            {
                'title': 'Device Configuration State', 'name': 'config', 'type': 'group', 'children': [
                    {'title': 'Configuration Label', 'name': 'label', 'type': 'str', 'value': await self.get_label()},
                    {'title': 'Local Memory Slot', 'name': 'slot', 'type': 'list', 'value': self.slot, 'limits': list(range(1, 13))},
                    {'title': 'Save Current Configuration?', 'name': 'save', 'type': 'bool_push', 'label': 'Save', 'value': False},
                    {'title': 'Restore Previous Configuration?', 'name': 'restore', 'type': 'bool_push', 'label': 'Restore', 'value': False},
                    {'title': 'Reset Device?', 'name': 'reset', 'type': 'bool_push', 'label': 'Reset', 'value': False}
                ]
            },
            {
                'title': 'Device Output State', 'name': 'output', 'type': 'group', 'children': [
                    {'title': 'Global State', 'name': 'global_state', 'type': 'led_push', 'value': await self.get_global_state(), 'default': False},
                    {'title': 'Global Mode', 'name': 'global_mode', 'type': 'list', 'value': await self.get_global_mode(), 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
                    {'title': 'Channel', 'name': 'channel_label', 'type': 'list', 'value': self.channel_label, 'limits': ['A', 'B', 'C', 'D']},
                    {'title': 'Channel Mode', 'name': 'channel_mode', 'type': 'list', 'value': await self.get_channel_mode(), 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
                    {'title': 'Channel State', 'name': 'channel_state', 'type': 'led_push', 'value': await self.get_channel_state(), 'default': False},
                    {'title': 'Width (ns)', 'name': 'width', 'type': 'float', 'value': await self.get_width() * 1e9, 'default': 10, 'min': 10, 'max': 999e9},
                    {'title': 'Delay (ns)', 'name': 'delay', 'type': 'float', 'value': await self.get_delay() * 1e9, 'default': 0, 'min': 0, 'max': 999.0}
                ]
            },
            {
                'title': 'Amplitude Profile', 'name': 'amp', 'type': 'group', 'children': [
                    {'title': 'Amplitude Mode', 'name': 'amplitude_mode', 'type': 'list', 'value': await self.get_amplitude_mode(), 'limits': ['ADJ', 'TTL']},
                    {'title': 'Amplitude (V)', 'name': 'amplitude', 'type': 'float', 'value': await self.get_amplitude(), 'default': 2.0, 'min': 2.0, 'max': 20.0},
                    {'title': 'Polarity', 'name': 'polarity', 'type': 'list', 'value': await self.get_polarity(), 'limits': ['NORM', 'COMP', 'INV']}
                ]
            },
            {
                'title': 'Continuous Mode', 'name': 'continuous_mode', 'type': 'group', 'children': [
                    {'title': 'Period (s)', 'name': 'period', 'type': 'float', 'value': await self.get_period(), 'default': 1e-3, 'min': 100e-9, 'max': 5000.0},
                    {'title': 'Repetition Rate (Hz)', 'name': 'rep_rate', 'type': 'float', 'value': 1.0 / await self.get_period(), 'default': 1e3, 'min': 2e-4, 'max': 10e6}
                ]
            },
            {
                'title': 'Trigger Mode', 'name': 'trigger_mode', 'type': 'group', 'children': [
                    {'title': 'Trigger Mode', 'name': 'trig_mode', 'type': 'list', 'value': await self.get_trig_mode(), 'limits': ['DIS', 'TRIG']},
                    {'title': 'Trigger Threshold (V)', 'name': 'trig_thresh', 'type': 'float', 'value': await self.get_trig_thresh(), 'default': 2.5, 'min': 0.2, 'max': 15.0},
                    {'title': 'Trigger Edge', 'name': 'trig_edge', 'type': 'list', 'value': await self.get_trig_edge(), 'limits': ['HIGH', 'LOW']}
                ]
            },
            {
                'title': 'Gating', 'name': 'gating', 'type': 'group', 'children': [
                    {'title': 'Global Gate Mode', 'name': 'gate_mode', 'type': 'list', 'value': await self.get_gate_mode(), 'limits': ['DIS', 'PULS', 'OUTP', 'CHAN']},
                    {'title': 'Channel Gate Mode', 'name': 'channel_gate_mode', 'type': 'list', 'value': await self.get_channel_gate_mode(), 'limits': ['DIS', 'PULS', 'OUTP']},
                    {'title': 'Gate Threshold (V)', 'name': 'gate_thresh', 'type': 'float', 'value': await self.get_gate_thresh(), 'default': 2.5, 'min': 0.2, 'max': 15.0},
                    {'title': 'Gate Logic', 'name': 'gate_logic', 'type': 'list', 'value': await self.get_gate_logic(), 'limits': ['HIGH', 'LOW']}
                ]
            }
        ]

