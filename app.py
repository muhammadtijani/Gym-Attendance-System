from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
db = SQLAlchemy(app)

# --- THE DATABASE MODELS ---
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tier = db.Column(db.String(20), default='Basic')
    # This "relationship" allows us to see all check-ins for a member easily
    checkins = db.relationship('Attendance', backref='member', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)

# --- THE ROUTES ---
@app.route('/')
def index():
    members = Member.query.all()
    # We also want to see the latest 5 check-ins on the dashboard
    recent_attendance = Attendance.query.order_by(Attendance.check_in_time.desc()).limit(5).all()
    return render_template('index.html', members=members, attendance=recent_attendance)

@app.route('/add_member', methods=['POST'])
def add_member():
    new_name = request.form.get('name')
    if new_name:
        db.session.add(Member(name=new_name))
        db.session.commit()
    return redirect('/')

@app.route('/checkin/<int:member_id>')
def checkin(member_id):
    # This creates a record linked to the Member's unique ID
    new_checkin = Attendance(member_id=member_id)
    db.session.add(new_checkin)
    db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)