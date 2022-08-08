
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


# Link up flask migration
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default="False", nullable="False")
    seeking_description = db.Column(db.String(500), nullable="True")
    website = db.Column(db.String(120))
    # testing storing genres as array
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    shows = db.relationship('Show', backref="venue",
                            lazy=True, cascade="all, delete-orphan")

    @property
    def upcoming_shows(self):
        return [show for show in self.shows if show.start_time > datetime.now()]

    @property
    def past_shows(self):
        return [show for show in self.shows if show.start_time < datetime.now()]

    def __repr__(self):
        return f'Venue name is {self.name} with id {self.id}'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable="False")
    seeking_description = db.Column(db.String(500), nullable="True")
    # testing storing genres as array
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    shows = db.relationship('Show', backref="artist", lazy=True)

    @property
    def upcoming_shows(self):

        return [show for show in self.shows if show.start_time > datetime.now()]

    @property
    def past_shows(self):
        return [show for show in self.shows if show.start_time < datetime.now()]

    def __repr__(self):
        return f'Artist name is {self.name} with id {self.id}'


class Show(db.Model):
    __tableName__ = "show"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable="False")
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def __repr__(self):
        return f'Show has id {self.id} with start time {self.start_time}'
