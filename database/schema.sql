CREATE TABLE books
(
book_id serial PRIMARY KEY,
book_name VARCHAR (300) NOT NULL,
author VARCHAR (255) NOT NULL,
publisher VARCHAR (300) NOT NULL,
genre VARCHAR (255)
);


CREATE TABLE members
(
member_id serial PRIMARY KEY,
member_name VARCHAR (300) NOT NULL,
joining_date TIMESTAMP NOT NULL,
exit_date TIMESTAMP,
is_active BOOLEAN NOT NULL,
contact VARCHAR (20) UNIQUE NOT NULL,
address VARCHAR (1000)
);

CREATE TABLE borrowings
(
borrowing_id serial PRIMARY KEY,
book_id INT NOT NULL,
member_id INT NOT NULL,
borrow_date TIMESTAMP NOT NULL,
return_date TIMESTAMP,
fine NUMERIC(10,2),
due_date TIMESTAMP NOT NULL,
CONSTRAINT borrowings_book_id_fkey FOREIGN KEY (book_id)
 REFERENCES books (book_id) MATCH SIMPLE
 ON UPDATE NO ACTION ON DELETE NO ACTION,
CONSTRAINT borrowings_member_id_fkey FOREIGN KEY (member_id)
 REFERENCES members (member_id) MATCH SIMPLE
 ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE INDEX idx_borrowings_member
ON borrowings(member_id);

CREATE INDEX idx_borrowings_book

ON borrowings(book_id);

CREATE UNIQUE INDEX idx_active_borrowing
ON borrowings(book_id)
WHERE return_date IS NULL;