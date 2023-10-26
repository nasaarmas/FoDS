from flask import Blueprint, render_template, redirect, url_for, flash, session
from src import db

dash_bp = Blueprint('dash', __name__, template_folder='src.templates')


@dash_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash('Musisz się zalogować, aby uzyskać dostęp do tej strony!', 'danger')
        return redirect(url_for('login.login'))
    student_competences = """
    SELECT STRING_AGG(k.nazwa, ', ') AS kompetencje
    FROM studentkompetencja s
    INNER JOIN kompetencja k ON s.idkompetencja = k.id
    WHERE s.idstudent = (SELECT id FROM Uzytkownik WHERE login = %s);"""
    student_competences = db.query(student_competences, (session['username'],))

    certificates = "SELECT certyfikatnazwa FROM studentcertyfikat WHERE idstudent = (SELECT id FROM Uzytkownik WHERE login = %s);"
    certificates = db.query(certificates, (session['username'],))

    is_student = db.query(
        "SELECT EXISTS(SELECT 1 FROM Student WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (session['username'],))[0][0]

    return render_template('dashboard.html', username=session['username'], student_competences=student_competences,
                           certs=certificates, is_student=is_student)


@dash_bp.route('/update_competences')
def update_competences():
    course_comps = """
    SELECT sek.idstudent, kompetencja.id as posiadane_kompetencje FROM studentedycjakursu sek
    INNER JOIN edycjakursu ON sek.idedycjakursu = edycjakursu.id
    INNER JOIN kompetencjaedycjakursu kek on edycjakursu.id = kek.idedycjakursu
    INNER JOIN kompetencja on kek.idkompetencja = kompetencja.id
    WHERE czyzdal = true AND sek.idstudent = (SELECT id FROM uzytkownik WHERE login = %s);"""

    for course_comp in db.query(course_comps, (session['username'],)):
        exists = "SELECT * FROM studentkompetencja WHERE idstudent = %s and idkompetencja = %s"
        if not db.query(exists, (course_comp[0], course_comp[1],)):
            db.cursor.execute("INSERT INTO studentkompetencja (idstudent, idkompetencja) VALUES (%s, %s)",
                              (course_comp[0], course_comp[1]))
            db.conn.commit()

    exam_comps = """
    SELECT se.idstudent, k.id as idkompetencja FROM studentegzamin se
    INNER JOIN egzamin ON se.egzaminnazwa = egzamin.nazwa
    INNER JOIN egzaminedycjakursu eek on egzamin.id = eek.idegzamin
    INNER JOIN kompetencjaegzamin ke ON eek.nazwa = ke.EgzaminEdycjaKursuNazwa
    INNER JOIN kompetencja k ON ke.idkompetencja = k.id
    WHERE se.czyzdal = true AND se.idstudent =  (SELECT id FROM uzytkownik WHERE login = 'jankowalski');"""

    for exam_comp in db.query(exam_comps, (session['username'],)):
        exists = "SELECT * FROM studentkompetencja WHERE idstudent = %s and idkompetencja = %s"
        if not db.query(exists, (exam_comp[0], exam_comp[1],)):
            db.cursor.execute("INSERT INTO studentkompetencja (idstudent, idkompetencja) VALUES (%s, %s)",
                              (exam_comp[0], exam_comp[1]))
            db.conn.commit()

    certificates = """
        WITH StudentKompetencje AS (
            SELECT DISTINCT sk.idkompetencja AS kompetencja_id, k.nazwa AS kompetencja_nazwa
            FROM studentkompetencja sk
            JOIN kompetencja k ON sk.idkompetencja = k.id
            WHERE sk.idstudent = (SELECT id FROM Uzytkownik WHERE login = %s)
        ),
        PotentialCertyfikaty AS (
            SELECT c.id AS certyfikat_id, c.nazwa AS certyfikat_nazwa, kc.idkompetencja
            FROM certyfikat c
            JOIN kompetencjacertyfikat kc ON c.nazwa = kc.certyfikatnazwa
        )
        SELECT pc.certyfikat_nazwa, STRING_AGG(sk.kompetencja_nazwa, ', ') AS kompetencje
        FROM PotentialCertyfikaty pc
        JOIN StudentKompetencje sk ON pc.idkompetencja = sk.kompetencja_id
        GROUP BY pc.certyfikat_nazwa
        HAVING COUNT(DISTINCT pc.idkompetencja) =
            (SELECT COUNT(DISTINCT idkompetencja) FROM kompetencjacertyfikat kc WHERE kc.certyfikatnazwa = pc.certyfikat_nazwa);"""

    certificates = db.query(certificates, (session['username'],))
    for cert in certificates:
        exists = "SELECT * FROM studentcertyfikat WHERE idstudent = (SELECT id FROM Uzytkownik WHERE login = %s) and certyfikatnazwa = %s"
        if not db.query(exists, (session['username'], cert[0],)):
            db.cursor.execute(
                "INSERT INTO studentcertyfikat (idstudent, certyfikatnazwa) VALUES ((SELECT id FROM Uzytkownik WHERE login = %s), %s)",
                (session['username'], cert[0]))
            db.conn.commit()
    return redirect(url_for('dash.dashboard'))
