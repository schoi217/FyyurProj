#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
                            passive_deletes=True, lazy=True)

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
    shows = db.relationship('Show', cascade="all, delete", passive_deletes=True, lazy=True)

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    #Query all the venues
    venues = Venue.query.all()

    #create a list for the data and a set for cities and states
    datas = list()
    cities_states = set()

    #iterate through the venue, create a set of city/state so no duplicates
    #add to cities_states
    for venue in venues:
        city = venue.city
        state = venue.state
        city_state = (city, state)
        cities_states.add(city_state)

    #make it iterable
    cities_states = list(cities_states)
    #go through all locations and create list of dictionary
    for location in cities_states:
        venue_info = []
        for venue in venues:
            if (venue.city == location[0]) & (venue.state == location[1]):
                venue_dict = {'id': venue.id, 'name': venue.name}
                venue_info.append(venue_dict)

        #add the new city, state, and list of venues to venues key
        datas.append({'city': location[0], 'state': location[1],
                      'venues': venue_info})

    return render_template('pages/venues.html', areas=datas);

@app.route('/venues/search', methods=['POST'])
def search_venues():

    #Get the search term that the user inputs
    search_term = request.form.get('search_term', '')

    #get a list of the venues that contain the search term
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    data = []
    #go through each venue and create a dictionary of the id and name
    for venue in venues:
        id = venue.id
        name = venue.name
        data.append({'id': id, 'name': name})
    #count the list of venues
    count = len(venues)
    responses = {'data':data, 'count': count}


    return render_template('pages/search_venues.html',
        results=responses, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    #query the venue with the right id
    venue = Venue.query.filter(Venue.id == venue_id).first()
    #with proper query, serialize the data
    if venue:
        datas={
        'id': venue.id,
        'name': venue.name,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone': venue.phone,
        'image_link': venue.image_link,
        'facebook_link': venue.facebook_link,
        'website': venue.website,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'genres': venue.genres,
        'past_shows_count': venue.past_shows_count,
        'upcoming_shows_count': venue.upcoming_shows_count
        }

    upcoming_shows = []
    past_shows = []
    #serialie the past shows and add the show info to the list
    for show in venue.past_shows:
        artist_info = Artist.query.get(show.artist_id)
        show_dict = {
            'artist_id': show.artist_id,
            'artist_name': artist_info.name,
            'artist_image_link': artist_info.image_link,
            'start_time': show.start_time
            }
        past_shows.append(show_dict)
    #serialize the upcoming shows and add the show info to the list
    for show in venue.upcoming_shows:
        artist_info = Artist.query.get(show.artist_id)
        show_dict = {
            'artist_id': show.artist_id,
            'artist_name': artist_info.name,
            'artist_image_link': artist_info.image_link,
            'start_time': show.start_time
            }
        upcoming_shows.append(show_dict)
    #add the list of upcoming/past shows into the dataset
    datas['upcoming_shows'] = upcoming_shows
    datas['past_shows'] = past_shows

    return render_template('pages/show_venue.html', venue=datas)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm(request.form)
    new_venue = Venue(
        name=form.name.data,
        phone=form.phone.data,
        state=form.state.data,
        address=form.address.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        city=form.city.data,
        website=form.website_link.data,
        genres=form.genres.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data)
    try:
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('Venue ' + request.form['name'] + " couldn't successfully listed!")
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.filter(Venue.id == venue_id).first()
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

    artists = Artist.query.all()

    data = []
    #Parse through artists, adding in an individual dict with artist info
    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    #retrieve the search information from the form
    search_term = request.form.get('search_term', '')

    #case insensitive filter search on the search query
    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

    #dictionary for the data to be passed through
    response = {
      'count': len(artists)
    }
    data = []
    #parse through artists and add individual artist info into a dictionary
    for artist in artists:
        data.append({
          'id': artist.id,
          'name': artist.name,
        })
    response['data'] = data

    return render_template('pages/search_artists.html',
            results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    #query the artist with the appropriate id
    artist = Artist.query.filter(Artist.id == artist_id).first()
    #with proper query, serialize the data
    if artist:
        data={
        'id': artist.id,
        'name': artist.name,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,

        }



    data1={
      "id": 4,
      "name": "Guns N Petals",
      "genres": ["Rock n Roll"],
      "city": "San Francisco",
      "state": "CA",
      "phone": "326-123-5000",
      "website": "https://www.gunsnpetalsband.com",
      "facebook_link": "https://www.facebook.com/GunsNPetals",
      "seeking_venue": True,
      "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
      "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "past_shows": [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "start_time": "2019-05-21T21:30:00.000Z"
      }],
      "upcoming_shows": [],
      "past_shows_count": 1,
      "upcoming_shows_count": 0,
    }
    data2={
      "id": 5,
      "name": "Matt Quevedo",
      "genres": ["Jazz"],
      "city": "New York",
      "state": "NY",
      "phone": "300-400-5000",
      "facebook_link": "https://www.facebook.com/mattquevedo923251523",
      "seeking_venue": False,
      "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "past_shows": [{
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
      }],
      "upcoming_shows": [],
      "past_shows_count": 1,
      "upcoming_shows_count": 0,
    }
    data3={
      "id": 6,
      "name": "The Wild Sax Band",
      "genres": ["Jazz", "Classical"],
      "city": "San Francisco",
      "state": "CA",
      "phone": "432-325-5432",
      "seeking_venue": False,
      "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "past_shows": [],
      "upcoming_shows": [{
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
      }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
      }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
      }],
      "past_shows_count": 0,
      "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    update_venue = Venue.query.filter(Venue.id == venue_id).first()
    update_venue.name=form.name.data
    update_venue.phone=form.phone.data
    update_venue.state=form.state.data
    update_venue.address=form.address.data
    update_venue.image_link=form.image_link.data
    update_venue.facebook_link=form.facebook_link.data
    update_venue.city=form.city.data
    update_venue.website=form.website_link.data
    update_venue.genres=form.genres.data
    update_venue.seeking_talent=form.seeking_talent.data
    update_venue.seeking_description=form.seeking_description.data
    db.session.commit()
    db.session.close()


    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
