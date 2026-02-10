#!/bin/bash
# PostgreSQL Database Setup Script

echo "🔄 Setting up PostgreSQL database..."

# Check if database exists
DB_EXISTS=$(psql -U postgres -lqt 2>/dev/null | cut -d \| -f 1 | grep -w fashion_shop_db)

if [ -z "$DB_EXISTS" ]; then
    echo "Creating database and user..."
    psql -U postgres <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'fashion_user') THEN
        CREATE USER fashion_user WITH PASSWORD 'fashion_password123';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE fashion_shop_db OWNER fashion_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fashion_shop_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fashion_shop_db TO fashion_user;
\c fashion_shop_db
GRANT ALL ON SCHEMA public TO fashion_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO fashion_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO fashion_user;

\q
EOF
    echo "✅ Database created!"
else
    echo "ℹ Database already exists, granting permissions..."
    psql -U postgres -d fashion_shop_db <<EOF
GRANT ALL ON SCHEMA public TO fashion_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO fashion_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO fashion_user;
\q
EOF
fi

echo "✅ PostgreSQL setup complete!"
