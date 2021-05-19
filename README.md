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
2. Установите модули из файла requirements.txt (если не устанавливается box2d, попробуйте другую версию python (3.6.x 32bit))
3. Клонируйте репозиторий
4. Запустите файл main.py
## Box2D
Для запуска игры необходимо установить модуль Box2D, находящийся в в файле requirements.txt, но у меня иногда возникали траблы с установкой через pip. 
Если у вас возникает ошибка при установке через pip, попробуйте установить python более поздней версии (например, Python 3.8.2 (стоит у меня) или Python 3.6.*), что помогло мне.
## Проектирование игры
Скорость различных тел в pygame достаточно сложно регулировать.
Основные моменты, влияющие на линейную скорость передвижения шарика, например, могут быть:
- задержка между кадрами (или скорость, с которой сменяются кадры - FPS)
- расстояние, на которое перемещается шарик между двумя кадрами

Как известно, задержка между кадрами не может быть постоянной, так как она зависит напрямую от производительности компьютера.
Поэтому, для того, чтобы игры "смотрелась" на любой технике одинакого лучше менять FPS, но при этом расстояние, на которое перемещается шарик между двумя кадрами также должно меняться.
При чем изменение расстояния должно быть прямо пропорционально задержке между кадрами (deltatime, или как сокращено у меня в коде, dt)
В общем и целом, просто домножаем величины, изменяющиеся с течением времени, на этот параметр (dt).
### Коротко о том, как сделано у меня.
Для каждого кадра определяем разницу со временем предыдущего кадра - dt.
В функцию каждого из объектов для обновления (update) передаем этот параметр.
## Рисование стен
Изображение стены представляет собой прямоугольник. 
Стены предсталяют собой ломанную, для красивой отрисовки которой необходимо было соединять стены между собой, чтобы место стыка не выделялось.
Для этого изображение каждой стены было перерисовано так, чтобы на концах прямоугольника рисовались окружности с радиусами, равными половине толщине прямоугольника.
Тогда при наложении двух картинок стен место стыка становиться скругленным при любых углах расположения стен.
## Рисование теней
Для каждого объекта, для которого нужно отрисовать тень, создаем копию изображения, но предварительно задав необходимый темный оттенок.
Переопределюем метод ривоания в классе камеры для отрисовки, чтобы сначала рисовалась тень с некоторым смщением, а потом уже поверх основное изобрадение.
## Физика
Все объекты в игровом мире являются телами или связкой тел в движке BOX2D.
Для отрисовки в pygame каждый кадр изображение поворачивается на угол, равный углу поворота тела в физическом мире, а также устанавливаютя координаты в соответствии с координатами физического тела. 
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
Все характеристики машины: максисальная передняя скорость, максимальная задняя скорость, импульс при заносе, сила при движении, величины для расчета трения шин о землю - описаны в классе PlayerCar.
Каждый кадр производятся расчеты действующих сил на каждое колесо в зависимости от углов и текущего направления движения.
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
## Сохранение уровней
Информация о каждом уровне игры хранится в .svg файлах (я редактировал в Adobe Illustrator).
## Подсказки во время игры
Почти на каждом уровне есть подсказки, говорящие о том, что нужно делать на уровне.
