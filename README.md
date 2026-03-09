# Faceless Video Engine 🚀🎬

**Faceless Video Engine** is a lightweight, self-hosted Microservice written in Python (FastAPI). It acts as the "rendering engine" for automated, faceless video creation workflows (like YouTube Shorts, TikToks, and Instagram Reels).

Since automation platforms like **n8n** cannot render videos directly, this service bridges the gap. It accepts image URLs and audio URLs, stitches them together using **FFmpeg** in a vertical format (9:16), and returns a fully compiled `.mp4` video file ready for publishing.

---

## 🏗️ Architecture & Workflow
This engine is designed to be the final step in your AI content creation factory:

1. **n8n / Make.com:** Schedules the job, relies on OpenAI (ChatGPT) to write the script, generates images (Midjourney/DALL-E), and creates voiceovers (ElevenLabs/OpenAI TTS).
2. **Faceless Video Engine (This API):** Receives the array of image & audio URLs, processes them, scales them to 1080x1920, and glues them into a seamless video.
3. **Publishing:** n8n takes the generated video and uploads it directly to YouTube or TikTok.

---

## ✨ Features
- **FastAPI Backend:** Extremely fast and concurrent API handling.
- **FFmpeg Integration:** Powered by the industry-standard tool for high-quality video processing.
- **Vertical Format Optimization:** Automatically scales, crops, and pads images to fit a TikTok/Shorts `1080x1920` canvas.
- **Stateless & Clean:** Generates temporary files and cleans up automatically (runs out of `/tmp`).
- **Coolify / Docker Ready:** Just plug and play on your personal VPS or Proxmox instance.

---

## 🛠️ Installation & Deployment

This project is built to be deployed easily via Docker or **Coolify**.

### Method 1: Deploy with Coolify (Recommended)
1. In your Coolify dashboard, click **Add New Resource** -> **Git Repository**.
2. Paste the URL of this repository: `https://github.com/haydary1986/faceless-video-engine.git`
3. Coolify will automatically detect the `Dockerfile`.
4. Click **Deploy**.
5. Once deployed, you will get a public URL (e.g., `https://api.yourdomain.com`).

### Method 2: Deploy Locally using Docker
If you want to run it on your own machine using Docker:
```bash
# Clone the repository
git clone https://github.com/haydary1986/faceless-video-engine.git
cd faceless-video-engine

# Build the Docker image
docker build -t faceless-video-engine .

# Run the container mapping port 8000
docker run -d -p 8000:8000 faceless-video-engine
```

---

## 📡 API Reference

### `POST /generate-video`
This is the main endpoint used to generate the video. Send a JSON payload containing an array of `scenes`. Each scene requires an `image_url` and an `audio_url`.

**Request Header:**
```text
Content-Type: application/json
```

**Request Body Example:**
```json
{
  "scenes": [
    {
      "image_url": "https://example.com/scene1-image.jpg",
      "audio_url": "https://example.com/scene1-audio.mp3"
    },
    {
      "image_url": "https://example.com/scene2-image.jpg",
      "audio_url": "https://example.com/scene2-audio.mp3"
    }
  ]
}
```

**Response:**
Returns a binary `.mp4` file (`video/mp4`) containing the merged video.

---

## 🤖 Integration with n8n

To connect this Engine to your n8n workflow:
1. Add an **HTTP Request** node.
2. **Method:** `POST`
3. **URL:** `https://api.yourdomain.com/generate-video`
4. **Authentication:** None (unless you configured a proxy auth).
5. **Send Body:** Select `JSON` and map your array of scenes.
6. **Response Format:** `File` (Important! This tells n8n to download the returning dataset as an `.mp4` file).
7. Link this output node to your YouTube or TikTok Upload Node!

---

## 📝 License
This project is open-source and free to use for your automated empires!
