from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src import db

admin_bp = Blueprint('admin', __name__, template_folder='src.templates')


@admin_bp.route('/admin')
def admin():
    if not session.get('logged_in'):
        flash('Musisz się zalogować, aby uzyskać dostęp do tej strony!', 'danger')
        return redirect(url_for('login.login'))
    is_admin = db.query(
        "SELECT czyAdmin FROM Uzytkownik WHERE login = %s", (session['username'],))[0][0]
    if not is_admin:
        flash('Nie masz uprawnień do dostępu do tej strony!', 'danger')
        return redirect(url_for('dash.dashboard'))

    users = """
    SELECT U.login,
       U.czyAdmin,
       STRING_AGG(DISTINCT group_name, ', ') AS groups
    FROM Uzytkownik U
    LEFT JOIN (
        SELECT idUzytkownik, 'Student' AS group_name FROM Student
        UNION ALL
        SELECT idUzytkownik, 'Nauczyciel' FROM Nauczyciel
        UNION ALL
        SELECT idUzytkownik, 'Autor' FROM Autor
        UNION ALL
        SELECT idUzytkownik, 'Manager' FROM Manager
    ) AS Groups ON U.id = Groups.idUzytkownik
    GROUP BY U.id, U.login, U.czyAdmin;"""
    users = db.query(users)
    return render_template('admin.html', users=users)


@admin_bp.route('/update_groups', methods=['POST'])
def update_groups():
    if not session.get('logged_in'):
        flash('Musisz się zalogować, aby uzyskać dostęp do tej strony!', 'danger')
        return redirect(url_for('login.login'))

    is_admin = db.query(
        "SELECT czyAdmin FROM Uzytkownik WHERE login = %s", (session['username'],))[0][0]
    if not is_admin:
        flash('Nie masz uprawnień do dostępu do tej strony!', 'danger')
        return redirect(url_for('dash.dashboard'))

    for user in db.query("SELECT login FROM Uzytkownik"):
        username = user[0]
        user_id = db.query(
            "SELECT id FROM Uzytkownik WHERE login = %s", (username,))[0][0]
        for group in ["Student", "Nauczyciel", "Autor", "Manager"]:
            checkbox_name = f"{username}_{group}"
            if request.form.get(checkbox_name):
                exists = db.query(
                    f"SELECT 1 FROM {group} WHERE idUzytkownik = %s", (user_id,))
                if not exists:
                    db.cursor.execute(
                        f"INSERT INTO {group} (idUzytkownik) VALUES (%s)", (user_id,))

            else:
                exists = db.query(
                    f"SELECT 1 FROM {group} WHERE idUzytkownik = %s", (user_id,))
                if exists:
                    db.cursor.execute(
                        f"DELETE FROM {group} WHERE idUzytkownik = %s", (user_id,))

        checkbox_name = f"{user[0]}_czyAdmin"
        if request.form.get(checkbox_name):
            exists = db.query("SELECT 1 FROM uzytkownik WHERE id = %s AND czyAdmin = true;", (user_id,))
            if not exists:
                db.cursor.execute("UPDATE Uzytkownik SET czyAdmin = True WHERE id = %s", (user_id,))
        else:
            exists = db.query("SELECT 1 FROM uzytkownik WHERE id = %s AND czyAdmin = true;", (user_id,))
            if exists:
                db.cursor.execute("UPDATE Uzytkownik SET czyAdmin = False WHERE id = %s", (user_id,))
    db.conn.commit()

    flash('Grupy zostały zaktualizowane!', 'success')
    return redirect(url_for('admin.admin'))
