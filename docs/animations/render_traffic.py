"""Generate self-contained SVG traffic animations using standard-library Python.

No raster frames, scripts, external assets or fonts are embedded. Eased motion
is rendered at browser refresh rate on one explicit timeline. These diagrams
describe service behavior, not throughput or concurrent payment guarantees.
"""

from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
BLUE, MINT, PURPLE, GOLD, RED = '#62d4ff', '#7af4c4', '#bda0ff', '#ffd28a', '#ff879c'
TEXT, MUTED = '#edf5ff', '#95a9c4'
COLORS = {'blue': BLUE, 'mint': MINT, 'purple': PURPLE, 'gold': GOLD, 'red': RED}


class SVG:
    def __init__(self, title, subtitle, tag, duration):
        self.title = title
        self.duration = duration
        self.parts = []
        self.definitions = '''
<linearGradient id="background" x2="1" y2="1"><stop stop-color="#101c30"/><stop offset="1" stop-color="#050a13"/></linearGradient>
<linearGradient id="glass" x2=".3" y2="1"><stop stop-color="#182d48"/><stop offset="1" stop-color="#0b1424"/></linearGradient>
<linearGradient id="edge" x2=".8" y2="1"><stop stop-color="#6384a9" stop-opacity=".5"/><stop offset=".5" stop-color="#243951"/><stop offset="1" stop-color="#6384a9" stop-opacity=".15"/></linearGradient>
<radialGradient id="atmosphere"><stop stop-color="#28568a" stop-opacity=".24"/><stop offset="1" stop-color="#28568a" stop-opacity="0"/></radialGradient>
<radialGradient id="halo"><stop stop-color="#62d4ff" stop-opacity=".15"/><stop offset="1" stop-color="#62d4ff" stop-opacity="0"/></radialGradient>
<linearGradient id="seat" x2=".2" y2="1"><stop stop-color="#284d60"/><stop offset="1" stop-color="#102636"/></linearGradient>
<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dy="14" stdDeviation="18" flood-color="#000" flood-opacity=".35"/></filter>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#7499be" opacity=".13"/></pattern>
<symbol id="users" viewBox="0 0 64 64"><circle cx="27" cy="21" r="9"/><path d="M10 49v-4c0-9 7-14 17-14s17 5 17 14v4M44 13c13 1 13 16 3 18M49 36c7 2 9 6 9 13"/></symbol>
<symbol id="chip" viewBox="0 0 64 64"><rect x="14" y="14" width="36" height="36" rx="7"/><rect x="23" y="23" width="18" height="18" rx="4"/><path d="M23 5v9m18-9v9M23 50v9m18-9v9M5 23h9m-9 18h9M50 23h9m-9 18h9"/></symbol>
<symbol id="redis" viewBox="0 0 64 64"><path d="m6 22 26-13 26 13-26 13Zm0 12 26 13 26-13M6 46l26 13 26-13"/></symbol>
<symbol id="database" viewBox="0 0 64 64"><ellipse cx="32" cy="14" rx="23" ry="9"/><path d="M9 14v34c0 12 46 12 46 0V14M9 30c0 12 46 12 46 0"/></symbol>
<symbol id="kafka" viewBox="0 0 64 64"><path d="m27 31 20-17M28 33l20 17M25 27V12m0 26v14"/><circle cx="24" cy="32" r="9"/><circle cx="25" cy="7" r="5"/><circle cx="52" cy="10" r="6"/><circle cx="53" cy="53" r="6"/><circle cx="25" cy="57" r="5"/></symbol>
<symbol id="lock" viewBox="0 0 64 64"><rect x="13" y="28" width="38" height="29" rx="8"/><path d="M21 28V18c0-15 22-15 22 0v10"/><circle cx="32" cy="41" r="3"/><path d="M32 44v5"/></symbol>
<symbol id="key" viewBox="0 0 64 64"><circle cx="22" cy="23" r="14"/><circle cx="19" cy="20" r="3"/><path d="m32 33 22 22h7v-8h-8v-8h-9"/></symbol>
'''
        for name, color in COLORS.items():
            self.definitions += f'<linearGradient id="tail-{name}"><stop stop-color="{color}" stop-opacity="0"/><stop offset="1" stop-color="{color}" stop-opacity=".8"/></linearGradient>\n'
        self.add('<rect width="1600" height="860" rx="26" fill="url(#background)"/>')
        self.add('<rect x="1" y="1" width="1598" height="858" rx="25" fill="none" stroke="#30465f" stroke-opacity=".6"/>')
        self.add('<ellipse cx="740" cy="410" rx="780" ry="420" fill="url(#atmosphere)"/>')
        self.add('<rect x="32" y="140" width="1536" height="560" fill="url(#grid)"/>')
        self.text(58, 104, title, 45, weight=650)

    def add(self, markup):
        self.parts.append(markup)

    def text(self, x, y, text, size=20, color=TEXT, weight=400, anchor='start', mono=False):
        family = ('Consolas,Malgun Gothic,monospace' if mono
                  else 'Malgun Gothic,Apple SD Gothic Neo,Noto Sans KR,Segoe UI,sans-serif')
        self.add(f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(text)}</text>')

    def rect(self, x, y, w, h, fill='url(#glass)', stroke='url(#edge)', radius=22, extra=''):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" {extra}/>')

    def circle(self, x, y, r, fill='none', stroke='none', extra=''):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" {extra}/>')

    def animate(self, attribute, points, extra=''):
        points = sorted(dict(points).items())
        assert points[0][0] == 0 and points[-1][0] == self.duration
        times = ';'.join(f'{t / self.duration:.5f}' for t, _ in points)
        values = ';'.join(str(v) for _, v in points)
        return f'<animate attributeName="{attribute}" dur="{self.duration}s" repeatCount="indefinite" keyTimes="{times}" values="{values}" {extra}/>'

    def window(self, start, end, fade=.18):
        points = [(0, 1 if start == 0 else 0), (self.duration, 0)]
        if start > 0:
            points += [(start, 0), (start + fade, 1)]
        points += [(end - fade, 1), (end, 0)]
        return self.animate('opacity', points)

    def group(self, content, start=0, end=None, fade=.18, extra=''):
        self.add(f'<g opacity="0" {extra}>{self.window(start, end or self.duration, fade)}{content}</g>')

    def fragment(self, callback):
        start = len(self.parts)
        callback()
        content = ''.join(self.parts[start:])
        del self.parts[start:]
        return content

    def icon(self, name, x, y, size, color):
        self.add(f'<use href="#{name}" x="{x}" y="{y}" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round"/>')

    def route(self, path, color=None, start=0, end=None):
        self.add(f'<path d="{path}" fill="none" stroke="#1d334c" stroke-width="2"/>')
        if color:
            self.group(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-opacity=".48"/>', start, end)

    def packet(self, path, start, end, color='blue', size=1):
        assert 0 < start < end < self.duration
        c = COLORS[color]
        content = f'''<g transform="scale({size})">
<path d="M-38-2.5 Q-16-5 -3-3 L-3 3 Q-16 5-38 2.5Z" fill="url(#tail-{color})"/>
<ellipse rx="9" ry="6" fill="{c}" opacity=".45" filter="url(#glow)"/>
<circle r="4.2" fill="{c}"/><circle cx="1" cy="-1" r="1.5" fill="#fff" opacity=".9"/></g>'''
        times = f'0;{start / self.duration:.5f};{end / self.duration:.5f};1'
        motion = f'<animateMotion path="{path}" dur="{self.duration}s" repeatCount="indefinite" rotate="auto" keyPoints="0;0;1;1" keyTimes="{times}" calcMode="spline" keySplines="0 0 1 1;.32 0 .68 1;0 0 1 1"/>'
        self.add(f'<g class="packet" opacity="0">{motion}{self.window(start, end, .13)}{content}</g>')

    def pulse(self, x, y, color, start, end, radius=30):
        self.group(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="none" stroke="{color}" stroke-width="2">'
                   f'<animate attributeName="r" values="{radius};{radius + 24}" dur="1.6s" repeatCount="indefinite"/>'
                   '<animate attributeName="opacity" values=".65;0" dur="1.6s" repeatCount="indefinite"/></circle>', start, end)

    def node(self, x, y, w, h, icon, title, subtitle, color, label):
        self.rect(x, y, w, h, extra='filter="url(#shadow)"')
        self.rect(x + 18, y + 20, 62, 62, fill='#0c192a', stroke='#30445a', radius=18)
        self.icon(icon, x + 27, y + 29, 44, color)
        self.text(x + 96, y + 65, title, 30, weight=600)
        if label:
            self.text(x + 24, y + h - 26, label, 22, MUTED)

    def timeline(self, stages):
        w = 1480 / len(stages)
        for i, (title, detail, start, end, color) in enumerate(stages):
            x = 60 + i * w
            self.add(f'<path d="M{x} 734h{w - 20}" stroke="#293c53" stroke-width="2"/>')
            self.text(x, 774, title, 24, MUTED, weight=600)
            self.group(self.fragment(lambda: self.text(x, 774, title, 24, color, weight=600)), start, end)
            self.group(f'<path d="M{x} 734h{w - 20}" stroke="{color}" stroke-width="3" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
                       + self.animate('stroke-dashoffset', [(0, 1), (start, 1), (end, 0), (self.duration, 0)]) + '</path>', start, end)

    def finish(self, filename, description):
        markup = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="860" viewBox="0 0 1600 860" style="max-width:100%;height:auto" role="img" aria-labelledby="title description">
<title id="title">{escape(self.title)}</title><desc id="description">{escape(description)}</desc>
<defs>{self.definitions}</defs>
{''.join(self.parts)}
</svg>\n'''
        root = ET.fromstring(markup)
        for el in root.iter():
            assert not el.tag.endswith(('script', 'foreignObject', 'image'))
        (OUT / filename).write_text(markup, encoding='utf-8', newline='\n')
        print(f'{filename}: {len(markup.encode()) / 1024:.1f} KiB, native vector motion, {self.duration}s loop')


def traffic():
    s = SVG('티켓 구매 흐름', '', '', 16.5)
    incoming = 'M330 361 C402 361 431 361 515 361'
    returning = 'M515 414 C435 414 416 414 330 414'
    redis = 'M805 345 C930 345 928 252 1120 252'
    redis_return = 'M1120 287 C950 287 960 395 805 395'
    database = 'M805 416 C930 416 963 433 1120 433'
    database_return = 'M1120 470 C981 470 943 458 805 458'
    kafka = 'M805 488 C939 488 926 614 1120 614'
    for path in (incoming, returning, redis, redis_return, database, database_return, kafka):
        s.route(path)
    s.add('<ellipse cx="660" cy="405" rx="250" ry="228" fill="url(#halo)"/>')
    s.circle(660, 405, 183, stroke='#284c6c', extra='stroke-opacity=".5"')
    stages = [
        ('캐시 조회', '', 0, 4, BLUE),
        ('대기 순번', '', 4, 8, PURPLE),
        ('예약 · 주문', '', 8, 12, GOLD),
        ('결제 확정', '', 12, 16.5, MINT),
    ]
    # Keep one connected signal, but cross hidden node interiors in less than
    # one display frame. Only the visible connecting routes take travel time.
    transfer = .004
    user, server = (210, 383), (660, 405)
    incoming_curves = [((275, 383), (280, 361), (330, 361)),
                       ((402, 361), (431, 361), (515, 361)),
                       ((580, 361), (600, 405), server)]
    response_curves = [((600, 405), (600, 414), (515, 414)),
                       ((435, 414), (416, 414), (330, 414)),
                       ((280, 414), (260, 383), user)]
    redis_curves = [((730, 405), (730, 345), (805, 345)),
                    ((930, 345), (928, 252), (1120, 252)),
                    ((1140, 252), (1160, 260), (1160, 269))]
    redis_back_curves = [((1140, 275), (1120, 287), (1120, 287)),
                         ((950, 287), (960, 395), (805, 395)),
                         ((730, 395), (730, 405), server)]
    db_curves = [((730, 405), (730, 416), (805, 416)),
                 ((930, 416), (963, 433), (1120, 433)),
                 ((1140, 433), (1160, 442), (1160, 450))]
    db_back_curves = [((1140, 456), (1120, 470), (1120, 470)),
                      ((981, 470), (943, 458), (805, 458)),
                      ((730, 458), (730, 405), server)]
    event_curves = [((730, 405), (730, 488), (805, 488)),
                    ((939, 488), (926, 614), (1120, 614)),
                    ((1140, 614), (1160, 625), (1160, 634))]

    def signal(origin, legs, color, kind='request'):
        path = f'M{origin[0]} {origin[1]}'
        position, distance = origin, 0
        stops = [(0, 0)]
        for start, end, curves in legs:
            assert end - start > 2 * transfer and len(curves) == 3
            if stops[-1][0] != start:
                stops.append((start, distance))
            for index, (control1, control2, target) in enumerate(curves):
                path += ' C' + ' '.join(str(v) for point in (control1, control2, target) for v in point)
                previous = position
                # Numerical arc length aligns motion stops with node centers.
                for step in range(1, 101):
                    t = step / 100
                    point = tuple((1 - t) ** 3 * position[j]
                                  + 3 * (1 - t) ** 2 * t * control1[j]
                                  + 3 * (1 - t) * t ** 2 * control2[j]
                                  + t ** 3 * target[j] for j in range(2))
                    distance += sum((point[j] - previous[j]) ** 2 for j in range(2)) ** .5
                    previous = point
                position = target
                curve_end = start + transfer if index == 0 else end - transfer if index == 1 else end
                stops.append((curve_end, distance))
        stops.append((s.duration, distance))
        assert all(a[0] < b[0] for a, b in zip(stops, stops[1:]))
        times = ';'.join(f'{time / s.duration:.7f}' for time, _ in stops)
        points = ';'.join(f'{length / distance:.7f}' for _, length in stops)
        c = COLORS[color]
        s.add(f'''<g class="packet" data-flow="{kind}" data-start="{legs[0][0]}" data-end="{legs[-1][1]}" data-origin="{origin[0]},{origin[1]}" opacity="0">
<animateMotion path="{path}" dur="{s.duration}s" repeatCount="indefinite" rotate="auto" keyPoints="{points}" keyTimes="{times}" calcMode="linear"/>
{s.window(legs[0][0], legs[-1][1], transfer)}
<path d="M-38-2.5 Q-16-5 -3-3 L-3 3 Q-16 5-38 2.5Z" fill="url(#tail-{color})"/>
<ellipse rx="9" ry="6" fill="{c}" opacity=".45" filter="url(#glow)"/>
<circle r="4.2" fill="{c}"/><circle cx="1" cy="-1" r="1.5" fill="#fff" opacity=".9"/>
</g>''')

    for phase, (_, _, start, end, color) in enumerate(stages):
        cname = ('blue', 'purple', 'gold', 'mint')[phase]
        target, reply = (redis, redis_return) if phase < 2 else (database, database_return)
        out_curves, back_curves = (redis_curves, redis_back_curves) if phase < 2 else (db_curves, db_back_curves)
        steps = [(.7, incoming_curves), (1.05, out_curves), (1.05, back_curves)]
        if phase < 3:
            steps.append((.7, response_curves))
        legs, time = [], start + .16
        for travel, curves in steps:
            arrival = time + travel + 2 * transfer
            legs.append((time, arrival, curves))
            time = arrival
        for route, a, b in ((incoming, *legs[0][:2]), (target, *legs[1][:2]), (reply, *legs[2][:2])):
            s.route(route, color, a, b)
        if phase < 3:
            s.route(returning, color, *legs[3][:2])
        signal(user, legs, cname)
        if phase == 3:
            fork_start = time

    # After the committed payment returns to the server, the only fan-out is
    # response + event. Both signals start at the exact same place and time.
    for curves, path, kind, travel in ((response_curves, returning, 'response', .7),
                                      (event_curves, kafka, 'event', 1.15)):
        fork_end = fork_start + travel + 2 * transfer
        s.route(path, MINT, fork_start, fork_end)
        signal(server, [(fork_start, fork_end, curves)], 'mint', kind)

    # Opaque node cards cover the internal motion, leaving one visible signal
    # on the connecting routes until the explicit post-commit fan-out.
    s.node(90, 288, 240, 190, 'users', '사용자', '', BLUE, '')
    s.rect(515, 260, 290, 300, extra='filter="url(#shadow)"')
    s.rect(607, 287, 106, 100, fill='#10243a', stroke='#3b6487', radius=26)
    s.icon('chip', 628, 305, 64, BLUE)
    s.text(660, 429, '예매 서버', 32, weight=650, anchor='middle')
    s.node(1120, 196, 370, 145, 'redis', 'Redis', '', PURPLE, '조회 캐시 · 대기 순번')
    s.node(1120, 379, 370, 145, 'database', 'PostgreSQL', '', GOLD, '예약 · 결제 저장')
    s.node(1120, 562, 370, 145, 'kafka', 'Kafka', '', MINT, '구매 완료 이벤트')
    for phase, (_, _, start, end, color) in enumerate(stages):
        action = ('캐시 조회 후 응답', '순번 발급 후 응답', '예약 저장 후 응답', '결제 확정')[phase]
        s.group(s.fragment(lambda: s.text(660, 505, action, 23, color, anchor='middle')),
                start, fork_start if phase == 3 else end)
    s.group(s.fragment(lambda: s.text(660, 505, '응답 · 이벤트 발행', 23, MINT, anchor='middle')), fork_start, s.duration)
    s.timeline(stages)
    s.finish('01-request-traffic.svg', '캐시 조회, 대기 순번, 예약과 결제 요청은 각각 하나의 신호로 순서대로 이동합니다. 결제 확정 후에만 예매 서버 한곳에서 구매 응답과 완료 이벤트가 갈라집니다. 대기 순번은 토큰 관리 기능입니다.')


def concurrency():
    s = SVG('동시 예약, 중복 선점 방지', '', '', 12)
    s.text(90, 222, '20명 동시 요청', 26, MUTED)
    points = [(118 + (i % 4) * 86, 282 + (i // 4) * 74) for i in range(20)]
    for i, (x, y) in enumerate(points):
        path = f'M{x + 24} {y} C500 {y} 506 408 620 408'
        back = f'M620 429 C503 429 491 {y + 10} {x + 24} {y + 10}'
        s.route(path)
        s.packet(path, .28 + i * .045, 2.3 + i * .025, 'blue', .8)
        if i:
            end = 4.9 + i * .105
            s.packet(back, end - 1.25, end, 'red', .8)
    s.add('<ellipse cx="952" cy="446" rx="232" ry="230" fill="url(#halo)"/>')
    for i, (x, y) in enumerate(points):
        s.circle(x, y, 25, '#102038', '#355370')
        s.circle(x, y - 5, 5, 'none', BLUE, 'stroke-width="1.5"')
        s.add(f'<path d="M{x - 9} {y + 11}c0-13 18-13 18 0" fill="none" stroke="{BLUE}" stroke-width="1.5"/>')
        color, start = (MINT, 3.15) if i == 0 else (RED, 4.9 + i * .105)
        overlay = f'<circle cx="{x}" cy="{y}" r="25" fill="#102038" stroke="{color}" stroke-width="2"/>'
        overlay += (f'<path d="M{x - 7} {y}l5 5 10-11" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>' if i == 0 else f'<path d="M{x - 6} {y - 6}l12 12m-12 0 12-12" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        s.group(overlay, start, 11.8)
    s.route('M750 408 C799 408 807 408 857 408', GOLD, 2.25, 11.7)
    s.packet('M750 408 C799 408 807 408 857 408', 2.58, 3.15, 'gold', 1.1)
    s.rect(620, 345, 130, 130, fill='url(#glass)', stroke='#826c49', radius=28, extra='filter="url(#shadow)"')
    s.icon('lock', 654, 367, 62, GOLD)
    s.text(685, 505, '비관적 잠금', 25, GOLD, anchor='middle')
    s.pulse(685, 410, GOLD, 2.2, 4.1, 68)
    s.add('<ellipse cx="954" cy="529" rx="139" ry="27" fill="#000" opacity=".3"/><ellipse cx="954" cy="521" rx="134" ry="27" fill="#143440" stroke="#2b5260"/>')
    s.text(954, 265, '좌석 1개', 26, TEXT, weight=600, anchor='middle')
    s.rect(904, 302, 100, 121, fill='url(#seat)', stroke='#7096a9', radius=25, extra='stroke-width="2"')
    s.rect(891, 418, 126, 36, fill='url(#seat)', stroke='#7096a9', radius=16, extra='stroke-width="2"')
    s.rect(875, 379, 15, 75, fill='#1e4053', stroke='#7096a9', radius=7)
    s.rect(1018, 379, 15, 75, fill='#1e4053', stroke='#7096a9', radius=7)
    s.add('<path d="M906 454v43m97-43v43" stroke="#7096a9" stroke-width="9" stroke-linecap="round"/>')
    s.group('<rect x="904" y="302" width="100" height="121" rx="25" fill="none" stroke="#7af4c4" stroke-width="3" filter="url(#glow)"/><path d="m936 359 12 12 24-26" fill="none" stroke="#7af4c4" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>', 3.15, 11.8)
    s.group(s.fragment(lambda: s.text(954, 578, '예약 가능', 25, BLUE, anchor='middle')), 0, 3.15)
    def held():
        s.text(954, 578, '5분 임시 예약', 25, MINT, anchor='middle')
    s.group(s.fragment(held), 3.15, 11.8)
    s.route('M1041 360 C1135 360 1135 297 1230 297', MINT, 3.15, 11.8)
    s.packet('M1041 360 C1135 360 1135 297 1230 297', 3.2, 3.9, 'mint', 1.1)
    s.text(1230, 250, '예약 성공', 25, MINT)
    s.group(s.fragment(lambda: s.text(1230, 339, '0', 86, MINT, weight=600)), 0, 3.9)
    s.group(s.fragment(lambda: s.text(1230, 339, '1', 86, MINT, weight=600)), 3.9, 11.8)
    s.text(1352, 331, '건', 25, MUTED)
    s.text(1230, 438, '충돌 거절', 25, RED)
    for count in range(20):
        start = 0 if count == 0 else 4.9 + count * .105
        end = 4.9 + (count + 1) * .105 if count < 19 else 11.8
        s.group(s.fragment(lambda n=count: s.text(1230, 527, str(n), 86, RED, weight=600)), start, end, fade=.025)
    s.text(1352, 519, '건', 25, MUTED)
    s.group(s.fragment(lambda: s.text(1230, 584, '중복 예약 0건', 25, MINT)), 7.2, 11.8)
    s.timeline([
        ('동시 요청', '', 0, 2.3, BLUE),
        ('좌석 잠금', '', 2.3, 4.4, GOLD),
        ('충돌 거절', '', 4.4, 7.2, RED),
        ('처리 완료', '', 7.2, 12, MINT),
    ])
    s.finish('02-seat-contention.svg', '동일 좌석에 20명이 동시에 예약을 요청합니다. 비관적 잠금으로 1건만 선점하고 나머지 19건은 충돌로 거절합니다. 성공 고객은 잠금 획득 순서에 따라 달라집니다.')


def payments():
    s = SVG('결제 재시도, 기존 결과 반환', '', '', 12)
    starts = (0, 4, 8)
    colors = (PURPLE, BLUE, RED)
    request_paths, return_paths = [], []
    for i, y in enumerate((239, 373, 507)):
        path = f'M422 {y + 45} C493 {y + 45} 490 349 555 349'
        back = f'M555 394 C490 394 494 {y + 71} 422 {y + 71}'
        request_paths.append(path)
        return_paths.append(back)
        s.route(path)
        s.route(back)
    db = 'M849 339 C939 339 953 292 1100 292'
    db_back = 'M1100 362 C954 362 945 411 849 411'
    kafka = 'M849 444 C966 444 970 592 1140 592'
    for path in (db, db_back, kafka):
        s.route(path)
    for i, y in enumerate((239, 373, 507)):
        color = colors[i]
        s.rect(60, y, 362, 107, radius=20)
        s.text(85, y + 43, ('첫 결제', '같은 결제 재시도', '멱등키 재사용')[i], 28, color, weight=600)
        s.text(85, y + 82, ('새 멱등키', '동일 키 · 주문 · 금액', '다른 주문 또는 금액')[i], 23, MUTED)
        s.group(f'<rect x="60" y="{y}" width="362" height="107" rx="20" fill="none" stroke="{color}" stroke-width="2"/>', starts[i], starts[i] + 4)
        a = starts[i]
        cname = ('purple', 'blue', 'red')[i]
        s.route(request_paths[i], color, a, a + 4)
        s.route(return_paths[i], color, a, a + 4)
        s.packet(request_paths[i], a + .25, a + 1.05, cname, 1.15)
        s.packet(db, a + 1.08, a + 1.72, 'gold')
        s.packet(db_back, a + 1.82, a + 2.38, 'gold')
        s.packet(return_paths[i], a + 2.95, a + 3.75, cname, 1.15)
    s.add('<ellipse cx="702" cy="366" rx="227" ry="233" fill="url(#halo)"/>')
    s.rect(555, 238, 294, 252, extra='filter="url(#shadow)"')
    s.circle(702, 311, 47, '#142b40', '#3d627d')
    s.icon('key', 675, 284, 54, PURPLE)
    s.text(702, 397, '결제 처리', 32, weight=650, anchor='middle')
    s.text(702, 450, '멱등키 확인', 24, PURPLE, anchor='middle')
    s.rect(1100, 217, 440, 222, extra='filter="url(#shadow)"')
    s.icon('database', 1124, 239, 47, GOLD)
    s.text(1188, 269, '결제 기록', 32, weight=600)
    s.add('<path d="M1124 305h392" stroke="#30445b"/>')
    s.group(s.fragment(lambda: s.text(1126, 377, '저장된 결과 없음', 28, MUTED)), 0, 2.75)
    s.group(s.fragment(lambda: s.text(1126, 377, '승인 결과 1건', 32, MINT)), 2.75, 11.8)
    s.node(1140, 535, 400, 139, 'kafka', '완료 이벤트', '', MINT, '구매 확정 후 발행')
    s.route(kafka, MINT, 2.85, 4)
    s.packet(kafka, 2.89, 3.79, 'mint', 1.2)
    s.group(s.fragment(lambda: s.text(555, 562, '한 트랜잭션으로 확정', 24, MUTED)), 0, 4)
    s.group(s.fragment(lambda: s.text(555, 562, '완료 상태 유지', 24, MUTED)), 4, 12)
    s.rect(555, 582, 520, 75, fill='#101c2d', stroke='#2b425a', radius=14)
    states = '예약 · 주문 · 좌석 · 티켓'
    s.group(s.fragment(lambda: s.text(815, 631, states, 26, MUTED, anchor='middle')), 0, 2.75)
    s.group(s.fragment(lambda: s.text(815, 631, states, 26, MINT, anchor='middle')), 2.75, 11.8)
    outcomes = ('신규 승인', '기존 결과 반환', '키 재사용 거절')
    for i, text in enumerate(outcomes):
        s.group(s.fragment(lambda i=i, text=text: s.text(60, 684, text, 28, colors[i], weight=600)), starts[i], starts[i] + 4)
    s.timeline([
        ('첫 승인', '', 0, 4, PURPLE),
        ('결제 재시도', '', 4, 8, BLUE),
        ('키 재사용 거절', '', 8, 12, RED),
    ])
    s.finish('03-payment-replay.svg', '첫 결제는 예약, 주문, 좌석, 티켓을 함께 확정하고 완료 이벤트를 발행합니다. 첫 승인 이후 동일한 멱등키, 주문, 금액으로 재시도하면 기존 결과를 반환합니다. 다른 주문이나 금액에 같은 키를 재사용하면 거절합니다.')


if __name__ == '__main__':
    traffic()
    concurrency()
    payments()
