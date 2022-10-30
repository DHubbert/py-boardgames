import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import UUID

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://DHubbert:v2_3v23f_Vn2GL8HQscmQmLHQdHFMRzA@db.bit.io/DHubbert/BoardGames"
db.init_app(app)

class game(db.Model):
	game_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('owner.owner_id'))
	name = db.Column(db.String, nullable=False)
	reference = db.Column(db.String)
	duration_upper = db.Column(db.Integer)
	duration_lower = db.Column(db.Integer)
	min_players = db.Column(db.Integer)
	max_players = db.Column(db.Integer)
	thumbnail = db.Column(db.String)
	image = db.Column(db.String)
	description = db.Column(db.String)

class owner(db.Model):
    owner_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    owner = db.relationship("game", backref="owner")

    def __repr__(self):
        return '<Owner: {}>'.format(self.games)


@app.route("/")
@app.route("/index")
def index():
#	games = db.session.query(game, owner).filter(game.owner_id == owner.owner_id).all()
	owners = db.session.query(owner).all()
	games = db.session.query(game).all()
	return render_template("index.html", games=games, owners=owners)

@app.route("/game-by-id/<uuid:id>")
def user_by_id(id):
    game = db.get_or_404(game, id)
    return render_template("show_game.html", game=game)

@app.route("/owner-by-id/<uuid:id>")
def owner_by_id(id):
    owner = db.one_or_404(owner, id)
    return render_template("show_owner.html", owner=owner)

if __name__ == '__main__':
	app.run(debug=True)