# portfolio_ai/setup.sh
echo "Cloning Django project..."
git clone https://github.com/in2itsaurabh/AI_Powered_Portfolio_Website.git
cd AI_Powered_Portfolio_Website  # Adjust if necessary

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Opening in VS Code..."
code .

echo "Starting Django server..."
python manage.py runserver
