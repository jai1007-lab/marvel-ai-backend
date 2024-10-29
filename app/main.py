from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.router import router
from app.services.logger import setup_logger
from app.api.error_utilities import ErrorResponse
# FastAPI core imports
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File

import os
from dotenv import load_dotenv, find_dotenv
# Application-specific imports
from app.features.notes_generator.core import generate_notes
from app.services.schemas import NotesRequest, ToolResponse


# Load environment variables
load_dotenv(find_dotenv())

# Set up logger
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Application Startup")
    yield
    logger.info("Application shutdown")

# Initialize FastAPI app with CORS middleware
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error['loc'])
        message = error['msg']
        error_detail = f"Error in field '{field}': {message}"
        errors.append(error_detail)
        logger.error(error_detail)

    error_response = ErrorResponse(status=422, message=errors)
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )

@app.post("/generate_notes")
async def notes_generator(inputs: NotesRequest, file: UploadFile = File(None)):
    """
    Endpoint to generate notes from provided content or file.

    Args:
        inputs (NotesRequest): Contains file URL, orientation, and columns info.
        file (UploadFile): Optional file to generate notes from.

    Returns:
        JSONResponse: Returns notes generation results or error message.
    """
    try:
        file_url = inputs.file_url
        orientation = inputs.orientation
        columns = inputs.columns

        # Check if file or URL is provided
        if not file and not file_url:
            raise ValueError("Either a file or a file URL must be provided.")

        # Read the uploaded file content if provided
        file_content = None
        if file:
            file_content = await file.read()

        # Call the generate_notes function
        result = await generate_notes(file_url=file_url, file_content=file_content, orientation=orientation, columns=columns)

        return ToolResponse(data=result)

    except Exception as e:
        logger.error(f"Unexpected error in notes_generator: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
