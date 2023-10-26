from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src import db

author_bp = Blueprint('author', __name__, template_folder='src.templates')


@author_bp.route('/author', methods=['GET'])
def author():
    username = session['username']
    is_author = db.query(
        "SELECT EXISTS(SELECT 1 FROM Autor WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (username,))[0][0]
    if not is_author:
        flash('You don\'t have enough permissions to view this site!', 'danger')
        return redirect(url_for('dash.dashboard'))

    courses = [row[0] for row in db.query("SELECT Nazwa FROM Kurs")]
    editions = [row[0] for row in db.query("SELECT Semestr FROM Edycja")]
    competences = [row[0] for row in db.query("SELECT Nazwa FROM Kompetencja")]
    courses_edition = [row[0]
                       for row in db.query("SELECT Nazwa FROM EdycjaKursu")]
    courses_edition_competences = db.query("""
    SELECT EdycjaKursu.Nazwa AS EdycjaKursu_Nazwa,
        ARRAY_AGG(DISTINCT Kompetencja.Nazwa) AS Kompetencje,
        ARRAY_AGG(DISTINCT dziedzina.nazwa) AS Dziedzina
    FROM EdycjaKursu
    LEFT JOIN KompetencjaEdycjaKursu ON EdycjaKursu.id = KompetencjaEdycjaKursu.idEdycjaKursu
    LEFT JOIN Kompetencja ON KompetencjaEdycjaKursu.idKompetencja = Kompetencja.id
    LEFT JOIN kursdziedzina ON EdycjaKursu.nazwakursu = kursdziedzina.nazwakursu
    LEFT JOIN dziedzina ON kursdziedzina.dziedzinanazwa = dziedzina.nazwa
    GROUP BY EdycjaKursu.Nazwa;""")
    fields = [row[0] for row in db.query("SELECT Nazwa FROM Dziedzina")]
    exams = [row[0] for row in db.query("SELECT Nazwa FROM Egzamin")]
    exams_course_edition = [row[0] for row in db.query(
        "SELECT Nazwa FROM EgzaminEdycjaKursu")]

    exam_editions_competences = db.query("""
        SELECT EgzaminEdycjaKursu.Nazwa AS EgzaminEdycjaKursu_Nazwa,
            ARRAY_AGG(DISTINCT Kompetencja.Nazwa) AS Kompetencje
        FROM EgzaminEdycjaKursu
        LEFT JOIN KompetencjaEgzamin ON EgzaminEdycjaKursu.Nazwa = KompetencjaEgzamin.EgzaminEdycjaKursuNazwa
        LEFT JOIN Kompetencja ON KompetencjaEgzamin.idKompetencja = Kompetencja.id
        LEFT JOIN EdycjaKursu ON EgzaminEdycjaKursu.idEdycjaKursu = EdycjaKursu.id
        GROUP BY EgzaminEdycjaKursu.Nazwa;
    """)

    students_enrolled_on_your_course = db.query("""
        SELECT Uzytkownik.imie, Uzytkownik.nazwisko, EdycjaKursu.Nazwa, StudentEdycjaKursu.czyZdal
        FROM Uzytkownik
        INNER JOIN Student ON Uzytkownik.id = Student.idUzytkownik
        INNER JOIN StudentEdycjaKursu ON Student.id = StudentEdycjaKursu.idStudent
        INNER JOIN EdycjaKursu ON StudentEdycjaKursu.idEdycjaKursu = EdycjaKursu.id
    """)
    students_enrolled_on_your_exam = db.query("""
        SELECT Uzytkownik.imie, Uzytkownik.nazwisko, EdycjaKursu.Nazwa as kurs, Egzamin.nazwa as egzamin, StudentEgzamin.czyZdal
        FROM Uzytkownik
        INNER JOIN Student ON Uzytkownik.id = Student.idUzytkownik
        INNER JOIN StudentEgzamin ON Student.id = StudentEgzamin.idStudent
        INNER JOIN Egzamin ON StudentEgzamin.EgzaminNazwa = Egzamin.Nazwa
        INNER JOIN EgzaminEdycjaKursu ON Egzamin.id = EgzaminEdycjaKursu.idEgzamin
        INNER JOIN EdycjaKursu ON EgzaminEdycjaKursu.idedycjakursu = EdycjaKursu.id
        GROUP BY EdycjaKursu.Nazwa, Egzamin.nazwa, Uzytkownik.nazwisko, Uzytkownik.imie, StudentEgzamin.czyZdal;
    """)
    return render_template('author.html', courses=courses, editions=editions, competences=competences,
                           courses_edition=courses_edition, courses_edition_competences=courses_edition_competences,
                           fields=fields, exams=exams, exam_editions=exams_course_edition,
                           exam_edition_competences=exam_editions_competences,
                           students_courses=students_enrolled_on_your_course,
                           students_exams=students_enrolled_on_your_exam)


@author_bp.route('/create_course', methods=['POST'])
def create_course():
    username = session['username']
    is_author = db.query(
        "SELECT EXISTS(SELECT 1 FROM Autor WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (username,))[0][0]
    if not is_author:
        flash('You don\'t have enough permissions to view this site!', 'danger')
        return redirect(url_for('dash.dashboard'))

    course_name = request.form.get('course_name')
    db.cursor.execute("INSERT INTO Kurs (Nazwa) VALUES (%s)", (course_name,))
    db.conn.commit()
    flash('Course created successfully!', 'success')
    return redirect(url_for('author.author'))


@author_bp.route('/create_course_edition', methods=['POST'])
def create_course_edition():
    username = session['username']
    is_author = db.query(
        "SELECT EXISTS(SELECT 1 FROM Autor WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (username,))[0][0]
    if not is_author:
        flash('You don\'t have enough permissions to view this site!', 'danger')
        return redirect(url_for('dash.dashboard'))

    course_name = request.form.get('course_name')
    edition_name = request.form.get('edition_name')

    db.cursor.execute(
        "INSERT INTO EdycjaKursu (Nazwa, NazwaKursu, SemestrEdycji) VALUES (%s, %s, %s)",
        (f"{course_name}_{edition_name}", course_name, edition_name,))
    db.conn.commit()
    flash('Course edition created successfully!', 'success')
    return redirect(url_for('author.author'))


@author_bp.route('/assign_competence_to_course_edition', methods=['POST'])
def assign_comptenece_to_course_edition():
    username = session['username']
    is_author = db.query(
        "SELECT EXISTS(SELECT 1 FROM Autor WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (username,))[0][0]
    if not is_author:
        flash('You don\'t have enough permissions to view this site!', 'danger')
        return redirect(url_for('dash.dashboard'))

    course_edition_name = request.form.get('course_edition_name')
    competences = request.form.getlist('competences')
    for competence in competences:
        db.cursor.execute(
            "INSERT INTO KompetencjaEdycjaKursu (idKompetencja, idEdycjaKursu) VALUES ((SELECT id FROM Kompetencja WHERE Nazwa = %s), (SELECT id FROM EdycjaKursu WHERE Nazwa = %s))",
            (competence, course_edition_name,))
        db.conn.commit()
    flash('Competences assigned successfully!', 'success')
    return redirect(url_for('author.author'))


@author_bp.route('/create_field', methods=['POST'])
def create_field():
    field_name = request.form.get('field_name')
    db.cursor.execute(
        "INSERT INTO Dziedzina (Nazwa, idTworca) VALUES (%s, (SELECT id FROM Uzytkownik WHERE login = %s))",
        (field_name, session['username']))
    db.conn.commit()
    flash('Competence created successfully!', 'success')
    return redirect(url_for('author.author'))


@author_bp.route('/assign_field_to_course', methods=['POST'])
def assign_field_to_course():
    course_name = request.form.get('course_name')
    field_name = request.form.get('field_name')
    db.cursor.execute("INSERT INTO kursdziedzina (nazwakursu, DziedzinaNazwa) VALUES (%s, %s)",
                      (course_name, field_name))

    db.conn.commit()
    flash('Field assigned successfully!', 'success')
    return redirect(url_for('author.author'))


@author_bp.route('/create_exam', methods=['POST'])
def create_exam():
    username = session['username']
    is_author = db.query(
        "SELECT EXISTS(SELECT 1 FROM Autor WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (username,))[0][0]
    if not is_author:
        flash('You don\'t have enough permissions to view this site!', 'danger')
        return redirect(url_for('dash.dashboard'))

    exam_name = request.form.get('exam_name')
    db.cursor.execute(
        "INSERT INTO Egzamin (Nazwa, Autor) VALUES (%s, %s)", (exam_name, username))
    db.conn.commit()
    flash('Examin created successfully!', 'success')
    return redirect(url_for('author.author'))


@author_bp.route('/assign_exam_to_course_edition', methods=['POST'])
def assign_exam_to_course_edition():
    username = session['username']
    is_author = db.query(
        "SELECT EXISTS(SELECT 1 FROM Autor WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (username,))[0][0]
    if not is_author:
        flash('You don\'t have enough permissions to view this site!', 'danger')
        return redirect(url_for('dash.dashboard'))

    course_edition_name = request.form.get('course_edition_name')
    exam_name = request.form.get('exam_name')
    exam_course_edition_name = f"{exam_name}_{course_edition_name}"
    db.cursor.execute(
        "INSERT INTO EgzaminEdycjaKursu (Nazwa, idEgzamin, idEdycjaKursu) VALUES (%s, (SELECT id FROM Egzamin WHERE Nazwa = %s), (SELECT id FROM EdycjaKursu WHERE Nazwa = %s))",
        (exam_course_edition_name, exam_name, course_edition_name,))
    db.conn.commit()
    flash('Examin assigned successfully!', 'success')
    return redirect(url_for('author.author'))


@author_bp.route('/assign_competences_to_exam_edition', methods=['POST'])
def assign_competences_to_exam_edition():
    username = session['username']
    is_author = db.query(
        "SELECT EXISTS(SELECT 1 FROM Autor WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (username,))[0][0]
    if not is_author:
        flash('You don\'t have enough permissions to view this site!', 'danger')
        return redirect(url_for('dash.dashboard'))

    exam_edition_name = request.form.get('exam_edition_name')
    competences = request.form.getlist('competences')
    for competence in competences:
        print(exam_edition_name, competences)
        db.cursor.execute(
            "INSERT INTO KompetencjaEgzamin (idKompetencja, EgzaminEdycjaKursuNazwa) VALUES ((SELECT id FROM Kompetencja WHERE Nazwa = %s), %s)",
            (competence, exam_edition_name,))
        db.conn.commit()
    flash('Competences assigned successfully!', 'success')
    return redirect(url_for('author.author'))


@author_bp.route('/student_passed_course', methods=['POST'])
def student_passed_course():
    students_and_courses = request.form
    for student, score in students_and_courses.items():
        student_name, student_surname, course_edition_name = student.split('-')
        db.cursor.execute(
            "UPDATE StudentEdycjaKursu SET czyZdal = %s WHERE idStudent = (SELECT id FROM Uzytkownik WHERE imie = %s AND nazwisko = %s) AND idEdycjaKursu = (SELECT id FROM EdycjaKursu WHERE Nazwa = %s)",
            (score, student_name, student_surname, course_edition_name,))
        db.conn.commit()
    return redirect(url_for('author.author'))


@author_bp.route('/student_passed_exam', methods=['POST'])
def student_passed_exam():
    students_and_exams = request.form
    for student, score in students_and_exams.items():
        exam_prefix, student_name, student_surname, exam_name = student.split('-')
        print(student)
        if exam_prefix == "exam":
            print(exam_prefix, student_name, student_surname, exam_name)
            db.cursor.execute(
                """UPDATE StudentEgzamin SET czyZdal = %s 
                WHERE idStudent = (SELECT id FROM Uzytkownik WHERE imie = %s AND nazwisko = %s) 
                AND EgzaminNazwa = %s""""", (score, student_name, student_surname, exam_name))
            db.conn.commit()

    return redirect(url_for('author.author'))
