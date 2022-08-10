#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
# Link up flask migration
migrate = Migrate(app, db)

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
    artists = Artist.query.order_by(Artist.id.desc()).limit(10)
    venues = Venue.query.order_by(Venue.id.desc()).limit(10)
    return render_template('pages/home.html', recent_artists=artists, recent_venues=venues)


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    try:
        allVenues = Venue.query.all()

        # Get all unique venue city and state in a set
        unique_locations = set()
        for venue in allVenues:
            unique_locations.add((venue.city, venue.state))

        response = []

        for place in unique_locations:
            venues_in_unique_locations = []
            for venue in allVenues:
                if venue.city == place[0] and venue.state == place[1]:
                    upcoming_shows = db.session.query(Show).join(Venue).filter(
                        Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()
                    venues_in_unique_locations.append({
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": len(upcoming_shows)
                    })

            response.append({
                "city": place[0],
                "state": place[1],
                "venues": venues_in_unique_locations
            })

    except:
        print(sys.exc_info())
        flash("An error occurred while getting all the venues")
    return render_template('pages/venues.html', areas=response)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    try:
        venues = Venue.query.filter(
            Venue.name.ilike('%' + search_term + '%')).all()
        venues_list = []

        for venue in venues:
            upcoming_shows = db.session.query(Show).join(Venue).filter(
                Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()
            venues_list.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows)
            })
        response = {
            "count": len(venues),
            "data": venues_list
        }
    except:
        print(sys.exc_info())
        flash("An error occurred while searching the venues")

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    try:
        venue = Venue.query.get_or_404(venue_id)

        response_past_shows = []
        response_upcoming_shows = []

        past_shows = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue.id).filter(Show.start_time < datetime.now()).all()

        upcoming_shows = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()

        for show in past_shows:
            print(show)

            response_past_shows.append({
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time),
            })

        for show in upcoming_shows:
            print("upcoming_shows", show)
            response_upcoming_shows.append({
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time),
            })

        response = {
            "id": venue_id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": response_past_shows,
            "upcoming_shows": response_upcoming_shows,
            "past_shows_count": len(response_past_shows),
            "upcoming_shows_count": len(response_upcoming_shows),
        }
    except:
        print(sys.exc_info())
        flash("An error occurred while getting the venue")
    finally:
        return render_template('pages/show_venue.html', venue=response)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data
    genres = form.genres.data

    if not form.validate():
        for message in form.errors.items():
            flash(f"{message[0].capitalize()}: {message[1][0]}", 'error')
        return redirect(url_for('create_venue_form'))

    duplicate_venue = Venue.query.filter_by(name=name).first()
    if duplicate_venue:
        flash(f"{duplicate_venue.name} already exists", "error")
        return redirect(url_for('create_venue_form'))
    error = False
    try:
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link, website=website,
                      seeking_talent=seeking_talent, seeking_description=seeking_description, genres=genres)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + form.name.data +
              ' was successfully listed!')
    except:
        error = True
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
        abort(500)
    finally:
        db.session.close()

    if error:
        return redirect(url_for('create_venue_form'))
    else:
        return redirect(url_for('show_venue', venue_id=Venue.query.order_by(Venue.id.desc()).first().id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash(f'Venue was successfully deleted!')
        return jsonify({
            'success': True,
            'message': f'Venue was successfully deleted!'
        })
    except:
        db.session.rollback()
        print(sys.exc_info())
        return jsonify({
            'success': False,
            'message': f'There was a problem deleting',
        })
    finally:
        db.session.close()

    # * BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = Artist.query.all()
    response = []
    for artist in artists:
        response.append({
            "id": artist.id,
            "name": artist.name,
        })
    return render_template('pages/artists.html', artists=response)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(
        Artist.name.ilike('%' + search_term + '%')).all()

    artists_list = []
    for artist in artists:
        upcoming_shows = db.session.query(Show).join(Venue).filter(
            Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()
        artists_list.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(upcoming_shows),
        })

    response = {
        "count": len(artists),
        "data": artists_list
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get_or_404(artist_id)
    response_upcoming_shows = []
    response_past_shows = []

    past_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist.id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()

    for show in upcoming_shows:
        response_upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time),
        })

    for show in past_shows:
        response_past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time),
        })

    response = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": (artist.phone),
        "seeking_venue": artist.seeking_venue,
        "image_link": artist.image_link,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "past_shows": response_past_shows,
        "upcoming_shows": response_upcoming_shows,
        "past_shows_count": len(response_past_shows),
        "upcoming_shows_count": len(response_upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=response)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(name=artist.name, city=artist.city, state=artist.state, phone=artist.phone, image_link=artist.image_link, facebook_link=artist.facebook_link,
                      website_link=artist.website, seeking_venue=artist.seeking_venue, seeking_description=artist.seeking_description, genres=artist.genres)
    return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    # artist record with ID <artist_id> using the new attributes
    if not form.validate():
        for message in form.errors.items():
            flash(f"{message[0].capitalize()}: {message[1][0]}")
        return redirect(url_for('edit_artist', artist_id=artist_id))
    error = False
    try:
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.genres = form.genres.data

        db.session.commit()
        flash(f"The artist {form.name.data} has been updated successfully")
    except:
        db.session.rollback()
        error = True
        flash(f"An error occurred while updating the artist")
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        return redirect(url_for('edit_artist', artist_id=artist_id))
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(name=venue.name, city=venue.city, state=venue.state, address=venue.address, phone=venue.phone, image_link=venue.image_link, facebook_link=venue.facebook_link, website_link=venue.website,
                     seeking_talent=venue.seeking_talent, seeking_description=venue.seeking_description, genres=venue.genres)
    return render_template('forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)

    if not form.validate():
        for message in form.errors.items():
            flash(f"{message[0].capitalize()}: {message[1][0]}",
                  "error")
        return redirect(url_for('edit_venue', venue_id=venue_id))

    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.genres = form.genres.data

        db.session.commit()
        flash(
            f"The venue {form.name.data} has been updated successfully")
    except:
        db.session.rollback()
        error = True
        flash(f"An error occurred while updating the venue")
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        return redirect(url_for('edit_venue', venue_id=venue_id))
    else:
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

    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
    genres = form.genres.data

    if not form.validate():
        for message in form.errors.items():
            flash(f"{message[0].capitalize()}: {message[1][0]}",
                  "error")
        return redirect(url_for('create_artist_form'))

    duplicate_artist = Artist.query.filter_by(name=name).first()
    if duplicate_artist:
        flash(f"{duplicate_artist.name} already exists", "error")
        return redirect(url_for('create_artist_form'))
    error = False
    try:
        artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, facebook_link=facebook_link,
                        website=website, seeking_venue=seeking_venue, seeking_description=seeking_description, genres=genres)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash(f"Artist {form.name.data} was successfully listed")

    except:
        error = True
        flash('An error occurred. Artist {name} could not be listed.')
        db.session.rollback()
        abort(500)
    finally:
        db.session.close()

    if error:
        return redirect(url_for('create_artist_form'))
    else:
        return redirect(url_for('show_artist', artist_id=Artist.query.order_by(Artist.id.desc()).first().id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows = Show.query.all()

    response = []
    for show in shows:
        response.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=response)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm(request.form)
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

    if not form.validate():
        for message in form.errors.items():
            flash(f"{message[0].capitalize()}: {message[1][0]}", "error")
        return redirect(url_for('create_shows'))

    artist_count = Artist.query.filter_by(id=artist_id).count()
    venue_count = Venue.query.filter_by(id=venue_id).count()

    if not artist_count or not venue_count:
        flash(
            f"The selected {'artist' if not artist_count else 'venue'} does not exist in our record. Please try another id", "error")
        return redirect(url_for('create_shows'))
    error = False
    try:
        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        flash('An error occurred. Show could not be listed.', "error")
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        return redirect(url_for('create_shows'))
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        return redirect(url_for('shows'))


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
