from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    web_link = db.Column(db.String(500), nullable=True)
    look_for_talent = db.Column(db.Boolean, nullable=False, default=False)
    seek_description = db.Column(db.String(500), nullable=True)
    genres = db.Column(db.String(120), nullable=True)

    artists = db.relationship('Artist', secondary='Show')
    shows = db.relationship('Show', backref=('Venue'))

    def num_upcoming_shows(self):
        return self.query.join(Show).filter_by(venue_id=self.id).filter(
            Show.start_time > datetime.now()).count()

    def num_past_shows(self):
        return self.query.join(Show).filter_by(venue_id=self.id).filter(
            Show.start_time < datetime.now()).count()

    def past_shows(self):
        return Show.get_past_by_artist(self.id)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    web_link = db.Column(db.String(), nullable=True)
    look_for_venue = db.Column(db.Boolean, nullable=False, default=False)
    seek_description = db.Column(db.String(), nullable=True)
    genres = db.Column(db.String(120), nullable=False)

    venues = db.relationship('Venue', secondary='Show')
    shows = db.relationship('Show', backref=('Artist'))

    def num_upcoming_shows(self):
        return self.query.join(Show).filter_by(artist_id=self.id).filter(
            Show.start_time > datetime.now()).count()

    def num_past_shows(self):
        return self.query.join(Show).filter_by(artist_id=self.id).filter(
            Show.start_time < datetime.now()).count()

    def past_shows(self):
        return Show.get_past_by_artist(self.id)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    venue = db.relationship('Venue')
    artist = db.relationship('Artist')

    def get_past_by_venue(cls, venue_id):
        shows = cls.query.filter_by(venue_id=venue_id).filter(
            cls.start_time < datetime.now()).all()
        return [show.show_details for show in shows]

    def get_upcoming_by_venue(cls, venue_id):
        shows = cls.query.filter_by(venue_id=venue_id).filter(
            cls.start_time > datetime.now()).all()
        return [show.show_details for show in shows]

    @classmethod
    def get_past_by_artist(cls, artist_id):
        shows = cls.query.filter_by(artist_id=artist_id).filter(
            cls.start_time < datetime.now()).all()
        return [show.show_details for show in shows]
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


# db.create_all()
