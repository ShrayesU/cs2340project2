echo "Installing Packages"
python3 -m pip install -r requirements.txt

echo "Migrating DB"
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo "Collecting static files"
python3 manage.py collectstatic --noinput

echo "Generating Translation Files"
python3 makemessages -a  

echo "Compiling Translations"
python3 compilemessages  