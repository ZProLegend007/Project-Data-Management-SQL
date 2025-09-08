#!/usr/bin/env python3
"""
EasyFlix Initialisation Script
Creates and populates the EasyFlix database with encryption and security.
Installs python requirements.
"""

import subprocess
import sys
import os
import site
import importlib

requirements_file = "requirements.txt"

if not os.path.exists(requirements_file):
    print(f"❌ {requirements_file} not found! Initialisation may not work!")

try:
    with open(requirements_file, 'r') as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not packages:
        print("📦 No packages to install")
    
    print(f"📦 Installing {len(packages)} packages from {requirements_file}...")
    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    print("✅ All packages installed successfully!")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Failed to install packages: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error reading requirements file: {e}")
    sys.exit(1)

importlib.reload(site)

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

class DatabaseInitialiser:
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
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_salt(self) -> str:
        """Generate random salt"""
        return secrets.token_hex(16)
    
    def create_tables(self):
        """Create all database tables"""
        conn = self._create_connection()
        cursor = conn.cursor()
        
        # ADMIN_CREDENTIALS table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ADMIN_CREDENTIALS (
            Admin_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username VARCHAR(50) UNIQUE NOT NULL,
            Password_Hash VARCHAR(64) NOT NULL,
            Salt VARCHAR(32) NOT NULL,
            Role VARCHAR(20) DEFAULT 'admin',
            Created_Date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # CUSTOMERS table with Marketing_Opt_In column
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CUSTOMERS (
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username VARCHAR(50) UNIQUE NOT NULL,
            Email VARCHAR(100) UNIQUE NOT NULL,
            Password_Hash VARCHAR(64) NOT NULL,
            Salt VARCHAR(32) NOT NULL,
            Subscription_Level VARCHAR(20) NOT NULL CHECK (Subscription_Level IN ('Basic', 'Premium')),
            Shows TEXT,
            Total_Spent DECIMAL(10,2) DEFAULT 0.00,
            Favourite_Genre VARCHAR(30),
            Marketing_Opt_In BOOLEAN DEFAULT 0
        )
        ''')
        
        # SHOWS table with Cost_To_Buy instead of Cost_To_Rent
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
            Cost_To_Buy DECIMAL(5,2) NULL
        )
        ''')
        
        # BUYS table (no return_date or expired fields)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS BUYS (
            Buy_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            User_ID INTEGER NOT NULL,
            Show_ID INTEGER NOT NULL,
            Buy_Date DATE NOT NULL,
            Cost DECIMAL(5,2) NOT NULL,
            FOREIGN KEY (User_ID) REFERENCES CUSTOMERS(User_ID),
            FOREIGN KEY (Show_ID) REFERENCES SHOWS(Show_ID)
        )
        ''')
        
        # STATISTICS table with separate premium and basic subscription tracking
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS STATISTICS (
            Date DATE PRIMARY KEY,
            Total_Shows_Bought INTEGER DEFAULT 0,
            Total_Subscriptions INTEGER DEFAULT 0,
            Premium_Subscriptions INTEGER DEFAULT 0,
            Basic_Subscriptions INTEGER DEFAULT 0,
            Total_Users INTEGER DEFAULT 0,
            Last_Updated DATETIME NOT NULL
        )
        ''')
        
        # FINANCIALS table with separate premium and basic subscription revenue
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS FINANCIALS (
            Date DATE PRIMARY KEY,
            Total_Revenue_Buys DECIMAL(10,2) DEFAULT 0.00,
            Total_Revenue_Subscriptions DECIMAL(10,2) DEFAULT 0.00,
            Premium_Subscription_Revenue DECIMAL(10,2) DEFAULT 0.00,
            Basic_Subscription_Revenue DECIMAL(10,2) DEFAULT 0.00,
            Total_Combined_Revenue DECIMAL(10,2) DEFAULT 0.00,
            Last_Updated DATETIME NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_admin_credentials(self):
        """Create default admin credentials"""
        conn = self._create_connection()
        cursor = conn.cursor()
        
        # Check if admin already exists
        cursor.execute("SELECT Admin_ID FROM ADMIN_CREDENTIALS WHERE Username = ?", ("EF@dm1n",))
        if cursor.fetchone():
            conn.close()
            return  # Admin already exists
        
        # Create default admin
        admin_username = "EF@dm1n"
        admin_password = "EFP@55"
        salt = self._generate_salt()
        password_hash = self._hash_password(admin_password, salt)
        
        cursor.execute('''
        INSERT INTO ADMIN_CREDENTIALS (Username, Password_Hash, Salt, Role)
        VALUES (?, ?, ?, ?)
        ''', (admin_username, password_hash, salt, "admin"))
        
        conn.commit()
        conn.close()
    
    def populate_shows(self):
        """Populate shows table with diverse content"""
        shows_data = [
            # Shows - Basic Access
            ("The Matrix", date(1999, 3, 31), "R", "Lana Wachowski, Lilly Wachowski", 136, "Action", "Basic", None),
            ("Inception", date(2010, 7, 16), "PG-13", "Christopher Nolan", 148, "Sci-Fi", "Basic", None),
            ("The Shawshank Redemption", date(1994, 9, 23), "R", "Frank Darabont", 142, "Drama", "Basic", None),
            ("Pulp Fiction", date(1994, 10, 14), "R", "Quentin Tarantino", 154, "Crime", "Basic", None),
            ("The Dark Knight", date(2008, 7, 18), "PG-13", "Christopher Nolan", 152, "Action", "Basic", None),
            ("Forrest Gump", date(1994, 7, 6), "PG-13", "Robert Zemeckis", 142, "Drama", "Basic", None),
            ("Fight Club", date(1999, 10, 15), "R", "David Fincher", 139, "Drama", "Basic", None),
            ("Star Wars: A New Hope", date(1977, 5, 25), "PG", "George Lucas", 121, "Sci-Fi", "Basic", None),
            ("The Godfather", date(1972, 3, 24), "R", "Francis Ford Coppola", 175, "Crime", "Basic", None),
            ("Breaking Bad", date(2008, 1, 20), "TV-MA", "Vince Gilligan", 47, "Drama", "Basic", None),
            ("Friends", date(1994, 9, 22), "TV-PG", "David Crane", 22, "Comedy", "Basic", None),
            ("The Office", date(2005, 3, 24), "TV-14", "Greg Daniels", 22, "Comedy", "Basic", None),
            ("Schindler's List", date(1993, 12, 15), "R", "Steven Spielberg", 195, "History", "Basic", None),
            ("Titanic", date(1997, 12, 19), "PG-13", "James Cameron", 194, "Romance", "Basic", None),
            ("Avatar", date(2009, 12, 18), "PG-13", "James Cameron", 162, "Sci-Fi", "Basic", None),
            ("The Avengers", date(2012, 5, 4), "PG-13", "Joss Whedon", 143, "Action", "Basic", None),
            ("Jurassic Park", date(1993, 6, 11), "PG-13", "Steven Spielberg", 127, "Adventure", "Basic", None),
            ("The Lion King", date(1994, 6, 24), "G", "Roger Allers", 88, "Animation", "Basic", None),
            ("Toy Story", date(1995, 11, 22), "G", "John Lasseter", 81, "Animation", "Basic", None),
            ("The Avengers: Endgame", date(2019, 4, 26), "PG-13", "Anthony Russo", 181, "Action", "Basic", None),
            ("Black Panther", date(2018, 2, 16), "PG-13", "Ryan Coogler", 134, "Action", "Basic", None),
            ("Iron Man", date(2008, 5, 2), "PG-13", "Jon Favreau", 126, "Action", "Basic", None),
            ("Captain America: The First Avenger", date(2011, 7, 22), "PG-13", "Joe Johnston", 124, "Action", "Basic", None),
            ("Thor", date(2011, 5, 6), "PG-13", "Kenneth Branagh", 115, "Action", "Basic", None),
            ("Guardians of the Galaxy", date(2014, 8, 1), "PG-13", "James Gunn", 121, "Action", "Basic", None),
            ("Doctor Strange", date(2016, 11, 4), "PG-13", "Scott Derrickson", 115, "Action", "Basic", None),
            ("Ant-Man", date(2015, 7, 17), "PG-13", "Peyton Reed", 117, "Action", "Basic", None),
            ("Captain Marvel", date(2019, 3, 8), "PG-13", "Anna Boden", 123, "Action", "Basic", None),
            ("Spider-Man: Homecoming", date(2017, 7, 7), "PG-13", "Jon Watts", 133, "Action", "Basic", None),
            
            # Shows - Premium Access
            ("Dune", date(2021, 10, 22), "PG-13", "Denis Villeneuve", 155, "Sci-Fi", "Premium", 6.99),
            ("No Time to Die", date(2021, 10, 8), "PG-13", "Cary Joji Fukunaga", 163, "Action", "Premium", 7.99),
            ("Spider-Man: No Way Home", date(2021, 12, 17), "PG-13", "Jon Watts", 148, "Action", "Premium", 7.99),
            ("The Batman", date(2022, 3, 4), "PG-13", "Matt Reeves", 176, "Action", "Premium", 8.99),
            ("Top Gun: Maverick", date(2022, 5, 27), "PG-13", "Joseph Kosinski", 130, "Action", "Premium", 7.99),
            ("Oppenheimer", date(2023, 7, 21), "R", "Christopher Nolan", 180, "Drama", "Premium", 9.99),
            ("Barbie", date(2023, 7, 21), "PG-13", "Greta Gerwig", 114, "Comedy", "Premium", 8.99),
            ("House of the Dragon", date(2022, 8, 21), "TV-MA", "Ryan J. Condal", 60, "Fantasy", "Premium", 4.99),
            ("The Last of Us", date(2023, 1, 15), "TV-MA", "Craig Mazin", 60, "Drama", "Premium", 5.99),
            ("Stranger Things", date(2016, 7, 15), "TV-14", "Matt Duffer", 51, "Sci-Fi", "Premium", 4.99),
            ("Chernobyl", date(2019, 5, 6), "TV-MA", "Craig Mazin", 60, "Drama", "Premium", 6.99),
            ("Watchmen", date(2019, 10, 20), "TV-MA", "Damon Lindelof", 60, "Sci-Fi", "Premium", 6.99),
            ("The Marvelous Mrs. Maisel", date(2017, 3, 17), "TV-14", "Amy Sherman-Palladino", 60, "Comedy", "Premium", 4.99),
            ("Fleabag", date(2016, 7, 21), "TV-MA", "Phoebe Waller-Bridge", 30, "Comedy", "Premium", 3.99),
            ("The Handmaid's Tale", date(2017, 4, 26), "TV-MA", "Bruce Miller", 60, "Drama", "Premium", 5.99),
            ("Big Little Lies", date(2017, 2, 19), "TV-MA", "David E. Kelley", 60, "Drama", "Premium", 5.99),
            ("True Detective", date(2014, 1, 12), "TV-MA", "Nic Pizzolatto", 60, "Crime", "Premium", 6.99),
            ("Fargo", date(2014, 4, 15), "TV-MA", "Noah Hawley", 60, "Crime", "Premium", 5.99),
            ("Mindhunter", date(2017, 10, 13), "TV-MA", "Joe Penhall", 60, "Crime", "Premium", 5.99),
            ("Narcos", date(2015, 8, 28), "TV-MA", "Chris Brancato", 60, "Crime", "Premium", 5.99),
            ("Peaky Blinders", date(2013, 9, 12), "TV-MA", "Steven Knight", 60, "Crime", "Premium", 5.99),
            ("The Leftovers", date(2014, 6, 29), "TV-MA", "Damon Lindelof", 60, "Drama", "Premium", 5.99),
            ("Westworld", date(2016, 10, 2), "TV-MA", "Jonathan Nolan", 60, "Sci-Fi", "Premium", 6.99),
            ("Russian Doll", date(2019, 2, 1), "TV-MA", "Natasha Lyonne", 30, "Comedy", "Premium", 3.99),
            ("The OA", date(2016, 12, 16), "TV-MA", "Brit Marling", 60, "Sci-Fi", "Premium", 5.99),
            ("Atlanta", date(2016, 9, 6), "TV-MA", "Donald Glover", 30, "Comedy", "Premium", 3.99),
            ("Barry", date(2018, 3, 25), "TV-MA", "Alec Berg", 30, "Comedy", "Premium", 4.99),
            ("Killing Eve", date(2018, 4, 8), "TV-14", "Phoebe Waller-Bridge", 45, "Thriller", "Premium", 4.99),
            ("The Good Place", date(2016, 9, 19), "TV-PG", "Michael Schur", 22, "Comedy", "Premium", 3.99),
            ("Ted Lasso", date(2020, 8, 14), "TV-MA", "Bill Lawrence", 30, "Comedy", "Premium", 4.99)
        ]
        
        conn = self._create_connection()
        cursor = conn.cursor()
        
        cursor.executemany('''
        INSERT OR IGNORE INTO SHOWS 
        (Name, Release_Date, Rating, Director, Length, Genre, Access_Group, Cost_To_Buy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', shows_data)
        
        conn.commit()
        conn.close()
    
    def initialise_stats_and_financials(self):
        """Initialise statistics and financials with today's date"""
        today = date.today()
        now = datetime.now()
        
        conn = self._create_connection()
        cursor = conn.cursor()
        
        # Initialise statistics
        cursor.execute('''
        INSERT OR REPLACE INTO STATISTICS 
        (Date, Total_Shows_Bought, Total_Subscriptions, Premium_Subscriptions, Basic_Subscriptions, Total_Users, Last_Updated)
        VALUES (?, 0, 0, 0, 0, 0, ?)
        ''', (today, now))
        
        # Initialise financials
        cursor.execute('''
        INSERT OR REPLACE INTO FINANCIALS 
        (Date, Total_Revenue_Buys, Total_Revenue_Subscriptions, Premium_Subscription_Revenue, Basic_Subscription_Revenue, Total_Combined_Revenue, Last_Updated)
        VALUES (?, 0.00, 0.00, 0.00, 0.00, 0.00, ?)
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
    """EasyFlix Database Initialisation Application"""
    
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
        color: #e94560;
        background: #1a1a2e;
    }
    """
    
    progress = reactive(0)
    status_text = reactive("Initialising EasyFlix Database...")
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Center():
            with Middle():
                with Vertical(classes="container"):
                    yield Static("[bold]🎬 EasyFlix Initialiser[/bold]", classes="status")
                    yield Static("", id="spinner_container")
                    yield LoadingSpinner(id="spinner")
                    yield Static(self.status_text, id="status")
                    yield ProgressBar(total=100, show_percentage=True, id="progress")
                    yield Static("", id="result")
        
        yield Footer()
    
    def on_mount(self):
        self.run_worker(self.initialise_database())
    
    async def initialise_database(self):
        """Main database initialisation process"""
        try:
            db_init = DatabaseInitialiser()
            
            # Step 1: Create tables
            await self.update_progress(10, "Creating database tables...")
            await asyncio.sleep(1)
            db_init.create_tables()
            
            # Step 2: Create admin credentials
            await self.update_progress(30, "Setting up admin credentials...")
            await asyncio.sleep(1)
            db_init.create_admin_credentials()
            
            # Step 3: Populate shows
            await self.update_progress(60, "Populating shows catalog...")
            await asyncio.sleep(2)
            db_init.populate_shows()
            
            # Step 4: Initialise stats and financials
            await self.update_progress(90, "Setting up statistics and financials...")
            await asyncio.sleep(1)
            db_init.initialise_stats_and_financials()
            
            # Step 5: Complete
            await self.update_progress(100, "Database initialisation complete!")
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
    print("🎬 EasyFlix Initialiser")
    print("=" * 40)
    
    # Check if database already exists
    if Path("easyflix.db").exists():
        response = input("Database already exists. Recreate? (y/N): ")
        if response.lower() != 'y':
            print("Initialisation cancelled.")
            return
        else:
            Path("easyflix.db").unlink()
    
    # Run the Textual app
    app = DatabaseInitApp()
    app.run()

if __name__ == "__main__":
    main()
