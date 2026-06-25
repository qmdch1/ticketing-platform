create table performances (
    id uuid primary key,
    title varchar(200) not null,
    starts_at timestamptz not null
);

create table seats (
    id uuid primary key,
    performance_id uuid not null references performances(id),
    section varchar(30) not null,
    seat_number varchar(30) not null,
    price bigint not null check (price >= 0),
    status varchar(20) not null,
    reservation_id uuid,
    version bigint not null default 0,
    unique (performance_id, section, seat_number)
);

create index idx_seats_performance_status on seats(performance_id, status);

create table reservations (
    id uuid primary key,
    performance_id uuid not null references performances(id),
    customer_id uuid not null,
    status varchar(20) not null,
    expires_at timestamptz not null,
    created_at timestamptz not null
);

create table reservation_seats (
    reservation_id uuid not null references reservations(id),
    seat_id uuid not null,
    primary key (reservation_id, seat_id)
);

create table ticket_orders (
    id uuid primary key,
    reservation_id uuid not null unique references reservations(id),
    customer_id uuid not null,
    total_amount bigint not null check (total_amount >= 0),
    status varchar(30) not null,
    created_at timestamptz not null
);

create table payments (
    id uuid primary key,
    order_id uuid not null references ticket_orders(id),
    idempotency_key varchar(100) not null unique,
    amount bigint not null check (amount >= 0),
    status varchar(20) not null,
    approved_at timestamptz
);

create table tickets (
    id uuid primary key,
    order_id uuid not null references ticket_orders(id),
    performance_id uuid not null references performances(id),
    seat_id uuid not null,
    ticket_code varchar(100) not null unique,
    status varchar(20) not null,
    issued_at timestamptz not null,
    unique (order_id, seat_id)
);
