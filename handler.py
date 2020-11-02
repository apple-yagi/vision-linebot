from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
import os
import json
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
secret_key = os.environ['LINE_CHANNEL_SECRET']

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret_key)


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def callback(event, context):
    try:
        signature = event["headers"]["X-Line-Signature"]
        event_body = event["body"]
        handler.handle(event_body, signature)
    except InvalidSignatureError as e:
        logger.error(e)
        return {"statusCode": 403, "body": "Invalid signature. Please check your channel access token/channel secret."}
    except Exception as e:
        logger.error(e)
        return {"statusCode": 500, "body": "exception error"}
    return {"statusCode": 200, "body": "request OK"}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )
