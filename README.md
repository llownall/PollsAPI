# PollsAPI

### Некоторые моменты

- После полного "разворачивания" создается суперюзер `admin:admin` (id 1) и 3 обычных пользователя (id 2-4)
- Для CRUD операций с опросами/вопросами/ответами требуется добавить в заголовки запросов `Authorization: Token <token>`. Токен можно получить по /api/obtain-token/ 

### Требования

- python 3.8+
- python3-pip, python3-venv
- Git

### Запуск локально

Описан запуск из командной строки Linux (правда, по памяти):

`git clone https://github.com/llownall/PollsAPI.git`

`cd PollsAPI/`

`python3 -m venv venv`

`source venv/bin/activate`

`pip3 install -r requirements.txt`

`python3 manage.py migrate`

`python3 manage.py runserver`

Ура, у вас работает сервер по адресу http://127.0.0.1:8000/ !

Документация к API - http://127.0.0.1:8000/swagger-ui/
