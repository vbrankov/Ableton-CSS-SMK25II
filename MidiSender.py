import time
import sys

IS_WINDOWS = sys.platform == 'win32'
MIN_SEND_INTERVAL = 0.001  # 1ms between messages


class MidiSender:
    """Handles MIDI sending with caching and throttling."""

    def __init__(self, send_func, log_func=None):
        """
        Args:
            send_func: Function to call to send MIDI (e.g., c_instance.send_midi)
            log_func: Optional logging function
        """
        self._send_func = send_func
        self._log_func = log_func
        self._last_send_time = 0.0
        self._cache = {}  # Maps (addr, mode) -> value
        self._bulk_mode = False

    def set_bulk_mode(self, enabled):
        """Enable/disable bulk mode (uses sleep instead of spin lock)."""
        self._bulk_mode = enabled

    def clear_cache(self):
        """Clear the value cache (e.g., when reconnecting to device)."""
        self._cache = {}

    def send(self, msg, cache_key=None):
        """
        Send a MIDI message with throttling.

        Args:
            msg: The MIDI message (tuple/list of bytes)
            cache_key: Optional key for caching. If provided and the value
                      matches the cached value, the message won't be sent.
        """
        # Check cache
        if cache_key is not None:
            msg_tuple = tuple(msg)
            if self._cache.get(cache_key) == msg_tuple:
                return  # Already sent this value
            self._cache[cache_key] = msg_tuple

        # Throttle
        self._wait_for_interval()

        # Send
        self._send_func(tuple(msg))
        self._last_send_time = time.perf_counter()

    def send_param(self, protocol, addr, bit_len, value, mode=0x49):
        """
        Send a parameter value, with caching by address.

        Args:
            protocol: ProtocolHandler instance
            addr: Parameter address
            bit_len: Value bit length
            value: Value to send
            mode: Protocol mode (0x49 for config, 0x59 for color)
        """
        cache_key = (addr, mode)

        # Check cache
        if self._cache.get(cache_key) == value:
            return  # Already sent this value

        # Build message
        msg = protocol.build_packet(addr, bit_len, value, mode=mode)
        self._cache[cache_key] = value

        # Throttle
        self._wait_for_interval()

        # Send
        self._send_func(tuple(msg))
        self._last_send_time = time.perf_counter()

    def _wait_for_interval(self):
        """Wait until minimum interval has passed since last send."""
        now = time.perf_counter()
        elapsed = now - self._last_send_time

        if elapsed < MIN_SEND_INTERVAL:
            wait_until = self._last_send_time + MIN_SEND_INTERVAL
            remaining = wait_until - now

            if self._bulk_mode or not IS_WINDOWS:
                time.sleep(remaining)
            else:
                # Busy-wait on Windows for precise timing
                while time.perf_counter() < wait_until:
                    pass
