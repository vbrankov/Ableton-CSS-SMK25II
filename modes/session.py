"""Session mode (Mode 0) - Track control with clip launching."""

import Live
from .base import ModeBase
from ..Hardware import PAD_TYPE_NOTE, COLOR_OFF

# Track control mode settings
TRACK_CTRL_CHANNEL = 9  # Channel 14 (0-indexed)
TRACK_CTRL_BASE_NOTE = 36
TRACK_CTRL_COLS = 7  # 7 columns for clips
TRACK_CTRL_ROWS = 2  # 2 rows

# Session mode knob settings
SESSION_KNOB_CHANNEL = 0  # Channel 1 (0-indexed)
SESSION_KNOB_BASE_CC = 21  # CC 21-28

# Session knob functions
SESSION_KNOB_SCROLL_V = 0
SESSION_KNOB_SCROLL_H = 1
SESSION_KNOB_PAD_MODE = 2
SESSION_KNOB_QUANTIZATION = 3
SESSION_KNOB_TEMPO = 4
SESSION_KNOB_METRONOME = 5
SESSION_KNOB_MASTER = 6
SESSION_KNOB_UNDO = 7


class SessionMode(ModeBase):
    """Session mode - Track control with clip launching."""

    def __init__(self, controller, hardware, mode_number):
        super().__init__(controller, hardware, mode_number)

        # Session box position
        self._session_track_offset = 0
        self._session_scene_offset = 0

        # Flash state for LEDs
        self._flash_state = 0  # 0 or 1
        self._last_flash_time = 0
        self._flash_interval = 0.25  # 250ms (double speed)

        # Clip launch mode
        self._clip_launch_mode = 0  # 0=play/stop, 1=stop, 2=record

        # Mode selector state
        self._is_showing_mode_selector = False
        self._mode_selector_timeout = 0

        # Listeners
        self._clip_slot_listeners = []

    def configure(self):
        """Configure hardware for session mode."""
        self.log("Configuring session mode...")

        # Clear hardware cache
        self._hw.clear_cache()

        # Configure pads as MCP type
        for i in range(16):
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=TRACK_CTRL_CHANNEL,
                note=TRACK_CTRL_BASE_NOTE + i,
                shifted=False
            )
            # Set LED state to ON
            self._hw.set_pad_led_state(i, 255, shifted=False)

        # Configure knobs
        self._configure_session_knobs()

        # Set session highlight
        self._set_session_highlight()

        # Add listeners
        self._add_clip_slot_listeners()
        self._add_track_list_listener()

        # Initial color update
        self.update()

        # Schedule a delayed update to handle Ableton startup timing issues
        # Sometimes track colors aren't fully initialized on first update
        self._controller.schedule_message(5, self._delayed_startup_update)

        # Start periodic updates for flashing
        self._schedule_next_update()

        self.log("Session mode configured.")

    def update(self):
        """Update pad colors based on clip states."""
        song = self.song()
        tracks = song.visible_tracks

        for row in range(TRACK_CTRL_ROWS):
            scene_idx = self._session_scene_offset + row

            for col in range(TRACK_CTRL_COLS):
                track_idx = self._session_track_offset + col
                pad_idx = col + (row * 8)

                if track_idx < len(tracks) and scene_idx < len(song.scenes):
                    track = tracks[track_idx]
                    clip_slot = track.clip_slots[scene_idx]
                    color = self._get_session_pad_color(clip_slot, track, self._flash_state)
                else:
                    color = COLOR_OFF

                self._hw.set_pad_color(pad_idx, color, shifted=False)

            # Scene pad (column 7) - use master track color
            scene_pad_idx = 7 + (row * 8)
            if scene_idx < len(song.scenes):
                master_color = self._get_track_color_rgb(song.master_track)
                self._hw.set_pad_color(scene_pad_idx, master_color, shifted=False)
            else:
                self._hw.set_pad_color(scene_pad_idx, COLOR_OFF, shifted=False)

    def _delayed_startup_update(self):
        """Delayed update after configure to handle Ableton startup timing."""
        self.log("Delayed startup update - refreshing colors...")
        self.update()

    def handle_pad(self, pad_index, velocity):
        """Handle pad press in session mode."""
        if velocity == 0:  # Release
            return

        # Scene launch pads (column 7)
        if pad_index in [7, 15]:
            row = 0 if pad_index == 7 else 1
            self._launch_scene(row)
        else:
            # Clip launch pads
            col = pad_index % 8
            row = pad_index // 8
            if col < TRACK_CTRL_COLS:
                self._toggle_clip(col, row)

    def handle_knob(self, knob_index, value):
        """Handle knob turn in session mode."""
        delta = self._decode_relative_value(value)
        if delta == 0:
            return

        if knob_index == SESSION_KNOB_SCROLL_V:
            self._scroll_view_horizontal(delta)  # Scroll red box horizontally
        elif knob_index == SESSION_KNOB_SCROLL_H:
            self._scroll_view_vertical(delta)  # Scroll red box vertically
        elif knob_index == SESSION_KNOB_PAD_MODE:
            self._handle_pad_mode_selector(delta)
        elif knob_index == SESSION_KNOB_QUANTIZATION:
            self._adjust_quantization(delta)
        elif knob_index == SESSION_KNOB_TEMPO:
            self._adjust_tempo(delta)
        elif knob_index == SESSION_KNOB_METRONOME:
            self._adjust_metronome_volume(delta)
        elif knob_index == SESSION_KNOB_MASTER:
            self._adjust_master_volume(delta)
        elif knob_index == SESSION_KNOB_UNDO:
            self._undo_redo(delta)

    def get_pad_colors(self):
        """Get current pad colors for web display."""
        colors = []
        song = self.song()
        tracks = song.visible_tracks

        for row in range(TRACK_CTRL_ROWS):
            scene_idx = self._session_scene_offset + row

            for col in range(TRACK_CTRL_COLS):
                track_idx = self._session_track_offset + col
                pad_idx = col + (row * 8)

                if track_idx < len(tracks) and scene_idx < len(song.scenes):
                    track = tracks[track_idx]
                    clip_slot = track.clip_slots[scene_idx]
                    color = self._get_session_pad_color(clip_slot, track, self._flash_state)
                else:
                    color = COLOR_OFF

                colors.append(color)

            # Scene pad (column 7) - use master track color
            if scene_idx < len(song.scenes):
                master_color = self._get_track_color_rgb(song.master_track)
                colors.append(master_color)
            else:
                colors.append(COLOR_OFF)

        return colors

    def get_pad_labels(self):
        """Get current pad labels (track names for clips, scene number+name for scenes)."""
        labels = []
        song = self.song()
        tracks = song.visible_tracks

        for row in range(TRACK_CTRL_ROWS):
            scene_idx = self._session_scene_offset + row

            for col in range(TRACK_CTRL_COLS):
                track_idx = self._session_track_offset + col

                # Clip pads: just track name (replace dash with space)
                if track_idx < len(tracks):
                    track = tracks[track_idx]
                    track_name = track.name.replace('-', ' ')
                    labels.append(track_name)
                else:
                    labels.append('')

            # Scene pad (column 7): scene number + name
            if scene_idx < len(song.scenes):
                scene = song.scenes[scene_idx]
                scene_num = scene_idx + 1
                scene_name = scene.name if hasattr(scene, 'name') and scene.name else ''
                if scene_name:
                    labels.append(f"{scene_num} {scene_name}")
                else:
                    labels.append(f"{scene_num}")
            else:
                labels.append('')

        return labels

    def disconnect(self):
        """Cleanup when leaving session mode."""
        self.log("Disconnecting session mode...")
        self._remove_clip_slot_listeners()
        self._remove_track_list_listener()

    # -------------------------------------------------------------------------
    # Configuration helpers
    # -------------------------------------------------------------------------

    def _configure_session_knobs(self):
        """Configure knobs for session mode."""
        self.log("Configuring session knobs...")
        for i in range(8):
            self._hw.configure_knob(
                knob_index=i,
                channel=SESSION_KNOB_CHANNEL,
                cc=SESSION_KNOB_BASE_CC + i,
                shifted=False
            )

    def _set_session_highlight(self):
        """Set Ableton's red box highlight."""
        self._controller.set_session_highlight(
            self._session_track_offset,
            self._session_scene_offset,
            TRACK_CTRL_COLS,
            TRACK_CTRL_ROWS,
            False  # include_return_tracks
        )

    # -------------------------------------------------------------------------
    # Periodic updates (for flashing)
    # -------------------------------------------------------------------------

    def _schedule_next_update(self):
        """Schedule next periodic update."""
        self._controller.schedule_message(1, self._periodic_update)

    def _periodic_update(self):
        """Periodic update for mode selector timeout."""
        import time
        current_time = time.time()

        # Handle mode selector timeout
        if self._is_showing_mode_selector:
            if current_time - self._mode_selector_timeout >= 0.25:
                self._is_showing_mode_selector = False
                self.update()

        # Reschedule
        self._schedule_next_update()

    # -------------------------------------------------------------------------
    # Color calculation
    # -------------------------------------------------------------------------

    def _get_session_pad_color(self, clip_slot, track, flash_state=0):
        """Get pad color for session mode."""
        track_color = self._get_track_color_rgb(track)
        dim_color = self._darken_color(track_color, 0.33)  # 1/3 brightness

        if not clip_slot.has_clip:
            return dim_color

        is_recording = track.arm and clip_slot.is_playing

        if is_recording:
            # Recording: blend red and track color (50/50)
            return self._blend_colors(0x0000FF, track_color)
        elif clip_slot.is_playing:
            # Playing: blend white and track color (50/50)
            return self._blend_colors(0xFFFFFF, track_color)
        elif clip_slot.is_triggered:
            # Triggered: full track color
            return track_color
        else:
            # Stopped: full track color
            return track_color

    def _get_track_color_rgb(self, track):
        """Get track color in hardware RGB format."""
        try:
            # Check if track is valid
            if not track or not hasattr(track, 'color'):
                self.log(f"Track invalid or no color attribute: {track}")
                return 0x808080  # Default grey

            ableton_color = track.color

            # Validate color value
            if ableton_color is None or ableton_color < 0:
                self.log(f"Track {track.name} has invalid color: {ableton_color}")
                return 0x808080

            r = (ableton_color >> 16) & 0xFF
            g = (ableton_color >> 8) & 0xFF
            b = ableton_color & 0xFF
            hw_color = r | (g << 8) | (b << 16)
            return hw_color
        except Exception as e:
            self.log(f"Error getting track color: {e}")
            return 0x808080

    def _darken_color(self, rgb, brightness):
        """Darken RGB color to brightness factor (0.0-1.0)."""
        r = int(((rgb >> 0) & 0xFF) * brightness)
        g = int(((rgb >> 8) & 0xFF) * brightness)
        b = int(((rgb >> 16) & 0xFF) * brightness)
        return r | (g << 8) | (b << 16)

    def _blend_colors(self, color1, color2):
        """Blend two RGB colors together (50/50 average).

        Args:
            color1: First RGB color
            color2: Second RGB color
        """
        r1 = (color1 >> 0) & 0xFF
        g1 = (color1 >> 8) & 0xFF
        b1 = (color1 >> 16) & 0xFF

        r2 = (color2 >> 0) & 0xFF
        g2 = (color2 >> 8) & 0xFF
        b2 = (color2 >> 16) & 0xFF

        # Average using bit shift: (a + b) >> 1
        r = (r1 + r2) >> 1
        g = (g1 + g2) >> 1
        b = (b1 + b2) >> 1

        return r | (g << 8) | (b << 16)

    # -------------------------------------------------------------------------
    # Clip/scene launching
    # -------------------------------------------------------------------------

    def _toggle_clip(self, col, row):
        """Launch/stop clip based on current launch mode."""
        song = self.song()
        tracks = song.visible_tracks
        track_idx = self._session_track_offset + col
        scene_idx = self._session_scene_offset + row

        if track_idx < len(tracks) and scene_idx < len(song.scenes):
            track = tracks[track_idx]
            clip_slot = track.clip_slots[scene_idx]

            if self._clip_launch_mode == 0:  # Play/Stop
                if clip_slot.is_playing:
                    track.stop_all_clips()
                elif clip_slot.has_clip:
                    clip_slot.fire()
            elif self._clip_launch_mode == 1:  # Stop only
                if clip_slot.is_playing:
                    track.stop_all_clips()
            elif self._clip_launch_mode == 2:  # Record
                if not track.can_be_armed:
                    return
                track.arm = True
                if clip_slot.has_clip:
                    clip_slot.fire()
                else:
                    clip_slot.fire()

    def _launch_scene(self, row):
        """Launch a scene."""
        song = self.song()
        scene_idx = self._session_scene_offset + row
        if scene_idx < len(song.scenes):
            song.scenes[scene_idx].fire()

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------

    def _scroll_view_vertical(self, delta):
        """Scroll session box vertically."""
        song = self.song()
        new_offset = max(0, min(len(song.scenes) - TRACK_CTRL_ROWS,
                                self._session_scene_offset + delta))
        self.log(f"Scene offset: {self._session_scene_offset} -> {new_offset}")
        if new_offset != self._session_scene_offset:
            self._session_scene_offset = new_offset
            self._set_session_highlight()
            self._remove_clip_slot_listeners()
            self._add_clip_slot_listeners()
            self.update()

    def _scroll_view_horizontal(self, delta):
        """Scroll session box horizontally."""
        self.log(f"Scroll horizontal: delta={delta}")
        song = self.song()
        new_offset = max(0, min(len(song.visible_tracks) - TRACK_CTRL_COLS,
                                self._session_track_offset + delta))
        self.log(f"Track offset: {self._session_track_offset} -> {new_offset}")
        if new_offset != self._session_track_offset:
            self._session_track_offset = new_offset
            self._set_session_highlight()
            self._remove_clip_slot_listeners()
            self._add_clip_slot_listeners()
            self.update()

    # -------------------------------------------------------------------------
    # Knob handlers
    # -------------------------------------------------------------------------

    def _handle_pad_mode_selector(self, delta):
        """Move through pad launch modes (left/right, clamped 0-2)."""
        # Clamp to 0-2
        new_mode = self._clip_launch_mode + delta
        self._clip_launch_mode = max(0, min(2, new_mode))
        self._show_mode_selector()
        import time
        self._mode_selector_timeout = time.time()
        self.log(f"Clip launch mode: {self._clip_launch_mode}")

    def _show_mode_selector(self):
        """Show mode selector on bottom-left 3 pads."""
        from ..Hardware import COLOR_WHITE, COLOR_DIM_WHITE

        self._is_showing_mode_selector = True

        for i in range(16):
            if i in [8, 9, 10]:
                is_selected = (i - 8) == self._clip_launch_mode
                color = COLOR_WHITE if is_selected else COLOR_DIM_WHITE
                self._hw.set_pad_color(i, color, shifted=False)
            else:
                self._hw.set_pad_color(i, COLOR_OFF, shifted=False)

    def _adjust_quantization(self, delta):
        """Adjust global quantization."""
        song = self.song()
        current = song.clip_trigger_quantization
        new_value = max(0, min(13, current - delta))
        song.clip_trigger_quantization = new_value
        self.log(f"Quantization: {new_value}")

    def _adjust_tempo(self, delta):
        """Adjust tempo."""
        song = self.song()
        new_tempo = max(20, min(999, song.tempo + delta))
        song.tempo = new_tempo
        self.log(f"Tempo: {new_tempo:.1f}")

    def _adjust_metronome_volume(self, delta):
        """Toggle metronome on/off (right = on, left = off)."""
        song = self.song()
        if delta > 0:
            song.metronome = True
            self.log("Metronome: ON")
        elif delta < 0:
            song.metronome = False
            self.log("Metronome: OFF")

    def _adjust_master_volume(self, delta):
        """Adjust master volume."""
        song = self.song()
        master = song.master_track
        mixer = master.mixer_device

        current = mixer.volume.value
        new_value = max(0.0, min(1.0, current + delta * 0.02))
        mixer.volume.value = new_value
        self.log(f"Master volume: {new_value:.2f}")

    def _undo_redo(self, delta):
        """Undo/redo operations."""
        song = self.song()
        if delta < 0:
            if song.can_undo:
                song.undo()
                self.log("Undo")
        else:
            if song.can_redo:
                song.redo()
                self.log("Redo")

    def _decode_relative_value(self, value):
        """Decode relative CC value to delta."""
        # Hardware sends ONLY two values:
        # 0x7F (127) = clockwise
        # 0x00 (0) = counter-clockwise
        if value == 0x7F:
            return 1  # Clockwise
        elif value == 0x00:
            return -1  # Counter-clockwise
        else:
            # Should never happen, log error
            self.log(f"ERROR: Unexpected relative knob value: {value}")
            return 0

    # -------------------------------------------------------------------------
    # Listeners
    # -------------------------------------------------------------------------

    def _add_clip_slot_listeners(self):
        """Add listeners for all visible clip slots."""
        song = self.song()
        tracks = song.visible_tracks

        for row in range(TRACK_CTRL_ROWS):
            scene_idx = self._session_scene_offset + row

            for col in range(TRACK_CTRL_COLS):
                track_idx = self._session_track_offset + col

                if track_idx < len(tracks) and scene_idx < len(song.scenes):
                    track = tracks[track_idx]
                    clip_slot = track.clip_slots[scene_idx]
                    listener = self._make_clip_listener(clip_slot, track)
                    clip_slot.add_has_clip_listener(listener)
                    self._clip_slot_listeners.append((clip_slot, 'has_clip', listener))

                    if clip_slot.has_clip:
                        playing_listener = self._make_clip_listener(clip_slot, track)
                        clip_slot.clip.add_playing_status_listener(playing_listener)
                        self._clip_slot_listeners.append((clip_slot, 'playing', playing_listener))

    def _remove_clip_slot_listeners(self):
        """Remove all clip slot listeners."""
        for clip_slot, listener_type, listener in self._clip_slot_listeners:
            try:
                if listener_type == 'has_clip':
                    clip_slot.remove_has_clip_listener(listener)
                elif listener_type == 'playing' and clip_slot.has_clip:
                    clip_slot.clip.remove_playing_status_listener(listener)
            except:
                pass
        self._clip_slot_listeners = []

    def _make_clip_listener(self, clip_slot, track):
        """Create a clip listener callback."""
        def listener():
            self.update()
        return listener

    def _add_track_list_listener(self):
        """Add listener for track list changes (add/remove tracks)."""
        song = self.song()
        song.add_visible_tracks_listener(self._on_tracks_changed)

    def _remove_track_list_listener(self):
        """Remove track list listener."""
        try:
            song = self.song()
            song.remove_visible_tracks_listener(self._on_tracks_changed)
        except:
            pass

    def _on_tracks_changed(self):
        """Called when tracks are added or removed."""
        self.log("Tracks changed, updating display...")
        # Re-add listeners for new track layout
        self._remove_clip_slot_listeners()
        self._add_clip_slot_listeners()
        # Update colors
        self.update()
