from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
import os
import io
import json
import math
import requests
from PIL import Image
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
        global detection_type
        detection_type = event["queryStringParameters"]["type"]

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


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    i = Image.open(io.BytesIO(message_content.content))
    filename = '/tmp/' + message_id + '.jpg'
    i.save(filename)

    upload_file = {'file': open(filename, 'rb')}
    vision_api_url = os.environ['VISION_API_URL'] + detection_type
    response = requests.post(vision_api_url, files=upload_file)

    data = response.json()
    key_list = list(data["responses"][0].keys())
    text = "結果はこちら\n" + pick_result(data["responses"][0][key_list[0]])

    os.remove(filename)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text)
    )


def pick_result(results) -> str:
    result_text = "\n概要  一致率"
    for result in results:
        text = result["description"] + " " + str(math.floor(result["score"] * 10000)
                                                 / 100) + "%"
        result_text += "\n" + text

    return result_text
