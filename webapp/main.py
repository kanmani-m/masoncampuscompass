from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from webapp import create_app, db
from webapp.models import Favorite

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - only accessible when logged in"""
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
    
    
    return render_template('dashboard.html', username=current_user.username, favorites=favorites_display, interests=interests)

@main_bp.route('/academicResource')
@login_required
def academicResource():
    """Academic resource page"""
    return render_template('academicResources.html')

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
    return render_template('transportation.html')


@main_bp.route('/campus-events-clubs')
@login_required
def campus_events_clubs():
    """Campus Events and Clubs page"""
    return render_template('campusEventsClubs.html')



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
    return render_template('wellnessResources.html')

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
