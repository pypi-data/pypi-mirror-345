from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_302_FOUND, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from starlette.requests import Request
from starlette.datastructures import UploadFile
from uvicorn import run
from typing import Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from json import loads
from textwrap import dedent
from html import escape
from re import match
from authbase import setup_authbase, send_email, User
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pathlib import Path

this_file_directory = Path(__file__).parent

app = FastAPI()
engine = create_engine('sqlite:///formflow.db')
setup_authbase(app, engine)

@app.post("/email", response_class=HTMLResponse)
async def contact(
    request: Request,
    user_id: str = Form(),
    redirect: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
):
    if redirect and "\n" in redirect:
        return HTMLResponse("Redirect URL is invalid.", status_code=HTTP_400_BAD_REQUEST)

    if subject and "\n" in subject:
        return HTMLResponse("Subject is invalid.", status_code=HTTP_400_BAD_REQUEST)

    multipart_data = MIMEMultipart()

    origin = (request.headers.get("origin") or request.headers.get("host")).split("/",maxsplit=2)[-1]

    html = dedent(f"""
        <!doctype html>
        <meta charset="UTF-8">
        <style>
            table {{ border-collapse: collapse; margin: 1em 0; }}
            th, td {{ border: 1px solid #999; padding: 1em; }}
        </style>
        <h1>Response from {escape(origin)}</h1>
        <table>
    """)

    files = []

    async with request.form() as form:
        for key, value in form.multi_items():
            if key in ["user_id", "redirect", "subject"]:
                continue
            if isinstance(value, UploadFile):
                if value.size > 0:
                    files.append(value)
            else:
                html += f"<tr><th>{escape(key)}</th><td>{escape(value)}</td></tr>"
    html += "</table>"

    if not subject:
        subject = "FormFlow: New Form Submission"

    with Session(engine) as session:
        try:
            user = session.query(User).get(user_id)
        except:
            return HTMLResponse("Unknown user.", status_code=HTTP_400_BAD_REQUEST)

    send_email(user.email, subject, html, files)

    if redirect:
        return RedirectResponse(redirect, status_code=HTTP_302_FOUND)
    return "<p style='text-align: center'>Your message has been sent.</p>"

app.mount("/", StaticFiles(directory=str(this_file_directory / "dist"), html=True), name="static")

def main():
    run("formflow:app", host="127.0.0.1", port=8000, reload=True)
