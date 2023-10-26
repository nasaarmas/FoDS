from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src import db

courses_bp = Blueprint('courses', __name__, template_folder='src.templates')


@courses_bp.route('/courses')
def browse_courses():
    if not session.get('logged_in'):
        flash('You have to login to access this site!', 'danger')
        return redirect(url_for('login.login'))
    is_student = db.query(
        "SELECT EXISTS(SELECT 1 FROM Student WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (session['username'],))[0][0]
    if not is_student:
        flash('You don\'t have enough permissions to view this site!', 'danger')
        return redirect(url_for('dash.dashboard'))

    courses = db.query("""
    SELECT ek.id, ek.nazwakursu, ek.semestredycji, kd.dziedzinanazwa, e.nazwa AS egzamin_nazwa
    FROM EdycjaKursu ek
    LEFT JOIN egzaminedycjakursu edk ON ek.id = edk.idedycjakursu
    LEFT JOIN egzamin e ON edk.idegzamin = e.id
    LEFT JOIN kursdziedzina kd ON kd.nazwakursu = ek.nazwakursu;""")

    course_id = """
    SELECT idstudent, string_agg(idedycjakursu::TEXT, ',') AS idedycjakursu
    FROM studentedycjakursu WHERE idstudent = (SELECT id from uzytkownik WHERE login=%s)
    GROUP BY idstudent;"""

    course_id = db.query(course_id, (session['username'],))
    if not course_id:
        course_id = [['0', '0']]

    signed_exams = db.query("""SELECT DISTINCT STRING_AGG(egzaminnazwa, ',') AS egzaminnazwa_list
    FROM studentegzamin
    WHERE idstudent = (SELECT id from uzytkownik WHERE login=%s)
    GROUP BY idstudent;""", (session['username'],))
    if not signed_exams:
        signed_exams = [['0', '0']]

    return render_template('signs_up.html', courses=courses, course_id=course_id, signed_exams=signed_exams)


@courses_bp.route('/courses/sign_up_courses', methods=['POST'])
def sign_up_courses():
    if not session.get('logged_in'):
        flash('You have to login to access this site!', 'danger')
        return redirect(url_for('login.login'))

    student_id = db.query(
        "SELECT id FROM Uzytkownik WHERE login = %s", (session['username'],))

    kursy = """
        SELECT ek.id, ek.nazwakursu AS kurs_nazwa, ek.semestredycji, e.nazwa AS egzamin_nazwa
        FROM EdycjaKursu ek
        LEFT JOIN egzaminedycjakursu edk ON ek.id = edk.idedycjakursu
        LEFT JOIN egzamin e ON edk.idegzamin = e.id;"""

    for course in db.query(kursy):
        radiobox_name = f"{course[0]}_{course[2]}_choice"
        query = "SELECT id FROM studentedycjakursu WHERE idedycjakursu = %s AND idstudent = %s;"
        exists = db.query(query, (course[0], student_id[0][0],))

        if request.form.get(radiobox_name) == '1':
            if not exists:
                db.cursor.execute(f"INSERT INTO studentedycjakursu (idstudent, idedycjakursu) VALUES (%s, %s)",
                                  (student_id[0][0], course[0],))
        else:
            if exists:
                db.cursor.execute(f"DELETE FROM studentedycjakursu WHERE idstudent = %s AND idedycjakursu = %s;",
                                  (student_id[0][0], course[0],))
        checkbox_name = f"{course[0]}_{course[3]}_egz"

        czy_zapisany = "SELECT id FROM studentegzamin WHERE egzaminnazwa = %s AND idstudent = %s;"
        czy_zapisany = db.query(czy_zapisany, (course[3], student_id[0][0],))
        if request.form.get(checkbox_name):
            if not czy_zapisany:
                db.cursor.execute(
                    "INSERT INTO studentegzamin (idstudent, egzaminnazwa, czyzdal) VALUES (%s, %s, false)",
                    (student_id[0][0], course[3],))
        else:
            if czy_zapisany:
                db.cursor.execute(
                    "DELETE FROM studentegzamin WHERE idstudent = %s AND egzaminnazwa = %s",
                    (student_id[0][0], course[3],))

    db.conn.commit()

    flash('Groups got updated successfully!', 'success')
    return redirect(url_for('courses.browse_courses'))
