import sqlite3

def init_db():
    conn = sqlite3.connect("microfund.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS borrower_tbl(
        id INTEGER primary key autoincrement,
        name TEXT not null,
        email TEXT,
        location TEXT not null,
        business_type TEXT not null,
        business_stage TEXT not null,
        loan_goal TEXT not null,
        sales DECIMAL (20,2) not null,
        income_freqruency TEXT not null,
        has_employees TEXT not null CHECK (has_employees IN ('yes', 'no')),
        essay TEXT not null,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def insert_borrower(name, email, location, business_type, business_stage, loan_goal, sales, income_freqruency, has_employees, essay):
    conn = sqlite3.connect("microfund.db")
    c = conn.cursor()
    c.execute("""
    INSERT INTO borrower_tbl (name, email, location, business_type, business_stage, loan_goal, sales, income_freqruency, has_employees, essay) 
              VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (name, email, location, business_type, business_stage, loan_goal, sales, income_freqruency, has_employees, essay))
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