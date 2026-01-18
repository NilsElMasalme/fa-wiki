"""
FAForever Wiki - Main Application
A futuristic wiki for FAForever with editor functionality
"""

import os
from datetime import datetime, timedelta
from flask import Flask, Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import current_user, login_required
from werkzeug.middleware.proxy_fix import ProxyFix

from config import get_config, BASE_PATH
from models import db, init_db, User, Page, ContentBlock, Button, Team, TeamMember, ReplayReview, RadarChart, EditorPermission
from auth import auth_bp, init_auth, can_edit, editor_mode_active

# Create Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Proxy fix for reverse proxy support
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize extensions
db.init_app(app)
init_auth(app)

# Register auth blueprint
app.register_blueprint(auth_bp, url_prefix=f'{BASE_PATH}')

# Main routes blueprint
main_bp = Blueprint('main', __name__)

# API routes blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


# =============================================================================
# Context Processors
# =============================================================================

@app.context_processor
def inject_globals():
    """Inject global variables into templates"""
    teams = Team.query.order_by(Team.position).limit(5).all()

    # Extract current page slug from request
    current_slug = None
    if request.endpoint == 'main.page':
        current_slug = request.view_args.get('slug', '')
    elif request.endpoint == 'main.rules_detail':
        current_slug = request.view_args.get('slug', '')
    elif request.endpoint == 'main.team_detail':
        current_slug = request.view_args.get('slug', '')

    return {
        'editor_mode': editor_mode_active(),
        'base_path': BASE_PATH,
        'current_year': datetime.now().year,
        'teams_nav': teams,
        'current_slug': current_slug
    }


# =============================================================================
# Main Routes
# =============================================================================

@main_bp.route('/')
def home():
    """Dashboard homepage with news, stats, activity"""
    # Stats
    stats = {
        'pages': Page.query.count() or 45,
        'teams': Team.query.count() or 11,
        'reviews': ReplayReview.query.count() or 23
    }

    # News items (hardcoded for demo)
    news_items = [
        {
            'category': 'patch',
            'title': 'Balance Patch 3812 Released',
            'excerpt': 'Major balance changes to T3 air units and experimental weapons. Cybran Loyalist now has improved splash damage, and Aeon Restorer cost reduced by 15%.',
            'date': 'Jan 15, 2026',
            'author': 'Balance Team'
        },
        {
            'category': 'event',
            'title': 'Winter Championship 2026 Announced',
            'excerpt': 'Registration is now open for the Winter Championship. $5000 prize pool with matches starting February 1st. Sign up on the forums!',
            'date': 'Jan 12, 2026',
            'author': 'Tournament Team'
        },
        {
            'category': 'announcement',
            'title': 'New Matchmaker Rating System',
            'excerpt': 'We are rolling out Trueskill2 for all ladder queues. Your rating will be recalculated over the next few games for better match quality.',
            'date': 'Jan 10, 2026',
            'author': 'Matchmaking Team'
        },
        {
            'category': 'update',
            'title': 'FAF Client v2024.1.0 Available',
            'excerpt': 'New client version with improved map preview, faster downloads, and a redesigned chat interface. Update now for the best experience.',
            'date': 'Jan 8, 2026',
            'author': 'DevOps Team'
        }
    ]

    # Activities (hardcoded for demo)
    activities = [
        {'type': 'edit', 'text': '<strong>Brutus5000</strong> updated "Economy Guide"', 'time': '2 hours ago'},
        {'type': 'add', 'text': '<strong>Trainer Team</strong> added new replay review', 'time': '5 hours ago'},
        {'type': 'user', 'text': '<strong>Sheikah</strong> joined the Balance Team', 'time': '1 day ago'},
        {'type': 'edit', 'text': '<strong>Askaholic</strong> updated "API Documentation"', 'time': '2 days ago'},
        {'type': 'add', 'text': '<strong>Penguin</strong> added "Seraphim T2 Guide"', 'time': '3 days ago'}
    ]

    return render_template('pages/home.html',
                         stats=stats,
                         news_items=news_items,
                         activities=activities,
                         active_nav='home',
                         current_path='Dashboard')


@main_bp.route('/getting-started')
def getting_started():
    """Getting Started page"""
    breadcrumbs = [
        {'name': 'Home', 'url': url_for('main.home')},
        {'name': 'Getting Started', 'url': None}
    ]

    faqs = [
        {'id': 1, 'question': 'What is FAForever?', 'answer': 'FAForever (FAF) is a community-driven project to provide a living multiplayer experience for Supreme Commander: Forged Alliance. We maintain dedicated servers, a custom client, and continuously update the game with balance patches, new maps, and mods.'},
        {'id': 2, 'question': 'Do I need the original game?', 'answer': 'Yes, you need a legitimate copy of Supreme Commander: Forged Alliance. You can purchase it on Steam or GOG. The FAF client will automatically patch your game to the latest version.'},
        {'id': 3, 'question': 'Is FAF free to play?', 'answer': 'FAF itself is completely free. You only need to own the base game (Supreme Commander: Forged Alliance). All patches, maps, mods, and client updates are provided at no cost.'},
        {'id': 4, 'question': 'How do I find games?', 'answer': 'Use the FAF client to browse the game lobby or join matchmaking queues. The matchmaker will find opponents of similar skill level for 1v1, 2v2, or 4v4 matches.'},
        {'id': 5, 'question': 'Where can I get help?', 'answer': 'Join our Discord server for real-time help from the community. You can also ask questions on the forums or check the #help-and-support channel.'}
    ]

    return render_template('pages/getting_started.html',
                         faqs=faqs,
                         breadcrumbs=breadcrumbs,
                         active_nav='getting-started',
                         current_path='Getting Started')


@main_bp.route('/playing')
def playing():
    """Playing page with game guides overview"""
    breadcrumbs = [
        {'name': 'Home', 'url': url_for('main.home')},
        {'name': 'Playing', 'url': None}
    ]

    return render_template('pages/playing.html',
                         breadcrumbs=breadcrumbs,
                         active_nav='playing',
                         current_path='Playing')


@main_bp.route('/rules')
def rules():
    """Rules overview page"""
    breadcrumbs = [
        {'name': 'Home', 'url': url_for('main.home')},
        {'name': 'Rules', 'url': None}
    ]

    return render_template('pages/rules.html',
                         breadcrumbs=breadcrumbs,
                         active_nav='rules',
                         current_path='Rules')


@main_bp.route('/rules/<slug>')
def rules_detail(slug):
    """Individual rules page with actual content"""
    breadcrumbs = [
        {'name': 'Home', 'url': url_for('main.home')},
        {'name': 'Rules', 'url': url_for('main.rules')},
        {'name': slug.replace('-', ' ').title(), 'url': None}
    ]

    # Get or create the page with content
    page = Page.query.filter_by(slug=f'rules/{slug}').first()
    if not page:
        page = Page(slug=f'rules/{slug}', title=slug.replace('-', ' ').title())
        db.session.add(page)
        db.session.commit()

    content = page.get_content()
    content_html = content.get('html', get_default_rules_content(slug))

    return render_template('pages/rules_detail.html',
                         page=page,
                         content_html=content_html,
                         breadcrumbs=breadcrumbs,
                         active_nav='rules',
                         current_path=f'Rules > {page.title}')


@main_bp.route('/teams')
def teams():
    """FAF Teams overview page"""
    breadcrumbs = [
        {'name': 'Home', 'url': url_for('main.home')},
        {'name': 'FAF Teams', 'url': None}
    ]

    teams_list = Team.query.order_by(Team.position).all()

    return render_template('pages/faf_teams.html',
                         teams=teams_list,
                         breadcrumbs=breadcrumbs,
                         active_nav='teams',
                         current_path='FAF Teams')


@main_bp.route('/teams/<slug>')
def team_detail(slug):
    """Individual team page"""
    team = Team.query.filter_by(slug=slug).first_or_404()

    breadcrumbs = [
        {'name': 'Home', 'url': url_for('main.home')},
        {'name': 'FAF Teams', 'url': url_for('main.teams')},
        {'name': team.name, 'url': None}
    ]

    members = TeamMember.query.filter_by(team_id=team.id).order_by(TeamMember.position).all()
    radar_charts = RadarChart.query.filter_by(team_id=team.id).all()

    # Get replay reviews for trainer team
    reviews = []
    if slug == 'trainer':
        reviews = ReplayReview.query.order_by(ReplayReview.published_at.desc()).limit(10).all()

    return render_template('pages/team_detail.html',
                         team=team,
                         members=members,
                         radar_charts=radar_charts,
                         reviews=reviews,
                         breadcrumbs=breadcrumbs,
                         active_nav='teams',
                         current_path=f'FAF Teams > {team.name}')


@main_bp.route('/creation')
def creation():
    """Creation & Development page"""
    breadcrumbs = [
        {'name': 'Home', 'url': url_for('main.home')},
        {'name': 'Creation & Development', 'url': None}
    ]

    return render_template('pages/creation_dev.html',
                         breadcrumbs=breadcrumbs,
                         active_nav='creation',
                         current_path='Creation & Development')


@main_bp.route('/page/<slug>')
def page(slug):
    """Generic page route"""
    page_obj = Page.query.filter_by(slug=slug).first()
    if not page_obj:
        page_obj = Page(slug=slug, title=slug.replace('-', ' ').title())
        db.session.add(page_obj)
        db.session.commit()

    # Determine active_nav based on slug category
    playing_pages = ['game-basics', 'matchmaking', 'tutorials', 'replays', 'eco-guide',
                     'micro-guide', 'faction-guide', 'build-orders', 'hotkeys', '1v1-guide',
                     'tmm-guide', 'custom-games', 'coop-campaign', 'faction-uef',
                     'faction-cybran', 'faction-aeon', 'faction-seraphim']
    creation_pages = ['mapping', 'modding', 'development', 'balance-contributions']

    if slug in playing_pages:
        active_nav = 'playing'
        parent_name = 'Playing'
        parent_url = url_for('main.playing')
    elif slug in creation_pages:
        active_nav = 'creation'
        parent_name = 'Creation & Dev'
        parent_url = url_for('main.creation')
    else:
        active_nav = None
        parent_name = None
        parent_url = None

    breadcrumbs = [
        {'name': 'Home', 'url': url_for('main.home')}
    ]
    if parent_name:
        breadcrumbs.append({'name': parent_name, 'url': parent_url})
    breadcrumbs.append({'name': page_obj.title, 'url': None})

    content = page_obj.get_content()
    content_html = content.get('html', get_default_page_content(slug))

    return render_template('pages/generic.html',
                         page=page_obj,
                         content_html=content_html,
                         breadcrumbs=breadcrumbs,
                         active_nav=active_nav,
                         current_path=page_obj.title)


# =============================================================================
# API Routes (same as before, abbreviated)
# =============================================================================

@api_bp.route('/button/form')
@login_required
def button_form():
    button_id = request.args.get('button_id')
    section = request.args.get('section', '')
    page_slug = request.args.get('page', '')
    button = Button.query.get(button_id) if button_id else None
    return render_template('partials/button_form.html', button=button, section=section, page_slug=page_slug)

@api_bp.route('/button', methods=['POST'])
@login_required
def create_button():
    data = request.form
    page_slug = data.get('page_slug', 'home')
    section_id = data.get('section_id', 'main-nav')
    page = Page.query.filter_by(slug=page_slug).first()
    if not page:
        page = Page(slug=page_slug, title=page_slug.replace('-', ' ').title())
        db.session.add(page)
        db.session.flush()
    content_block = ContentBlock.query.filter_by(page_id=page.id, section_id=section_id).first()
    if not content_block:
        content_block = ContentBlock(page_id=page.id, block_type='button_grid', section_id=section_id)
        db.session.add(content_block)
        db.session.flush()
    max_pos = db.session.query(db.func.max(Button.position)).filter_by(content_block_id=content_block.id).scalar() or 0
    button = Button(
        content_block_id=content_block.id,
        label=data.get('label', 'New Button'),
        description=data.get('description', ''),
        link_url=data.get('link_url', '#'),
        link_type=data.get('link_type', 'internal'),
        icon_url=data.get('icon_url', ''),
        position=max_pos + 1
    )
    db.session.add(button)
    db.session.commit()
    return jsonify({'success': True, 'id': button.id})

@api_bp.route('/page/<slug>/content', methods=['PUT'])
@login_required
def update_page_content(slug):
    page = Page.query.filter_by(slug=slug).first()
    if not page:
        page = Page(slug=slug, title=slug.replace('-', ' ').title())
        db.session.add(page)
    data = request.get_json()
    content = page.get_content()
    content['html'] = data.get('content', '')
    page.set_content(content)
    page.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/reviews')
def reviews():
    """API endpoint for replay reviews with filtering"""
    gamemode = request.args.get('gamemode', '')
    time_filter = request.args.get('filter', '')

    query = ReplayReview.query

    if gamemode:
        query = query.filter(ReplayReview.gamemode == gamemode)

    reviews = query.order_by(ReplayReview.published_at.desc()).limit(10).all()

    html = ''
    for review in reviews:
        html += f'''
        <div class="review-card">
            <div class="review-header">
                <span class="review-gamemode">{review.gamemode}</span>
                <span class="review-map">{review.map_name}</span>
            </div>
            <h4 class="review-title">{review.title}</h4>
            <div class="review-content">{review.content_html[:200]}...</div>
            <div class="review-meta">
                <span>by {review.author}</span>
                <span>{review.published_at.strftime('%Y-%m-%d')}</span>
            </div>
        </div>
        '''

    if not html:
        html = '<p class="text-muted">No replay reviews found.</p>'

    return html


# =============================================================================
# Helper Functions
# =============================================================================

def get_page_buttons(page_slug, section_id):
    page = Page.query.filter_by(slug=page_slug).first()
    if not page:
        return []
    content_block = ContentBlock.query.filter_by(page_id=page.id, section_id=section_id).first()
    if not content_block:
        return []
    return Button.query.filter_by(content_block_id=content_block.id).order_by(Button.position).all()

def get_page_faqs(page_slug):
    return []

def get_default_rules_content(slug):
    rules_content = {
        'general-rules': '''
<h2>General Community Rules</h2>
<p>Welcome to FAForever! To ensure everyone has a great experience, please follow these rules:</p>

<h3>1. Respect All Players</h3>
<p>Treat everyone with respect. Harassment, hate speech, discrimination based on race, gender, nationality, religion, or sexual orientation will not be tolerated and will result in immediate action.</p>

<h3>2. No Cheating or Exploiting</h3>
<p>Using cheats, hacks, exploits, or any unauthorized modifications that give you an unfair advantage is strictly prohibited. This includes:</p>
<ul>
    <li>Map hacks or vision cheats</li>
    <li>Speed hacks or resource exploits</li>
    <li>Automated scripts (bots) that play for you</li>
    <li>Exploiting game bugs intentionally</li>
</ul>

<h3>3. Game Conduct</h3>
<p>When playing games:</p>
<ul>
    <li>Don't intentionally grief teammates</li>
    <li>Don't abandon rated games without good reason</li>
    <li>Don't abuse the rating system (smurfing, boosting)</li>
    <li>Accept losses gracefully - everyone loses sometimes</li>
</ul>

<h3>4. Chat Behavior</h3>
<p>In all FAF chat channels:</p>
<ul>
    <li>No spamming or flooding</li>
    <li>No advertising unrelated content</li>
    <li>Keep conversations appropriate for all ages</li>
    <li>English is preferred in global channels</li>
</ul>

<h3>5. Account Rules</h3>
<p>Each player may only have ONE account. Multiple accounts ("smurfs") are prohibited and will be banned. If you lose access to your account, contact support.</p>

<h3>Enforcement</h3>
<p>Violations may result in warnings, temporary bans, or permanent bans depending on severity. Appeals can be made on the forums or via Discord moderation channel.</p>
''',
        'vault-rules': '''
<h2>Map & Mod Vault Rules</h2>
<p>The vault allows community members to share maps and mods. To keep it useful for everyone, follow these guidelines:</p>

<h3>Content Requirements</h3>
<ul>
    <li><strong>Originality:</strong> Only upload content you created or have permission to share</li>
    <li><strong>Quality:</strong> Maps should be playable and tested. Broken uploads will be removed.</li>
    <li><strong>Naming:</strong> Use clear, descriptive names. No profanity or misleading titles.</li>
    <li><strong>Screenshots:</strong> Include clear preview images showing the map/mod</li>
</ul>

<h3>Map Requirements</h3>
<ul>
    <li>Must have proper spawn points for the listed player count</li>
    <li>Must have working mass points and hydros</li>
    <li>Should be reasonably balanced for competitive play</li>
    <li>File size should be optimized (no unnecessarily large textures)</li>
</ul>

<h3>Mod Requirements</h3>
<ul>
    <li>Must be compatible with current FAF version</li>
    <li>Should include clear description of features</li>
    <li>UI mods must not provide unfair advantages</li>
    <li>Sim mods are for unranked/custom games only</li>
</ul>

<h3>Prohibited Content</h3>
<ul>
    <li>Copyrighted material without permission</li>
    <li>Malicious code or exploits</li>
    <li>Offensive imagery or names</li>
    <li>Duplicate uploads of existing content</li>
</ul>
''',
        'chat-rules': '''
<h2>Chat & Communication Rules</h2>
<p>FAF provides multiple ways to communicate. Please follow these rules across all platforms:</p>

<h3>In-Game Chat</h3>
<ul>
    <li>Be respectful to opponents and teammates</li>
    <li>Brief strategic communication is fine</li>
    <li>Don't spam or flood the chat</li>
    <li>Saying "gg" at the end is good etiquette</li>
</ul>

<h3>Lobby Chat (#aeolus)</h3>
<ul>
    <li>English is the primary language</li>
    <li>Keep discussions friendly and on-topic</li>
    <li>Don't advertise external services</li>
    <li>Political and religious debates should be avoided</li>
</ul>

<h3>Discord Server</h3>
<ul>
    <li>Read and follow channel-specific rules</li>
    <li>Use appropriate channels for your topic</li>
    <li>Don't ping @everyone or staff without reason</li>
    <li>Voice channels: no excessive background noise</li>
</ul>

<h3>Forums</h3>
<ul>
    <li>Search before posting duplicate topics</li>
    <li>Stay on topic within threads</li>
    <li>Constructive criticism is welcome; personal attacks are not</li>
    <li>Don't bump old threads without good reason</li>
</ul>
'''
    }
    return rules_content.get(slug, '<p>Content coming soon...</p>')

def get_default_page_content(slug):
    page_content = {
        'game-basics': '''
<h2>Game Basics</h2>
<p>Supreme Commander: Forged Alliance is a real-time strategy game focused on large-scale warfare. Here are the fundamentals:</p>

<h3>Resources</h3>
<p>Two resources drive your economy:</p>
<ul>
    <li><strong>Mass:</strong> Collected from mass extractors placed on mass points (shown as white dots on the map)</li>
    <li><strong>Energy:</strong> Generated by power generators, hydrocarbons, and some other buildings</li>
</ul>

<h3>Tech Levels</h3>
<p>Units and buildings come in four tech levels:</p>
<ul>
    <li><strong>T1:</strong> Basic units, cheap and fast to build</li>
    <li><strong>T2:</strong> More powerful units with special abilities</li>
    <li><strong>T3:</strong> Advanced units with high firepower</li>
    <li><strong>T4 (Experimental):</strong> Game-changing superunits</li>
</ul>

<h3>Your Commander (ACU)</h3>
<p>Your Armored Command Unit is both your most powerful unit and your victory condition. If it dies, you lose! The ACU can:</p>
<ul>
    <li>Build structures</li>
    <li>Fight enemies (overcharge attack)</li>
    <li>Be upgraded with various enhancements</li>
    <li>Capture enemy buildings</li>
</ul>
''',
        'matchmaking': '''
<h2>Matchmaking System</h2>
<p>FAF uses a sophisticated matchmaking system to create balanced games:</p>

<h3>Available Queues</h3>
<ul>
    <li><strong>1v1 Ladder:</strong> Competitive solo queue</li>
    <li><strong>2v2 TMM:</strong> Team matchmaker for pairs</li>
    <li><strong>4v4 TMM:</strong> Full team matchmaker</li>
</ul>

<h3>Rating System</h3>
<p>FAF uses TrueSkill2 to track player skill:</p>
<ul>
    <li>Separate ratings for each queue</li>
    <li>Rating adjusts after each game based on performance</li>
    <li>Uncertainty decreases as you play more games</li>
</ul>

<h3>How Matching Works</h3>
<ol>
    <li>Join a queue in the FAF client</li>
    <li>System searches for players of similar rating</li>
    <li>Search expands over time if no match found</li>
    <li>When matched, map is randomly selected from the pool</li>
</ol>
''',
        'tutorials': '''
<h2>Tutorials & Learning Resources</h2>

<h3>Video Tutorials</h3>
<p>Check out these community-created tutorials:</p>
<ul>
    <li>Heaven's Beginner Guide Series</li>
    <li>Jagged's Build Order Tutorials</li>
    <li>BRNKoINSANITY's Casting Analysis</li>
</ul>

<h3>Practice Methods</h3>
<ol>
    <li><strong>Campaign:</strong> Play the single-player campaign to learn basics</li>
    <li><strong>AI Games:</strong> Practice against AI opponents</li>
    <li><strong>Replay Analysis:</strong> Watch your games to identify mistakes</li>
    <li><strong>Trainer Sessions:</strong> Request a session from the Trainer Team</li>
</ol>
''',
        'mapping': '''
<h2>Map Creation Guide</h2>
<p>Creating maps for FAF is a rewarding way to contribute to the community!</p>

<h3>Getting Started</h3>
<ol>
    <li>Download the FAF Map Editor from the client</li>
    <li>Learn the terrain tools and object placement</li>
    <li>Study existing maps to understand good design</li>
    <li>Join #mapping on Discord for help</li>
</ol>

<h3>Map Design Tips</h3>
<ul>
    <li>Balance spawn positions carefully</li>
    <li>Consider all game modes (1v1 to 8v8)</li>
    <li>Test your map against AI before publishing</li>
    <li>Get feedback from experienced mappers</li>
</ul>
''',
        'development': '''
<h2>Contributing to FAF Development</h2>
<p>FAF is open source and welcomes contributors!</p>

<h3>Projects</h3>
<ul>
    <li><strong>fa:</strong> Game patches and balance</li>
    <li><strong>client:</strong> The FAF client application</li>
    <li><strong>server:</strong> Backend game servers</li>
    <li><strong>api:</strong> REST API for FAF services</li>
</ul>

<h3>How to Contribute</h3>
<ol>
    <li>Fork the repository on GitHub</li>
    <li>Make your changes in a feature branch</li>
    <li>Submit a pull request with clear description</li>
    <li>Address review feedback</li>
</ol>

<p>Visit <a href="https://github.com/FAForever">github.com/FAForever</a> to explore our repositories.</p>
'''
    }
    return page_content.get(slug, '<p>This page is under construction. Content coming soon!</p>')


# =============================================================================
# Register Blueprints
# =============================================================================

app.register_blueprint(main_bp, url_prefix=BASE_PATH)
app.register_blueprint(api_bp, url_prefix=f'{BASE_PATH}/api')


# =============================================================================
# Database Seeding
# =============================================================================

def seed_comprehensive_data():
    """Seed the database with comprehensive example data"""
    with app.app_context():
        # Skip if already seeded
        if Team.query.count() > 0:
            return

        # Demo users (example.com is a reserved domain for testing)
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)

        editor_teams = User(username='editor_teams', email='editor@example.com')
        editor_teams.set_password('editor123')
        db.session.add(editor_teams)

        db.session.flush()

        # Permissions
        db.session.add(EditorPermission(user_id=admin.id, page_slug='*', can_edit=True))
        db.session.add(EditorPermission(user_id=editor_teams.id, page_slug='teams/*', can_edit=True))

        # Teams with detailed descriptions
        teams_data = [
            ('Trainer Team', 'trainer', 'Dedicated volunteers who help new players improve their skills through replay analysis, coaching sessions, and educational content. Request a trainer session on Discord!'),
            ('Promotions Team', 'promotions', 'Manages FAF social media, creates promotional content, and organizes community events to grow the FAF playerbase.'),
            ('FAF Live Team', 'faf-live', 'Professional casters who stream and commentate FAF matches, tournaments, and special events on Twitch and YouTube.'),
            ('Tournament Team', 'tournament', 'Organizes and runs competitive tournaments from weekly events to major championships with prize pools.'),
            ('Matchmaking Team', 'matchmaking', 'Develops and maintains the matchmaking system, ladder pools, and rating algorithms for fair competitive play.'),
            ('Balance Team', 'balance', 'Responsible for game balance patches, unit statistics, and ensuring fair gameplay across all factions.'),
            ('Games Team', 'games', 'Core game development including bug fixes, new features, and maintaining the FAF game patch.'),
            ('Creative Team', 'creative', 'Creates artwork, UI designs, map assets, and other visual content for FAF.'),
            ('Moderation Team', 'moderation', 'Maintains a healthy community by enforcing rules, handling reports, and resolving disputes.'),
            ('DevOps Team', 'devops', 'Keeps FAF infrastructure running - servers, databases, deployments, and technical operations.'),
            ('Campaign Team', 'campaign', 'Develops and maintains the co-op campaign missions and single-player content.'),
        ]

        for i, (name, slug, desc) in enumerate(teams_data):
            team = Team(name=name, slug=slug, description=desc, position=i)
            db.session.add(team)

        db.session.flush()

        # Team members for Trainer Team
        trainer_team = Team.query.filter_by(slug='trainer').first()
        trainers = [
            ('Morax', 'Head Trainer', 'Specializes in economy and macro strategy'),
            ('Tagada', 'Senior Trainer', 'Expert in aggressive play and timing attacks'),
            ('Blackheart', 'Trainer', 'Focuses on air gameplay and micro'),
            ('Blodir', 'Trainer', 'Naval specialist and map awareness'),
            ('Farms', 'Trainer', 'ACU play and early game optimization'),
        ]
        for i, (name, role, desc) in enumerate(trainers):
            member = TeamMember(team_id=trainer_team.id, name=name, role=role, description=desc, position=i)
            db.session.add(member)

        # Replay reviews
        reviews_data = [
            ('1v1 Opening Analysis: UEF vs Cybran', '1v1', 'Dual Gap', 'Morax', '''
<p>This replay showcases excellent early game decision making by the UEF player. Key takeaways:</p>
<ul>
    <li>Factory positioning allowed for better map control</li>
    <li>E/Mass ratio stayed balanced throughout T1 phase</li>
    <li>Scout timing was perfect to anticipate Cybran aggression</li>
</ul>
<p>The critical moment came at 8:30 when UEF correctly identified the Mantis push and pre-positioned tanks.</p>
'''),
            ('Team Game Coordination Guide', '4v4', 'Setons Clutch', 'Tagada', '''
<p>This 4v4 demonstrates proper team coordination and role assignment. Watch for:</p>
<ul>
    <li>Clear naval/air/land split from the start</li>
    <li>Proper eco distribution - front players went aggro, back players teched</li>
    <li>Coordinated experimental timing at 25 minutes</li>
</ul>
'''),
            ('Seraphim T2 Push Timing', '1v1', 'Adaptive Thule', 'Blackheart', '''
<p>Perfect example of the devastating Seraphim T2 push. This replay shows:</p>
<ul>
    <li>Optimal T2 transition at 6:30</li>
    <li>Ilshavoh positioning for maximum raid potential</li>
    <li>ACU upgrade timing to support the push</li>
</ul>
'''),
        ]
        for title, gamemode, map_name, author, content in reviews_data:
            review = ReplayReview(
                title=title,
                content_html=content,
                gamemode=gamemode,
                map_name=map_name,
                author=author,
                published_at=datetime.utcnow() - timedelta(days=len(reviews_data))
            )
            db.session.add(review)

        # Create some pages
        pages_to_create = ['home', 'getting-started', 'rules', 'rules/general-rules', 'rules/vault-rules', 'rules/chat-rules']
        for slug in pages_to_create:
            page = Page(slug=slug, title=slug.split('/')[-1].replace('-', ' ').title())
            db.session.add(page)

        db.session.commit()
        print("Database seeded with comprehensive example data!")


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)

    with app.app_context():
        db.create_all()
        seed_comprehensive_data()

    print(f"\n{'='*60}")
    print(f"  FAForever Wiki")
    print(f"{'='*60}")
    print(f"  Running at: http://localhost:5000{BASE_PATH}/")
    print(f"\n  Demo credentials:")
    print(f"    Admin: admin / admin123")
    print(f"    Teams Editor: editor_teams / editor123")
    print(f"\n  To enable editor mode: login and add ?edit=1 to URL")
    print(f"{'='*60}\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
