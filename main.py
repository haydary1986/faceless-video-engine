from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import subprocess
import requests
import uuid
import os
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Faceless Video Engine is running correctly!"}

class Scene(BaseModel):
    image_url: str
    text: Optional[str] = None
    audio_url: Optional[str] = None

class VideoRequest(BaseModel):
    scenes: list[Scene]
    elevenlabs_api_key: Optional[str] = None
    voice_id: str = "EXAVITQu4vr4xnSDxMaL" # Default Arabic/Multi voice

@app.post("/generate-video")
def generate_video(req: VideoRequest):
    job_id = str(uuid.uuid4())
    work_dir = f"/tmp/{job_id}"
    os.makedirs(work_dir, exist_ok=True)
    
    clips = []
    
    try:
        for i, scene in enumerate(req.scenes):
            img_path = f"{work_dir}/img_{i}.jpg"
            aud_path = f"{work_dir}/aud_{i}.mp3"
            clip_path = f"{work_dir}/clip_{i}.mp4"
            
            # 1. Download Image
            with open(img_path, 'wb') as f:
                f.write(requests.get(scene.image_url).content)
                
            # 2. Get Audio (Either from URL or Generate via ElevenLabs)
            if scene.audio_url:
                with open(aud_path, 'wb') as f:
                    f.write(requests.get(scene.audio_url).content)
            elif scene.text and req.elevenlabs_api_key:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{req.voice_id}"
                headers = {
                    "xi-api-key": req.elevenlabs_api_key, 
                    "Content-Type": "application/json"
                }
                data = {
                    "text": scene.text, 
                    "model_id": "eleven_multilingual_v2"
                }
                res = requests.post(url, json=data, headers=headers)
                if res.status_code != 200:
                    raise Exception(f"ElevenLabs Error: {res.text}")
                with open(aud_path, 'wb') as f:
                    f.write(res.content)
            else:
                raise Exception("Scene must have either audio_url or (text + elevenlabs_api_key)")
                
            # 3. Merge Audio and Image
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", img_path, "-i", aud_path,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=crop,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", 
                "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", clip_path
            ]
            subprocess.run(cmd, check=True)
            clips.append(clip_path)
            
        # 4. Concat all scenes
        concat_file = f"{work_dir}/concat.txt"
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
                
        final_output = f"/tmp/final_{job_id}.mp4"
        concat_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
            "-c", "copy", final_output
        ]
        subprocess.run(concat_cmd, check=True)

        return FileResponse(final_output, media_type="video/mp4", filename=f"short_{job_id}.mp4")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
