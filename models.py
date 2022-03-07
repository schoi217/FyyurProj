from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(250))
    genres = db.Column(db.ARRAY(db.String(120)))
    shows = db.relationship('Show', cascade="all, delete",
                            passive_deletes=True, lazy='joined',
                            backref='venue')

    @property
    def upcoming_shows(self):
        upcoming = []
        for show in self.shows:
            if show.start_time > datetime.now():
                upcoming.append(show)
        return upcoming

    @property
    def upcoming_shows_count(self):
        upcoming_shows_count = len(self.upcoming_shows)
        return upcoming_shows_count

    @property
    def past_shows(self):
        past_shows = []
        for show in self.shows:
            if show.start_time < datetime.now():
                past_shows.append(show)
        return past_shows

    @property
    def past_shows_count(self):
        return len(self.past_shows)


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Show', cascade="all, delete",
                            passive_deletes=True, lazy='joined',
                            backref='artist')

    @property
    def upcoming_shows(self):
        upcoming = []
        for show in self.shows:
            if show.start_time > datetime.now():
                upcoming.append(show)
        return upcoming

    @property
    def upcoming_shows_count(self):
        upcoming_shows_count = len(self.upcoming_shows)
        return upcoming_shows_count

    @property
    def past_shows(self):
        past_shows = []
        for show in self.shows:
            if show.start_time < datetime.now():
                past_shows.append(show)
        return past_shows

    @property
    def past_shows_count(self):
        return len(self.past_shows)


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete="CASCADE"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete="CASCADE"), nullable=False)
