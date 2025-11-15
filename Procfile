web: cd backend && (python3 manage.py migrate --noinput || exit 1) && (python3 manage.py create_dummy_data || echo 'Dummy data creation skipped') && python3 -m gunicorn pos_system.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120

