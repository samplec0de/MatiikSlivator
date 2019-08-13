import random
import sys
import time
import traceback
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from python3_anticaptcha import ImageToTextTask
import requests
import base64

# https://oauth.vk.com/token?grant_type=password&client_id=
# 3140623&client_secret=VeWdmVclDCtn6ihuP1nt&username=+7000000&password=*******

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 '
                  '(KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1',
}


def captcha_handler(captcha):
    """ При возникновении капчи вызывается эта функция и ей передается объект
        капчи. Через метод get_url можно получить ссылку на изображение.
        Через метод try_again можно попытаться отправить запрос с кодом капчи
    """
    print("Captcha url: {0}".format(captcha.get_url()))
    anti_captcha_key = 'ANTI_CAPTCHA_KEY'
    code = ImageToTextTask.ImageToTextTask(
        anticaptcha_key=anti_captcha_key).captcha_handler(
        captcha_base64=base64.b64encode(requests.get(captcha.get_url(), headers=headers).content).decode("utf-8"))
    print(code)
    if 'solution' in code and 'text' in code['solution']:
        key = code['solution']['text']
    else:
        key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    print(f"key={key}")
    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


pwd = open('token.txt', 'r').readlines()[0]
vk_session = vk_api.VkApi(token=pwd, app_id=3140623,
                          client_secret="VeWdmVclDCtn6ihuP1nt", captcha_handler=captcha_handler)
vk = vk_session.get_api()
long_poll = VkLongPoll(vk_session)
withdrawal = False
incorrect = False
last_task = 0


def main():
    global incorrect, withdrawal, last_task
    for event in long_poll.listen():
        try:
            if time.time() - last_task >= random.randint(100, 248):
                vk.messages.send(peer_id=-181521013, message="Вывод",
                                 random_id=random.randint(100000000, 2000000000))
                last_task = time.time()
            if event.type != VkEventType.MESSAGE_NEW or event.peer_id != -181521013:
                continue
            msg = event.message
            if msg.startswith("Неправильно"):
                incorrect = True
                continue
            if msg.startswith("Сколько будет"):
                if incorrect:
                    incorrect = False
                    continue
                last_task = time.time()
                expression = msg.replace("Сколько будет => ", "")
                expression = expression.replace(' ', '')
                signs = ['+', '-', '*', '/'] + [str(x) for x in range(0, 10)]
                for char in expression:
                    if char not in signs:
                        continue
                ans = eval(expression)
                print(f"{expression}={ans}")
                sleeping = random.randint(2, 5)
                print(f"Сплю {sleeping}")
                time.sleep(sleeping)
                if withdrawal:
                    withdrawal = False
                    continue
                vk.messages.send(peer_id=event.peer_id, message=ans, random_id=random.randint(100000000, 2000000000))
            elif msg.startswith("Молодец, счет:"):
                count = int(msg.replace("Молодец, счет: ", ''))
                print(f"Баланс {count}")
                if count >= random.randint(480, 1000):
                    vk.messages.send(peer_id=event.peer_id, message="Вывод",
                                     random_id=random.randint(100000000, 2000000000))
                    withdrawal = True
                    print(f"Сливаем {count}")
        except:
            print("Exception in polling:")
            print('-' * 60)
            traceback.print_exc(file=sys.stdout)
            print('-' * 60)


while True:
    try:
        main()
    except:
        print("Exception in main:")
        print('-' * 60)
        traceback.print_exc(file=sys.stdout)
        print('-' * 60)
