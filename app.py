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
        flash('Venue ' + venue.name + ' was successfully deleted!')
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


@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.filter(Artist.id == artist_id).first()
        db.session.delete(artist)
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully deleted!')
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

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
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows_count': artist.past_shows_count,
        'upcoming_shows_count': artist.upcoming_shows_count
        }

        #Go through all past shows and add in serialized venue info
        past_shows = []
        for past_show in artist.past_shows:
            venue = Venue.query.get(past_show.venue_id)
            past_shows.append({
                'venue_id': past_show.venue_id,
                'start_time': past_show.start_time,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link
            })
        data['past_shows'] = past_shows

        #Go through all upcoming shows and add in serialized venue info
        upcoming_shows = []
        for upcoming_show in artist.upcoming_shows:
            venue = Venue.query.get(upcoming_show.venue_id)
            upcoming_shows.append({
                'venue_id': upcoming_show.venue_id,
                'start_time': upcoming_show.start_time,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link
            })
        data['upcoming_shows'] = upcoming_shows

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter(Artist.id == artist_id).first()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    form = ArtistForm(request.form)
    update_artist = Artist.query.filter(Artist.id == artist_id).first()
    update_artist.name=form.name.data
    update_artist.phone=form.phone.data
    update_artist.state=form.state.data
    update_artist.image_link=form.image_link.data
    update_artist.facebook_link=form.facebook_link.data
    update_artist.city=form.city.data
    update_artist.website=form.website_link.data
    update_artist.genres=form.genres.data
    update_artist.seeking_venue=form.seeking_venue.data
    update_artist.seeking_description=form.seeking_description.data
    db.session.commit()
    db.session.close()

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
    form = ArtistForm(request.form)
    new_artist = Artist(
        name=form.name.data,
        phone=form.phone.data,
        state=form.state.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        city=form.city.data,
        website=form.website_link.data,
        genres=form.genres.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data)
    try:
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('Artist ' + request.form['name'] + " wasn't successfully listed!")
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    #query all the shows
    shows = Show.query.all()
    #go through all shows, add in a dictionary of show info
    for show in shows:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        data.append({
            'venue_id': show.venue_id,
            'artist_id': show.artist_id,
            'venue_name': venue.name,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time
        })

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
    form = ShowForm(request.form)
    new_show = Show(
        start_time=form.start_time.data,
        venue_id=form.venue_id.data,
        artist_id=form.artist_id.data
    )
    try:
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash("Show wasn't successfully listed!")
    finally:
        db.session.close()
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
