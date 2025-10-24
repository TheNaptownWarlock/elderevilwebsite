# Elder Evil Website Project Overview

## Project Description
A fantasy convention (BenCon) event management and social platform combining a Streamlit web app for event management with a static website for content display. Features include real-time chat, event scheduling, and various fantasy-themed content sections.

## Key Components

### Core Applications
1. **Streamlit App** (`app.py`)
   - Event management and scheduling
   - Real-time tavern chat
   - User authentication and profiles
   - Event RSVP system
   - Private messaging

2. **Static Website** (`index.html`, etc.)
   - Content display for various sections
   - Product showcases
   - Blog system
   - Fantasy calendar integration

### Database (Supabase)
- User management
- Event scheduling
- Chat system
- RSVP tracking
- Private messages
- Real-time updates via websockets

### Key Files

#### Backend & Data
- `app.py` - Main Streamlit application
- `realtime_chat.py` - Websocket-based tavern chat component
- `supabase_integration.py` - Database interaction layer
- `cloud_database.py` - Cloud database utilities
- `fantasy_calendar_db.py` - Fantasy calendar functionality
- `hybrid_database.py` - Local/cloud database hybrid system

#### Frontend
- `index.html` - Main website
- `blog-template.html` - Blog post template
- `fantasy-calendar.html` - Fantasy calendar interface
- `assets/` - Static assets (images, CSS, JS)
  - `css/` - Stylesheets
  - `js/` - JavaScript files
  - `images/` - Image assets
  - `audio/` - Audio files

#### Configuration
- `secrets.toml` - Configuration secrets (Supabase credentials)
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel deployment configuration

#### Database Setup
- `create_supabase_tables.py` - Database initialization
- `setup_supabase.py` - Supabase configuration
- `supabase_tables.sql` - Table definitions
- `supabase_setup.sql` - Database setup SQL

### Key Features

#### Event Management
- Event creation and editing
- RSVP system
- Seat management
- Schedule viewing
- Event tags and categories

#### Tavern Chat System
- Real-time messaging
- Websocket-based updates
- User avatars and roles
- Message persistence
- Emoji support

#### User System
- Authentication
- Profile management
- Avatar selection
- Private messaging
- Event hosting capabilities

#### Content Sections
1. **Boozin'**
   - BlackTalon
   - Cider
   - FirstMead
   - Hush
   - WineLineup

2. **Food**
   - Elder Evil Coffee
   - Necro-NOM-icon
   - The Elder Cow

3. **Merchandise**
   - Glasses
   - Hexproof items

4. **Art & Crafts**
   - Clay creations
   - Various themed collections

### Technical Stack
- **Frontend**: HTML, CSS, JavaScript, Streamlit
- **Backend**: Python, Streamlit
- **Database**: Supabase (PostgreSQL)
- **Real-time**: Supabase Realtime (websockets)
- **Hosting**: Vercel (static site), Streamlit Cloud (app)

### Deployment
- Static site deployed on Vercel
- Streamlit app hosted on Streamlit Cloud
- Supabase for database and real-time features
- Configured with deployment guides and checklists

## Development Guidelines

### Local Development
1. Activate virtual environment: `.venv\Scripts\activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Supabase credentials in `secrets.toml`
4. Run Streamlit app: `streamlit run app.py`

### Database Updates
1. Use `create_supabase_tables.py` for schema changes
2. Update `supabase_tables.sql` for table definitions
3. Test locally before deploying

### Content Updates
1. Add new content to appropriate asset folders
2. Update HTML templates as needed
3. Follow established naming conventions
4. Use provided guides for blog posts and portfolios

## Future Enhancements
1. Enhanced real-time features
2. Advanced event management
3. Improved user profiles
4. Extended fantasy calendar integration
5. Additional content sections

## Project Structure
```
elderevilwebsite/
├── app.py                     # Main Streamlit application
├── realtime_chat.py          # Real-time chat component
├── index.html                # Main website
├── assets/                   # Static assets
│   ├── css/
│   ├── js/
│   ├── images/
│   └── audio/
├── blog-posts/              # Blog content
├── database/               # Database related files
└── docs/                  # Documentation
```