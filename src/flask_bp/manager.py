from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src import db

manager_bp = Blueprint('manager', __name__, template_folder='src.templates')


@manager_bp.route('/manager', methods=['GET'])
def manager():
    username = session['username']

    is_manager = db.query(
        "SELECT EXISTS(SELECT 1 FROM Manager WHERE idUzytkownik = (SELECT id FROM Uzytkownik WHERE login = %s))",
        (username,))[0][0]

    if not is_manager:
        flash('You don\'t have permission to view this site!', 'danger')
        return redirect(url_for('dash.dashboard'))

    certificate_competences = db.query("""
    SELECT Certyfikat.Nazwa AS Certyfikat_Nazwa,
        ARRAY_AGG(DISTINCT Kompetencja.Nazwa) AS Kompetencje,
        ARRAY_AGG(DISTINCT certyfikatdziedzina.dziedzinanazwa) AS Dziedziny
    FROM Certyfikat
    LEFT JOIN KompetencjaCertyfikat ON Certyfikat.Nazwa = KompetencjaCertyfikat.CertyfikatNazwa
    LEFT JOIN Kompetencja ON KompetencjaCertyfikat.idKompetencja = Kompetencja.id
    LEFT JOIN certyfikatdziedzina ON Certyfikat.Nazwa = certyfikatdziedzina.certyfikatnazwa
    GROUP BY Certyfikat.Nazwa;
    """)

    certificates = [row[0] for row in db.query("SELECT Nazwa FROM Certyfikat")]
    competences = [row[0] for row in db.query("SELECT Nazwa FROM Kompetencja")]
    fields = [row[0] for row in db.query("SELECT Nazwa FROM Dziedzina")]

    return render_template('manager.html', certificates=certificates, competences=competences,
                           certificate_competences=certificate_competences, fields=fields)


@manager_bp.route('/create_certificate', methods=['POST'])
def create_certificate():
    certificate_name = request.form.get('certificate_name')
    db.cursor.execute(
        "INSERT INTO Certyfikat (Nazwa, idManager) VALUES (%s, (SELECT id FROM Uzytkownik WHERE login = %s))",
        (certificate_name, session['username']))

    db.conn.commit()
    flash('Certificate created successfully!', 'success')
    return redirect(url_for('manager.manager'))


@manager_bp.route('/assign_competence_to_certificate', methods=['POST'])
def assign_competence_to_certificate():
    certificate_name = request.form.get('certificate_name')
    competence_name = request.form.get('competence_name')

    db.cursor.execute(
        "INSERT INTO KompetencjaCertyfikat (idKompetencja, CertyfikatNazwa) VALUES ((SELECT id FROM Kompetencja WHERE Nazwa = %s), %s)",
        (competence_name, certificate_name))

    db.conn.commit()
    flash('Competence assigned successfully!', 'success')
    return redirect(url_for('manager.manager'))


@manager_bp.route('/create_competence', methods=['POST'])
def create_competence():
    competence_name = request.form.get('competence_name')
    db.cursor.execute(
        "INSERT INTO Kompetencja (Nazwa, idmanager) VALUES (%s, (SELECT id FROM Uzytkownik WHERE login = %s))",
        (competence_name, session['username']))
    db.conn.commit()
    flash('Competence created successfully!', 'success')
    return redirect(url_for('manager.manager'))


@manager_bp.route('/create_field', methods=['POST'])
def create_field():
    field_name = request.form.get('field_name')
    db.cursor.execute(
        "INSERT INTO Dziedzina (Nazwa, idTworca) VALUES (%s, (SELECT id FROM Uzytkownik WHERE login = %s))",
        (field_name, session['username']))
    db.conn.commit()
    flash('Field created successfully!', 'success')
    return redirect(url_for('manager.manager'))


@manager_bp.route('/assign_field_to_certificate', methods=['POST'])
def assign_field_to_certificate():
    certificate_name = request.form.get('certificate_name')
    field_name = request.form.get('field_name')

    db.cursor.execute("INSERT INTO certyfikatdziedzina (CertyfikatNazwa, DziedzinaNazwa) VALUES (%s, %s)",
                      (certificate_name, field_name))

    db.conn.commit()
    flash('Field assigned successfully!', 'success')
    return redirect(url_for('manager.manager'))
