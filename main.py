from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(title="Rakib Testing")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_index():
    html_file_path = "static/index.html"
    if not os.path.exists(html_file_path):
        raise HTTPException(status_code=500, detail="index.html not found")

    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(html_content)

# Only needed if you want to run locally
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
