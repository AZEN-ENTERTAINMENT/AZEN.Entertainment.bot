#!/bin/bash

# اسکریپت راه‌اندازی گیت و ایجاد مخزن
echo "راه‌اندازی مخزن گیت..."

# بررسی اینکه آیا گیت نصب است
if ! command -v git &> /dev/null; then
    echo "خطا: گیت نصب نیست. لطفاً ابتدا گیت را نصب کنید."
    exit 1
fi

# بررسی اینکه آیا مخزن گیت قبلاً راه‌اندازی شده است
if [ -d ".git" ]; then
    echo "مخزن گیت قبلاً راه‌اندازی شده است."
else
    # راه‌اندازی مخزن گیت
    git init
    echo "مخزن گیت با موفقیت راه‌اندازی شد."
fi

# افزودن فایل‌ها به مخزن
git add .

# ایجاد کامیت اولیه
git commit -m "کامیت اولیه: راه‌اندازی پروژه ربات تلگرام AZEN Entertainment"

echo "ربات تلگرام AZEN Entertainment با موفقیت در مخزن گیت ذخیره شد."
echo "برای اضافه کردن یک مخزن از راه دور (remote repository)، از دستورات زیر استفاده کنید:"
echo "git remote add origin YOUR_REMOTE_REPOSITORY_URL"
echo "git push -u origin main"

exit 0
