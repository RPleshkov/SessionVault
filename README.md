## Установка

### Установка Docker
```bash
curl -sSL https://get.docker.com/ | sh
```

### Установка uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Установка Python
```bash
uv python install 3.13
```

### Установка зависимостей
```bash
uv sync
```

## Настройка

### Копирование конфигурации
```bash
cp .env.example .env
```

### Запуск Docker
```bash
docker compose up -d
```

### Настройка прав доступа

```bash
sudo chown -R 5050:5050 ./_data/pgadmin
sudo chmod -R 700 ./_data/pgadmin

sudo chown -R 999:999 ./_data/postgres
sudo chmod -R 700 ./_data/postgres
```

### Перезапуск Docker
```bash
docker compose down
docker compose up -d
```

### Применение миграций и генерация сертификатов
```bash
bash scripts/entrypoint.sh
```

## Запуск приложения
```bash
uv run fastapi run app/main.py
```