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

from PIL import Image, ImageDraw, ImageFont

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
    size = 1000
    img = Image.new("RGB", (size, size), PAPER)
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, 430

    # Outer rings
    draw.ellipse((cx - 340, cy - 340, cx + 340, cy + 340), fill=PRIMARY)
    draw.ellipse((cx - 315, cy - 315, cx + 315, cy + 315), fill=GOLD)
    draw.ellipse((cx - 292, cy - 292, cx + 292, cy + 292), fill=PRIMARY_DARK)
    draw.ellipse((cx - 265, cy - 265, cx + 265, cy + 265), fill=PAPER)

    # Simple open-book emblem
    book_w, book_h = 190, 110
    bx, by = cx - book_w // 2, cy - 70
    draw.polygon(
        [(bx, by + 10), (cx, by - 15), (bx + book_w, by + 10),
         (bx + book_w, by + book_h), (cx, by + book_h - 25), (bx, by + book_h)],
        fill=PRIMARY,
    )
    draw.line((cx, by - 15, cx, by + book_h - 25), fill=PAPER, width=4)

    # "BADGE OF COMPLETION" arc-ish label
    label_font = _load_font(28, bold=True)
    _centered_text(draw, cx, cy + 60, "BADGE OF COMPLETION", label_font, PRIMARY_DARK)

    diff_font = _load_font(24, bold=True)
    _centered_text(draw, cx, cy + 105, course.get_difficulty_display().upper(), diff_font, CLAY)

    # Course title, wrapped
    title_font = _load_font(40, bold=True)
    title_y = cy + 380
    title_y = _wrapped_centered_text(
        draw, cx, title_y, course.title, title_font, INK, max_chars=26, line_height=50
    )

    # School name
    school_font = _load_font(26)
    _centered_text(draw, cx, title_y + 14, course.school.name, school_font, PRIMARY)

    # Divider
    draw.line((size * 0.18, title_y + 70, size * 0.82, title_y + 70), fill=LINE, width=2)

    # Recipient + date
    name_font = _load_font(32, bold=True)
    meta_font = _load_font(22)
    _centered_text(draw, cx, title_y + 95, _user_display_name(user), name_font, INK)
    date_str = datetime.now().strftime("Awarded %B %d, %Y")
    _centered_text(draw, cx, title_y + 140, date_str, meta_font, PRIMARY_DARK)

    # Footer brand mark
    brand_font = _load_font(24, bold=True)
    _centered_text(draw, cx, size - 60, "SWEEP", brand_font, GOLD)

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
