"""Document Repository routes."""

import os

from fastapi import APIRouter, Request
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import Optional

from . import db_service, get_auth_context, check_permission

router = APIRouter()


class DocumentUploadRequest(BaseModel):
    document_name: str = "New Institutional Document"
    category: str = "Protocol"
    trial_ctri: str = ""
    version: str = "v1.0"
    status: str = "Under Review"
    description: str = ""
    file_name: Optional[str] = None
    file_content: Optional[str] = None


class DocumentVersionRequest(BaseModel):
    version: str = "v1.1"
    change_summary: str = "Routine periodic version update."
    status: str = "Approved"
    file_name: Optional[str] = None
    file_content: Optional[str] = None


@router.get("/documents/summary")
async def get_documents_summary():
    return db_service.get_documents_summary()


@router.get("/documents")
async def get_documents(
    category: str = "", search: str = "", trial_ctri: str = "",
    status: str = "", page: int = 1, limit: int = 20,
):
    return db_service.get_documents(
        category=category, search=search, trial_ctri=trial_ctri,
        status=status, page=page, limit=limit,
    )


@router.get("/documents/{doc_id}/download")
async def download_document(doc_id: str, version: str = "", request: Request = None):
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", ""),
        x_session_token=request.headers.get("X-Session-Token", ""),
        x_active_role=request.headers.get("X-Active-Role", ""),
        request=request,
    )
    perm_err = check_permission(auth, "documents:read")
    if perm_err:
        return JSONResponse(perm_err, status_code=403)

    doc_file = db_service.get_document_file_path(doc_id, version=version if version else None)
    if not doc_file or not os.path.exists(doc_file["file_path"]):
        return JSONResponse({"error": "Document file not found in secure repository."}, status_code=404)

    db_service.log_audit_event(
        user_name=auth["user_name"], role=auth["role"],
        action="DOWNLOAD_DOCUMENT", entity="DocumentRepository",
        entity_id=doc_file["doc_id"], previous_value="Stored Securely",
        new_value=f"Downloaded {doc_file['file_name']} (v{doc_file['version']}) - SHA256: {doc_file['checksum_sha256'][:12]}...",
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    with open(doc_file["file_path"], "rb") as f:
        file_bytes = f.read()

    return Response(
        content=file_bytes,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{doc_file["file_name"]}"',
            "X-Document-ID": doc_file["doc_id"],
            "X-Document-Checksum": doc_file["checksum_sha256"],
        },
    )


@router.get("/documents/{doc_id}")
async def get_document_detail(doc_id: str):
    doc_detail = db_service.get_document_detail(doc_id)
    if doc_detail:
        return doc_detail
    return JSONResponse({"error": "Document not found"}, status_code=404)


@router.post("/documents/upload")
async def upload_document(body: DocumentUploadRequest, request: Request = None):
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", "") if request else "",
        x_session_token=request.headers.get("X-Session-Token", "") if request else "",
        x_active_role=request.headers.get("X-Active-Role", "") if request else "",
        request=request,
    )
    perm_err = check_permission(auth, "documents:write", method="POST")
    if perm_err:
        return JSONResponse(perm_err, status_code=403)

    file_name = body.file_name or f"{body.document_name.replace(' ', '_')}.pdf"
    file_content_raw = body.file_content or f"Institutional Record: {body.document_name}\nCategory: {body.category}\nVersion: {body.version}\n"
    file_bytes = file_content_raw.encode("utf-8")

    return db_service.create_document(
        document_name=body.document_name, category=body.category,
        trial_ctri=body.trial_ctri, version=body.version,
        uploaded_by=auth.get("user_name", "Prof. (Dr.) Tanuja Nesari"),
        status=body.status, description=body.description,
        file_name=file_name, file_content_bytes=file_bytes,
    )


@router.post("/documents/{doc_id}/version")
async def add_document_version(doc_id: str, body: DocumentVersionRequest, request: Request = None):
    auth = get_auth_context(
        authorization=request.headers.get("Authorization", "") if request else "",
        x_session_token=request.headers.get("X-Session-Token", "") if request else "",
        x_active_role=request.headers.get("X-Active-Role", "") if request else "",
        request=request,
    )
    perm_err = check_permission(auth, "documents:write", method="POST")
    if perm_err:
        return JSONResponse(perm_err, status_code=403)

    file_name = body.file_name or f"Document_Update_{body.version}.pdf"
    file_content_raw = body.file_content or f"Updated Document Version: {body.version}\nSummary: {body.change_summary}\n"
    file_bytes = file_content_raw.encode("utf-8")

    return db_service.add_document_version(
        document_id=doc_id, version=body.version,
        change_summary=body.change_summary,
        uploaded_by=auth.get("user_name", "Principal Investigator"),
        status=body.status, file_name=file_name,
        file_content_bytes=file_bytes,
    )
