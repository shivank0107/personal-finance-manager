from flask import (Flask,render_template,request,redirect,url_for,jsonify,send_file)

import os
import json
from datetime import datetime
from collections import defaultdict

import psycopg2
from psycopg2.extras import Json


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

BACKUP_DIR = os.path.join(
    DATA_DIR,
    "backups"
)

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


# =========================================================
# DATA FILES
# =========================================================

DATA_FILES = {
    "accounts": "accounts.json",
    "incomes": "incomes.json",
    "expenses": "expenses.json",
    "budgets": "budgets.json",

    "credit_cards": "credit_cards.json",
    "credit_card_transactions":
        "credit_card_transactions.json",

    "loans": "loans.json",
    "loan_repayments":
        "loan_repayments.json",

    "investments": "investments.json",
    "investment_transactions":
        "investment_transactions.json",

    "savings_goals":
        "savings_goals.json",

    "recurring_payments":
        "recurring_payments.json"
}

# =========================================================
# POSTGRESQL STORAGE
# =========================================================

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        return None

    return psycopg2.connect(DATABASE_URL)


def init_database():
    if not DATABASE_URL:
        return

    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_data (
                    collection VARCHAR(100) PRIMARY KEY,
                    data JSONB NOT NULL DEFAULT '[]'::jsonb
                )
            """)

        conn.commit()

    finally:
        conn.close()


def load_database_collection(collection):
    conn = get_db_connection()

    if conn is None:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT data
                FROM finance_data
                WHERE collection = %s
                """,
                (collection,)
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return row[0]

    finally:
        conn.close()


def save_database_collection(collection, data):
    conn = get_db_connection()

    if conn is None:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO finance_data
                    (collection, data)
                VALUES
                    (%s, %s)
                ON CONFLICT (collection)
                DO UPDATE SET
                    data = EXCLUDED.data
                """,
                (
                    collection,
                    Json(data)
                )
            )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


init_database()


# =========================================================
# JSON HELPERS
# =========================================================

def data_path(filename):

    return os.path.join(
        DATA_DIR,
        filename
    )


def load_json(filename, default=None):

    if default is None:
        default = []

    # Render/PostgreSQL
    if DATABASE_URL:

        collection = os.path.splitext(
            os.path.basename(filename)
        )[0]

        data = load_database_collection(
            collection
        )

        if data is None:

            # First-time initialization
            save_database_collection(
                collection,
                default
            )

            return default

        return data

    # Local JSON fallback
    filepath = data_path(filename)

    if not os.path.exists(filepath):

        save_json(
            filename,
            default
        )

        return default

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            return data

    except (
        json.JSONDecodeError,
        OSError
    ):

        return default


def save_json(filename, data):

    # Render/PostgreSQL
    if DATABASE_URL:

        collection = os.path.splitext(
            os.path.basename(filename)
        )[0]

        save_database_collection(
            collection,
            data
        )

        return

    # Local JSON fallback
    filepath = data_path(filename)

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# LOAD / SAVE FUNCTIONS
# =========================================================

def load_accounts():
    return load_json(
        DATA_FILES["accounts"]
    )


def save_accounts(data):
    save_json(
        DATA_FILES["accounts"],
        data
    )


def load_incomes():
    return load_json(
        DATA_FILES["incomes"]
    )


def save_incomes(data):
    save_json(
        DATA_FILES["incomes"],
        data
    )


def load_expenses():
    return load_json(
        DATA_FILES["expenses"]
    )


def save_expenses(data):
    save_json(
        DATA_FILES["expenses"],
        data
    )


def load_budgets():
    return load_json(
        DATA_FILES["budgets"]
    )


def save_budgets(data):
    save_json(
        DATA_FILES["budgets"],
        data
    )


def load_credit_cards():
    return load_json(
        DATA_FILES["credit_cards"]
    )


def save_credit_cards(data):
    save_json(
        DATA_FILES["credit_cards"],
        data
    )


def load_credit_card_transactions():
    return load_json(
        DATA_FILES[
            "credit_card_transactions"
        ]
    )


def save_credit_card_transactions(data):
    save_json(
        DATA_FILES[
            "credit_card_transactions"
        ],
        data
    )


def load_loans():
    return load_json(
        DATA_FILES["loans"]
    )


def save_loans(data):
    save_json(
        DATA_FILES["loans"],
        data
    )


def load_loan_repayments():
    return load_json(
        DATA_FILES["loan_repayments"]
    )


def save_loan_repayments(data):
    save_json(
        DATA_FILES["loan_repayments"],
        data
    )


def load_investments():
    return load_json(
        DATA_FILES["investments"]
    )


def save_investments(data):
    save_json(
        DATA_FILES["investments"],
        data
    )


def load_investment_transactions():
    return load_json(
        DATA_FILES[
            "investment_transactions"
        ]
    )


def save_investment_transactions(data):
    save_json(
        DATA_FILES[
            "investment_transactions"
        ],
        data
    )


def load_savings_goals():
    return load_json(
        DATA_FILES["savings_goals"]
    )


def save_savings_goals(data):
    save_json(
        DATA_FILES["savings_goals"],
        data
    )


def load_recurring_payments():
    return load_json(
        DATA_FILES["recurring_payments"]
    )


def save_recurring_payments(data):
    save_json(
        DATA_FILES["recurring_payments"],
        data
    )


# =========================================================
# ID GENERATOR
# =========================================================

def get_next_id(items):

    if not items:
        return 1

    ids = []

    for item in items:

        try:

            ids.append(
                int(item.get("id", 0))
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    return max(ids, default=0) + 1


# =========================================================
# VALIDATION
# =========================================================

def get_positive_amount(
    value,
    field_name="Amount"
):
    try:

        if value is None:
            raise ValueError

        value = str(value).strip()

        # Remove currency symbol
        value = value.replace("₹", "")

        # Remove comma formatting
        value = value.replace(",", "")

        value = value.strip()

        if not value:
            raise ValueError

        amount = float(value)

    except (
        ValueError,
        TypeError
    ):

        raise ValueError(
            f"{field_name} must be a valid number."
        )

    if amount <= 0:

        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return round(
        amount,
        2
    )


def validate_date(
    value,
    field_name="Date"
):
    value = str(
        value or ""
    ).strip()

    if not value:
        raise ValueError(
            f"{field_name} is required."
        )

    try:
        datetime.strptime(
            value,
            "%Y-%m-%d"
        )

    except ValueError:

        raise ValueError(
            f"{field_name} must be a valid date."
        )

    return value


def validate_date_range(
    start_date,
    end_date
):
    start_date = validate_date(
        start_date,
        "Start Date"
    )

    end_date = validate_date(
        end_date,
        "End Date"
    )

    if start_date > end_date:

        raise ValueError(
            "Start Date cannot be after End Date."
        )

    return (
        start_date,
        end_date
    )
# =========================================================
# ACCOUNT BALANCE
# =========================================================

def calculate_account_balance(
    account_id
):

    accounts = load_accounts()

    account = next(
        (
            item
            for item in accounts
            if str(item.get("id"))
            == str(account_id)
        ),
        None
    )

    if account is None:
        return 0.0

    balance = float(
        account.get(
            "opening_balance",
            0
        ) or 0
    )


    # -----------------------------------------------------
    # INCOME
    # -----------------------------------------------------

    for income in load_incomes():

        if str(
            income.get("account_id")
        ) == str(account_id):

            balance += float(
                income.get(
                    "amount",
                    0
                ) or 0
            )


    # -----------------------------------------------------
    # EXPENSES
    # -----------------------------------------------------

    for expense in load_expenses():

        if str(
            expense.get("account_id")
        ) != str(account_id):

            continue

        if (
            expense.get("payment_mode")
            == "Credit Card"
        ):

            continue

        balance -= float(
            expense.get(
                "amount",
                0
            ) or 0
        )


    # -----------------------------------------------------
    # INVESTMENT TRANSACTIONS
    # -----------------------------------------------------

    for transaction in (
        load_investment_transactions()
    ):

        if str(
            transaction.get("account_id")
        ) != str(account_id):

            continue

        amount = float(
            transaction.get(
                "amount",
                0
            ) or 0
        )

        if transaction.get("type") == "buy":

            balance -= amount

        elif transaction.get("type") == "sell":

            balance += amount


    # -----------------------------------------------------
    # CREDIT CARD PAYMENTS
    # -----------------------------------------------------

    for transaction in (
        load_credit_card_transactions()
    ):

        if str(
            transaction.get("account_id")
        ) != str(account_id):

            continue

        if transaction.get("type") != "payment":

            continue

        balance -= float(
            transaction.get(
                "amount",
                0
            ) or 0
        )


    # -----------------------------------------------------
    # LOAN REPAYMENTS
    # -----------------------------------------------------

    for repayment in load_loan_repayments():

        if str(
            repayment.get("account_id")
        ) != str(account_id):

            continue

        balance -= float(
            repayment.get(
                "amount",
                0
            ) or 0
        )


    return round(
        balance,
        2
    )


# =========================================================
# CREDIT CARD CALCULATION
# =========================================================

def calculate_credit_card_outstanding(
    card_id
):

    outstanding = 0.0

    for transaction in (
        load_credit_card_transactions()
    ):

        if str(
            transaction.get("card_id")
        ) != str(card_id):

            continue

        amount = float(
            transaction.get(
                "amount",
                0
            ) or 0
        )

        if transaction.get("type") == "purchase":

            outstanding += amount

        elif transaction.get("type") == "payment":

            outstanding -= amount

    return round(
        max(outstanding, 0),
        2
    )


# =========================================================
# BUDGET CALCULATION
# =========================================================

def calculate_budget_usage(budget):

    spent = 0.0

    # Budget category
    category = str(
        budget.get("category", "")
    ).strip().lower()

    # Budget amount
    budget_amount = float(
        budget.get("amount", 0) or 0
    )

    # Budget dates
    start_date = str(
        budget.get("start_date", "")
    ).strip()

    end_date = str(
        budget.get("end_date", "")
    ).strip()


    # -----------------------------------------------------
    # CHECK ALL EXPENSES
    # -----------------------------------------------------

    expenses_list = load_expenses()

    for expense in expenses_list:

        # Expense category
        expense_category = str(
            expense.get("category", "")
        ).strip().lower()


        # Category must match
        if expense_category != category:
            continue


        # Expense date
        expense_date = str(
            expense.get("date", "")
        ).strip()


        # Start date check
        if start_date:

            if not expense_date:
                continue

            if expense_date < start_date:
                continue


        # End date check
        if end_date:

            if not expense_date:
                continue

            if expense_date > end_date:
                continue


        # Add expense amount
        try:

            expense_amount = float(
                expense.get(
                    "amount",
                    0
                ) or 0
            )

        except (
            ValueError,
            TypeError
        ):

            expense_amount = 0.0


        spent += expense_amount


    # -----------------------------------------------------
    # CALCULATIONS
    # -----------------------------------------------------

    remaining = (
        budget_amount - spent
    )


    if budget_amount > 0:

        progress = (
            spent / budget_amount
        ) * 100

    else:

        progress = 0


    # Don't show negative remaining
    # as positive budget balance

    return {
        "spent": round(
            spent,
            2
        ),

        "remaining": round(
            remaining,
            2
        ),

        "progress": round(
            progress,
            2
        )
    }

# =========================================================
# LOAN CALCULATION
# =========================================================

def calculate_loan_summary(
    loan_id
):

    loans = load_loans()

    loan = next(
        (
            item
            for item in loans
            if int(
                item.get("id", 0)
            ) == int(loan_id)
        ),
        None
    )

    if loan is None:
        return None

    principal = float(
        loan.get(
            "principal",
            loan.get(
                "amount",
                0
            )
        ) or 0
    )

    total_paid = 0.0

    for repayment in load_loan_repayments():

        if str(
            repayment.get("loan_id")
        ) == str(loan_id):

            total_paid += float(
                repayment.get(
                    "amount",
                    0
                ) or 0
            )

    outstanding = max(
        principal - total_paid,
        0
    )

    percentage = (
        total_paid / principal * 100
        if principal > 0
        else 0
    )

    return {

        "principal": round(
            principal,
            2
        ),

        "total_paid": round(
            total_paid,
            2
        ),

        "outstanding": round(
            outstanding,
            2
        ),

        "paid_percentage": round(
            min(percentage, 100),
            2
        )

    }


# =========================================================
# INVESTMENT HOLDINGS
# =========================================================

def calculate_investment_holdings(
    investment_id
):

    units = 0.0
    invested = 0.0
    sold_amount = 0.0
    realized_profit_loss = 0.0

    transactions = (
        load_investment_transactions()
    )

    for transaction in transactions:

        if str(
            transaction.get(
                "investment_id"
            )
        ) != str(investment_id):

            continue

        transaction_type = (
            transaction.get("type")
        )

        transaction_units = float(
            transaction.get(
                "units",
                0
            ) or 0
        )

        amount = float(
            transaction.get(
                "amount",
                0
            ) or 0
        )

        price = float(
            transaction.get(
                "price",
                0
            ) or 0
        )

        if transaction_type == "buy":

            units += transaction_units

            invested += amount

        elif transaction_type == "sell":

            units -= transaction_units

            sold_amount += amount

            average_price = (
                invested / (units + transaction_units)
                if (units + transaction_units) > 0
                else 0
            )

            realized_profit_loss += (
                amount
                - (
                    transaction_units
                    * average_price
                )
            )

            invested -= (
                transaction_units
                * average_price
            )

    return {

        "units": round(
            max(units, 0),
            6
        ),

        "invested": round(
            max(invested, 0),
            2
        ),

        "sold_amount": round(
            sold_amount,
            2
        ),

        "realized_profit_loss": round(
            realized_profit_loss,
            2
        )

    }


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    accounts = load_accounts()
    incomes = load_incomes()
    expenses = load_expenses()
    investments = load_investments()
    budgets = load_budgets()
    savings_goals = load_savings_goals()

    # -----------------------------------------------------
    # ACCOUNT BALANCE
    # -----------------------------------------------------

    total_account_balance = 0.0

    for account in accounts:

        account["current_balance"] = (
            calculate_account_balance(
                account["id"]
            )
        )

        total_account_balance += (
            account["current_balance"]
        )


    # -----------------------------------------------------
    # TOTAL INCOME / EXPENSE
    # -----------------------------------------------------

    total_income = sum(
        float(
            item.get(
                "amount",
                0
            ) or 0
        )
        for item in incomes
    )

    total_expense = sum(
        float(
            item.get(
                "amount",
                0
            ) or 0
        )
        for item in expenses
    )


    # -----------------------------------------------------
    # MONTHLY CHART
    # -----------------------------------------------------

    monthly_income = defaultdict(float)
    monthly_expense = defaultdict(float)

    for income in incomes:

        date_value = income.get(
            "date",
            ""
        )

        if len(date_value) >= 7:

            monthly_income[
                date_value[:7]
            ] += float(
                income.get(
                    "amount",
                    0
                ) or 0
            )

    for expense in expenses:

        date_value = expense.get(
            "date",
            ""
        )

        if len(date_value) >= 7:

            monthly_expense[
                date_value[:7]
            ] += float(
                expense.get(
                    "amount",
                    0
                ) or 0
            )

    months = sorted(
        set(
            monthly_income.keys()
        )
        |
        set(
            monthly_expense.keys()
        )
    )

    monthly_chart = {

        "labels": months,

        "income": [
            round(
                monthly_income[m],
                2
            )
            for m in months
        ],

        "expense": [
            round(
                monthly_expense[m],
                2
            )
            for m in months
        ]

    }


    # -----------------------------------------------------
    # EXPENSE CATEGORY CHART
    # -----------------------------------------------------

    category_expenses = defaultdict(float)

    for expense in expenses:

        category = expense.get(
            "category",
            "Other"
        ) or "Other"

        category_expenses[
            category
        ] += float(
            expense.get(
                "amount",
                0
            ) or 0
        )

    expense_category_chart = {

        "labels":
            list(
                category_expenses.keys()
            ),

        "values": [
            round(
                value,
                2
            )
            for value
            in category_expenses.values()
        ]

    }


    # -----------------------------------------------------
    # BUDGET DATA
    # -----------------------------------------------------

    total_budget = 0.0
    total_budget_spent = 0.0

    for budget in budgets:

        usage = calculate_budget_usage(
            budget
        )

        budget.update(
            usage
        )

        total_budget += float(
            budget.get(
                "amount",
                0
            ) or 0
        )

        total_budget_spent += usage[
            "spent"
        ]


    # -----------------------------------------------------
    # SAVINGS CHART
    # -----------------------------------------------------

    savings_chart = {

        "labels": [
            goal.get(
                "name",
                "Goal"
            )
            for goal in savings_goals
        ],

        "saved": [
            float(
                goal.get(
                    "saved_amount",
                    0
                ) or 0
            )
            for goal in savings_goals
        ],

        "target": [
            float(
                goal.get(
                    "target_amount",
                    0
                ) or 0
            )
            for goal in savings_goals
        ]

    }


    # -----------------------------------------------------
    # INVESTMENT DATA
    # -----------------------------------------------------

    for investment in investments:

        holdings = (
            calculate_investment_holdings(
                investment["id"]
            )
        )

        current_price = float(
            investment.get(
                "current_price",
                0
            ) or 0
        )

        investment[
            "units"
        ] = holdings["units"]

        investment[
            "current_value"
        ] = round(
            holdings["units"]
            * current_price,
            2
        )


    # -----------------------------------------------------
    # RECENT TRANSACTIONS
    # -----------------------------------------------------

    recent_transactions = []

    for income in incomes:

        recent_transactions.append({

            "type": "Income",
            "date": income.get(
                "date",
                ""
            ),
            "amount": float(
                income.get(
                    "amount",
                    0
                ) or 0
            ),
            "description": income.get(
                "description",
                ""
            )

        })

    for expense in expenses:

        recent_transactions.append({

            "type": "Expense",
            "date": expense.get(
                "date",
                ""
            ),
            "amount": float(
                expense.get(
                    "amount",
                    0
                ) or 0
            ),
            "description": expense.get(
                "description",
                ""
            )

        })

    recent_transactions.sort(
        key=lambda x: x.get(
            "date",
            ""
        ),
        reverse=True
    )

    recent_transactions = (
        recent_transactions[:10]
    )


    return render_template(

        "dashboard.html",

        accounts=accounts,

        total_account_balance=round(
            total_account_balance,
            2
        ),

        total_balance=round(
            total_account_balance,
            2
        ),

        total_income=round(
            total_income,
            2
        ),

        total_expense=round(
            total_expense,
            2
        ),

        total_expenses=round(
            total_expense,
            2
        ),

        net_balance=round(
            total_income
            - total_expense,
            2
        ),

        investments=investments,

        budgets=budgets,

        savings_goals=savings_goals,

        monthly_chart=monthly_chart,

        expense_category_chart=(
            expense_category_chart
        ),

        savings_chart=savings_chart,

        recent_transactions=(
            recent_transactions
        )

    )

# =========================================================
# INCOME
# =========================================================

@app.route("/income")
def income():

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    incomes = load_incomes()
    accounts = load_accounts()


    # -----------------------------------------------------
    # SORT BY DATE - NEWEST FIRST
    # -----------------------------------------------------

    incomes.sort(
        key=lambda x: x.get(
            "date",
            ""
        ),
        reverse=True
    )


    # -----------------------------------------------------
    # ACCOUNT MAPPING
    # -----------------------------------------------------

    account_map = {}

    for account in accounts:

        account_id = str(
            account.get(
                "id",
                ""
            )
        )

        account_name = account.get(
            "name",
            ""
        )

        if account_id:

            account_map[
                account_id
            ] = account_name


    # -----------------------------------------------------
    # ADD ACCOUNT NAME TO INCOME RECORDS
    # -----------------------------------------------------

    for item in incomes:

        account_id = str(
            item.get(
                "account_id",
                ""
            )
        )

        item["account_name"] = account_map.get(
            account_id,
            ""
        )


    # -----------------------------------------------------
    # TOTAL INCOME
    # -----------------------------------------------------

    total_income = sum(
        float(
            item.get(
                "amount",
                0
            ) or 0
        )
        for item in incomes
    )


    # -----------------------------------------------------
    # CURRENT MONTH INCOME
    # -----------------------------------------------------

    current_month = datetime.now().strftime(
        "%Y-%m"
    )

    monthly_income = sum(
        float(
            item.get(
                "amount",
                0
            ) or 0
        )
        for item in incomes
        if str(
            item.get(
                "date",
                ""
            )
        ).startswith(
            current_month
        )
    )


    # -----------------------------------------------------
    # AVERAGE INCOME
    # -----------------------------------------------------

    average_income = (
        total_income / len(incomes)
        if incomes
        else 0
    )


    # -----------------------------------------------------
    # RENDER PAGE
    # -----------------------------------------------------

    return render_template(
        "income.html",

        incomes=incomes,

        accounts=accounts,

        total_income=round(
            total_income,
            2
        ),

        monthly_income=round(
            monthly_income,
            2
        ),

        average_income=round(
            average_income,
            2
        )
    )


@app.route(
    "/income/add",
    methods=["GET", "POST"]
)
def add_income():

    accounts = load_accounts()

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get("amount"),
                "Amount"
            )

            date_value = validate_date(
                request.form.get("date")
            )

        except ValueError as error:

            return str(error), 400

        incomes = load_incomes()

        income = {

            "id": get_next_id(
                incomes
            ),

            "date": date_value,

            "amount": amount,

            "category": request.form.get(
                "category",
                "Salary"
            ),

            "account_id": request.form.get(
                "account_id"
            ),

            "payment_mode": request.form.get(
                "payment_mode",
                ""
            ),

            "description": request.form.get(
                "description",
                ""
            ).strip(),

            "created_at":
                datetime.now().isoformat()

        }

        incomes.append(
            income
        )

        save_incomes(
            incomes
        )

        return redirect(
            url_for("income")
        )

    return render_template(
        "add_income.html",
        accounts=accounts
    )


@app.route(
    "/income/<int:income_id>/edit",
    methods=["GET", "POST"]
)
def edit_income(income_id):

    incomes = load_incomes()

    income_item = next(
        (
            item
            for item in incomes
            if int(
                item.get("id", 0)
            ) == income_id
        ),
        None
    )

    if income_item is None:

        return (
            "Income not found.",
            404
        )

    accounts = load_accounts()

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get("amount"),
                "Amount"
            )

            date_value = validate_date(
                request.form.get("date")
            )

        except ValueError as error:

            return str(error), 400

        income_item["date"] = date_value

        income_item["amount"] = amount

        income_item["category"] = request.form.get(
            "category",
            ""
        )

        income_item["account_id"] = request.form.get(
            "account_id"
        )

        income_item["payment_mode"] = request.form.get(
            "payment_mode",
            ""
        )

        income_item["description"] = request.form.get(
            "description",
            ""
        ).strip()

        save_incomes(
            incomes
        )

        return redirect(
            url_for("income")
        )

    return render_template(
        "edit_income.html",
        income=income_item,
        accounts=accounts
    )


@app.route(
    "/income/<int:income_id>/delete",
    methods=["POST"]
)
def delete_income(income_id):

    incomes = load_incomes()

    updated = [
        item
        for item in incomes
        if int(
            item.get("id", 0)
        ) != income_id
    ]

    if len(updated) == len(incomes):

        return (
            "Income not found.",
            404
        )

    save_incomes(
        updated
    )

    return redirect(
        url_for("income")
    )

# =========================================================
# EXPENSES
# =========================================================

@app.route("/expenses")
def expenses():

    expenses_list = load_expenses()

    expenses_list.sort(
        key=lambda x: x.get(
            "date",
            ""
        ),
        reverse=True
    )

    total_expenses = sum(
        float(
            item.get(
                "amount",
                0
            ) or 0
        )
        for item in expenses_list
    )

    return render_template(
        "expenses.html",
        expenses=expenses_list,
        total_expenses=round(
            total_expenses,
            2
        )
    )


@app.route(
    "/expenses/add",
    methods=["GET", "POST"]
)
def add_expense():

    accounts = load_accounts()

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get("amount"),
                "Amount"
            )

            date_value = validate_date(
                request.form.get("date")
            )

        except ValueError as error:

            return str(error), 400

        expenses = load_expenses()

        expense = {

            "id": get_next_id(
                expenses
            ),

            "date": date_value,

            "amount": amount,

            "category": request.form.get(
                "category",
                "Other"
            ),

            "account_id": request.form.get(
                "account_id"
            ),

            "payment_mode": request.form.get(
                "payment_mode",
                ""
            ),

            "description": request.form.get(
                "description",
                ""
            ).strip(),

            "created_at":
                datetime.now().isoformat()

        }

        expenses.append(
            expense
        )

        save_expenses(
            expenses
        )

        return redirect(
            url_for("expenses")
        )

    return render_template(
        "add_expense.html",
        accounts=accounts
    )


@app.route(
    "/expenses/<int:expense_id>/edit",
    methods=["GET", "POST"]
)
def edit_expense(expense_id):

    expenses_list = load_expenses()

    expense = None

    for item in expenses_list:

        try:
            item_id = int(item.get("id", 0))
        except (ValueError, TypeError):
            continue

        if item_id == expense_id:
            expense = item
            break

    if expense is None:
        return "Expense not found.", 404

    accounts = load_accounts()

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get("amount"),
                "Amount"
            )

            date_value = validate_date(
                request.form.get("date")
            )

        except ValueError as error:

            return str(error), 400

        expense["date"] = date_value

        expense["amount"] = amount

        expense["category"] = request.form.get(
            "category",
            "Other"
        )

        expense["account_id"] = request.form.get(
            "account_id"
        )

        expense["payment_mode"] = request.form.get(
            "payment_mode",
            ""
        )

        expense["description"] = request.form.get(
            "description",
            ""
        ).strip()

        save_expenses(
            expenses_list
        )

        return redirect(
            url_for("expenses")
        )

    return render_template(
        "edit_expense.html",
        expense=expense,
        accounts=accounts
    )


@app.route(
    "/expenses/<int:expense_id>/delete",
    methods=["POST"]
)
@app.route(
    "/expenses/<int:expense_id>/delete",
    methods=["POST"]
)
def delete_expense(expense_id):

    try:

        expenses_list = load_expenses()

        updated_expenses = []

        deleted = False

        for expense in expenses_list:

            try:
                current_id = int(
                    expense.get("id", 0)
                )
            except (ValueError, TypeError):

                current_id = 0

            if current_id == expense_id:

                deleted = True

                continue

            updated_expenses.append(
                expense
            )

        if not deleted:

            return (
                "Expense not found.",
                404
            )

        save_expenses(
            updated_expenses
        )

        return redirect(
            url_for("expenses")
        )

    except Exception as error:

        app.logger.exception(
            "Error deleting expense"
        )

        return (
            f"Error deleting expense: {error}",
            500
        )

# =========================================================
# ACCOUNTS
# =========================================================

@app.route("/accounts")
def accounts():

    accounts_list = load_accounts()

    total_balance = 0.0

    for account in accounts_list:

        account["current_balance"] = (
            calculate_account_balance(
                account["id"]
            )
        )

        total_balance += (
            account["current_balance"]
        )

    return render_template(
        "accounts.html",
        accounts=accounts_list,
        total_balance=round(
            total_balance,
            2
        )
    )


@app.route(
    "/accounts/add",
    methods=["GET", "POST"]
)
def add_account():

    if request.method == "POST":

        try:

            opening_balance = float(
                request.form.get(
                    "opening_balance",
                    0
                ) or 0
            )

        except (
            ValueError,
            TypeError
        ):

            return (
                "Invalid opening balance.",
                400
            )

        accounts_list = load_accounts()

        account = {

            "id": get_next_id(
                accounts_list
            ),

            "name": request.form.get(
                "name",
                ""
            ).strip(),

            "type": request.form.get(
                "type",
                "Bank Account"
            ),

            "bank_name": request.form.get(
                "bank_name",
                ""
            ).strip(),

            "account_number": request.form.get(
                "account_number",
                ""
            ).strip(),

            "opening_balance":
                round(
                    opening_balance,
                    2
                ),

            "created_at":
                datetime.now().isoformat()

        }

        accounts_list.append(
            account
        )

        save_accounts(
            accounts_list
        )

        return redirect(
            url_for("accounts")
        )

    return render_template(
        "add_account.html"
    )


@app.route(
    "/accounts/<int:account_id>/edit",
    methods=["GET", "POST"]
)
def edit_account(account_id):

    accounts_list = load_accounts()

    account = next(
        (
            item
            for item in accounts_list
            if int(
                item.get("id", 0)
            ) == account_id
        ),
        None
    )

    if account is None:

        return (
            "Account not found.",
            404
        )

    if request.method == "POST":

        try:

            opening_balance = float(
                request.form.get(
                    "opening_balance",
                    0
                ) or 0
            )

        except (
            ValueError,
            TypeError
        ):

            return (
                "Invalid opening balance.",
                400
            )

        account["name"] = request.form.get(
            "name",
            ""
        ).strip()

        account["type"] = request.form.get(
            "type",
            "Bank Account"
        )

        account["bank_name"] = request.form.get(
            "bank_name",
            ""
        ).strip()

        account["account_number"] = request.form.get(
            "account_number",
            ""
        ).strip()

        account["opening_balance"] = round(
            opening_balance,
            2
        )

        save_accounts(
            accounts_list
        )

        return redirect(
            url_for("accounts")
        )

    return render_template(
        "edit_account.html",
        account=account
    )


@app.route(
    "/accounts/<int:account_id>/delete",
    methods=["POST"]
)
def delete_account(account_id):

    accounts_list = load_accounts()

    account = next(
        (
            item
            for item in accounts_list
            if int(
                item.get("id", 0)
            ) == account_id
        ),
        None
    )

    if account is None:

        return (
            "Account not found.",
            404
        )

    linked = False

    for item in load_incomes():

        if str(
            item.get("account_id")
        ) == str(account_id):

            linked = True
            break

    if not linked:

        for item in load_expenses():

            if str(
                item.get("account_id")
            ) == str(account_id):

                linked = True
                break

    if not linked:

        for item in load_loan_repayments():

            if str(
                item.get("account_id")
            ) == str(account_id):

                linked = True
                break

    if not linked:

        for item in load_investment_transactions():

            if str(
                item.get("account_id")
            ) == str(account_id):

                linked = True
                break

    if linked:

        return (
            "This account has linked transactions. "
            "Delete or move those transactions first.",
            400
        )

    accounts_list = [
        item
        for item in accounts_list
        if int(
            item.get("id", 0)
        ) != account_id
    ]

    save_accounts(
        accounts_list
    )

    return redirect(
        url_for("accounts")
    )


# =========================================================
# BUDGETS
# =========================================================

@app.route("/budgets")
def budgets():

    budgets_list = load_budgets()

    total_budget = 0.0
    total_spent = 0.0

    for budget in budgets_list:

        usage = calculate_budget_usage(
            budget
        )

        budget.update(
            usage
        )

        total_budget += float(
            budget.get(
                "amount",
                0
            ) or 0
        )

        total_spent += usage[
            "spent"
        ]

    return render_template(
        "budgets.html",

        budgets=budgets_list,

        total_budget=round(
            total_budget,
            2
        ),

        total_spent=round(
            total_spent,
            2
        ),

        total_remaining=round(
            total_budget - total_spent,
            2
        )
    )


@app.route(
    "/budgets/add",
    methods=["GET", "POST"]
)
def add_budget():

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get("amount"),
                "Budget amount"
            )

            start_date = validate_date(
                request.form.get("start_date")
            )

            end_date = validate_date(
                request.form.get("end_date")
            )

            validate_date_range(
                start_date,
                end_date
            )

        except ValueError as error:

            return str(error), 400

        budgets_list = load_budgets()

        budget = {

            "id": get_next_id(
                budgets_list
            ),

            "name": request.form.get(
                "name",
                ""
            ).strip(),

            "category": request.form.get(
                "category",
                "Other"
            ),

            "amount": amount,

            "start_date": start_date,

            "end_date": end_date,

            "created_at":
                datetime.now().isoformat()

        }

        budgets_list.append(
            budget
        )

        save_budgets(
            budgets_list
        )

        return redirect(
            url_for("budgets")
        )

    return render_template(
        "add_budget.html"
    )


@app.route(
    "/budgets/<int:budget_id>/edit",
    methods=["GET", "POST"]
)
def edit_budget(budget_id):

    budgets_list = load_budgets()

    budget = next(
        (
            item
            for item in budgets_list
            if int(
                item.get("id", 0)
            ) == budget_id
        ),
        None
    )

    if budget is None:

        return (
            "Budget not found.",
            404
        )

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get("amount"),
                "Budget amount"
            )

            start_date = validate_date(
                request.form.get("start_date")
            )

            end_date = validate_date(
                request.form.get("end_date")
            )

            validate_date_range(
                start_date,
                end_date
            )

        except ValueError as error:

            return str(error), 400

        budget["name"] = request.form.get(
            "name",
            ""
        ).strip()

        budget["category"] = request.form.get(
            "category",
            "Other"
        )

        budget["amount"] = amount

        budget["start_date"] = start_date
        budget["end_date"] = end_date

        save_budgets(
            budgets_list
        )

        return redirect(
            url_for("budgets")
        )

    return render_template(
        "edit_budget.html",
        budget=budget
    )


@app.route(
    "/budgets/<int:budget_id>/delete",
    methods=["POST"]
)
def delete_budget(budget_id):

    budgets_list = load_budgets()

    updated = [
        item
        for item in budgets_list
        if int(
            item.get("id", 0)
        ) != budget_id
    ]

    if len(updated) == len(budgets_list):

        return (
            "Budget not found.",
            404
        )

    save_budgets(
        updated
    )

    return redirect(
        url_for("budgets")
    )


# =========================================================
# CREDIT CARDS
# =========================================================

@app.route("/credit-cards")
def credit_cards():

    cards = load_credit_cards()

    total_limit = 0.0
    total_outstanding = 0.0

    for card in cards:

        limit = float(
            card.get(
                "credit_limit",
                0
            ) or 0
        )

        outstanding = (
            calculate_credit_card_outstanding(
                card["id"]
            )
        )

        card["outstanding"] = outstanding

        card["available_limit"] = round(
            max(
                limit - outstanding,
                0
            ),
            2
        )

        card["utilization"] = round(
            (
                outstanding / limit * 100
            )
            if limit > 0
            else 0,
            2
        )

        total_limit += limit
        total_outstanding += outstanding

    return render_template(
        "credit_cards.html",

        cards=cards,

        total_limit=round(
            total_limit,
            2
        ),

        total_outstanding=round(
            total_outstanding,
            2
        ),

        total_available=round(
            max(
                total_limit
                - total_outstanding,
                0
            ),
            2
        )
    )


@app.route(
    "/credit-cards/add",
    methods=["GET", "POST"]
)
def add_credit_card():

    if request.method == "POST":

        try:

            credit_limit = get_positive_amount(
                request.form.get(
                    "credit_limit"
                ),
                "Credit limit"
            )

        except ValueError as error:

            return str(error), 400

        cards = load_credit_cards()

        card = {

            "id": get_next_id(
                cards
            ),

            "name": request.form.get(
                "name",
                ""
            ).strip(),

            "bank_name": request.form.get(
                "bank_name",
                ""
            ).strip(),

            "last_four": request.form.get(
                "last_four",
                ""
            ).strip(),

            "credit_limit":
                credit_limit,

            "billing_day": request.form.get(
                "billing_day",
                ""
            ),

            "due_day": request.form.get(
                "due_day",
                ""
            ),

            "created_at":
                datetime.now().isoformat()

        }

        cards.append(
            card
        )

        save_credit_cards(
            cards
        )

        return redirect(
            url_for("credit_cards")
        )

    return render_template(
        "add_credit_card.html"
    )


@app.route(
    "/credit-cards/<int:card_id>/edit",
    methods=["GET", "POST"]
)
def edit_credit_card(card_id):

    cards = load_credit_cards()

    card = next(
        (
            item
            for item in cards
            if int(
                item.get("id", 0)
            ) == card_id
        ),
        None
    )

    if card is None:

        return (
            "Credit card not found.",
            404
        )

    if request.method == "POST":

        try:

            credit_limit = get_positive_amount(
                request.form.get(
                    "credit_limit"
                ),
                "Credit limit"
            )

        except ValueError as error:

            return str(error), 400

        card["name"] = request.form.get(
            "name",
            ""
        ).strip()

        card["bank_name"] = request.form.get(
            "bank_name",
            ""
        ).strip()

        card["last_four"] = request.form.get(
            "last_four",
            ""
        ).strip()

        card["credit_limit"] = (
            credit_limit
        )

        card["billing_day"] = request.form.get(
            "billing_day",
            ""
        )

        card["due_day"] = request.form.get(
            "due_day",
            ""
        )

        save_credit_cards(
            cards
        )

        return redirect(
            url_for("credit_cards")
        )

    return render_template(
        "edit_credit_card.html",
        card=card
    )


@app.route(
    "/credit-cards/<int:card_id>/delete",
    methods=["POST"]
)
def delete_credit_card(card_id):

    cards = load_credit_cards()

    card = next(
        (
            item
            for item in cards
            if int(
                item.get("id", 0)
            ) == card_id
        ),
        None
    )

    if card is None:

        return (
            "Credit card not found.",
            404
        )

    transactions = (
        load_credit_card_transactions()
    )

    if any(
        str(
            item.get("card_id")
        ) == str(card_id)
        for item in transactions
    ):

        return (
            "This credit card has transactions. "
            "Delete those transactions first.",
            400
        )

    cards = [
        item
        for item in cards
        if int(
            item.get("id", 0)
        ) != card_id
    ]

    save_credit_cards(
        cards
    )

    return redirect(
        url_for("credit_cards")
    )


# =========================================================
# CREDIT CARD PURCHASE
# =========================================================

@app.route(
    "/credit-cards/<int:card_id>/purchase",
    methods=["GET", "POST"]
)
def credit_card_purchase(card_id):

    cards = load_credit_cards()

    card = next(
        (
            item
            for item in cards
            if int(
                item.get("id", 0)
            ) == card_id
        ),
        None
    )

    if card is None:

        return (
            "Credit card not found.",
            404
        )

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get(
                    "amount"
                )
            )

        except ValueError as error:

            return str(error), 400

        outstanding = (
            calculate_credit_card_outstanding(
                card_id
            )
        )

        limit = float(
            card.get(
                "credit_limit",
                0
            ) or 0
        )

        if outstanding + amount > limit:

            return (
                "Transaction exceeds available credit limit.",
                400
            )

        transactions = (
            load_credit_card_transactions()
        )

        transaction = {

            "id": get_next_id(
                transactions
            ),

            "card_id":
                card_id,

            "type":
                "purchase",

            "amount":
                amount,

            "date":
                request.form.get(
                    "date"
                ),

            "description":
                request.form.get(
                    "description",
                    ""
                ).strip(),

            "created_at":
                datetime.now().isoformat()

        }

        transactions.append(
            transaction
        )

        save_credit_card_transactions(
            transactions
        )

        return redirect(
            url_for("credit_cards")
        )

    return render_template(
        "credit_card_purchase.html",
        card=card
    )


# =========================================================
# CREDIT CARD PAYMENT
# =========================================================

@app.route(
    "/credit-cards/<int:card_id>/payment",
    methods=["GET", "POST"]
)
@app.route(
    "/credit-cards/<int:card_id>/pay",
    methods=["GET", "POST"]
)
def credit_card_payment(card_id):

    cards = load_credit_cards()

    card = next(
        (
            item
            for item in cards
            if int(
                item.get("id", 0)
            ) == card_id
        ),
        None
    )

    if card is None:

        return (
            "Credit card not found.",
            404
        )

    accounts = load_accounts()

    outstanding = (
        calculate_credit_card_outstanding(
            card_id
        )
    )

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get(
                    "amount"
                )
            )

        except ValueError as error:

            return str(error), 400

        if amount > outstanding:

            return (
                "Payment cannot exceed outstanding amount.",
                400
            )

        account_id = request.form.get(
            "account_id"
        )

        if not account_id:

            return (
                "Please select an account.",
                400
            )

        transactions = (
            load_credit_card_transactions()
        )

        transaction = {

            "id": get_next_id(
                transactions
            ),

            "card_id":
                card_id,

            "account_id":
                account_id,

            "type":
                "payment",

            "amount":
                amount,

            "date":
                request.form.get(
                    "date"
                ),

            "description":
                request.form.get(
                    "description",
                    ""
                ).strip(),

            "created_at":
                datetime.now().isoformat()

        }

        transactions.append(
            transaction
        )

        save_credit_card_transactions(
            transactions
        )

        return redirect(
            url_for("credit_cards")
        )

    return render_template(
        "credit_card_payment.html",
        card=card,
        accounts=accounts,
        outstanding=outstanding
    )


# Alias used by some templates
@app.route(
    "/credit-cards/<int:card_id>/pay-card",
    methods=["GET", "POST"]
)
def pay_credit_card(card_id):

    return credit_card_payment(
        card_id
    )


# =========================================================
# LOANS
# =========================================================

@app.route("/loans")
def loans():

    loans_list = load_loans()

    total_principal = 0.0
    total_paid = 0.0
    total_outstanding = 0.0

    for loan in loans_list:

        summary = calculate_loan_summary(
            int(
                loan["id"]
            )
        )

        loan.update(
            summary
        )

        total_principal += summary[
            "principal"
        ]

        total_paid += summary[
            "total_paid"
        ]

        total_outstanding += summary[
            "outstanding"
        ]

    return render_template(
        "loans.html",

        loans=loans_list,

        total_principal=round(
            total_principal,
            2
        ),

        total_paid=round(
            total_paid,
            2
        ),

        total_outstanding=round(
            total_outstanding,
            2
        )
    )


@app.route(
    "/loans/add",
    methods=["GET", "POST"]
)
def add_loan():

    if request.method == "POST":

        try:

            principal = get_positive_amount(
                request.form.get(
                    "principal"
                ),
                "Principal"
            )

        except ValueError as error:

            return str(error), 400

        loans_list = load_loans()

        loan = {

            "id": get_next_id(
                loans_list
            ),

            "name": request.form.get(
                "name",
                ""
            ).strip(),

            "lender": request.form.get(
                "lender",
                ""
            ).strip(),

            "principal":
                principal,

            "interest_rate":
                float(
                    request.form.get(
                        "interest_rate",
                        0
                    ) or 0
                ),

            "tenure":
                int(
                    request.form.get(
                        "tenure",
                        0
                    ) or 0
                ),

            "emi":
                float(
                    request.form.get(
                        "emi",
                        0
                    ) or 0
                ),

            "start_date":
                request.form.get(
                    "start_date",
                    ""
                ),

            "description":
                request.form.get(
                    "description",
                    ""
                ).strip(),

            "created_at":
                datetime.now().isoformat()

        }

        loans_list.append(
            loan
        )

        save_loans(
            loans_list
        )

        return redirect(
            url_for("loans")
        )

    return render_template(
        "add_loan.html"
    )


@app.route(
    "/loans/<int:loan_id>/edit",
    methods=["GET", "POST"]
)
def edit_loan(loan_id):

    loans_list = load_loans()

    loan = next(
        (
            item
            for item in loans_list
            if int(
                item.get("id", 0)
            ) == loan_id
        ),
        None
    )

    if loan is None:

        return (
            "Loan not found.",
            404
        )

    if request.method == "POST":

        try:

            principal = get_positive_amount(
                request.form.get(
                    "principal"
                ),
                "Principal"
            )

        except ValueError as error:

            return str(error), 400

        loan["name"] = request.form.get(
            "name",
            ""
        ).strip()

        loan["lender"] = request.form.get(
            "lender",
            ""
        ).strip()

        loan["principal"] = principal

        loan["interest_rate"] = float(
            request.form.get(
                "interest_rate",
                0
            ) or 0
        )

        loan["tenure"] = int(
            request.form.get(
                "tenure",
                0
            ) or 0
        )

        loan["emi"] = float(
            request.form.get(
                "emi",
                0
            ) or 0
        )

        loan["start_date"] = request.form.get(
            "start_date",
            ""
        )

        loan["description"] = request.form.get(
            "description",
            ""
        ).strip()

        save_loans(
            loans_list
        )

        return redirect(
            url_for("loans")
        )

    return render_template(
        "edit_loan.html",
        loan=loan
    )


@app.route(
    "/loans/<int:loan_id>/delete",
    methods=["POST"]
)
def delete_loan(loan_id):

    loans_list = load_loans()

    if not any(
        int(
            item.get("id", 0)
        ) == loan_id
        for item in loans_list
    ):

        return (
            "Loan not found.",
            404
        )

    repayments = load_loan_repayments()

    if any(
        str(
            item.get("loan_id")
        ) == str(loan_id)
        for item in repayments
    ):

        return (
            "This loan has repayment records. "
            "Delete those records first.",
            400
        )

    loans_list = [
        item
        for item in loans_list
        if int(
            item.get("id", 0)
        ) != loan_id
    ]

    save_loans(
        loans_list
    )

    return redirect(
        url_for("loans")
    )


@app.route(
    "/loans/<int:loan_id>"
)
def loan_details(loan_id):

    loans_list = load_loans()

    loan = next(
        (
            item
            for item in loans_list
            if int(
                item.get("id", 0)
            ) == loan_id
        ),
        None
    )

    if loan is None:

        return (
            "Loan not found.",
            404
        )

    summary = calculate_loan_summary(
        loan_id
    )

    repayments = [
        item
        for item in load_loan_repayments()
        if str(
            item.get("loan_id")
        ) == str(loan_id)
    ]

    repayments.sort(
        key=lambda x: x.get(
            "date",
            ""
        ),
        reverse=True
    )

    return render_template(
        "loan_details.html",

        loan=loan,

        summary=summary,

        repayments=repayments
    )


# =========================================================
# LOAN PAYMENT
# =========================================================

@app.route(
    "/loans/<int:loan_id>/payment",
    methods=["GET", "POST"]
)
def loan_payment(loan_id):

    loans_list = load_loans()

    loan = next(
        (
            item
            for item in loans_list
            if int(
                item.get("id", 0)
            ) == loan_id
        ),
        None
    )

    if loan is None:

        return (
            "Loan not found.",
            404
        )

    accounts = load_accounts()

    summary = calculate_loan_summary(
        loan_id
    )

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get(
                    "amount"
                )
            )

        except ValueError as error:

            return str(error), 400

        if amount > summary[
            "outstanding"
        ]:

            return (
                "Payment cannot exceed outstanding principal.",
                400
            )

        account_id = request.form.get(
            "account_id"
        )

        if not account_id:

            return (
                "Please select an account.",
                400
            )

        repayments = load_loan_repayments()

        repayment = {

            "id":
                get_next_id(
                    repayments
                ),

            "loan_id":
                loan_id,

            "account_id":
                account_id,

            "date":
                request.form.get(
                    "date"
                ),

            "amount":
                amount,

            "description":
                request.form.get(
                    "description",
                    ""
                ).strip(),

            "created_at":
                datetime.now().isoformat()

        }

        repayments.append(
            repayment
        )

        save_loan_repayments(
            repayments
        )

        return redirect(
            url_for(
                "loan_details",
                loan_id=loan_id
            )
        )

    return render_template(
        "loan_payment.html",

        loan=loan,

        accounts=accounts,

        summary=summary
    )


# =========================================================
# INVESTMENTS
# =========================================================

@app.route("/investments")
def investments():

    investments_list = load_investments()

    total_value = 0.0
    total_invested = 0.0

    for investment in investments_list:

        holdings = (
            calculate_investment_holdings(
                investment["id"]
            )
        )

        current_price = float(
            investment.get(
                "current_price",
                0
            ) or 0
        )

        current_value = (
            holdings["units"]
            * current_price
        )

        investment.update(
            holdings
        )

        investment[
            "current_value"
        ] = round(
            current_value,
            2
        )

        total_value += current_value
        total_invested += holdings[
            "invested"
        ]

    return render_template(
        "investments.html",

        investments=investments_list,

        total_value=round(
            total_value,
            2
        ),

        total_invested=round(
            total_invested,
            2
        ),

        total_profit_loss=round(
            total_value
            - total_invested,
            2
        )
    )


@app.route(
    "/investments/add",
    methods=["GET", "POST"]
)
def add_investment():

    accounts = load_accounts()

    if request.method == "POST":

        investments_list = (
            load_investments()
        )

        investment = {

            "id":
                get_next_id(
                    investments_list
                ),

            "name":
                request.form.get(
                    "name",
                    ""
                ).strip(),

            "type":
                request.form.get(
                    "type",
                    "Stocks"
                ),

            "symbol":
                request.form.get(
                    "symbol",
                    ""
                ).strip(),

            "current_price":
                float(
                    request.form.get(
                        "current_price",
                        0
                    ) or 0
                ),

            "description":
                request.form.get(
                    "description",
                    ""
                ).strip(),

            "created_at":
                datetime.now().isoformat()

        }

        investments_list.append(
            investment
        )

        save_investments(
            investments_list
        )

        return redirect(
            url_for("investments")
        )

    return render_template(
        "add_investment.html",
        accounts=accounts
    )


@app.route(
    "/investments/<int:investment_id>/edit",
    methods=["GET", "POST"]
)
def edit_investment(investment_id):

    investments_list = (
        load_investments()
    )

    investment = next(
        (
            item
            for item in investments_list
            if int(
                item.get("id", 0)
            ) == investment_id
        ),
        None
    )

    if investment is None:

        return (
            "Investment not found.",
            404
        )

    if request.method == "POST":

        investment["name"] = request.form.get(
            "name",
            ""
        ).strip()

        investment["type"] = request.form.get(
            "type",
            "Stocks"
        )

        investment["symbol"] = request.form.get(
            "symbol",
            ""
        ).strip()

        investment["current_price"] = float(
            request.form.get(
                "current_price",
                0
            ) or 0
        )

        investment["description"] = request.form.get(
            "description",
            ""
        ).strip()

        save_investments(
            investments_list
        )

        return redirect(
            url_for("investments")
        )

    return render_template(
        "edit_investment.html",
        investment=investment
    )


@app.route(
    "/investments/<int:investment_id>/delete",
    methods=["POST"]
)
def delete_investment(investment_id):

    investments_list = (
        load_investments()
    )

    transactions = (
        load_investment_transactions()
    )

    if any(
        str(
            item.get("investment_id")
        ) == str(investment_id)
        for item in transactions
    ):

        return (
            "This investment has transactions. "
            "Delete those transactions first.",
            400
        )

    updated = [
        item
        for item in investments_list
        if int(
            item.get("id", 0)
        ) != investment_id
    ]

    if len(updated) == len(
        investments_list
    ):

        return (
            "Investment not found.",
            404
        )

    save_investments(
        updated
    )

    return redirect(
        url_for("investments")
    )


# =========================================================
# INVESTMENT TRANSACTIONS
# =========================================================

@app.route(
    "/investments/<int:investment_id>/transactions"
)
def investment_transactions(
    investment_id
):

    investments_list = (
        load_investments()
    )

    investment = next(
        (
            item
            for item in investments_list
            if int(
                item.get("id", 0)
            ) == investment_id
        ),
        None
    )

    if investment is None:

        return (
            "Investment not found.",
            404
        )

    transactions = [
        item
        for item in load_investment_transactions()
        if str(
            item.get("investment_id")
        ) == str(investment_id)
    ]

    transactions.sort(
        key=lambda x: x.get(
            "date",
            ""
        ),
        reverse=True
    )

    return render_template(
        "investment_transactions.html",

        investment=investment,

        transactions=transactions
    )


@app.route(
    "/investments/<int:investment_id>/transaction/add",
    methods=["GET", "POST"]
)
def add_investment_transaction(
    investment_id
):

    investments_list = (
        load_investments()
    )

    investment = next(
        (
            item
            for item in investments_list
            if int(
                item.get("id", 0)
            ) == investment_id
        ),
        None
    )

    if investment is None:

        return (
            "Investment not found.",
            404
        )

    accounts = load_accounts()

    if request.method == "POST":

        try:

            units = get_positive_amount(
                request.form.get(
                    "units"
                ),
                "Units"
            )

            price = get_positive_amount(
                request.form.get(
                    "price"
                ),
                "Price"
            )

        except ValueError as error:

            return str(error), 400

        transaction_type = request.form.get(
            "type",
            "buy"
        ).lower()

        amount = round(
            units * price,
            2
        )

        transactions = (
            load_investment_transactions()
        )

        if transaction_type == "sell":

            holdings = (
                calculate_investment_holdings(
                    investment_id
                )
            )

            if units > holdings["units"]:

                return (
                    "You cannot sell more units than you own.",
                    400
                )

        transaction = {

            "id":
                get_next_id(
                    transactions
                ),

            "investment_id":
                investment_id,

            "account_id":
                request.form.get(
                    "account_id"
                ),

            "type":
                transaction_type,

            "units":
                units,

            "price":
                price,

            "amount":
                amount,

            "date":
                request.form.get(
                    "date"
                ),

            "description":
                request.form.get(
                    "description",
                    ""
                ).strip(),

            "created_at":
                datetime.now().isoformat()

        }

        transactions.append(
            transaction
        )

        save_investment_transactions(
            transactions
        )

        return redirect(
            url_for(
                "investment_transactions",
                investment_id=investment_id
            )
        )

    return render_template(
        "add_investment_transaction.html",

        investment=investment,

        accounts=accounts
    )


@app.route(
    "/investments/<int:investment_id>/history"
)
def investment_history(
    investment_id
):

    investments_list = (
        load_investments()
    )

    investment = next(
        (
            item
            for item in investments_list
            if int(
                item.get("id", 0)
            ) == investment_id
        ),
        None
    )

    if investment is None:

        return (
            "Investment not found.",
            404
        )

    transactions = [
        item
        for item in load_investment_transactions()
        if str(
            item.get("investment_id")
        ) == str(investment_id)
    ]

    transactions.sort(
        key=lambda x: x.get(
            "date",
            ""
        ),
        reverse=True
    )

    holdings = (
        calculate_investment_holdings(
            investment_id
        )
    )

    total_bought = sum(
        float(
            item.get(
                "amount",
                0
            ) or 0
        )
        for item in transactions
        if item.get("type") == "buy"
    )

    total_sold = sum(
        float(
            item.get(
                "amount",
                0
            ) or 0
        )
        for item in transactions
        if item.get("type") == "sell"
    )

    return render_template(
        "investment_history.html",

        investment=investment,

        transactions=transactions,

        holdings=holdings,

        total_bought=round(
            total_bought,
            2
        ),

        total_sold=round(
            total_sold,
            2
        )
    )


@app.route(
    "/investments/<int:investment_id>/valuation"
)
def investment_valuation(
    investment_id
):

    investments_list = (
        load_investments()
    )

    investment = next(
        (
            item
            for item in investments_list
            if int(
                item.get("id", 0)
            ) == investment_id
        ),
        None
    )

    if investment is None:

        return (
            "Investment not found.",
            404
        )

    holdings = (
        calculate_investment_holdings(
            investment_id
        )
    )

    current_price = float(
        investment.get(
            "current_price",
            0
        ) or 0
    )

    current_value = round(
        holdings["units"]
        * current_price,
        2
    )

    return render_template(
        "investment_valuation.html",

        investment=investment,

        holdings=holdings,

        current_value=current_value,

        profit_loss=round(
            current_value
            - holdings["invested"],
            2
        )
    )


# =========================================================
# SAVINGS GOALS
# =========================================================

@app.route("/savings-goals")
def savings_goals():

    goals = load_savings_goals()

    total_target = 0.0
    total_saved = 0.0

    for goal in goals:

        target = float(
            goal.get(
                "target_amount",
                0
            ) or 0
        )

        saved = float(
            goal.get(
                "saved_amount",
                0
            ) or 0
        )

        remaining = max(
            target - saved,
            0
        )

        progress = (
            saved / target * 100
            if target > 0
            else 0
        )

        goal["remaining"] = round(
            remaining,
            2
        )

        goal["progress"] = round(
            min(progress, 100),
            2
        )

        total_target += target
        total_saved += saved

    return render_template(
        "savings_goals.html",

        goals=goals,

        total_target=round(
            total_target,
            2
        ),

        total_saved=round(
            total_saved,
            2
        ),

        total_remaining=round(
            max(
                total_target
                - total_saved,
                0
            ),
            2
        )
    )


@app.route(
    "/savings-goals/add",
    methods=["GET", "POST"]
)
def add_savings_goal():

    if request.method == "POST":

        try:

            target_amount = get_positive_amount(
                request.form.get(
                    "target_amount"
                ),
                "Target amount"
            )

        except ValueError as error:

            return str(error), 400

        goals = load_savings_goals()

        goal = {

            "id":
                get_next_id(
                    goals
                ),

            "name":
                request.form.get(
                    "name",
                    ""
                ).strip(),

            "target_amount":
                target_amount,

            "saved_amount":
                0,

            "target_date":
                request.form.get(
                    "target_date",
                    ""
                ),

            "description":
                request.form.get(
                    "description",
                    ""
                ).strip(),

            "created_at":
                datetime.now().isoformat()

        }

        goals.append(
            goal
        )

        save_savings_goals(
            goals
        )

        return redirect(
            url_for("savings_goals")
        )

    return render_template(
        "add_savings_goal.html"
    )


@app.route(
    "/savings-goals/<int:goal_id>/edit",
    methods=["GET", "POST"]
)
def edit_savings_goal(goal_id):

    goals = load_savings_goals()

    goal = next(
        (
            item
            for item in goals
            if int(
                item.get("id", 0)
            ) == goal_id
        ),
        None
    )

    if goal is None:

        return (
            "Savings goal not found.",
            404
        )

    if request.method == "POST":

        try:

            target_amount = get_positive_amount(
                request.form.get(
                    "target_amount"
                ),
                "Target amount"
            )

        except ValueError as error:

            return str(error), 400

        goal["name"] = request.form.get(
            "name",
            ""
        ).strip()

        goal["target_amount"] = (
            target_amount
        )

        goal["target_date"] = request.form.get(
            "target_date",
            ""
        )

        goal["description"] = request.form.get(
            "description",
            ""
        ).strip()

        save_savings_goals(
            goals
        )

        return redirect(
            url_for("savings_goals")
        )

    return render_template(
        "edit_savings_goal.html",
        goal=goal
    )


@app.route(
    "/savings-goals/<int:goal_id>/delete",
    methods=["POST"]
)
def delete_savings_goal(goal_id):

    goals = load_savings_goals()

    updated = [
        item
        for item in goals
        if int(
            item.get("id", 0)
        ) != goal_id
    ]

    if len(updated) == len(goals):

        return (
            "Savings goal not found.",
            404
        )

    save_savings_goals(
        updated
    )

    return redirect(
        url_for("savings_goals")
    )


@app.route(
    "/savings-goals/<int:goal_id>/contribute",
    methods=["GET", "POST"]
)
def contribute_savings_goal(
    goal_id
):

    goals = load_savings_goals()

    goal = next(
        (
            item
            for item in goals
            if int(
                item.get("id", 0)
            ) == goal_id
        ),
        None
    )

    if goal is None:

        return (
            "Savings goal not found.",
            404
        )

    if request.method == "POST":

        try:

            amount = get_positive_amount(
                request.form.get(
                    "amount"
                )
            )

        except ValueError as error:

            return str(error), 400

        current_saved = float(
            goal.get(
                "saved_amount",
                0
            ) or 0
        )

        goal["saved_amount"] = round(
            current_saved + amount,
            2
        )

        save_savings_goals(
            goals
        )

        return redirect(
            url_for("savings_goals")
        )

    return render_template(
        "contribute_savings_goal.html",
        goal=goal
    )


# Alias
@app.route(
    "/savings-goals/<int:goal_id>/add-saving",
    methods=["GET", "POST"]
)
def add_goal_saving(goal_id):

    return contribute_savings_goal(
        goal_id
    )


# =========================================================
# RECURRING PAYMENTS
# =========================================================

@app.route("/recurring-payments")
def recurring_payments():

    payments = load_recurring_payments()

    return render_template(
        "recurring_payments.html",
        recurring_payments=payments,
        payments=payments
    )


@app.route(
    "/recurring-payments/add",
    methods=["GET", "POST"]
)
def add_recurring_payment():

    if request.method == "POST":

        payments = (
            load_recurring_payments()
        )

        payment = {

            "id":
                get_next_id(
                    payments
                ),

            "name":
                request.form.get(
                    "name",
                    ""
                ).strip(),

            "amount":
                float(
                    request.form.get(
                        "amount",
                        0
                    ) or 0
                ),

            "category":
                request.form.get(
                    "category",
                    "Other"
                ),

            "frequency":
                request.form.get(
                    "frequency",
                    "Monthly"
                ),

            "next_date":
                request.form.get(
                    "next_date",
                    ""
                ),

            "description":
                request.form.get(
                    "description",
                    ""
                ).strip(),

            "active":
                True,

            "created_at":
                datetime.now().isoformat()

        }

        payments.append(
            payment
        )

        save_recurring_payments(
            payments
        )

        return redirect(
            url_for(
                "recurring_payments"
            )
        )

    return render_template(
        "add_recurring_payment.html"
    )


@app.route(
    "/recurring-payments/<int:payment_id>/edit",
    methods=["GET", "POST"]
)
def edit_recurring_payment(
    payment_id
):

    payments = (
        load_recurring_payments()
    )

    payment = next(
        (
            item
            for item in payments
            if int(
                item.get("id", 0)
            ) == payment_id
        ),
        None
    )

    if payment is None:

        return (
            "Recurring payment not found.",
            404
        )

    if request.method == "POST":

        payment["name"] = request.form.get(
            "name",
            ""
        ).strip()

        payment["amount"] = float(
            request.form.get(
                "amount",
                0
            ) or 0
        )

        payment["category"] = request.form.get(
            "category",
            "Other"
        )

        payment["frequency"] = request.form.get(
            "frequency",
            "Monthly"
        )

        payment["next_date"] = request.form.get(
            "next_date",
            ""
        )

        payment["description"] = request.form.get(
            "description",
            ""
        ).strip()

        save_recurring_payments(
            payments
        )

        return redirect(
            url_for(
                "recurring_payments"
            )
        )

    return render_template(
        "edit_recurring_payment.html",
        payment=payment
    )


# =========================================================
# REPORTS
# =========================================================

@app.route("/reports")
def reports():

    incomes = load_incomes()
    expenses = load_expenses()

    category_totals = defaultdict(float)

    for expense in expenses:

        category = expense.get(
            "category",
            "Other"
        )

        category_totals[
            category
        ] += float(
            expense.get(
                "amount",
                0
            ) or 0
        )

    return render_template(
        "reports.html",

        incomes=incomes,

        expenses=expenses,

        category_totals=dict(
            category_totals
        ),

        total_income=sum(
            float(
                x.get(
                    "amount",
                    0
                ) or 0
            )
            for x in incomes
        ),

        total_expenses=sum(
            float(
                x.get(
                    "amount",
                    0
                ) or 0
            )
            for x in expenses
        )
    )


# =========================================================
# TAX PLANNER
# =========================================================

@app.route("/tax-planner")
def tax_planner():

    incomes = load_incomes()

    total_income = sum(
        float(
            item.get(
                "amount",
                0
            ) or 0
        )
        for item in incomes
    )

    return render_template(
        "tax_planner.html",
        total_income=round(
            total_income,
            2
        )
    )


# =========================================================
# CALCULATORS
# =========================================================

@app.route("/calculators")
def calculators():

    return render_template(
        "calculators.html"
    )


# =========================================================
# FINANCIAL CALENDAR
# =========================================================

@app.route("/financial-calendar")
def financial_calendar():

    return render_template(
        "financial_calendar.html"
    )


# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings")
def settings():

    return render_template(
        "settings.html"
    )


# =========================================================
# BACKUP
# =========================================================

BACKUP_FILES = list(
    DATA_FILES.values()
)


@app.route("/backup/create")
def create_backup():

    backup_data = {}

    for filename in BACKUP_FILES:

        backup_data[
            filename
        ] = load_json(
            filename,
            []
        )

    backup_data[
        "_backup_info"
    ] = {

        "application":
            "Personal Finance Manager",

        "version":
            "1.0",

        "created_at":
            datetime.now().isoformat()

    }

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"finance_backup_{timestamp}.json"
    )

    filepath = os.path.join(
        BACKUP_DIR,
        filename
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            backup_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype="application/json"
    )


@app.route(
    "/backup/restore",
    methods=["POST"]
)
def restore_backup():

    if "backup_file" not in request.files:

        return (
            "No backup file selected.",
            400
        )

    file = request.files[
        "backup_file"
    ]

    if not file.filename:

        return (
            "No backup file selected.",
            400
        )

    if not file.filename.lower().endswith(
        ".json"
    ):

        return (
            "Only JSON backup files are supported.",
            400
        )

    try:

        backup_data = json.load(
            file
        )

    except Exception:

        return (
            "Invalid backup file.",
            400
        )

    restored = 0

    for filename in BACKUP_FILES:

        if filename not in backup_data:

            continue

        if not isinstance(
            backup_data[filename],
            list
        ):

            continue

        save_json(
            filename,
            backup_data[filename]
        )

        restored += 1

    if restored == 0:

        return (
            "No valid finance data found in backup.",
            400
        )

    return redirect(
        url_for("settings")
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "error.html",

        error_code=404,

        error_title="Page Not Found",

        error_message=(
            "The page you are looking for "
            "does not exist."
        )

    ), 404


@app.errorhandler(400)
def bad_request(error):

    return render_template(
        "error.html",

        error_code=400,

        error_title="Bad Request",

        error_message=(
            "The request could not be processed."
        )

    ), 400


@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "error.html",

        error_code=500,

        error_title="Something Went Wrong",

        error_message=(
            "An unexpected error occurred. "
            "Please try again."
        )

    ), 500


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        debug=False,
        host="0.0.0.0",
        port=port
    )