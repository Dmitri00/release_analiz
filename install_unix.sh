pip3 install virtualenv

virtualenv poisk_venv
source poisk_venv/bin/activate
pip3 install -r requirements.txt
python -c 'import nltk;nltk.download("punct")'

virtualenv deactivate
python -c 'input("Установка выполнена успешно\nНажмите любую клавишу")'
