"""Base class for all modes."""


class ModeBase:
    """Abstract base class for all modes."""

    def __init__(self, controller, hardware, mode_number):
        """
        Initialize mode.

        Args:
            controller: MyController instance
            hardware: Hardware instance
            mode_number: Mode number (0-15)
        """
        self._controller = controller
        self._hw = hardware
        self._mode_number = mode_number

    def configure(self):
        """
        Configure hardware and software for this mode.
        Called when entering the mode.
        """
        pass

    def update(self):
        """
        Update mode state (colors, visual feedback, etc.).
        Called periodically or when state changes.
        """
        pass

    def handle_pad(self, pad_index, velocity):
        """
        Handle pad press/release.

        Args:
            pad_index: Pad index (0-15)
            velocity: MIDI velocity (0-127, 0 = release)
        """
        pass

    def handle_knob(self, knob_index, value):
        """
        Handle knob turn.

        Args:
            knob_index: Knob index (0-7)
            value: Relative CC value
        """
        pass

    def disconnect(self):
        """
        Cleanup when leaving mode.
        Remove listeners, clear state, etc.
        """
        pass

    # Utility methods available to all modes
    def log(self, message):
        """Log a message."""
        self._controller.log_message(f"[Mode {self._mode_number}] {message}")

    def song(self):
        """Get the Live song instance."""
        return self._controller.song()

    def application(self):
        """Get the Live application instance."""
        return self._controller.application()
