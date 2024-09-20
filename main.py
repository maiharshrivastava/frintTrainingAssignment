from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse
from typing import Dict

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResumeData(BaseModel):
    name: str
    email: str
    phone: str
    education: str
    experience: str
    skills: str

@app.post("/generate_resume/")
async def generate_resume(data: ResumeData) -> Dict[str, str]:
    """
    Generate a resume based on the provided data.

    Args:
        data (ResumeData): The input data containing personal information, education, experience, and skills.

    Returns:
        Dict[str, str]: A dictionary containing the generated resume content as a plain text string.

    Raises:
        HTTPException: If there is an error generating the resume, a 500 Internal Server Error is raised.
    """
    try:
        resume_content = f"""
        Name: {data.name}
        Email: {data.email}
        Phone: {data.phone}
        Education: {data.education}
        Experience: {data.experience}
        Skills: {data.skills}
        """
        return {"resume_content": resume_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_pdf/")
async def generate_pdf(data: ResumeData) -> StreamingResponse:
    """
    Generate a PDF of the resume based on the provided data.

    Args:
        data (ResumeData): The input data containing personal information, education, experience, and skills.

    Returns:
        StreamingResponse: A response containing the generated resume as a PDF file.

    Raises:
        HTTPException: If there is an error generating the PDF, a 500 Internal Server Error is raised.
    """
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        c.drawString(100, height - 100, f"Name: {data.name}")
        c.drawString(100, height - 120, f"Email: {data.email}")
        c.drawString(100, height - 140, f"Phone: {data.phone}")
        c.drawString(100, height - 160, f"Education: {data.education}")
        c.drawString(100, height - 180, f"Experience: {data.experience}")
        c.drawString(100, height - 200, f"Skills: {data.skills}")

        c.showPage()
        c.save()

        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=resume.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
