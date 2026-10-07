"""Capture the rendered demo dashboard at desktop and mobile sizes.

Install the screenshots extra and run `playwright install chromium` first.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.dashboard_app import dashboard


def capture(output_dir: Path, executable_path: str | None = None) -> None:
    from playwright.sync_api import sync_playwright

    output_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=executable_path)
        try:
            for name, width, height in [("desktop", 1440, 1000), ("mobile", 390, 844)]:
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                page.set_content(dashboard(), wait_until="load")
                page.screenshot(path=str(output_dir / f"dashboard-{name}.png"), full_page=True)
                page.close()
        finally:
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable-path", help="Optional installed Chromium/Chrome executable")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "docs" / "screenshots")
    args = parser.parse_args()
    capture(args.output_dir, args.executable_path)
