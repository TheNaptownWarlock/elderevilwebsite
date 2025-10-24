-- Add bio field to users table
ALTER TABLE users ADD COLUMN bio TEXT;

-- Add password hint field
ALTER TABLE users ADD COLUMN password_hint TEXT;

-- Add verification fields for email verification (keeping for future use)
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;
ALTER TABLE users ADD COLUMN verification_token TEXT;
ALTER TABLE users ADD COLUMN verification_expires TIMESTAMPTZ;

-- Add password reset fields
ALTER TABLE users ADD COLUMN reset_token TEXT;
ALTER TABLE users ADD COLUMN reset_expires TIMESTAMPTZ;
