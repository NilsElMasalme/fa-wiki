from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    permissions = db.relationship('EditorPermission', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, page_slug, section_id=None):
        """Check if user has edit permission for a page/section"""
        for perm in self.permissions:
            if perm.page_slug == '*':
                return True
            if perm.page_slug.endswith('/*'):
                prefix = perm.page_slug[:-2]
                if page_slug.startswith(prefix):
                    if section_id is None or perm.section_id is None or perm.section_id == section_id:
                        return perm.can_edit
            if perm.page_slug == page_slug:
                if section_id is None or perm.section_id is None or perm.section_id == section_id:
                    return perm.can_edit
        return False

class EditorPermission(db.Model):
    __tablename__ = 'editor_permissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    page_slug = db.Column(db.String(200), nullable=False)
    section_id = db.Column(db.String(100), nullable=True)
    can_edit = db.Column(db.Boolean, default=True)

class Page(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    parent_slug = db.Column(db.String(200), nullable=True)
    content_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    content_blocks = db.relationship('ContentBlock', backref='page', lazy='dynamic', cascade='all, delete-orphan')

    def get_content(self):
        return json.loads(self.content_json) if self.content_json else {}

    def set_content(self, content):
        self.content_json = json.dumps(content)

class ContentBlock(db.Model):
    __tablename__ = 'content_blocks'

    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False)
    block_type = db.Column(db.String(50), nullable=False)  # button, text, image, faq, radar_chart, button_grid
    position = db.Column(db.Integer, default=0)
    content_json = db.Column(db.Text, default='{}')
    section_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    buttons = db.relationship('Button', backref='content_block', lazy='dynamic', cascade='all, delete-orphan')

    def get_content(self):
        return json.loads(self.content_json) if self.content_json else {}

    def set_content(self, content):
        self.content_json = json.dumps(content)

class Button(db.Model):
    __tablename__ = 'buttons'

    id = db.Column(db.Integer, primary_key=True)
    content_block_id = db.Column(db.Integer, db.ForeignKey('content_blocks.id'), nullable=False)
    icon_url = db.Column(db.String(500), nullable=True)
    label = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    link_url = db.Column(db.String(500), nullable=False)
    link_type = db.Column(db.String(20), default='internal')  # internal, external
    position = db.Column(db.Integer, default=0)

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icon_url = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, default=0)

    members = db.relationship('TeamMember', backref='team', lazy='dynamic', cascade='all, delete-orphan')
    radar_charts = db.relationship('RadarChart', backref='team', lazy='dynamic', cascade='all, delete-orphan')

class TeamMember(db.Model):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, default=0)

class ReplayReview(db.Model):
    __tablename__ = 'replay_reviews'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content_html = db.Column(db.Text, nullable=False)
    gamemode = db.Column(db.String(50), nullable=True)
    map_name = db.Column(db.String(100), nullable=True)
    author = db.Column(db.String(100), nullable=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RadarChart(db.Model):
    __tablename__ = 'radar_charts'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    content_block_id = db.Column(db.Integer, db.ForeignKey('content_blocks.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    axes_json = db.Column(db.Text, default='[]')
    data_json = db.Column(db.Text, default='[]')

    def get_axes(self):
        return json.loads(self.axes_json) if self.axes_json else []

    def set_axes(self, axes):
        self.axes_json = json.dumps(axes)

    def get_data(self):
        return json.loads(self.data_json) if self.data_json else []

    def set_data(self, data):
        self.data_json = json.dumps(data)

def init_db(app):
    """Initialize database with tables and seed data"""
    with app.app_context():
        db.create_all()

        # Check if we need to seed
        if User.query.count() == 0:
            seed_demo_data()

def seed_demo_data():
    """Seed demo users and initial content"""
    # Demo users
    admin = User(username='admin', email='admin@faf.wiki')
    admin.set_password('admin123')
    db.session.add(admin)

    editor_teams = User(username='editor_teams', email='teams@faf.wiki')
    editor_teams.set_password('editor123')
    db.session.add(editor_teams)

    editor_rules = User(username='editor_rules', email='rules@faf.wiki')
    editor_rules.set_password('editor123')
    db.session.add(editor_rules)

    db.session.flush()

    # Permissions
    db.session.add(EditorPermission(user_id=admin.id, page_slug='*', can_edit=True))
    db.session.add(EditorPermission(user_id=editor_teams.id, page_slug='teams/*', can_edit=True))
    db.session.add(EditorPermission(user_id=editor_rules.id, page_slug='rules/*', can_edit=True))

    # Teams
    teams_data = [
        ('Trainer Team', 'trainer', 'Training and coaching players'),
        ('Promotions Team', 'promotions', 'Promoting FAF content and events'),
        ('FAF Live Team', 'faf-live', 'Live streaming and casting'),
        ('Tournament Team', 'tournament', 'Organizing tournaments'),
        ('Matchmaking Team', 'matchmaking', 'Improving matchmaking experience'),
        ('Balance Team', 'balance', 'Game balance and patches'),
        ('Games Team', 'games', 'Game development'),
        ('Creative Team', 'creative', 'Art, design and creative content'),
        ('Moderation Team', 'moderation', 'Community moderation'),
        ('DevOps Team', 'devops', 'Infrastructure and operations'),
        ('Campaign Team', 'campaign', 'Single player campaigns'),
    ]

    for i, (name, slug, desc) in enumerate(teams_data):
        team = Team(name=name, slug=slug, description=desc, position=i)
        db.session.add(team)

    # Home page
    home_page = Page(slug='home', title='FAForever Wiki')
    db.session.add(home_page)
    db.session.flush()

    # Main navigation buttons
    main_buttons = ContentBlock(
        page_id=home_page.id,
        block_type='button_grid',
        position=0,
        section_id='main-nav'
    )
    db.session.add(main_buttons)
    db.session.flush()

    nav_items = [
        ('Getting Started', 'Start your FAF journey', '/getting-started', 'rocket'),
        ('Playing', 'Learn to play', '/playing', 'gamepad'),
        ('Rules', 'Community guidelines', '/rules', 'book'),
        ('FAF Teams', 'Meet the teams', '/teams', 'users'),
    ]

    for i, (label, desc, url, icon) in enumerate(nav_items):
        btn = Button(
            content_block_id=main_buttons.id,
            label=label,
            description=desc,
            link_url=url,
            link_type='internal',
            icon_url=f'/static/assets/icons/{icon}.svg',
            position=i
        )
        db.session.add(btn)

    db.session.commit()
