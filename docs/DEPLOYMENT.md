# راهنمای استقرار روی سرور و دامنه

خرید دامنه و تهیه سرور عملیات بیرون از کد هستند، اما پروژه برای استقرار آماده شده است. پیشنهاد ساده این است که فرانت و API روی یک دامنه باشند و Nginx درخواست‌های `/api/` را به FastAPI بفرستد.

## 1. اجرا با Docker روی Ubuntu

```bash
git clone <YOUR_REPOSITORY_URL> unireg
cd unireg
docker compose up -d --build
```

در این حالت برای تست مستقیم:

- Frontend: `http://SERVER_IP:5500`
- Backend: `http://SERVER_IP:8000`

## 2. Nginx برای دامنه

نمونه تنظیمات زیر را با دامنه خود جایگزین کنید:

```nginx
server {
    listen 80;
    server_name example.ir www.example.ir;

    root /var/www/unireg/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

فرانت در حالت دامنه به صورت خودکار API را از `/api` صدا می‌زند. در حالت localhost، API روی پورت `8000` استفاده می‌شود.

## 3. Cloudflare

پس از افزودن دامنه به Cloudflare:

1. Nameserverهای دامنه را به Nameserverهای Cloudflare تغییر دهید.
2. یک رکورد `A` برای دامنه اصلی به IP سرور بسازید.
3. در صورت نیاز برای `www` یک `CNAME` به دامنه اصلی بسازید.
4. SSL/TLS را پس از فعال شدن HTTPS روی `Full (strict)` قرار دهید.

## 4. HTTPS

روی Ubuntu می‌توانید از Certbot استفاده کنید:

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.ir -d www.example.ir
```

## 5. کنترل نهایی

پس از استقرار این مسیرها را بررسی کنید:

```text
https://example.ir/
https://example.ir/api/
https://example.ir/api/docs
https://example.ir/api/summary
https://example.ir/api/data
```
