from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src import db
import ast
import re

teacher_bp = Blueprint('teacher', __name__, template_folder='src.templates')


@teacher_bp.route('/teacher', methods=['GET'])
def teacher():
    materials_authors = db.query("SELECT Nazwa, Autor FROM Materialy")
    courses = db.query("SELECT Nazwa FROM EdycjaKursu")
    course_edition_materials = db.query("""
        SELECT EdycjaKursu.Nazwa,
            ARRAY_AGG(Materialy.Autor),
            ARRAY_AGG(Materialy.Nazwa)
        FROM EdycjaKursu
        INNER JOIN MaterialyEdycjaKursu ON EdycjaKursu.id = MaterialyEdycjaKursu.idEdycjaKursu
        INNER JOIN Materialy ON Materialy.id = MaterialyEdycjaKursu.idMaterialy
        GROUP BY EdycjaKursu.Nazwa;
    """)
    return render_template('teacher.html', materials_authors=materials_authors, courses=courses, courses_materials=course_edition_materials)

@teacher_bp.route('/create_material', methods=['POST'])
def create_material():
    material_name = request.form.get('material_name')
    material_author = request.form.get('material_author')
    username = session['username']

    db.cursor.execute(
        "INSERT INTO Materialy (Autor, Nazwa, idNauczyciel) VALUES (%s, %s, (SELECT id FROM Uzytkownik WHERE login = %s))",
        (material_author, material_name, username))
    db.conn.commit()

    flash('Material created successfully!', 'success')
    return redirect(url_for('teacher.teacher'))

@teacher_bp.route('/assign_material', methods=['POST'])
def assign_material_to_course_edition():
    course_edition_name = ast.literal_eval(request.form.get('course_edition_name'))
    materials_authors = request.form.getlist('material_author')
    for material_author_str in materials_authors:
        material_name, material_author = ast.literal_eval(material_author_str)
        db.cursor.execute(
            """INSERT INTO MaterialyEdycjaKursu (idEdycjaKursu, idMaterialy)
            SELECT e.id, m.id FROM EdycjaKursu e, Materialy m
            WHERE e.Nazwa = %s AND m.Nazwa = %s AND m.Autor = %s
            AND NOT EXISTS (
                SELECT 1 FROM MaterialyEdycjaKursu mek
                WHERE mek.idEdycjaKursu = e.id AND mek.idMaterialy = m.id
            )""",
            (course_edition_name, material_name, material_author))
    db.conn.commit()

    flash('Material assigned successfully!', 'success')
    return redirect(url_for('teacher.teacher'))