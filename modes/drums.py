"""Drums mode (Mode 8) - Drum pad mode."""

from .base import ModeBase
from ..Hardware import PAD_TYPE_NOTE

# Drum mode settings
DRUM_CHANNEL = 0  # Channel 1
DRUM_BASE_NOTE = 36  # C1
COLOR_DRUM = 0x00A0FF  # Orange


class DrumsMode(ModeBase):
    """Drums mode - Basic drum pad grid."""

    def configure(self):
        """Configure hardware for drums mode."""
        self.log("Configuring drums mode...")

        # Clear hardware cache
        self._hw.clear_cache()

        # Configure all pads as drum notes
        for i in range(16):
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=DRUM_CHANNEL,
                note=DRUM_BASE_NOTE + i,
                shifted=False
            )
            # Set color to orange
            self._hw.set_pad_color(i, COLOR_DRUM, shifted=False)

        self.log("Drums mode configured.")

    def update(self):
        """Update drum mode (no dynamic updates needed)."""
        pass

    def handle_pad(self, pad_index, velocity):
        """Handle pad press (notes sent automatically by hardware)."""
        pass

    def handle_knob(self, knob_index, value):
        """Handle knob turn in drums mode."""
        # Could add drum volume, tuning, etc. later
        pass

    def disconnect(self):
        """Cleanup when leaving drums mode."""
        self.log("Disconnecting drums mode...")
