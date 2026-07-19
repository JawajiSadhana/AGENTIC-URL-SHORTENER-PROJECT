from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .db import SessionLocal, URL
import string, random
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="Agentic URL Shortener")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

def gen_code(n=6): 
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

@app.post("/shorten")
@limiter.limit("10/minute")
def shorten(url: str, request: Request, db: Session = Depends(get_db)):
    code = gen_code()
    db_url = URL(short_code=code, original_url=url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return {"short_url": f"http://localhost:8000/{code}", "code": code}  # <-- code bhi return kar diya

@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == code).first()
    if not url: 
        raise HTTPException(status_code=404, detail="URL not found")
    url.clicks += 1
    db.commit()
    return RedirectResponse(url.original_url)

@app.get("/analytics/{code}")
def analytics(code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == code).first()
    if not url: 
        raise HTTPException(status_code=404, detail="URL not found")
    return {"short_code": code, "clicks": url.clicks, "original": url.original_url}