import logging 

from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

TOKEN_BOT = "6987157333:AAGmXc9UMzyqCiuJ7XCI4I28EJbVRJYPopA"
user_data = {}


logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

class Task:
    def __init__(self, title: str, deadline: datetime = None):
        self.title = title
        self.deadline = deadline
        self.completed = False
    
    def __str__(self) -> str:
        completed = "✅" if self.completed else "❌"
        if self.deadline:
            return f'{completed} {self.title} | {self.deadline.strftime("%Y-%m-%d %H:%M:%S")}'
        
        return f'{completed} {self.title}'

async def start(update: Update, context: CallbackContext) -> None:
    logging.info("start pressed")
    await update.message.reply_text(
        "Welcome to my ToDo list Bot!\n"
        "Commands:\n"
        "Adding tasks: /add <task> [| <deadline>]\n"
        "List tasks: /list\n"
        "Remove tasks: /remove <task number>\n"
        "Clear tasks: /clear\n"
    )

async def add_task(update: Update, context: CallbackContext) -> None:
    """
    format 
    /add <task> [| <deadline>]
    """
    user_id = update.message.from_user.id
    task_parts = " ".join(context.args).split("|")
    task_title = task_parts[0].strip()
    deadline = None

    if len(task_parts) > 1:
        try:
            deadline = datetime.strptime(task_parts[1].strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logging.error("Invalid deadline format")
            await update.message.reply_text("please use %Y-%m-%d %H:%M:%S format")
            return
    
    if not user_data.get(user_id):
        user_data[user_id] = []

    task = Task(task_title, deadline)
    user_data[user_id].append(task)
    await update.message.reply_text(f"Task: {task} was successfully added!")

async def list_task(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if not user_data.get(user_id):
        await update.message.reply_text("You dont have any tasks")
        return
    
    result = "\n".join([f'{i + 1}, {t}' for i, t in enumerate(user_data[user_id])])
    await update.message.reply_text(result)

async def remove_task(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if not user_data.get(user_id):
        await update.message.reply_text("You dont have tasks to remove")
        return

    try:
        remove_idx = int(context.args[0]) - 1
        task = user_data[user_id].pop(remove_idx)
        await update.message.reply_text(f"Task: {task} removed")
    except (ValueError, IndexError):
        await update.message.reply_text("You entered invalid index")

async def clear_task(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data[user_id] = []
    await update.message.reply_text("Tasks are cleared")

async def mark_completed(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if not user_data.get(user_id):
        await update.message.reply_text("You dont have tasks to complete")
        return
    
    try:
        complete_idx = int(context.args[0]) - 1
        task = user_data[user_id][complete_idx]
        task.completed = True
        await update.message.reply_text(f"Task: {task} completed")
    except (ValueError, IndexError):
        await update.message.reply_text("You entered invalid index")

async def check_deadlines(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if not user_data.get(user_id):
        await update.message.reply_text("You dont have tasks")
        return
    
    now = datetime.now()
    upcoming_deadlines = list()
    for task in user_data[user_id]:
        if task.deadline and task.deadline <= (now + timedelta(days=1)) and not task.completed:
             upcoming_deadlines.append(f'{task}')

    if upcoming_deadlines:
        await update.message.reply_text(
            f'upcoming tasks:\n'
            f'{' '.join(upcoming_deadlines)}'
        )
        return
    await update.message.reply_text("You dont have upcoming tasks")

def run():
    app = ApplicationBuilder().token(TOKEN_BOT).build()
    logging.info("build success")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("add_expense", add_expence))
    app.add_handler(CommandHandler("list", list_task))
    app.add_handler(CommandHandler("remove", remove_task))
    app.add_handler(CommandHandler("clear", clear_task))
    app.add_handler(CommandHandler("complete", mark_completed))
    app.add_handler(CommandHandler("deadline", check_deadlines))

    app.run_polling()

if __name__ == "__main__":
    run()

