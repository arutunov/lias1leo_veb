from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Transaction


def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transaction).order_by(desc(Transaction.date)).offset(skip).limit(limit).all()


def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def create_transaction(db: Session, transaction_data: dict):
    db_transaction = Transaction(**transaction_data)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def update_transaction(db: Session, transaction_id: int, transaction_data: dict):
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if db_transaction:
        for key, value in transaction_data.items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: int):
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return True
    return False


def get_stats(db: Session) -> dict[str, int | float]:
    transactions = db.query(Transaction).all()
    total_income = sum(float(t.amount) for t in transactions if str(t.type) == "income")
    total_expense = sum(float(t.amount) for t in transactions if str(t.type) == "expense")
    balance = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "transaction_count": len(transactions),
    }
