import re, io, time, requests
from pathlib import Path
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIG ===
project_url = "https://studio.code.org/projects/gamelab/ZTN1UoLQ77vrf_uiTWAVdPuAQoaeQeiOTK96oaX99Ok"
student_name = "SampleBunny"


# === UTILS ===
def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)


def screenshot_app(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=800,600")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)
    png = driver.get_screenshot_as_png()
    driver.quit()
    return Image.open(io.BytesIO(png))


def get_sample_colors(image):
    width, height = image.size
    y = int(height * 0.35)
    left = image.getpixel((int(width * 0.35), y))
    center = image.getpixel((int(width * 0.50), y))
    right = image.getpixel((int(width * 0.65), y))
    return left, center, right


# === PROCESS ===
img = screenshot_app(project_url)
left, center, right = get_sample_colors(img)

screenshot_dir = Path("data/screenshots")
screenshot_dir.mkdir(parents=True, exist_ok=True)
safe_name = sanitize_filename(student_name)
img_path = screenshot_dir / f"{safe_name}.png"
img.save(img_path)

# === OUTPUT HTML ===
html_path = Path("data/test_feedback.html")
html_path.write_text(f"""
<html><body>
<h2>{student_name}</h2>
<p><a href="{project_url}" target="_blank">🔗 View Project</a></p>
<p>🎯 Sampled Colors — Left: {left}, Center: {center}, Right: {right}</p>
<img src="screenshots/{safe_name}.png" width="300">
</body></html>
""", encoding="utf-8")

print(f"✅ Done. Open 'data/test_feedback.html' in your browser.")
