# AI-assistant(Telegram Bot) https://t.me/yandex_proect_bot
## Описание проекта
Ваш личный помощник который не только принимает текст но еще и слушает вас, у вас есть некие ограничения 
5 аудиоблоков, 1500 символов И 1500 Ттокенов, также в боте есть режим без GPT отправки, можно либо текст в голос
или же наоборот голос в текст, так же бот хранит всю вашу переписку с ним.

## Используемые библиотеки
![PyPI - Version](https://img.shields.io/pypi/v/aiogram?style=flat&label=aiogram&labelColor=red&color=green)<br>
![PyPI - Version](https://img.shields.io/pypi/v/requests?style=flat&label=requests&labelColor=red&color=green)<br>
![PyPI - Version](https://img.shields.io/pypi/v/python-dotenv?label=python-dotenv&labelColor=red&color=green)<br>


## Как запустить проект у себя
Вам нужно иметь версию Pytnon 3.12(Последняя версия). Установить все необходимые библиотеки:<br>
1. Установить aiogram<br>
  ```
  pip install aiogram
  ```
2. Установить requests
  ```
  pip install requests
  ```
3. Установить python-dotenv
 ```
 pip install python-dotenv
 ```
**Дополнительные библиотеки которые есть в проекте, предварительно устанавливать не нужно, их нужно только импортировать.**
## Файл .env
*Создать обычный файл дать название .env*<br>
Здесь вам нужно указать:<br> 
+ TOKEN **(Токен бота)**
+ IAM_TOKEN 
+ FOLDER_ID
+ DB_FILE 

**Все константы которые указаны используются в проекте, поэтому их название копируйте отсюда!**
