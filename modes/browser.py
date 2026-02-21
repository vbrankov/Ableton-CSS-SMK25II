"""Browser mode (Mode 5) - Navigate browser and manage devices."""

import os
import json
import time
from .base import ModeBase
from ..Hardware import PAD_TYPE_NOTE

# Mode configuration
BROWSER_PAD_CHANNEL = 9  # Channel 6
BROWSER_PAD_BASE_NOTE = 36  # C1
BROWSER_KNOB_CHANNEL = 5  # Channel 6
BROWSER_KNOB_BASE_CC = 20  # CC 20-27

# Pad hold timeout for memorization (1 second)
MEMORIZE_HOLD_TIME = 1.0


class BrowserMode(ModeBase):
    """Browser mode - navigate browser and manage devices."""

    def __init__(self, controller, hardware, mode_number):
        super(BrowserMode, self).__init__(controller, hardware, mode_number)
        self._pressed_pads = set()  # Currently pressed pad indices
        self._pad_press_times = {}  # Pad index -> press timestamp
        self._memorized_items = {}  # Pad combination -> browser item path or URI
        self._current_device_index = 0  # Selected device on track
        self._config_file = None  # Path to config file

        # Browser state
        self._browser_items = []  # Current list of items at this level
        self._browser_index = 0  # Current index in items list
        self._browser_stack = []  # Stack of (items, index) for going back

    def configure(self):
        """Configure hardware for browser mode."""
        self.log("Configuring browser mode...")

        # Clear hardware cache
        self._hw.clear_cache()

        # Configure all 16 pads as MCP (don't trigger notes)
        for i in range(16):
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=BROWSER_PAD_CHANNEL,
                note=BROWSER_PAD_BASE_NOTE + i,
                shifted=False
            )

        # Set all LEDs to dim white (or off)
        for i in range(16):
            self._hw.set_pad_led_state(i, 128, shifted=False)
            self._hw.set_pad_color(i, 0x202020, shifted=False)  # Dim white

        # Configure knobs as relative (CW type)
        for i in range(8):
            self._hw.configure_knob(
                knob_index=i,
                channel=BROWSER_KNOB_CHANNEL,
                cc=BROWSER_KNOB_BASE_CC + i,
                shifted=False
            )

        # Load configuration
        self._load_config()

        # Initialize browser
        self._init_browser()

        self.log("Browser mode configured.")

    def update(self):
        """Update mode state (not much visual feedback needed)."""
        pass

    def handle_pad(self, pad_index, velocity):
        """Handle pad press/release for combination memorization."""
        if velocity > 0:
            # Pad pressed
            self._pressed_pads.add(pad_index)
            self._pad_press_times[pad_index] = time.time()
        else:
            # Pad released
            if pad_index in self._pressed_pads:
                self._pressed_pads.remove(pad_index)

                # Check if this was a quick tap (not a hold)
                press_time = self._pad_press_times.get(pad_index, 0)
                hold_duration = time.time() - press_time

                if hold_duration < MEMORIZE_HOLD_TIME:
                    # Quick tap - trigger add
                    self._handle_pad_tap()
                # If hold >= 1s, memorization happens in handle_knob or we need a timer
                # For now, let's check on knob turns if any pads have been held for 1s

    def handle_knob(self, knob_index, value):
        """Handle knob turn in browser mode."""
        delta = self._decode_relative_value(value)
        if delta == 0:
            return

        # Check if any pads have been held for >= 1 second (memorization)
        self._check_memorization()

        # Knob 0: Navigate tracks
        if knob_index == 0:
            self._navigate_tracks(delta)

        # Knob 1: Add track (right) / Delete track (left)
        elif knob_index == 1:
            if delta > 0:
                self._add_track()
            else:
                self._delete_track()

        # Knob 2: Navigate browser hierarchy (left/right)
        elif knob_index == 2:
            self._navigate_browser_hierarchy(delta)

        # Knob 3: Scroll browser items (one by one)
        elif knob_index == 3:
            self._scroll_browser_items(delta)

        # Knob 4: Navigate devices on track
        elif knob_index == 4:
            self._navigate_devices(delta)

        # Knob 5: Reorder devices
        elif knob_index == 5:
            self._reorder_devices(delta)

        # Knob 6: Delete device
        elif knob_index == 6:
            self._delete_device()

        # Knob 7: Undo/Redo
        elif knob_index == 7:
            song = self.song()
            if delta > 0 and song.can_redo:
                song.redo()
                self.log("Redo")
            elif delta < 0 and song.can_undo:
                song.undo()
                self.log("Undo")

    def _handle_pad_tap(self):
        """Handle quick tap - add item based on current combination."""
        combination = self._get_current_combination()

        if combination in self._memorized_items:
            # Load memorized item
            item_path = self._memorized_items[combination]
            self._load_browser_item(item_path)
            self.log(f"Loading memorized item: {item_path}")
        elif combination == "":
            # No pads pressed - this shouldn't happen in tap handler
            pass
        else:
            # No memorized item for this combination
            self.log(f"No item memorized for combination: {combination}")

    def _check_memorization(self):
        """Check if any pads have been held >= 1 second for memorization."""
        if not self._pressed_pads:
            return

        current_time = time.time()
        # Check if all currently pressed pads have been held >= 1 second
        all_held_long_enough = all(
            current_time - self._pad_press_times.get(pad, current_time) >= MEMORIZE_HOLD_TIME
            for pad in self._pressed_pads
        )

        if all_held_long_enough:
            # Memorize current browser item to this combination
            combination = self._get_current_combination()
            item_path = self._get_current_browser_item_path()

            if item_path:
                self._memorized_items[combination] = item_path
                self._save_config()
                self.log(f"✓ MEMORIZED '{item_path}' to pads: {combination}")
            else:
                self.log(f"No item selected to memorize")

    def _get_current_combination(self):
        """Get current pad combination as sorted comma-separated string."""
        if not self._pressed_pads:
            return ""
        return ",".join(str(i) for i in sorted(self._pressed_pads))

    def _navigate_tracks(self, delta):
        """Navigate tracks left/right."""
        song = self.song()
        tracks = list(song.tracks)

        try:
            current_index = tracks.index(song.view.selected_track)
        except (ValueError, AttributeError):
            current_index = 0

        new_index = current_index + delta
        new_index = max(0, min(len(tracks) - 1, new_index))

        if new_index < len(tracks):
            song.view.selected_track = tracks[new_index]
            self._current_device_index = 0
            self.log(f"Selected track: {tracks[new_index].name}")

    def _add_track(self):
        """Add a new MIDI track."""
        song = self.song()
        try:
            current_index = list(song.tracks).index(song.view.selected_track)
            song.create_midi_track(current_index + 1)
            self.log("Added MIDI track")
        except:
            song.create_midi_track(-1)
            self.log("Added MIDI track at end")

    def _delete_track(self):
        """Delete current track."""
        song = self.song()
        try:
            track = song.view.selected_track
            track_name = track.name
            song.delete_track(track)
            self.log(f"Deleted track: {track_name}")
        except Exception as e:
            self.log(f"Cannot delete track: {e}")

    def _init_browser(self):
        """Initialize browser at true top level with all categories."""
        try:
            app = self.application()

            if not hasattr(app, 'browser'):
                self.log("Browser not available in this Live version")
                self._browser_items = []
                return

            browser = app.browser

            # Build top-level list with all browser categories
            self._browser_items = []
            categories = [
                ('sounds', 'Sounds'),
                ('drums', 'Drums'),
                ('instruments', 'Instruments'),
                ('audio_effects', 'Audio Effects'),
                ('midi_effects', 'MIDI Effects'),
                ('plugins', 'Plugins'),
                ('clips', 'Clips'),
                ('samples', 'Samples'),
            ]

            for attr_name, display_name in categories:
                if hasattr(browser, attr_name):
                    category_item = getattr(browser, attr_name)
                    if category_item:
                        self._browser_items.append(category_item)
                        self.log(f"Found category: {display_name}")

            self._browser_index = 0
            self._browser_stack = []

            self.log(f"Browser initialized with {len(self._browser_items)} categories")
        except Exception as e:
            self.log(f"ERROR initializing browser: {e}")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}")
            self._browser_items = []

    def _navigate_browser_hierarchy(self, delta):
        """Navigate browser hierarchy (into/out of folders)."""
        try:
            if delta > 0:
                # Enter folder (go deeper)
                self._enter_current_folder()
            else:
                # Exit folder (go back)
                self._exit_folder()
        except Exception as e:
            self.log(f"ERROR navigating hierarchy: {e}")

    def _enter_current_folder(self):
        """Enter the currently selected folder."""
        if not self._browser_items or self._browser_index >= len(self._browser_items):
            self.log("No item selected to enter")
            return

        current_item = self._browser_items[self._browser_index]

        # Try to enter if item has children (folder or category)
        if hasattr(current_item, 'children'):
            try:
                children = list(current_item.children)
                if children:
                    # Save current state
                    self._browser_stack.append((self._browser_items, self._browser_index))

                    # Enter folder/category
                    self._browser_items = children
                    self._browser_index = 0
                    self.log(f"Entered: {current_item.name if hasattr(current_item, 'name') else 'Unknown'} ({len(self._browser_items)} items)")

                    # Send updated browser levels
                    self._send_browser_levels()
                else:
                    self.log("Item has no children")
            except Exception as e:
                self.log(f"Cannot enter item: {e}")
        else:
            self.log("Current item cannot be entered (no children)")

    def _exit_folder(self):
        """Exit current folder and go back to parent."""
        if not self._browser_stack:
            self.log("Already at root level")
            return

        # Restore previous state
        self._browser_items, self._browser_index = self._browser_stack.pop()
        self.log(f"Exited to parent folder ({len(self._browser_items)} items)")

        # Send updated browser levels
        self._send_browser_levels()

    def _scroll_browser_items(self, delta):
        """Scroll browser items at current level."""
        if not self._browser_items:
            self.log("No browser items to scroll")
            return

        # Update index
        self._browser_index += delta
        self._browser_index = max(0, min(len(self._browser_items) - 1, self._browser_index))

        # Log and preview current item
        if self._browser_index < len(self._browser_items):
            item = self._browser_items[self._browser_index]
            item_name = item.name if hasattr(item, 'name') else "Unknown"
            is_folder = " [folder]" if (hasattr(item, 'is_folder') and item.is_folder) else ""
            item_type = "folder" if (hasattr(item, 'is_folder') and item.is_folder) else "item"

            self.log(f"Browser: {item_name}{is_folder} ({self._browser_index + 1}/{len(self._browser_items)})")

            # Try to preview item in Ableton browser
            self._preview_item(item)

    def _get_current_browser_item_path(self):
        """Get path/URI of currently selected browser item (from Ableton's selection or our internal state)."""
        try:
            app = self.application()
            browser = app.browser

            # Try to get Ableton's current browser selection first
            selected_item = None
            if hasattr(browser, 'hotswap_target'):
                selected_item = browser.hotswap_target

            # Check for other selection properties
            if not selected_item and hasattr(browser, 'selected_item'):
                selected_item = browser.selected_item

            if not selected_item and hasattr(browser, 'preview_item'):
                # preview_item might be the currently previewed item
                pass

            # If we found a selected item in Ableton, use it
            if selected_item:
                if hasattr(selected_item, 'uri'):
                    self.log(f"Using Ableton selection: {selected_item.name if hasattr(selected_item, 'name') else 'Unknown'}")
                    return selected_item.uri
                elif hasattr(selected_item, 'name'):
                    return selected_item.name

        except Exception as e:
            pass  # Silently ignore browser access errors

        # Fall back to our internal navigation
        if not self._browser_items or self._browser_index >= len(self._browser_items):
            return ""

        item = self._browser_items[self._browser_index]

        # Try to get URI (unique identifier for the item)
        if hasattr(item, 'uri'):
            return item.uri
        elif hasattr(item, 'name'):
            # Fallback: build path from stack
            path_parts = []
            for items, idx in self._browser_stack:
                if idx < len(items) and hasattr(items[idx], 'name'):
                    path_parts.append(items[idx].name)
            path_parts.append(item.name)
            return "/".join(path_parts)
        else:
            return ""

    def _load_browser_item(self, item_path):
        """Load a browser item by path/URI."""
        try:
            app = self.application()
            browser = app.browser
            song = self.song()
            track = song.view.selected_track

            # Try to find item by URI or path
            item = self._find_browser_item_by_path(item_path)

            if item:
                # Load item onto current track
                if hasattr(item, 'is_loadable') and item.is_loadable:
                    browser.load_item(track)
                    self.log(f"Loaded: {item.name if hasattr(item, 'name') else item_path}")
                else:
                    self.log(f"Item not loadable: {item_path}")
            else:
                self.log(f"Item not found: {item_path}")

        except Exception as e:
            self.log(f"ERROR loading item: {e}")

    def _preview_item(self, item):
        """Preview/select an item in the Ableton browser."""
        try:
            app = self.application()
            browser = app.browser

            # Try to preview the item
            if hasattr(browser, 'preview_item'):
                browser.preview_item(item)

            # Try to show browser view
            if hasattr(app.view, 'show_view'):
                app.view.show_view("Browser")

        except Exception as e:
            # Preview might not be available or item might not be previewable
            pass

    def _find_browser_item_by_path(self, path):
        """Find a browser item by path or URI."""
        try:
            app = self.application()
            browser = app.browser

            # If path is a URI, try to load directly
            if hasattr(browser, 'load_item'):
                # Search through browser items
                # This is a simplified search - in practice, would need recursive search
                for item in self._browser_items:
                    if hasattr(item, 'uri') and item.uri == path:
                        return item
                    if hasattr(item, 'name') and item.name in path:
                        return item

            return None
        except Exception as e:
            self.log(f"ERROR finding item: {e}")
            return None

    def _navigate_devices(self, delta):
        """Navigate devices on current track."""
        song = self.song()
        track = song.view.selected_track
        devices = list(track.devices) if hasattr(track, 'devices') else []

        if not devices:
            return

        self._current_device_index = (self._current_device_index + delta) % len(devices)
        song.view.select_device(devices[self._current_device_index])
        self.log(f"Selected device: {devices[self._current_device_index].name}")

    def _reorder_devices(self, delta):
        """Reorder selected device (move left/right)."""
        song = self.song()
        track = song.view.selected_track
        devices = list(track.devices) if hasattr(track, 'devices') else []

        if not devices or self._current_device_index >= len(devices):
            return

        new_index = self._current_device_index + delta
        new_index = max(0, min(len(devices) - 1, new_index))

        if new_index != self._current_device_index:
            try:
                # Move device (one position at a time)
                device_to_move = devices[self._current_device_index]
                self._current_device_index = new_index
                self.log(f"Device reorder: Moving {device_to_move.name} to position {new_index + 1}")
                # Note: Full implementation would use track method to actually move the device
                # For now, just update index - actual device moving would need API support
            except Exception as e:
                self.log(f"ERROR reordering device: {e}")

    def _delete_device(self):
        """Delete currently selected device."""
        song = self.song()
        track = song.view.selected_track
        devices = list(track.devices) if hasattr(track, 'devices') else []

        if not devices or self._current_device_index >= len(devices):
            self.log("No device to delete")
            return

        try:
            device = devices[self._current_device_index]
            device_name = device.name
            track.delete_device(self._current_device_index)
            self._current_device_index = max(0, min(self._current_device_index, len(devices) - 2))
            self.log(f"Deleted device: {device_name}")
        except Exception as e:
            self.log(f"ERROR deleting device: {e}")

    def _load_config(self):
        """Load memorized items from config file."""
        try:
            home = os.path.expanduser("~")
            config_dir = os.path.join(home, ".config", "SMK25II")

            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            self._config_file = os.path.join(config_dir, "browser_memory.json")

            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    data = json.load(f)
                    self._memorized_items = data.get('memorized_items', {})
                    self.log(f"Loaded config from {self._config_file}")
            else:
                self.log(f"No existing config, will create: {self._config_file}")

        except Exception as e:
            self.log(f"ERROR loading config: {e}")
            self._memorized_items = {}

    def _save_config(self):
        """Save memorized items to config file."""
        if not self._config_file:
            return

        try:
            data = {
                '_readme': 'SMK25II Browser Mode - Pad combinations mapped to instrument/device paths',
                'memorized_items': self._memorized_items
            }
            with open(self._config_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.log(f"Saved config to {self._config_file}")

        except Exception as e:
            self.log(f"ERROR saving config: {e}")

    def _decode_relative_value(self, value):
        """Decode relative CC value to delta."""
        if value == 0x7F:
            return 1  # Clockwise
        elif value == 0x00:
            return -1  # Counter-clockwise
        else:
            self.log(f"ERROR: Unexpected relative knob value: {value}")
            return 0

    def get_pad_colors(self):
        """Get current pad colors (16 RGB values in hardware format)."""
        colors = []
        active_level = min(len(self._browser_stack), 3)
        level_colors = [0x0000FF, 0x00FF00, 0xFF0000, 0xFFFF00]  # Blue, Green, Red, Yellow

        for i in range(16):
            if i < 4:
                # Level indicators
                if i == active_level:
                    colors.append(level_colors[i])  # Bright color for active level
                else:
                    colors.append(0x202020)  # Dim gray for inactive
            else:
                # Memorization pads - dim white
                colors.append(0x202020)

        return colors

    def get_status(self):
        """Get current browser status for web display."""
        # Calculate current levels (similar to _send_browser_levels but just return data)
        level1 = ""
        level2 = ""
        level3 = ""
        level4 = ""
        active_level = min(len(self._browser_stack), 3)

        if len(self._browser_stack) == 0:
            if self._browser_items and self._browser_index < len(self._browser_items):
                item = self._browser_items[self._browser_index]
                item_name = item.name if hasattr(item, 'name') else "Unknown"
                level1 = f"{item_name} ({self._browser_index + 1}/{len(self._browser_items)})"

        elif len(self._browser_stack) == 1:
            parent_items, parent_index = self._browser_stack[0]
            if parent_index < len(parent_items):
                item_name = parent_items[parent_index].name if hasattr(parent_items[parent_index], 'name') else "Unknown"
                level1 = f"{item_name} ({parent_index + 1}/{len(parent_items)})"

            if self._browser_items and self._browser_index < len(self._browser_items):
                item = self._browser_items[self._browser_index]
                item_name = item.name if hasattr(item, 'name') else "Unknown"
                level2 = f"{item_name} ({self._browser_index + 1}/{len(self._browser_items)})"

        else:
            if len(self._browser_stack) > 0:
                parent_items, parent_index = self._browser_stack[0]
                if parent_index < len(parent_items):
                    item_name = parent_items[parent_index].name if hasattr(parent_items[parent_index], 'name') else "Unknown"
                    level1 = f"{item_name} ({parent_index + 1}/{len(parent_items)})"

            if len(self._browser_stack) > 1:
                parent_items, parent_index = self._browser_stack[1]
                if parent_index < len(parent_items):
                    item_name = parent_items[parent_index].name if hasattr(parent_items[parent_index], 'name') else "Unknown"
                    level2 = f"{item_name} ({parent_index + 1}/{len(parent_items)})"

            if len(self._browser_stack) > 2:
                parent_items, parent_index = self._browser_stack[2]
                if parent_index < len(parent_items):
                    item_name = parent_items[parent_index].name if hasattr(parent_items[parent_index], 'name') else "Unknown"
                    level3 = f"{item_name} ({parent_index + 1}/{len(parent_items)})"

                if self._browser_items and self._browser_index < len(self._browser_items):
                    item = self._browser_items[self._browser_index]
                    item_name = item.name if hasattr(item, 'name') else "Unknown"
                    level4 = f"{item_name} ({self._browser_index + 1}/{len(self._browser_items)})"
            else:
                if self._browser_items and self._browser_index < len(self._browser_items):
                    item = self._browser_items[self._browser_index]
                    item_name = item.name if hasattr(item, 'name') else "Unknown"
                    level3 = f"{item_name} ({self._browser_index + 1}/{len(self._browser_items)})"

        return {
            'level1': level1,
            'level2': level2,
            'level3': level3,
            'level4': level4,
            'active_level': active_level
        }

    def disconnect(self):
        """Cleanup when leaving browser mode."""
        self.log("Disconnecting browser mode...")
        self._save_config()
