# Ограбление банка
Ты управляешь гоночной машиной с видом сверху, и тебе нужно ограбить банк, объезжая различные препядствия:
- боты - полицейские машины
- турели
- скользкая дорога

У тебя есть запас энергии, который необходимо сохранить втечение игры.
Энергия теряется при столкновении, попадания пули и тд.
Энергию можно пополнить, собирая предметы на уровне.
## Предупреждение
Python очень медленный язык сам по себе, поэтому вот что можно предпринять на слабых ПК для повышения фпс:
- в файле констант (constants.py) поменять разрешения на более маленькое
- в файле констант (constants.py) поставить значение DRAW_SHADOWS на 0 для отключения теней (хотя без них графон ужасный, поэтому не советую, лучше уменьшить разрешение)

Крайне не рекомендую изменять другие значения в файле констант, так как это может плохо повлиять на работу игры.
## Установка
1. Установите Python 3.x (лучше 32 бит с ним меньше проблем)
2. Установите модули из файла requirenments.txt (если не устанавливается box2d, попробуйте другую версию python (3.6.x 32bit))
3. Клонируйте репозиторий
4. Запустите файл main.py
## Box2D
Для запуска игры необходимо установить модуль Box2D, находящийся в в файле requirements.txt, но у меня иногда возникали траблы с установкой через pip. 
Если у вас возникает ошибка при установке через pip, попробуйте установить python более поздней версии (например, Python 3.8.2 (стоит у меня) или Python 3.6.*), что помогло мне.
## Сохранение уровней
Информация о каждом уровне игры хранится в .svg файлах.
## Подсказки во время игры
Почти на каждом уровне есть подсказки, говорящие о том, что нужно делать на уровне.
## Физика
В игре реализовано взаимодействие с физическим движком BOX2D для лучшего геймплея:
- разгон, торможение
- дрифт
- столкновение с объектами
- взрывы с помощью метода RayCast (далее подробно)
## RayCast
Метод пускания лучей из одной точки в другую в игровом мире для нахождения определенных колизий.
Используется для симуляции взрывов бомб, огненных шаров (выпускаем определенное количество лучей из точки, где находится взрывающийся объект на небольшое рассояние и применяем импульс телу, с которым столкнолся луч), а также при отслеживании полицией вашу машину.
Преймуществом данного метода является реалистичная механика игры (взрыв не работает сквозь стены, и полиция не может "видеть" вас через стены и другие объекты).
## Механика машины
Любая машина в игре по строена из 5 тел: основное тело и 4 колеса, что добавляет реалистичности в повороте колес и "погибании" игрока.
Производятся расчеты действующих сил на каждое колесо, что позволило добавить в геймплей занос автомобиля.
## Игровые эффекты
- анимация при исчезновении объектов
- покадровая анимация объекта
- парктиклы во время заноса машины
- взрывы
- мерцание экрана во время погони
- тени (можно отключить в файле констант)
- эффект "тряски" камеры во время взрыва бомб, огненных шаров
## Графический интерфейс
Для действий с интерфейсом игры было реализованы:
- анимированные кнопки, изменяющие состояние при наведении курсора
- анимированные переходы через экран загрузки между состояними игры
- миникарта
## Звуки
- фоновые
- во время стрельбы
- во время заноса
- взрыв
- при других эвентах
## Виртуальная валюта
Проходя уровни и грабя деньги, ты можешь позволить купить себе скины в магазине.
## Сохранение игры
Сохранение игры хранится в файле save.bin, так что, для удаления прогресса, достаточно удалить этот файл перед запуском игры.
