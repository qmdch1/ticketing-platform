insert into performances(id, title, starts_at)
values ('11111111-1111-1111-1111-111111111111', 'Backend Live 2026', '2026-12-20T10:00:00Z');

insert into seats(id, performance_id, section, seat_number, price, status)
values
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', '11111111-1111-1111-1111-111111111111', 'A', '1', 120000, 'AVAILABLE'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', '11111111-1111-1111-1111-111111111111', 'A', '2', 120000, 'AVAILABLE'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', '11111111-1111-1111-1111-111111111111', 'A', '3', 120000, 'AVAILABLE'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4', '11111111-1111-1111-1111-111111111111', 'A', '4', 120000, 'AVAILABLE'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5', '11111111-1111-1111-1111-111111111111', 'A', '5', 120000, 'AVAILABLE');
