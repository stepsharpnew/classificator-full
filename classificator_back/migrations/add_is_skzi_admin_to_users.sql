-- Добавление флага администратора СКЗИ для пользователей
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_skzi_admin BOOLEAN DEFAULT FALSE;
