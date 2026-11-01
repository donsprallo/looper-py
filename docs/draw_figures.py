"""Draw the figures of the looper-py handbook as plain SVG files.

The figures are code so that a label can be changed without a drawing
program, and so that every figure shares one palette and one font with the
handbooks of looper-core and looper-rs. Each is drawn on a light card of its
own, which keeps it readable in Furo's dark scheme as well.

Run it from anywhere; it needs nothing beyond the standard library:

    python docs/draw_figures.py            # writes docs/images/*.svg
    python docs/draw_figures.py some/dir   # writes somewhere else

The numbers in the figures are the ones the blinky example of looper-core
really produces, so the pictures and the examples in the text agree.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "images"

SANS = "Segoe UI, Helvetica Neue, Helvetica, Arial, sans-serif"
MONO = "Consolas, Menlo, DejaVu Sans Mono, monospace"

# The light palette shared with the looper-rs handbook.
TEXT = "#1b1f2a"
MUTED = "#5f6879"
BORDER = "#d7dbe4"
SURFACE = "#ffffff"
RAISED = "#eef0f5"
ACCENT = "#2563eb"
GOOD = "#108b63"
WARN = "#b57d09"
BAD = "#c93b3b"
GRID = "#e3e6ee"
BLUE_SOFT = "#dbe7ff"
GREEN_SOFT = "#d6f2e6"
AMBER_SOFT = "#fdecc8"
RED_SOFT = "#f8dcdc"
VIOLET = "#7c5cd6"
VIOLET_SOFT = "#ebe4fb"


class Svg:
    """One figure: a list of SVG fragments on a rounded white card."""

    def __init__(self, width: int, height: int, title: str) -> None:
        self.width, self.height, self.parts = width, height, []
        self.title = title

    def add(self, fragment: str) -> None:
        self.parts.append(fragment)

    def rect(self, x, y, w, h, fill=SURFACE, stroke=None, rx=0, width=1, dash=None, opacity=None):
        extra = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        extra += f' stroke-dasharray="{dash}"' if dash else ""
        extra += f' fill-opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{extra}/>')

    def text(self, x, y, content, size=13, fill=TEXT, weight="normal", anchor="start", mono=False,
             italic=False):
        family = MONO if mono else SANS
        style = ' font-style="italic"' if italic else ""
        style += ' xml:space="preserve"' if mono else ""
        self.add(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{style}>{escape(content)}</text>'
        )

    def line(self, x1, y1, x2, y2, stroke=TEXT, width=1.5, dash=None, arrow=False):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        extra += ' marker-end="url(#arrow)"' if arrow else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
                 f'stroke-width="{width}"{extra}/>')

    def path(self, d, stroke=TEXT, width=1.5, fill="none", dash=None, arrow=False, opacity=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        extra += ' marker-end="url(#arrow)"' if arrow else ""
        extra += f' fill-opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<path d="{d}" stroke="{stroke}" stroke-width="{width}" fill="{fill}" '
                 f'stroke-linejoin="round" stroke-linecap="round"{extra}/>')

    def polyline(self, points, stroke=ACCENT, width=2):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
        self.path(d, stroke=stroke, width=width)

    def circle(self, x, y, r, fill=TEXT, stroke=None):
        extra = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ""
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"{extra}/>')

    def badge(self, x, y, number, fill=TEXT):
        self.circle(x, y, 12, fill=fill)
        self.text(x, y + 4.5, str(number), size=12, fill="#ffffff", weight="bold", anchor="middle")

    def save(self, name: str) -> None:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" role="img">\n'
            f"<title>{escape(self.title)}</title>\n"
            "<defs>"
            '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            'fill="context-stroke"/></marker>'
            "</defs>\n"
            f'<rect x="0.5" y="0.5" width="{self.width - 1}" height="{self.height - 1}" rx="12" '
            f'fill="{SURFACE}" stroke="{BORDER}"/>\n'
        )
        (OUT / name).write_text(head + "\n".join(self.parts) + "\n</svg>\n", encoding="utf-8")


def box(svg, x, y, w, h, title, subtitle, fill, stroke, inner=()):
    """A titled box with a few labelled rows inside, as the overviews draw a process."""
    svg.rect(x, y, w, h, fill=fill, stroke=stroke, rx=12, width=1.5)
    svg.text(x + w / 2, y + 28, title, size=16, weight="bold", anchor="middle")
    svg.text(x + w / 2, y + 47, subtitle, size=12, fill=MUTED, anchor="middle")
    for index, label in enumerate(inner):
        svg.rect(x + 22, y + 62 + index * 38, w - 44, 29, fill=SURFACE, stroke=stroke, rx=7)
        svg.text(x + w / 2, y + 81 + index * 38, label, size=12.5, anchor="middle", mono=True)


def two_way(svg, x1, x2, y, label, sublabel=""):
    """A request going right and its answer coming back, between two boxes."""
    svg.line(x1 + 6, y, x2 - 6, y, stroke=TEXT, arrow=True)
    svg.line(x2 - 6, y + 22, x1 + 6, y + 22, stroke=MUTED, arrow=True)
    svg.text((x1 + x2) / 2, y - 8, label, size=12, weight="bold", anchor="middle")
    if sublabel:
        svg.text((x1 + x2) / 2, y + 40, sublabel, size=11, fill=MUTED, anchor="middle")


# ---------------------------------------------------------------------------


def system_overview():
    svg = Svg(940, 400, "A test, looper-cli run and the simulation, with a window beside the test")
    box(svg, 30, 70, 250, 180, "your test", "pytest + looper (this library)", BLUE_SOFT, ACCENT,
        ["looper.run(...)", "simulation.expect()"])
    box(svg, 345, 70, 250, 180, "looper-cli run", "looper-core", GREEN_SOFT, GOOD,
        ["inspector server", "use cases"])
    box(svg, 660, 70, 250, 180, "simulation", "your firmware, built for the host", AMBER_SOFT, WARN,
        ["firmware + device model", "looper-rt"])
    two_way(svg, 280, 345, 140, "gRPC", "contract")
    two_way(svg, 595, 660, 140, "pipes", "stdin / stdout")
    svg.path("M155,70 C155,28 470,28 470,68", stroke=MUTED, dash="5 4", arrow=True)
    svg.text(312, 34, "starts it, and stops it when the test is done", size=12, fill=MUTED,
             anchor="middle")
    svg.path("M470,70 C470,28 785,28 785,68", stroke=MUTED, dash="5 4", arrow=True)
    svg.text(628, 34, "builds and starts it", size=12, fill=MUTED, anchor="middle")
    svg.rect(345, 300, 250, 64, fill=VIOLET_SOFT, stroke=VIOLET, rx=12, width=1.5)
    svg.text(470, 327, "looper-rs window", size=15, weight="bold", anchor="middle")
    svg.text(470, 346, "optional, looks at the same simulation", size=12, fill=MUTED,
             anchor="middle")
    svg.line(470, 298, 470, 256, stroke=VIOLET, arrow=True, dash="4 3")
    svg.text(482, 282, "gRPC", size=12, weight="bold", fill=VIOLET)
    svg.save("system-overview.svg")


def lockstep():
    svg = Svg(940, 380, "A held clock moves only for the span a test lets pass")
    left, right, top, bottom = 90, 900, 50, 280
    svg.line(left, bottom, right, bottom, stroke=MUTED)
    svg.line(left, bottom, left, top, stroke=MUTED)
    svg.text((left + right) / 2, bottom + 66, "wall clock: what the test is doing  ->", size=12,
             fill=MUTED, anchor="middle")
    svg.text(left - 14, top - 14, "simulated time (sim_us)", size=12, fill=MUTED)
    phases = [
        (90, 230, "held", "test sets the scene", 0.0),
        (230, 300, "runs", "advance(1.0)", 1.0),
        (300, 470, "held", "test reads, nothing moves", 0.0),
        (470, 560, "runs", "evaluate(for_seconds=1.5)", 1.5),
        (560, 760, "held", "clock + counts read together", 0.0),
        (760, 830, "runs", "advance(1.0)", 1.0),
        (830, 900, "held", "", 0.0),
    ]
    scale = 50
    level = 0.0
    points = [(left, bottom)]
    for start, end, kind, label, seconds in phases:
        y_start = bottom - level * scale
        level += seconds
        y_end = bottom - level * scale
        fill = GREEN_SOFT if kind == "runs" else RAISED
        svg.rect(start, top, end - start, bottom - top, fill=fill, opacity=0.6)
        points.append((end, y_end))
        if kind == "held":
            svg.line(start, y_start, end, y_end, stroke=ACCENT, width=3)
        else:
            svg.line(start, y_start, end, y_end, stroke=GOOD, width=3)
        if label:
            svg.text((start + end) / 2, bottom + 18 + (20 if kind == "runs" else 0), label,
                     size=11, fill=GOOD if kind == "runs" else MUTED, anchor="middle",
                     mono=kind == "runs")
    for seconds in (1.0, 2.5, 3.5):
        y = bottom - seconds * scale
        svg.line(left - 5, y, left, y, stroke=MUTED)
        svg.text(left - 9, y + 4, f"{seconds:g} s", size=11, fill=MUTED, anchor="end", mono=True)
    svg.rect(120, 66, 300, 52, fill=SURFACE, stroke=BORDER, rx=8)
    svg.line(134, 84, 160, 84, stroke=ACCENT, width=3)
    svg.text(168, 88, "held: the clock stands still", size=12)
    svg.line(134, 104, 160, 104, stroke=GOOD, width=3)
    svg.text(168, 108, "runs: exactly the time let pass", size=12)
    svg.save("lockstep.svg")


def evaluate_steps():
    svg = Svg(940, 270, "What evaluate does, step by step")
    steps = [
        ("declare", "check.channel(...)", "check.call(...)", BLUE_SOFT, ACCENT),
        ("clear", "recordings and counts", "for every client", AMBER_SOFT, WARN),
        ("let time pass", "run a held clock", "or wait if it runs alone", GREEN_SOFT, GOOD),
        ("observe", "clock + counts, then", "samples, exchanges, memory", VIOLET_SOFT, VIOLET),
        ("check", "every expectation", "-> ExpectationReport", BLUE_SOFT, ACCENT),
    ]
    width, gap, x = 160, 22, 30
    for index, (title, first, second, fill, stroke) in enumerate(steps):
        svg.rect(x, 70, width, 130, fill=fill, stroke=stroke, rx=12, width=1.5)
        svg.badge(x + width / 2, 70, index + 1, fill=stroke)
        svg.text(x + width / 2, 112, title, size=15, weight="bold", anchor="middle")
        svg.text(x + width / 2, 142, first, size=11.5, fill=MUTED, anchor="middle")
        svg.text(x + width / 2, 162, second, size=11.5, fill=MUTED, anchor="middle")
        if index < len(steps) - 1:
            svg.line(x + width + 3, 135, x + width + gap - 3, 135, stroke=TEXT, arrow=True)
        x += width + gap
    svg.text(30, 238, "Steps 2 to 5 are one call: report = check.evaluate(for_seconds=1.0). "
             "Twenty expectations cost one reading of each recording.", size=12, fill=MUTED)
    svg.save("evaluate-steps.svg")


def waveforms():
    svg = Svg(940, 330, "The waveforms a signal generator offers")
    shapes = [
        ("constant", lambda phase: 0.0),
        ("sine", lambda phase: math.sin(2 * math.pi * phase)),
        ("square", lambda phase: 1.0 if phase % 1.0 < 0.5 else -1.0),
        ("triangle", lambda phase: 1 - 4 * abs((phase % 1.0) - 0.5)),
        ("sawtooth", lambda phase: 2 * (phase % 1.0) - 1),
    ]
    panel, gap, x = 164, 13, 30
    for name, shape in shapes:
        top, height = 70, 150
        middle = top + height / 2 + 15
        svg.rect(x, top, panel, height + 30, fill=RAISED, rx=10)
        svg.text(x + panel / 2, top - 14, f'waveform="{name}"', size=12.5, anchor="middle",
                 mono=True)
        svg.line(x + 10, middle, x + panel - 10, middle, stroke=MUTED, dash="4 3", width=1)
        points = []
        for step in range(161):
            phase = step / 160 * 2
            y = middle - shape(phase) * 50 - (35 if name == "constant" else 0)
            points.append((x + 10 + step / 160 * (panel - 20), y))
        svg.polyline(points, stroke=ACCENT, width=2.2)
        x += panel + gap
    terms = [
        (30, 284, "offset", "the level it swings around; all of a constant"),
        (30, 308, "amplitude", "how far it swings either way"),
        (490, 284, "frequency_hz", "how often it repeats"),
        (490, 308, "phase_degrees", "where in its period it starts"),
    ]
    for x, y, term, meaning in terms:
        svg.text(x, y, term, size=12.5, weight="bold", mono=True)
        svg.text(x + 120, y, meaning, size=12.5, fill=MUTED)
    svg.save("waveforms.svg")


def channel_checks():
    svg = Svg(940, 340, "What reaches and stays_between look at")
    # Left: a first-order step response reaching its target.
    left, top, width, height = 60, 70, 380, 200
    svg.text(left, top - 22, "reaches(4.95, tolerance=0.05, within_seconds=0.5)", size=12.5,
             mono=True)
    target_y = top + 30
    svg.rect(left, target_y - 10, width, 20, fill=GREEN_SOFT)
    svg.text(left + width - 4, target_y - 14, "4.95 +/- 0.05", size=11, fill=GOOD, anchor="end")
    deadline = left + width * 0.5 / 0.8
    svg.line(deadline, top, deadline, top + height, stroke=WARN, dash="5 4")
    svg.text(deadline + 5, top + height - 6, "within 0.5 s", size=11, fill=WARN)
    points = []
    for step in range(121):
        seconds = step / 120 * 0.8
        value = 5.0 * (1 - math.exp(-seconds / 0.08))
        points.append((left + seconds / 0.8 * width, top + height - value / 5.0 * (height - 30)))
    svg.polyline(points, stroke=ACCENT, width=2.4)
    reached = 0.389
    rx = left + reached / 0.8 * width
    svg.circle(rx, target_y + 8, 5, fill=GOOD)
    svg.line(rx, target_y + 13, deadline + 8, target_y + 40, stroke=GOOD, width=1)
    svg.text(deadline + 12, target_y + 44, "first sample in the band:", size=11, fill=GOOD)
    svg.text(deadline + 12, target_y + 59, "reached after 0.389 s", size=11, fill=GOOD)
    svg.line(left, top + height, left + width, top + height, stroke=MUTED)
    svg.text(left, top + height + 18, "window starts", size=11, fill=MUTED)
    # Right: a sine that stays inside its bounds.
    left2 = 500
    svg.text(left2, top - 22, "stays_between(1.0, 3.0)", size=12.5, mono=True)
    high_y, low_y = top + 30, top + height - 30
    svg.rect(left2, high_y, width, low_y - high_y, fill=GREEN_SOFT, opacity=0.55)
    svg.line(left2, high_y, left2 + width, high_y, stroke=GOOD, dash="5 4")
    svg.line(left2, low_y, left2 + width, low_y, stroke=GOOD, dash="5 4")
    svg.text(left2 + width - 4, high_y - 6, "high 3.0", size=11, fill=GOOD, anchor="end")
    svg.text(left2 + width - 4, low_y + 16, "low 1.0", size=11, fill=GOOD, anchor="end")
    middle = (high_y + low_y) / 2
    points = [
        (left2 + step / 200 * width, middle - 0.3 * (low_y - high_y) * math.sin(step / 200 * 10 * math.pi))
        for step in range(201)
    ]
    svg.polyline(points, stroke=ACCENT, width=2.2)
    svg.text(left2, top + height + 18, "every sample of the window has to be inside", size=11,
             fill=MUTED)
    svg.save("channel-checks.svg")


def window_edges():
    svg = Svg(940, 260, "How many toggles a window catches depends on where it starts")
    left, right, axis = 60, 900, 120
    per_second = (right - left) / 4.2
    svg.line(left, axis, right, axis, stroke=MUTED)
    for tick in range(0, 5):
        x = left + tick * per_second
        svg.line(x, axis - 4, x, axis + 4, stroke=MUTED)
        svg.text(x, axis + 20, f"{tick} s", size=11, fill=MUTED, anchor="middle", mono=True)
    for half in range(1, 9):
        x = left + half * 0.5 * per_second
        svg.circle(x, axis, 6, fill=ACCENT)
    svg.text(left, 52, "the LED toggles every 500 ms (2 Hz)", size=12.5, weight="bold")
    windows = [(0.0, 2.0, 160, "window 0 .. 2 000 000 us (end excluded) catches 3 toggles: 1.5 Hz", WARN,
                AMBER_SOFT),
               (0.25, 2.25, 200, "window 250 000 .. 2 250 000 us catches 4 toggles: 2 Hz", GOOD,
                GREEN_SOFT)]
    for start, end, y, label, stroke, fill in windows:
        x1, x2 = left + start * per_second, left + end * per_second
        svg.rect(x1, y - 14, x2 - x1, 22, fill=fill, stroke=stroke, rx=6)
        svg.text(x2 + 10, y + 2, label, size=12, fill=stroke)
    svg.save("window-edges.svg")


def report_anatomy():
    svg = Svg(940, 300, "How a report reads")
    lines = [
        ("3 of 4 met", TEXT, "bold"),
        ("FAIL  FILTERED: expected 4.95 +/- 0.05 within 0.1 s, saw never closer than 7.3e-05", BAD,
         "normal"),
        ("ok    the firmware: expected still calling the adapter, saw 12004 calls", GOOD, "normal"),
        ("ok    the heap: expected no allocation at all, saw 0 allocations", GOOD, "normal"),
        ("ok    the stack: expected at most 16 frames, saw 4 frames at the deepest", GOOD,
         "normal"),
    ]
    svg.rect(60, 30, 850, 170, fill=RAISED, rx=10)
    for index, (content, fill, weight) in enumerate(lines):
        svg.text(80, 62 + index * 30, content, size=13, fill=fill, weight=weight, mono=True)
    markers = [(42, 58, 1), (42, 88, 2), (692, 84, 3)]
    for x, y, number in markers:
        svg.badge(x, y, number, fill=ACCENT)
    legend = [
        (60, 232, 1, "how many of the expectations were met"),
        (60, 258, 2, "failures come first, then what was met"),
        (500, 232, 3, "subject, what was expected, and what was seen"),
    ]
    for x, y, number, label in legend:
        svg.badge(x + 12, y - 4, number, fill=ACCENT)
        svg.text(x + 32, y, label, size=12.5, fill=TEXT)
    svg.text(500, 258, "assert report, report.summary", size=12.5, mono=True)
    svg.text(500, 278, "true when all were met; the summary is the message", size=12, fill=MUTED)
    svg.save("report-anatomy.svg")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    figures = [system_overview, lockstep, evaluate_steps, waveforms, channel_checks, window_edges,
               report_anatomy]
    for figure in figures:
        figure()
    print(f"wrote {len(figures)} figures to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
