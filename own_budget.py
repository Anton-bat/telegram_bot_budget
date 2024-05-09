import json
import logging 
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

with open('own_budget.py', 'r') as file:
    code = file.read()
code_data = {'code': code}
with open('code.json', 'w') as json_file:
    json.dump(code_data, json_file)

TOKEN_BOT = "6892967840:AAHf3E8UkfY0LodhYUPrnQW0zv6jp_uDy0A"

user_incomes = {}
user_expences = {}

expence_list = ['relax', 'cinema', 'food', 'events', 'else']
income_list = []
logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

class Expences:
    def __init__(self, amount: float, category: str, date: datetime):
        self.amount = amount
        self.category = category
        self.date = date

class Incomes:
    def __init__(self, amount: float, category: str, date: datetime):
        self.amount = amount
        self.category = category
        self.date = date

    
async def start(update: Update, context: CallbackContext) -> None:
    logging.info("start pressed")
    await update.message.reply_text(
        "Welcome to my Own_budget Bot!\n"
        "Commands:\n"
        "Outcomes categories with expences: /out_cat <out_categories>\n"
        "Create income categories: /inc_cat <create_category>\n"
        "Adding incomes: /add_inc <income>\n"
        "List of outcomes: /list\n"
        "View in/out costs during period: /view <view> [|<period>]\n"
        "Remove record: /remove <cost number>\n"
        "Statistic: /stats <stats>\n"
    )

async def show_expense_category(update: Update, context: CallbackContext) -> None:
    exp_categories = "\n".join(expence_list)
    await update.message.reply_text(f'You have follow expence categories:\n {exp_categories}')

async def add_expense(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    args = context.args
    try:
        if len(args) < 2:
            await update.message.reply_text("Please give amount and category in one message")
        amount = float(args[0])
        category = " ".join(args[1:])
        date = datetime.now()
        if not user_expences.get(user_id):
            user_expences[user_id] = []
        expences = Expences(amount, category, date)
        user_expences[user_id].append(expences)
        update.message.reply_text(f"Expences {amount} added to {category} successfully")
    except (ValueError, IndexError):
        update.message.reply_text("Invalid command. Please use /add_expense <amount> <category>")


async def add_income(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    args = context.args
    try:
        if len(args) < 2:
            await update.message.reply_text("Please give amount and category in one message")
        amount = float(args[0])
        category = args[1]
        date = datetime.now()
        incomes = Incomes(amount, category, date)
        if category not in expence_list:
            await update.message.reply_text(f"No such expences list, creating income income {category}")
            income_list.append(category)
        user_incomes.append(incomes)
        update.message.reply_text(f"Income {amount} added to {category} successfully")
    except (ValueError, IndexError):
        update.message.reply_text("Invalid command. Please use /add_income <amount> <category>")    


        
async def list_expences_category(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if not user_expences.get(user_id):
        await update.message.reply_text("You dont have any inputs")
        return
    result = "\n".join([f'Your expences:\n {i + 1}, {t}, Category: {user_expences['category']}' for i, t in enumerate(user_expences[user_id])])
    await update.message.reply_text(result)

async def list_income_category(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if not user_incomes.get(user_id):
        await update.message.reply_text("You dont have any inputs")
        return
    
    result = "\n".join([f'Your incomes:\n {i + 1}, {t}, Category: {user_incomes['category']}' for i, t in enumerate(user_incomes[user_id])])
    await update.message.reply_text(result)

async def filtered_expences(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    start_date = datetime.now()  
    end_date = datetime.now() 
    category = None

    filtered_expenses = Expences(user_expences, category, start_date, end_date)

    update.message.reply_text("Filtered expenses:")
    for expense in filtered_expenses:
        update.message.reply_text(str(expense))

async def remove_record(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if not user_incomes.get(user_id) or not user_expences.get(user_id):
        await update.message.reply_text("You dont have records to remove")
        return

    try:
        remove_idx = int(context.args[0]) - 1
        record_e = user_expences[user_id].pop(remove_idx)
        record_i = user_incomes[user_id].pop(remove_idx)
        await update.message.reply_text(f"Task: {record_e} {record_i} removed")
    except (ValueError, IndexError):
        await update.message.reply_text("You entered invalid index")

def run() -> None:
    app = ApplicationBuilder().token(TOKEN_BOT).build()
    logging.info("build success")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("add_expense", add_expense))
    app.add_handler(CommandHandler("add_income", add_income))
    app.add_handler(CommandHandler("Exp_cat", list_expences_category))
    app.add_handler(CommandHandler("Inc_cat", list_income_category))
    app.add_handler(CommandHandler("Filter_exp", filtered_expences))
    app.add_handler(CommandHandler("Del_record", remove_record))
    app.run_polling()

if __name__ == "__main__":
    run()


