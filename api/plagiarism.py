# FastAPI Backend - Plagiarism Checker API (Simplified)
from fastapi import FastAPI, HTTPException, UploadFile, File, Response
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import re
from datetime import datetime
import asyncio
import random
import io
try:
    import docx
except ImportError:
    docx = None
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

app = FastAPI()

class PlagiarismRequest(BaseModel):
    content: str

class PlagiarismResult(BaseModel):
    id: str
    source: str
    similarity: float
    matched_text: str
    url: str
    type: str

class PlagiarismResponse(BaseModel):
    overallScore: float
    results: List[PlagiarismResult]
    processingTime: float

@app.post("/api/plagiarism/check", response_model=PlagiarismResponse)
async def check_plagiarism(request: PlagiarismRequest):
    """
    Check content for plagiarism using simulated analysis
    """
    start_time = datetime.now()
    
    try:
        content = request.content
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Generate mock results based on content analysis
        results = await generate_mock_results(content)
        print(f"[DEBUG] Plagiarism results for input: {results}")
        
        # Calculate overall score
        total_similarity = sum(result.similarity for result in results)
        overall_score = max(0, 100 - total_similarity)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return PlagiarismResponse(
            overallScore=overall_score,
            results=results,
            processingTime=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plagiarism/import", response_model=PlagiarismResponse)
async def import_and_check_plagiarism(file: UploadFile = File(...)):
    """
    Import a document (TXT, DOCX, PDF), extract text, and check for plagiarism.
    """
    try:
        content = await file.read()
        text = ""
        if file.filename.endswith(".txt"):
            text = content.decode("utf-8", errors="ignore")
        elif file.filename.endswith(".docx") and docx:
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs])
        elif file.filename.endswith(".pdf") and PyPDF2:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type or missing dependency.")
        # Run plagiarism check
        results = await generate_mock_results(text)
        total_similarity = sum(result.similarity for result in results)
        overall_score = max(0, 100 - total_similarity)
        processing_time = 2.0  # Simulate
        return PlagiarismResponse(
            overallScore=overall_score,
            results=results,
            processingTime=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plagiarism/export")
async def export_plagiarism_report(format: str = "json", response: PlagiarismResponse = None):
    """
    Export plagiarism report as JSON or TXT. Accepts PlagiarismResponse payload.
    """
    if response is None:
        raise HTTPException(status_code=400, detail="No report data provided.")
    if format == "json":
        return Response(content=response.json(), media_type="application/json", headers={"Content-Disposition": "attachment; filename=plagiarism_report.json"})
    elif format == "txt":
        txt = f"Plagiarism Report\nScore: {response.overallScore}\nProcessing Time: {response.processingTime}s\n\nResults:\n"
        for r in response.results:
            txt += f"- Source: {r.source}\n  Similarity: {r.similarity}%\n  Matched: {r.matched_text}\n  URL: {r.url}\n  Type: {r.type}\n\n"
        return Response(content=txt, media_type="text/plain", headers={"Content-Disposition": "attachment; filename=plagiarism_report.txt"})
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format.")

async def generate_mock_results(content: str) -> List[PlagiarismResult]:
    """Generate realistic mock plagiarism results"""
    results = []
    import random
    # Mock sources
    sources = [
        {"name": "Wikipedia", "type": "web", "domain": "wikipedia.org"},
        {"name": "Academic Paper - ResearchGate", "type": "academic", "domain": "researchgate.net"},
        {"name": "Journal Article - JSTOR", "type": "publication", "domain": "jstor.org"},
        {"name": "News Article - BBC", "type": "web", "domain": "bbc.com"},
        {"name": "Blog Post - Medium", "type": "web", "domain": "medium.com"},
        {"name": "IEEE Paper", "type": "academic", "domain": "ieee.org"},
        {"name": "Nature Journal", "type": "publication", "domain": "nature.com"},
        {"name": "Educational Resource", "type": "web", "domain": "edu"}
    ]
    if content.strip():
        source = random.choice(sources)
        snippet = content.strip()[:100] + ("..." if len(content.strip()) > 100 else "")
        similarity = round(random.uniform(5, 20), 1)
        results.append(PlagiarismResult(
            id="result_0",
            source=source["name"],
            similarity=similarity,
            matched_text=snippet,
            url=f"https://{source['domain']}/article/0",
            type=source["type"]
        ))
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)