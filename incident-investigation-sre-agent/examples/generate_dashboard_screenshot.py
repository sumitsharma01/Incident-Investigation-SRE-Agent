import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.demo_data import build_demo_context
from examples.dashboard_demo import render_dashboard


def create_dashboard_screenshot(output_path: str = "examples/dashboard_screenshot.png") -> str:
    context = build_demo_context("checkout")
    text = render_dashboard(context)

    image = Image.new("RGB", (1200, 900), "#0b1220")
    draw = ImageDraw.Draw(image)

    title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
    body_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 21)
    small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 17)

    draw.rectangle((30, 30, 1170, 870), fill="#132238", outline="#2b4a72", width=2)
    draw.text((60, 55), "Incident Investigation SRE Agent Dashboard", fill="#8be9fd", font=title_font)

    y = 110
    for line in text.splitlines():
        color = "#e5eefb"
        if line.startswith("Service:") or line.startswith("SLO:") or line.startswith("Error budget remaining") or line.startswith("Toil risk"):
            color = "#ffd166"
        elif line.startswith("SLI snapshot") or line.startswith("Top recommendations") or line.startswith("Evidence summary"):
            color = "#7dd3fc"
        draw.text((60, y), line, fill=color, font=body_font if not line.startswith("  •") else small_font)
        y += 28

    output = Path(output_path)
    image.save(output)
    return str(output)


if __name__ == "__main__":
    print(create_dashboard_screenshot())
