from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import uvicorn

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


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")  # use 0.0.0.0 for Docker
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host=host, port=port)
