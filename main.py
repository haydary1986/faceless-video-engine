from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import requests
import uuid
import os

app = FastAPI()

class Scene(BaseModel):
    image_url: str
    audio_url: str

class VideoRequest(BaseModel):
    scenes: list[Scene]

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
            
            # تحميل الصورة والصوت من الروابط
            with open(img_path, 'wb') as f:
                f.write(requests.get(scene.image_url).content)
            with open(aud_path, 'wb') as f:
                f.write(requests.get(scene.audio_url).content)
                
            # دمج الصورة والصوت باستخدام FFmpeg
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", img_path, "-i", aud_path,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=crop,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", 
                "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", clip_path
            ]
            subprocess.run(cmd, check=True)
            clips.append(clip_path)
            
        # دمج المشاهد
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
