// Prime Ayrus Travel — поведение и анимации (Anime.js v3, assets/anime.min.js).
// Без скрипта всё видно и работает; при «уменьшить движение» анимаций нет.
(() => {
  const doc = document.documentElement;
  doc.classList.add('js');
  const A = window.anime;
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches || !A;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const WA = 'https://wa.me/77074395979?text=';
  const wa = (t) => WA + encodeURIComponent(t);
  const EASE = 'cubicBezier(.22, .8, .2, 1)';
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  // ─── Меню на весь экран ───
  const menu = document.querySelector('.menu');
  const open = () => {
    document.body.classList.add('menu-open');
    menu.querySelector('.menu__close').focus();
    if (!calm) A({ targets: menu.querySelectorAll('.menu__links a'), translateY: [40, 0], opacity: [0, 1], duration: 700, delay: A.stagger(55, { start: 80 }), easing: EASE });
  };
  const close = () => document.body.classList.remove('menu-open');
  document.querySelectorAll('.burger').forEach((b) => b.addEventListener('click', open));
  if (menu) {
    menu.querySelector('.menu__close').addEventListener('click', close);
    menu.querySelectorAll('a').forEach((a) => a.addEventListener('click', close));
    addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  }

  // ─── Появление блоков ───
  const rv = [...document.querySelectorAll('.rv')];
  const seen = (els, fn, margin = '-8%', threshold = 0) => {
    if (!('IntersectionObserver' in window)) { els.forEach(fn); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { io.unobserve(e.target); fn(e.target); }
    }), { rootMargin: `0px 0px ${margin} 0px`, threshold });
    els.forEach((el) => io.observe(el));
  };
  if (calm) rv.forEach((el) => el.classList.add('in'));
  else seen(rv, (el) => el.classList.add('in'));

  // ─── Первый экран: видео, появление, параллакс ───
  const hero = document.querySelector('.hero__box');
  const heroBg = hero && hero.querySelector('.hero__bg');
  const heroMid = hero && hero.querySelector('.hero__mid');
  const video = hero && hero.querySelector('video');
  if (video) {
    if (calm) { video.removeAttribute('autoplay'); video.pause(); }
    else if ('IntersectionObserver' in window) {
      new IntersectionObserver(([e]) => { if (e.isIntersecting) video.play().catch(() => {}); else video.pause(); }).observe(hero);
    }
  }
  if (hero && !calm) {
    A.timeline({ easing: EASE })
      .add({ targets: heroBg.firstElementChild, scale: [1.18, 1], duration: 2600 }, 0)
      .add({ targets: hero.querySelectorAll('.hero h1 span'), translateY: ['45%', 0], opacity: [0, 1], duration: 1200, delay: A.stagger(70) }, 200)
      .add({ targets: hero.querySelectorAll('.hero__kicker, .hero__lead'), translateY: [20, 0], opacity: [0, 1], duration: 1000, delay: A.stagger(160) }, 450)
      .add({ targets: hero.querySelectorAll('.hero__bar > *, .hero__loc'), translateY: [24, 0], opacity: [0, 1], duration: 900, delay: A.stagger(70) }, 750);
  }
  let mx = 0, my = 0, tx = 0, ty = 0;
  if (hero && fine && !calm) {
    hero.addEventListener('pointermove', (e) => {
      const r = hero.getBoundingClientRect();
      tx = (e.clientX - r.left) / r.width - .5; ty = (e.clientY - r.top) / r.height - .5;
    });
    hero.addEventListener('pointerleave', () => { tx = 0; ty = 0; });
  }

  // ─── Движение от прокрутки: первый экран, лента городов, параллакс фото ───
  const rows = [...document.querySelectorAll('[data-ribbon]')].map((row) => ({ row, track: row.firstElementChild, dir: +row.dataset.ribbon, one: 0 }));
  const pars = [...document.querySelectorAll('[data-par]')].map((el) => ({ el, k: +el.dataset.par }));
  const measure = () => rows.forEach((r) => { r.one = r.track.scrollWidth / 3; });
  measure();
  addEventListener('resize', measure);
  if (document.fonts) document.fonts.ready.then(measure);
  if (!calm) {
    let t0 = performance.now();
    const frame = (now) => {
      const vh = innerHeight, sy = scrollY;
      if (hero) {
        mx += (tx - mx) * .06; my += (ty - my) * .06;
        const h = hero.offsetHeight, p = clamp(sy / h, 0, 1);
        if (sy < h * 1.2) {
          heroBg.style.transform = `translate3d(${-mx * 18}px, ${p * h * .22 - my * 12}px, 0) scale(${1.04 + p * .08})`;
          heroMid.style.transform = `translate3d(${mx * 14}px, ${-p * h * .18 + my * 8}px, 0)`;
          heroMid.style.opacity = String(1 - p * 1.1);
        }
      }
      const drift = (now - t0) / 1000 * 22;
      rows.forEach((r) => {
        const b = r.row.getBoundingClientRect();
        if (b.bottom < -50 || b.top > vh + 50 || !r.one) return;
        const off = (sy * .45 + drift) * r.dir;
        const x = -(((off % r.one) + r.one) % r.one);
        r.track.style.transform = `translate3d(${x}px, 0, 0)`;
      });
      pars.forEach((p) => {
        const b = p.el.getBoundingClientRect();
        if (b.bottom < -100 || b.top > vh + 100) return;
        p.el.style.translate = `0 ${((b.top + b.height / 2) - vh / 2) * p.k}px`;
      });
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }

  // ─── Карта маршрута ───
  document.querySelectorAll('[data-rmap]').forEach(initMap);

  function initMap(rm) {
    const data = JSON.parse(rm.querySelector('.rmap__data').textContent);
    const days = data.days, C = data.cities;
    const box = rm.querySelector('.rmap__map');
    const svg = box.querySelector('svg');
    const lbls = [...box.querySelectorAll('.mlbl')].map((el) => ({ el, x: +el.dataset.x, y: +el.dataset.y, city: el.dataset.city }));
    const legs = {}; box.querySelectorAll('.leg').forEach((p) => { legs[p.dataset.leg] = p; });
    const bases = {}; box.querySelectorAll('.leg-base').forEach((p, i) => { bases[Object.keys(legs)[i]] = p; });
    const dots = {}; box.querySelectorAll('.city').forEach((c) => { dots[c.dataset.city] = c; });
    const marker = box.querySelector('.marker');
    const pills = [...rm.querySelectorAll('.tl__d')];
    const bar = rm.querySelector('.tl__bar');
    const K = (k) => rm.querySelector(`[data-k="${k}"]`);
    const pic = rm.querySelector('.rmap__pic');
    const order = days.map((d) => d.legs).join('').split('');

    const cam = { x: data.vb[0], y: data.vb[1], w: data.vb[2], h: data.vb[3] };
    let mpos = C.antalya.slice();
    let cur = -1, playing = false, timer = 0, anims = [];

    // Точки, которые должны попасть в кадр в этот день.
    const legPts = (k) => { const p = bases[k], L = p.getTotalLength(), out = []; for (let i = 0; i <= 12; i++) { const q = p.getPointAtLength(L * i / 12); out.push([q.x, q.y]); } return out; };
    const framePts = (i) => {
      if (i < 0 || i === days.length - 1) return Object.values(C).concat(...Object.keys(legs).map(legPts), [data.vb.slice(0, 2), [data.vb[0] + data.vb[2], data.vb[1] + data.vb[3]]]);
      const d = days[i];
      if (d.legs) return d.legs.split('').flatMap(legPts);
      return [C[d.city]];
    };
    const fit = (pts, single) => {
      const w = box.clientWidth || 1, h = box.clientHeight || 1;
      const mob = w < 700;
      const pad = mob ? 34 : 70, top = mob ? 40 : 56;
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      pts.forEach(([x, y]) => { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); });
      let s = Math.max((x1 - x0) / Math.max(w - pad * 2, 50), (y1 - y0) / Math.max(h - pad * 2 - top, 50));
      s = Math.max(s, (single ? 560 : 640) / w);
      const cw = w * s, ch = h * s;
      return { x: (x0 + x1) / 2 - cw / 2, y: (y0 + y1) / 2 - ch / 2 - top * s / 2, w: cw, h: ch };
    };
    const target = (i) => fit(framePts(i), i >= 0 && i < days.length - 1 && !days[i].legs);

    const apply = () => {
      svg.setAttribute('viewBox', `${cam.x.toFixed(2)} ${cam.y.toFixed(2)} ${cam.w.toFixed(2)} ${cam.h.toFixed(2)}`);
      const w = box.clientWidth, h = box.clientHeight, s = cam.w / w;
      lbls.forEach((l) => {
        const px = (l.x - cam.x) / s, py = (l.y - cam.y) / s;
        if (l.city) {
          // Подпись города не вылезает за край карты; город за кадром — без подписи.
          const half = (l.w || (l.w = l.el.offsetWidth)) / 2 + 10;
          l.el.style.left = clamp(px, half, w - half) + 'px'; l.el.style.top = py + 'px';
          l.el.classList.toggle('is-off', px < -4 || px > w + 4 || py < 30 || py > h + 4);
        } else {
          l.el.style.left = px + 'px'; l.el.style.top = py + 'px';
          l.el.classList.toggle('is-off', px < 40 || px > w - 40 || py < 20 || py > h - 20);
        }
      });
      marker.setAttribute('transform', `translate(${mpos[0].toFixed(2)} ${mpos[1].toFixed(2)}) scale(${s.toFixed(4)})`);
      Object.values(dots).forEach((c) => c.setAttribute('r', (5.5 * s).toFixed(3)));
      Object.values(bases).forEach((b) => { b.style.strokeWidth = 2 * s; b.style.strokeDasharray = `${1 * s} ${7 * s}`; });
      Object.values(legs).forEach((l) => { l.style.strokeWidth = 3 * s; });
    };

    const swapPanel = (d) => {
      K('n').textContent = `День ${d.n} из ${days.length}`;
      const txt = rm.querySelector('.rmap__txt');
      const fill = () => {
        K('route').textContent = d.route; K('title').textContent = d.title + '.'; K('text').textContent = d.text;
        const o = K('opt'); o.hidden = !d.opt; o.textContent = d.opt;
      };
      const old = pic.querySelector('img:last-child');
      if (old.getAttribute('src') !== d.img) {
        const img = new Image(); img.src = d.img; img.alt = d.route; img.dataset.k = 'img';
        pic.appendChild(img);
        if (calm) { old.remove(); } else {
          A({ targets: img, opacity: [0, 1], scale: [1.08, 1], duration: 900, easing: EASE, complete: () => pic.querySelectorAll('img').forEach((x) => { if (x !== img) x.remove(); }) });
        }
      }
      if (calm) fill();
      else A({ targets: txt, opacity: [1, 0], translateY: [0, -8], duration: 220, easing: 'easeInQuad', complete: () => { fill(); A({ targets: txt, opacity: [0, 1], translateY: [10, 0], duration: 500, easing: EASE }); } });
    };

    const go = (i, opts = {}) => {
      i = clamp(i, 0, days.length - 1);
      anims.forEach((a) => a.pause()); anims = [];
      const d = days[i];
      const fromPrev = i === cur + 1;
      cur = i;
      // Пройденные отрезки — до этого дня; отрезки дня рисуются сейчас.
      const before = days.slice(0, i).map((x) => x.legs).join('');
      Object.entries(legs).forEach(([k, p]) => { p.style.strokeDashoffset = before.includes(k) ? 0 : 1; });
      const visited = new Set(['antalya']);
      days.slice(0, i + 1).forEach((x) => { visited.add(x.city); x.legs.split('').forEach((k) => { const a = { a: 'pamukkale', b: 'cappadocia', c: 'konya', d: 'antalya' }[k]; visited.add(a); }); });
      Object.entries(dots).forEach(([k, c]) => c.classList.toggle('is-done', visited.has(k)));
      lbls.forEach((l) => l.city && l.el.classList.toggle('is-on', l.city === d.city));
      pills.forEach((p, j) => { p.classList.toggle('is-on', j === i); p.classList.toggle('is-done', j < i); p.setAttribute('aria-current', j === i ? 'step' : 'false'); });
      bar.style.setProperty('--p', i / (days.length - 1));
      swapPanel(d);

      const tgt = target(i);
      const ks = d.legs.split('');
      const travel = ks.length && (fromPrev || opts.replay);
      const done = () => { if (playing) timer = setTimeout(() => (cur < days.length - 1 ? go(cur + 1) : stop()), 2600); };
      if (calm || opts.instant) {
        Object.assign(cam, tgt);
        ks.forEach((k) => { legs[k].style.strokeDashoffset = 0; });
        mpos = C[d.city].slice(); apply(); done(); return;
      }
      const dur = travel ? 2400 : 1500;
      anims.push(A({ targets: cam, x: tgt.x, y: tgt.y, w: tgt.w, h: tgt.h, duration: dur, easing: 'easeInOutCubic', update: apply }));
      if (travel) {
        const Ls = ks.map((k) => bases[k].getTotalLength()), tot = Ls.reduce((a, b) => a + b, 0);
        const st = { t: 0 };
        anims.push(A({
          targets: st, t: 1, duration: dur, easing: 'easeInOutSine',
          update: () => {
            let rest = st.t * tot;
            ks.forEach((k, j) => {
              const f = clamp(rest / Ls[j], 0, 1);
              legs[k].style.strokeDashoffset = 1 - f;
              if (rest >= 0 && (rest <= Ls[j] || j === ks.length - 1)) { const q = bases[k].getPointAtLength(Math.min(rest, Ls[j])); mpos = [q.x, q.y]; }
              rest -= Ls[j];
            });
          },
          complete: done,
        }));
      } else {
        ks.forEach((k) => { legs[k].style.strokeDashoffset = 0; });
        const m = { x: mpos[0], y: mpos[1] }, to = C[d.city];
        anims.push(A({ targets: m, x: to[0], y: to[1], duration: dur, easing: 'easeInOutCubic', update: () => { mpos = [m.x, m.y]; }, complete: done }));
      }
    };

    const stop = () => { playing = false; clearTimeout(timer); rm.classList.remove('is-playing'); };
    const play = () => {
      playing = true; rm.classList.add('is-playing');
      if (cur >= days.length - 1 || cur < 0) {
        Object.values(legs).forEach((p) => { p.style.strokeDashoffset = 1; });
        mpos = C.antalya.slice(); cur = -1;
      }
      go(cur + 1, { replay: true });
    };
    const user = (fn) => (e) => { stop(); fn(e); };

    rm.querySelector('[data-act="play"]').addEventListener('click', () => (playing ? stop() : play()));
    rm.querySelector('[data-act="prev"]').addEventListener('click', user(() => go(cur - 1)));
    rm.querySelector('[data-act="next"]').addEventListener('click', user(() => go(cur + 1)));
    pills.forEach((p) => p.addEventListener('click', user(() => go(+p.dataset.day))));
    lbls.forEach((l) => l.city && l.el.addEventListener('click', user(() => go(days.findIndex((d) => d.city === l.city || d.legs.includes({ pamukkale: 'a', cappadocia: 'b', konya: 'c' }[l.city]))))));
    rm.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { stop(); go(cur + 1); } else if (e.key === 'ArrowLeft') { stop(); go(cur - 1); }
    });
    // Клик по карточке дня в программе — к карте и к этому дню.
    document.querySelectorAll('.daycard[data-day]').forEach((c) => {
      c.style.cursor = 'pointer';
      c.title = 'Показать на карте';
      c.addEventListener('click', () => { stop(); rm.scrollIntoView({ behavior: calm ? 'auto' : 'smooth', block: 'center' }); setTimeout(() => go(+c.dataset.day), calm ? 0 : 450); });
    });

    // Старт: виден весь маршрут; когда карта на экране — проигрываем дни.
    Object.values(legs).forEach((p) => { p.style.strokeDashoffset = 1; });
    Object.assign(cam, target(-1)); apply();
    if ('ResizeObserver' in window) new ResizeObserver(() => { lbls.forEach((l) => { l.w = 0; }); if (!anims.some((a) => !a.completed)) { Object.assign(cam, target(cur)); apply(); } }).observe(box);
    const preload = () => days.forEach((d) => { const i = new Image(); i.src = d.img; });
    if (calm) { go(0, { instant: true }); return; }
    seen([box], () => {
      preload();
      // Сначала весь маршрут прорисовывается разом, потом — по дням.
      const st = { t: 0 };
      A({
        targets: st, t: 1, duration: 1800, easing: 'easeInOutSine',
        update: () => { const n = order.length; order.forEach((k, j) => { legs[k].style.strokeDashoffset = 1 - clamp(st.t * n - j, 0, 1); }); },
        complete: () => setTimeout(() => { if (cur < 0) { playing = true; rm.classList.add('is-playing'); Object.values(legs).forEach((p) => { p.style.strokeDashoffset = 1; }); go(0); } }, 700),
      });
    }, '-25%');
  }

  // ─── Доп. услуги: выбор уходит в сообщение ───
  document.querySelectorAll('[data-extras]').forEach((box) => {
    const send = box.querySelector('[data-send]');
    const count = box.querySelector('[data-count]');
    const upd = () => {
      const picked = [...box.querySelectorAll('.chip[aria-pressed="true"]')].map((c) => c.textContent.trim());
      send.href = wa(picked.length
        ? `Здравствуйте! К туру по Турции интересуют: ${picked.join(', ')}. Сколько это стоит на мои даты?`
        : 'Здравствуйте! Расскажите, пожалуйста, о дополнительных услугах к туру по Турции.');
      count.textContent = picked.length ? `Выбрано: ${picked.length}` : 'Отметьте, что интересно';
    };
    box.querySelectorAll('.chip').forEach((c) => c.addEventListener('click', () => {
      c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') !== 'true');
      if (!calm) A({ targets: c, scale: [.92, 1], duration: 600, easing: 'spring(1, 200, 12, 0)' });
      upd();
    }));
    upd();
  });

  // ─── Заявка: готовое сообщение в WhatsApp ───
  document.querySelectorAll('form[data-wa]').forEach((f) => f.addEventListener('submit', (e) => {
    e.preventDefault();
    const d = new FormData(f);
    const lines = [f.dataset.wa];
    for (const [k, label] of [['name', 'Имя'], ['phone', 'Телефон'], ['topic', 'Тема'], ['people', 'Человек'], ['message', 'Комментарий']]) {
      const v = (d.get(k) || '').toString().trim();
      if (v) lines.push(`${label}: ${v}`);
    }
    window.open(wa(lines.join('\n')), '_blank', 'noopener');
  }));
})();
