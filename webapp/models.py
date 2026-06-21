from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from webapp import db, login_manager


user_interests = db.Table(
    'user_interests',
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    ),
    db.Column(
        'interest_id',
        db.Integer,
        db.ForeignKey('interests.id'),
        primary_key=True
    )
)

resource_tags = db.Table(
    'resource_tags',
    db.Column(
        'resource_id',
        db.Integer,
        db.ForeignKey('resources.id'),
        primary_key=True
    ),
    db.Column(
        'tag_id',
        db.Integer,
        db.ForeignKey('tags.id'),
        primary_key=True
    )
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )
    password_hash = db.Column(
        db.String(255),
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    interests = db.relationship(
        'Interest',
        secondary=user_interests,
        backref=db.backref(
            'users',
            lazy='dynamic'
        )
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):
        return f'<User {self.username}>'


class Interest(db.Model):
    __tablename__ = 'interests'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )


class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(db.Text)

    url = db.Column(
        db.String(500),
        nullable=False
    )

    tags = db.relationship(
        'Tag',
        secondary=resource_tags,
        backref=db.backref(
            'resources',
            lazy='dynamic'
        )
    )


class SavedResource(db.Model):
    __tablename__ = 'saved_resources'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    resource_id = db.Column(
        db.Integer,
        db.ForeignKey('resources.id'),
        nullable=False
    )

    user = db.relationship(
        'User',
        backref=db.backref(
            'saved_resources_assoc',
            lazy=True
        )
    )

    resource = db.relationship(
        'Resource',
        backref=db.backref(
            'saved_resources_assoc',
            lazy=True
        )
    )


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    resource_id = db.Column(
        db.String(100),
        nullable=False
    )

    resource_type = db.Column(
        db.String(50),
        default='dining'
    )

    created_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    user = db.relationship(
        'User',
        backref=db.backref(
            'favorites',
            lazy=True,
            cascade='all, delete-orphan'
        )
    )

    __table_args__ = (
        db.UniqueConstraint(
            'user_id',
            'resource_id',
            'resource_type',
            name='uq_user_resource_type'
        ),
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))