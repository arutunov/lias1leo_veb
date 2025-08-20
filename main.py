from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.crud import (
    create_transaction,
    delete_transaction,
    get_stats,
    get_transaction,
    get_transactions,
)
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Tracker")

app.mount("/static", StaticFiles(directory="./app/static"), name="static")
templates = Jinja2Templates(directory="./app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    stats = get_stats(db)
    recent_transactions = get_transactions(db, limit=5)
    return templates.TemplateResponse(
        "index.html", {"request": request, "stats": stats, "transactions": recent_transactions}
    )


@app.get("/transactions", response_class=HTMLResponse)
async def read_transactions(request: Request, db: Session = Depends(get_db)):
    transactions = get_transactions(db)
    return templates.TemplateResponse(
        "transactions.html", {"request": request, "transactions": transactions}
    )


@app.get("/add-transaction", response_class=HTMLResponse)
async def add_transaction_form(request: Request):
    return templates.TemplateResponse("add_transaction.html", {"request": request})


@app.post("/add-transaction", response_class=HTMLResponse)
async def add_transaction(
    request: Request,
    type: str = Form(...),
    amount: float = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    transaction_data = {"type": type, "amount": amount, "description": description}
    create_transaction(db, transaction_data)
    return RedirectResponse(url="/transactions", status_code=303)


@app.get("/stats", response_class=HTMLResponse)
async def read_stats(request: Request, db: Session = Depends(get_db)):
    stats = get_stats(db)
    return templates.TemplateResponse("stats.html", {"request": request, "stats": stats})


# HTMX endpoints
@app.delete("/transaction/{transaction_id}")
async def delete_transaction_htmx(transaction_id: int, db: Session = Depends(get_db)):
    success = delete_transaction(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return ""


@app.get("/transaction/{transaction_id}", response_class=HTMLResponse)
async def get_transaction_htmx(
    transaction_id: int, request: Request, db: Session = Depends(get_db)
):
    transaction = get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return templates.TemplateResponse(
        "transaction_row.html", {"request": request, "transaction": transaction}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
