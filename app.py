
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(20))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue = db.relationship("Venue", back_populates="show")
    artist = db.relationship("Artist", back_populates="show")


class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship("Show", back_populates="venue")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', back_populates="artist")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


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

    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    # data=[{
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "venues": [{
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "num_upcoming_shows": 0,
    #   }, {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "num_upcoming_shows": 1,
    #   }]
    # }, {
    #   "city": "New York",
    #   "state": "NY",
    #   "venues": [{
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "num_upcoming_shows": 0,
    #   }]
    # }]
    try:
      # venues = Venue.query.all()
        venues = Venue.query.order_by(Venue.city).all()
        data = []

        for venue in venues:
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": 0,
                }]
            })
    except:
        db.session.rollback()

    finally:
        db.session.close()

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_by = request.form.get('search_term')
    search_result = Venue.query.filter(
        Venue.name.ilike(f'%{search_by}%')).all()
    response = []

    for result in search_result:
        response.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": 0,
        })

    return render_template('pages/search_venues.html',
                           results=response,
                           number=len(search_result),
                           search_by=search_by)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # data1={
    #   "id": 1,
    #   "name": "The Musical Hop",
    #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #   "address": "1015 Folsom Street",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "123-123-1234",
    #   "website": "https://www.themusicalhop.com",
    #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #   "seeking_talent": True,
    #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #   "past_shows": [{
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data2={
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "genres": ["Classical", "R&B", "Hip-Hop"],
    #   "address": "335 Delancey Street",
    #   "city": "New York",
    #   "state": "NY",
    #   "phone": "914-003-1132",
    #   "website": "https://www.theduelingpianos.com",
    #   "facebook_link": "https://www.facebook.com/theduelingpianos",
    #   "seeking_talent": False,
    #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #   "past_shows": [],
    #   "upcoming_shows": [],
    #   "past_shows_count": 0,
    #   "upcoming_shows_count": 0,
    # }
    # data3={
    #   "id": 3,
    #   "name": "Park Square Live Music & Coffee",
    #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #   "address": "34 Whiskey Moore Ave",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "415-000-1234",
    #   "website": "https://www.parksquarelivemusicandcoffee.com",
    #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #   "seeking_talent": False,
    #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #   "past_shows": [{
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [{
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

    venue = Venue.query.filter(Venue.id == venue_id).first()
    current_time = datetime.datetime.utcnow()
    show = Show.query.filter(Show.venue_id == venue_id).all()
    show_past = Show.query.filter(
        Show.venue_id == venue_id).filter(Show.time < current_time)
    show_future = Show.query.filter(
        Show.venue_id == venue_id).filter(Show.time > current_time)

    past_shows = []
    future_shows = []

    for show in show_past:
        name = Artist.query.get(show.artist_id)

        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": name,
            "artist_image_link": "https://www.freedigitalphotos.net/images/img/homepage/394230.jpg",
            "start_time": (show.time).strftime("%m/%d/%Y, %H:%M")
        })

    for show in show_future:
        name = Artist.query.get(show.artist_id)

        future_shows.append({
            "artist_id": show.artist_id,
            "artist_name": name,
            "artist_image_link": "https://www.freedigitalphotos.net/images/img/homepage/394230.jpg",
            "start_time": (show.time).strftime("%m/%d/%Y, %H:%M")
        })

    show_data = {
      "past_shows": past_shows,
      "upcoming_shows": future_shows,
      "past_shows_count": show_past.count(),
      "upcoming_shows_count": show_future.count()
    }

    # venue = {
    #   "id": result.id,
    #   "name": result.name,
    #   "city": result.city,
    #   "state":result.state,
    #   "address": result.address,
    #   "phone": result.phone,
    #   "image_link": result.iamge_link,
    #   "genres": result.genres,
    #   "facebook_link": result.facebook_link,
    #   "upcoming_shows_count": show.count()
    # }

    # for result in show:
    #   show_data.append({
    #     "id": result.id,
    #     "time": result.time,
    #     "venue_id": result.venue_id,
    #     "artist_id": result.artist_id
    #   })

    return render_template('pages/show_venue.html',
                           venue=venue,
                           show=show_data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()

    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    venue_form = VenueForm(request.form)

    venue = Venue(
        name=venue_form.name.data,
        city=venue_form.city.data,
        state=venue_form.state.data,
        address=venue_form.address.data,
        phone=venue_form.phone.data,
        # image_link= request.form['image_link'],
        genres=venue_form.genres.data,
        facebook_link=venue_form.facebook_link.data,
    )
    try:
        number = Venue.query.filter(Venue.name == venue.name).count()

        if number == 0:
            db.session.add(venue)
            db.session.commit()
            flash(f'Venue was {venue_form.name.data} successfully listed!')
        else:
            flash(
                f'This venue is already listed {venue_form.name.data}, please try again')
    except:
        db.session.rollback()
        print('DB rollback')
        print(sys.exc_info())
        flash(
            f'There was a problem recording the venue {venue_form.name.data}, please try again')
    finally:
        print('db closed')
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        Venue.query.get(venue_id).delete()
        db.session.commit()
        flash(f'Venue {venue_form.name.data} has been deleted form the lists')

    except:
        db.session.rollback()
        flash(
            f'There was an error and Venue {venue_form.name.data} could not be deleted at this time. Please try again')

    finally:
        db.session.close()

    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.order_by(Artist.city).all()
    data = []

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
        })

    # data=[{
    #   "id": 4,
    #   "name": "Guns N Petals",
    # }, {
    #   "id": 5,
    #   "name": "Matt Quevedo",
    # }, {
    #   "id": 6,
    #   "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_by = request.form.get('search_term')
    search_result = Artist.query.filter(
        Artist.name.ilike(f'%{search_by}%')).all()
    response = []

    for result in search_result:
        response.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": 0,
        })

    # response={
    #   "count": 1,
    #   "data": [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "num_upcoming_shows": 0,
    #   }]
    # }
    return render_template('pages/search_artists.html',
                           results=response,
                           number=len(search_result),
                           search_term=search_by)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.filter(Artist.id == artist_id).first()
    show = Show.query.filter(Show.artist_id == artist_id)
    print('artist', artist)
    print(artist.name)

    show_data = []

    # data1={
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "genres": ["Rock n Roll"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "326-123-5000",
    #   "website": "https://www.gunsnpetalsband.com",
    #   "facebook_link": "https://www.facebook.com/GunsNPetals",
    #   "seeking_venue": True,
    #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "past_shows": [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data2={
    #   "id": 5,
    #   "name": "Matt Quevedo",
    #   "genres": ["Jazz"],
    #   "city": "New York",
    #   "state": "NY",
    #   "phone": "300-400-5000",
    #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "past_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data3={
    #   "id": 6,
    #   "name": "The Wild Sax Band",
    #   "genres": ["Jazz", "Classical"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "432-325-5432",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "past_shows": [],
    #   "upcoming_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }],
    #   "past_shows_count": 0,
    #   "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html',
                           artist=artist,
                           shows=show_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
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
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    artist = Artist(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        # image_link= request.form['image_link'],
        genres=request.form['genres'],
        facebook_link=request.form['facebook_link'],
    )
    try:
        number = Artist.query.filter(Artist.name == artist.name).count()

        if number == 0:
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        else:
            flash(
                f'This Artsit is already listed {request.form["name"]}, please try again')
    except:
        db.session.rollback()
        print('DB rollback')
        print(sys.exc_info())
        flash(
            f'There was a problem recording the Artist {request.form["name"]}, please try again')
    finally:
        print('db closed')
        db.session.close()

    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    show = Show.query.all()

    data = []

    for result in show:
        venue = Venue.query.get(result.venue_id)
        artist = Artist.query.get(result.artist_id)
        print(result.time)
        data.append({
            "venue_id": result.venue_id,
            "venue_name": venue.name,
            "artist_id": result.artist_id,
            "artist_name": artist.name,
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": (result.time).strftime("%m/%d/%Y, %H:%M")
        })

    # data=[{
    #   "venue_id": 1,
    #   "venue_name": "The Musical Hop",
    #   "artist_id": 4,
    #   "artist_name": "Guns N Petals",
    #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 5,
    #   "artist_name": "Matt Quevedo",
    #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html',
                           shows=data,
                           time=(result.time).strftime("%m/%d/%Y, %H:%M"))


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.time = request.form['start_time']

    try:
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print('DB rollback')
        flash('There was a problem recording the show...please try again')
    finally:
        print('db close')
        db.session.close()

    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success

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
