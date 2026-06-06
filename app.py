import logging
import os
from urllib.parse import urlparse

import joblib
import numpy as np
import requests
from flask import Flask, jsonify, request
from io import BytesIO
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# These are the possible categories (classes) which can be detected
NAMEMAP = [
    'axes',
    'boots',
    'carabiners',
    'crampons',
    'gloves',
    'hardshell_jackets',
    'harnesses',
    'helmets',
    'insulated_jackets',
    'pulleys',
    'rope',
    'tents',
]

app = Flask(__name__)

# Load the model once at startup rather than on every request
MODEL_PATH = os.environ.get('MODEL_PATH', 'pickle_model.pkl')
model = joblib.load(MODEL_PATH)
logger.info("Model loaded from %s", MODEL_PATH)


def resize(image):
    """Resize an image so its longest side is 128 px, then centre-pad to 128x128."""
    base = 128
    width, height = image.size
    resample = Image.Resampling.LANCZOS

    if width > height:
        wpercent = base / float(width)
        hsize = int(float(height) * wpercent)
        image = image.resize((base, hsize), resample)
    else:
        hpercent = base / float(height)
        wsize = int(float(width) * hpercent)
        image = image.resize((wsize, base), resample)

    canvas = Image.new('RGB', (base, base), (255, 255, 255))
    position = (int(base / 2 - image.width / 2), 0)
    canvas.paste(image, position)
    return canvas


def normalize(arr):
    """Min-max normalise each RGB channel independently to the 0-255 range.

    Normalization is useful when the distribution of the data is unknown or
    non-Gaussian: it scales each channel so the minimum becomes 0 and the
    maximum becomes 255.
    """
    arr = arr.astype('float')
    for i in range(3):
        minval = arr[..., i].min()
        maxval = arr[..., i].max()
        if minval != maxval:
            arr[..., i] -= minval
            arr[..., i] *= 255.0 / (maxval - minval)
    return arr


def process_image(image):
    """Resize and normalise an image for model inference."""
    image = resize(image)
    arr = np.array(image)
    processed = Image.fromarray(normalize(arr).astype('uint8'), 'RGB')
    return processed


@app.route('/health', methods=['GET'])
def health():
    """Liveness probe — returns 200 when the service is ready."""
    return jsonify({"status": "ok"})


@app.route('/classify', methods=['POST'])
def classify():
    """Classify an image by URL.

    POST a JSON body with a ``url`` key pointing to an image.  The endpoint
    returns the predicted category label.  Example::

        {"url": "https://example.com/image.jpg"}

    Swap out *pickle_model.pkl* with any compatible scikit-learn model to
    classify different objects.
    """
    body = request.get_json(silent=True)
    if not body or 'url' not in body:
        return jsonify({"error": "Request body must be JSON with a 'url' field."}), 400

    img_url = body['url']

    # Reject non-HTTP/S schemes to prevent SSRF (e.g. file://, gopher://)
    try:
        parsed = urlparse(img_url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            return jsonify({"error": "URL must use http or https."}), 400
    except Exception:
        return jsonify({"error": "Invalid URL."}), 400

    logger.info("Classifying image: %s", img_url)

    try:
        response = requests.get(img_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert('RGB')
    except requests.RequestException as exc:
        logger.warning("Failed to fetch image %s: %s", img_url, exc)
        return jsonify({"error": "Could not retrieve image."}), 422
    except Exception as exc:
        logger.warning("Could not open image from %s: %s", img_url, exc)
        return jsonify({"error": "Could not open image."}), 422

    processed_img = process_image(img)

    # Flatten the 128x128x3 image into a 1-D feature vector
    img_features = np.array(processed_img).ravel().reshape(1, -1)
    prediction = model.predict(img_features)
    label = NAMEMAP[int(prediction[0])]
    logger.info("Prediction: %s", label)

    # Convert the integer index into a human-readable label.
    # e.g. 0 → 'axes', 1 → 'boots', 2 → 'carabiners'
    return jsonify({"classification": label})


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0')
