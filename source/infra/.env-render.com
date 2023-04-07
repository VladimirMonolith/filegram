POSTGRES_DB_NAME=postgres_test_ach3 # имя базы данных
POSTGRES_USER=postgres_test # логин для подключения к базе данных
POSTGRES_PASSWORD=rzC2zcyqTrAGRwHNqwj2PYGbx00ZlQUb # пароль для подключения к БД (установите свой)
POSTGRES_HOST=dpg-cgnvhqd269v5rj8v44u0-a
POSTGRES_PORT=5432 # порт для подключения к БД

SECRET=SECRET # ключ для кодирования и декодирования JWT-токенов
PASSWORD=PASSWORD # ключ для сброса пароля и его верификации

SMTP_USER=uhodbeey@gmail.com
SMTP_PASSWORD=shsxaxeopjmjwudr
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

REDIS_HOST=red-cgnvil5269v5rj8v8hj0
REDIS_PORT=6379