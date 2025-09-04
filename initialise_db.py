#!/usr/bin/env python3
"""
EasyFlix Database Initialization Script
Creates and populates the EasyFlix database with encryption and security.
"""

import sqlite3
import hashlib
import secrets
import asyncio
from datetime import datetime, date
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.widgets import Header, Footer, Static, ProgressBar, Label
from textual.reactive import reactive
import time

class DatabaseInitializer:
    def __init__(self, db_path="easyflix.db", password="E@syFl1xP@ss"):
        self.db_path = db_path
        self.password = password
        self.authorized_user = "EFAPI"
        
    def _create_connection(self):
        """Create encrypted database connection"""
        conn = sqlite3.connect(self.db_path)
        # Enable encryption with password
        conn.execute(f"PRAGMA key = '{self.password}'")
        # Set authorized user
        conn.execute(f"PRAGMA user = '{self.authorized_user}'")
        return conn
    
    def create_tables(self):
        """Create all database tables"""
        conn = self._create_connection()
        cursor = conn.cursor()
        
        # CUSTOMERS table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CUSTOMERS (
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username VARCHAR(50) UNIQUE NOT NULL,
            Email VARCHAR(100) UNIQUE NOT NULL,
            Password_Hash VARCHAR(64) NOT NULL,
            Salt VARCHAR(32) NOT NULL,
            Subscription_Level VARCHAR(20) NOT NULL CHECK (Subscription_Level IN ('Basic', 'Premium')),
            Shows TEXT,
            Rentals TEXT,
            Total_Spent DECIMAL(10,2) DEFAULT 0.00,
            Favourite_Genre VARCHAR(30)
        )
        ''')
        
        # SHOWS table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS SHOWS (
            Show_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name VARCHAR(100) NOT NULL,
            Release_Date DATE NOT NULL,
            Rating VARCHAR(10) NOT NULL,
            Director VARCHAR(100) NOT NULL,
            Length INTEGER NOT NULL,
            Genre VARCHAR(30) NOT NULL,
            Access_Group VARCHAR(20) NOT NULL CHECK (Access_Group IN ('Basic', 'Premium')),
            Cost_To_Rent DECIMAL(5,2) NOT NULL
        )
        ''')
        
        # RENTALS table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS RENTALS (
            Rental_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            User_ID INTEGER NOT NULL,
            Show_ID INTEGER NOT NULL,
            Rental_Date DATE NOT NULL,
            Return_Date DATE,
            Expired BOOLEAN DEFAULT FALSE,
            Cost DECIMAL(5,2) NOT NULL,
            FOREIGN KEY (User_ID) REFERENCES CUSTOMERS(User_ID),
            FOREIGN KEY (Show_ID) REFERENCES SHOWS(Show_ID)
        )
        ''')
        
        # STATISTICS table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS STATISTICS (
            Date DATE PRIMARY KEY,
            Total_Shows_Rented INTEGER DEFAULT 0,
            Total_Subscriptions INTEGER DEFAULT 0,
            Total_Users INTEGER DEFAULT 0,
            Last_Updated DATETIME NOT NULL
        )
        ''')
        
        # FINANCIALS table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS FINANCIALS (
            Date DATE PRIMARY KEY,
            Total_Revenue_Rent DECIMAL(10,2) DEFAULT 0.00,
            Total_Revenue_Subscriptions DECIMAL(10,2) DEFAULT 0.00,
            Total_Combined_Revenue DECIMAL(10,2) DEFAULT 0.00,
            Last_Updated DATETIME NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_shows(self):
        """Populate shows table with diverse content"""
        shows_data = [
            # Premium Movies
            ("The Matrix", "1999-03-31", "M", "Lana Wachowski", 136, "Sci-Fi", "Premium", 6.99),
            ("Inception", "2010-07-16", "M", "Christopher Nolan", 148, "Sci-Fi", "Premium", 7.99),
            ("The Dark Knight", "2008-07-18", "M", "Christopher Nolan", 152, "Action", "Premium", 7.99),
            ("Pulp Fiction", "1994-10-14", "MA15+", "Quentin Tarantino", 154, "Crime", "Premium", 6.99),
            ("The Godfather", "1972-03-24", "MA15+", "Francis Ford Coppola", 175, "Crime", "Premium", 8.99),
            ("Schindler's List", "1993-02-04", "MA15+", "Steven Spielberg", 195, "Drama", "Premium", 7.99),
            ("Goodfellas", "1990-09-21", "MA15+", "Martin Scorsese", 146, "Crime", "Premium", 6.99),
            ("The Shawshank Redemption", "1994-09-23", "MA15+", "Frank Darabont", 142, "Drama", "Premium", 8.99),
            ("Fight Club", "1999-10-15", "MA15+", "David Fincher", 139, "Drama", "Premium", 7.99),
            ("Interstellar", "2014-11-07", "M", "Christopher Nolan", 169, "Sci-Fi", "Premium", 8.99),
            ("Blade Runner 2049", "2017-10-06", "M", "Denis Villeneuve", 164, "Sci-Fi", "Premium", 7.99),
            ("Mad Max: Fury Road", "2015-05-15", "MA15+", "George Miller", 120, "Action", "Premium", 6.99),
            ("John Wick", "2014-10-24", "MA15+", "Chad Stahelski", 101, "Action", "Premium", 5.99),
            ("The Wolf of Wall Street", "2013-12-25", "MA15+", "Martin Scorsese", 180, "Biography", "Premium", 7.99),
            ("Parasite", "2019-05-30", "MA15+", "Bong Joon-ho", 132, "Thriller", "Premium", 7.99),
            
            # Basic Movies
            ("Forrest Gump", "1994-07-06", "M", "Robert Zemeckis", 142, "Drama", "Basic", 4.99),
            ("The Lion King", "1994-06-24", "G", "Roger Allers", 88, "Animation", "Basic", 3.99),
            ("Toy Story", "1995-11-22", "G", "John Lasseter", 81, "Animation", "Basic", 3.99),
            ("Finding Nemo", "2003-05-30", "G", "Andrew Stanton", 100, "Animation", "Basic", 3.99),
            ("Shrek", "2001-05-18", "PG", "Andrew Adamson", 90, "Animation", "Basic", 3.99),
            ("The Incredibles", "2004-11-05", "PG", "Brad Bird", 115, "Animation", "Basic", 4.99),
            ("Up", "2009-05-29", "PG", "Pete Docter", 96, "Animation", "Basic", 4.99),
            ("Wall-E", "2008-06-27", "G", "Andrew Stanton", 98, "Animation", "Basic", 4.99),
            ("Moana", "2016-11-23", "PG", "Ron Clements", 107, "Animation", "Basic", 4.99),
            ("Frozen", "2013-11-27", "PG", "Chris Buck", 102, "Animation", "Basic", 4.99),
            ("Spider-Man: Into the Spider-Verse", "2018-12-14", "PG", "Bob Persichetti", 117, "Animation", "Basic", 5.99),
            ("The Avengers", "2012-05-04", "M", "Joss Whedon", 143, "Action", "Basic", 5.99),
            ("Guardians of the Galaxy", "2014-08-01", "M", "James Gunn", 121, "Action", "Basic", 5.99),
            ("Iron Man", "2008-05-02", "M", "Jon Favreau", 126, "Action", "Basic", 5.99),
            ("Captain America: The Winter Soldier", "2014-04-04", "M", "Anthony Russo", 136, "Action", "Basic", 5.99),
            
            # Premium TV Shows
            ("Breaking Bad", "2008-01-20", "MA15+", "Vince Gilligan", 47, "Crime", "Premium", 8.99),
            ("Game of Thrones", "2011-04-17", "MA15+", "David Benioff", 57, "Fantasy", "Premium", 9.99),
            ("The Sopranos", "1999-01-10", "MA15+", "David Chase", 55, "Crime", "Premium", 8.99),
            ("The Wire", "2002-06-02", "MA15+", "David Simon", 60, "Crime", "Premium", 8.99),
            ("Better Call Saul", "2015-02-08", "MA15+", "Vince Gilligan", 47, "Crime", "Premium", 7.99),
            ("Westworld", "2016-10-02", "MA15+", "Jonathan Nolan", 62, "Sci-Fi", "Premium", 8.99),
            ("House of Cards", "2013-02-01", "MA15+", "Beau Willimon", 51, "Political", "Premium", 7.99),
            ("Stranger Things", "2016-07-15", "M", "The Duffer Brothers", 51, "Sci-Fi", "Premium", 7.99),
            ("The Crown", "2016-11-04", "M", "Peter Morgan", 58, "Biography", "Premium", 7.99),
            ("Ozark", "2017-07-21", "MA15+", "Bill Dubuque", 60, "Crime", "Premium", 7.99),
            
            # Basic TV Shows
            ("Friends", "1994-09-22", "PG", "David Crane", 22, "Comedy", "Basic", 3.99),
            ("The Office", "2005-03-24", "PG", "Greg Daniels", 22, "Comedy", "Basic", 3.99),
            ("Parks and Recreation", "2009-04-09", "PG", "Greg Daniels", 22, "Comedy", "Basic", 3.99),
            ("Brooklyn Nine-Nine", "2013-09-17", "M", "Dan Goor", 22, "Comedy", "Basic", 3.99),
            ("How I Met Your Mother", "2005-09-19", "M", "Carter Bays", 22, "Comedy", "Basic", 3.99),
            ("The Big Bang Theory", "2007-09-24", "PG", "Chuck Lorre", 22, "Comedy", "Basic", 3.99),
            ("Modern Family", "2009-09-23", "PG", "Christopher Lloyd", 22, "Comedy", "Basic", 3.99),
            ("Seinfeld", "1989-07-05", "PG", "Larry David", 22, "Comedy", "Basic", 4.99),
            ("The Simpsons", "1989-12-17", "PG", "Matt Groening", 22, "Animation", "Basic", 3.99),
            ("Avatar: The Last Airbender", "2005-02-21", "PG", "Michael Dante DiMartino", 23, "Animation", "Basic", 4.99)
        ]
        
        conn = self._create_connection()
        cursor = conn.cursor()
        
        cursor.executemany('''
        INSERT OR IGNORE INTO SHOWS 
        (Name, Release_Date, Rating, Director, Length, Genre, Access_Group, Cost_To_Rent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', shows_data)
        
        conn.commit()
        conn.close()
    
    def initialize_stats_and_financials(self):
        """Initialize statistics and financials with today's date"""
        today = date.today()
        now = datetime.now()
        
        conn = self._create_connection()
        cursor = conn.cursor()
        
        # Initialize statistics
        cursor.execute('''
        INSERT OR REPLACE INTO STATISTICS 
        (Date, Total_Shows_Rented, Total_Subscriptions, Total_Users, Last_Updated)
        VALUES (?, 0, 0, 0, ?)
        ''', (today, now))
        
        # Initialize financials
        cursor.execute('''
        INSERT OR REPLACE INTO FINANCIALS 
        (Date, Total_Revenue_Rent, Total_Revenue_Subscriptions, Total_Combined_Revenue, Last_Updated)
        VALUES (?, 0.00, 0.00, 0.00, ?)
        ''', (today, now))
        
        conn.commit()
        conn.close()

class LoadingSpinner(Static):
    """Animated loading spinner widget""" 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.current_frame = 0
        self.update_timer = None
    
    def on_mount(self):
        self.update_timer = self.set_interval(0.1, self.update_spinner)
    
    def update_spinner(self):
        self.current_frame = (self.current_frame + 1) % len(self.spinner_chars)
        self.update(f"[bold cyan]{self.spinner_chars[self.current_frame]}[/bold cyan]")

class DatabaseInitApp(App):
    """EasyFlix Database Initialization Application"""
    
    CSS = """
    Screen {
        background: #0f1419;
    }
    
    Header {
        background: #1a1a2e;
        color: #e94560;
        text-style: bold;
    }
    
    Footer {
        background: #16213e;
        color: #0f3460;
    }
    
    .container {
        background: #16213e;
        border: solid #e94560;
        border-title-color: #f5f5f5;
        padding: 2;
        margin: 2;
    }
    
    .status {
        color: #f39c12;
        text-style: bold;
        padding: 1;
    }
    
    .success {
        color: #27ae60;
        text-style: bold;
    }
    
    .loading {
        color: #3498db;
        text-style: bold;
    }
    
    ProgressBar {
        bar-color: #e94560;
        background-color: #1a1a2e;
    }
    """
    
    progress = reactive(0)
    status_text = reactive("Initializing EasyFlix Database...")
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Center():
            with Middle():
                with Vertical(classes="container"):
                    yield Static("[bold]🎬 EasyFlix Database Initializer[/bold]", classes="status")
                    yield Static("", id="spinner_container")
                    yield LoadingSpinner(id="spinner")
                    yield Static(self.status_text, id="status")
                    yield ProgressBar(total=100, show_percentage=True, id="progress")
                    yield Static("", id="result")
        
        yield Footer()
    
    def on_mount(self):
        self.run_worker(self.initialize_database())
    
    async def initialize_database(self):
        """Main database initialization process"""
        try:
            db_init = DatabaseInitializer()
            
            # Step 1: Create tables
            await self.update_progress(10, "Creating database tables...")
            await asyncio.sleep(1)
            db_init.create_tables()
            
            # Step 2: Populate shows
            await self.update_progress(30, "Populating shows catalog...")
            await asyncio.sleep(2)
            db_init.populate_shows()
            
            # Step 3: Initialize stats and financials
            await self.update_progress(60, "Setting up statistics and financials...")
            await asyncio.sleep(1)
            db_init.initialize_stats_and_financials()
            
            # Step 4: Final verification
            await self.update_progress(80, "Verifying database integrity...")
            await asyncio.sleep(1)
            
            # Step 5: Complete
            await self.update_progress(100, "Database initialization complete!")
            await asyncio.sleep(1)
            
            # Hide spinner and show success
            self.query_one("#spinner").display = False
            self.query_one("#result").update("[bold green]✅ EasyFlix database successfully created![/bold green]")
            self.query_one("#result").add_class("success")
            
            # Auto-exit after 3 seconds
            await asyncio.sleep(3)
            self.exit()
            
        except Exception as e:
            self.query_one("#spinner").display = False
            self.query_one("#result").update(f"[bold red]❌ Error: {str(e)}[/bold red]")
            await asyncio.sleep(5)
            self.exit()
    
    async def update_progress(self, value: int, status: str):
        """Update progress bar and status text""" 
        self.progress = value
        self.status_text = status
        self.query_one("#progress").progress = value
        self.query_one("#status").update(status)

def main():
    """Main entry point"""
    print("🎬 EasyFlix Database Initializer")
    print("=" * 40)
    
    # Check if database already exists
    if Path("easyflix.db").exists():
        response = input("Database already exists. Recreate? (y/N): ")
        if response.lower() != 'y':
            print("Initialization cancelled.")
            return
        else:
            Path("easyflix.db").unlink()
    
    # Run the Textual app
    app = DatabaseInitApp()
    app.run()

if __name__ == "__main__":
    main()