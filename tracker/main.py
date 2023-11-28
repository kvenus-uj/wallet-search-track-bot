import os.path
import re
from util import *
import requests
import sys, os
import concurrent.futures
import threading
import json

latest_tx_hashes = {}
last_run_time = 0


class RateLimiter:
    def __init__(self, max_calls, interval):
        self.max_calls = max_calls
        self.interval = interval
        self.calls = 0
        self.lock = threading.Lock()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self.lock:
                if self.calls == self.max_calls:
                    elapsed = time.time() - self.last_call_time
                    if elapsed < self.interval:
                        time.sleep(self.interval - elapsed)
                        self.calls = 0
                self.calls += 1
                self.last_call_time = time.time()
            return func(*args, **kwargs)

        return wrapper


@RateLimiter(max_calls=30, interval=1)
def wallet_check(wallet):
    global latest_tx_hashes
    global last_run_time
    show_log('{} checking'.format(wallet))
    try:
        blockchain = "ETH"
        wallet_address = wallet["address"]
        rate = wallet["reason"]
        message_header = f'Wallet:<a href="https://etherscan.io/address/{wallet_address}">{wallet_address}</a>\nReason:{rate}\n'
    except:
        blockchain, wallet_address = wallet.split(':')
        message_header = f'{wallet_address}\n'
    swaps = get_swaps(wallet_address, last_run_time, 2)
    for swap in swaps:
        behavious = "BUY" if swap["pair"]["token0"]["symbol"] != "WETH" else "SELL"
        token_name = swap["pair"]["token0"]["symbol"] if swap["pair"]["token0"]["symbol"] != "WETH" else \
        swap["pair"]["token1"]["symbol"]
        token_address = swap["pair"]["token0"]["id"] if swap["pair"]["token0"]["symbol"] != "WETH" else \
        swap["pair"]["token1"]["id"]
        tx = swap["transaction"]["id"]
        blocknumber = swap["transaction"]["blockNumber"]
        message = f'🚨 {message_header}Behaviour:{behavious}\nToken name:{token_name}\nChain:{blockchain}\nToken Address:<a href="https://etherscan.io/address/{token_address}">{token_address}</a>\n'
        send_telegram_notification(message, tx, token_address)
        latest_tx_hashes = add_item(latest_tx_hashes, tx, int(blocknumber))

    swaps = get_swaps(wallet_address, last_run_time, 3)
    for swap in swaps:
        behavious = "BUY" if swap["token0"]["symbol"] == "WETH" else "SELL"
        token_name = swap["token0"]["symbol"] if swap["token0"]["symbol"] != "WETH" else \
            swap["token1"]["symbol"]
        token_address = swap["token0"]["id"] if swap["token0"]["symbol"] != "WETH" else \
            swap["token1"]["id"]
        tx = swap["transaction"]["id"]
        blocknumber = swap["transaction"]["blockNumber"]
        message = f'🚨 {message_header}Behaviour:{behavious}\nToken name:{token_name}\nChain:{blockchain}\nToken Address:<a href="https://etherscan.io/address/{token_address}">{token_address}</a>\n'
        send_telegram_notification(message, tx, token_address)
        latest_tx_hashes = add_item(latest_tx_hashes, tx, int(blocknumber))

    return True

# Define some helper functions
def monitor_wallets():
    file_path = "../walletData.json"
    if not os.path.exists(file_path):
        open(file_path, 'w').close()

    global latest_tx_hashes
    global last_run_time

    latest_tx_hashes_path = "log/latest_tx_hashes.json"
    if os.path.exists(latest_tx_hashes_path):
        with open(latest_tx_hashes_path, "r") as f:
            latest_tx_hashes = json.load(f)

    last_run_time_path = "log/last_run_time.txt"
    if os.path.exists(last_run_time_path):
        with open(last_run_time_path, "r") as f:
            last_run_time = int(f.read())
    while True:
        try:
            # Read from file
            with open(file_path, 'r') as f:
                wallets = json.load(f)
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(wallet_check, wallet) for wallet in wallets]

                # wait for all tasks to complete
                for future in concurrent.futures.as_completed(futures):
                    future.result()

            # Save latest_tx_hashes to file
            with open(latest_tx_hashes_path, "w") as f:
                json.dump(latest_tx_hashes, f)

            # Update last_run_time
            last_run_time = int(time.time())
            with open(last_run_time_path, "w") as f:
                f.write(str(last_run_time - 150))

            # Sleep for 10 seconds
            time.sleep(10)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
            time.sleep(10)


def add_wallet(wallet_address, blockchain, rate=""):
    file_path = "../walletData.json"
    with open(file_path, 'a') as f:
        if rate:
            f.write(f'{blockchain}:{wallet_address}:{rate}\n')
        else:
            f.write(f'{blockchain}:{wallet_address}\n')


def remove_wallet(wallet_address, blockchain):
    file_path = "../walletData.json"
    temp_file_path = "temp.txt"
    with open(file_path, 'r') as f, open(temp_file_path, 'w') as temp_f:
        for line in f:
            if not (f'{blockchain}:{wallet_address}' in line.strip()):
                temp_f.write(line)
    os.replace(temp_file_path, file_path)


# Define the command handlers for the Telegram bot
def start(update, context):
    message = """
    👋 Welcome to the Ethereum and Binance Wallet Monitoring Bot!

    Use /add <blockchain> <wallet_address> to add a new wallet to monitor.

    Example: /add ETH 0x123456789abcdef

    Use /remove <blockchain> <wallet_address> to stop monitoring a wallet.

    Example: /remove ETH 0x123456789abcdef

    Use /list <blockchain> to list all wallets being monitored for a specific blockchain.

    Example: /list ETH or just /list

    Don't forget to star my Github repo if you find this bot useful! https://github.com/cankatx/crypto-wallet-tracker ⭐️
        """
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


def add(update, context):
    if len(context.args) < 2:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Please provide a blockchain and wallet address to add.")
        return

    blockchain = context.args[0].lower()
    wallet_address = context.args[1]

    if len(context.args) == 3:
        rate = context.args[2]
    else:
        rate = ""

    # Check if the wallet address is in the correct format for the specified blockchain
    if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"{wallet_address} is not a valid Ethereum wallet address.")
        return

    add_wallet(wallet_address, blockchain, rate)
    message = f'Added {wallet_address} to the list of watched {blockchain.upper()} wallets.'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


def remove(update, context):
    if len(context.args) < 2:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Please provide a blockchain and wallet address to remove.\nUsage: /remove ARB 0x123456789abcdef")
        return
    blockchain = context.args[0].lower()
    wallet_address = context.args[1]
    remove_wallet(wallet_address, blockchain)
    message = f'Removed {wallet_address} from the list of watched {blockchain.upper()} wallets.'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


def list_wallets(update, context):
    with open("..//walletData.json", "r") as f:
        wallets = [line.strip() for line in f.readlines()]
    if wallets:
        eth_wallets = []
        bsc_wallets = []
        arb_wallets = []
        for wallet in wallets:
            try:
                blockchain, wallet_address, rate = wallet.split(':')
            except:
                blockchain, wallet_address = wallet.split(':')
                rate = ""
            if blockchain == 'eth':
                eth_wallets.append([wallet_address, rate])
            elif blockchain == 'bsc':
                bsc_wallets.append([wallet_address, rate])
            elif blockchain == 'arb':
                arb_wallets.append([wallet_address, rate])

        message = "The following wallets are currently being monitored\n"
        message += "\n"
        if eth_wallets:
            message += "Ethereum Wallets:\n"
            for i, wallet in enumerate(eth_wallets):
                if wallet[1]:
                    message += f"{i + 1}. {wallet[0]}:{wallet[1]}\n"
                else:
                    message += f"{i + 1}. {wallet[0]}\n"
            message += "\n"
        if bsc_wallets:
            message += "Binance Coin Wallets:\n"
            if wallet[1]:
                message += f"{i + 1}. {wallet[0]}:{wallet[1]}\n"
            else:
                message += f"{i + 1}. {wallet[0]}\n"
        if arb_wallets:
            message += "ARBITRAM Wallets:\n"
            if wallet[1]:
                message += f"{i + 1}. {wallet[0]}:{wallet[1]}\n"
            else:
                message += f"{i + 1}. {wallet[0]}\n"
            message += "\n"
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
    else:
        message = "There are no wallets currently being monitored."
        context.bot.send_message(chat_id=update.message.chat_id, text=message)


# Set up the Telegram bot
from telegram.ext import Updater, CommandHandler

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Define the command handlers
start_handler = CommandHandler('start', start)
add_handler = CommandHandler('add', add)
remove_handler = CommandHandler('remove', remove)
list_handler = CommandHandler('list', list_wallets)

# Add the command handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(remove_handler)
dispatcher.add_handler(list_handler)

updater.start_polling()
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Telegram bot started.")

print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Monitoring wallets...")

url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
payload = {'chat_id': f'{TELEGRAM_CHAT_ID}',
           'text': "Stating bot...",
           'parse_mode': 'HTML'}
# response = requests.post(url, data=payload)
print('Stated bot')
monitor_wallets()
