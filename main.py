"""
Health Insurance Claim Processing System.

API endpoint for processing claim files.
"""

import logging
import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Health Insurance Claim Processor")


@app.post("/process-claim")
async def process_claim(files: list[UploadFile] = File(...)):
    """Process uploaded claim files and return decision."""
    from src.agent.react_agent import run_agent
    
    # Save uploaded files temporarily
    temp_files = []
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_files.append(temp_file.name)
    
    try:
        # Run the agent
        result = run_agent(temp_files)
        return JSONResponse(content=result)
    finally:
        # Clean up temp files
        for temp_file in temp_files:
            os.unlink(temp_file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)