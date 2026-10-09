"""Render the README's illustrative traffic animations with Pillow.

Run from any directory: python docs/animations/render_traffic.py
The diagrams describe service behavior, not measured throughput. The payment
replay scene is sequential and does not claim concurrent exactly-once delivery.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
WIDTH, HEIGHT, SCALE = 1180, 660, 2
BG = "#0b1220"
PANEL = "#111e31"
EDGE = "#263952"
TEXT = "#edf5ff"
MUTED = "#9cafc8"
BLUE = "#64b5ff"
MINT = "#5de4ba"
AMBER = "#ffcc70"
PURPLE = "#ba9aff"
RED = "#ff8b9d"


def font_path(bold: bool) -> str:
    candidates = [
        Path("C:/Windows/Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu")
        / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental")
        / ("Arial Bold.ttf" if bold else "Arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise RuntimeError("Install Segoe UI, DejaVu Sans, or Arial to render the diagrams")


FONTS = {
    (size, bold): ImageFont.truetype(font_path(bold), size * SCALE)
    for size in (14, 16, 18, 20, 22, 24, 26, 30, 36, 44)
    for bold in (False, True)
}


class Canvas:
    def __init__(self, title: str, subtitle: str, badge: str, accent: str):
        self.im = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), BG)
        self.d = ImageDraw.Draw(self.im)
        self.rect((0, 0, WIDTH, 5), accent, radius=0)
        self.text((40, 23), title, 36, bold=True)
        self.text((42, 76), subtitle, 18, MUTED)
        self.pill((918, 34, 1138, 74), badge, accent)
        self.text((42, 630), "TICKETING PLATFORM", 14, MUTED, bold=True)
        self.text((1138, 630), "ILLUSTRATIVE FLOW  /  LOOP", 14, MUTED, anchor="ra")

    def text(self, xy, value, size=18, color=TEXT, bold=False, anchor="la"):
        self.d.text(
            tuple(v * SCALE for v in xy), value,
            font=FONTS[size, bold], fill=color, anchor=anchor,
        )

    def rect(self, box, fill=PANEL, outline=None, radius=18, width=1):
        self.d.rounded_rectangle(
            tuple(int(v * SCALE) for v in box), radius=radius * SCALE,
            fill=fill, outline=outline, width=width * SCALE,
        )

    def line(self, pts, color=EDGE, width=2):
        self.d.line(
            [(int(x * SCALE), int(y * SCALE)) for x, y in pts],
            fill=color, width=width * SCALE, joint="curve",
        )

    def dot(self, xy, color, r=5):
        x, y = xy
        self.d.ellipse(
            ((x - r) * SCALE, (y - r) * SCALE,
             (x + r) * SCALE, (y + r) * SCALE), fill=color,
        )

    def pill(self, box, label, accent):
        self.rect(box, PANEL, accent, radius=12)
        self.text(((box[0] + box[2]) / 2, box[1] + 8), label,
                  16, accent, bold=True, anchor="ma")

    def card(self, box, kicker, title, subtitle, accent, active=True):
        self.rect(box, PANEL, accent if active else EDGE, width=2)
        x, y, _, _ = box
        self.text((x + 20, y + 16), kicker, 14,
                  accent if active else MUTED, bold=True)
        self.text((x + 20, y + 41), title, 26, bold=True)
        self.text((x + 20, y + 80), subtitle, 16, MUTED)

    def route(self, pts, active=False, color=BLUE):
        self.line(pts, color if active else EDGE, 2)
        x, y = pts[-1]
        px, py = pts[-2]
        angle = math.atan2(y - py, x - px)
        arrow = [
            (x - 9 * math.cos(angle - .5), y - 9 * math.sin(angle - .5)),
            (x, y),
            (x - 9 * math.cos(angle + .5), y - 9 * math.sin(angle + .5)),
        ]
        self.line(arrow, color if active else EDGE, 2)

    def packet(self, pts, progress, color, radius=6):
        if not 0 <= progress <= 1:
            return
        lengths = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
        remaining = progress * sum(lengths)
        for i, length in enumerate(lengths):
            if remaining <= length:
                a, b = pts[i], pts[i + 1]
                ratio = remaining / length if length else 0
                self.dot((a[0] + (b[0] - a[0]) * ratio,
                          a[1] + (b[1] - a[1]) * ratio), color, radius)
                return
            remaining -= length

    def during(self, pts, p, start, end, color, count=1):
        for i in range(count):
            shift = i * .07
            self.packet(pts, (p - start - shift) / (end - start), color)

    def timeline(self, labels, selected, accent, progress):
        gap, x0, y, total = 12, 42, 551, 1096
        width = (total - gap * (len(labels) - 1)) / len(labels)
        for i, label in enumerate(labels):
            x = x0 + i * (width + gap)
            self.rect((x, y, x + width, y + 55), PANEL,
                      accent if i == selected else EDGE, radius=12)
            self.text((x + 16, y + 13), f"0{i + 1}  {label}", 18,
                      accent if i == selected else MUTED, bold=i == selected)
            if i == selected:
                self.line([(x + 12, y + 50), (x + 12 + (width - 24) * progress, y + 50)],
                          accent, 3)

    def finish(self):
        return self.im.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def traffic(frame: int) -> Image.Image:
    phase, p = frame // 36, (frame % 36) / 35
    accent = (BLUE, PURPLE, AMBER, MINT)[phase]
    badges = ("SEAT CACHE HIT", "QUEUE TOKEN", "HOLD + ORDER", "COMMIT + EVENT")
    c = Canvas("Follow the request.", "Clients / Spring API / Redis / PostgreSQL / Kafka",
               badges[phase], accent)
    client_api = [(258, 318), (404, 318)]
    api_client = [(404, 359), (258, 359)]
    api_redis = [(652, 297), (748, 297), (748, 186), (876, 186)]
    redis_api = [(876, 211), (782, 211), (782, 324), (652, 324)]
    api_db = [(652, 348), (876, 348)]
    db_api = [(876, 377), (652, 377)]
    api_kafka = [(652, 401), (748, 401), (748, 480), (876, 480)]
    c.route(client_api, True, accent)
    c.route(api_client, True, accent)
    c.route(api_redis, phase != 3, accent)
    c.route(redis_api, phase in (0, 1), accent)
    c.route(api_db, phase in (2, 3), accent)
    c.route(db_api, phase in (2, 3), accent)
    c.route(api_kafka, phase == 3 and p >= .57, MINT)
    c.card((42, 245, 258, 425), "HTTP REQUESTS", "Clients", "Browse / reserve / pay", BLUE)
    for i in range(5):
        c.dot((74 + i * 32, 385), accent, 6)
    c.card((404, 245, 652, 440), "APPLICATION", "Spring API", "Domain transactions", accent)
    c.pill((424, 366, 631, 413),
           ("GET seats", "POST token", "POST hold / order", "POST payment")[phase], accent)
    c.card((876, 131, 1138, 249), "CACHE + WAITING ROOM", "Redis", "10s TTL / Sorted Set", PURPLE, phase != 3)
    c.card((876, 294, 1138, 412), "SOURCE OF TRUTH", "PostgreSQL", "Locks / atomic state", AMBER, phase in (2, 3))
    c.card((876, 457, 1138, 575), "AFTER COMMIT", "Kafka", "ticket-issued-events", MINT, phase == 3 and p >= .57)
    c.text((286, 276), "request", 16, MUTED)
    c.text((288, 374), "response", 16, MUTED)
    c.during(client_api, p, .02, .19, accent, 2)
    if phase in (0, 1):
        c.during(api_redis, p, .24, .42, accent)
        c.during(redis_api, p, .48, .67, accent)
        c.during(api_client, p, .72, .88, MINT, 2)
    elif phase == 2:
        c.during(api_db, p, .25, .40, AMBER, 2)
        c.during(db_api, p, .49, .63, MINT, 2)
        c.during(api_redis, p, .62, .81, AMBER)
        c.during(api_client, p, .76, .93, MINT)
    else:
        c.during(api_db, p, .24, .40, AMBER)
        c.during(db_api, p, .44, .56, MINT)
        c.during(api_kafka, p, .58, .83, MINT)
        c.during(api_client, p, .76, .93, MINT)
    details = (
        ("Redis HIT", "Cached seats return to the client."),
        ("Token + rank", "Issue / reuse / cancel tokens; no admission gate."),
        ("Lock + write", "Hold the seat, create an order, evict the seat cache."),
        ("Commit first", "Payment writes commit before the ticket event is sent."),
    )
    c.text((42, 470), details[phase][0], 24, accent, bold=True)
    c.text((42, 509), details[phase][1], 18, MUTED)
    # The timeline ends before the Kafka column, keeping every label visible.
    labels = ("Cache", "Token", "Hold", "Pay")
    for i, label in enumerate(labels):
        x = 42 + i * 200
        c.rect((x, 555, x + 188, 605), PANEL,
               accent if phase == i else EDGE, radius=10)
        c.text((x + 16, 566), f"0{i + 1}  {label}", 18,
               accent if phase == i else MUTED, bold=phase == i)
        if phase == i:
            c.line([(x + 12, 600), (x + 12 + 164 * p, 600)], accent, 3)
    return c.finish()


def concurrency(frame: int) -> Image.Image:
    p = frame / 107
    phase = min(int(p * 4), 3)
    c = Canvas("20 requests. One seat.", "Concurrent reservations / PostgreSQL PESSIMISTIC_WRITE",
               "SAME SEAT: A1", AMBER)
    c.text((42, 124), "20 CUSTOMERS", 16, MUTED, bold=True)
    center = (344, 301)
    destinations = []
    for i in range(20):
        x, y = 42 + (i % 4) * 64, 170 + (i // 4) * 59
        point = (x + 52, y + 22)
        destinations.append(point)
        c.line([point, center], EDGE, 1)
    # Route the burst behind the client tiles and stop before the lock label.
    for i, point in enumerate(destinations):
        start = .08 + i * .006
        c.during([point, center], p, start, start + .20, BLUE)
    for i in range(20):
        x, y = 42 + (i % 4) * 64, 170 + (i // 4) * 59
        arrived = p >= .08 + i * .006 + .20
        rejected = i > 0 and p >= .48 + i * .01
        color = MINT if i == 0 and p >= .38 else RED if rejected else BLUE
        c.rect((x, y, x + 52, y + 44), PANEL, color if arrived else EDGE, radius=9)
        c.text((x + 26, y + 10), f"{i + 1:02d}", 16, color, bold=True, anchor="ma")
    c.route([center, (354, 301)], p >= .28, AMBER)
    c.route([(562, 301), (625, 301)], p >= .28, AMBER)
    c.card((354, 214, 562, 387), "SERIALIZE WRITES", "Row lock", "SELECT ... FOR UPDATE", AMBER, p >= .28)
    c.pill((374, 331, 541, 370), "ACQUIRED" if p >= .28 else "WAITING", AMBER)
    held = p >= .39
    c.card((625, 214, 840, 387), "SHARED RESOURCE", "Seat A1", "5-minute reservation", MINT if held else BLUE)
    c.pill((645, 331, 819, 370), "HELD" if held else "AVAILABLE", MINT if held else BLUE)
    c.route([(840, 276), (920, 276)], held, MINT)
    c.route([(840, 344), (876, 344), (876, 418), (920, 418)], p >= .49, RED)
    rejected_count = sum(p >= .48 + i * .01 for i in range(1, 20))
    c.rect((920, 214, 1138, 326), PANEL, MINT, width=2)
    c.text((941, 229), "201 CREATED", 16, MINT, bold=True)
    c.text((940, 255), f"{int(held):02d}", 44, MINT, bold=True)
    c.text((1017, 273), "hold", 20, MUTED)
    c.rect((920, 354, 1138, 466), PANEL, RED, width=2)
    c.text((941, 369), "409 CONFLICT", 16, RED, bold=True)
    c.text((940, 395), f"{rejected_count:02d}", 44, RED, bold=True)
    c.text((1017, 413), "rejected", 20, MUTED)
    # The drawn winner is illustrative; real lock acquisition order can vary.
    c.during([(562, 301), (625, 301)], p, .29, .39, MINT)
    c.during([(840, 276), (920, 276)], p, .40, .48, MINT)
    for i in range(1, 20):
        c.during([(840, 344), (876, 344), (876, 418), (920, 418)],
                 p, .43 + i * .01, .48 + i * .01, RED)
    status = (
        "All clients request A1 at the same time.",
        "One transaction locks A1 and changes AVAILABLE to HELD.",
        "Later lock holders see HELD and return SEAT_NOT_AVAILABLE.",
        "1 successful hold / 19 conflicts / 0 duplicate reservations.",
    )[phase]
    c.text((42, 499), status, 20, MINT if phase == 3 else MUTED)
    c.timeline(("Burst", "Acquire lock", "Reject conflicts", "Result"), phase, AMBER,
               p * 4 - phase)
    return c.finish()


def payments(frame: int) -> Image.Image:
    phase, p = frame // 44, (frame % 44) / 43
    accent = (MINT, BLUE, RED)[phase]
    c = Canvas("Retries reuse the payment.", "Idempotency-Key / sequential replay / same order + amount",
               ("FIRST REQUEST", "REPLAY REQUEST", "KEY MISMATCH")[phase], accent)
    client_api = [(266, 242), (433, 242)]
    api_client = [(433, 281), (266, 281)]
    api_db = [(697, 242), (876, 242)]
    db_api = [(876, 281), (697, 281)]
    kafka = [(697, 322), (858, 322), (858, 422), (876, 422)]
    c.route(client_api, True, accent)
    c.route(api_client, p >= .66, accent)
    c.route(api_db, True, AMBER)
    c.route(db_api, True, AMBER)
    c.route(kafka, phase == 0 and p >= .68, MINT)
    c.card((42, 176, 266, 335), "PAYMENT REQUEST", "Client", "POST /orders/.../payments", BLUE)
    c.card((433, 176, 697, 335), "VALIDATE / APPROVE", "PaymentService", "Lookup by Idempotency-Key", accent)
    c.card((876, 176, 1138, 335), "PAYMENT RECORD", "PostgreSQL", "New write / existing result", AMBER)
    c.card((876, 363, 1138, 481), "AFTER COMMIT", "Kafka", "ticket-issued-events", MINT,
           phase == 0 and p >= .68)
    c.pill((42, 363, 316, 403), "key: payment-request-001", PURPLE)
    c.text((42, 418), "order-001 / KRW 120,000" if phase != 2 else "order-002 / same key",
           18, RED if phase == 2 else MUTED)
    committed = phase > 0 or p >= .65
    c.during(client_api, p, .03, .19, accent)
    c.during(api_db, p, .23, .37, AMBER)
    c.during(db_api, p, .40, .53, AMBER)
    if phase == 0:
        c.during(api_db, p, .54, .64, MINT)
        c.during(kafka, p, .69, .85, MINT)
        c.during(api_client, p, .80, .96, MINT)
    else:
        c.during(api_client, p, .66, .87, accent)
    status = (
        "MISS > lock + write > COMMIT > publish event",
        "HIT > validate order + amount > return existing payment",
        "HIT > different order > 409 IDEMPOTENCY_KEY_REUSED",
    )[phase]
    c.text((352, 371),
           "ATOMIC DATABASE TRANSACTION" if phase == 0 else "EXISTING COMMITTED STATE",
           14, MINT if committed else MUTED, bold=True)
    items = (("Reservation", "CONFIRMED"), ("Order", "PAID"), ("Seat", "SOLD"),
             ("Ticket", "ISSUED"), ("Payment", "APPROVED"))
    for i, (name, state) in enumerate(items):
        x = 352 + i * 101
        c.rect((x, 403, x + 93, 465), PANEL, MINT if committed else EDGE, radius=10)
        c.text((x + 46, 409), name, 14, MUTED, anchor="ma")
        c.text((x + 46, 436), state if committed else "PENDING", 14,
               MINT if committed else MUTED, bold=True, anchor="ma")
    c.text((42, 499), status, 20, accent)
    c.timeline(("Approve once", "Reuse result", "Reject mismatch"), phase, accent, p)
    return c.finish()


def save_animation(filename: str, renderer, count: int):
    frames = [renderer(i) for i in range(count)]
    # One palette for the entire loop avoids color changes between frames.
    samples = Image.new("RGB", (WIDTH, HEIGHT * 6), BG)
    for i in range(6):
        samples.paste(frames[i * (count - 1) // 5], (0, HEIGHT * i))
    palette = samples.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    path = OUT / filename
    indexed[0].save(path, save_all=True, append_images=indexed[1:],
                    duration=90, loop=0, optimize=True, disposal=1)
    print(f"{path.name}: {count} frames, {count * .09:.2f}s, {path.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    save_animation("01-request-traffic.gif", traffic, 144)
    save_animation("02-seat-contention.gif", concurrency, 108)
    save_animation("03-payment-replay.gif", payments, 132)
