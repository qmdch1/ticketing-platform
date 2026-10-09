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
        self.text(58, 43, 'T I C K E T I N G   /   E N G I N E E R I N G', 15, MUTED, weight=600)
        self.text(58, 104, title, 45, weight=650)
        self.text(60, 142, subtitle, 21, MUTED)
        self.rect(1265, 60, 275, 43, fill='#101d2e', stroke='#304b67', radius=22)
        self.circle(1289, 81, 4, MINT)
        self.text(1310, 87, tag, 16, MUTED, mono=True)
        self.text(60, 825, 'REQUESTS  /  RESPONSES  /  STATE', 15, MUTED, mono=True)
        self.text(1540, 825, 'ILLUSTRATIVE · CONTINUOUS LOOP', 15, MUTED, anchor='end', mono=True)

    def add(self, markup):
        self.parts.append(markup)

    def text(self, x, y, text, size=20, color=TEXT, weight=400, anchor='start', mono=False):
        family = 'Consolas,DejaVu Sans Mono,monospace' if mono else 'Segoe UI,Arial,sans-serif'
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
        self.text(x + 96, y + 45, label, 16 if w < 300 else 17, color, weight=600)
        self.text(x + 96, y + 76, title, 26, weight=600)
        self.text(x + 24, y + h - 23, subtitle, 19 if w < 300 else 20, MUTED)

    def timeline(self, stages):
        w = 1480 / len(stages)
        for i, (title, detail, start, end, color) in enumerate(stages):
            x = 60 + i * w
            self.add(f'<path d="M{x} 734h{w - 20}" stroke="#293c53" stroke-width="2"/>')
            self.text(x, 769, f'0{i + 1}  {title}', 20, MUTED, weight=600)
            self.group(self.fragment(lambda: self.text(x, 769, f'0{i + 1}  {title}', 20, color, weight=600)), start, end)
            self.text(x, 795, detail, 18, MUTED)
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
        (OUT / filename).write_text(markup, encoding='utf-8')
        print(f'{filename}: {len(markup.encode()) / 1024:.1f} KiB, native vector motion, {self.duration}s loop')


def traffic():
    s = SVG('Every request has a path.', 'A live view of the ticketing purchase flow.', '01 / REQUEST TRAFFIC', 16)
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
    s.add('<g><animateTransform attributeName="transform" type="rotate" from="0 660 405" to="360 660 405" dur="24s" repeatCount="indefinite"/><circle cx="660" cy="405" r="183" fill="none" stroke="#62d4ff" stroke-opacity=".65" stroke-width="2" stroke-dasharray="28 260"/></g>')
    s.node(90, 288, 240, 190, 'users', 'Clients', 'Browse · reserve · pay', BLUE, 'HTTP REQUESTS')
    s.rect(515, 260, 290, 300, extra='filter="url(#shadow)"')
    s.rect(607, 287, 106, 100, fill='#10243a', stroke='#3b6487', radius=26)
    s.icon('chip', 628, 305, 64, BLUE)
    s.text(660, 429, 'Spring API', 32, weight=650, anchor='middle')
    s.text(660, 459, 'Domain transactions', 19, MUTED, anchor='middle')
    s.node(1120, 196, 370, 145, 'redis', 'Redis', '10s seat cache · Sorted Set tokens', PURPLE, 'CACHE / WAITING ROOM')
    s.node(1120, 379, 370, 145, 'database', 'PostgreSQL', 'Row locks · atomic purchase state', GOLD, 'SOURCE OF TRUTH')
    s.node(1120, 562, 370, 145, 'kafka', 'Kafka', 'ticket-issued-events', MINT, 'AFTER TRANSACTION COMMIT')
    s.text(392, 337, 'REQUEST', 16, MUTED, mono=True)
    s.text(394, 449, 'RESPONSE', 16, MUTED, mono=True)
    stages = [
        ('Seat cache', 'Redis HIT → return cached seats', 0, 4, BLUE),
        ('Waiting token', 'Issue / reuse / cancel → rank', 4, 8, PURPLE),
        ('Reserve & order', 'Lock → hold → order → evict', 8, 12, GOLD),
        ('Approve payment', 'Atomic COMMIT → ticket event', 12, 16, MINT),
    ]
    for phase, (_, _, start, end, color) in enumerate(stages):
        cname = ('blue', 'purple', 'gold', 'mint')[phase]
        s.route(incoming, color, start, end)
        s.route(returning, MINT, start, end)
        method = ('GET /seats', 'POST /waiting-room', 'POST /hold · /orders', 'POST /payments')[phase]
        def badge():
            s.rect(540, 486, 240, 43, fill='#0b1829', stroke=color, radius=14)
            s.text(660, 514, method, 17, color, anchor='middle', mono=True)
        s.group(s.fragment(badge), start, end)
        for i in range(3):
            a = start + .18 + i * .92
            s.packet(incoming, a, a + .85, cname)
            s.packet(returning, a + 1.05, min(a + 1.95, end - .04), 'mint')
        target = redis if phase < 2 else database
        reply = redis_return if phase < 2 else database_return
        s.route(target, color, start, end)
        s.route(reply, color, start, end)
        for i in range(2):
            a = start + .72 + i * 1.22
            s.packet(target, a, a + .82, cname)
            s.packet(reply, a + .95, a + 1.66, cname)
        if phase == 2:
            s.route(redis, GOLD, 10.5, 12)
            s.packet(redis, 10.65, 11.65, 'gold')
        if phase == 3:
            s.route(kafka, MINT, 14.2, 16)
            s.packet(kafka, 14.32, 15.45, 'mint', 1.2)
            s.pulse(1160, 625, MINT, 15.1, 15.95, 34)
        caption = ('CACHE HIT', 'TOKEN + RANK', 'PESSIMISTIC_WRITE', 'COMMIT → PUBLISH')[phase]
        s.group(s.fragment(lambda: s.text(660, 630, caption, 23, color, anchor='middle', mono=True)), start, end)
    s.timeline(stages)
    s.finish('01-request-traffic.svg', 'Animated clients, Spring API, Redis cache and waiting tokens, PostgreSQL reservations and payments, and Kafka ticket events after commit. Tokens do not enforce admission.')


def concurrency():
    s = SVG('Twenty requests. One owner.', 'One shared seat. Every request passes through the database lock.', '02 / SEAT CONTENTION', 12)
    s.text(90, 222, '20 CONCURRENT CUSTOMERS', 17, MUTED, mono=True)
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
        s.text(x, y + 44, f'{i + 1:02}', 14, MUTED, anchor='middle', mono=True)
        color, start = (MINT, 3.15) if i == 0 else (RED, 4.9 + i * .105)
        overlay = f'<circle cx="{x}" cy="{y}" r="25" fill="#102038" stroke="{color}" stroke-width="2"/>'
        overlay += (f'<path d="M{x - 7} {y}l5 5 10-11" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>' if i == 0 else f'<path d="M{x - 6} {y - 6}l12 12m-12 0 12-12" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        s.group(overlay, start, 11.8)
    s.route('M750 408 C799 408 807 408 857 408', GOLD, 2.25, 11.7)
    s.packet('M750 408 C799 408 807 408 857 408', 2.58, 3.15, 'gold', 1.1)
    s.rect(620, 345, 130, 130, fill='url(#glass)', stroke='#826c49', radius=28, extra='filter="url(#shadow)"')
    s.icon('lock', 654, 367, 62, GOLD)
    s.text(685, 505, 'ROW LOCK', 19, GOLD, anchor='middle', mono=True)
    s.text(685, 535, 'FOR UPDATE', 15, MUTED, anchor='middle', mono=True)
    s.pulse(685, 410, GOLD, 2.2, 4.1, 68)
    s.add('<ellipse cx="954" cy="529" rx="139" ry="27" fill="#000" opacity=".3"/><ellipse cx="954" cy="521" rx="134" ry="27" fill="#143440" stroke="#2b5260"/>')
    s.text(954, 265, 'SEAT A1', 23, TEXT, weight=600, anchor='middle')
    s.rect(904, 302, 100, 121, fill='url(#seat)', stroke='#7096a9', radius=25, extra='stroke-width="2"')
    s.rect(891, 418, 126, 36, fill='url(#seat)', stroke='#7096a9', radius=16, extra='stroke-width="2"')
    s.rect(875, 379, 15, 75, fill='#1e4053', stroke='#7096a9', radius=7)
    s.rect(1018, 379, 15, 75, fill='#1e4053', stroke='#7096a9', radius=7)
    s.add('<path d="M906 454v43m97-43v43" stroke="#7096a9" stroke-width="9" stroke-linecap="round"/>')
    s.group('<rect x="904" y="302" width="100" height="121" rx="25" fill="none" stroke="#7af4c4" stroke-width="3" filter="url(#glow)"/><path d="m936 359 12 12 24-26" fill="none" stroke="#7af4c4" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>', 3.15, 11.8)
    s.group(s.fragment(lambda: s.text(954, 578, 'AVAILABLE', 20, BLUE, anchor='middle', mono=True)), 0, 3.15)
    def held():
        s.text(954, 578, 'HELD · 5 MIN', 20, MINT, anchor='middle', mono=True)
        s.text(954, 608, 'No second owner.', 19, MUTED, anchor='middle')
    s.group(s.fragment(held), 3.15, 11.8)
    s.route('M1041 360 C1135 360 1135 297 1230 297', MINT, 3.15, 11.8)
    s.packet('M1041 360 C1135 360 1135 297 1230 297', 3.2, 3.9, 'mint', 1.1)
    s.text(1230, 250, '201 CREATED', 17, MINT, mono=True)
    s.group(s.fragment(lambda: s.text(1230, 339, '00', 86, MINT, weight=600)), 0, 3.9)
    s.group(s.fragment(lambda: s.text(1230, 339, '01', 86, MINT, weight=600)), 3.9, 11.8)
    s.text(1352, 331, 'reservation', 22, MUTED)
    s.text(1230, 438, '409 CONFLICT', 17, RED, mono=True)
    for count in range(20):
        start = 0 if count == 0 else 4.9 + count * .105
        end = 4.9 + (count + 1) * .105 if count < 19 else 11.8
        s.group(s.fragment(lambda n=count: s.text(1230, 527, f'{n:02}', 86, RED, weight=600)), start, end, fade=.025)
    s.text(1352, 519, 'rejected', 22, MUTED)
    s.text(1230, 584, 'SEAT_NOT_AVAILABLE', 15, RED, mono=True)
    s.text(90, 666, 'One winner is illustrative. Actual ownership follows lock acquisition order.', 20, MUTED)
    s.timeline([
        ('Request burst', '20 clients → the same seat', 0, 2.3, BLUE),
        ('Acquire & hold', 'AVAILABLE → HELD', 2.3, 4.4, GOLD),
        ('Reject conflicts', 'Later lock holders see HELD', 4.4, 7.2, RED),
        ('One owner', '1 hold / 19 conflicts / 0 duplicates', 7.2, 12, MINT),
    ])
    s.finish('02-seat-contention.svg', 'Twenty concurrent seat requests converge on a PostgreSQL write lock. One client holds the seat for five minutes; nineteen receive conflicts. The chosen winner is illustrative.')


def payments():
    s = SVG('Same key. Same payment.', 'Sequential retries return the committed result instead of creating another ticket.', '03 / PAYMENT REPLAY', 12)
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
        s.text(85, y + 33, ('FIRST REQUEST', 'SAME ORDER · SAME AMOUNT', 'DIFFERENT ORDER · SAME KEY')[i], 18, color, mono=True)
        s.text(85, y + 66, 'payment-request-001', 21, weight=600)
        s.text(85, y + 91, 'order-002 · 120,000 KRW' if i == 2 else 'order-001 · 120,000 KRW', 17, MUTED, mono=True)
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
    s.text(702, 397, 'PaymentService', 29, weight=650, anchor='middle')
    s.text(702, 430, 'Lookup → validate → approve', 18, MUTED, anchor='middle')
    s.text(702, 461, 'Idempotency-Key', 17, PURPLE, anchor='middle', mono=True)
    s.rect(1100, 217, 440, 222, extra='filter="url(#shadow)"')
    s.icon('database', 1124, 239, 47, GOLD)
    s.text(1188, 257, 'PostgreSQL', 27, weight=600)
    s.text(1188, 283, 'THE COMMITTED PAYMENT', 14, GOLD, mono=True)
    s.add('<path d="M1124 305h392" stroke="#30445b"/>')
    s.text(1126, 341, 'payment-request-001', 21, PURPLE, mono=True)
    s.text(1126, 374, 'order-001 · 120,000 KRW', 19, MUTED, mono=True)
    s.group(s.fragment(lambda: s.text(1126, 410, 'LOOKUP: NOT FOUND', 19, MUTED, mono=True)), 0, 2.75)
    s.group(s.fragment(lambda: s.text(1126, 410, 'APPROVED · payment-001', 19, MINT, mono=True)), 2.75, 11.8)
    s.node(1140, 535, 400, 139, 'kafka', 'Kafka', 'ticket-issued-events', MINT, 'FIRST APPROVAL / AFTER COMMIT')
    s.route(kafka, MINT, 2.85, 4)
    s.packet(kafka, 2.89, 3.79, 'mint', 1.2)
    s.group(s.fragment(lambda: s.text(555, 562, 'ONE ATOMIC DATABASE TRANSACTION', 17, MUTED, mono=True)), 0, 4)
    s.group(s.fragment(lambda: s.text(555, 562, 'EXISTING COMMITTED STATE', 17, MUTED, mono=True)), 4, 12)
    items = (('Reservation', 'CONFIRMED'), ('Order', 'PAID'), ('Seat', 'SOLD'), ('Ticket', 'ISSUED'), ('Payment', 'APPROVED'))
    for i, (name, status) in enumerate(items):
        x = 555 + i * 106
        s.rect(x, 582, 96, 75, fill='#101c2d', stroke='#2b425a', radius=14)
        s.text(x + 48, 607, name, 17, MUTED, anchor='middle')
        s.group(s.fragment(lambda x=x: s.text(x + 48, 635, 'PENDING', 16, MUTED, weight=600, anchor='middle')), 0, 2.75)
        s.group(s.fragment(lambda x=x, value=status: s.text(x + 48, 635, value, 16, MINT, weight=600, anchor='middle')), 2.75, 11.8)
    outcomes = ('NEW APPROVAL → COMMIT → EVENT', 'EXISTING PAYMENT → SAME RESULT', '409 · IDEMPOTENCY_KEY_REUSED')
    for i, text in enumerate(outcomes):
        s.group(s.fragment(lambda i=i, text=text: s.text(60, 684, text, 21, colors[i], mono=True)), starts[i], starts[i] + 4)
    s.timeline([
        ('First approval', 'Write state → COMMIT → publish', 0, 4, PURPLE),
        ('Sequential replay', 'Same order + amount → same payment', 4, 8, BLUE),
        ('Reject reused key', 'Different order or amount → conflict', 8, 12, RED),
    ])
    s.finish('03-payment-replay.svg', 'The initial payment writes all purchase state atomically, then publishes a ticket event after commit. A subsequent matching replay returns the same approved payment; key reuse for a different order or amount is rejected.')


if __name__ == '__main__':
    traffic()
    concurrency()
    payments()
