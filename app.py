
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


@app.route('/', methods=['DELETE','GET'])
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    data = []
    
    try:
        venues = Venue.query.order_by(Venue.city).all()
        data = []

        for venue in venues:
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id).count(),
                }]
            })
    except:
        db.session.rollback()

    finally:
        db.session.close()

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_by = request.form.get('search_term')
    search_result = Venue.query.filter(
        Venue.name.ilike(f'%{search_by}%')).all()
    response = []

    for result in search_result:
        response.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": Show.query.filter(Show.venue_id == result.id).count(),
        })

    return render_template('pages/search_venues.html',
                           results=response,
                           number=len(search_result),
                           search_by=search_by)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

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
        artist = Artist.query.get(show.artist_id)

        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": "https://www.freedigitalphotos.net/images/img/homepage/394230.jpg",
            "start_time": (show.time).strftime("%m/%d/%Y, %H:%M")
        })

    for show in show_future:
        artist = Artist.query.get(show.artist_id)

        future_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": "https://www.freedigitalphotos.net/images/img/homepage/394230.jpg",
            "start_time": (show.time).strftime("%m/%d/%Y, %H:%M")
        })

    show_data = {
      "past_shows": past_shows,
      "upcoming_shows": future_shows,
      "past_shows_count": show_past.count(),
      "upcoming_shows_count": show_future.count()
    }

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
        genres=", ".join(venue_form.genres.data),
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


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)

    try:
      Show.query.filter(Show.venue_id == venue.id).delete()
      db.session.delete(venue)
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.order_by(Artist.city).all()
    data = []

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
        })


    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    search_by = request.form.get('search_term')
    search_result = Artist.query.filter(
        Artist.name.ilike(f'%{search_by}%')).all()
    response = []

    for result in search_result:
        response.append({
            "id": result.id,
            "name": result.name, 
            "num_upcoming_shows": Show.query.filter(Show.artist_id == result.id).count(),
        })

    return render_template('pages/search_artists.html',
                           results=response,
                           number=len(search_result),
                           search_term=search_by)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):


    artist = Artist.query.filter(Artist.id == artist_id).first()
    show = Show.query.filter(Show.artist_id == artist_id)
    print('artist', artist)
    print(artist.name)

    show_data = []

    current_time = datetime.datetime.utcnow()
    show = Show.query.filter(Show.artist_id == artist_id).all()
    show_past = Show.query.filter(Show.artist_id == artist_id).filter(Show.time < current_time)
    show_future = Show.query.filter(Show.artist_id == artist_id).filter(Show.time > current_time)

    past_shows = []
    future_shows = []

    for show in show_past:
        venue = Venue.query.get(show.venue_id)
        past_shows.append({
            "artist_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": "https://www.freedigitalphotos.net/images/img/homepage/394230.jpg",
            "start_time": (show.time).strftime("%m/%d/%Y, %H:%M")
        })

    for show in show_future:
        venue = Venue.query.get(show.venue_id)
        future_shows.append({
            "artist_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": "https://www.freedigitalphotos.net/images/img/homepage/394230.jpg",
            "start_time": (show.time).strftime("%m/%d/%Y, %H:%M")
        })

    show_data = {
      "past_shows": past_shows,
      "upcoming_shows": future_shows,
      "past_shows_count": show_past.count(),
      "upcoming_shows_count": show_future.count()
    }

   
    return render_template('pages/show_artist.html',
                           artist=artist,
                           shows=show_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form_artist = ArtistForm(request.form)

    try:
      artist = Artist.query.get(artist_id)
     
      artist.name= form_artist.name.data
      artist.genres = ", ".join(form_artist.genres.data)
      artist.city = form_artist.city.data
      artist.state = form_artist.state.data
      artist.phone = form_artist.phone.data
    #  artist.website = form_artist.website.data,
      artist.facebook_link = form_artist.facebook_link.data
    #   artist.seeking_venue = form_artist.seeking_venue.data,
    #   artist.seeking_description = form_artist.seeking_description.data,
    #   artsit.image_link = form_artist.image_link.data
    
      db.session.commit()
    except:
      db.session.rollback()
      print('DB rollback')
      print(sys.exc_info())
      flash(f'There was a problem updating the Artist {request.form["name"]}, please try again')
    finally:
      print('db closed')
      db.session.close()
    
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
   
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form_venue = VenueForm(request.form)

    try:
      venue = Venue.query.get(venue_id)
     
      venue.name= form_venue.name.data
      venue.genres = ", ".join(form_venue.genres.data)
      venue.address = form_venue.address.data
      venue.city = form_venue.city.data
      venue.state = form_venue.state.data
      venue.phone = form_venue.phone.data
    #  venue.website = form_venue.website.data,
      venue.facebook_link = form_venue.facebook_link.data
    #   venue.seeking_talent = form_venue.seeking_venue.data,
    #   venue.seeking_description = form_venue.seeking_description.data,
    #   venue.image_link = form_venue.image_link.data
    
      db.session.commit()
    except:
      db.session.rollback()
      print('DB rollback')
      print(sys.exc_info())
      flash(f'There was a problem updating the Venue {request.form["name"]}, please try again')
    finally:
      print('db closed')
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

    artist = Artist(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        # image_link= request.form['image_link'],
        genres=", ".join(request.form['genres']),
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

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

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
