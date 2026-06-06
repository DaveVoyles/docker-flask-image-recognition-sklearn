
# Docker + Flask Image Classification with scikit-learn

#### Author: Dave Voyles | [@DaveVoyles](https://twitter.com/DaveVoyles)

A containerised REST API that classifies outdoor-gear images using a pre-trained
scikit-learn model, served via Flask and Gunicorn inside Docker.

---

## Why would you want this?

Imagine you've built a machine-learning model and want others to call it over HTTP.
Packaging it inside Docker means:

- **Portability** – "works on my machine" becomes "works everywhere."
- **Scalability** – run multiple replicas behind a load-balancer with no code changes.
- **Reproducibility** – the exact Python version and dependencies are frozen in the image.

### Tech stack

| Tool | Purpose |
|---|---|
| **Docker** | Containerises the entire application |
| **Flask** | Lightweight Python web framework |
| **Gunicorn** | Production-grade WSGI server |
| **scikit-learn** | Loads and runs the pre-trained model |
| **Pillow / NumPy** | Image pre-processing |

---

## What can it classify?

POST any publicly reachable image URL and the API returns its predicted category:

- axes
- boots
- carabiners
- crampons
- gloves
- hardshell jackets
- harnesses
- helmets
- insulated jackets
- pulleys
- rope
- tents

---

## Using your own model

1. Train a scikit-learn classifier that expects a flat **128 × 128 × 3 = 49 152**-feature vector.
2. Serialize it with `joblib.dump(model, 'pickle_model.pkl')`.
3. Drop your `pickle_model.pkl` into this directory and rebuild the image.

The `process_image()` helper in `app.py` handles resizing and per-channel min-max
normalisation automatically, so new images will be prepared consistently.

---

## Build and run locally

**Build the image**

```bash
docker build -t davevoyles/docker-flask-image-recognition-sklearn:latest .
```

**Run the container**

```bash
docker run -d \
  --name flask-classifier \
  -p 5000:5000 \
  davevoyles/docker-flask-image-recognition-sklearn:latest
```

**Verify the container is running**

```bash
docker ps
docker logs flask-classifier
```

**Check the health endpoint**

```bash
curl http://localhost:5000/health
# {"status": "ok"}
```

**Remove the container**

```bash
docker rm -f flask-classifier
```

---

## Push to Docker Hub

```bash
docker push davevoyles/docker-flask-image-recognition-sklearn:latest
```

---

## Deploy to Azure Container Instances

**Login**

```bash
az login
```

**Create a resource group (one time)**

```bash
az group create -l eastus -n dv-containers-rg
```

**Create the container**

```bash
az container create \
  --resource-group dv-containers-rg \
  --name dv-flask-container \
  --image davevoyles/docker-flask-image-recognition-sklearn:latest \
  --ip-address public \
  --location eastus \
  --ports 5000
```

**Get the public IP**

```bash
az container show \
  --resource-group dv-containers-rg \
  --name dv-flask-container \
  --query ipAddress
```

Sample output:

```json
{
  "ip": "40.114.107.193",
  "ports": [{"port": 5000, "protocol": "TCP"}]
}
```

**Stream logs**

```bash
az container logs --resource-group dv-containers-rg --name dv-flask-container
```

**Delete the container**

```bash
az container delete --resource-group dv-containers-rg --name dv-flask-container
```

You can also monitor the container from the [Azure Portal](https://portal.azure.com).

![Azure Portal 1](/Images/az-portal-1.png)

![Azure Portal 2](/Images/az-portal-2.png)

---

## API reference

### `GET /health`

Liveness probe.  Returns `200 OK` when the service is ready.

```bash
curl http://<YOUR_IP>:5000/health
```

```json
{"status": "ok"}
```

---

### `POST /classify`

Classify an image by URL.

**Request body**

```json
{"url": "https://example.com/path/to/image.jpg"}
```

**Response**

```json
{"classification": "insulated_jackets"}
```

**Example – insulated jacket**

```bash
curl -X POST http://<YOUR_IP>:5000/classify \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://images.thenorthface.com/is/image/TheNorthFace/NF0A2VD5_KX7_hero?$638x745$"}'
```

**Example – helmet**

```bash
curl -X POST http://<YOUR_IP>:5000/classify \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://m.fortnine.ca/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/catalogimages/gmax/gm45-half-helmet-matte-black-xs.jpg"}'
```

**Error responses**

| Status | Meaning |
|---|---|
| `400` | Missing or malformed JSON body |
| `422` | Image URL could not be fetched or decoded |
| `500` | Unexpected server error |

