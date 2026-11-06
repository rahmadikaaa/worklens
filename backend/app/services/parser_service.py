"""Service for reading and parsing uploaded assessment files (JSON/CSV) for WORKLENS."""

import csv
import io
import json
from pathlib import Path
from typing import Any
from fastapi import HTTPException, status


def validate_and_resolve_file(filename: str, upload_dir: Path) -> Path:
    """Validate filename against path traversal and resolve to upload directory."""
    if not filename or Path(filename).name != filename or "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: path traversal or invalid characters detected.",
        )

    upload_dir_resolved = upload_dir.resolve()
    target_path = (upload_dir / filename).resolve()

    # Ensure path stays strictly inside upload_dir
    try:
        target_path.relative_to(upload_dir_resolved)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: file path escapes upload directory.",
        )

    if not target_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{filename}' not found in upload directory.",
        )

    return target_path


def decode_csv_bytes(raw_bytes: bytes) -> str:
    """Decode raw CSV bytes supporting UTF-8 BOM, UTF-8, and Windows-1252."""
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty (0 bytes).",
        )

    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return raw_bytes.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unable to decode CSV file. Supported encodings are UTF-8, UTF-8 BOM, and Windows-1252.",
    )


def parse_csv_file(target_path: Path) -> dict[str, Any]:
    """Parse CSV file supporting comma and semicolon delimiters without mutating source."""
    raw_bytes = target_path.read_bytes()
    text = decode_csv_bytes(raw_bytes)

    lines = text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file contains no records or header.",
        )

    # Check for unclosed quotation marks
    if text.count('"') % 2 != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed CSV file: unclosed quotation mark detected.",
        )

    # Detect delimiter: comma vs semicolon based on header frequency
    first_line = non_empty_lines[0]
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","

    f_stream = io.StringIO(text)
    reader = csv.reader(f_stream, delimiter=delimiter, strict=True)

    try:
        header_row = next(reader, None)
    except csv.Error as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Malformed CSV header: {err}",
        ) from err

    if not header_row or not any(col.strip() for col in header_row):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed CSV: header row is empty or contains no valid column names.",
        )

    columns = [col.strip() for col in header_row if col.strip()]

    total_rows = 0
    try:
        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            total_rows += 1
    except csv.Error as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Malformed CSV file: {err}",
        ) from err

    return {
        "filename": target_path.name,
        "file_format": "csv",
        "total_rows": total_rows,
        "total_columns": len(columns),
        "columns": columns,
        "metadata": {},
        "parsing_status": "success",
        "message": f"Successfully parsed {total_rows} records with {len(columns)} columns.",
    }


def parse_json_file(target_path: Path) -> dict[str, Any]:
    """Parse JSON file supporting envelope with 'value' and top-level array structures."""
    raw_bytes = target_path.read_bytes()
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JSON file is empty (0 bytes).",
        )

    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"JSON encoding error: file must be UTF-8 encoded ({err}).",
        ) from err

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON syntax: {err}",
        ) from err

    metadata: dict[str, Any] = {}
    records: list[dict[str, Any]] = []

    if isinstance(parsed, dict):
        if "value" not in parsed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported JSON structure: expected top-level array or object with 'value' property.",
            )
        if not isinstance(parsed["value"], list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported JSON structure: 'value' property must be an array of records.",
            )
        records = parsed["value"]
        # Extract envelope metadata
        for key, val in parsed.items():
            if key != "value":
                metadata[key] = val

    elif isinstance(parsed, list):
        records = parsed
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported JSON structure: root element must be a JSON object or array.",
        )

    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported JSON structure: record at index {idx} is not an object.",
            )

    columns: list[str] = []
    for record in records:
        for col in record.keys():
            if col not in columns:
                columns.append(col)

    total_rows = len(records)
    total_columns = len(columns)

    return {
        "filename": target_path.name,
        "file_format": "json",
        "total_rows": total_rows,
        "total_columns": total_columns,
        "columns": columns,
        "metadata": metadata,
        "parsing_status": "success",
        "message": f"Successfully parsed {total_rows} records with {total_columns} columns.",
    }


def extract_records_from_file(target_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    """Extract raw row dictionaries, metadata envelope, and columns from JSON/CSV without mutating source."""
    suffix = target_path.suffix.lower()
    if suffix == ".json":
        raw_bytes = target_path.read_bytes()
        if not raw_bytes:
            return [], {}, []
        try:
            text = raw_bytes.decode("utf-8-sig")
            parsed = json.loads(text)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read JSON file: {err}",
            ) from err

        metadata: dict[str, Any] = {}
        records: list[dict[str, Any]] = []

        if isinstance(parsed, dict):
            if "value" in parsed and isinstance(parsed["value"], list):
                records = parsed["value"]
                for k, v in parsed.items():
                    if k != "value":
                        metadata[k] = v
            else:
                records = [parsed]
        elif isinstance(parsed, list):
            records = [r for r in parsed if isinstance(r, dict)]

        columns: list[str] = []
        for r in records:
            for k in r.keys():
                if k not in columns:
                    columns.append(k)

        return records, metadata, columns

    elif suffix == ".csv":
        raw_bytes = target_path.read_bytes()
        if not raw_bytes:
            return [], {}, []
        text = decode_csv_bytes(raw_bytes)
        non_empty_lines = [line for line in text.splitlines() if line.strip()]
        if not non_empty_lines:
            return [], {}, []

        first_line = non_empty_lines[0]
        delimiter = ";" if first_line.count(";") > first_line.count(",") else ","

        f_stream = io.StringIO(text)
        reader = csv.DictReader(f_stream, delimiter=delimiter)
        raw_fields = reader.fieldnames or []
        columns = [f.strip() for f in raw_fields if f and f.strip()]

        records = []
        for row in reader:
            if not row or not any(str(v).strip() for v in row.values() if v is not None):
                continue
            cleaned_row = {
                (k.strip() if k else f"col_{idx}"): (v.strip() if isinstance(v, str) else v)
                for idx, (k, v) in enumerate(row.items())
                if k and k.strip()
            }
            records.append(cleaned_row)

        return records, {}, columns

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{suffix}'. Only .json and .csv are supported.",
        )


def parse_assessment_file(filename: str, upload_dir: Path) -> dict[str, Any]:
    """Dispatch file parsing based on extension without altering source content."""
    target_path = validate_and_resolve_file(filename, upload_dir)
    suffix = target_path.suffix.lower()

    if suffix == ".json":
        return parse_json_file(target_path)
    elif suffix == ".csv":
        return parse_csv_file(target_path)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{suffix}'. Only .json and .csv are supported.",
        )
