-- Synthetic data for local development of the dedicated test database.
-- Never run this against a database containing data you need to keep.
TRUNCATE TABLE borrowings, members, books RESTART IDENTITY CASCADE;

INSERT INTO books (book_name, author, publisher, genre) VALUES
('Clean Code', 'Robert C. Martin', 'Prentice Hall', 'Programming'),
('The Pragmatic Programmer', 'Andrew Hunt, David Thomas', 'Addison-Wesley', 'Programming'),
('Design Patterns', 'Erich Gamma et al.', 'Addison-Wesley', 'Software Engineering'),
('1984', 'George Orwell', 'Secker & Warburg', 'Fiction');

INSERT INTO members
    (member_name, joining_date, exit_date, is_active, contact, address)
VALUES
('Alice Johnson', '2024-01-15 10:30:00', NULL, TRUE, '9000000001', '12 Maple Street'),
('Brian Smith', '2023-08-10 09:15:00', NULL, TRUE, '9000000002', '45 Oak Avenue'),
('Inactive Member', '2022-05-20 14:00:00', '2025-02-28 17:00:00', FALSE, '9000000003', NULL);

INSERT INTO borrowings
    (book_id, member_id, borrow_date, due_date, return_date, fine)
VALUES
(1, 1, '2026-05-01 10:00:00', '2026-05-15 10:00:00', '2026-05-14 10:00:00', 0),
(2, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '14 days', NULL, NULL),
(3, 1, '2026-04-01 10:00:00', '2026-04-15 10:00:00', '2026-04-18 10:00:00', 30);
