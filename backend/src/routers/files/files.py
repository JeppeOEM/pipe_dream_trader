import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
import pandas as pd
from ...dependencies import db_dependency, user_dependency
from ...lib.data.FileLoader import FileLoader
from ...lib.data.FileValidator import FileValidator
from ...models import Files, Users
from ...schemas import *
from ...utils.exceptions import (
    handle_db_error,
    handle_not_found_error,
    handle_not_validated_file_error,
)

router = APIRouter(prefix="/file", tags=["file"])


class FileRequest(BaseModel):
    period: str
    pair: str



@router.get("", status_code=status.HTTP_200_OK, response_model=List[FileSchema])
def get_all_files(db: db_dependency):
    # user: user_dependency,
    try:
        files = db.query(Files).all()
        if not files:
            handle_not_found_error("No files found.")
        #
        return [file for file in files]

    except SQLAlchemyError as e:

        handle_db_error(e, "SQLAlchemy failed feching the file paths")

    except Exception as e:

        handle_db_error(e, "Unexpected error occurred while fetching the file paths")


@router.get("/{file_id}", status_code=status.HTTP_200_OK, response_model=FileResponse)

def get_file(db: db_dependency, file_id: int):
    ##user: user_dependency,
    try:
        file = db.query(Files).get(file_id)

        if not file:
            handle_not_found_error("No file found")
        
        path = file.path
        fileLoader = FileLoader(path)
        fileLoader.load_data()
        data = fileLoader.df.to_json(orient="index")
        
        if not data or fileLoader.df.empty:
            handle_not_found_error("No data found in the file")
        columns = fileLoader.df.columns.tolist()

        return {"file": file, "data": data, "columns": columns}

    except SQLAlchemyError as e:

        handle_db_error(e, "SQLAlchemy failed feching the file path")

    except Exception as e:
        handle_db_error(e, "Unexpected error occurred while fetching the file")


@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_uploaded_file(db: db_dependency, file: UploadFile):
    """
    user: user_dependency,
    FastAPI automatically reads the file and populates UploadFile.
    UploadFile comes with file, filename, size and headers as instance attributes
    -------------------------------------------------------------------
    Will saves to disk if validation passes otherwise retures a list of broken
    rows in the error message

    -------------------------------------------------------------------
    FastApi dont have max file size so depends on the server

    """

    file_path = None
    try:
        file_path = save_file(file)

        name = Path(file_path).name
        fileValidation = FileValidator(file_path)
        validated = fileValidation.validate()
        print(validated, "validation check")
        if validated == True:
            name = Path(file_path).name
            saved_file = Files(
                path=file_path, name=name, file_type=fileValidation.file_type
            )
            # TODO: check os remove
            # os.remove(fileValidation.file_path)
            db.add(saved_file)
            db.commit()
        else:
            os.remove(fileValidation.file_path)
            handle_not_validated_file_error(
                "File contains validation errors, see result in the details",
                fileValidation.errors,
            )

    except Exception as e:
        if file_path:
            # clean up if validation fails
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"File not saved: {e}")

    return {"file_saved": file_path}


def save_file(file: UploadFile) -> str:
    folder_path = Path(__file__).parent.parent.parent.parent / "uploaded_files"
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / file.filename

    if file_path.exists():
        # send a "Conflict" status code
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File '{file.filename}' already exists.",
        )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(file_path)


def validate_or_delete(result, file_path) -> bool:
    if not result.validated:
        print(result.errors)
        os.remove(file_path)
        handle_not_validated_file_error(
            "File contains validation errors, see result in details", result.errors
        )
    return True
