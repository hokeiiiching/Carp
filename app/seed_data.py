"""
Seed data module for CARP Application.

Contains comprehensive demo data for showcasing the application.
"""

from datetime import datetime, timedelta, timezone

from app import db
from app.models import User, Participant, Event, Registration


def clear_database():
    """Clear all existing data from database tables."""
    Registration.query.delete()
    Participant.query.delete()
    Event.query.delete()
    User.query.delete()
    db.session.commit()


def create_users():
    """Create demo user accounts."""
    users_data = [
        # Admin accounts
        {"email": "admin@carp.sg", "password": "admin123", "role": "admin"},
        {"email": "staff@carp.sg", "password": "staff123", "role": "admin"},
        # Caregiver accounts
        {"email": "alice.tan@gmail.com", "password": "demo123", "role": "caregiver"},
        {"email": "bob.lee@gmail.com", "password": "demo123", "role": "caregiver"},
        {"email": "clara.wong@gmail.com", "password": "demo123", "role": "caregiver"},
        {"email": "david.chen@hotmail.com", "password": "demo123", "role": "caregiver"},
        {"email": "emma.lim@yahoo.com", "password": "demo123", "role": "caregiver"},
        {"email": "frank.ng@gmail.com", "password": "demo123", "role": "caregiver"},
        {"email": "grace.koh@outlook.com", "password": "demo123", "role": "caregiver"},
        {"email": "henry.goh@gmail.com", "password": "demo123", "role": "caregiver"},
    ]
    
    users = []
    for data in users_data:
        user = User(email=data["email"], role=data["role"])
        user.set_password(data["password"])
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    return users


def create_participants(users):
    """Create participant profiles (seniors) linked to caregivers."""
    caregivers = [u for u in users if u.role == 'caregiver']
    
    participants_data = [
        # Linked to caregivers
        {"nric": "S1234567A", "full_name": "Tan Ah Kow", "caregiver_idx": 0},
        {"nric": "S1234567B", "full_name": "Tan Ah Moi", "caregiver_idx": 0},
        {"nric": "S2345678A", "full_name": "Lee Siew Lian", "caregiver_idx": 1},
        {"nric": "S2345678B", "full_name": "Lee Ah Beng", "caregiver_idx": 1},
        {"nric": "S2345678C", "full_name": "Lee Kim Huat", "caregiver_idx": 1},
        {"nric": "S3456789A", "full_name": "Wong Mei Ling", "caregiver_idx": 2},
        {"nric": "S4567890A", "full_name": "Chen Ah Hua", "caregiver_idx": 3},
        {"nric": "S4567890B", "full_name": "Chen Mei Fong", "caregiver_idx": 3},
        {"nric": "S5678901A", "full_name": "Lim Seng Hock", "caregiver_idx": 4},
        {"nric": "S5678901B", "full_name": "Lim Bee Choo", "caregiver_idx": 4},
        {"nric": "S6789012A", "full_name": "Ng Ah Seng", "caregiver_idx": 5},
        {"nric": "S7890123A", "full_name": "Koh Swee Lan", "caregiver_idx": 6},
        {"nric": "S7890123B", "full_name": "Koh Boon Teck", "caregiver_idx": 6},
        {"nric": "S8901234A", "full_name": "Goh Kim Cheng", "caregiver_idx": 7},
        # Shadow profiles (walk-ins)
        {"nric": "S9012345A", "full_name": "Ong Chee Keong", "caregiver_idx": None},
        {"nric": "S9012345B", "full_name": "Teo Siew Eng", "caregiver_idx": None},
        {"nric": "S9012345C", "full_name": "Yeo Ah Lian", "caregiver_idx": None},
        {"nric": "S9012345D", "full_name": "Chua Beng Huat", "caregiver_idx": None},
        {"nric": "S9012345E", "full_name": "Sim Mei Yee", "caregiver_idx": None},
        {"nric": "S9012345F", "full_name": "Ho Ah Meng", "caregiver_idx": None},
    ]
    
    participants = []
    for data in participants_data:
        user_id = None
        if data["caregiver_idx"] is not None:
            user_id = caregivers[data["caregiver_idx"]].id
        
        participant = Participant(
            nric=data["nric"],
            full_name=data["full_name"],
            user_id=user_id
        )
        db.session.add(participant)
        participants.append(participant)
    
    db.session.commit()
    return participants


def create_events():
    """Create diverse demo events."""
    now = datetime.now(timezone.utc)
    
    events_data = [
        # Past events
        {
            "title": "Healthy Cooking Workshop",
            "description": "Learn to prepare nutritious meals suitable for seniors. Our chef instructor will demonstrate simple yet delicious recipes focusing on low-sodium and heart-healthy cooking techniques. Ingredients and recipe booklets will be provided.",
            "max_capacity": 15,
            "start_time": now - timedelta(days=14)
        },
        {
            "title": "Tai Chi for Beginners",
            "description": "An introduction to the ancient art of Tai Chi. This gentle exercise is perfect for improving balance, flexibility, and mental clarity. No prior experience required. Wear comfortable clothing and flat shoes.",
            "max_capacity": 20,
            "start_time": now - timedelta(days=7)
        },
        # Upcoming events
        {
            "title": "Morning Yoga Session",
            "description": "Start your day right with gentle yoga stretches designed for seniors. Improve flexibility, reduce stress, and enhance overall well-being. Yoga mats will be provided. Suitable for all fitness levels.",
            "max_capacity": 12,
            "start_time": now + timedelta(days=2, hours=9)
        },
        {
            "title": "Digital Photography Basics",
            "description": "Learn how to take beautiful photos using your smartphone. This hands-on workshop covers camera settings, composition tips, and basic photo editing. Bring your own smartphone.",
            "max_capacity": 10,
            "start_time": now + timedelta(days=3, hours=14)
        },
        {
            "title": "Line Dancing Class",
            "description": "Get moving with fun line dancing! No partner needed. Learn popular dance routines to classic and contemporary hits. Great for exercise and socializing. All skill levels welcome.",
            "max_capacity": 25,
            "start_time": now + timedelta(days=4, hours=10)
        },
        {
            "title": "Calligraphy Workshop",
            "description": "Discover the beauty of Chinese calligraphy. Learn basic brush strokes and create your own artwork. All materials including brushes, ink, and rice paper will be provided.",
            "max_capacity": 15,
            "start_time": now + timedelta(days=5, hours=14)
        },
        {
            "title": "Health Talk: Managing Diabetes",
            "description": "Join our healthcare professional for an informative session on diabetes management. Topics include diet tips, medication adherence, foot care, and recognizing warning signs. Q&A session included.",
            "max_capacity": 50,
            "start_time": now + timedelta(days=6, hours=10)
        },
        {
            "title": "Potluck Gathering",
            "description": "Bring your favorite dish and share a meal with fellow community members. A wonderful opportunity to socialize, exchange recipes, and make new friends. Tea and coffee provided.",
            "max_capacity": 30,
            "start_time": now + timedelta(days=7, hours=12)
        },
        {
            "title": "Garden Walk at Botanic Gardens",
            "description": "Enjoy a leisurely guided walk through the beautiful Singapore Botanic Gardens. Learn about local flora and enjoy the fresh air. Meeting point at Tanglin Gate. Wear comfortable walking shoes.",
            "max_capacity": 20,
            "start_time": now + timedelta(days=8, hours=8)
        },
        {
            "title": "Smartphone Basics Class",
            "description": "Learn essential smartphone skills including making calls, sending messages, using WhatsApp, video calling family, and online safety tips. Patient instructors will guide you step by step.",
            "max_capacity": 10,
            "start_time": now + timedelta(days=9, hours=14)
        },
        {
            "title": "Mahjong Social",
            "description": "Join fellow enthusiasts for a friendly mahjong session. Tables and tiles provided. Beginners welcome - experienced players are happy to teach! Light refreshments included.",
            "max_capacity": 16,
            "start_time": now + timedelta(days=10, hours=14)
        },
        {
            "title": "Art Therapy Session",
            "description": "Express yourself through art in a relaxing environment. No artistic experience needed. Our certified art therapist will guide you through various creative exercises. All materials provided.",
            "max_capacity": 12,
            "start_time": now + timedelta(days=12, hours=10)
        },
        {
            "title": "Singing Together: Oldies",
            "description": "Sing along to beloved oldies from the 60s, 70s, and 80s. Song sheets provided with lyrics in English and Chinese. A joyful way to exercise your voice and memory!",
            "max_capacity": 40,
            "start_time": now + timedelta(days=14, hours=15)
        },
        {
            "title": "Chair Exercises",
            "description": "Low-impact exercises performed while seated. Perfect for those with mobility limitations. Improve strength, flexibility, and circulation. Led by a certified fitness instructor.",
            "max_capacity": 20,
            "start_time": now + timedelta(days=15, hours=10)
        },
        {
            "title": "Movie Afternoon: Classic Films",
            "description": "Enjoy a classic film on the big screen with fellow movie lovers. Popcorn and drinks provided. This month's feature: a beloved Cantonese classic with English subtitles.",
            "max_capacity": 35,
            "start_time": now + timedelta(days=17, hours=14)
        },
        # Future events
        {
            "title": "CNY Craft Workshop",
            "description": "Create beautiful Chinese New Year decorations including red packets, paper lanterns, and paper cutting art. Take home your festive creations. All materials provided.",
            "max_capacity": 20,
            "start_time": now + timedelta(days=25, hours=14)
        },
        {
            "title": "Cooking Demo: Festive Dishes",
            "description": "Watch our chef prepare traditional festive dishes and learn tips for your own celebration cooking. Tasting samples included. Recipe cards will be distributed.",
            "max_capacity": 25,
            "start_time": now + timedelta(days=28, hours=11)
        },
        {
            "title": "Bingo Night",
            "description": "An evening of fun and excitement! Win attractive prizes in our friendly bingo competition. Light dinner and refreshments included. Bring your lucky charm!",
            "max_capacity": 40,
            "start_time": now + timedelta(days=30, hours=18)
        },
    ]
    
    events = []
    for data in events_data:
        event = Event(
            title=data["title"],
            description=data["description"],
            max_capacity=data["max_capacity"],
            start_time=data["start_time"]
        )
        db.session.add(event)
        events.append(event)
    
    db.session.commit()
    return events


def create_registrations(events, participants):
    """Create realistic registration patterns."""
    registration_patterns = [
        (0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], ['online']*10 + ['walkin']*5),
        (1, [0, 2, 4, 6, 8, 10, 12, 14, 15, 16, 17, 18], ['online']*8 + ['walkin']*4),
        (2, [1, 3, 5, 7, 9, 11, 13, 15, 17, 19], ['online']*8 + ['walkin']*2),
        (3, [0, 4, 8, 12, 16], ['online']*5),
        (4, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], ['online']*15 + ['walkin']*5),
        (5, [1, 3, 5, 7, 9, 11, 13], ['online']*7),
        (6, list(range(20)), ['online']*12 + ['walkin']*8),
        (7, [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 6, 7], ['online']*15 + ['walkin']*3),
        (8, list(range(20)), ['online']*18 + ['walkin']*2),
        (9, [0, 2, 4, 6, 8, 10, 12, 14, 16, 18], ['online']*10),
        (10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17], ['online']*12 + ['walkin']*4),
        (11, [1, 3, 5, 7, 9, 11, 15, 17], ['online']*8),
        (12, list(range(0, 20)) + [14, 15, 16, 17, 18], ['online']*20 + ['walkin']*5),
        (13, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17, 18], ['online']*12 + ['walkin']*3),
        (14, list(range(20)), ['online']*15 + ['walkin']*5),
        (15, [1, 3, 5, 7, 9], ['online']*5),
        (16, [0, 2, 4], ['online']*3),
        (17, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], ['online']*10),
    ]
    
    total_registrations = 0
    for event_idx, participant_indices, sources in registration_patterns:
        event = events[event_idx]
        valid_indices = [i for i in participant_indices if i < len(participants)]
        
        for i, p_idx in enumerate(valid_indices):
            source = sources[i] if i < len(sources) else 'online'
            time_offset = timedelta(days=-(i % 7), hours=-(i * 2 % 24), minutes=-(i * 17 % 60))
            
            registration = Registration(
                event_id=event.id,
                participant_id=participants[p_idx].id,
                source=source,
                timestamp=datetime.now(timezone.utc) + time_offset
            )
            db.session.add(registration)
            total_registrations += 1
    
    db.session.commit()
    return total_registrations


def seed_database():
    """
    Main function to seed the database with comprehensive demo data.
    
    Returns:
        Dictionary with summary of seeded data
    """
    # Clear existing data
    clear_database()
    
    # Create all demo data
    users = create_users()
    participants = create_participants(users)
    events = create_events()
    total_registrations = create_registrations(events, participants)
    
    # Build summary
    summary = {
        'users': {
            'total': len(users),
            'admins': len([u for u in users if u.role == 'admin']),
            'caregivers': len([u for u in users if u.role == 'caregiver'])
        },
        'participants': {
            'total': len(participants),
            'linked': len([p for p in participants if p.user_id is not None]),
            'shadow': len([p for p in participants if p.user_id is None])
        },
        'events': len(events),
        'registrations': total_registrations,
        'demo_credentials': {
            'admin': {'email': 'admin@carp.sg', 'password': 'admin123'},
            'caregiver': {'email': 'alice.tan@gmail.com', 'password': 'demo123'}
        }
    }
    
    return summary
