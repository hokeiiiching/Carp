"""
Comprehensive Database Seed Script for CARP Application.

This script populates the database with realistic demo data for showcasing
the Centralized Activity Registration Platform (CARP).

Usage:
    # For local development (uses .env.local or environment variables)
    python seed_database.py

    # For production (set POSTGRES_URL environment variable first)
    POSTGRES_URL=your_connection_string python seed_database.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Load environment variables from .env.local if it exists
from pathlib import Path
env_file = Path(__file__).parent / '.env.local'
if env_file.exists():
    print(f"📁 Loading environment from .env.local")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())
else:
    print("⚠️  No .env.local found, using existing environment variables")

from app import create_app, db
from app.models import User, Participant, Event, Registration


def clear_database():
    """Clear all existing data from database tables."""
    print("🗑️  Clearing existing data...")
    Registration.query.delete()
    Participant.query.delete()
    Event.query.delete()
    User.query.delete()
    db.session.commit()
    print("   ✓ Database cleared")


def create_users():
    """Create demo user accounts."""
    print("\n👥 Creating user accounts...")
    
    users_data = [
        # Admin accounts
        {
            "email": "admin@carp.sg",
            "password": "admin123",
            "role": "admin"
        },
        {
            "email": "staff@carp.sg", 
            "password": "staff123",
            "role": "admin"
        },
        # Caregiver accounts (family members who register seniors)
        {
            "email": "alice.tan@gmail.com",
            "password": "demo123",
            "role": "caregiver"
        },
        {
            "email": "bob.lee@gmail.com",
            "password": "demo123",
            "role": "caregiver"
        },
        {
            "email": "clara.wong@gmail.com",
            "password": "demo123",
            "role": "caregiver"
        },
        {
            "email": "david.chen@hotmail.com",
            "password": "demo123",
            "role": "caregiver"
        },
        {
            "email": "emma.lim@yahoo.com",
            "password": "demo123",
            "role": "caregiver"
        },
        {
            "email": "frank.ng@gmail.com",
            "password": "demo123",
            "role": "caregiver"
        },
        {
            "email": "grace.koh@outlook.com",
            "password": "demo123",
            "role": "caregiver"
        },
        {
            "email": "henry.goh@gmail.com",
            "password": "demo123",
            "role": "caregiver"
        },
    ]
    
    users = []
    for data in users_data:
        user = User(email=data["email"], role=data["role"])
        user.set_password(data["password"])
        db.session.add(user)
        users.append(user)
        print(f"   ✓ Created user: {data['email']} ({data['role']})")
    
    db.session.commit()
    return users


def create_participants(users):
    """Create participant profiles (seniors) linked to caregivers."""
    print("\n👴 Creating participant profiles...")
    
    # Get caregiver users (skip first 2 admin accounts)
    caregivers = [u for u in users if u.role == 'caregiver']
    
    participants_data = [
        # Participants linked to Alice Tan (caregiver index 0)
        {"nric": "S1234567A", "full_name": "Tan Ah Kow", "caregiver_idx": 0},
        {"nric": "S1234567B", "full_name": "Tan Ah Moi", "caregiver_idx": 0},
        
        # Participants linked to Bob Lee (caregiver index 1)
        {"nric": "S2345678A", "full_name": "Lee Siew Lian", "caregiver_idx": 1},
        {"nric": "S2345678B", "full_name": "Lee Ah Beng", "caregiver_idx": 1},
        {"nric": "S2345678C", "full_name": "Lee Kim Huat", "caregiver_idx": 1},
        
        # Participants linked to Clara Wong (caregiver index 2)
        {"nric": "S3456789A", "full_name": "Wong Mei Ling", "caregiver_idx": 2},
        
        # Participants linked to David Chen (caregiver index 3)
        {"nric": "S4567890A", "full_name": "Chen Ah Hua", "caregiver_idx": 3},
        {"nric": "S4567890B", "full_name": "Chen Mei Fong", "caregiver_idx": 3},
        
        # Participants linked to Emma Lim (caregiver index 4)
        {"nric": "S5678901A", "full_name": "Lim Seng Hock", "caregiver_idx": 4},
        {"nric": "S5678901B", "full_name": "Lim Bee Choo", "caregiver_idx": 4},
        
        # Participants linked to Frank Ng (caregiver index 5)
        {"nric": "S6789012A", "full_name": "Ng Ah Seng", "caregiver_idx": 5},
        
        # Participants linked to Grace Koh (caregiver index 6)
        {"nric": "S7890123A", "full_name": "Koh Swee Lan", "caregiver_idx": 6},
        {"nric": "S7890123B", "full_name": "Koh Boon Teck", "caregiver_idx": 6},
        
        # Participants linked to Henry Goh (caregiver index 7)
        {"nric": "S8901234A", "full_name": "Goh Kim Cheng", "caregiver_idx": 7},
        
        # Shadow profiles (walk-ins without linked caregiver)
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
        
        link_info = f"→ {caregivers[data['caregiver_idx']].email}" if data["caregiver_idx"] is not None else "(walk-in)"
        print(f"   ✓ Created: {data['full_name']} ({data['nric']}) {link_info}")
    
    db.session.commit()
    return participants


def create_events():
    """Create diverse demo events."""
    print("\n📅 Creating events...")
    
    # Base time for events (use current time as reference)
    now = datetime.now(timezone.utc)
    
    events_data = [
        # Past events (already completed)
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
        
        # Upcoming events (happening soon)
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
        
        # Future events (next month)
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
        
        # Format date for display
        local_time = data["start_time"].strftime("%Y-%m-%d %H:%M")
        print(f"   ✓ Created: {data['title']} (capacity: {data['max_capacity']}, date: {local_time})")
    
    db.session.commit()
    return events


def create_registrations(events, participants):
    """Create realistic registration patterns."""
    print("\n📝 Creating registrations...")
    
    # Registration patterns: (event_index, participant_indices, sources)
    registration_patterns = [
        # Past event: Healthy Cooking Workshop (fully booked)
        (0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], 
         ['online']*10 + ['walkin']*5),
        
        # Past event: Tai Chi for Beginners (partially filled)
        (1, [0, 2, 4, 6, 8, 10, 12, 14, 15, 16, 17, 18], 
         ['online']*8 + ['walkin']*4),
        
        # Upcoming: Morning Yoga Session (almost full - 10/12)
        (2, [1, 3, 5, 7, 9, 11, 13, 15, 17, 19], 
         ['online']*8 + ['walkin']*2),
        
        # Upcoming: Digital Photography Basics (half filled - 5/10)
        (3, [0, 4, 8, 12, 16], 
         ['online']*5),
        
        # Upcoming: Line Dancing Class (popular - 20/25)
        (4, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 
         ['online']*15 + ['walkin']*5),
        
        # Upcoming: Calligraphy Workshop (7/15)
        (5, [1, 3, 5, 7, 9, 11, 13], 
         ['online']*7),
        
        # Upcoming: Health Talk (well attended - 35/50)
        (6, list(range(20)), 
         ['online']*12 + ['walkin']*8),
        
        # Upcoming: Potluck Gathering (good signup - 18/30)
        (7, [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 6, 7], 
         ['online']*15 + ['walkin']*3),
        
        # Upcoming: Garden Walk (full - 20/20)
        (8, list(range(20)), 
         ['online']*18 + ['walkin']*2),
        
        # Upcoming: Smartphone Basics (full - 10/10)
        (9, [0, 2, 4, 6, 8, 10, 12, 14, 16, 18], 
         ['online']*10),
        
        # Upcoming: Mahjong Social (exactly 16/16 = 4 tables)
        (10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17], 
         ['online']*12 + ['walkin']*4),
        
        # Upcoming: Art Therapy Session (8/12)
        (11, [1, 3, 5, 7, 9, 11, 15, 17], 
         ['online']*8),
        
        # Upcoming: Singing Together (25/40)
        (12, list(range(0, 20)) + [14, 15, 16, 17, 18], 
         ['online']*20 + ['walkin']*5),
        
        # Upcoming: Chair Exercises (15/20)
        (13, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17, 18], 
         ['online']*12 + ['walkin']*3),
        
        # Upcoming: Movie Afternoon (28/35)
        (14, list(range(20)) + [0, 1, 2, 3, 4, 5, 6, 7][:8], 
         ['online']*20 + ['walkin']*8),
        
        # Future: CNY Craft Workshop (5/20 - just started accepting)
        (15, [1, 3, 5, 7, 9], 
         ['online']*5),
        
        # Future: Cooking Demo (3/25 - early registrations)
        (16, [0, 2, 4], 
         ['online']*3),
        
        # Future: Bingo Night (10/40 - early bird signups)
        (17, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 
         ['online']*10),
    ]
    
    total_registrations = 0
    for event_idx, participant_indices, sources in registration_patterns:
        event = events[event_idx]
        
        # Limit to actual number of participants and sources
        valid_indices = [i for i in participant_indices if i < len(participants)]
        
        for i, p_idx in enumerate(valid_indices):
            if i >= len(sources):
                source = 'online'
            else:
                source = sources[i]
            
            # Vary timestamps to make data look realistic
            time_offset = timedelta(
                days=-(i % 7),
                hours=-(i * 2 % 24),
                minutes=-(i * 17 % 60)
            )
            
            registration = Registration(
                event_id=event.id,
                participant_id=participants[p_idx].id,
                source=source,
                timestamp=datetime.now(timezone.utc) + time_offset
            )
            db.session.add(registration)
            total_registrations += 1
        
        registered = len(valid_indices)
        print(f"   ✓ {event.title}: {registered}/{event.max_capacity} registrations")
    
    db.session.commit()
    print(f"\n   Total registrations created: {total_registrations}")


def print_summary(users, participants, events):
    """Print a summary of seeded data."""
    print("\n" + "="*60)
    print("📊 SEED DATA SUMMARY")
    print("="*60)
    
    print(f"\n👥 Users: {len(users)} total")
    admins = [u for u in users if u.role == 'admin']
    caregivers = [u for u in users if u.role == 'caregiver']
    print(f"   • Admins: {len(admins)}")
    print(f"   • Caregivers: {len(caregivers)}")
    
    print(f"\n👴 Participants: {len(participants)} total")
    linked = [p for p in participants if p.user_id is not None]
    shadow = [p for p in participants if p.user_id is None]
    print(f"   • Linked to caregivers: {len(linked)}")
    print(f"   • Shadow profiles (walk-ins): {len(shadow)}")
    
    print(f"\n📅 Events: {len(events)} total")
    
    total_regs = Registration.query.count()
    print(f"\n📝 Registrations: {total_regs} total")
    
    print("\n" + "="*60)
    print("🔐 DEMO LOGIN CREDENTIALS")
    print("="*60)
    print("\n   Admin Account:")
    print("   • Email: admin@carp.sg")
    print("   • Password: admin123")
    print("\n   Caregiver Account (for testing):")
    print("   • Email: alice.tan@gmail.com")
    print("   • Password: demo123")
    print("="*60)


def main():
    """Main entry point for seeding the database."""
    print("="*60)
    print("🌱 CARP DATABASE SEEDING SCRIPT")
    print("="*60)
    
    app = create_app()
    
    with app.app_context():
        print(f"\n🔗 Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
        
        # Confirm before clearing existing data
        if os.environ.get('SKIP_CONFIRMATION') != 'true':
            response = input("\n⚠️  This will clear all existing data. Continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Aborted.")
                sys.exit(0)
        
        try:
            # Seed the database
            clear_database()
            users = create_users()
            participants = create_participants(users)
            events = create_events()
            create_registrations(events, participants)
            
            # Print summary
            print_summary(users, participants, events)
            
            print("\n✅ Database seeding completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    main()
