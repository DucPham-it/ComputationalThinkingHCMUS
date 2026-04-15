ALTER TABLE users
ADD COLUMN IF NOT EXISTS user_name VARCHAR(255);

UPDATE users
SET user_name = COALESCE(NULLIF(user_name, ''), split_part(email, '@', 1))
WHERE user_name IS NULL OR user_name = '';
