pip3 install virtualenv

virtualenv poisk_venv
if [ $? -ne "0" ]
then
	python3 -m venv poisk_venv
fi
source poisk_venv/bin/activate
pip3 install -r requirements.txt
python -c 'import nltk;nltk.download("punkt")'

virtualenv deactivate
if [ $? -ne "0" ]
then
	deactivate
fi
python -c 'input("Установка выполнена успешно\nНажмите любую клавишу")'
