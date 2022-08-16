#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from ast import Return
from audioop import add
from calendar import c
import imp
import json
from operator import ge
import re
import sys
from webbrowser import get
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@ app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    venues = Venue.query.order_by(Venue.city, Venue.state).all()
    data = []

    ven_list = []
    venn = []
    for venue in venues:
        ven = {}
        ven['city'] = venue.city
        ven['state'] = venue.state
        if ven not in venn:
            venn.append(ven)
            ven_list.append(venue)

    for venue in ven_list:
        tmpp = {}
        ven_data = []
        tmpp['city'] = venue.city
        tmpp['state'] = venue.state
        for i in (Venue.query.filter_by(city=venue.city, state=venue.state)):
            tmp = {}
            tmp['id'] = i.id
            tmp['name'] = i.name
            tmp['num_upcoming_shows'] = len(list(filter(lambda x: x.start_time > datetime.today(),
                                                        i.shows)))
            ven_data.append(tmp)
        tmpp['venues'] = ven_data
        data.append(tmpp)

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    response = {}
    data = []

    def num_of_upcoming(venue_shows):
        num = 0
        for venue_show in venue_shows:
            if venue_show.start_time > datetime.today():
                num += 1
        return num

    for venue in venues:
        ven = {}
        ven['id'] = venue.id
        ven['name'] = venue.name
        ven['num_upcoming_shows'] = num_of_upcoming(venue.shows)

        data.append(ven)

    response['count'] = len(data)
    response['data'] = data
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue  data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id)

    data = {}

    data['id'] = venue.id
    data['name'] = venue.name
    data['genres'] = [venue.genres]
    data['address'] = venue.address
    data['city'] = venue.city
    data['state'] = venue.state
    data['phone'] = venue.phone
    data['website'] = venue.web_link
    data['facebook_link'] = venue.facebook_link
    data['seeking_venue'] = venue.look_for_talent
    data['seeking_description'] = venue.seek_description
    data['image_link'] = venue.image_link
    data['past_shows'] = (show.get_past_by_venue(Show, venue_id)
                          for show in shows)
    data['upcoming_shows'] = (show.get_upcoming_by_venue(
        Show, venue_id) for show in shows)
    data['past_shows_count'] = venue.num_past_shows()
    data['upcoming_shows_count'] = venue.num_upcoming_shows()

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    if request.form.get('seeking_talent') == None:  # use get method
        look_for_talent = False
    else:
        look_for_talent = True
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        web_link = request.form['website_link']
        look_for_talent = look_for_talent
        seek_description = request.form['seeking_description']
        genres = request.form.getlist('genres')

        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link,
                      facebook_link=facebook_link, web_link=web_link, look_for_talent=look_for_talent,
                      seek_description=seek_description, genres=genres)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')
    finally:
        db.session.close()


@ app.route('/venue/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail
    try:
        venue = Venue.query.get(venue_id)
        for ven in venue.shows:
            db.session.delete(ven)

        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully deleted!')
        return render_template('pages/home.html')
    except:
        db.session.rollback()
        flash('Error Delelting Venue ' + request.form['name'] + '!')
        return render_template('pages/home.html')
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    #  Artists
    #  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    artists = Artist.query.all()
    data = []
    for artist in artists:
        art = {}
        art['id'] = artist.id
        art['name'] = artist.name
        data.append(art)

    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term')
    artists = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    response = {}
    data = []

    def num_of_upcoming(artist_shows):
        num = 0
        for artist_show in artist_shows:
            if artist_show.start_time > datetime.today():
                num += 1
        return num

    for artist in artists:
        art = {}
        art['id'] = artist.id
        art['name'] = artist.name
        art['num_upcoming_shows'] = num_of_upcoming(artist.shows)

        data.append(art)

    response['count'] = len(data)
    response['data'] = data

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.get(artist_id)
    past_shows = []
    upcoming_shows = []
    shows = Show.query.filter_by(artist_id=artist_id)
    for show in shows:
        ven = {}
        if show.start_time < datetime.today():
            ven['venue_id'] = show.venue_id
            ven['venue_name'] = (Venue.query.get(show.venue_id)).name
            ven['venue_image_link'] = (
                Venue.query.get(show.venue_id)).image_link
            ven['start_time'] = str(show.start_time)
            past_shows.append(ven)
        else:
            ven['venue_id'] = show.venue_id
            ven['venue_name'] = (Venue.query.get(show.venue_id)).name
            ven['venue_image_link'] = (
                Venue.query.get(show.venue_id)).image_link
            ven['start_time'] = str(show.start_time)
            upcoming_shows.append(ven)

    data = {}

    data['id'] = artist.id
    data['name'] = artist.name
    data['genres'] = [artist.genres]
    data['city'] = artist.city
    data['state'] = artist.state
    data['phone'] = artist.phone
    data['website'] = artist.web_link
    data['facebook_link'] = artist.facebook_link
    data['seeking_venue'] = artist.look_for_venue
    data['seeking_description'] = artist.seek_description
    data['image_link'] = artist.image_link
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    get_artist = Artist.query.get(artist_id)
    artist = {}
    artist['id'] = get_artist.id
    artist['name'] = get_artist.name
    artist['genres'] = [get_artist.genres]
    artist['city'] = get_artist.city
    artist['state'] = get_artist.state
    artist['phone'] = get_artist.phone
    artist['website'] = get_artist.web_link
    artist['facebook_link'] = get_artist.facebook_link
    artist['seeking_venue'] = get_artist.look_for_venue
    artist['seeking_description'] = get_artist.seek_description
    artist['image_link'] = get_artist.image_link

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    if request.form.get('seeking_venue') == None:
        look_for_venue = False
    else:
        look_for_venue = True
    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.web_link = request.form['website_link']
        artist.look_for_venue = look_for_venue
        artist.seek_description = request.form['seeking_description']
        artist.genres = request.form.getlist('genres')

        artist = Artist(name=artist.name, city=artist.city, state=artist.state, phone=artist.phone, image_link=artist.image_link,
                        facebook_link=artist.facebook_link, web_link=artist.web_link, look_for_venue=artist.look_for_venue,
                        seek_description=artist.seek_description, genres=artist.genres)

        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' +
              request.form['name'] + ' successfully updated.')
        return redirect(url_for('show_artist', artist_id=artist_id))
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return redirect(url_for('show_artist', artist_id=artist_id))
    finally:
        db.session.close()


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    get_venue = Venue.query.get(venue_id)
    venue = {}
    venue['id'] = get_venue.id
    venue['name'] = get_venue.name
    venue['genres'] = [get_venue.genres]
    venue['address'] = get_venue.address
    venue['city'] = get_venue.city
    venue['state'] = get_venue.state
    venue['phone'] = get_venue.phone
    venue['website'] = get_venue.web_link
    venue['facebook_link'] = get_venue.facebook_link
    venue['seeking_talent'] = get_venue.look_for_talent
    venue['seeking_description'] = get_venue.seek_description
    venue['image_link'] = get_venue.image_link
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    if request.form.get('seeking_talent') == None:
        look_for_talent = False
    else:
        look_for_talent = True
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        venue.web_link = request.form['website_link']
        venue.look_for_talent = look_for_talent
        venue.seek_description = request.form['seeking_description']
        venue.genres = request.form.getlist('genres')

        venue = Venue(name=venue.name, city=venue.city, state=venue.state, phone=venue.phone, image_link=venue.image_link,
                      facebook_link=venue.facebook_link, web_link=venue.web_link, look_for_talent=venue.look_for_talent,
                      seek_description=venue.seek_description, genres=venue.genres)

        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' +
              request.form['name'] + ' successfully updated.')
        return redirect(url_for('show_venue', venue_id=venue_id))
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return redirect(url_for('show_venue', venue_id=venue_id))
    finally:
        db.session.close()


#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # # called upon submitting the new artist listing form
    # # TODO: insert form data as a new Venue record in the db, instead
    # # TODO: modify data to be the data object returned from db insertion

    if request.form.get('seeking_venue') == None:
        look_for_venue = False
    else:
        look_for_venue = True
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        web_link = request.form['website_link']
        look_for_venue = look_for_venue
        seek_description = request.form['seeking_description']
        genres = request.form.getlist('genres')

        artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link,
                        facebook_link=facebook_link, web_link=web_link, look_for_venue=look_for_venue,
                        seek_description=seek_description, genres=genres)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')
    finally:
        db.session.close()


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    data = []
    shows = Show.query.all()
    for show in shows:
        shw = {}
        shw['venue_id'] = show.venue_id
        shw['venue_name'] = (Venue.query.get(show.venue_id)).name
        shw['artist_id'] = show.artist_id
        shw['artist_name'] = (Artist.query.get(show.artist_id)).name
        shw['artist_image_link'] = (
            Artist.query.get(show.artist_id).image_link)
        shw['start_time'] = str(show.start_time)
        data.append(shw)

    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        print(sys.exc_info())
        return render_template('pages/home.html')
    finally:
        db.session.close()


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
