from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from webapp import create_app, db
from webapp.models import Favorite

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@main_bp.route('/favorites')
@login_required
def favorites():
    """Favorites page - only accessible when logged in"""
    interests = current_user.interests

    # Get user's favorite dining resources
    dining_favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='dining'
    ).all()
    
    # Get user's favorite career resources
    career_favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='career'
    ).all()

    # Get user's favorite wellness resources
    wellness_favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='wellness'
    ).all()
    # Get user's favorite academic resources
    academic_favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='academic'
    ).all()
    # Get user's favorite transportation resources
    transportation_favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='transportation'
    ).all()

    campus_events_clubs_favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='campus_events_clubs'
    ).all()

    # Create a mapping of favorite IDs to display names
    favorite_map = {
        #dining resources
        'dining_locations': {
            'name': 'Dining Halls & Locations',
            'icon': '📍',
            'url': 'https://new.dineoncampus.com/GMU/campus-map'
        },
        'meal_plans': {
            'name': 'Meal Plans',
            'icon': '💳',
            'url': 'https://new.dineoncampus.com/GMU/find-your-perfect-meal-plan'
        },
        'patriot_pantry': {
            'name': 'Patriot Pantry',
            'icon': '🤝',
            'url': 'https://ssac.gmu.edu/patriot-pantry/'
        },

        #career resources
        'technology_resources': {
            'name': 'Tech Industry Resources',
            'icon': '💼',
            'url': 'https://careers.gmu.edu/technology'
        },
        'engineering_resources': {
            'name': 'Engineering Industry Resources',
            'icon': '💼',
            'url': 'https://careers.gmu.edu/engineering'
        },
        'data_science_resources': {
            'name': 'Data Science Industry Resources',
            'icon': '💼',
            'url': 'https://careers.gmu.edu/data-science'
        },       
        'create_resume': {
            'name': 'Create a Resume',
            'icon': '💼',
            'url': 'https://careers.gmu.edu/create-resume'
        },
        'find_job': {
            'name': 'Find a Job',
            'icon': '💼',
            'url': 'https://careers.gmu.edu/find-job-or-internship'
        },

        #wellness resources
        'student_health_services': {
            'name': 'Student Health Services',
            'icon': '🏥',
            'url': 'https://shs.gmu.edu/'
        },
        'counseling_services': {
            'name': 'Counseling and Psychological Services',
            'icon': '💬',
            'url': 'https://caps.gmu.edu/'
        },
        'community_mental_health': {
            'name': 'Community Mental Health',
            'icon': '🧠',
            'url': 'https://ccmh.gmu.edu/services/the-stepped-mental-health-care-program'
        },
        'accessibility_services': {
            'name': 'Accessibility Services',
            'icon': '📝',
            'url': 'https://www.gmu.edu/academics/accessibility-resources'
        },
        'student_advocacy': {
            'name': 'Student Advocacy',
            'icon': '✊',
            'url': 'https://ssac.gmu.edu/'
        },

        #academic resources
        'academicResource1': {
            'name': 'Math Tutoring',
            'icon': '📚',
            'url': 'https://science.gmu.edu/academics/departments-units/mathematical-sciences/math-tutoring'
        },
        'academicResource2': {
            'name': 'The Writing Center',
            'icon': '📚',
            'url': 'https://writingcenter.gmu.edu/'
        },
        'academicResource3': {
            'name': 'The Communication Center',
            'icon': '📚',
            'url': 'https://communicationcenter.gmu.edu/'
        },       
        'academicResource4': {
            'name': 'Academic Coaching Program',
            'icon': '📚',
            'url': 'https://learningservices.gmu.edu/'
        },
        'academicResource5': {
            'name': 'Learning Resources for Multilingual Students',
            'icon': '📚',
            'url': 'https://intomason.gmu.edu/current-students/learning-resource-center'
        },  
        'academicResource6': {
            'name': 'Learning Resources for Online Students',
            'icon': '📚',
            'url': 'https://learningservices.gmu.edu/learning-resources/online-learning/'
        },
        'academicResource7': {
            'name': 'Disability Services',
            'icon': '📚',
            'url': 'https://ds.gmu.edu/'
        },
        'academicResource8': {
            'name': 'Transfer-Student Advising',
            'icon': '📚',
            'url': 'https://advising.gmu.edu/transferstudents/'
        },       
        'academicResource9': {
            'name': 'First-Year GMU Student Advising',
            'icon': '📚',
            'url': 'https://advising.gmu.edu/firstyear/'
        },
        'academicResource10': {
            'name': 'GMU Library Hub',
            'icon': '📚',
            'url': 'https://library.gmu.edu/'
        }, 

        #transportation
        'transportation_services': {
            'name': 'GMU Transportation Services',
            'icon': '🚌',
            'url': 'https://transportation.gmu.edu/transportation-services/'
        },
        'mason_commutes': {
            'name': 'Mason Commutes',
            'icon': '🚙',
            'url': 'https://www.masoncommutes.com/public/home.aspx'
        },
        'parking_information': {
            'name': 'Parking Information',
            'icon': '🅿️',
            'url': 'https://transportation.gmu.edu/parking/#ResidentStudents'
        },

        #campus events and clubs
        'mason360_student_orgs': {
            'name': 'Mason360 – Student Orgs',
            'icon': '🏛️',
            'url': 'https://mason360.gmu.edu/organizations'
        },
        'upcoming_campus_events': {
            'name': 'Upcoming Campus Events',
            'icon': '📅',
            'url': 'https://mason360.gmu.edu/events'
        },
        'center_for_student_involvement': {
            'name': 'Center for Student Involvement',
            'icon': '🎓',
            'url': 'https://csi.gmu.edu/'
        },
        'intramural_recreation': {
            'name': 'Intramural & Recreation',
            'icon': '🏆',
            'url': 'https://recsports.gmu.edu/programs/intramurals/'
        },
        'multicultural_events': {
            'name': 'Multicultural Events',
            'icon': '🌍',
            'url': 'https://odime.gmu.edu/'
        },
        'student_government': {
            'name': 'Student Government',
            'icon': '📢',
            'url': 'https://sga.gmu.edu/'
        }

    }
    
    favorites_display = []
    #dining
    for fav in dining_favorites:
        if fav.resource_id in favorite_map:
            favorites_display.append(favorite_map[fav.resource_id])

    #career
    for fav in career_favorites:
        if fav.resource_id in favorite_map:
            favorites_display.append(favorite_map[fav.resource_id])

    #wellness
    for fav in wellness_favorites:
        if fav.resource_id in favorite_map:
            favorites_display.append(favorite_map[fav.resource_id])

    #academics
    for fav in academic_favorites:
        if fav.resource_id in favorite_map:
            favorites_display.append(favorite_map[fav.resource_id])

    #transportation
    for fav in transportation_favorites:
        if fav.resource_id in favorite_map:
            favorites_display.append(favorite_map[fav.resource_id])

    #campus events and clubs
    for fav in campus_events_clubs_favorites:
        if fav.resource_id in favorite_map:
            favorites_display.append(favorite_map[fav.resource_id])

    return render_template(
        'favorites.html',
        username=current_user.username,
        favorites=favorites_display,
        interests=interests
    )

@main_bp.route('/dashboard')
@login_required
def dashboard_redirect():
    """Legacy dashboard route kept for backward compatibility."""
    return redirect(url_for('main.favorites'))


@main_bp.route('/academicResource')
@login_required
def academicResource():
    """Academic resource page"""
    favorites=Favorite.query.filter_by(user_id=current_user.id, resource_type='academic').all()
    favorite_ids=[fav.resource_id for fav in favorites]
    return render_template('academicResources.html', favorite_ids=favorite_ids)

@main_bp.route('/dining')
@login_required
def dining():
    """Dining and food resources page"""
    # Get user's favorite dining resources
    favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='dining'
    ).all()
    favorite_ids = [fav.resource_id for fav in favorites]
    
    return render_template('dining.html', favorite_ids=favorite_ids)



# transportation route
@main_bp.route('/transportation')
@login_required
def transportation():
    """Transportation resources page"""
    favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='transportation'
    ).all()
    favorite_ids = [fav.resource_id for fav in favorites]

    return render_template('transportation.html', favorite_ids=favorite_ids)




@main_bp.route('/campus-events-clubs')
@login_required
def campus_events_clubs():
    """Campus Events and Clubs page"""
    favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='campus_events_clubs'
    ).all()
    favorite_ids = [fav.resource_id for fav in favorites]
    return render_template('campusEventsClubs.html', favorite_ids=favorite_ids)


@main_bp.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    """Add or remove a favorite resource"""
    data = request.get_json()
    resource_id = data.get('resource_id')
    resource_type = data.get('resource_type', 'dining')
    
    if not resource_id:
        return jsonify({'success': False, 'message': 'Resource ID is required'}), 400
    
    # Check if already favorited
    existing = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_id=resource_id,
        resource_type=resource_type
    ).first()
    
    try:
        if existing:
            # Remove favorite
            db.session.delete(existing)
            message = 'Removed from favorites'
        else:
            # Add favorite
            favorite = Favorite(
                user_id=current_user.id,
                resource_id=resource_id,
                resource_type=resource_type
            )
            db.session.add(favorite)
            message = 'Added to favorites'
        
        db.session.commit()
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/wellness-resources')
@login_required
def wellness_resources():
    """Wellness resources page"""
    #Get user's favorite wellness resources
    favoritets = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='wellness'
    ).all()
    favorite_ids = [fav.resource_id for fav in favoritets]
    return render_template('wellnessResources.html', favorite_ids=favorite_ids)

@main_bp.route('/career-internship-resources')
@login_required
def career_internship_resources():
    """Career and internship resources page"""
    # Get user's favorite career resources
    favorites = Favorite.query.filter_by(
        user_id=current_user.id,
        resource_type='career'
    ).all()
    favorite_ids = [fav.resource_id for fav in favorites]
    
    return render_template('careerInternResources.html', favorite_ids=favorite_ids)



if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
