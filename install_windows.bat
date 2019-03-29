pip install virtualenv

virtualenv poisk_venv
call poisk_venv\Scripts\activate
pip install -r requirements.txt
python -c "import nltk;nltk.download(\"punkt\")"
call poisk_venv\Scripts\deactivate.bat

python -c "input(\"Установка выполнена успешно\nНажмите любую клавишу\")"
 
