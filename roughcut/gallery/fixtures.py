"""Made-up recordings for stories. Each call returns a fresh copy."""

import random

from roughcut.model.recording import Marker, Recording, Window


def at(hours, minutes, seconds):
    return ((hours * 60 + minutes) * 60 + seconds) * 1000


def empty_recording():
    return Recording(name="raid_night_0412", duration_ms=at(1, 22, 10))


def raid_night():
    """Six markers: one unnamed, two close enough that their windows merge."""
    return Recording(name="raid_night_0412", duration_ms=at(1, 22, 10), markers=[
        Marker(1, at(0, 3, 12), "Breach", "Red", "Door charge on the east wall"),
        Marker(2, at(0, 11, 40), "Ambush", "Yellow"),
        Marker(3, at(0, 11, 50), "Push", "Yellow"),
        Marker(4, at(0, 27, 5), "", "Blue"),
        Marker(5, at(0, 41, 58), "Funny", "Pink", "Teammate falls off the ladder"),
        Marker(6, at(1, 19, 30), "Extract", "Green"),
    ])


def raid_night_hand_set():
    """raid_night with one window set by hand, so it ignores the handle settings."""
    recording = raid_night()
    recording.marker(5).window = Window(at(0, 41, 30), at(0, 42, 40))
    return recording


def many_markers():
    rng = random.Random(412)
    names = ["Breach", "Ambush", "Flank", "Clutch", "Funny", "Wipe", "", "Snipe", "Extract", ""]
    colors = ["Red", "Yellow", "Green", "Blue", "Pink", "Purple", "Cyan"]
    duration = at(2, 5, 0)
    times = sorted(rng.sample(range(10_000, duration - 10_000, 1000), 44))
    return Recording(name="milsim_op_weekend", duration_ms=duration, markers=[
        Marker(i + 1, t, rng.choice(names), rng.choice(colors)) for i, t in enumerate(times)
    ])


def edge_markers():
    """Markers 5 seconds from each end, so their windows clamp."""
    duration = at(0, 30, 0)
    return Recording(name="short_session", duration_ms=duration, markers=[
        Marker(1, at(0, 0, 5), "Spawn", "Green"),
        Marker(2, at(0, 14, 0), "Mid", "Blue"),
        Marker(3, duration - 5_000, "Last kill", "Red"),
    ])


ALL = {
    "empty": empty_recording,
    "raid_night": raid_night,
    "raid_night_hand_set": raid_night_hand_set,
    "many_markers": many_markers,
    "edge_markers": edge_markers,
}
