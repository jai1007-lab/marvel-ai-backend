# Standard library imports
from typing import Any, Dict, Optional

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

# Application-specific imports
from app.features.notes_generator.tools import NotesGenerator
from app.services.logger import setup_logger
from app.services.schemas import NotesRequest

# Initialize the logger
logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI()

async def generate_notes(file_url: Optional[str] = None, 
                         file_content: Optional[bytes] = None, 
                         orientation: str = 'portrait', 
                         columns: int = 1) -> Dict[str, Any]:
    """
    Generates notes from the provided content or file.

    Args:
        file_url (str): URL of the file to be processed (if provided).
        file_content (bytes): Content of the uploaded file (if provided).
        orientation (str): Page orientation for PDF output ('portrait' or 'landscape').
        columns (int): Number of columns in the PDF (1 or 2).

    Returns:
        dict: A dictionary containing the result of the notes generation process.
    """
    try:
        # Ensure at least one input source is provided
        if not file_url and not file_content:
            raise ValueError("Either a file URL or file content must be provided.")

        # Initialize the NotesGenerator
        notes_generator = NotesGenerator(
            model='llama-3.1-70b-versatile',
            notes_content=file_url or file_content,
            orientation=orientation,
            columns=columns
        )

        # Run the notes generation process
        result = notes_generator.run()

        # Log success
        logger.info("Notes generated successfully.")

        return {"status": "success", "data": result}

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise

    except Exception as e:
        error_message = f"Error generating notes: {e}"
        logger.error(error_message)
        raise RuntimeError(error_message)

@app.post("/generate_notes")
async def notes_generator(
    file: Optional[UploadFile] = File(None),
    file_url: Optional[str] = None,
    orientation: Optional[str] = "portrait",
    columns: Optional[int] = 1
):
    try:
        file_content = None

        if file:
            file_content = await file.read()

        request_data = NotesRequest(file_url=file_url, orientation=orientation, columns=columns)

        # Pass data to generate_notes function
        result = await generate_notes(
            file_url=request_data.file_url,
            file_content=file_content,
            orientation=request_data.orientation,
            columns=request_data.columns
        )

        return {"status": "success", "data": result}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in notes_generator: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
