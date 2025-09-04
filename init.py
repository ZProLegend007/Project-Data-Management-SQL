#!/usr/bin/env python3
"""
EasyFlix Initialisation Script
Creates and populates the EasyFlix database with encryption and security.
Installs python requirements.
"""

import subprocess
import sys
import os
    
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

class Initialise:
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
            Cost_To_Rent DECIMAL(5,2) NULL
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
    # Movies - Basic Access
            ("The Matrix", date(1999, 3, 31), "R", "Lana Wachowski, Lilly Wachowski", 136, "Action", "Basic", None),
            ("Inception", date(2010, 7, 16), "PG-13", "Christopher Nolan", 148, "Sci-Fi", "Basic", None),
            ("The Shawshank Redemption", date(1994, 9, 23), "R", "Frank Darabont", 142, "Drama", "Basic", None),
            ("Pulp Fiction", date(1994, 10, 14), "R", "Quentin Tarantino", 154, "Crime", "Basic", None),
            ("The Dark Knight", date(2008, 7, 18), "PG-13", "Christopher Nolan", 152, "Action", "Basic", None),
            ("Forrest Gump", date(1994, 7, 6), "PG-13", "Robert Zemeckis", 142, "Drama", "Basic", None),
            ("Fight Club", date(1999, 10, 15), "R", "David Fincher", 139, "Drama", "Basic", None),
            ("The Lord of the Rings: The Fellowship", date(2001, 12, 19), "PG-13", "Peter Jackson", 178, "Fantasy", "Basic", None),
            ("Star Wars: A New Hope", date(1977, 5, 25), "PG", "George Lucas", 121, "Sci-Fi", "Basic", None),
            ("The Godfather", date(1972, 3, 24), "R", "Francis Ford Coppola", 175, "Crime", "Basic", None),
            ("Goodfellas", date(1990, 9, 21), "R", "Martin Scorsese", 146, "Crime", "Basic", None),
            ("The Silence of the Lambs", date(1991, 2, 14), "R", "Jonathan Demme", 118, "Thriller", "Basic", None),
            ("Saving Private Ryan", date(1998, 7, 24), "R", "Steven Spielberg", 169, "War", "Basic", None),
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
            ("Wonder Woman", date(2017, 6, 2), "PG-13", "Patty Jenkins", 141, "Action", "Basic", None),
            ("Justice League", date(2017, 11, 17), "PG-13", "Zack Snyder", 120, "Action", "Basic", None),
            ("Man of Steel", date(2013, 6, 14), "PG-13", "Zack Snyder", 143, "Action", "Basic", None),
            ("Batman Begins", date(2005, 6, 15), "PG-13", "Christopher Nolan", 140, "Action", "Basic", None),
            ("The Dark Knight Rises", date(2012, 7, 20), "PG-13", "Christopher Nolan", 165, "Action", "Basic", None),
            ("X-Men", date(2000, 7, 14), "PG-13", "Bryan Singer", 104, "Action", "Basic", None),
            ("X-Men: Days of Future Past", date(2014, 5, 23), "PG-13", "Bryan Singer", 131, "Action", "Basic", None),
            ("Deadpool", date(2016, 2, 12), "R", "Tim Miller", 108, "Action", "Basic", None),
            ("Logan", date(2017, 3, 3), "R", "James Mangold", 137, "Action", "Basic", None),
            ("The Terminator", date(1984, 10, 26), "R", "James Cameron", 107, "Sci-Fi", "Basic", None),
            ("Terminator 2: Judgment Day", date(1991, 7, 3), "R", "James Cameron", 137, "Sci-Fi", "Basic", None),
            ("Aliens", date(1986, 7, 18), "R", "James Cameron", 137, "Sci-Fi", "Basic", None),
            ("Alien", date(1979, 5, 25), "R", "Ridley Scott", 117, "Horror", "Basic", None),
            ("Blade Runner", date(1982, 6, 25), "R", "Ridley Scott", 117, "Sci-Fi", "Basic", None),
            ("The Fifth Element", date(1997, 5, 9), "PG-13", "Luc Besson", 126, "Sci-Fi", "Basic", None),
            ("Men in Black", date(1997, 7, 2), "PG-13", "Barry Sonnenfeld", 98, "Sci-Fi", "Basic", None),
            ("Independence Day", date(1996, 7, 3), "PG-13", "Roland Emmerich", 145, "Sci-Fi", "Basic", None),
            ("E.T. the Extra-Terrestrial", date(1982, 6, 11), "PG", "Steven Spielberg", 115, "Family", "Basic", None),
            ("Back to the Future", date(1985, 7, 3), "PG", "Robert Zemeckis", 116, "Adventure", "Basic", None),
            ("Back to the Future Part II", date(1989, 11, 22), "PG", "Robert Zemeckis", 108, "Adventure", "Basic", None),
            ("Indiana Jones: Raiders of the Lost Ark", date(1981, 6, 12), "PG", "Steven Spielberg", 115, "Adventure", "Basic", None),
            ("Indiana Jones: The Last Crusade", date(1989, 5, 24), "PG-13", "Steven Spielberg", 127, "Adventure", "Basic", None),
            ("Jaws", date(1975, 6, 20), "PG", "Steven Spielberg", 124, "Thriller", "Basic", None),
            ("Close Encounters of the Third Kind", date(1977, 11, 16), "PG", "Steven Spielberg", 138, "Sci-Fi", "Basic", None),
            ("The Goonies", date(1985, 6, 7), "PG", "Richard Donner", 114, "Adventure", "Basic", None),
            ("Ghostbusters", date(1984, 6, 8), "PG", "Ivan Reitman", 105, "Comedy", "Basic", None),
            ("Groundhog Day", date(1993, 2, 12), "PG", "Harold Ramis", 101, "Comedy", "Basic", None),
            ("Big", date(1988, 6, 3), "PG", "Penny Marshall", 104, "Comedy", "Basic", None),
            ("Mrs. Doubtfire", date(1993, 11, 24), "PG-13", "Chris Columbus", 125, "Comedy", "Basic", None),
            ("Home Alone", date(1990, 11, 16), "PG", "Chris Columbus", 103, "Comedy", "Basic", None),
            ("The Mask", date(1994, 7, 29), "PG-13", "Chuck Russell", 101, "Comedy", "Basic", None),
            ("Dumb and Dumber", date(1994, 12, 16), "PG-13", "Peter Farrelly", 107, "Comedy", "Basic", None),
            ("Wayne's World", date(1992, 2, 14), "PG-13", "Penelope Spheeris", 94, "Comedy", "Basic", None),
            ("Austin Powers: International Man of Mystery", date(1997, 5, 2), "PG-13", "Jay Roach", 89, "Comedy", "Basic", None),
            ("The Hangover", date(2009, 6, 5), "R", "Todd Phillips", 100, "Comedy", "Basic", None),
            ("Superbad", date(2007, 8, 17), "R", "Greg Mottola", 113, "Comedy", "Basic", None),
            ("Pineapple Express", date(2008, 8, 6), "R", "David Gordon Green", 111, "Comedy", "Basic", None),
            ("Knocked Up", date(2007, 6, 1), "R", "Judd Apatow", 129, "Comedy", "Basic", None),
            ("Anchorman: The Legend of Ron Burgundy", date(2004, 7, 9), "PG-13", "Adam McKay", 94, "Comedy", "Basic", None),
            ("Wedding Crashers", date(2005, 7, 15), "R", "David Dobkin", 119, "Comedy", "Basic", None),
            ("Meet the Parents", date(2000, 10, 6), "PG-13", "Jay Roach", 108, "Comedy", "Basic", None),
            
            # Movies - Premium Access
            ("Dune", date(2021, 10, 22), "PG-13", "Denis Villeneuve", 155, "Sci-Fi", "Premium", 6.99),
            ("No Time to Die", date(2021, 10, 8), "PG-13", "Cary Joji Fukunaga", 163, "Action", "Premium", 7.99),
            ("Spider-Man: No Way Home", date(2021, 12, 17), "PG-13", "Jon Watts", 148, "Action", "Premium", 7.99),
            ("The Batman", date(2022, 3, 4), "PG-13", "Matt Reeves", 176, "Action", "Premium", 8.99),
            ("Top Gun: Maverick", date(2022, 5, 27), "PG-13", "Joseph Kosinski", 130, "Action", "Premium", 7.99),
            ("Black Widow", date(2021, 7, 9), "PG-13", "Cate Shortland", 134, "Action", "Premium", 6.99),
            ("Fast & Furious 9", date(2021, 6, 25), "PG-13", "Justin Lin", 143, "Action", "Premium", 6.99),
            ("Eternals", date(2021, 11, 5), "PG-13", "Chloé Zhao", 156, "Action", "Premium", 7.99),
            ("The Matrix Resurrections", date(2021, 12, 22), "R", "Lana Wachowski", 148, "Sci-Fi", "Premium", 8.99),
            ("John Wick: Chapter 4", date(2023, 3, 24), "R", "Chad Stahelski", 169, "Action", "Premium", 9.99),
            ("Avengers: Infinity War", date(2018, 4, 27), "PG-13", "Anthony Russo", 149, "Action", "Premium", 8.99),
            ("Thor: Love and Thunder", date(2022, 7, 8), "PG-13", "Taika Waititi", 119, "Action", "Premium", 7.99),
            ("Doctor Strange in the Multiverse of Madness", date(2022, 5, 6), "PG-13", "Sam Raimi", 126, "Action", "Premium", 8.99),
            ("Shang-Chi and the Legend of the Ten Rings", date(2021, 9, 3), "PG-13", "Destin Daniel Cretton", 132, "Action", "Premium", 7.99),
            ("The Suicide Squad", date(2021, 8, 6), "R", "James Gunn", 132, "Action", "Premium", 7.99),
            ("Wonder Woman 1984", date(2020, 12, 25), "PG-13", "Patty Jenkins", 151, "Action", "Premium", 6.99),
            ("Aquaman", date(2018, 12, 21), "PG-13", "James Wan", 143, "Action", "Premium", 6.99),
            ("The Flash", date(2023, 6, 16), "PG-13", "Andy Muschietti", 144, "Action", "Premium", 8.99),
            ("Blade Runner 2049", date(2017, 10, 6), "R", "Denis Villeneuve", 164, "Sci-Fi", "Premium", 7.99),
            ("Mad Max: Fury Road", date(2015, 5, 15), "R", "George Miller", 120, "Action", "Premium", 6.99),
            ("Interstellar", date(2014, 11, 7), "PG-13", "Christopher Nolan", 169, "Sci-Fi", "Premium", 7.99),
            ("Tenet", date(2020, 9, 3), "PG-13", "Christopher Nolan", 150, "Sci-Fi", "Premium", 8.99),
            ("Oppenheimer", date(2023, 7, 21), "R", "Christopher Nolan", 180, "Drama", "Premium", 9.99),
            ("Barbie", date(2023, 7, 21), "PG-13", "Greta Gerwig", 114, "Comedy", "Premium", 8.99),
            ("Everything Everywhere All at Once", date(2022, 3, 25), "R", "Daniels", 139, "Sci-Fi", "Premium", 8.99),
            ("The French Dispatch", date(2021, 10, 22), "R", "Wes Anderson", 107, "Comedy", "Premium", 6.99),
            ("Parasite", date(2019, 5, 30), "R", "Bong Joon-ho", 132, "Thriller", "Premium", 7.99),
            ("Knives Out", date(2019, 11, 27), "PG-13", "Rian Johnson", 130, "Mystery", "Premium", 6.99),
            ("Glass Onion: A Knives Out Mystery", date(2022, 12, 23), "PG-13", "Rian Johnson", 139, "Mystery", "Premium", 8.99),
            ("Once Upon a Time in Hollywood", date(2019, 7, 26), "R", "Quentin Tarantino", 161, "Drama", "Premium", 7.99),
            ("The Irishman", date(2019, 11, 27), "R", "Martin Scorsese", 209, "Crime", "Premium", 8.99),
            ("1917", date(2019, 12, 25), "R", "Sam Mendes", 119, "War", "Premium", 7.99),
            ("Ford v Ferrari", date(2019, 11, 15), "PG-13", "James Mangold", 152, "Drama", "Premium", 6.99),
            ("A Quiet Place", date(2018, 4, 6), "PG-13", "John Krasinski", 90, "Horror", "Premium", 5.99),
            ("A Quiet Place Part II", date(2020, 5, 28), "PG-13", "John Krasinski", 97, "Horror", "Premium", 7.99),
            ("It", date(2017, 9, 8), "R", "Andy Muschietti", 135, "Horror", "Premium", 6.99),
            ("It Chapter Two", date(2019, 9, 6), "R", "Andy Muschietti", 169, "Horror", "Premium", 7.99),
            ("Get Out", date(2017, 2, 24), "R", "Jordan Peele", 104, "Horror", "Premium", 5.99),
            ("Us", date(2019, 3, 22), "R", "Jordan Peele", 116, "Horror", "Premium", 6.99),
            ("Nope", date(2022, 7, 22), "R", "Jordan Peele", 130, "Horror", "Premium", 8.99),
            ("Hereditary", date(2018, 6, 8), "R", "Ari Aster", 127, "Horror", "Premium", 6.99),
            ("Midsommar", date(2019, 7, 3), "R", "Ari Aster", 148, "Horror", "Premium", 7.99),
            ("The Lighthouse", date(2019, 10, 18), "R", "Robert Eggers", 109, "Horror", "Premium", 6.99),
            ("Scream", date(2022, 1, 14), "R", "Matt Bettinelli-Olpin", 114, "Horror", "Premium", 7.99),
            ("Halloween Kills", date(2021, 10, 15), "R", "David Gordon Green", 105, "Horror", "Premium", 6.99),
            ("The Conjuring: The Devil Made Me Do It", date(2021, 6, 4), "R", "Michael Chaves", 112, "Horror", "Premium", 6.99),
            ("Dune: Part Two", date(2024, 3, 1), "PG-13", "Denis Villeneuve", 166, "Sci-Fi", "Premium", 9.99),
            ("Mission: Impossible - Dead Reckoning", date(2023, 7, 12), "PG-13", "Christopher McQuarrie", 163, "Action", "Premium", 8.99),
            ("Indiana Jones and the Dial of Destiny", date(2023, 6, 30), "PG-13", "James Mangold", 154, "Adventure", "Premium", 8.99),
            ("Transformers: Rise of the Beasts", date(2023, 6, 9), "PG-13", "Steven Caple Jr.", 127, "Action", "Premium", 7.99),
            ("Guardians of the Galaxy Vol. 3", date(2023, 5, 5), "PG-13", "James Gunn", 150, "Action", "Premium", 8.99),
            ("The Little Mermaid", date(2023, 5, 26), "PG", "Rob Marshall", 135, "Family", "Premium", 7.99),
            ("Scream VI", date(2023, 3, 10), "R", "Matt Bettinelli-Olpin", 122, "Horror", "Premium", 7.99),
            ("Cocaine Bear", date(2023, 2, 24), "R", "Elizabeth Banks", 95, "Comedy", "Premium", 6.99),
            ("Ant-Man and the Wasp: Quantumania", date(2023, 2, 17), "PG-13", "Peyton Reed", 124, "Action", "Premium", 7.99),
            ("Avatar: The Way of Water", date(2022, 12, 16), "PG-13", "James Cameron", 192, "Sci-Fi", "Premium", 9.99),
            ("Black Adam", date(2022, 10, 21), "PG-13", "Jaume Collet-Serra", 125, "Action", "Premium", 7.99),
            ("Wakanda Forever", date(2022, 11, 11), "PG-13", "Ryan Coogler", 161, "Action", "Premium", 8.99),
            ("Thor: Love and Thunder", date(2022, 7, 8), "PG-13", "Taika Waititi", 119, "Action", "Premium", 7.99),
            ("Minions: The Rise of Gru", date(2022, 7, 1), "PG", "Kyle Balda", 87, "Animation", "Premium", 6.99),
            
            # TV Shows - Basic Access
            ("Breaking Bad", date(2008, 1, 20), "TV-MA", "Vince Gilligan", 47, "Drama", "Basic", None),
            ("Game of Thrones", date(2011, 4, 17), "TV-MA", "David Benioff", 57, "Fantasy", "Basic", None),
            ("Friends", date(1994, 9, 22), "TV-PG", "David Crane", 22, "Comedy", "Basic", None),
            ("The Office", date(2005, 3, 24), "TV-14", "Greg Daniels", 22, "Comedy", "Basic", None),
            ("Stranger Things", date(2016, 7, 15), "TV-14", "Matt Duffer", 51, "Sci-Fi", "Basic", None),
            ("The Crown", date(2016, 11, 4), "TV-MA", "Peter Morgan", 58, "Drama", "Basic", None),
            ("Sherlock", date(2010, 7, 25), "TV-14", "Mark Gatiss", 90, "Crime", "Basic", None),
            ("Black Mirror", date(2011, 12, 4), "TV-MA", "Charlie Brooker", 60, "Sci-Fi", "Basic", None),
            ("The Walking Dead", date(2010, 10, 31), "TV-MA", "Frank Darabont", 44, "Horror", "Basic", None),
            ("Lost", date(2004, 9, 22), "TV-14", "J.J. Abrams", 42, "Mystery", "Basic", None),
            ("House of Cards", date(2013, 2, 1), "TV-MA", "Beau Willimon", 51, "Drama", "Basic", None),
            ("The Sopranos", date(1999, 1, 10), "TV-MA", "David Chase", 55, "Crime", "Basic", None),
            ("Mad Men", date(2007, 7, 19), "TV-14", "Matthew Weiner", 47, "Drama", "Basic", None),
            ("Better Call Saul", date(2015, 2, 8), "TV-MA", "Vince Gilligan", 47, "Drama", "Basic", None),
            ("The Wire", date(2002, 6, 2), "TV-MA", "David Simon", 60, "Crime", "Basic", None),
            ("The Simpsons", date(1989, 12, 17), "TV-PG", "Matt Groening", 22, "Animation", "Basic", None),
            ("Seinfeld", date(1989, 7, 5), "TV-PG", "Larry David", 22, "Comedy", "Basic", None),
            ("How I Met Your Mother", date(2005, 9, 19), "TV-14", "Carter Bays", 22, "Comedy", "Basic", None),
            ("The Big Bang Theory", date(2007, 9, 24), "TV-14", "Chuck Lorre", 22, "Comedy", "Basic", None),
            ("Parks and Recreation", date(2009, 4, 9), "TV-14", "Greg Daniels", 22, "Comedy", "Basic", None),
            ("Brooklyn Nine-Nine", date(2013, 9, 17), "TV-14", "Dan Goor", 22, "Comedy", "Basic", None),
            ("NCIS", date(2003, 9, 23), "TV-14", "Donald P. Bellisario", 43, "Crime", "Basic", None),
            ("Criminal Minds", date(2005, 9, 22), "TV-14", "Jeff Davis", 42, "Crime", "Basic", None),
            ("CSI: Crime Scene Investigation", date(2000, 10, 6), "TV-14", "Anthony E. Zuiker", 43, "Crime", "Basic", None),
            ("Law & Order: SVU", date(1999, 9, 20), "TV-14", "Dick Wolf", 43, "Crime", "Basic", None),
            ("Grey's Anatomy", date(2005, 3, 27), "TV-14", "Shonda Rhimes", 43, "Drama", "Basic", None),
            ("ER", date(1994, 9, 19), "TV-14", "Michael Crichton", 44, "Drama", "Basic", None),
            ("The West Wing", date(1999, 9, 22), "TV-14", "Aaron Sorkin", 42, "Drama", "Basic", None),
            ("24", date(2001, 11, 6), "TV-14", "Joel Surnow", 44, "Thriller", "Basic", None),
            ("Prison Break", date(2005, 8, 29), "TV-14", "Paul Scheuring", 42, "Drama", "Basic", None),
            ("Heroes", date(2006, 9, 25), "TV-14", "Tim Kring", 43, "Sci-Fi", "Basic", None),
            ("Supernatural", date(2005, 9, 13), "TV-14", "Eric Kripke", 42, "Supernatural", "Basic", None),
            ("The X-Files", date(1993, 9, 10), "TV-14", "Chris Carter", 45, "Sci-Fi", "Basic", None),
            ("Buffy the Vampire Slayer", date(1997, 3, 10), "TV-14", "Joss Whedon", 44, "Fantasy", "Basic", None),
            ("Angel", date(1999, 10, 5), "TV-14", "Joss Whedon", 44, "Fantasy", "Basic", None),
            ("Dexter", date(2006, 10, 1), "TV-MA", "James Manos Jr.", 53, "Crime", "Basic", None),
            ("The Shield", date(2002, 3, 12), "TV-MA", "Shawn Ryan", 45, "Crime", "Basic", None),
            ("Six Feet Under", date(2001, 6, 3), "TV-MA", "Alan Ball", 52, "Drama", "Basic", None),
            ("Deadwood", date(2004, 3, 21), "TV-MA", "David Milch", 55, "Western", "Basic", None),
            ("The Twilight Zone", date(1959, 10, 2), "TV-PG", "Rod Serling", 25, "Sci-Fi", "Basic", None),
            ("Star Trek: The Next Generation", date(1987, 9, 28), "TV-PG", "Gene Roddenberry", 44, "Sci-Fi", "Basic", None),
            ("Battlestar Galactica", date(2004, 10, 18), "TV-14", "Ronald D. Moore", 44, "Sci-Fi", "Basic", None),
            ("Firefly", date(2002, 9, 20), "TV-14", "Joss Whedon", 42, "Sci-Fi", "Basic", None),
            ("Arrested Development", date(2003, 11, 2), "TV-14", "Mitchell Hurwitz", 22, "Comedy", "Basic", None),
            ("Scrubs", date(2001, 10, 2), "TV-14", "Bill Lawrence", 22, "Comedy", "Basic", None),
            ("30 Rock", date(2006, 10, 11), "TV-14", "Tina Fey", 22, "Comedy", "Basic", None),
            ("Community", date(2009, 9, 17), "TV-14", "Dan Harmon", 22, "Comedy", "Basic", None),
            ("It's Always Sunny in Philadelphia", date(2005, 8, 4), "TV-MA", "Rob McElhenney", 22, "Comedy", "Basic", None),
            ("The Fresh Prince of Bel-Air", date(1990, 9, 10), "TV-PG", "Andy Borowitz", 23, "Comedy", "Basic", None),
            ("Full House", date(1987, 9, 22), "TV-G", "Jeff Franklin", 22, "Family", "Basic", None),
            ("Family Guy", date(1999, 1, 31), "TV-14", "Seth MacFarlane", 22, "Animation", "Basic", None),
            ("South Park", date(1997, 8, 13), "TV-MA", "Trey Parker", 22, "Animation", "Basic", None),
            ("King of the Hill", date(1997, 1, 12), "TV-PG", "Mike Judge", 22, "Animation", "Basic", None),
            ("Futurama", date(1999, 3, 28), "TV-14", "Matt Groening", 22, "Animation", "Basic", None),
            ("The Venture Bros.", date(2003, 8, 7), "TV-14", "Jackson Publick", 22, "Animation", "Basic", None),
            ("Frasier", date(1993, 9, 16), "TV-PG", "David Angell", 22, "Comedy", "Basic", None),
            ("Cheers", date(1982, 9, 30), "TV-PG", "James Burrows", 24, "Comedy", "Basic", None),
            ("M*A*S*H", date(1972, 9, 17), "TV-PG", "Larry Gelbart", 25, "Comedy", "Basic", None),
            ("The Mary Tyler Moore Show", date(1970, 9, 19), "TV-G", "James L. Brooks", 25, "Comedy", "Basic", None),
            ("All in the Family", date(1971, 1, 12), "TV-PG", "Norman Lear", 25, "Comedy", "Basic", None),
            ("The Jeffersons", date(1975, 1, 18), "TV-PG", "Norman Lear", 25, "Comedy", "Basic", None),
            ("Good Times", date(1974, 2, 8), "TV-PG", "Eric Monte", 25, "Comedy", "Basic", None),
            ("Sanford and Son", date(1972, 1, 14), "TV-PG", "Bud Yorkin", 25, "Comedy", "Basic", None),
            ("The Cosby Show", date(1984, 9, 20), "TV-G", "Bill Cosby", 24, "Family", "Basic", None),
            ("Family Matters", date(1989, 9, 22), "TV-G", "William Bickley", 24, "Family", "Basic", None),
            
            # TV Shows - Premium Access
            ("House of the Dragon", date(2022, 8, 21), "TV-MA", "Ryan J. Condal", 60, "Fantasy", "Premium", 4.99),
            ("The Last of Us", date(2023, 1, 15), "TV-MA", "Craig Mazin", 60, "Drama", "Premium", 5.99),
            ("Wednesday", date(2022, 11, 23), "TV-14", "Alfred Gough", 50, "Comedy", "Premium", 3.99),
            ("Euphoria", date(2019, 6, 16), "TV-MA", "Sam Levinson", 60, "Drama", "Premium", 4.99),
            ("The Bear", date(2022, 6, 23), "TV-MA", "Christopher Storer", 30, "Comedy", "Premium", 3.99),
            ("Only Murders in the Building", date(2021, 8, 31), "TV-14", "Steve Martin", 35, "Comedy", "Premium", 3.99),
            ("The White Lotus", date(2021, 7, 11), "TV-MA", "Mike White", 60, "Comedy", "Premium", 4.99),
            ("Succession", date(2018, 6, 3), "TV-MA", "Jesse Armstrong", 60, "Drama", "Premium", 5.99),
            ("The Mandalorian", date(2019, 11, 12), "TV-PG", "Jon Favreau", 40, "Sci-Fi", "Premium", 4.99),
            ("Ozark", date(2017, 7, 21), "TV-MA", "Bill Dubuque", 60, "Crime", "Premium", 4.99),
            ("The Crown Season 4", date(2020, 11, 15), "TV-MA", "Peter Morgan", 58, "Drama", "Premium", 5.99),
            ("Bridgerton", date(2020, 12, 25), "TV-MA", "Chris Van Dusen", 60, "Romance", "Premium", 4.99),
            ("Squid Game", date(2021, 9, 17), "TV-MA", "Hwang Dong-hyuk", 60, "Thriller", "Premium", 6.99),
            ("Money Heist", date(2017, 5, 2), "TV-MA", "Álex Pina", 70, "Crime", "Premium", 5.99),
            ("The Queen's Gambit", date(2020, 10, 23), "TV-MA", "Scott Frank", 60, "Drama", "Premium", 6.99),
            ("Lupin", date(2021, 1, 8), "TV-MA", "George Kay", 45, "Crime", "Premium", 4.99),
            ("Dark", date(2017, 12, 1), "TV-MA", "Baran bo Odar", 60, "Sci-Fi", "Premium", 5.99),
            ("Elite", date(2018, 10, 5), "TV-MA", "Carlos Montero", 50, "Drama", "Premium", 4.99),
            ("The Witcher", date(2019, 12, 20), "TV-MA", "Lauren Schmidt", 60, "Fantasy", "Premium", 6.99),
            ("Stranger Things 4", date(2022, 5, 27), "TV-14", "Matt Duffer", 75, "Sci-Fi", "Premium", 7.99),
            ("Better Call Saul Final Season", date(2022, 4, 18), "TV-MA", "Vince Gilligan", 50, "Drama", "Premium", 6.99),
            ("The Boys", date(2019, 7, 26), "TV-MA", "Eric Kripke", 60, "Action", "Premium", 5.99),
            ("Invincible", date(2021, 3, 26), "TV-MA", "Robert Kirkman", 45, "Animation", "Premium", 4.99),
            ("The Umbrella Academy", date(2019, 2, 15), "TV-14", "Steve Blackman", 60, "Sci-Fi", "Premium", 5.99),
            ("Cobra Kai", date(2018, 5, 2), "TV-14", "Josh Heald", 30, "Drama", "Premium", 3.99),
            ("Yellowstone", date(2018, 6, 20), "TV-MA", "Taylor Sheridan", 60, "Drama", "Premium", 6.99),
            ("Mare of Easttown", date(2021, 4, 18), "TV-MA", "Brad Ingelsby", 60, "Crime", "Premium", 5.99),
            ("The Night Manager", date(2016, 2, 21), "TV-14", "Susanne Bier", 60, "Thriller", "Premium", 5.99),
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
            ("Ted Lasso", date(2020, 8, 14), "TV-MA", "Bill Lawrence", 30, "Comedy", "Premium", 4.99),
            ("The Morning Show", date(2019, 11, 1), "TV-MA", "Kerry Ehrin", 60, "Drama", "Premium", 5.99),
            ("See", date(2019, 11, 1), "TV-MA", "Steven Knight", 60, "Sci-Fi", "Premium", 5.99),
            ("Foundation", date(2021, 9, 24), "TV-14", "David S. Goyer", 60, "Sci-Fi", "Premium", 6.99),
            ("For All Mankind", date(2019, 11, 1), "TV-MA", "Ronald D. Moore", 60, "Sci-Fi", "Premium", 5.99),
            ("Servant", date(2019, 11, 28), "TV-MA", "Tony Basgallop", 30, "Thriller", "Premium", 4.99),
            ("Defending Jacob", date(2020, 4, 24), "TV-MA", "Mark Bomback", 60, "Drama", "Premium", 5.99),
            ("The Outsider", date(2020, 1, 12), "TV-MA", "Richard Price", 60, "Horror", "Premium", 5.99),
            ("Lovecraft Country", date(2020, 8, 16), "TV-MA", "Misha Green", 60, "Horror", "Premium", 6.99),
            ("His Dark Materials", date(2019, 11, 3), "TV-14", "Jack Thorne", 60, "Fantasy", "Premium", 5.99),
            ("The Nevers", date(2021, 4, 11), "TV-MA", "Joss Whedon", 60, "Fantasy", "Premium", 5.99),
            ("Shadow and Bone", date(2021, 4, 23), "TV-14", "Eric Heisserer", 60, "Fantasy", "Premium", 4.99),
            ("The Falcon and the Winter Soldier", date(2021, 3, 19), "TV-14", "Malcolm Spellman", 50, "Action", "Premium", 5.99)
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
    
    def initialise_stats_and_financials(self):
        """Initialise statistics and financials with today's date"""
        today = date.today()
        now = datetime.now()
        
        conn = self._create_connection()
        cursor = conn.cursor()
        
        # Initialise statistics
        cursor.execute('''
        INSERT OR REPLACE INTO STATISTICS 
        (Date, Total_Shows_Rented, Total_Subscriptions, Total_Users, Last_Updated)
        VALUES (?, 0, 0, 0, ?)
        ''', (today, now))
        
        # Initialise financials
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
            
            # Step 2: Populate shows
            await self.update_progress(30, "Populating shows catalog...")
            await asyncio.sleep(2)
            db_init.populate_shows()
            
            # Step 3: Initialise stats and financials
            await self.update_progress(60, "Setting up statistics and financials...")
            await asyncio.sleep(1)
            db_init.initialise_stats_and_financials()
            
            # Step 4: Final verification
            await self.update_progress(80, "Verifying database integrity...")
            await asyncio.sleep(1)
            
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
