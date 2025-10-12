# Banking Management System (Python/Tkinter/SQLite)

A complete desktop application prototype for banking administrators, covering user authentication, customer relationship management, transaction handling, and internal employee and feedback management.

## 🚀 Features

* **Secure Authentication:** Admin login with SQLite database.
* **Modular Architecture:** Separation of GUI (Tkinter) and Data Logic (DatabaseManager class).
* **Customer CRUD:** Create, Read, Update, Delete customer accounts with automatic Account Number generation.
* **Financial Transactions:** Dedicated modules for Withdrawal and Deposit with validation checks.
* **Professional Reporting:** Utilizes `ttk.Treeview` for displaying comprehensive customer lists.
* **Feedback Management:** Dedicated Complaint and Suggestion trackers with status updates for complaints (Pending, Resolved).

## 🛠️ Technologies Used

* **Python 3.x**
* **Tkinter:** For the Graphical User Interface (GUI).
* **SQLite3:** For persistent data storage.

## 💡 How to Run Locally

1.  **Clone the Repository:**
    ```bash
    git clone [Your-Repo-Link-Here]
    cd BankingManagementSystem
    ```

2.  **Install Dependencies:**
    (Tkinter and SQLite are usually built-in, but this is good practice.)
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python main.py
    ```
    *(The system will automatically create the database file `mybankingdb.db` and the tables on the first run.)*

---
