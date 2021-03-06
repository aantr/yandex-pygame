from resources import Resources


class Level:
    levels = [
        [Resources.path('res/maps/1.svg'),
         [
             ['Привет. В этой игре тебе нужно ограбить банк.',
              'Управление кнонками W, A, S, D для движения.'],
             ['У тебя есть запас энергии.',
              'Энергия тратится, например, при столкновении с полицией.',
              'Энергию можно пополнить, собирая её на дороге.',
              'Чтобы уйти от погони, можно уехать от машины или стрелять в нее.',
              'Попади 3 раза, чтобы уничтожить полицию.',
              'Стрелять огненными шарами на ЛКМ.'],
             ['Ты добрался до банка. Продержись возле него 10 секунд.']
         ]],
        [Resources.path('res/maps/2.svg'),
         [
             ['В этом уровне будет достаточно мало предметов, пополняющих энергию.',
              'Чтобы её пополнить ты должен дрифтить.',
              'Энергию пополняется только в случае, если за тобой ведётся погоня.']
         ]],
        [Resources.path('res/maps/3.svg'),
         [
             ['В этом уровне будет турель, которая стреляет взрывающимися шариками.',
              'К сожелению, её не получится как-то убрать с пути.', ]
         ]],
        [Resources.path('res/maps/4.svg'),
         [
             ['Впереди поверхность, ухудшающая контроль над машиной.', ]
         ]],
        [Resources.path('res/maps/5.svg'),
         [
             ['Упс, тупик.',
              'Чтобы разрушать такие стены, воспользуйся бомбой на клавишу B.',
              'Бомбы могут нанести тебе урон, если ты находишься слишком близко.',
              'Лучше всего просто заехать за стену.']
         ]],
    ]
