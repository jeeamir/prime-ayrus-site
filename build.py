#!/usr/bin/env python3
"""Сборка сайта Prime Ayrus Travel.

    python3 build.py

Тексты, цена, программа и контакты — в блоке «Данные». Карта маршрута строится
из контуров стран Natural Earth (файл map-countries.json рядом, из пакета
world-atlas, лицензия ISC). Результат — готовые .html рядом с этим файлом.
"""
import json
from math import cos, radians, hypot
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent

# ───────────────────────────── Данные ─────────────────────────────
PHONE = '+7 707 439-59-79'
PHONE_HREF = 'tel:+77074395979'
EMAIL = 'travelayrus@gmail.com'
ADDRESS = 'г. Алматы, ул. Ч. Валиханова, 58'
HOURS = 'Пн–пт, 9:00–18:00'
LEGAL = 'ИП «PRIME AYRUS TRAVEL», ИИН 860228300934'
LICENSE_NO = 'KZ21TWG00012021'
LICENSE = 'Уведомление о турагентской деятельности №&nbsp;' + LICENSE_NO
PRICE = '260 000 ₸'
INSTAGRAM = ''  # рабочая ссылка на профиль; пусто — ссылка не показывается
MAP_URL = 'https://2gis.kz/almaty/search/' + quote('Валиханова 58')


def wa(text='Здравствуйте! Хочу узнать о туре по Турции.'):
    return 'https://wa.me/77074395979?text=' + quote(text)


NAV = [('tour.html', 'Программа'), ('about.html', 'О компании'),
       ('agents.html', 'Агентствам'), ('contacts.html', 'Контакты')]

INCLUDED = ['6 ночей в отелях 4–5★', 'Завтраки и ужины по маршруту', 'Трансферы и транспорт между городами',
            'Обзорные экскурсии в четырёх городах', 'Гид-историк на весь маршрут', 'Медицинская страховка',
            'Термальный бассейн отеля в Памуккале']
NOT_INCLUDED = ['Международные авиабилеты', 'Обеды', 'Входные билеты в музеи и на исторические объекты',
                'Дополнительные экскурсии и развлечения']
EXTRAS = ['Шар над Каппадокией', 'Шар над Памуккале', 'Полёт на вертолёте', 'Параглайдинг',
          'Джип-сафари с панорамой', 'Панорамная площадка', 'Прогулки на животных', 'Турецкая ночь',
          'Шоу-программы', 'Обеды']

# (город на карте, маршрут, заголовок, текст, по желанию)
DAYS = [
    ('antalya', 'Анталия', 'Прилёт', 'Встреча в аэропорту, трансфер в отель и свободный вечер у моря.', ''),
    ('pamukkale', 'Анталия — Памуккале', 'Калеичи и Дюден', 'Старый город Калеичи и водопад Дюден, днём переезд в Памуккале, вечером термальный бассейн отеля.', ''),
    ('pamukkale', 'Памуккале', 'Террасы и Иераполис', 'Белые травертиновые террасы, античный Иераполис и театр на склоне.', 'По желанию: бассейн Клеопатры'),
    ('cappadocia', 'Дорога в Каппадокию', 'Через Анатолию', 'Переезд через плато Анатолии, вечер и ночь в отеле Каппадокии.', ''),
    ('cappadocia', 'Каппадокия', 'Долины и подземный город', 'Подземный город, крепость Учхисар и долины с каменными столбами.', 'По желанию: шар на рассвете'),
    ('konya', 'Конья — Анталия', 'Комплекс Мевланы', 'Мавзолей и музей Мевланы в Конье, вечером возвращение в Анталию.', ''),
    ('antalya', 'Анталия', 'Вылет', 'Трансфер в аэропорт и дорога домой.', ''),
]

SEE = [('px-balloons-sunset.jpg', 'Шары на рассвете'), ('px-pamukkale-pools.jpg', 'Травертины Памуккале'), ('px-kaleici-street.jpg', 'Улочки Калеичи'),
       ('px-hierapolis-theatre.jpg', 'Театр Иераполиса'), ('px-fairy-chimneys.jpg', 'Каменные столбы'), ('px-mevlana.jpg', 'Комплекс Мевланы'),
       ('px-hadrian-gate.jpg', 'Ворота Адриана'), ('px-uchisar-night.jpg', 'Каппадокия вечером'), ('px-konyaalti.jpg', 'Пляж Коньяалты')]

FAQ = [
    ('Что входит в стоимость?', 'Шесть ночей в отелях 4–5★, завтраки и ужины, трансферы и транспорт между городами, обзорные экскурсии в четырёх городах, гид-историк, медицинская страховка и термальный бассейн отеля в Памуккале.'),
    ('Что оплачивается отдельно?', 'Международные авиабилеты, обеды, входные билеты в музеи и на исторические объекты, дополнительные экскурсии и развлечения.'),
    ('Входит ли полёт на шаре?', 'Нет, это дополнительная услуга. Полёт бывает только при подходящей погоде, цену на ваши даты назовёт менеджер.'),
    ('Можно ли поехать с детьми?', 'Да, в том числе с детьми до пяти лет — условия уточняйте у менеджера. Учтите, что в программе длинные переезды.'),
    ('Как забронировать?', 'Напишите менеджеру или оставьте заявку. Подберём дату группы, заключим договор, выдадим ваучер и расскажем, как внести оплату.'),
    ('Может ли программа измениться?', 'Порядок и время посещения объектов иногда меняются по организационным причинам. Города и основные экскурсии остаются.'),
]

# ───────────────────────────── Карта ─────────────────────────────
# Вся западная и центральная Турция; камера двигается по дням программы.
LON0, LON1, LAT0, LAT1 = 24.5, 42.0, 34.2, 42.6
K = 100
KX = K * cos(radians(38))
W, H = round((LON1 - LON0) * KX), round((LAT1 - LAT0) * K)


def P(lon, lat):
    return (lon - LON0) * KX, (LAT1 - lat) * K


def countries_svg():
    topo = json.loads((ROOT / 'map-countries.json').read_text())
    (sx, sy), (tx, ty) = topo['transform']['scale'], topo['transform']['translate']
    arcs = []
    for arc in topo['arcs']:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a[1:] if pts else a)
        return pts

    out = []
    for g in topo['objects']['countries']['geometries']:
        polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']] if g['type'] == 'Polygon' else []
        d = ''
        for poly in polys:
            for r in poly:
                pts = ring(r)
                lons = [p[0] for p in pts]; lats = [p[1] for p in pts]
                if max(lons) < LON0 - 1 or min(lons) > LON1 + 1 or max(lats) < LAT0 - 1 or min(lats) > LAT1 + 1:
                    continue
                kept, last = [], None
                for lon, lat in pts:
                    q = P(lon, lat)
                    if last is None or hypot(q[0] - last[0], q[1] - last[1]) > .45:
                        kept.append(q); last = q
                if len(kept) > 2:
                    d += 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in kept) + 'Z'
        if d:
            cls = 'land land--tr' if g['properties']['name'] == 'Turkey' else 'land'
            out.append(f'<path class="{cls}" d="{d}" vector-effect="non-scaling-stroke"/>')
    return ''.join(out)


CITIES = {  # ключ: (название, дни, долгота, широта)
    'antalya': ('Анталия', '1, 7', 30.71, 36.89),
    'pamukkale': ('Памуккале', '2–3', 29.12, 37.92),
    'cappadocia': ('Каппадокия', '4–5', 34.83, 38.64),
    'konya': ('Конья', '6', 32.49, 37.87),
}
# Отрезки пути: откуда, куда, контрольная точка кривой (долгота, широта).
LEGS = {
    'a': ('antalya', 'pamukkale', (30.35, 37.75)),
    'b': ('pamukkale', 'cappadocia', (31.9, 39.75)),
    'c': ('cappadocia', 'konya', (33.85, 37.95)),
    'd': ('konya', 'antalya', (31.95, 36.95)),
}
# День: город, где ночуем, отрезки этого дня, фото.
DAY_MAP = [('antalya', '', 'px-konyaalti.jpg'), ('pamukkale', 'a', 'px-hadrian-gate.jpg'),
           ('pamukkale', '', 'px-pamukkale-pools.jpg'), ('cappadocia', 'b', 'px-uchisar-sunset.jpg'),
           ('cappadocia', '', 'px-balloons-sunset.jpg'), ('antalya', 'cd', 'px-mevlana.jpg'),
           ('antalya', '', 'px-kaleici-street.jpg')]
PLACES = [('Анкара', 32.85, 39.93), ('Измир', 27.14, 38.42), ('Стамбул', 28.98, 41.01),
          ('Мерсин', 34.64, 36.8), ('Бодрум', 27.43, 37.03)]
SEAS = [('Средиземное море', 31.6, 35.75), ('Эгейское море', 25.7, 38.6), ('Чёрное море', 34.0, 42.2)]


def leg_d(key):
    a, b, c = LEGS[key]
    (x0, y0), (x1, y1) = P(*CITIES[a][2:]), P(*CITIES[b][2:])
    cx, cy = P(*c)
    return f'M{x0:.1f} {y0:.1f}Q{cx:.1f} {cy:.1f} {x1:.1f} {y1:.1f}'


MAP_HTML = '''<div class="rmap rv" data-rmap>
  <div class="rmap__panel">
    <div class="rmap__head"><span class="pill" data-k="n">День 1 из 7</span>
      <div class="rmap__ctl"><button type="button" class="rbtn" data-act="prev" aria-label="Предыдущий день">{back}</button>
        <button type="button" class="rbtn rbtn--play" data-act="play" aria-label="Проиграть маршрут"><svg class="i-play" viewBox="0 0 16 16"><path d="M5 3.5v9l7.5-4.5z" fill="currentColor"/></svg><svg class="i-pause" viewBox="0 0 16 16"><path d="M5 3.5v9M11 3.5v9" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg></button>
        <button type="button" class="rbtn" data-act="next" aria-label="Следующий день">{arrow}</button></div></div>
    <div class="rmap__pic"><img data-k="img" src="{img}" alt="{route}" loading="lazy"></div>
    <div class="rmap__txt" aria-live="polite"><h3 data-k="route">{route}</h3><p><b data-k="title">{title}.</b> <span data-k="text">{text}</span></p><p class="opt" data-k="opt" hidden></p></div>
    <div class="tl"><div class="tl__bar"><i></i></div><div class="tl__days">{pills}</div></div>
  </div>
  <div class="rmap__map">
    <svg viewBox="{vb}" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Карта маршрута: Анталия — Памуккале — Каппадокия — Конья — Анталия">
      {lands}
      {legs}
      {dots}
      <g class="marker" transform="translate({ax:.1f} {ay:.1f})"><circle class="marker__pulse" r="9" vector-effect="non-scaling-stroke"/><circle class="marker__dot" r="7"/></g>
    </svg>
    <div class="rmap__lbls">{lbls}</div>
    <span class="rmap__credit">Карта: Natural Earth</span>
  </div>
  <script type="application/json" class="rmap__data">{data}</script>
</div>'''


def map_card():
    legs = ''.join(f'<path class="leg-base" d="{leg_d(k)}"/>' for k in LEGS)
    legs += ''.join(f'<path class="leg" data-leg="{k}" d="{leg_d(k)}" pathLength="1"/>' for k in LEGS)
    dots = ''.join(f'<circle class="city" data-city="{k}" cx="{P(lo, la)[0]:.1f}" cy="{P(lo, la)[1]:.1f}" r="5" vector-effect="non-scaling-stroke"/>'
                   for k, (_n, _d, lo, la) in CITIES.items())
    ax, ay = P(*CITIES['antalya'][2:])
    # Вид по умолчанию (без скрипта) — весь маршрут.
    x0, y0 = P(27.4, 40.3)
    x1, y1 = P(36.6, 35.8)
    vbw, vbh = x1 - x0, y1 - y0

    def pos(x, y):  # положение подписи в % для вида по умолчанию
        return f'left:{(x - x0) / vbw * 100:.2f}%;top:{(y - y0) / vbh * 100:.2f}%'

    lbls = ''
    for k, (name, dd, lo, la) in CITIES.items():
        x, y = P(lo, la)
        lbls += (f'<button type="button" class="mlbl mlbl--city" data-city="{k}" data-x="{x:.1f}" data-y="{y:.1f}" style="{pos(x, y)}">'
                 f'<b>{dd}</b>{name}</button>')
    for name, lo, la in PLACES:
        x, y = P(lo, la)
        lbls += f'<span class="mlbl mlbl--place" data-x="{x:.1f}" data-y="{y:.1f}" style="{pos(x, y)}">{name}</span>'
    for name, lo, la in SEAS:
        x, y = P(lo, la)
        lbls += f'<span class="mlbl mlbl--sea" data-x="{x:.1f}" data-y="{y:.1f}" style="{pos(x, y)}">{name}</span>'
    days = []
    for i, ((_s, route, title, text, opt), (city, legs_k, img)) in enumerate(zip(DAYS, DAY_MAP)):
        days.append({'n': i + 1, 'city': city, 'legs': legs_k, 'img': 'images/' + img, 'route': route,
                     'title': title, 'text': text, 'opt': opt})
    pills = ''.join(f'<button type="button" class="tl__d" data-day="{d["n"] - 1}" aria-label="День {d["n"]}: {d["route"]}">{d["n"]}</button>' for d in days)
    data = json.dumps({'days': days, 'cities': {k: [round(c, 1) for c in P(lo, la)] for k, (_n, _d, lo, la) in CITIES.items()},
                       'vb': [round(x0, 1), round(y0, 1), round(vbw, 1), round(vbh, 1)]}, ensure_ascii=False)
    back = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="M13 8H3M7 4L3 8l4 4"/></svg>')
    return MAP_HTML.format(back=back, arrow=ARROW, img=days[0]['img'], route=days[0]['route'], title=days[0]['title'],
                           text=days[0]['text'], pills=pills, vb=f'{x0:.0f} {y0:.0f} {vbw:.0f} {vbh:.0f}',
                           lands=countries_svg(), legs=legs, dots=dots, ax=ax, ay=ay, lbls=lbls, data=data)


# ───────────────────────────── Каркас ─────────────────────────────
ARROW = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
         'stroke-linejoin="round" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>')
ARROW_UR = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="M4.5 11.5l7-7M5.5 4.5h6v6"/></svg>')


def nav(current, over=False):
    links = ''.join('<a href="{}"{}>{}</a>'.format(h, ' aria-current="page"' if h == current else '', t) for h, t in NAV)
    btn_cls = 'btn btn--white' if over else 'btn'
    return f'''<nav class="nav{' nav--over' if over else ''}" aria-label="Основное меню">
  <a class="nav__logo" href="index.html" aria-label="Prime Ayrus Travel — главная"><img src="brand/logo.svg" width="112" height="46" alt="Prime Ayrus Travel"></a>
  <div class="nav__links">{links}</div>
  <a class="nav__tel" href="{PHONE_HREF}">{PHONE}</a>
  <a class="{btn_cls}" href="{wa()}" target="_blank" rel="noopener">Написать нам</a>
  <button class="burger" type="button" aria-label="Открыть меню"><span></span></button>
</nav>'''


def menu():
    links = ''.join(f'<a href="{h}">{t}</a>' for h, t in [('index.html', 'Главная')] + NAV + [('tour.html#price', 'Стоимость')])
    left = ''.join(f'<img src="images/{f}" alt="" loading="lazy">' for f in ['px-kaleici-harbour.jpg', 'px-pamukkale-pools.jpg', 'gallery10.jpg', 'px-fairy-chimneys.jpg'] * 2)
    right = ''.join(f'<img src="images/{f}" alt="" loading="lazy">' for f in ['px-balloons-sunset.jpg', 'px-hierapolis-theatre.jpg', 'px-uchisar-sunset.jpg', 'px-mevlana.jpg'] * 2)
    return f'''<div class="menu" role="dialog" aria-modal="true" aria-label="Меню">
  <div class="menu__top"><img src="brand/logo.svg" width="112" height="46" alt="Prime Ayrus Travel"><button class="menu__close" type="button" aria-label="Закрыть меню">×</button></div>
  <div class="menu__mid">
    <div class="menu__side menu__side--l" aria-hidden="true"><div class="menu__strip">{left}</div></div>
    <div class="menu__links">{links}</div>
    <div class="menu__side menu__side--r" aria-hidden="true"><div class="menu__strip menu__strip--r">{right}</div></div>
  </div>
  <div class="menu__bot"><a href="{PHONE_HREF}">{PHONE}</a><a href="{wa()}" target="_blank" rel="noopener">WhatsApp</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
</div>'''


def foot():
    insta = f'<li><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a></li>' if INSTAGRAM else ''
    return f'''<footer class="foot">
  <div class="wrap">
    <div class="foot__top">
      <div><img class="foot__logo" src="brand/logo.svg" width="140" height="57" alt="Prime Ayrus Travel"><p class="foot__about">Групповые туры по исторической Турции. Офис в Алматы.</p></div>
      <div><h4>Тур</h4><ul><li><a href="tour.html">Программа по дням</a></li><li><a href="tour.html#price">Стоимость</a></li><li><a href="tour.html#extras">Дополнительно</a></li></ul></div>
      <div><h4>Компания</h4><ul><li><a href="about.html">О компании</a></li><li><a href="agents.html">Агентствам</a></li><li><a href="contacts.html">Контакты</a></li></ul></div>
      <div><h4>Связаться</h4><ul><li><a class="foot__tel" href="{PHONE_HREF}">{PHONE}</a></li><li><a href="{wa()}" target="_blank" rel="noopener">WhatsApp</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li>{insta}<li>{ADDRESS}</li></ul></div>
    </div>
    <div class="foot__bot"><span>© 2026 {LEGAL}</span><span>{LICENSE}</span><span>Цены и даты подтверждает менеджер</span></div>
  </div>
</footer>'''


def page(file, title, desc, body, over=False):
    top = '' if over else f'<header class="topbar">{nav(file)}</header>'
    html = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="images/hero-poster.jpg">
<meta name="theme-color" content="#FFFFFF">
<link rel="icon" href="brand/favicon.svg" type="image/svg+xml">
<link rel="icon" href="brand/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
{top}
<main>
{body}
</main>
{foot()}
{menu()}
<script src="assets/anime.min.js" defer></script>
<script src="assets/app.js" defer></script>
</body>
</html>
'''
    (ROOT / file).write_text(html, encoding='utf-8')
    print('✓', file)


# ───────────────────────────── Блоки ─────────────────────────────
def ticks(items, no=False):
    return f'<ul class="ticks{" ticks--no" if no else ""}">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'


def shead(title, sub='', link=None):
    right = f'<p class="sub">{sub}</p>' if sub else ''
    if link:
        right = f'<a class="round" href="{link}" aria-label="Подробнее">{ARROW_UR}</a>'
    return f'<div class="shead rv"><h2 class="h2">{title}</h2>{right}</div>'


RIB1 = [('Анталия', 'px-kaleici-harbour.jpg'), ('Памуккале', 'px-pamukkale-pool.jpg'), ('Каппадокия', 'px-fairy-chimneys.jpg'), ('Конья', 'px-mevlana-tower.jpg')]
RIB2 = [('Калеичи', 'px-hadrian-gate.jpg'), ('Иераполис', 'px-hierapolis-street.jpg'), ('Учхисар', 'px-uchisar-sunset.jpg'), ('Коньяалты', 'px-konyaalti.jpg')]


def ribbon(items):
    one = ''.join(f'<span class="ribbon__w">{w}</span><span class="ribbon__pic"><img src="images/{f}" alt="" loading="lazy"></span>' for w, f in items)
    return f'<div class="ribbon__track">{one * 3}</div>'


def bento():
    # Раскладка 4×3: две карточки, высокое фото, карточка; ещё четыре дня по
    # бокам от фото; внизу широкое фото, седьмой день и фото.
    pics = {1: ('px-pamukkale-pool.jpg', 'Памуккале', 'tall'), 5: ('px-rose-valley.jpg', 'Долины Каппадокии', 'wide'),
            6: ('px-hierapolis-street.jpg', 'Иераполис на закате', '')}
    out = ''
    for i, (stop, route, title, text, opt) in enumerate(DAYS):
        opt_html = f'<p class="opt">{opt}</p>' if opt else ''
        out += (f'<article class="daycard rv" data-stop="{stop}" data-day="{i}"><div class="daycard__top"><h3>{route}</h3>'
                f'<span class="pill">День {i + 1}</span></div><p><b style="color:var(--ink);font-weight:600">{title}.</b> {text}</p>{opt_html}</article>')
        if i in pics:
            f, c, cls = pics[i]
            out += f'<figure class="card-pic rv {cls}"><img src="images/{f}" alt="{c}" loading="lazy"><span class="pill pill--white tag">{c}</span></figure>'
    return f'<div class="bento">{out}</div>'


def price_block():
    return f'''<section class="sec wrap" id="price">
  {shead('Стоимость тура', 'Цена за человека при двухместном размещении. Даты групп и доплаты подскажет менеджер.')}
  <div class="price">
    <div class="price__main rv"><span class="pill">7 дней / 6 ночей</span><p class="price__num">{PRICE}</p><p>на человека при двухместном размещении</p>
      <a class="btn btn--white" href="{wa('Здравствуйте! Подскажите, пожалуйста, ближайшие даты тура по Турции.')}" target="_blank" rel="noopener">Узнать даты <span class="ic">{ARROW}</span></a></div>
    <div class="list-card rv" style="--d:.08s"><h3>Входит</h3>{ticks(INCLUDED)}</div>
    <div class="list-card rv" style="--d:.16s"><h3>Оплачивается отдельно</h3>{ticks(NOT_INCLUDED, True)}</div>
  </div>
</section>'''


def extras_block():
    chips = ''.join(f'<button type="button" class="chip" aria-pressed="false">{x}</button>' for x in EXTRAS)
    return f'''<section class="sec wrap" id="extras">
  <div class="extras" data-extras>
    <div class="extras__box rv">
      <span class="pill pill--white"><i></i>Не входит в тур</span>
      <h2 class="h2">Дополнительно, по&nbsp;желанию</h2>
      <p class="sub">Отметьте, что интересно, — менеджер посчитает цену на ваши даты.</p>
      <div class="chips">{chips}</div>
      <div class="extras__act"><a class="btn" data-send href="{wa()}" target="_blank" rel="noopener">Спросить цену <span class="ic">{ARROW}</span></a><span data-count aria-live="polite">Отметьте, что интересно</span></div>
    </div>
    <figure class="card-pic rv" style="--d:.1s"><img src="images/gallery7.jpg" alt="Воздушный шар над Каппадокией" loading="lazy"><span class="pill pill--white tag">Шар над Каппадокией</span></figure>
  </div>
</section>'''


def faq_block(items, title='Частые вопросы'):
    qa = ''.join(f'<details class="rv"><summary>{q}</summary><p>{a}</p></details>' for q, a in items)
    return f'''<section class="sec wrap" id="faq">
  <div class="faq">
    <div class="rv" style="display:grid;gap:16px"><h2 class="h2">{title}</h2><p class="sub">Не нашли ответ — напишите менеджеру, он на связи в рабочее время.</p>
      <a class="btn btn--soft" style="justify-self:start" href="{wa('Здравствуйте! У меня вопрос о туре по Турции.')}" target="_blank" rel="noopener">Задать вопрос <span class="ic">{ARROW}</span></a></div>
    <div class="faq__list">{qa}</div>
  </div>
</section>'''


def trust_block():
    return f'''<section class="sec wrap">
  {shead('Работаем официально', 'Турагентство зарегистрировано в Казахстане, на каждую поездку оформляем документы.')}
  <div class="trust">
    <div class="rv"><b>Договор на каждую поездку</b><span>С вашими данными, маршрутом и стоимостью — до оплаты.</span></div>
    <div class="rv" style="--d:.08s"><b>Ваучер с вашим именем</b><span>Маршрут, даты, отели и питание на одном листе.</span></div>
    <div class="rv" style="--d:.16s"><span class="num">№ {LICENSE_NO}</span><b>Уведомление о турагентской деятельности</b><span>Государственный реестр разрешений и уведомлений, elicense.kz</span></div>
  </div>
</section>'''


def final_block():
    return f'''<section class="sec wrap">
  <div class="final rv">
    <img src="images/px-uchisar-sunset.jpg" alt="Крепость Учхисар на закате" loading="lazy" data-par="-.12">
    <div class="final__in">
      <div><h2>Ваша Турция начинается здесь</h2><p>Подскажем ближайшие даты групп, программу и условия бронирования.</p></div>
      <div class="final__acts"><a class="btn btn--white" href="{wa('Здравствуйте! Подскажите, пожалуйста, ближайшие даты тура по Турции.')}" target="_blank" rel="noopener">Написать в WhatsApp <span class="ic">{ARROW}</span></a>
        <a class="btn" style="background:rgba(255,255,255,.18)" href="{PHONE_HREF}">{PHONE}</a></div>
    </div>
  </div>
</section>'''


# ───────────────────────────── Страницы ─────────────────────────────
HERO_H1 = ''.join('<span aria-hidden="true">' + c + '</span>' for c in 'Турция')


def build_index():
    see = ''.join(f'<figure class="card-pic rv" style="--d:{(i % 3) * .06:.2f}s"><img src="images/{f}" alt="{c}" loading="lazy"><span class="pill pill--white tag">{c}</span></figure>' for i, (f, c) in enumerate(SEE))
    body = f'''<section class="hero">
  <div class="hero__box">
    {nav('index.html', over=True)}
    <div class="hero__bg"><video autoplay muted loop playsinline preload="auto" poster="images/hero-poster.jpg" aria-label="Воздушные шары над долинами Каппадокии на рассвете">
      <source src="media/hero-m.mp4" type="video/mp4" media="(max-width: 760px)"><source src="media/hero-m.webm" type="video/webm" media="(max-width: 760px)"><source src="media/hero.mp4" type="video/mp4"><source src="media/hero.webm" type="video/webm"></video></div>
    <span class="hero__loc pill"><i></i>Каппадокия, рассвет</span>
    <div class="hero__mid">
      <p class="hero__kicker">Историческая Турция за семь дней</p>
      <h1 aria-label="Турция">{HERO_H1}</h1>
      <p class="hero__lead">Анталия, Памуккале, Каппадокия и Конья — групповой тур из Алматы с гидом-историком и отелями 4–5★.</p>
    </div>
    <dl class="hero__bar">
      <div><dt>Маршрут</dt><dd>4 города, петля из Анталии</dd></div>
      <div><dt>Длительность</dt><dd>7 дней / 6 ночей</dd></div>
      <div><dt>Проживание</dt><dd>Отели 4–5★, завтраки и ужины</dd></div>
      <div><dt>Стоимость</dt><dd>{PRICE} на человека</dd></div>
      <a href="{wa('Здравствуйте! Подскажите, пожалуйста, ближайшие даты тура по Турции.')}" target="_blank" rel="noopener">Узнать даты {ARROW}</a>
    </dl>
  </div>
</section>

<section class="sec wrap">
  <div class="intro rv">
    <div class="intro__chips"><span class="pill"><i></i>Офис в Алматы</span><span class="pill"><i></i>Гид-историк</span><span class="pill"><i></i>Договор и ваучер</span></div>
    <h2>Показываем Турцию, <span>которую знаем сами</span></h2>
  </div>
  <div class="values">
    <div class="values__text rv">
      <span class="pill" style="justify-self:start"><i></i>Почему мы</span>
      <h3>Не просто турагентство</h3>
      <p class="sub">Мы возим группы по одному маршруту и знаем на нём каждую дорогу, отель и смотровую площадку. Вам остаётся только прилететь.</p>
      <a class="btn" href="tour.html">Программа тура <span class="ic">{ARROW}</span></a>
    </div>
    <div class="stairs">
      <figure class="rv" data-par=".06"><div class="card-pic"><img src="images/px-pamukkale-terraces.jpg" alt="Травертины Памуккале" loading="lazy"><span class="pill pill--white tag">Памуккале</span></div><figcaption class="cap"><b>Террасы и Иераполис</b><span>Третий день маршрута</span></figcaption></figure>
      <figure class="rv" style="--d:.1s" data-par="-.08"><div class="card-pic"><img src="images/px-uchisar.jpg" alt="Крепость Учхисар" loading="lazy"><span class="pill pill--white tag">Каппадокия</span></div><figcaption class="cap"><b>Учхисар и долины</b><span>Пятый день</span></figcaption></figure>
      <figure class="rv" style="--d:.2s" data-par=".03"><div class="card-pic"><img src="images/px-kaleici-harbour.jpg" alt="Старая гавань Калеичи" loading="lazy"><span class="pill pill--white tag">Анталия</span></div><figcaption class="cap"><b>Старый город Калеичи</b><span>Первый и второй день</span></figcaption></figure>
    </div>
  </div>
</section>


<section class="ribbon" aria-label="Города маршрута">
  <div class="ribbon__row" data-ribbon="1">{ribbon(RIB1)}</div>
  <div class="ribbon__row ribbon__row--alt" data-ribbon="-1">{ribbon(RIB2)}</div>
</section>
<section class="sec wrap">
  {shead('Всё, что вы увидите', 'Белые террасы, долины с каменными столбами, старые города и шары на рассвете.')}
  <div class="grid9">{see}</div>
</section>

<section class="sec wrap" id="route">
  {shead('Смотрите, куда едем', 'Петля в четыре города: на запад к белым террасам, на восток к долинам Каппадокии и обратно к морю через Конью.')}
  {map_card()}
</section>

<section class="sec wrap" id="program">
  {shead('Программа тура', link='tour.html')}
  {bento()}
</section>

{price_block()}
{extras_block()}
{trust_block()}
{faq_block(FAQ)}
{final_block()}'''
    page('index.html', 'Prime Ayrus Travel — тур по исторической Турции из Алматы',
         'Групповой тур Prime Ayrus Travel: Анталия, Памуккале, Каппадокия, Конья. 7 дней, отели 4–5★, гид-историк, 260 000 ₸ на человека. Офис в Алматы.', body, over=True)


def phead(title, sub, img, alt):
    return f'''<section class="wrap phead rv"><h1>{title}</h1><p class="sub">{sub}</p></section>
<div class="wrap"><div class="pcover rv"><img src="images/{img}" alt="{alt}"></div></div>'''


def build_tour():
    body = phead('Программа тура', f'Анталия — Памуккале — Каппадокия — Конья — Анталия. Семь дней и шесть ночей, {PRICE} на человека.', 'px-balloons-sunset.jpg', 'Шары над Каппадокией на рассвете') + f'''
<section class="sec wrap" id="program">{shead('По дням', 'Дни насыщенные, с длинными переездами. Обеды и входные билеты оплачиваются на месте.')}{bento()}</section>
<section class="sec wrap" id="route">{shead('Маршрут на карте', 'Нажмите на день — карта переедет к нужному городу. Или включите весь маршрут.')}{map_card()}</section>
{price_block()}
{extras_block()}
{faq_block(FAQ[2:], 'Перед поездкой')}
{final_block()}'''
    page('tour.html', 'Программа тура по исторической Турции — Prime Ayrus Travel',
         'Программа по дням: Анталия, Памуккале, Каппадокия, Конья. Что входит в 260 000 ₸, что оплачивается отдельно, дополнительные услуги.', body)


def steps(items):
    return '<ol class="steps">' + ''.join(f'<li class="rv" style="--d:{i * .08:.2f}s"><span class="pill">Шаг {i + 1}</span><b>{t}</b><span>{d}</span></li>' for i, (t, d) in enumerate(items)) + '</ol>'


def build_about():
    body = phead('О компании', 'Prime Ayrus Travel — турагентство из Алматы. Мы возим группы по исторической Турции.', 'collage-2.jpg', 'Группа Prime Ayrus Travel у исторической мечети') + f'''
<section class="sec wrap"><div class="cols2">
  <h2 class="h2 rv">Один маршрут, продуманный до&nbsp;мелочей</h2>
  <div class="prose rv" style="--d:.08s">
    <p class="big">У нас один тур — петля через Анталию, Памуккале, Каппадокию и Конью.</p>
    <p>Поэтому мы знаем на нём каждую дорогу, отель и остановку. С группой едет гид-историк: за городами стоят люди и эпохи, а не только точки на карте.</p>
    <p>В Алматы работает офис: консультируем, заключаем договоры, выдаём ваучеры и остаёмся на связи с туристами всю поездку.</p>
  </div>
</div></section>
<section class="sec wrap">{shead('Как проходит поездка')}{steps([('Вы пишете нам', 'В WhatsApp или через заявку — когда хотите поехать и сколько вас.'), ('Подбираем группу', 'Менеджер называет даты и считает стоимость вместе с доплатами.'), ('Оформляем документы', 'Договор, ваучер и порядок оплаты.'), ('Встречаем в Анталии', 'В аэропорту ждут трансфер, отель и гид.')])}</section>
{trust_block()}
<section class="sec wrap"><div class="cols2">
  <h2 class="h2 rv">Реквизиты</h2>
  <dl class="kv rv">
    <div><dt>Наименование</dt><dd>ИП «PRIME AYRUS TRAVEL»</dd></div>
    <div><dt>ИИН</dt><dd>860228300934</dd></div>
    <div><dt>Турагентская деятельность</dt><dd>{LICENSE}</dd></div>
    <div><dt>Адрес офиса</dt><dd>{ADDRESS}</dd></div>
    <div><dt>Телефон</dt><dd><a href="{PHONE_HREF}">{PHONE}</a></dd></div>
    <div><dt>Почта</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
  </dl>
</div></section>
{final_block()}'''
    page('about.html', 'О компании — Prime Ayrus Travel',
         'Prime Ayrus Travel — турагентство из Алматы: групповые туры по исторической Турции, договор и ваучер на каждую поездку, уведомление № KZ21TWG00012021.', body)


def form(intro, fields, title):
    return f'''<form class="form rv" style="--d:.08s" data-wa="{intro}">
      <h3>{title}</h3>
      <div class="field"><label for="f-name">Имя</label><input id="f-name" name="name" required autocomplete="name"></div>
      <div class="field"><label for="f-phone">Телефон</label><input id="f-phone" name="phone" type="tel" required autocomplete="tel" placeholder="+7"></div>
      {fields}
      <div class="field"><label for="f-msg">Комментарий</label><textarea id="f-msg" name="message"></textarea></div>
      <button class="btn" type="submit">Отправить в WhatsApp <span class="ic">{ARROW}</span></button>
      <small>Заявка откроется готовым сообщением в WhatsApp менеджера.</small>
    </form>'''


def build_agents():
    body = phead('Турагентствам', 'Готовый тур по исторической Турции для ваших клиентов. Группы, документы и сопровождение — на нас.', 'px-rose-valley.jpg', 'Долины Каппадокии') + f'''
<section class="sec wrap"><div class="cols2">
  <h2 class="h2 rv">Что получает партнёр</h2>
  <div class="prose rv" style="--d:.08s">
    <p class="big">Вознаграждение за каждого туриста, которого вы к нам привели.</p>
    <p>Условия фиксируем с каждым партнёром отдельно. Вы получаете код партнёра — по нему мы узнаём ваших туристов в каждой заявке.</p>
    <p>Список туристов присылаете по нашему шаблону. Мы заводим заявку, оформляем договоры и ваучеры и ведём ваших клиентов до возвращения домой.</p>
  </div>
</div></section>
<section class="sec wrap">{shead('Как начать работу')}{steps([('Знакомимся', 'Рассказываем о туре, условиях и вознаграждении.'), ('Выдаём код', 'По нему ваши туристы видны в каждой заявке.'), ('Даём материалы', 'Программа, фотографии и ответы на вопросы клиентов.'), ('Считаем выплату', 'Вознаграждение — по вашим туристам в поездке.')])}</section>
<section class="sec wrap"><div class="cols2">
  <div style="display:grid;gap:20px" class="rv"><h2 class="h2">Обсудим условия</h2><p class="sub">Оставьте контакты — менеджер расскажет о вознаграждении и порядке работы.</p>
    <dl class="kv"><div><dt>Телефон</dt><dd><a href="{PHONE_HREF}">{PHONE}</a></dd></div><div><dt>Почта</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div></dl></div>
  {form('Здравствуйте! Хотим стать партнёром Prime Ayrus Travel.', '<div class="field"><label for="f-topic">Агентство и город</label><input id="f-topic" name="topic"></div>', 'Заявка на партнёрство')}
</div></section>'''
    page('agents.html', 'Турагентствам — Prime Ayrus Travel',
         'Партнёрство с Prime Ayrus Travel для турагентств и агентов: готовый тур по Турции, код партнёра, сопровождение, вознаграждение за каждого туриста.', body)


CONTACT_FIELDS = ('<div class="field"><label for="f-topic">Что интересует</label><select id="f-topic" name="topic">'
                  '<option>Ближайшие даты</option><option>Стоимость и доплаты</option><option>Поездка группой</option>'
                  '<option>Сотрудничество</option><option>Другое</option></select></div>'
                  '<div class="field"><label for="f-people">Сколько человек едет</label><input id="f-people" name="people" inputmode="numeric"></div>')


def build_contacts():
    insta = f'<div><dt>Instagram</dt><dd><a href="{INSTAGRAM}" target="_blank" rel="noopener">Открыть профиль</a></dd></div>' if INSTAGRAM else ''
    body = phead('Контакты', 'Офис в Алматы. Подскажем даты групп, программу и условия бронирования.', 'day3.jpg', 'Террасы Памуккале на закате') + f'''
<section class="sec wrap"><div class="cols2">
  <div style="display:grid;gap:20px" class="rv"><h2 class="h2">Офис</h2>
    <dl class="kv">
      <div><dt>Адрес</dt><dd>{ADDRESS}</dd></div>
      <div><dt>Режим работы</dt><dd>{HOURS}</dd></div>
      <div><dt>Телефон</dt><dd><a href="{PHONE_HREF}">{PHONE}</a></dd></div>
      <div><dt>WhatsApp</dt><dd><a href="{wa()}" target="_blank" rel="noopener">Написать менеджеру</a></dd></div>
      <div><dt>Почта</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
      {insta}
      <div><dt>Турагентство</dt><dd>PRIME AYRUS TRAVEL</dd></div>
      <div><dt>Документ</dt><dd>{LICENSE}</dd></div>
    </dl>
    <a class="btn btn--soft" style="justify-self:start" href="{MAP_URL}" target="_blank" rel="noopener">Открыть в 2ГИС <span class="ic">{ARROW}</span></a></div>
  {form('Здравствуйте! Заявка с сайта Prime Ayrus Travel.', CONTACT_FIELDS, 'Оставить заявку')}
</div></section>
{faq_block(FAQ[:4])}'''
    page('contacts.html', 'Контакты — Prime Ayrus Travel',
         'Prime Ayrus Travel: г. Алматы, ул. Ч. Валиханова, 58. Телефон +7 707 439-59-79, WhatsApp, travelayrus@gmail.com.', body)


if __name__ == '__main__':
    build_index()
    build_tour()
    build_about()
    build_agents()
    build_contacts()
