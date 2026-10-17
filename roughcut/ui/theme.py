"""Color tokens for light and dark, and the marker color set.

Values are plain hex strings so they can be checked without Qt; `color()`
turns a token into a QColor for whichever theme QFluentWidgets is showing.
"""

# token -> (light, dark)
TOKENS = {
    "surface": ("#F9F9F9", "#272727"),
    "surface_alt": ("#F0F0F0", "#202020"),
    "border": ("#D6D6D6", "#3A3A3A"),
    "text": ("#1B1B1B", "#F2F2F2"),
    "text_muted": ("#5F5F5F", "#A8A8A8"),
    "track": ("#E4E4E4", "#333333"),
    "track_tick": ("#B8B8B8", "#555555"),
    "clip_fill": ("#3FA97C", "#3DBB8A"),
    "clip_edge": ("#1F7A55", "#7FE0B8"),
    "visible_range": ("#0067C0", "#4CC2FF"),
    "playhead": ("#C42B1C", "#FF6B5B"),
    "viewer": ("#1A1A1A", "#0E0E0E"),
    "viewer_text": ("#9A9A9A", "#7A7A7A"),
    "error": ("#C42B1C", "#FF99A4"),
    "error_fill": ("#FDE7E9", "#442726"),
}

# The marker colors DaVinci Resolve offers, in its order; shades tuned per theme.
MARKER_COLORS = {
    "Blue": ("#2F6FE4", "#5A93FF"),
    "Cyan": ("#0095B6", "#2CC6E6"),
    "Green": ("#2E9447", "#4CC764"),
    "Yellow": ("#B88E00", "#F2CC2E"),
    "Red": ("#D13438", "#F05454"),
    "Pink": ("#D24A8C", "#F27BB4"),
    "Purple": ("#7E45C9", "#A877F0"),
    "Fuchsia": ("#B23AB8", "#DD62E2"),
    "Rose": ("#BC4E62", "#E2808F"),
    "Lavender": ("#6F69C9", "#ACA8F0"),
    "Sky": ("#3A8FCF", "#7DBEF0"),
    "Mint": ("#269C82", "#66D4BA"),
    "Lemon": ("#9AA21F", "#DCE35C"),
    "Sand": ("#9E8150", "#D8BC8C"),
    "Cocoa": ("#7A4E33", "#B07D5C"),
    "Cream": ("#A8996C", "#EFE3BE"),
}


def _pick(pair):
    from qfluentwidgets import isDarkTheme

    return pair[1] if isDarkTheme() else pair[0]


def color(token):
    from PySide6.QtGui import QColor

    return QColor(_pick(TOKENS[token]))


def marker_color(name):
    from PySide6.QtGui import QColor

    return QColor(_pick(MARKER_COLORS.get(name, MARKER_COLORS["Blue"])))


def format_time(ms):
    """01:22:10 style, the way the timeline and lists show times."""
    seconds = max(0, ms) // 1000
    return f"{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}"


def format_length(ms):
    """2:45 or 1:02:45, for totals."""
    seconds = max(0, ms) // 1000
    hours, minutes, secs = seconds // 3600, seconds // 60 % 60, seconds % 60
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"
