# Ограбление банка
Ты управляешь гоночной машиной с видом сверху, и тебе нужно ограбить банк, объезжая различные препятствия:
- боты - полицейские машины
- турели
- скользкая дорога

У тебя есть запас энергии, который необходимо сохранить в процессе игры.
Энергия теряется при столкновении, попадания пули и тд.
Энергию можно пополнить, собирая предметы на уровне.
## Установка
1. Установите Python 3.x (лучше 32 бит с ним меньше проблем)
2. Установите модули из файла requirements.txt (если не устанавливается box2d, попробуйте другую версию python (3.6.x 32bit))
3. Клонируйте репозиторий
4. Запустите файл main.py
<pre><code>git clone https://github.com/aantr/yandex-pygame
cd yandex-pygame
pip install -r requirements.txt
python main.py
</code></pre>
## Предупреждение
Python очень медленный ЯП, поэтому вот что можно предпринять на слабых ПК для повышения FPS:
- в файле настроек (configurations.py) попробовать поставить поменьше (или побольше, если вы запускаете на компьютерах NASA :) ) значение FPS (изменение этого значения никак не повлияет на другие параметры игры, 
то есть скорость объектов не изменится, а изменится только частота обновления кадров)
- в файле настроек (configurations.py) поменять разрешения на более маленькое
- в файле настроек (configurations.py) поставить значение DRAW_SHADOWS на 0 для отключения теней (хотя без них графон ужасный, поэтому не советую, лучше уменьшить разрешение)

Не рекомендую изменять значение PPM в файле настроек, так как это может плохо повлиять на работу игры.
## Установка Box2D
Для запуска игры необходимо установить модуль Box2D, находящийся в файле requirements.txt, но у меня иногда возникали траблы с установкой через pip. 
Если у вас возникает ошибка при установке через pip, попробуйте установить python более поздней версии (например, Python 3.8.2 (стоит у меня) или Python 3.6.*), что помогло мне.
## Проектирование игры
Задержка между кадрами не может быть постоянной, так как она зависит напрямую от производительности компьютера.
Для того, чтобы игры "смотрелась" на любой технике одинаково лучше менять FPS, но при этом расстояние, на которое перемещается шарик между двумя кадрами также должно меняться.
При чем изменение расстояния должно быть прямо пропорционально задержке между кадрами (deltatime, или как сокращено у меня в коде, dt)
В общем и целом, просто умножаем величины, изменяющиеся с течением времени, на этот параметр (dt).

Для каждого кадра определяем разницу со временем предыдущего кадра - dt.
В функцию каждого из объектов для обновления (update) передаем этот параметр.
## Рисование стен
Изображение стены представляет собой прямоугольник. 
Стены представляют собой ломанную, для красивой отрисовки которой необходимо было соединять стены между собой, чтобы место стыка не выделялось.
Для этого изображение каждой стены было перерисовано так, чтобы на концах прямоугольника рисовались окружности с радиусами, равными половине толщине прямоугольника.
Тогда при наложении двух картинок стен место стыка становиться скругленным при любых углах расположения стен.

Так как стена бывает достаточно большой, изображение нескольких будет занимать много оперативной памяти.
Чтоб этого избежать, для стен с одинаковым углом наклона и длиной используем одно и то же изображение.
## Рисование теней
Для каждого объекта, для которого нужно отрисовать тень, создаем копию изображения, предварительно наложив фильтры.
Переопределяем метод рисования в классе камеры для отрисовки, чтобы сначала рисовалась тень с некоторым смещением, а потом уже поверх основное изображение.

В файле настроек можно кастомизировать тени, попробовать применить разные фильтры, а также задать цвет тени для машины игрока.
## Физика
Все объекты в игровом мире являются телами или связкой тел в движке BOX2D.
Для отрисовки в pygame каждый кадр изображение поворачивается на угол, равный углу поворота тела в физическом мире, а также устанавливаются координаты в соответствии с координатами физического тела. 
В игре реализовано взаимодействие с физическим движком BOX2D для лучшего геймплея:
- разгон, торможение
- дрифт
- столкновение с объектами
- взрывы с помощью метода RayCast (далее подробно)
## RayCast
Метод пускания лучей из одной точки в другую в игровом мире для нахождения столкновений.
Используется для симуляции взрывов бомб, огненных шаров (выпускаем определенное количество лучей из точки, где находится взрывающийся объект на небольшое расстояние и применяем импульс телу, с которым столкнётся луч), а также при отслеживании полицией вашу машину.
Преимуществом данного метода является реалистичная механика игры (взрыв не работает сквозь стены, и полиция не может "видеть" вас через стены и другие объекты).
## Механика машины
Любая машина в игре по строена из 5 тел: основное тело и 4 колеса.
Все характеристики машины: максимальная передняя скорость, максимальная задняя скорость, импульс при заносе, сила при движении, величины для расчета трения шин о землю - описаны в классе PlayerCar.
Каждый кадр производятся расчеты действующих сил на каждое колесо в зависимости от углов и текущего направления движения.

В файле настроек можно попробовать поизменять различные параметры машины игрока, чтобы достичь более правдоподобного поведения.
## Игровые эффекты
- анимация при исчезновении объектов
- покадровая анимация объекта
- частицы во время заноса машины
- взрывы
- мерцание экрана во время погони
- тени (можно отключить в файле настроек)
- эффект "тряски" камеры во время взрыва бомб, огненных шаров
## Графический интерфейс
Для действий с интерфейсом игры было реализованы:
- анимированные кнопки, изменяющие состояние при наведении курсора
- анимированные переходы через экран загрузки между состояниями игры
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
## Сохранение уровней
Информация о каждом уровне игры хранится в .svg файлах (я редактировал в Adobe Illustrator).
## Подсказки во время игры
Почти на каждом уровне есть подсказки, говорящие о том, что нужно делать на уровне.
