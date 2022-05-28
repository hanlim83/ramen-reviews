DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ExID INTEGER NOT NULL,
    Country TEXT NOT NULL,
    Brand TEXT NOT NULL,
    `Type` TEXT NOT NULL,
    Packaging TEXT CHECK (Packaging in ('Cup','Pack','Tray','Bowl','Box','Can','Bar')) NOT NULL,
    Rating REAL CHECK (Rating >= 0 AND Rating <=5) NOT NULL
);