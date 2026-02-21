from .ProtocolHandler import ProtocolHandler
from .MidiSender import MidiSender

# Knob Type values
KNOB_TYPE_CC = 0
KNOB_TYPE_AFTERTOUCH = 1
KNOB_TYPE_NOTE = 2
KNOB_TYPE_RELATIVE = 3  # CW (clockwise/relative)

# Pad Type values
PAD_TYPE_NOTE = 0
PAD_TYPE_CC_TOGGLE = 1
PAD_TYPE_MOMENTARY = 2
PAD_TYPE_PROGRAM = 3
PAD_TYPE_MCP = 4
PAD_TYPE_CUSTOM = 5
PAD_TYPE_COMB_MCP = 6

# Colors (RGB, R is lowest byte)
COLOR_OFF = 0x000000
COLOR_WHITE = 0xFFFFFF
COLOR_RED = 0x0000FF
COLOR_GREEN = 0x00FF00
COLOR_BLUE = 0xFF0000
COLOR_YELLOW = 0x00FFFF
COLOR_CYAN = 0xFFFF00
COLOR_MAGENTA = 0xFF00FF
COLOR_ORANGE = 0x0080FF
COLOR_DIM_WHITE = 0x404040


class Hardware:
    """Handles SMK25II hardware configuration."""

    def __init__(self, send_func, log_func=None):
        self._protocol = ProtocolHandler()
        self._midi = MidiSender(send_func, log_func)
        self._log = log_func or (lambda msg: None)

    def set_bulk_mode(self, enabled):
        """Enable/disable bulk mode for faster init."""
        self._midi.set_bulk_mode(enabled)

    def clear_cache(self):
        """Clear MIDI cache."""
        self._midi.clear_cache()

    # -------------------------------------------------------------------------
    # Knob configuration
    # -------------------------------------------------------------------------

    def set_knob_type(self, knob_index, knob_type, shifted=False):
        """Set a knob's type (CC, Aftertouch, Note, or Relative)."""
        addr = self._protocol.get_knob_addr(knob_index, shifted=shifted)
        self._midi.send_param(self._protocol, addr, 8, knob_type, mode=0x49)

    def set_knob_speed(self, knob_index, speed, shifted=False):
        """Set a knob's speed (0=Slowest, 1=Slow, 2=Normal, 3=Fast, 4=Fastest)."""
        addr = self._protocol.get_knob_addr(knob_index, shifted=shifted)
        self._midi.send_param(self._protocol, addr + 1, 8, speed, mode=0x49)

    def set_knob_channel(self, knob_index, channel, shifted=False):
        """Set a knob's MIDI channel (0-15)."""
        addr = self._protocol.get_knob_addr(knob_index, shifted=shifted)
        self._midi.send_param(self._protocol, addr + 2, 8, channel, mode=0x49)

    def set_knob_cc(self, knob_index, cc, shifted=False):
        """Set a knob's CC number."""
        addr = self._protocol.get_knob_addr(knob_index, shifted=shifted)
        self._midi.send_param(self._protocol, addr + 3, 8, cc, mode=0x49)

    def configure_knob(self, knob_index, channel, cc, speed=0, shifted=False):
        """Fully configure a knob as relative CC."""
        self.set_knob_type(knob_index, KNOB_TYPE_RELATIVE, shifted=shifted)
        self.set_knob_speed(knob_index, speed, shifted=shifted)
        self.set_knob_channel(knob_index, channel, shifted=shifted)
        self.set_knob_cc(knob_index, cc, shifted=shifted)

    # -------------------------------------------------------------------------
    # Pad configuration
    # -------------------------------------------------------------------------

    def set_pad_color(self, pad_index, color, shifted=False):
        """Set a pad's RGB color only (not LED state)."""
        addr = self._protocol.get_pad_addr(pad_index, shifted=shifted)
        # Set color only - LED state is set separately during init
        self._midi.send_param(self._protocol, addr + 5, 24, color, mode=0x59)

    def set_pad_led_state(self, pad_index, led_state, shifted=False):
        """Set a pad's LED on/off state (0-255)."""
        addr = self._protocol.get_pad_addr(pad_index, shifted=shifted)
        self._midi.send_param(self._protocol, addr + 8, 8, led_state, mode=0x49)

    def set_pad_type(self, pad_index, pad_type, shifted=False):
        """Set a pad's type."""
        addr = self._protocol.get_pad_addr(pad_index, shifted=shifted)
        self._midi.send_param(self._protocol, addr, 8, pad_type, mode=0x49)

    def set_pad_note(self, pad_index, note, shifted=False):
        """Set a pad's note number."""
        addr = self._protocol.get_pad_addr(pad_index, shifted=shifted)
        self._midi.send_param(self._protocol, addr + 2, 8, note, mode=0x49)

    def set_pad_channel(self, pad_index, channel, shifted=False):
        """Set a pad's MIDI channel (0-15)."""
        addr = self._protocol.get_pad_addr(pad_index, shifted=shifted)
        self._midi.send_param(self._protocol, addr + 1, 8, channel, mode=0x49)

    def set_pad_velocity_range(self, pad_index, min_vel, max_vel, shifted=False):
        """Set a pad's velocity range."""
        addr = self._protocol.get_pad_addr(pad_index, shifted=shifted)
        self._midi.send_param(self._protocol, addr + 3, 8, min_vel, mode=0x49)
        self._midi.send_param(self._protocol, addr + 4, 8, max_vel, mode=0x49)

    def configure_pad(self, pad_index, pad_type, channel, note, shifted=False):
        """Fully configure a pad."""
        self._log(f"HW: configure_pad(pad={pad_index}, type={pad_type}, ch={channel}, note={note}, shifted={shifted})")
        self.set_pad_type(pad_index, pad_type, shifted=shifted)
        self.set_pad_channel(pad_index, channel, shifted=shifted)
        self.set_pad_note(pad_index, note, shifted=shifted)
        self.set_pad_velocity_range(pad_index, 0, 127, shifted=shifted)

    def set_pad_sysex(self, pad_index, sysex_bytes, shifted=False):
        """Set a pad's sysex payload (for CUSTOM pads).

        Args:
            pad_index: Pad index (0-15)
            sysex_bytes: List of MIDI bytes to send when pad is pressed
            shifted: Whether to configure shifted pad
        """
        addr = self._protocol.get_pad_addr(pad_index, shifted=shifted)
        msg = self._protocol.build_sysex_packet(addr, sysex_bytes)
        self._midi.send(msg)
