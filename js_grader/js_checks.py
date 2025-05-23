import requests
import io
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def check_project_is_viewable(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️ Could not connect to {url}: {e}")
        return False


def screenshot_app(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=800,600")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)  # Allow time for canvas and sprites to load

    png = driver.get_screenshot_as_png()
    driver.quit()

    return Image.open(io.BytesIO(png))


def get_dominant_color(image):
    small = image.resize((50, 50))
    result = small.convert('P', palette=Image.ADAPTIVE, colors=5)
    palette = result.getpalette()
    color_counts = sorted(result.getcolors(), reverse=True)
    dominant = color_counts[0][1]
    rgb = tuple(palette[dominant * 3:dominant * 3 + 3])
    return rgb


def get_sample_colors(image):
    """
    Return RGB tuples from the left, center, and right zones of the canvas.
    """
    width, height = image.size
    y = int(height * 0.25)  # sample row 25% down

    left = image.getpixel((int(width * 0.10), y))
    center = image.getpixel((int(width * 0.50), y))
    right = image.getpixel((int(width * 0.85), y))

    return {
        "left_color": left,
        "center_color": center,
        "right_color": right
    }


def grade_js_project(url):
    if not url:
        return {
            'dominant_color': 'N/A',
            'feedback_html': "<p>❌ No project URL provided.</p>"
        }

    if not check_project_is_viewable(url):
        return {
            'dominant_color': 'N/A',
            'feedback_html': "<p>❌ Could not access the project. Is it shared?</p>"
        }

    try:
        img = screenshot_app(url)
        color_samples = get_sample_colors(img)
        feedback = f"<p>🎨 Sampled Colors – Left: {color_samples['left_color']}, Center: {color_samples['center_color']}, Right: {color_samples['right_color']}</p>"
    except Exception as e:
        return {
            'dominant_color': 'Error',
            'feedback_html': f"<p>❌ Could not capture or analyze screenshot: {e}</p>"
        }

    return {
        'dominant_color': str(get_dominant_color(img)),
        'left_color': str(color_samples['left_color']),
        'center_color': str(color_samples['center_color']),
        'right_color': str(color_samples['right_color']),
        'feedback_html': feedback
    }
