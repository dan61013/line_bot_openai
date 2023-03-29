import os

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from api.chatgpt import ChatGPT

line_bot_api = LineBotApi(os.getenv("LNIE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFAULT_TALKING", default="true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

# domain root
@app.route("/")
def home():
    return "Hello World"

@app.route("/webhook", methods=["POST"])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]
    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    
    if event.message.type != "text":
        return
    
    # if event.message.text == "啟動":
    #     working_status = True
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text="AI上線囉，來聊聊吧~")
    #     )
    
    # if event.message.text =="安靜":
    #     working_status = False
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text="掰掰~ 如果要找我的話，請再輸入「啟動」~")
    #     )
    #     return
    
    if working_status:
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg)
        )
    
if __name__ == "__main__":
    app.run()