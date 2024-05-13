import os
import json
import logging 
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

data_folder = "user_data"

def save_user_data(user_id, data):
    file_path = os.path.join(data_folder, f"{user_id}.json")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def load_user_data(user_id):
    file_path = os.path.join(data_folder, f"{user_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        return {"expenses": [], "incomes": [] }

TOKEN_BOT = "6892967840:AAHf3E8UkfY0LodhYUPrnQW0zv6jp_uDy0A"

expence_list = ['Relax', 'Cinema', 'Food', 'Events', 'Else']
income_list = []
logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

class Expenses:
    def __init__(self, amount: float, category: str, date: datetime):
        self.amount = amount
        self.category = category
        self.date = date.isoformat(sep='#', timespec='minutes')

class Incomes:
    def __init__(self, amount: float, category: str, date: datetime):
        self.amount = amount
        self.category = category
        self.date = date.isoformat(sep='#', timespec='minutes')

async def start(update: Update, context: CallbackContext) -> None:
    logging.info("start pressed")
    await update.message.reply_text(
        "Welcome to my Own_budget Bot!\n"
    )

async def show_expense_category(update: Update, context: CallbackContext) -> None:
    exp_categories = "\n".join(expence_list)
    await update.message.reply_text(f'You have following expense categories:\n {exp_categories}')


async def add_expense(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Please give amount and category in one message")
        return
    try:
        amount = float(args[0])
        category = args[1]
        if category not in expence_list:
            await update.message.reply_text("Invalid category. Please choose from existing categories.")
            return
        date = datetime.now()
        user_data = load_user_data(user_id)
        expenses = Expenses(amount, category, date)
        user_data["expenses"].append(expenses.__dict__)
        save_user_data(user_id, user_data)
        await update.message.reply_text(f"Expense of {amount} added to {category} successfully")
    except (ValueError, IndexError):
        await update.message.reply_text("Invalid command. Please use /add_expense <amount> <category>")

async def add_income(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Please give amount and category in one message")
        return
    try:
        amount = float(args[0])
        category = args[1]
        date = datetime.now()
        user_data = load_user_data(user_id)
        incomes = Incomes(amount, category, date)
        user_data["incomes"].append(incomes.__dict__)
        save_user_data(user_id, user_data)
        await update.message.reply_text(f"Incomes {amount} added to {category} successfully")
    except (ValueError, IndexError):
        update.message.reply_text("Invalid command. Please use /add_income <amount> <category>")    

async def list_expenses_category(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    expenses = user_data["expenses"]
    await display_expenses(update, context, expenses)

async def list_income_category(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    incomes = user_data["incomes"]
    await display_incomes(update, context, incomes)
    
async def display_expenses(update: Update, context: CallbackContext, expenses: list) -> None:
    if expenses:
        message = "\n".join([f"{index + 1}. {exp['amount']} - {exp['category']} - {exp['date']}" for index, exp in enumerate(expenses)])
        await update.message.reply_text(f"Expenses:\n{message}")
    else:
        await update.message.reply_text("No expenses found.")

async def display_incomes(update: Update, context: CallbackContext, incomes: list) -> None:
    if incomes:
        message = "\n".join([f"{index + 1}. {inc['amount']} - {inc['category']} - {inc['date']}" for index, inc in enumerate(incomes)])
        await update.message.reply_text(f"Incomes:\n{message}")
    else:
        await update.message.reply_text("No incomes found.")

async def filter_expenses(user_data: int, period: str = None, category: str = None) -> list:
    expenses = user_data.get("expenses", [])
    if period:
        today = datetime.now()
        if period == 'day':
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())
        elif period == 'month':
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'year':
            start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        expenses = [exp for exp in expenses if exp['date'] >= start_date]
    if category:
        expenses = [exp for exp in expenses if exp['category'] == category]
    return expenses

async def filtered_expenses(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    period = context.args[0] if context.args else None
    category = context.args[1] if len(context.args) > 1 else None
    filtered_expenses_result = await filter_expenses(user_id, period, category)
    await display_expenses(update, context, filtered_expenses_result)

async def stats_expenses(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    filtered_expenses_res = filter_expenses(period, category)
    total_expenses = sum([expense['amount'] for expense in filtered_expenses_res])
    message = f"Total Expenses: {total_expenses}\n"
    expense_categories = {}
    for expense in filtered_expenses:
        expense_categories[expense['category']] = expense_categories.get(expense['category'], 0) + expense['amount']
    message += "Expense Categories:\n"
    for category, amount in expense_categories.items():
        message += f"{category}: {amount}\n"
    await update.message.reply_text(message)

async def filter_incomes(user_data: int, period: str = None, category: str = None) -> list:
    incomes = user_data.get("incomes", [])
    if period:
        today = datetime.now()
        if period == 'day':
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())
        elif period == 'month':
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'year':
            start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        incomes = [inc for inc in incomes if inc['date'] >= start_date]
    if category:
        incomes = [inc for inc in incomes if inc['category'] == category]
    return incomes

async def filtered_incomes(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    period = context.args[0] if context.args else None
    category = context.args[1] if len(context.args) > 1 else None
    filtered_incomes = filter_incomes(period, category)
    await display_incomes(update, context, filtered_incomes)

async def stats_incomes(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    filtered_incomes = filter_incomes(user_data)
    total_incomes = sum([income['amount'] for income in filtered_incomes])
    message = f"Total incomes: {total_incomes}\n"
    income_categories = {}
    for income in filtered_incomes:
        income_categories[income['category']] = income_categories.get(income['category'], 0) + income['amount']
    message += "Income Categories:\n"
    for category, amount in income_categories.items():
        message += f"{category}: {amount}\n"
    await update.message.reply_text(message)


async def remove_expence(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    if not user_data["expenses"]:
        await update.message.reply_text("You dont have records to remove")
        return
    try:
        remove_idx = int(context.args[0]) - 1
        record = user_data["expenses"].pop(remove_idx)
        await update.message.reply_text(f"Expense: {record} removed")
    except (ValueError, IndexError):
        await update.message.reply_text("You entered invalid index")

async def remove_income(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    if not user_data["incomes"]:
        await update.message.reply_text("You dont have records to remove")
        return
    try:
        remove_idx = int(context.args[0]) - 1
        record = user_data["incomes"].pop(remove_idx)
        await update.message.reply_text(f"Income: {record} removed")
    except (ValueError, IndexError):
        await update.message.reply_text("You entered invalid index")

def run() -> None:
    app = ApplicationBuilder().token(TOKEN_BOT).build()
    logging.info("build success")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("exp_list", show_expense_category))
    app.add_handler(CommandHandler("add_expense", add_expense))
    app.add_handler(CommandHandler("add_income", add_income))
    app.add_handler(CommandHandler("list_expenses", list_expenses_category))
    app.add_handler(CommandHandler("list_incomes", list_income_category))
    app.add_handler(CommandHandler("filtered_expenses", filtered_expenses))
    app.add_handler(CommandHandler("filtered_incomes", filtered_incomes))
    app.add_handler(CommandHandler("stats_expenses", stats_expenses))
    app.add_handler(CommandHandler("stats_incomes", stats_incomes))
    app.add_handler(CommandHandler("del_expense", remove_expence))
    app.add_handler(CommandHandler("del_income", remove_income))
    app.run_polling()

if __name__ == "__main__":
    run()