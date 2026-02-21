"""Drum Color mode (Mode 9) - Drum pads with color editing."""

import os
import json
import time
import colorsys
from .base import ModeBase
from ..Hardware import PAD_TYPE_CUSTOM, PAD_TYPE_NOTE

# Drum mode settings
DRUM_COLOR_PAD_CHANNEL = 9  # Channel 10 (standard MIDI drum channel)
DRUM_COLOR_KNOB_CHANNEL = 10  # Channel 11
DRUM_BASE_NOTE = 36  # C1
DRUM_KNOB_BASE_CC = 20  # CC 20-27

# Default HSV values (hue, saturation, value/brightness)
# Start with orange color (matches Mode 8 Drums default)
# Orange: RGB(255, 160, 0) = HSV(37.65°, 100%, 100%)
DEFAULT_HSV = [(37.65/360, 1.0, 1.0)] * 16  # All pads orange


class DrumColorMode(ModeBase):
    """Drum Color mode - Drum pads with interactive color editing."""

    def __init__(self, controller, hardware, mode_number):
        super(DrumColorMode, self).__init__(controller, hardware, mode_number)
        self._pad_release_times = {}  # Map pad_index -> release timestamp
        self._pad_press_times = {}  # Map pad_index -> press timestamp
        self._pad_colors_hsv = list(DEFAULT_HSV)  # HSV values for each pad
        self._instrument_colors = {}  # Map instrument ID -> color array
        self._history = []  # History of last 16 instrument IDs
        self._history_index = 0  # Current position in history navigation
        self._config_file = None  # Path to config file
        self._current_instrument_id = None  # Current instrument device ID
        self._device_listener = None  # Device change listener

    def configure(self):
        """Configure hardware for drum color mode."""
        self.log("Configuring drum color mode...")

        # Clear hardware cache
        self._hw.clear_cache()

        # Initialize all pad press/release times to 0
        self._pad_press_times = {i: 0 for i in range(16)}
        self._pad_release_times = {i: 0 for i in range(16)}

        # Load configuration
        self._load_config()

        # Get current instrument and load its colors
        self._update_instrument()

        # Configure all pads as regular NOTE pads on channel 9
        # Same layout as Mode 8: top row (0-7) = upper notes (44-51), bottom row (8-15) = lower notes (36-43)
        for i in range(16):
            if i < 8:
                # Top row - upper octave (notes 44-51)
                note = DRUM_BASE_NOTE + 8 + i
            else:
                # Bottom row - lower octave (notes 36-43)
                note = DRUM_BASE_NOTE + (i - 8)

            # Configure as NOTE type on channel 9
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=DRUM_COLOR_PAD_CHANNEL,  # Channel 9
                note=note,
                shifted=False
            )

        # Set all LEDs to ON (255)
        for i in range(16):
            self._hw.set_pad_led_state(i, 255, shifted=False)

        # Configure knobs as relative (CW type)
        for i in range(8):
            self._hw.configure_knob(
                knob_index=i,
                channel=DRUM_COLOR_KNOB_CHANNEL,
                cc=DRUM_KNOB_BASE_CC + i,
                shifted=False
            )

        # Add device change listener
        self._add_device_listener()

        # Initial color update
        self.update()

        self.log("Drum color mode configured.")

    def update(self):
        """Update pad colors based on current HSV values."""
        for i in range(16):
            h, s, v = self._pad_colors_hsv[i]
            rgb = self._hsv_to_rgb(h, s, v)
            self._hw.set_pad_color(i, rgb, shifted=False)

    def handle_pad(self, pad_index, velocity):
        """Handle pad press/release - track press/release times for color editing."""
        if velocity == 0:
            # Pad released - record the release time
            self._pad_release_times[pad_index] = time.time()
        else:
            # Pad pressed - record the press time
            self._pad_press_times[pad_index] = time.time()

    def handle_knob(self, knob_index, value):
        """Handle knob turn in drum color mode."""
        delta = self._decode_relative_value(value)
        if delta == 0:
            return

        # Knob 0: Hue adjustment
        if knob_index == 0:
            self._adjust_hue(delta)

        # Knob 1: Saturation adjustment
        elif knob_index == 1:
            self._adjust_saturation(delta)

        # Knob 2: Brightness/Value adjustment
        elif knob_index == 2:
            self._adjust_brightness(delta)

        # Knob 3: Red adjustment
        elif knob_index == 3:
            self._adjust_red(delta)

        # Knob 4: Green adjustment
        elif knob_index == 4:
            self._adjust_green(delta)

        # Knob 5: Blue adjustment
        elif knob_index == 5:
            self._adjust_blue(delta)

        # Knob 6: Match color
        elif knob_index == 6:
            self._match_color(delta)

        # Knob 7: History navigation
        elif knob_index == 7:
            self._navigate_history(delta)

    def _get_recently_released_pads(self):
        """Get pads that were pressed or released while the most recently released pad was held.

        Algorithm:
        1. Find the pad that was most recently released (pad R)
        2. Get the time window [R's press time, R's release time]
        3. Include all pads that were pressed OR released during this window
        """
        if not self._pad_release_times:
            return []

        # Find the most recently released pad
        most_recent_pad = max(self._pad_release_times.keys(),
                             key=lambda p: self._pad_release_times[p])

        # Get the time window for this pad
        press_time = self._pad_press_times.get(most_recent_pad, 0)
        release_time = self._pad_release_times[most_recent_pad]

        # Include all pads that were pressed or released during this window
        recent_pads = []
        for pad_idx in range(16):
            pad_press = self._pad_press_times.get(pad_idx, 0)
            pad_release = self._pad_release_times.get(pad_idx, 0)

            # Check if this pad was pressed or released during the window
            pressed_during = press_time <= pad_press <= release_time
            released_during = press_time <= pad_release <= release_time

            if pressed_during or released_during:
                recent_pads.append(pad_idx)

        return recent_pads

    def _adjust_hue(self, delta):
        """Adjust hue for recently released pads only."""
        recent_pads = self._get_recently_released_pads()

        if not recent_pads:
            return

        for pad_idx in recent_pads:
            h, s, v = self._pad_colors_hsv[pad_idx]
            # Hue rotates (wraps around 0-1)
            h = (h + delta * 0.02) % 1.0  # 2% step, wraps at 1.0
            self._pad_colors_hsv[pad_idx] = (h, s, v)

        self.update()
        self._save_current_instrument_colors()

    def _adjust_saturation(self, delta):
        """Adjust saturation for recently released pads only."""
        recent_pads = self._get_recently_released_pads()

        if not recent_pads:
            return

        for pad_idx in recent_pads:
            h, s, v = self._pad_colors_hsv[pad_idx]
            # Saturation clamps at 0-1
            s = max(0.0, min(1.0, s + delta * 0.02))  # 2% step
            self._pad_colors_hsv[pad_idx] = (h, s, v)

        self.update()
        self._save_current_instrument_colors()

    def _adjust_brightness(self, delta):
        """Adjust brightness/value for recently released pads only."""
        recent_pads = self._get_recently_released_pads()

        if not recent_pads:
            return

        for pad_idx in recent_pads:
            h, s, v = self._pad_colors_hsv[pad_idx]
            # Brightness clamps at 0-1
            v = max(0.0, min(1.0, v + delta * 0.02))  # 2% step
            self._pad_colors_hsv[pad_idx] = (h, s, v)

        self.update()
        self._save_current_instrument_colors()

    def _adjust_red(self, delta):
        """Adjust red channel for recently released pads only."""
        recent_pads = self._get_recently_released_pads()

        if not recent_pads:
            return

        for pad_idx in recent_pads:
            h, s, v = self._pad_colors_hsv[pad_idx]
            # Convert to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            # Adjust red
            r = max(0.0, min(1.0, r + delta * 0.04))  # 4% step (2x speed)
            # Convert back to HSV
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            self._pad_colors_hsv[pad_idx] = (h, s, v)

        self.update()
        self._save_current_instrument_colors()

    def _adjust_green(self, delta):
        """Adjust green channel for recently released pads only."""
        recent_pads = self._get_recently_released_pads()

        if not recent_pads:
            return

        for pad_idx in recent_pads:
            h, s, v = self._pad_colors_hsv[pad_idx]
            # Convert to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            # Adjust green
            g = max(0.0, min(1.0, g + delta * 0.04))  # 4% step (2x speed)
            # Convert back to HSV
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            self._pad_colors_hsv[pad_idx] = (h, s, v)

        self.update()
        self._save_current_instrument_colors()

    def _adjust_blue(self, delta):
        """Adjust blue channel for recently released pads only."""
        recent_pads = self._get_recently_released_pads()

        if not recent_pads:
            return

        for pad_idx in recent_pads:
            h, s, v = self._pad_colors_hsv[pad_idx]
            # Convert to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            # Adjust blue
            b = max(0.0, min(1.0, b + delta * 0.04))  # 4% step (2x speed)
            # Convert back to HSV
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            self._pad_colors_hsv[pad_idx] = (h, s, v)

        self.update()
        self._save_current_instrument_colors()

    def _match_color(self, delta):
        """Move all recently released pads towards the most recently pressed pad's color.

        Moves each HSV component towards target by 0.04 per rotation (2x speed).
        """
        recent_pads = self._get_recently_released_pads()

        if len(recent_pads) < 2:
            # Need at least 2 pads to match
            return

        # Find the most recently pressed pad
        target_pad = max(recent_pads, key=lambda p: self._pad_press_times.get(p, 0))
        target_h, target_s, target_v = self._pad_colors_hsv[target_pad]

        # Move other pads towards target color
        step = 0.04  # 4% step (2x speed)
        for pad_idx in recent_pads:
            if pad_idx == target_pad:
                continue

            h, s, v = self._pad_colors_hsv[pad_idx]

            # Move each component towards target
            if h < target_h:
                h = min(h + step, target_h)
            elif h > target_h:
                h = max(h - step, target_h)

            if s < target_s:
                s = min(s + step, target_s)
            elif s > target_s:
                s = max(s - step, target_s)

            if v < target_v:
                v = min(v + step, target_v)
            elif v > target_v:
                v = max(v - step, target_v)

            self._pad_colors_hsv[pad_idx] = (h, s, v)

        self.update()
        self._save_current_instrument_colors()

    def _navigate_history(self, delta):
        """Navigate through history of instrument color layouts."""
        if not self._history:
            return

        self._history_index = (self._history_index + delta) % len(self._history)
        instrument_id = self._history[self._history_index]

        if instrument_id in self._instrument_colors:
            # Load colors from history
            self._pad_colors_hsv = list(self._instrument_colors[instrument_id])
            self.update()
            self.log(f"Loaded colors from history: {instrument_id}")

    def _add_device_listener(self):
        """Add listener for device changes."""
        song = self.song()

        def on_device_change():
            """Called when selected track or device changes."""
            self._update_instrument()
            self.update()

        # Listen for track changes (which may change the device)
        song.view.add_selected_track_listener(on_device_change)
        self._device_listener = on_device_change

    def _remove_device_listener(self):
        """Remove device change listener."""
        if self._device_listener:
            song = self.song()
            song.view.remove_selected_track_listener(self._device_listener)
            self._device_listener = None

    def _update_instrument(self):
        """Update current instrument and load its colors."""
        song = self.song()
        track = song.view.selected_track

        # Get first device on track (typically the instrument/drum rack)
        devices = list(track.devices) if hasattr(track, 'devices') else []
        if not devices:
            self._current_instrument_id = None
            return

        device = devices[0]
        instrument_id = self._get_instrument_id(device)

        if instrument_id != self._current_instrument_id:
            self._current_instrument_id = instrument_id

            # Check if we have saved colors for this instrument
            if instrument_id in self._instrument_colors:
                # Load saved colors
                self._pad_colors_hsv = list(self._instrument_colors[instrument_id])
                self.log(f"Loaded saved colors for instrument: {instrument_id}")
            else:
                # New instrument - use current colors (last shown)
                self._save_current_instrument_colors()
                self.log(f"New instrument, assigned current colors: {instrument_id}")

            # Update history
            if instrument_id in self._history:
                self._history.remove(instrument_id)
            self._history.insert(0, instrument_id)
            # Keep only last 16
            self._history = self._history[:16]
            self._history_index = 0

            self._save_config()

    def _get_instrument_id(self, device):
        """Get a unique identifier for the instrument device."""
        # Use device name + class name as identifier
        # Could also use device hash or other unique properties
        try:
            return f"{device.class_name}:{device.name}"
        except:
            return "unknown"

    def _save_current_instrument_colors(self):
        """Save current pad colors for the current instrument."""
        if self._current_instrument_id:
            self._instrument_colors[self._current_instrument_id] = list(self._pad_colors_hsv)
            self._save_config()

    def _load_config(self):
        """Load color configuration from file."""
        try:
            # Get user home directory and create config path
            # Ableton allows scripts to write to user preferences directory
            home = os.path.expanduser("~")
            config_dir = os.path.join(home, ".config", "SMK25II")

            # Create directory if it doesn't exist
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            self._config_file = os.path.join(config_dir, "drum_colors.json")

            # Load existing config
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    data = json.load(f)
                    self._instrument_colors = data.get('instruments', {})
                    self._history = data.get('history', [])
                    self.log(f"Loaded config from {self._config_file}")
            else:
                self.log(f"No existing config, will create: {self._config_file}")

        except Exception as e:
            self.log(f"ERROR loading config: {e}")
            self._instrument_colors = {}
            self._history = []

    def _save_config(self):
        """Save color configuration to file."""
        if not self._config_file:
            return

        try:
            data = {
                '_readme': 'SMK25II Drum Color Config - Each instrument has 16 pads with [hue, saturation, brightness] values (0.0-1.0)',
                'instruments': self._instrument_colors,
                'history': self._history
            }
            with open(self._config_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.log(f"Saved config to {self._config_file}")

        except Exception as e:
            self.log(f"ERROR saving config: {e}")

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB integer (for LED)."""
        # Use Python's colorsys module
        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        # Convert to 0-255 range
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)

        # Pack into RGB integer: R | G<<8 | B<<16
        return r | (g << 8) | (b << 16)

    def _decode_relative_value(self, value):
        """Decode relative CC value to delta."""
        if value == 0x7F:
            return 1  # Clockwise
        elif value == 0x00:
            return -1  # Counter-clockwise
        else:
            self.log(f"ERROR: Unexpected relative knob value: {value}")
            return 0

    def disconnect(self):
        """Cleanup when leaving drum color mode."""
        self.log("Disconnecting drum color mode...")
        # Remove device listener
        self._remove_device_listener()
        # Save final state
        self._save_config()
