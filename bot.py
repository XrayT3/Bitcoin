import telebot, logging
from aiohttp import web
import ssl
import json, urllib.request
token = ""


WEBHOOK_HOST = '85.143.175.123'
WEBHOOK_PORT = 80  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(token)


bot = telebot.TeleBot(token)


app = web.Application()


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle)

@bot.message_handler(commands=['btc'])
def get_currency(message):
    with urllib.request.urlopen("https://blockchain.info/ru/ticker") as url:
        data = json.loads(url.read().decode())
    bot.send_message(message.chat.id, "Курс биткойна:\nПокупка: %s руб.\nПродажа: %s руб."%(str(data.get("RUB").get("buy")), str(data.get("RUB").get("sell"))) )
@bot.message_handler(commands=["copyright"])
def copyright(message):
    bot.send_message(message.chat.id, "@name")



bot.remove_webhook()


bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
