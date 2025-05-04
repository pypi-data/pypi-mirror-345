"""
Device interface for Wuhan Jingce EYE2-400 Color Analyzer (MES,1).
"""

import logging
import serial
from serial.tools import list_ports
from typing import List, Dict

class Eye2CLI:
    def __init__(self, port: str, timeout: float = 2.0, eol: str = 'CR'):
        eol_map = {'CR': b'\r', 'LF': b'\n', 'CRLF': b'\r\n'}
        self.eol = eol_map[eol]
        self.timeout = timeout
        self.ser = serial.Serial(
            port=port,
            baudrate=115200,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=timeout,
        )

    @staticmethod
    def list_ports() -> List[str]:
        return [p.device for p in list_ports.comports()]

    def measure(self) -> Dict[str, str]:
        self.ser.reset_input_buffer()
        self.ser.write(b'MES,1' + self.eol)
        raw = self.ser.read_until(self.eol)
        text = raw.decode('ascii', errors='ignore').strip()
        logging.debug(f"Raw data received: {text!r}")
        if not text.startswith('OK'):
            raise RuntimeError(f"Unexpected reply: {text!r}")

        parts = text.split(',')
        data_vals = [v.strip() for v in parts[1:-1]]
        if len(data_vals) < 6:
            raise RuntimeError(f"Expected at least 6 fields, got {len(data_vals)}")

        keys = ['Mode', 'x_unused', 'x', 'y', 'Lv', 'ΔE']
        return dict(zip(keys, data_vals))

    def close(self) -> None:
        self.ser.close()
