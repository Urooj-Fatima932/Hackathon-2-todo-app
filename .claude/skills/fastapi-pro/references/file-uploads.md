# FastAPI File Upload Patterns

## Single File Upload

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid

router = APIRouter(prefix="/files", tags=["files"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(..., description="File to upload")
) -> dict:
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Invalid file type")

    # Validate file size (read in chunks)
    max_size = 10 * 1024 * 1024  # 10MB
    size = 0
    chunks = []
    while chunk := await file.read(1024 * 1024):  # 1MB chunks
        size += len(chunk)
        if size > max_size:
            raise HTTPException(413, "File too large")
        chunks.append(chunk)

    # Save file
    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4()}{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        for chunk in chunks:
            f.write(chunk)

    return {"filename": filename, "size": size}
```

## Multiple File Upload

```python
from typing import List

@router.post("/upload-multiple/")
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="Files to upload")
) -> dict:
    if len(files) > 10:
        raise HTTPException(400, "Maximum 10 files allowed")

    results = []
    for file in files:
        # Process each file
        content = await file.read()
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = UPLOAD_DIR / filename

        with open(filepath, "wb") as f:
            f.write(content)

        results.append({
            "original_name": file.filename,
            "saved_name": filename,
            "size": len(content)
        })

    return {"files": results}
```

## File Upload with Form Data

```python
from fastapi import Form

@router.post("/upload-with-metadata/")
async def upload_with_metadata(
    file: UploadFile = File(...),
    title: str = Form(..., max_length=100),
    description: str = Form(None, max_length=500),
) -> dict:
    content = await file.read()
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        f.write(content)

    # Save metadata to database
    return {
        "filename": filename,
        "title": title,
        "description": description,
    }
```

## Streaming Large Files

```python
import aiofiles

@router.post("/upload-large/")
async def upload_large_file(file: UploadFile = File(...)) -> dict:
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = UPLOAD_DIR / filename

    async with aiofiles.open(filepath, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await f.write(chunk)

    return {"filename": filename}
```

## File Download

```python
from fastapi.responses import FileResponse, StreamingResponse
import aiofiles

@router.get("/download/{filename}")
async def download_file(filename: str) -> FileResponse:
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "File not found")

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/octet-stream"
    )

@router.get("/stream/{filename}")
async def stream_file(filename: str) -> StreamingResponse:
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "File not found")

    async def file_iterator():
        async with aiofiles.open(filepath, "rb") as f:
            while chunk := await f.read(1024 * 1024):
                yield chunk

    return StreamingResponse(
        file_iterator(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

## Image Processing

```python
from PIL import Image
from io import BytesIO

@router.post("/upload-image/")
async def upload_image(
    file: UploadFile = File(...),
    max_width: int = 800,
    max_height: int = 800,
) -> dict:
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    content = await file.read()
    image = Image.open(BytesIO(content))

    # Resize if needed
    image.thumbnail((max_width, max_height))

    # Save
    filename = f"{uuid.uuid4()}.webp"
    filepath = UPLOAD_DIR / filename
    image.save(filepath, "WEBP", quality=85)

    return {
        "filename": filename,
        "width": image.width,
        "height": image.height
    }
```

## S3 Upload

```python
import boto3
from botocore.exceptions import ClientError
from app.config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION,
)

@router.post("/upload-s3/")
async def upload_to_s3(file: UploadFile = File(...)) -> dict:
    filename = f"{uuid.uuid4()}_{file.filename}"

    try:
        content = await file.read()
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=filename,
            Body=content,
            ContentType=file.content_type,
        )
    except ClientError as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

    url = f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
    return {"filename": filename, "url": url}
```

## Upload Schema for Database

```python
from pydantic import BaseModel
from datetime import datetime

class FileUpload(BaseModel):
    id: int
    original_name: str
    stored_name: str
    content_type: str
    size: int
    url: str
    uploaded_by: int
    created_at: datetime

# SQLAlchemy model
class FileModel(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255), unique=True)
    content_type: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column()
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

## Virus Scanning (Example with ClamAV)

```python
import clamd

def scan_file(filepath: Path) -> bool:
    """Scan file for viruses. Returns True if clean."""
    cd = clamd.ClamdUnixSocket()
    result = cd.scan(str(filepath))
    return result[str(filepath)][0] == "OK"

@router.post("/upload-safe/")
async def upload_with_scan(file: UploadFile = File(...)) -> dict:
    # Save to temp location
    temp_path = Path(f"/tmp/{uuid.uuid4()}")
    content = await file.read()
    temp_path.write_bytes(content)

    try:
        if not scan_file(temp_path):
            raise HTTPException(400, "File failed virus scan")

        # Move to permanent location
        final_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
        shutil.move(temp_path, final_path)

        return {"filename": final_path.name}
    finally:
        if temp_path.exists():
            temp_path.unlink()
```
