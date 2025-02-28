import os

PULSAR_URL = os.getenv('PULSAR_URL', 'pulsar://pulsar:6650')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@db_services:5432/users_db')
