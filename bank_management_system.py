import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import random
import time
from datetime import datetime

# ====================================================================
# 1. DATABASE MANAGEMENT CLASS
# ====================================================================
class DatabaseManager:
    def __init__(self, db_name="mybankingdb.db"):
        self.conn = None
        self.db_name = db_name
        self.connect()
        self.create_tables()

    def connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {e}")
            self.conn = None
            exit() 

    def create_tables(self):
        """Ensures all necessary tables exist in the database."""
        if not self.conn: return

        cursor = self.conn.cursor()
        
        # --- Core Tables ---
        cursor.execute("CREATE TABLE IF NOT EXISTS login(username TEXT PRIMARY KEY, password TEXT NOT NULL)")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer(
                accno TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, contacts TEXT NOT NULL, 
                emails TEXT, address TEXT, amounts REAL NOT NULL, datess TEXT, idtypes TEXT, 
                idnos TEXT, genders TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                trans_id INTEGER PRIMARY KEY AUTOINCREMENT, accno TEXT NOT NULL, name TEXT NOT NULL, 
                contactno TEXT, old_amount REAL NOT NULL, datess TEXT NOT NULL, trans_money REAL NOT NULL, 
                balance REAL NOT NULL, type TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee(
                empid TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, contact TEXT NOT NULL, 
                email TEXT, address TEXT, job TEXT, salary REAL, dates TEXT, idtype TEXT, 
                idno TEXT, gender TEXT
            )
        """)
        
        # --- New Management Tables ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints(
                compid INTEGER PRIMARY KEY AUTOINCREMENT, accno TEXT, subject TEXT NOT NULL, 
                details TEXT NOT NULL, datess TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestions(
                suggid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, contact TEXT, 
                subject TEXT NOT NULL, details TEXT NOT NULL, datess TEXT NOT NULL
            )
        """)
        
        self.conn.commit()

    def execute_query(self, query, params=()):
        """Handles SELECT queries and returns results."""
        if not self.conn: return []
        try:
            cursor = self.conn.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Query failed: {e}")
            return []

    def execute_dml(self, query, params=()):
        """Handles INSERT, UPDATE, DELETE queries."""
        if not self.conn: return False
        try:
            self.conn.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Database Error", "Integrity error (e.g., duplicate ID).")
            return False
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Operation failed: {e}")
            return False

# ====================================================================
# 2. HELPER FUNCTIONS
# ====================================================================

def generate_unique_acc_no(db_manager):
    """Generates a unique 8-digit account number."""
    while True:
        acc_no = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        result = db_manager.execute_query("SELECT accno FROM customer WHERE accno=?", (acc_no,))
        if not result:
            return acc_no

def validate_numeric_input(value, field_name):
    """Checks if a string is a valid positive number."""
    try:
        num = float(value)
        if num < 0:
            messagebox.showerror("Input Error", f"{field_name} cannot be negative.")
            return None
        return num
    except ValueError:
        messagebox.showerror("Input Error", f"{field_name} must be a valid number.")
        return None

# ====================================================================
# 3. ROOT WINDOW AND DATABASE SETUP
# ====================================================================
win = tk.Tk()
win.title("Banking Management System - COMPLETE")
win.geometry("1000x700")

db_manager = DatabaseManager()

# ====================================================================
# 4. STRINGVAR DECLARATIONS
# ====================================================================
current_date = datetime.now().strftime("%Y-%m-%d")

# Login Variables
login_user = tk.StringVar()
login_pass = tk.StringVar()

# Employee Variables
emp_no = tk.StringVar()
emp_name = tk.StringVar()
emp_contact = tk.StringVar()
emp_email = tk.StringVar()
emp_address = tk.StringVar()
emp_job = tk.StringVar()
emp_salary = tk.StringVar()

# Customer/Transaction Variables
cust_acno = tk.StringVar()
cust_name = tk.StringVar()
cust_contact = tk.StringVar()
cust_email = tk.StringVar()
cust_address = tk.StringVar()
cust_amount = tk.StringVar()
cust_dates = tk.StringVar(value=current_date)
cust_idtype = tk.StringVar()
cust_idno = tk.StringVar()
cust_gender = tk.StringVar()
trans_money = tk.StringVar()
trans_balance = tk.StringVar()

# Complaint/Suggestion Variables (New)
comp_accno = tk.StringVar()
comp_subject = tk.StringVar()
comp_details = tk.StringVar()
sugg_name = tk.StringVar()
sugg_contact = tk.StringVar()
sugg_subject = tk.StringVar()
sugg_details = tk.StringVar()


# ====================================================================
# 5. FRAME CREATION
# ====================================================================

# Create all frames
lgframe = tk.Frame(win)
mnframe = tk.Frame(win)
acframe = tk.Frame(win)
ncframe = tk.Frame(win)
wcframe = tk.Frame(win)
dcframe = tk.Frame(win)
neframe = tk.Frame(win)
# Updated Frames
comframe = tk.Frame(win)
suggframe = tk.Frame(win)
# New Reporting/Listing Frames
comp_list_frame = tk.Frame(win)
sugg_list_frame = tk.Frame(win)
allcustframe = tk.Frame(win) 
thankframe = tk.Frame(win)

# Initial frame setup
win.grid_columnconfigure(0, weight=1)
win.grid_rowconfigure(0, weight=1)
lgframe.grid(row=0, column=0, sticky="nsew") 

def show_frame(frame_to_show):
    """Hides all frames and shows the specified one."""
    all_frames = [
        lgframe, mnframe, acframe, ncframe, wcframe, dcframe, neframe, 
        comframe, suggframe, thankframe, allcustframe, comp_list_frame, sugg_list_frame
    ]
    
    for frame in all_frames:
        frame.grid_forget()
        # Reset Treeview frames when leaving them
        if frame == allcustframe:
            for item in customer_tree.get_children(): customer_tree.delete(item)
        if frame == comp_list_frame:
            for item in complaint_tree.get_children(): complaint_tree.delete(item)
        if frame == sugg_list_frame:
            for item in suggestion_tree.get_children(): suggestion_tree.delete(item)
                
    frame_to_show.grid(row=0, column=0, sticky="nsew")

# ====================================================================
# 6. NAVIGATION & MANAGEMENT FUNCTIONS
# ====================================================================

# Back/Exit functions
def exits(): win.quit()
def lgback(): show_frame(lgframe)
def mnback(): show_frame(mnframe)
def cutback(): show_frame(acframe)
def wcback(): show_frame(acframe)
def dcsback(): show_frame(acframe)
def Empback(): show_frame(mnframe)
def acaccount(): show_frame(acframe)
def newEmployee(): show_frame(neframe)
def cust_list_back(): show_frame(acframe)

# Complaint/Suggestion Navigation
def comshow(): show_frame(comframe)
def suggshow(): show_frame(suggframe)
def submit_comp_back(): show_frame(mnframe)
def submit_sugg_back(): show_frame(mnframe)
def list_comp_back(): show_frame(mnframe)
def list_sugg_back(): show_frame(mnframe)


# --- Login Functions (Same as previous) ---
def reset_login():
    login_user.set("")
    login_pass.set("")

def signup():
    username = login_user.get()
    password = login_pass.get()
    if not username or not password:
        messagebox.showinfo("Banking Management", "Please enter both username and password.")
        return
    query = "INSERT INTO login VALUES(?, ?)"
    if db_manager.execute_dml(query, (username, password)):
        messagebox.showinfo("Banking Management", "You are now a registered User.")

def signin():
    username = login_user.get()
    password = login_pass.get()
    if not username or not password:
        messagebox.showinfo("Banking Management", "Please enter both username and password.")
        return
    query = "SELECT * FROM login WHERE username=? AND password=?"
    if db_manager.execute_query(query, (username, password)):
        messagebox.showinfo("Banking Management", "Login successful. Welcome administrator.")
        show_frame(mnframe)
    else:
        messagebox.showinfo("Banking Management", "Invalid username or password.")

# --- Customer CRUD/Transaction Functions (Same as previous) ---
# (ncreset, ncsave, ncsearch, ncdelete, ncupdate, trans_reset, trans_search, wcsave, dcsave, Empreset, Empsave, Empupdate, Empdelete, Empsearch)
# ... (These functions remain as they were in the previous complete code block) ...

def ncreset():
    cust_acno.set("")
    cust_name.set("")
    cust_contact.set("")
    cust_email.set("")
    cust_address.set("")
    cust_amount.set("")
    cust_dates.set(datetime.now().strftime("%Y-%m-%d"))
    cust_idtype.set("")
    cust_idno.set("")
    cust_gender.set("")

def ncsave():
    acno = generate_unique_acc_no(db_manager) 
    amount_validated = validate_numeric_input(cust_amount.get(), "Amount")
    
    if amount_validated is None: return
    
    data = (
        acno, cust_name.get(), cust_contact.get(), cust_email.get(), cust_address.get(), 
        amount_validated, cust_dates.get(), cust_idtype.get(), cust_idno.get(), cust_gender.get()
    )

    if any(not d for d in data[1:]): 
        messagebox.showinfo("Banking Management", "Please fill in all the fields.")
        return

    query = "INSERT INTO customer VALUES(?,?,?,?,?,?,?,?,?,?)"
    if db_manager.execute_dml(query, data):
        messagebox.showinfo("Banking Management", f"New Customer Registered. Account No: {acno}")
        ncreset()

def ncsearch():
    acno1 = cust_acno.get()
    if not acno1:
        messagebox.showinfo("Banking Management system", "Please enter the account number.")
        return
    
    query = "SELECT * FROM customer WHERE accno=?"
    row = db_manager.execute_query(query, (acno1,))
    
    if row:
        row = row[0]
        cust_name.set(row[1])
        cust_contact.set(row[2])
        cust_email.set(row[3])
        cust_address.set(row[4])
        cust_amount.set(row[5])
        cust_dates.set(row[6])
        cust_idtype.set(row[7])
        cust_idno.set(row[8])
        cust_gender.set(row[9])
        messagebox.showinfo("Banking management", "Record Found.")
    else:
        messagebox.showinfo("Banking management", "Record not found.")

def ncdelete():
    acno1 = cust_acno.get()
    if not acno1:
        messagebox.showinfo("Banking Management", "Please enter the account number.")
        return
    
    if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete account {acno1}?"):
        query = "DELETE FROM customer WHERE accno=?"
        if db_manager.execute_dml(query, (acno1,)):
            messagebox.showinfo("Banking Management", "Record Deleted.")
            ncreset()

def ncupdate():
    amount_validated = validate_numeric_input(cust_amount.get(), "Amount")
    if amount_validated is None: return

    data = (
        cust_name.get(), cust_contact.get(), cust_email.get(), cust_address.get(), 
        amount_validated, cust_dates.get(), cust_idtype.get(), cust_idno.get(), cust_gender.get(), cust_acno.get()
    )

    if any(not d for d in data[:-1]):
        messagebox.showinfo("Banking Management", "Please fill in all the fields.")
        return

    query = """
        UPDATE customer SET 
            name=?, contacts=?, emails=?, address=?, amounts=?, datess=?, 
            idtypes=?, idnos=?, genders=? 
        WHERE accno=?
    """
    if db_manager.execute_dml(query, data):
        messagebox.showinfo("Customer Record", "Record Updated.")

def seeallcust():
    show_frame(allcustframe)
    for item in customer_tree.get_children():
        customer_tree.delete(item)

    query = "SELECT accno, name, contacts, amounts FROM customer"
    rows = db_manager.execute_query(query)
    
    for row in rows:
        customer_tree.insert('', 'end', values=row)

def trans_reset():
    cust_acno.set("")
    cust_name.set("")
    cust_contact.set("")
    cust_amount.set("")
    cust_dates.set(datetime.now().strftime("%Y-%m-%d"))
    trans_money.set("")
    trans_balance.set("")

def trans_search(frame_type):
    acno1 = cust_acno.get() 
    if not acno1:
        messagebox.showinfo(frame_type, "Please enter account number.")
        return
    
    query = "SELECT * FROM customer WHERE accno=?"
    row = db_manager.execute_query(query, (acno1,))
    
    if row:
        row = row[0]
        cust_name.set(row[1])
        cust_contact.set(row[2])
        cust_amount.set(row[5]) 
        messagebox.showinfo(frame_type, "Record Found.")
    else:
        messagebox.showinfo(frame_type, "Record not found.")

def wcsearch(): trans_search("Withdrawal")
def dcsearch(): trans_search("Deposit")

def perform_transaction(trans_type):
    acno = cust_acno.get()
    if not acno:
        messagebox.showerror("Transaction Error", "Please search for an account first.")
        return

    try:
        current_amount = float(cust_amount.get())
    except ValueError:
        messagebox.showerror("Transaction Error", "Current Amount is missing or invalid.")
        return
        
    trans_value = validate_numeric_input(trans_money.get(), f"{trans_type} Money")
    if trans_value is None: return

    if trans_type == "Withdraw":
        if trans_value > current_amount:
            messagebox.showinfo("Banking Management", "Transaction not possible (Insufficient funds).")
            return
        new_balance = current_amount - trans_value
    else: # Deposit
        new_balance = current_amount + trans_value
    
    trans_balance.set(f"{new_balance:.2f}")

    update_query = "UPDATE customer SET amounts=? WHERE accno=?"
    if not db_manager.execute_dml(update_query, (new_balance, acno)):
        return

    log_data = (
        acno, cust_name.get(), cust_contact.get(), current_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        trans_value, new_balance, trans_type
    )
    log_query = "INSERT INTO transactions VALUES(NULL,?,?,?,?,?,?,?,?)"
    
    if db_manager.execute_dml(log_query, log_data):
        messagebox.showinfo("Banking management", f"Transaction ({trans_type}) Successful. Balance Updated.")
        cust_amount.set(f"{new_balance:.2f}")

def wcsave(): perform_transaction("Withdraw")
def dcsave(): perform_transaction("Deposit")

def Empreset():
    emp_no.set("")
    emp_name.set("")
    emp_contact.set("")
    emp_email.set("")
    emp_address.set("")
    emp_job.set("")
    emp_salary.set("")
    cust_dates.set(datetime.now().strftime("%Y-%m-%d"))
    cust_idtype.set("")
    cust_idno.set("")
    cust_gender.set("")

def Empsave():
    salary_validated = validate_numeric_input(emp_salary.get(), "Salary")
    if salary_validated is None: return
    
    data = (
        emp_no.get(), emp_name.get(), emp_contact.get(), emp_email.get(), emp_address.get(), 
        emp_job.get(), salary_validated, cust_dates.get(), cust_idtype.get(), cust_idno.get(), cust_gender.get()
    )
    
    if any(not d for d in data):
        messagebox.showinfo("Banking Management", "Please fill in all the fields.")
        return
    
    query = "INSERT INTO employee VALUES(?,?,?,?,?,?,?,?,?,?,?)"
    if db_manager.execute_dml(query, data):
        messagebox.showinfo("Banking Management", "Employee Registered.")

def Empupdate():
    salary_validated = validate_numeric_input(emp_salary.get(), "Salary")
    if salary_validated is None: return

    data = (
        emp_name.get(), emp_contact.get(), emp_email.get(), emp_address.get(), emp_job.get(), 
        salary_validated, cust_dates.get(), cust_idtype.get(), cust_idno.get(), cust_gender.get(), emp_no.get()
    )

    if any(not d for d in data[:-1]):
        messagebox.showinfo("Banking Management", "Please fill in all the fields.")
        return
        
    query = """
        UPDATE employee SET 
            name=?, contact=?, email=?, address=?, job=?, salary=?, dates=?, 
            idtype=?, idno=?, gender=? 
        WHERE empid=?
    """
    if db_manager.execute_dml(query, data):
        messagebox.showinfo("Employee Record", "Record Updated.")

def Empdelete():
    empno1 = emp_no.get()
    if not empno1:
        messagebox.showinfo("Employee Record", "Please enter the employee number.")
        return

    if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete employee {empno1}?"):
        query = "DELETE FROM employee WHERE empid=?"
        if db_manager.execute_dml(query, (empno1,)):
            messagebox.showinfo("Employee Info", "Record Deleted.")
            Empreset()

def Empsearch():
    empno1 = emp_no.get()
    if not empno1:
        messagebox.showinfo("Employee Record", "Please enter the employee number.")
        return

    query = "SELECT * FROM employee WHERE empid=?"
    row = db_manager.execute_query(query, (empno1,))
    
    if row:
        row = row[0]
        emp_name.set(row[1])
        emp_contact.set(row[2])
        emp_email.set(row[3])
        emp_address.set(row[4])
        emp_job.set(row[5])
        emp_salary.set(row[6])
        cust_dates.set(row[7]) 
        cust_idtype.set(row[8])
        cust_idno.set(row[9])
        cust_gender.set(row[10])
        messagebox.showinfo("Employee Record", "Record Found and loaded.")
    else:
        messagebox.showinfo("Employee Record", "Record not found.")


# ====================================================================
# 7. COMPLAINT MANAGEMENT FUNCTIONS (New)
# ====================================================================

def comp_reset():
    comp_accno.set("")
    comp_subject.set("")
    comp_details.set("")

def comp_save():
    acno = comp_accno.get()
    subject = comp_subject.get()
    details = comp_details.get("1.0", tk.END).strip()
    
    if not acno or not subject or not details:
        messagebox.showerror("Error", "Please fill in all fields.")
        return
        
    data = (acno, subject, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    query = "INSERT INTO complaints (accno, subject, details, datess) VALUES (?, ?, ?, ?)"
    
    if db_manager.execute_dml(query, data):
        messagebox.showinfo("Success", "Complaint submitted successfully. Status: Pending.")
        comp_reset()

def show_complaints():
    show_frame(comp_list_frame)
    for item in complaint_tree.get_children(): complaint_tree.delete(item)
        
    rows = db_manager.execute_query("SELECT compid, accno, subject, datess, status FROM complaints ORDER BY datess DESC")
    
    for row in rows:
        tag = 'pending' if row[4] == 'Pending' else 'resolved' if row[4] == 'Resolved' else 'in_progress'
        complaint_tree.insert('', 'end', values=row, tags=(tag,))

def update_comp_status(status):
    selected = complaint_tree.focus()
    if not selected:
        messagebox.showerror("Error", "Please select a complaint to update.")
        return
    
    comp_id = complaint_tree.item(selected, 'values')[0]
    
    query = "UPDATE complaints SET status=? WHERE compid=?"
    if db_manager.execute_dml(query, (status, comp_id)):
        messagebox.showinfo("Success", f"Complaint {comp_id} status updated to {status}.")
        show_complaints() # Refresh list

# ====================================================================
# 8. SUGGESTION MANAGEMENT FUNCTIONS (New)
# ====================================================================

def sugg_reset():
    sugg_name.set("")
    sugg_contact.set("")
    sugg_subject.set("")
    sugg_details.set("1.0", tk.END).strip() # Clear Text widget

def sugg_save():
    name = sugg_name.get()
    contact = sugg_contact.get()
    subject = sugg_subject.get()
    details = sugg_details_text.get("1.0", tk.END).strip()
    
    if not name or not subject or not details:
        messagebox.showerror("Error", "Please fill in all mandatory fields.")
        return
        
    data = (name, contact, subject, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    query = "INSERT INTO suggestions (name, contact, subject, details, datess) VALUES (?, ?, ?, ?, ?)"
    
    if db_manager.execute_dml(query, data):
        messagebox.showinfo("Success", "Suggestion submitted successfully.")
        sugg_reset()

def show_suggestions():
    show_frame(sugg_list_frame)
    for item in suggestion_tree.get_children(): suggestion_tree.delete(item)
        
    rows = db_manager.execute_query("SELECT suggid, name, contact, subject, datess FROM suggestions ORDER BY datess DESC")
    
    for row in rows:
        suggestion_tree.insert('', 'end', values=row)

# ====================================================================
# 9. FRAME LAYOUTS
# ====================================================================

# --- LOGIN FRAME (Same as previous) ---
tk.Label(lgframe, text="BANKING MANAGEMENT SYSTEM", bg='black', fg='white', font=('mangal', 40, 'bold')).grid(row=0, columnspan=5, pady=20, sticky="ew")
tk.Label(lgframe, text="ADMIN LOGIN", font=('arial', 30, 'bold'), bg="steel blue").grid(row=3, columnspan=5, pady=10, sticky="ew")
tk.Label(lgframe, text="Username", font=('arial', 20, 'bold')).grid(row=5, column=1, sticky='e', padx=10, pady=10)
e1 = tk.Entry(lgframe, textvariable=login_user, bg="steelblue", bd=5, font=('arial', 20, 'bold'), fg='white')
e1.grid(row=5, column=2, columnspan=2, padx=10, pady=10, sticky='ew')
tk.Label(lgframe, text="Password", font=('arial', 20, 'bold')).grid(row=6, column=1, sticky='e', padx=10, pady=10)
e2 = tk.Entry(lgframe, textvariable=login_pass, show="*", bg="steelblue", bd=5, font=('arial', 20, 'bold'), fg='white')
e2.grid(row=6, column=2, columnspan=2, padx=10, pady=10, sticky='ew')
tk.Button(lgframe, text="Sign Up", font=('arial', 15, 'bold'), bd=5, bg="cyan", command=signup).grid(row=10, column=2, pady=10, sticky='ew', padx=5)
tk.Button(lgframe, text="Sign In", font=('arial', 15, 'bold'), bd=5, bg="cyan", command=signin).grid(row=10, column=3, pady=10, sticky='ew', padx=5)
tk.Button(lgframe, text="Reset", font=('arial', 15, 'bold'), bd=5, bg="cyan", command=reset_login).grid(row=10, column=4, pady=10, sticky='ew', padx=5)
for i in range(1, 5): lgframe.grid_columnconfigure(i, weight=1)

# --- MAIN MENU FRAME ---
tk.Label(mnframe, text="WELCOME TO BANKING SYSTEM", bg='black', fg='white', font=('arial', 40, 'bold')).pack(pady=30, fill='x')
tk.Button(mnframe, text="Customer Management", font=('arial', 20, 'bold'), bd=10, bg="cyan", command=acaccount, width=25).pack(pady=10)
tk.Button(mnframe, text="Employee Management", font=('arial', 20, 'bold'), bd=10, bg="cyan", command=newEmployee, width=25).pack(pady=10)
tk.Button(mnframe, text="Submit Complaint", font=('arial', 20, 'bold'), bd=10, bg="light blue", command=comshow, width=25).pack(pady=5)
tk.Button(mnframe, text="View Complaints", font=('arial', 20, 'bold'), bd=10, bg="steel blue", fg='white', command=show_complaints, width=25).pack(pady=5)
tk.Button(mnframe, text="Submit Suggestion", font=('arial', 20, 'bold'), bd=10, bg="light yellow", command=suggshow, width=25).pack(pady=5)
tk.Button(mnframe, text="View Suggestions", font=('arial', 20, 'bold'), bd=10, bg="gold", command=show_suggestions, width=25).pack(pady=5)
tk.Button(mnframe, text="Exit", font=('arial', 20, 'bold'), bd=10, bg="red", fg="white", command=exits, width=25).pack(pady=10)
tk.Button(mnframe, text="Back (Logout)", font=('arial', 20, 'bold'), bd=10, bg="orange", command=lgback, width=25).pack(pady=10)

# --- CUSTOMER ACCOUNT MENU FRAME (acframe) ---
tk.Label(acframe, text="CUSTOMER ACCOUNT MANAGEMENT", bd=10, bg='black', fg='white', font=('arial', 40, 'bold')).pack(pady=30, fill='x')
tk.Button(acframe, text="Create/Manage Account", font=('arial', 20, 'bold'), bd=10, bg="cyan", command=lambda: show_frame(ncframe), width=25).pack(pady=10)
tk.Button(acframe, text="Withdrawal Money", font=('arial', 20, 'bold'), bd=10, bg="cyan", command=lambda: show_frame(wcframe), width=25).pack(pady=10)
tk.Button(acframe, text="Deposit Money", font=('arial', 20, 'bold'), bd=10, bg="cyan", command=lambda: show_frame(dcframe), width=25).pack(pady=10)
tk.Button(acframe, text="Show All Accounts", font=('arial', 20, 'bold'), bd=10, bg="cyan", command=seeallcust, width=25).pack(pady=10)
tk.Button(acframe, text="Back", font=('arial', 20, 'bold'), bd=10, bg="orange", command=mnback, width=25).pack(pady=10)
tk.Button(acframe, text="Exit", font=('arial', 20, 'bold'), bd=10, bg="red", fg="white", command=exits, width=25).pack(pady=10)

# --- ADD NEW CUSTOMER FRAME (ncframe) ---
ncframe.grid_columnconfigure(1, weight=1)
ncframe.grid_columnconfigure(3, weight=1)
tk.Label(ncframe, text='Add/Manage Customer', bg='black', fg='white', bd=10, font=('arial', 30, 'bold')).grid(row=0, columnspan=4, pady=20, sticky='ew')
fields = [
    ('Account no', cust_acno), ('Name', cust_name), ('Contact no', cust_contact), ('Email', cust_email),
    ('Address', cust_address), ('Amount', cust_amount), ('Date', cust_dates), ('Id Proof', cust_idtype),
    ('Id No', cust_idno), ('Gender', cust_gender)
]
for i, (text, var) in enumerate(fields):
    tk.Label(ncframe, text=text, bd=10, font=('arial', 15, 'bold')).grid(row=i + 2, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(ncframe, textvariable=var, bd=5, bg='pink', font=('arial', 15, 'bold'))
    entry.grid(row=i + 2, column=1, sticky='ew', padx=10, pady=5)

tk.Button(ncframe, text='Save', command=ncsave, bd=5, font=('arial', 15, 'bold'), bg='green', fg='white', width=10).grid(row=2, column=2, padx=10, pady=5)
tk.Button(ncframe, text='Update', command=ncupdate, bd=5, font=('arial', 15, 'bold'), bg='blue', fg='white', width=10).grid(row=3, column=2, padx=10, pady=5)
tk.Button(ncframe, text='Delete', command=ncdelete, bd=5, font=('arial', 15, 'bold'), bg='red', fg='white', width=10).grid(row=4, column=2, padx=10, pady=5)
tk.Button(ncframe, text='Search', command=ncsearch, bd=5, font=('arial', 15, 'bold'), bg='grey', width=10).grid(row=2, column=3, padx=10, pady=5)
tk.Button(ncframe, text='Reset', command=ncreset, bd=5, font=('arial', 15, 'bold'), bg='grey', width=10).grid(row=3, column=3, padx=10, pady=5)
tk.Button(ncframe, text='Back', command=cutback, bd=5, font=('arial', 15, 'bold'), bg='grey', width=10).grid(row=4, column=3, padx=10, pady=5)


# --- ALL CUSTOMER LIST FRAME (allcustframe) ---
tk.Label(allcustframe, text="All Customer Accounts", font=('arial', 30, 'bold'), bg='black', fg='white').pack(pady=20, fill='x')
customer_tree = ttk.Treeview(allcustframe, columns=('#1', '#2', '#3', '#4'), show='headings')
customer_tree.heading('#1', text='Account No'); customer_tree.column('#1', width=150, anchor='center')
customer_tree.heading('#2', text='Name'); customer_tree.column('#2', width=200, anchor='w')
customer_tree.heading('#3', text='Contact'); customer_tree.column('#3', width=150, anchor='center')
customer_tree.heading('#4', text='Balance'); customer_tree.column('#4', width=150, anchor='e')
customer_tree.pack(pady=10, padx=10, fill='both', expand=True)
tk.Button(allcustframe, text="Back to Customer Menu", command=cust_list_back, font=('arial', 15, 'bold'), bg='orange').pack(pady=10)


# --- WITHDRAWAL & DEPOSIT FRAMES (Same as previous) ---
# ... (Layouts for wcframe and dcframe remain the same) ...
# --- WITHDRAWAL FRAME (wcframe) ---
wcframe.grid_columnconfigure(1, weight=1)
tk.Label(wcframe, text='WithDrawal Money', bg='black', fg='white', font=('arial', 30, 'bold'), bd=10).grid(row=0, columnspan=4, pady=20, sticky='ew')
wc_fields = [
    ('Account no', cust_acno, False), ('Name', cust_name, True), ('Contact no', cust_contact, True), 
    ('Current Amount', cust_amount, True), ('Date', cust_dates, False), ('Withdrawal Money', trans_money, False), 
    ('New Balance', trans_balance, True)
]
for i, (text, var, readonly) in enumerate(wc_fields):
    tk.Label(wcframe, text=text, font=('arial', 15, 'bold')).grid(row=i + 2, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(wcframe, textvariable=var, bg="pink", bd=5, font=('arial', 15, 'bold'))
    if readonly: entry.config(state='readonly')
    entry.grid(row=i + 2, column=1, sticky='ew', padx=10, pady=5)

tk.Button(wcframe, text='Search', command=wcsearch, font=('arial', 15, 'bold'), bd=5, bg="grey", width=15).grid(row=2, column=2, padx=10, pady=5)
tk.Button(wcframe, text='WITHDRAW', command=wcsave, font=('arial', 15, 'bold'), bd=5, bg="red", fg='white', width=15).grid(row=6, column=2, padx=10, pady=5)
tk.Button(wcframe, text='Reset', command=trans_reset, font=('arial', 15, 'bold'), bd=5, bg="grey", width=15).grid(row=4, column=3, padx=10, pady=5)
tk.Button(wcframe, text='Back', command=wcback, font=('arial', 15, 'bold'), bd=5, bg="grey", width=15).grid(row=2, column=3, padx=10, pady=5)

# --- DEPOSIT FRAME (dcframe) ---
dcframe.grid_columnconfigure(1, weight=1)
tk.Label(dcframe, text='Deposit Money', bg='black', fg='white', font=('arial', 30, 'bold'), bd=10).grid(row=0, columnspan=4, pady=20, sticky='ew')
dc_fields = [
    ('Account no', cust_acno, False), ('Name', cust_name, True), ('Contact no', cust_contact, True), 
    ('Current Amount', cust_amount, True), ('Date', cust_dates, False), ('Deposit Money', trans_money, False), 
    ('New Balance', trans_balance, True)
]
for i, (text, var, readonly) in enumerate(dc_fields):
    tk.Label(dcframe, text=text, font=('arial', 15, 'bold')).grid(row=i + 2, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(dcframe, textvariable=var, bg="pink", bd=5, font=('arial', 15, 'bold'))
    if readonly: entry.config(state='readonly')
    entry.grid(row=i + 2, column=1, sticky='ew', padx=10, pady=5)

tk.Button(dcframe, text='Search', command=dcsearch, font=('arial', 15, 'bold'), bd=5, bg="grey", width=15).grid(row=2, column=2, padx=10, pady=5)
tk.Button(dcframe, text='DEPOSIT', command=dcsave, font=('arial', 15, 'bold'), bd=5, bg="green", fg='white', width=15).grid(row=6, column=2, padx=10, pady=5)
tk.Button(dcframe, text='Reset', command=trans_reset, font=('arial', 15, 'bold'), bd=5, bg="grey", width=15).grid(row=4, column=3, padx=10, pady=5)
tk.Button(dcframe, text='Back', command=dcsback, font=('arial', 15, 'bold'), bd=5, bg="grey", width=15).grid(row=2, column=3, padx=10, pady=5)


# --- NEW EMPLOYEE FRAME (neframe) ---
neframe.grid_columnconfigure(1, weight=1)
neframe.grid_columnconfigure(3, weight=1)
tk.Label(neframe, text='Add/Manage Employee', font=('arial', 30, 'bold'), bg='black', fg='white', bd=10).grid(row=0, columnspan=4, pady=20, sticky='ew')
emp_fields = [
    ('Emp no', emp_no), ('Name', emp_name), ('Contact no', emp_contact), ('Email', emp_email),
    ('Address', emp_address), ('Job', emp_job), ('Salary', emp_salary), ('Date of Birth', cust_dates),
    ('Id Proof', cust_idtype), ('Id No', cust_idno), ('Gender', cust_gender)
]
for i, (text, var) in enumerate(emp_fields):
    tk.Label(neframe, text=text, bd=5, font=('arial', 15, 'bold')).grid(row=i + 2, column=0, sticky='w', padx=10, pady=5)
    tk.Entry(neframe, textvariable=var, bd=5, bg="pink", font=('arial', 15, 'bold')).grid(row=i + 2, column=1, sticky='ew', padx=10, pady=5)

tk.Button(neframe, text='Save', command=Empsave, bd=5, font=('arial', 15, 'bold'), bg='green', fg='white', width=10).grid(row=2, column=2, padx=10, pady=5)
tk.Button(neframe, text='Update', command=Empupdate, bd=5, font=('arial', 15, 'bold'), bg='blue', fg='white', width=10).grid(row=3, column=2, padx=10, pady=5)
tk.Button(neframe, text='Delete', command=Empdelete, bd=5, font=('arial', 15, 'bold'), bg='red', fg='white', width=10).grid(row=4, column=2, padx=10, pady=5)
tk.Button(neframe, text='Search', command=Empsearch, bd=5, font=('arial', 15, 'bold'), bg='grey', width=10).grid(row=2, column=3, padx=10, pady=5)
tk.Button(neframe, text='Reset', command=Empreset, bd=5, font=('arial', 15, 'bold'), bg='grey', width=10).grid(row=3, column=3, padx=10, pady=5)
tk.Button(neframe, text='Back', command=Empback, bd=5, font=('arial', 15, 'bold'), bg='grey', width=10).grid(row=4, column=3, padx=10, pady=5)


# --- SUBMIT COMPLAINT FRAME (comframe) ---
comframe.grid_columnconfigure(1, weight=1)
tk.Label(comframe, text='Submit New Complaint', font=('arial', 30, 'bold'), bg='dark red', fg='white', bd=10).grid(row=0, columnspan=2, pady=20, sticky='ew')
tk.Label(comframe, text='Account No:', font=('arial', 15, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=5)
tk.Entry(comframe, textvariable=comp_accno, bd=5, font=('arial', 15)).grid(row=1, column=1, sticky='ew', padx=10, pady=5)
tk.Label(comframe, text='Subject:', font=('arial', 15, 'bold')).grid(row=2, column=0, sticky='w', padx=10, pady=5)
tk.Entry(comframe, textvariable=comp_subject, bd=5, font=('arial', 15)).grid(row=2, column=1, sticky='ew', padx=10, pady=5)
tk.Label(comframe, text='Details:', font=('arial', 15, 'bold')).grid(row=3, column=0, sticky='nw', padx=10, pady=5)
comp_details_text = tk.Text(comframe, height=5, width=40, bd=5, font=('arial', 15))
comp_details_text.grid(row=3, column=1, sticky='ew', padx=10, pady=5)
tk.Button(comframe, text='Submit Complaint', command=comp_save, font=('arial', 15, 'bold'), bg='red', fg='white').grid(row=4, column=1, sticky='ew', padx=10, pady=10)
tk.Button(comframe, text='Back to Menu', command=submit_comp_back, font=('arial', 15, 'bold')).grid(row=4, column=0, sticky='ew', padx=10, pady=10)


# --- VIEW COMPLAINTS FRAME (comp_list_frame) ---
tk.Label(comp_list_frame, text="COMPLAINT TRACKER", font=('arial', 30, 'bold'), bg='dark red', fg='white').pack(pady=20, fill='x')
# Treeview setup for complaints
complaint_tree = ttk.Treeview(comp_list_frame, columns=('#1', '#2', '#3', '#4', '#5'), show='headings')
complaint_tree.heading('#1', text='ID'); complaint_tree.column('#1', width=50, anchor='center')
complaint_tree.heading('#2', text='Acc No'); complaint_tree.column('#2', width=100, anchor='center')
complaint_tree.heading('#3', text='Subject'); complaint_tree.column('#3', width=250, anchor='w')
complaint_tree.heading('#4', text='Date'); complaint_tree.column('#4', width=150, anchor='center')
complaint_tree.heading('#5', text='Status'); complaint_tree.column('#5', width=100, anchor='center')
complaint_tree.tag_configure('pending', background='#FFAAAA', foreground='black') # Red background
complaint_tree.tag_configure('resolved', background='#AAFFAA', foreground='black') # Green background
complaint_tree.tag_configure('in_progress', background='#FFFFCC', foreground='black') # Yellow background
complaint_tree.pack(pady=10, padx=10, fill='both', expand=True)

comp_btn_frame = tk.Frame(comp_list_frame)
comp_btn_frame.pack(pady=10)
tk.Button(comp_btn_frame, text='Set Pending', command=lambda: update_comp_status('Pending'), font=('arial', 12), bg='orange').pack(side='left', padx=5)
tk.Button(comp_btn_frame, text='Set In Progress', command=lambda: update_comp_status('In Progress'), font=('arial', 12), bg='yellow').pack(side='left', padx=5)
tk.Button(comp_btn_frame, text='Set Resolved', command=lambda: update_comp_status('Resolved'), font=('arial', 12), bg='green', fg='white').pack(side='left', padx=5)
tk.Button(comp_btn_frame, text='Back to Menu', command=list_comp_back, font=('arial', 12), bg='grey', fg='white').pack(side='left', padx=15)


# --- SUBMIT SUGGESTION FRAME (suggframe) ---
suggframe.grid_columnconfigure(1, weight=1)
tk.Label(suggframe, text='Submit Suggestion', font=('arial', 30, 'bold'), bg='dark green', fg='white', bd=10).grid(row=0, columnspan=2, pady=20, sticky='ew')
tk.Label(suggframe, text='Name:', font=('arial', 15, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=5)
tk.Entry(suggframe, textvariable=sugg_name, bd=5, font=('arial', 15)).grid(row=1, column=1, sticky='ew', padx=10, pady=5)
tk.Label(suggframe, text='Contact (Optional):', font=('arial', 15, 'bold')).grid(row=2, column=0, sticky='w', padx=10, pady=5)
tk.Entry(suggframe, textvariable=sugg_contact, bd=5, font=('arial', 15)).grid(row=2, column=1, sticky='ew', padx=10, pady=5)
tk.Label(suggframe, text='Subject:', font=('arial', 15, 'bold')).grid(row=3, column=0, sticky='w', padx=10, pady=5)
tk.Entry(suggframe, textvariable=sugg_subject, bd=5, font=('arial', 15)).grid(row=3, column=1, sticky='ew', padx=10, pady=5)
tk.Label(suggframe, text='Details:', font=('arial', 15, 'bold')).grid(row=4, column=0, sticky='nw', padx=10, pady=5)
sugg_details_text = tk.Text(suggframe, height=5, width=40, bd=5, font=('arial', 15))
sugg_details_text.grid(row=4, column=1, sticky='ew', padx=10, pady=5)
tk.Button(suggframe, text='Submit Suggestion', command=sugg_save, font=('arial', 15, 'bold'), bg='green', fg='white').grid(row=5, column=1, sticky='ew', padx=10, pady=10)
tk.Button(suggframe, text='Back to Menu', command=submit_sugg_back, font=('arial', 15, 'bold')).grid(row=5, column=0, sticky='ew', padx=10, pady=10)


# --- VIEW SUGGESTIONS FRAME (sugg_list_frame) ---
tk.Label(sugg_list_frame, text="SUGGESTION LOG", font=('arial', 30, 'bold'), bg='dark green', fg='white').pack(pady=20, fill='x')
# Treeview setup for suggestions
suggestion_tree = ttk.Treeview(sugg_list_frame, columns=('#1', '#2', '#3', '#4', '#5'), show='headings')
suggestion_tree.heading('#1', text='ID'); suggestion_tree.column('#1', width=50, anchor='center')
suggestion_tree.heading('#2', text='Name'); suggestion_tree.column('#2', width=150, anchor='w')
suggestion_tree.heading('#3', text='Contact'); suggestion_tree.column('#3', width=120, anchor='center')
suggestion_tree.heading('#4', text='Subject'); suggestion_tree.column('#4', width=200, anchor='w')
suggestion_tree.heading('#5', text='Date'); suggestion_tree.column('#5', width=150, anchor='center')
suggestion_tree.pack(pady=10, padx=10, fill='both', expand=True)
tk.Button(sugg_list_frame, text="Back to Menu", command=list_sugg_back, font=('arial', 15, 'bold'), bg='grey').pack(pady=10)


# --- THANKFUL PAGE ---
tk.Label(thankframe, text="THANK YOU FOR USING", font=('arial', 30, 'bold')).pack(pady=50)
tk.Label(thankframe, text="BANKING MANAGEMENT SYSTEM SOFTWARE", font=('arial', 30, 'bold')).pack(pady=10)


# ====================================================================
# 10. MAINLOOP
# ====================================================================
win.mainloop()

if db_manager.conn:
    db_manager.conn.close()