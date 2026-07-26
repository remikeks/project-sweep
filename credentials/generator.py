"""
Renders badge and certificate artwork as PNG (for on-screen viewing/sharing)
and PDF (for printing), using Pillow only, so the platform has no
dependency on a browser or headless renderer being available.

Visual language (kept consistent across the whole platform):
  paper        #EEF0F5  soft cool-linen background
  ink          #16202E  near-black text
  primary      #0B2C7A  navy blue (SWEEP brand)
  primary_dark #071D52
  gold         #F5A400  achievement gold (badges/seals)
  clay         #F2650A  warm orange accent
  line         #D9DEE8  hairline rule
"""

import io
import textwrap
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Bundled badge artwork (ships with the app, unlike user-uploaded media, so
# it is always present on disk regardless of the deployment target).
BADGE_TEMPLATE_PATH = Path(__file__).resolve().parent / "assets" / "badge_template.png"

PAPER = (238, 240, 245)
INK = (22, 32, 46)
PRIMARY = (11, 44, 122)
PRIMARY_DARK = (7, 29, 82)
GOLD = (245, 164, 0)
CLAY = (242, 101, 10)
LINE = (217, 222, 232)
WHITE = (255, 255, 255)

_FONT_CANDIDATES_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
_FONT_CANDIDATES_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]


def _load_font(size, bold=False):
    candidates = _FONT_CANDIDATES_BOLD if bold else _FONT_CANDIDATES_REGULAR
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _centered_text(draw, cx, y, text, font, fill, letter_spacing=0):
    if letter_spacing:
        text = ("\u200a" * 0).join(text)  # no-op placeholder for readability
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((cx - w / 2, y), text, font=font, fill=fill)
    return w


def _wrapped_centered_text(draw, cx, y, text, font, fill, max_chars, line_height):
    lines = textwrap.wrap(text, width=max_chars) or [text]
    for i, line in enumerate(lines):
        _centered_text(draw, cx, y + i * line_height, line, font, fill)
    return y + len(lines) * line_height


@lru_cache(maxsize=1)
def _load_badge_template() -> Image.Image:
    """Load the bundled badge artwork once per process; callers get a copy."""
    return Image.open(BADGE_TEMPLATE_PATH).convert("RGB")


def _best_fit_lines(draw, text, max_width, max_height, bold=True, start_size=92, min_size=30, max_lines=2):
    """
    Pick the largest font size (down to min_size) at which `text` wraps into
    at most `max_lines` lines that all fit within max_width, with the whole
    block fitting within max_height. Returns (font, lines, line_height).
    """
    for size in range(start_size, min_size - 1, -4):
        font = _load_font(size, bold=bold)
        avg_char_w = draw.textlength("MCOMPLETEDW", font=font) / 11
        chars_per_line = max(4, int(max_width / avg_char_w))
        lines = textwrap.wrap(text, width=chars_per_line) or [text]

        while any(draw.textlength(line, font=font) > max_width for line in lines) and chars_per_line > 4:
            chars_per_line -= 1
            lines = textwrap.wrap(text, width=chars_per_line) or [text]

        line_height = int(size * 1.25)
        block_height = line_height * len(lines)
        fits_width = all(draw.textlength(line, font=font) <= max_width for line in lines)
        if len(lines) <= max_lines and block_height <= max_height and fits_width:
            return font, lines, line_height

    font = _load_font(min_size, bold=bold)
    lines = textwrap.wrap(text, width=max(4, int(max_width / (draw.textlength("M", font=font) or 1)))) or [text]
    return font, lines[:max_lines], int(min_size * 1.25)


def _user_display_name(user):
    full_name = user.get_full_name() if hasattr(user, "get_full_name") else ""
    return full_name.strip() or user.get_username()


def _image_to_png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def _image_to_pdf_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PDF")
    return buf.getvalue()


# --------------------------------------------------------------------------
# Badge (per-course completion badge)
# --------------------------------------------------------------------------

def render_badge_image(user, course) -> Image.Image:
    """
    Badge artwork = the bundled SWEEP Academy badge template with the
    generic "COURSE COMPLETED" line replaced by the specific course that
    was just completed, e.g. "SAFEGUARDING BASICS COMPLETED". Everything
    else in the template (seal, ribbon, laurels, wordmark) is untouched.
    """
    img = _load_badge_template().copy()
    w, h = img.size
    draw = ImageDraw.Draw(img)
    cx = w // 2

    # Patch box: covers the two-line "COURSE" / "COMPLETED" placeholder
    # text. Measured directly against the template (pixel-sampled, not
    # guessed) to stay clear of the laurels, which intrude much further
    # toward center than they visually appear — a naive percentage-based
    # box here will clip the wreath artwork.
    box_left, box_right = int(w * 0.24), int(w * 0.76)
    box_top, box_bottom = int(h * 0.403), int(h * 0.561)
    template_bg = img.getpixel((cx, box_top + 4))  # sample the cream backdrop from inside the box
    draw.rectangle((box_left, box_top, box_right, box_bottom), fill=template_bg)

    headline = f"{course.title} Completed".upper()
    max_width = box_right - box_left
    max_height = box_bottom - box_top
    font, lines, line_height = _best_fit_lines(draw, headline, max_width, max_height)

    block_height = line_height * len(lines)
    y = box_top + (max_height - block_height) // 2
    for line in lines:
        _centered_text(draw, cx, y, line, font, PRIMARY_DARK)
        y += line_height

    return img


# --------------------------------------------------------------------------
# Certificate (per-school certification)
# --------------------------------------------------------------------------

def render_certificate_image(user, school, score=None) -> Image.Image:
    w, h = 1650, 1275  # landscape, ~US letter at 150dpi
    img = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(img)

    margin = 60
    draw.rectangle((margin, margin, w - margin, h - margin), outline=PRIMARY, width=6)
    draw.rectangle((margin + 18, margin + 18, w - margin - 18, h - margin - 18), outline=GOLD, width=3)

    cx = w // 2

    eyebrow_font = _load_font(28, bold=True)
    _centered_text(draw, cx, margin + 70, "SOCIAL WORK E-LEARNING AND EMPOWERMENT PLATFORM",
                    eyebrow_font, PRIMARY)

    heading_font = _load_font(72, bold=True)
    _centered_text(draw, cx, margin + 130, "Certificate of Completion", heading_font, INK)

    draw.line((cx - 260, margin + 230, cx + 260, margin + 230), fill=GOLD, width=4)

    body_font = _load_font(30)
    _centered_text(draw, cx, margin + 270, "This certifies that", body_font, INK)

    name_font = _load_font(58, bold=True)
    _centered_text(draw, cx, margin + 320, _user_display_name(user), name_font, PRIMARY_DARK)
    name_bbox = draw.textbbox((0, 0), _user_display_name(user), font=name_font)
    name_w = name_bbox[2] - name_bbox[0]
    draw.line((cx - name_w / 2 - 10, margin + 400, cx + name_w / 2 + 10, margin + 400), fill=GOLD, width=3)

    body2_font = _load_font(30)
    _centered_text(
        draw, cx, margin + 425,
        "has successfully completed every course and passed the certification",
        body2_font, INK,
    )
    _centered_text(draw, cx, margin + 465, "examination for the", body2_font, INK)

    school_font = _load_font(46, bold=True)
    _centered_text(draw, cx, margin + 515, school.name, school_font, PRIMARY)

    # Seal (mini badge)
    seal_cx, seal_cy = cx, margin + 660
    draw.ellipse((seal_cx - 90, seal_cy - 90, seal_cx + 90, seal_cy + 90), fill=GOLD)
    draw.ellipse((seal_cx - 75, seal_cy - 75, seal_cx + 75, seal_cy + 75), fill=PRIMARY_DARK)
    seal_font = _load_font(22, bold=True)
    _centered_text(draw, seal_cx, seal_cy - 14, "SWEEP", seal_font, PAPER)
    _centered_text(draw, seal_cx, seal_cy + 14, "CERTIFIED", seal_font, PAPER)

    # Footer: date + score + signature line
    footer_font = _load_font(24)
    date_str = datetime.now().strftime("%B %d, %Y")
    score_str = f"Exam score: {score}%" if score is not None else ""

    draw.line((margin + 100, h - margin - 140, margin + 500, h - margin - 140), fill=LINE, width=2)
    draw.text((margin + 100, h - margin - 130), "Date awarded", font=footer_font, fill=PRIMARY_DARK)
    draw.text((margin + 100, h - margin - 95), date_str, font=footer_font, fill=INK)

    draw.line((w - margin - 500, h - margin - 140, w - margin - 100, h - margin - 140), fill=LINE, width=2)
    draw.text((w - margin - 500, h - margin - 130), "Program Director, SWEEP", font=footer_font, fill=PRIMARY_DARK)
    if score_str:
        draw.text((w - margin - 500, h - margin - 95), score_str, font=footer_font, fill=INK)

    return img


# --------------------------------------------------------------------------
# Public helpers used by learning/services.py
# --------------------------------------------------------------------------

def generate_badge_files(user, course):
    """Return (png_bytes, pdf_bytes) for a course-completion badge."""
    image = render_badge_image(user, course)
    return _image_to_png_bytes(image), _image_to_pdf_bytes(image)


def generate_certificate_files(user, school, score=None):
    """Return (png_bytes, pdf_bytes) for a school certificate."""
    image = render_certificate_image(user, school, score=score)
    return _image_to_png_bytes(image), _image_to_pdf_bytes(image)


# --------------------------------------------------------------------------
# Single-format helpers used by the on-demand serving views (credentials/views.py).
# Rendering is deterministic from (user, course/school) and cheap (<100ms),
# so these are generated fresh on every request rather than depending on a
# file that was previously saved to disk. See credentials/views.py for why.
# --------------------------------------------------------------------------

def render_badge_png_bytes(user, course) -> bytes:
    return _image_to_png_bytes(render_badge_image(user, course))


def render_badge_pdf_bytes(user, course) -> bytes:
    return _image_to_pdf_bytes(render_badge_image(user, course))


def render_certificate_png_bytes(user, school, score=None) -> bytes:
    return _image_to_png_bytes(render_certificate_image(user, school, score=score))


def render_certificate_pdf_bytes(user, school, score=None) -> bytes:
    return _image_to_pdf_bytes(render_certificate_image(user, school, score=score))
