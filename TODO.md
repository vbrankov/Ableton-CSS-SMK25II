# TODO List

## Known Issues

- [ ] Blue hand not visible in Ableton when controlling device parameters
  - Currently we set `song.appointed_device` but the blue hand doesn't appear in the UI
  - May require using Ableton's `DeviceComponent` from `_Framework` instead of manual parameter control
  - Functionally everything works (parameters are controlled correctly), but the visual indicator is missing

- [ ] Adding a new device doesn't automatically appoint it (pad stays dim instead of turning blue)
  - When you add a device to a track, it appears as dim (available) but not blue (selected for control)
  - This is Ableton's default behavior - devices are only appointed when explicitly selected
  - Would be nice if newly added devices were automatically appointed for immediate control
