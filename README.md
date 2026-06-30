# RealEstate AI — Деплой на VPS

## Требования
- VPS 185.219.83.199
- Ubuntu 22.04+
- Node.js 20+, Python 3.11+, PM2, Nginx

---

## 1. Клонировать репозиторий

```bash
git clone <repo-url> /root/realestate-ai
cd /root/realestate-ai
```

---

## 2. Backend

```bash
cd /root/realestate-ai/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # заполнить переменные
```

**Запуск через PM2:**
```bash
pm2 start ecosystem.config.js
pm2 save
```

---

## 3. Frontend

```bash
cd /root/realestate-ai/frontend
npm install

cp .env.local.example .env.local
nano .env.local   # NEXT_PUBLIC_API_URL=https://api.YOURDOMAIN.com
                  # NEXT_PUBLIC_TG_BOT_USERNAME=YOUR_BOT

npm run build
pm2 start ecosystem.config.js
pm2 save
```

---

## 4. Nginx

```bash
cp /root/realestate-ai/nginx.conf /etc/nginx/sites-available/realestate
# заменить YOURDOMAIN.com на реальный домен
sed -i 's/YOURDOMAIN.com/yourdomain.com/g' /etc/nginx/sites-available/realestate

ln -s /etc/nginx/sites-available/realestate /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

---

## 5. SSL (Certbot)

```bash
certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

---

## 6. Переменные окружения

**Backend `.env`:**
```
ANTHROPIC_API_KEY=sk-ant-...
BOT_TOKEN=telegram_bot_token
MONO_TOKEN=monobank_token
MONO_WEBHOOK_SECRET=secret
JWT_SECRET=long_random_string_min_32_chars
DATABASE_URL=sqlite+aiosqlite:////root/realestate-ai/backend/realestate.db
```

**Frontend `.env.local`:**
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_TG_BOT_USERNAME=your_bot_username
```

---

## 7. PM2 автозапуск

```bash
pm2 startup
pm2 save
```

---

## Telegram Bot настройка

1. Создать бота через @BotFather
2. Команда `/setdomain` → указать домен сайта (для Login Widget)
3. Вставить `BOT_TOKEN` в `.env`
4. Вставить username бота в `.env.local`
