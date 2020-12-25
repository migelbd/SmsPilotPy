![Upload Python Package](https://github.com/migelbd/SmsPilotPy/workflows/Upload%20Python%20Package/badge.svg)
# SmsPilotPy

Не официальный клиент API проекта SMSPilot 

https://smspilot.ru/

### Установка
```shell
pip install sms-pilot-py
```

### Пример использования
```python
from sms_pilot import SmsPilot

API_KEY = 'XXXXXXXXXXXXYYYYYYYYYYYYZZZZZZZZXXXXXXXXXXXXYYYYYYYYYYYYZZZZZZZZ'

api = SmsPilot(API_KEY, default_sender='INFORM')

result = api.send_message(79201112223, 'Привет, мир!')
print(result.status, result.get_status_verbose()) 
print(result.cost)

# Запрос PING
ping_response = api.ping(79201112223)
# time.sleep(10)
ping_result = api.check_ping_hlr(ping_response.server_id)

if ping_result.is_ot_of_service():
    print('Не обслуживается')
```

### Отправка нескольких сообщений
```python
from sms_pilot import SmsPilot
from sms_pilot import Callback

API_KEY = 'XXXXXXXXXXXXYYYYYYYYYYYYZZZZZZZZXXXXXXXXXXXXYYYYYYYYYYYYZZZZZZZZ'

api = SmsPilot(API_KEY, default_sender='INFORM')

api.add_message(79221112233, 'Hello')
api.add_message(79221112222, 'Привет', sender='MYSENDER')
api.add_message(79122334434, 'Привет мир', id=455, callback=Callback('https://smspilot.ru/callback', 'POST'))
result = api.send_messages()

print(result.cost)

for msg_result in result.send:
    print(msg_result.status, msg_result.id)
```

Для использования требуется регистрация на https://smspilot.ru

Больше информации о API на http://www.smspilot.ru/apikey.php