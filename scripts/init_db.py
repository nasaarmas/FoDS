import psycopg2

INIT_TABLES = [
    "CREATE TABLE IF NOT EXISTS Uzytkownik (id SERIAL PRIMARY KEY, login VARCHAR(255) UNIQUE, imie VARCHAR(255), nazwisko VARCHAR(255), haslo VARCHAR(255), czyAdmin BOOLEAN);",
    "CREATE TABLE IF NOT EXISTS Student (id SERIAL PRIMARY KEY, idUzytkownik INTEGER, FOREIGN KEY (idUzytkownik) REFERENCES Uzytkownik(id) ON DELETE CASCADE);",
    "CREATE TABLE IF NOT EXISTS Nauczyciel (id SERIAL PRIMARY KEY, idUzytkownik INTEGER, FOREIGN KEY (idUzytkownik) REFERENCES Uzytkownik(id) ON DELETE CASCADE);",
    "CREATE TABLE IF NOT EXISTS Autor (id SERIAL PRIMARY KEY, idUzytkownik INTEGER, FOREIGN KEY (idUzytkownik) REFERENCES Uzytkownik(id) ON DELETE CASCADE);",
    "CREATE TABLE IF NOT EXISTS Manager (id SERIAL PRIMARY KEY, idUzytkownik INTEGER, FOREIGN KEY (idUzytkownik) REFERENCES Uzytkownik(id) ON DELETE CASCADE);",
    "CREATE TABLE IF NOT EXISTS Kurs (id SERIAL PRIMARY KEY, Nazwa VARCHAR(255) UNIQUE);",
    "CREATE TABLE IF NOT EXISTS Edycja (id SERIAL PRIMARY KEY, Semestr VARCHAR(255) UNIQUE);",
    "CREATE TABLE IF NOT EXISTS EdycjaKursu (id SERIAL PRIMARY KEY, Nazwa VARCHAR(255) UNIQUE, NazwaKursu VARCHAR(255), SemestrEdycji VARCHAR(255), FOREIGN KEY (NazwaKursu) REFERENCES Kurs(Nazwa), FOREIGN KEY (SemestrEdycji) REFERENCES Edycja(Semestr));",
    "CREATE TABLE IF NOT EXISTS Materialy (id SERIAL PRIMARY KEY, Autor VARCHAR(255), Nazwa VARCHAR(255) UNIQUE, idNauczyciel INT, FOREIGN KEY (idNauczyciel) REFERENCES Uzytkownik(id));",
    "CREATE TABLE IF NOT EXISTS MaterialyEdycjaKursu (id SERIAL PRIMARY KEY, idMaterialy INT, idEdycjaKursu INT, FOREIGN KEY (idMaterialy) REFERENCES Materialy(id), FOREIGN KEY (idEdycjaKursu) REFERENCES EdycjaKursu(id));",
    "CREATE TABLE IF NOT EXISTS StudentEdycjaKursu (id SERIAL PRIMARY KEY, idStudent INT, idEdycjaKursu INT, czyZdal bool DEFAULT false, FOREIGN KEY (idStudent) REFERENCES Uzytkownik(id), FOREIGN KEY (idEdycjaKursu) REFERENCES EdycjaKursu(id));",
    "CREATE TABLE IF NOT EXISTS Egzamin (id SERIAL PRIMARY KEY, Nazwa VARCHAR(255) UNIQUE, Autor VARCHAR(255));",
    "CREATE TABLE IF NOT EXISTS EgzaminEdycjaKursu (id SERIAL PRIMARY KEY, Nazwa VARCHAR(255) UNIQUE, idEgzamin INT, idEdycjaKursu INT, FOREIGN KEY (idEgzamin) REFERENCES Egzamin(id), FOREIGN KEY (idEdycjaKursu) REFERENCES EdycjaKursu(id));",
    "CREATE TABLE IF NOT EXISTS KursDziedzina (id SERIAL PRIMARY KEY, NazwaKursu VARCHAR(255), DziedzinaNazwa VARCHAR(255), FOREIGN KEY (NazwaKursu) REFERENCES Kurs(Nazwa));",
    "CREATE TABLE IF NOT EXISTS StudentEgzamin (id SERIAL PRIMARY KEY, idStudent INT, EgzaminNazwa VARCHAR(255), czyZdal bool DEFAULT false, FOREIGN KEY (idStudent) REFERENCES Uzytkownik(id), FOREIGN KEY (EgzaminNazwa) REFERENCES Egzamin(Nazwa));",
    "CREATE TABLE IF NOT EXISTS KompetencjaEgzamin (id SERIAL PRIMARY KEY, idKompetencja INT, EgzaminEdycjaKursuNazwa VARCHAR(255));",
    "CREATE TABLE IF NOT EXISTS KompetencjaEdycjaKursu (id SERIAL PRIMARY KEY, idKompetencja INT, idEdycjaKursu INT);",
    "CREATE TABLE IF NOT EXISTS StudentKompetencja (id SERIAL PRIMARY KEY, idStudent INT, idKompetencja INT);",
    "CREATE TABLE IF NOT EXISTS Kompetencja (id SERIAL PRIMARY KEY, Nazwa VARCHAR(255) UNIQUE, idManager INT, FOREIGN KEY (idManager) REFERENCES Uzytkownik(id));"
    "CREATE TABLE IF NOT EXISTS Dziedzina (id SERIAL PRIMARY KEY, Nazwa VARCHAR(255) UNIQUE, idTworca INT, FOREIGN KEY (idTworca) REFERENCES Uzytkownik(id));",
    "CREATE TABLE IF NOT EXISTS StudentCertyfikat (id SERIAL PRIMARY KEY, idStudent INT, CertyfikatNazwa VARCHAR(255));",
    "CREATE TABLE IF NOT EXISTS KompetencjaCertyfikat (id SERIAL PRIMARY KEY, idKompetencja INT, CertyfikatNazwa VARCHAR(255));",
    "CREATE TABLE IF NOT EXISTS Certyfikat (id SERIAL PRIMARY KEY, Nazwa VARCHAR(255) UNIQUE, idManager INT, FOREIGN KEY (idManager) REFERENCES Uzytkownik(id));",
    "CREATE TABLE IF NOT EXISTS CertyfikatDziedzina (id SERIAL PRIMARY KEY, CertyfikatNazwa VARCHAR(255), DziedzinaNazwa VARCHAR(255), FOREIGN KEY (CertyfikatNazwa) REFERENCES Certyfikat(Nazwa), FOREIGN KEY (DziedzinaNazwa) REFERENCES Dziedzina(Nazwa));"
]

DUMMY_DATA = '''
WITH inserted_students AS (
    INSERT INTO Uzytkownik (login, imie, nazwisko, haslo, czyAdmin) VALUES 
    ('jankowalski', 'Jan', 'Kowalski', 'haslo123', FALSE),
    ('annanowak', 'Anna', 'Nowak', 'haslo123', TRUE),
    ('tomaszjankowski', 'Tomasz', 'Jankowski', 'haslo123', FALSE),
    ('mariawojcik', 'Maria', 'Wojcik', 'haslo123', FALSE),
    ('piotrkaczmarek', 'Piotr', 'Kaczmarek', 'haslo123', FALSE),
    ('magdalenakrawczyk', 'Magdalena', 'Krawczyk', 'haslo123', FALSE),
    ('marcinzawadzki', 'Marcin', 'Zawadzki', 'haslo123', FALSE),
    ('katarzynawolak', 'Katarzyna', 'Wolak', 'haslo123', FALSE),
    ('michalsikora', 'Michal', 'Sikora', 'haslo123', FALSE),
    ('karolinamaj', 'Karolina', 'Maj', 'haslo123', FALSE)
    RETURNING id
)
INSERT INTO Student (idUzytkownik) 
SELECT id FROM inserted_students;

WITH inserted_teachers AS (
    INSERT INTO Uzytkownik (login, imie, nazwisko, haslo, czyAdmin) VALUES 
    ('robertlewandowski', 'Robert', 'Lewandowski', 'haslo321', TRUE),
    ('lukaszpiszczek', 'Lukasz', 'Piszczek', 'haslo321', FALSE),
    ('wojciechszczesny', 'Wojciech', 'Szczesny', 'haslo321', FALSE),
    ('jakubblaszczykowski', 'Jakub', 'Blaszczykowski', 'haslo321', FALSE),
    ('grzegorzkrychowiak', 'Grzegorz', 'Krychowiak', 'haslo321', FALSE)
    RETURNING id
)
INSERT INTO Nauczyciel (idUzytkownik) 
SELECT id FROM inserted_teachers;

INSERT INTO Kurs (Nazwa) VALUES 
('Kurs programowania w Pythonie'),
('Kurs lutowania'),
('Kurs Inventora'),
('Kurs baz danych'),
('Kurs UI/UX');

INSERT INTO Edycja (Semestr) VALUES 
('2022L'),
('2022Z'),
('2023L'),
('2023Z'),
('2024L');

INSERT INTO EdycjaKursu (Nazwa, NazwaKursu, SemestrEdycji) VALUES 
('Kurs lutowania_2022L', 'Kurs lutowania', '2022L'),
('Kurs lutowania_2022Z', 'Kurs lutowania', '2022Z'),
('Kurs lutowania_2023L', 'Kurs lutowania', '2023L'),
('Kurs baz danych_2022L', 'Kurs baz danych', '2022L'),
('Kurs baz danych_2022Z', 'Kurs baz danych', '2022Z');


INSERT INTO StudentEdycjaKursu (idStudent, idEdycjaKursu) VALUES 
(1, 1),
(1, 2),
(1, 3),
(2, 2);

INSERT INTO Manager (idUzytkownik) VALUES (2);
INSERT INTO Autor (idUzytkownik) VALUES (2);
INSERT INTO Nauczyciel (idUzytkownik) VALUES (2);

INSERT INTO Kompetencja (Nazwa, idmanager) VALUES
('lutowanie', 1),
('spawanie', 1),
('programowanie obiektowe', 1),
('sieci komputerowe', 1),
('programowanie strukturalne', 1);

INSERT INTO Dziedzina (nazwa, idtworca) VALUES 
('Elektronika', 2),
('Informatyka', 2),
('Matematyka', 2),
('Ekonomia', 2);

INSERT INTO StudentKompetencja (idstudent, idkompetencja) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(2, 1),
(2, 2),
(2, 3),
(2, 4),
(2, 5);

INSERT INTO Certyfikat (nazwa, idmanager) VALUES 
('Zaawansowane programowanie', 2),
('Tworzenie układów scalonych', 2);

INSERT INTO certyfikatdziedzina (certyfikatnazwa, dziedzinanazwa) VALUES 
('Zaawansowane programowanie', 'Informatyka'),
('Tworzenie układów scalonych', 'Elektronika'),
('Zaawansowane programowanie', 'Matematyka');
'''

CLEAR_DB = [
    "DROP TABLE IF EXISTS StudentEgzamin CASCADE;",
    "DROP TABLE IF EXISTS StudentEdycjaKursu CASCADE;",
    "DROP TABLE IF EXISTS MaterialyEdycjaKursu CASCADE;",
    "DROP TABLE IF EXISTS StudentKompetencja CASCADE;",
    "DROP TABLE IF EXISTS EgzaminEdycjaKursu CASCADE;",
    "DROP TABLE IF EXISTS KompetencjaEgzamin CASCADE;",
    "DROP TABLE IF EXISTS KompetencjaEdycjaKursu CASCADE;",
    "DROP TABLE IF EXISTS KompetencjaCertyfikat CASCADE;",
    "DROP TABLE IF EXISTS StudentCertyfikat CASCADE;",
    "DROP TABLE IF EXISTS CertyfikatDziedzina CASCADE;",
    "DROP TABLE IF EXISTS KursDziedzina CASCADE;",
    "DROP TABLE IF EXISTS Materialy CASCADE;",
    "DROP TABLE IF EXISTS EdycjaKursu CASCADE;",
    "DROP TABLE IF EXISTS Student CASCADE;",
    "DROP TABLE IF EXISTS Nauczyciel CASCADE;",
    "DROP TABLE IF EXISTS Autor CASCADE;",
    "DROP TABLE IF EXISTS Manager CASCADE;",
    "DROP TABLE IF EXISTS Uzytkownik CASCADE;",
    "DROP TABLE IF EXISTS Kurs CASCADE;",
    "DROP TABLE IF EXISTS Edycja CASCADE;",
    "DROP TABLE IF EXISTS Egzamin CASCADE;",
    "DROP TABLE IF EXISTS Dziedzina CASCADE;",
    "DROP TABLE IF EXISTS Kompetencja CASCADE;",
    "DROP TABLE IF EXISTS Certyfikat CASCADE;"
]

conn = psycopg2.connect(dbname="usos2", user="postgres", password="haslo", host="localhost", port="5432")
cursor = conn.cursor()
for query in CLEAR_DB:
    cursor.execute(query)

for query in INIT_TABLES:
    cursor.execute(query)
conn.commit()

cursor.execute(DUMMY_DATA)
conn.commit()

conn.close()
