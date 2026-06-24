from flask import Flask, render_template, request, session, redirect
from db import connection, cursor
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
app = Flask(__name__)
app.secret_key = "placementportal123"
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        query = """
        INSERT INTO students(name,email,password)
        VALUES(%s,%s,%s)
        """

        values = (name, email, hashed_password)

        cursor.execute(query, values)

        connection.commit()

        return "Registration Successful"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        query= """
        cursor.execute(
            "SELECT * FROM students WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()
        """

        values = (email, password)

        cursor.execute(query, values)

        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):

            session['student_id'] = user[0]
            session['student_name'] = user[1]

            return redirect('/dashboard')

        else:
            return "Invalid Email or Password"

    return render_template('login.html')
@app.route('/dashboard')
def dashboard():

    if 'student_id' not in session:
        return redirect('/login')

    return render_template(
        'dashboard.html',
        name=session['student_name']
    )
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')
@app.route('/test', methods=['GET','POST'])
def test():

    if 'student_id' not in session:
        return redirect('/login')

    cursor.execute("SELECT * FROM questions")

    questions = cursor.fetchall()

    if request.method == 'POST':

        score = 0

        for q in questions:

            qid = str(q[0])

            selected = request.form.get("q" + qid)

            correct = q[6]

            if selected == correct:
                score += 1

        query = """
        INSERT INTO results(student_id, score)
        VALUES(%s, %s)
        """

        values = (session['student_id'], score)

        cursor.execute(query, values)

        connection.commit()

        return f"Your Score is {score}"

    return render_template(
        'test.html',
        questions=questions
    )
@app.route('/results')
def results():

    if 'student_id' not in session:
        return redirect('/login')

    query = """
    SELECT * FROM results
    WHERE student_id=%s
    """

    cursor.execute(
        query,
        (session['student_id'],)
    )

    data = cursor.fetchall()

    return render_template(
        'results.html',
        results=data
    )
@app.route('/admin_login', methods=['GET','POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        query = """
        SELECT * FROM admins
        WHERE username=%s AND password=%s
        """

        cursor.execute(
            query,
            (username,password)
        )

        admin = cursor.fetchone()

        if admin:

            session['admin_id'] = admin[0]

            return redirect('/admin_dashboard')

        else:

            return "Invalid Admin Credentials"

    return render_template('admin_login.html')
@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin_id' not in session:
        return redirect('/admin_login')

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total Questions
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    # Total Tests
    cursor.execute("SELECT COUNT(*) FROM results")
    total_tests = cursor.fetchone()[0]

    # Highest Score
    cursor.execute("SELECT MAX(score) FROM results")
    highest_score = cursor.fetchone()[0]

    if highest_score is None:
        highest_score = 0

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_questions=total_questions,
        total_tests=total_tests,
        highest_score=highest_score
    )
@app.route('/add_question', methods=['GET', 'POST'])
def add_question():

    if 'admin_id' not in session:
        return redirect('/admin_login')

    if request.method == 'POST':

        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']

        query = """
        INSERT INTO questions
        (question, option1, option2, option3, option4, answer)
        VALUES(%s,%s,%s,%s,%s,%s)
        """

        values = (
            question,
            option1,
            option2,
            option3,
            option4,
            answer
        )

        cursor.execute(query, values)
        connection.commit()

        return "Question Added Successfully"

    return render_template('add_question.html')
@app.route('/view_questions')
def view_questions():

    if 'admin_id' not in session:
        return redirect('/admin_login')

    cursor.execute(
        "SELECT * FROM questions"
    )

    questions = cursor.fetchall()

    return render_template(
        'view_questions.html',
        questions=questions
    )
@app.route('/delete_question/<int:qid>')
def delete_question(qid):

    if 'admin_id' not in session:
        return redirect('/admin_login')

    query = """
    DELETE FROM questions
    WHERE qid=%s
    """

    cursor.execute(
        query,
        (qid,)
    )

    connection.commit()

    return redirect('/view_questions')
@app.route('/edit_question/<int:qid>', methods=['GET','POST'])
def edit_question(qid):

    if 'admin_id' not in session:
        return redirect('/admin_login')

    if request.method == 'POST':

        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']

        query = """
        UPDATE questions
        SET question=%s,
            option1=%s,
            option2=%s,
            option3=%s,
            option4=%s,
            answer=%s
        WHERE qid=%s
        """

        cursor.execute(
            query,
            (
                question,
                option1,
                option2,
                option3,
                option4,
                answer,
                qid
            )
        )

        connection.commit()

        return redirect('/view_questions')

    cursor.execute(
        "SELECT * FROM questions WHERE qid=%s",
        (qid,)
    )

    q = cursor.fetchone()

    return render_template(
        'edit_question.html',
        q=q
    )

if __name__ == '__main__':
    app.run(debug=True)