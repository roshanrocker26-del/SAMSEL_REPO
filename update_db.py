import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from django.db import connection

sql = """
DROP TABLE IF EXISTS school CASCADE;
CREATE TABLE school (
	school_name VARCHAR(150) NOT NULL,
    school_id VARCHAR(50) PRIMARY KEY,
    contact VARCHAR(15),
    password_hash VARCHAR(200) NOT NULL
);
INSERT INTO school VALUES
('St.George','SG01','9123456456','SG@123'),
('Maharishi','MAH01','9988777234','MAH@123'),
('SKHM School','SKHM02','9345612112','SKHM@123');

DROP TABLE IF EXISTS purchase_items CASCADE;
DROP TABLE IF EXISTS purchase CASCADE;
DROP TABLE IF EXISTS books CASCADE;

CREATE TABLE books (
    book_id VARCHAR(50) PRIMARY KEY,
    series_name VARCHAR(100) NOT NULL,
    class VARCHAR(20) NOT NULL,
    path VARCHAR(150)
);

INSERT INTO books (book_id,series_name,class) VALUES
('ibot1','i-bot','1'),
('ibot2','i-bot','2'),
('ibot3','i-bot','3'),
('ibot4','i-bot','4'),
('ibot5','i-bot','5'),
('ibot6','i-bot','6'),
('ibot7','i-bot','7'),
('ibot8','i-bot','8'),
('ibot9','i-bot','9'),

('iwhizz1','i-whizz','1'),
('iwhizz2','i-whizz','2'),
('iwhizz3','i-whizz','3'),
('iwhizz4','i-whizz','4'),
('iwhizz5','i-whizz','5'),
('iwhizz6','i-whizz','6'),
('iwhizz7','i-whizz','7'),
('iwhizz8','i-whizz','8'),
('iwhizz9','i-whizz','9'),

('ismart1','i-smart','1'),
('ismart2','i-smart','2'),
('ismart3','i-smart','3'),
('ismart4','i-smart','4'),
('ismart5','i-smart','5'),
('ismart6','i-smart','6'),
('ismart7','i-smart','7'),
('ismart8','i-smart','8'),
('ismart9','i-smart','9');

CREATE TABLE purchase (
    purchase_id VARCHAR(50) PRIMARY KEY,
    school_id VARCHAR(50) NOT NULL,
    purchase_date DATE DEFAULT CURRENT_DATE,

    CONSTRAINT fk_purchase_school
    FOREIGN KEY (school_id)
    REFERENCES school(school_id)
    ON DELETE CASCADE
);

INSERT INTO purchase VALUES
('pSG1','SG01',CURRENT_DATE),
('pMAH1','MAH01',CURRENT_DATE),
('pSK1','SKHM02','2026-03-01');

CREATE TABLE purchase_items (
    id SERIAL PRIMARY KEY,
    purchase_id VARCHAR(50) NOT NULL,
    book_id VARCHAR(50) NOT NULL,
    valid_upto DATE NOT NULL,

    CONSTRAINT fk_purchase_items_purchase
    FOREIGN KEY (purchase_id)
    REFERENCES purchase(purchase_id)
    ON DELETE CASCADE,

    CONSTRAINT fk_purchase_items_book
    FOREIGN KEY (book_id)
    REFERENCES books(book_id)
    ON DELETE CASCADE,

    CONSTRAINT unique_purchase_book
    UNIQUE (purchase_id, book_id)
);

INSERT INTO purchase_items (purchase_id,book_id,valid_upto) VALUES

('pSG1','iwhizz6',CURRENT_DATE + INTERVAL '365 days'),
('pSG1','ibot2',CURRENT_DATE + INTERVAL '365 days'),

('pMAH1','ismart9',CURRENT_DATE + INTERVAL '365 days'),
('pMAH1','iwhizz6',CURRENT_DATE + INTERVAL '365 days'),

('pSK1','ibot3',CURRENT_DATE + INTERVAL '365 days'),
('pSK1','iwhizz6',CURRENT_DATE + INTERVAL '365 days');
"""

with connection.cursor() as cursor:
    cursor.execute(sql)
print("Database schema successfully updated")
