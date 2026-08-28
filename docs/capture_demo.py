import os
import time
import subprocess
from playwright.sync_api import sync_playwright

def main():
    os.makedirs("/tmp/demo_frames", exist_ok=True)
    frame_idx = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        print("Navigating to http://127.0.0.1:8085/...")
        page.goto("http://127.0.0.1:8085/", wait_until="networkidle")
        time.sleep(2)

        # Initial frame
        for _ in range(3):
            page.screenshot(path=f"/tmp/demo_frames/frame_{frame_idx:04d}.png")
            frame_idx += 1

        prompts_to_run = [
            ("🌲 Find Nature Walks", "Find scenic nature walks near my drop-off location", 5),
            ("🎼 Custom AI Song", "Sing a happy song in Kannada about coffee walk in the park", 6),
            ("☀️ Check Live Weather", "Check current walk weather and UV index", 4),
            ("⏱️ Calculate Schedule", "Calculate time schedule for 45 min class returning 5 mins early", 4),
        ]

        for label, prompt_text, wait_sec in prompts_to_run:
            print(f"Triggering demo action: {label}...")
            # Trigger sendQuickPrompt directly via JS
            page.evaluate(f"sendQuickPrompt('{prompt_text}')")

            for _ in range(wait_sec * 2):
                time.sleep(0.5)
                page.screenshot(path=f"/tmp/demo_frames/frame_{frame_idx:04d}.png")
                frame_idx += 1

        browser.close()

    print(f"Captured {frame_idx} frames. Assembling MP4 & GIF with FFmpeg...")

    mp4_path = "docs/demo_walkthrough.mp4"
    gif_path = "docs/demo_walkthrough.gif"

    cmd_mp4 = [
        "ffmpeg", "-y", "-framerate", "2",
        "-i", "/tmp/demo_frames/frame_%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-vf", "scale=1280:-2",
        mp4_path
    ]
    subprocess.run(cmd_mp4, check=True)

    cmd_gif = [
        "ffmpeg", "-y", "-framerate", "2",
        "-i", "/tmp/demo_frames/frame_%04d.png",
        "-vf", "scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        gif_path
    ]
    subprocess.run(cmd_gif, check=True)

    print(f"Successfully generated {mp4_path} and {gif_path}!")

if __name__ == "__main__":
    main()
