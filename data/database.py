import sqlite3
import os
import uuid

def init_db():
    conn = sqlite3.connect("microfund.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS borrower_tbl(
        id INTEGER primary key autoincrement,
        name TEXT not null,
        email TEXT DEFAULT "No Email",
        location TEXT not null,
        business_type TEXT not null,
        business_stage TEXT not null,
        loan_goal TEXT not null,
        sales DECIMAL (20,2) not null,
        income_freqruency TEXT not null,
        has_employees TEXT not null CHECK (has_employees IN ('yes', 'no')),
        essay TEXT not null,
        timestamp DATETIME not null DEFAULT CURRENT_TIMESTAMP,
        bank_num TEXT not null,
        valid_id TEXT,
        business_permit TEXT,
        bank_statement TEXT,
        income_tax_file TEXT,
        collateral TEXT not null DEFAULT "No Collateral"
    )
    """)
    conn.commit()
    conn.close()

def insert_borrower(
    name, email, location, business_type, business_stage, loan_goal, sales, 
    income_freqruency, has_employees, essay, bank_num, collateral):

    conn = sqlite3.connect("microfund.db")
    c = conn.cursor()
    c.execute("""
    INSERT INTO borrower_tbl (
        name, email, location, business_type, business_stage, loan_goal, sales,
        income_freqruency, has_employees, essay, bank_num, collateral
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, email, location, business_type, business_stage, loan_goal, sales,
        income_freqruency, has_employees, essay, bank_num, collateral
    ))
    borrower_id = c.lastrowid
    conn.commit()
    conn.close()
    return borrower_id

def save_file_to_data(uploaded_file, borrower_id, subfolder="data"):
    folder_path = os.path.join(subfolder, f"borrower_{borrower_id}")
    os.makedirs(folder_path, exist_ok=True)

    file_ext = os.path.splitext(uploaded_file.name)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    save_path = os.path.join(folder_path, unique_filename)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    return os.path.relpath(save_path)

def update_borrower_files(id, valid_id, business_permit, bank_statement, income_tax_file):
    conn = sqlite3.connect("microfund.db")
    c = conn.cursor()
    c.execute("""
        UPDATE borrower_tbl
        SET valid_id = ?, business_permit = ?, bank_statement = ?, income_tax_file = ?
        WHERE id = ?
    """, (valid_id, business_permit, bank_statement, income_tax_file, id))
    conn.commit()
    conn.close()

def get_all_submissions():
    conn = sqlite3.connect("microfund.db")
    c = conn.cursor()
    c.execute("SELECT * FROM borrower_tbl ORDER BY timestamp DESC")
    data = c.fetchall()
    conn.close()
    return data

def get_id(id): 
    conn = sqlite3.connect("microfund.db")
    c = conn.cursor()
    c.execute("SELECT * FROM borrower_tbl where id = ?", (id,))
    borrower_data = c.fetchone()
    conn.close()
    return borrower_data

def search_name(name):
    conn = sqlite3.connect("microfund.db")
    c = conn.cursor()
    c.execute("SELECT * FROM borrower_tbl WHERE name LIKE ? ORDER BY timestamp DESC", (f"%{name}%",))
    s_name = c.fetchall()
    conn.close()
    return s_name

def delete_user(id):
    conn = sqlite3.connect("microfund.db")
    c = conn.cursor()
    c.execute("DELETE FROM borrower_tbl WHERE id = ?", (id,))
    conn.commit()
    conn.close()