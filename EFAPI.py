#!/usr/bin/env python3
"""
EasyFlix API (EFAPI.py)
Secure API interface for EasyFlix database operations
"""

import sqlite3
import argparse
import json
import hashlib
import os
import sys
import asyncio
import threading
from datetime import date, datetime
from typing import Dict, List, Optional, Any

class EFAPIError(Exception):
    """Custom exception for EFAPI errors"""
    pass

class EFAPI_Commands:
    def __init__(self, db_path: str = "easyflix.db", password: str = "E@syFl1xP@ss"):
        self.db_path = db_path
        self.password = password
        self._verify_database()
    
    def _verify_database(self):
        """Verify database exists and is accessible"""
        if not os.path.exists(self.db_path):
            raise EFAPIError(f"Database not found: {self.db_path}")
    
    def _get_connection(self):
        """Get secure database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(f"PRAGMA key = '{self.password}'")
            # Test connection
            conn.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            return conn
        except sqlite3.Error as e:
            raise EFAPIError(f"Database connection failed: {e}")
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_salt(self) -> str:
        """Generate random salt"""
        return os.urandom(16).hex()
    
    def _format_response(self, success: bool, data: Any = None, message: str = "") -> str:
        """Format API response as JSON"""
        response = {
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(response, indent=2, default=str)
    
    def _update_statistics_async(self):
        """Update statistics and financials asynchronously"""
        def update_stats():
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                today = date.today()
                now = datetime.now()
                
                # Calculate total users
                cursor.execute("SELECT COUNT(*) FROM CUSTOMERS")
                total_users = cursor.fetchone()[0]
                
                # Calculate total subscriptions
                cursor.execute("SELECT COUNT(*) FROM CUSTOMERS WHERE Subscription_Level = 'Premium'")
                premium_subs = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM CUSTOMERS WHERE Subscription_Level = 'Basic'")
                basic_subs = cursor.fetchone()[0]
                total_subscriptions = premium_subs + basic_subs
                
                # Calculate total shows bought
                cursor.execute("SELECT COUNT(*) FROM BUYS")
                total_shows_bought = cursor.fetchone()[0]
                
                # Calculate revenues
                cursor.execute("SELECT COALESCE(SUM(Cost), 0) FROM BUYS")
                total_revenue_buys = cursor.fetchone()[0]
                
                # Calculate subscription revenue (Basic: $30, Premium: $80)
                subscription_revenue = (basic_subs * 30.0) + (premium_subs * 80.0)
                total_combined_revenue = total_revenue_buys + subscription_revenue
                
                # Update statistics
                cursor.execute('''
                INSERT OR REPLACE INTO STATISTICS 
                (Date, Total_Shows_Bought, Total_Subscriptions, Total_Users, Last_Updated)
                VALUES (?, ?, ?, ?, ?)
                ''', (today, total_shows_bought, total_subscriptions, total_users, now))
                
                # Update financials
                cursor.execute('''
                INSERT OR REPLACE INTO FINANCIALS 
                (Date, Total_Revenue_Buys, Total_Revenue_Subscriptions, Total_Combined_Revenue, Last_Updated)
                VALUES (?, ?, ?, ?, ?)
                ''', (today, total_revenue_buys, subscription_revenue, total_combined_revenue, now))
                
                # Update favourite genres for users opted into marketing
                cursor.execute('''
                SELECT User_ID, Shows FROM CUSTOMERS 
                WHERE Marketing_Opt_In = 1 AND Shows IS NOT NULL AND Shows != ''
                ''')
                
                users_with_shows = cursor.fetchall()
                for user_id, shows_str in users_with_shows:
                    if shows_str:
                        show_ids = [int(x.strip()) for x in shows_str.split(',') if x.strip()]
                        if show_ids:
                            # Get genres for user's shows
                            placeholders = ','.join(['?' for _ in show_ids])
                            cursor.execute(f'''
                            SELECT Genre FROM SHOWS WHERE Show_ID IN ({placeholders})
                            ''', show_ids)
                            
                            genres = [row[0] for row in cursor.fetchall()]
                            if genres:
                                # Find most common genre
                                genre_counts = {}
                                for genre in genres:
                                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
                                
                                favourite_genre = max(genre_counts, key=genre_counts.get)
                                
                                # Update user's favourite genre
                                cursor.execute('''
                                UPDATE CUSTOMERS SET Favourite_Genre = ? WHERE User_ID = ?
                                ''', (favourite_genre, user_id))
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                print(f"Error updating statistics: {e}")
        
        # Run in separate thread to not block main execution
        thread = threading.Thread(target=update_stats)
        thread.daemon = True
        thread.start()
    
    def authenticate_user(self, username: str, password: str) -> str:
        """Authenticate user credentials"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID, Password_Hash, Salt, Username, Email, Subscription_Level, Total_Spent, Favourite_Genre, Shows, Marketing_Opt_In
                FROM CUSTOMERS 
                WHERE Username = ?
            """, (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, stored_hash, salt, username, email, subscription_level, total_spent, favourite_genre, shows, marketing_opt_in = result
                input_hash = self._hash_password(password, salt)
                
                if input_hash == stored_hash:
                    user_data = {
                        "user_id": user_id,
                        "username": username,
                        "email": email,
                        "subscription_level": subscription_level,
                        "total_spent": total_spent,
                        "favourite_genre": favourite_genre,
                        "shows": shows or "",
                        "marketing_opt_in": bool(marketing_opt_in)
                    }
                    return self._format_response(True, user_data, "Authentication successful")
                else:
                    return self._format_response(False, message="Invalid credentials")
            else:
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Authentication error: {e}")
    
    def create_user(self, username: str, email: str, password: str, subscription_level: str, marketing_opt_in: bool = False) -> str:
        """Create new user account with subscription charges"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID FROM CUSTOMERS 
                WHERE Username = ? OR Email = ?
            """, (username, email))
            
            if cursor.fetchone():
                conn.close()
                return self._format_response(False, message="Username or email already exists")
            
            salt = self._generate_salt()
            password_hash = self._hash_password(password, salt)
            
            # Calculate subscription cost
            subscription_cost = 30.00 if subscription_level == "Basic" else 80.00
            
            cursor.execute("""
                INSERT INTO CUSTOMERS (Username, Email, Password_Hash, Salt, Subscription_Level, Total_Spent, Favourite_Genre, Shows, Marketing_Opt_In)
                VALUES (?, ?, ?, ?, ?, ?, '', '', ?)
            """, (username, email, password_hash, salt, subscription_level, subscription_cost, marketing_opt_in))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Update statistics asynchronously
            self._update_statistics_async()
            
            return self._format_response(True, {"user_id": user_id, "charged": subscription_cost}, "User created successfully")
            
        except Exception as e:
            return self._format_response(False, message=f"User creation error: {e}")
    
    def get_all_shows(self) -> str:
        """Get all shows from database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Show_ID, Name, Release_Date, Rating, Director, Length, 
                       Genre, Access_Group, Cost_To_Buy
                FROM SHOWS
                ORDER BY Name
            """)
            
            shows = []
            for row in cursor.fetchall():
                shows.append({
                    "show_id": row[0],
                    "name": row[1],
                    "release_date": row[2],
                    "rating": row[3],
                    "director": row[4],
                    "length": row[5],
                    "genre": row[6],
                    "access_group": row[7],
                    "cost_to_buy": row[8]
                })
            
            conn.close()
            return self._format_response(True, shows, f"Retrieved {len(shows)} shows")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving shows: {e}")
    
    def search_shows(self, genre: str = None, rating: str = None, year: int = None, name: str = None) -> str:
        """Advanced search for shows with filtering"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT Show_ID, Name, Release_Date, Rating, Director, Length, 
                       Genre, Access_Group, Cost_To_Buy
                FROM SHOWS
                WHERE 1=1
            """
            params = []
            
            if genre:
                query += " AND Genre = ?"
                params.append(genre)
            
            if rating:
                query += " AND Rating = ?"
                params.append(rating)
            
            if year:
                query += " AND strftime('%Y', Release_Date) = ?"
                params.append(str(year))
            
            if name:
                query += " AND Name LIKE ?"
                params.append(f"%{name}%")
            
            query += " ORDER BY Name"
            
            cursor.execute(query, params)
            
            shows = []
            for row in cursor.fetchall():
                shows.append({
                    "show_id": row[0],
                    "name": row[1],
                    "release_date": row[2],
                    "rating": row[3],
                    "director": row[4],
                    "length": row[5],
                    "genre": row[6],
                    "access_group": row[7],
                    "cost_to_buy": row[8]
                })
            
            conn.close()
            return self._format_response(True, shows, f"Found {len(shows)} shows")
            
        except Exception as e:
            return self._format_response(False, message=f"Error searching shows: {e}")
    
    def get_shows_by_access(self, access_group: str) -> str:
        """Get shows by access group (Basic/Premium)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Show_ID, Name, Release_Date, Rating, Director, Length, 
                       Genre, Access_Group, Cost_To_Buy
                FROM SHOWS
                WHERE Access_Group = ?
                ORDER BY Name
            """, (access_group,))
            
            shows = []
            for row in cursor.fetchall():
                shows.append({
                    "show_id": row[0],
                    "name": row[1],
                    "release_date": row[2],
                    "rating": row[3],
                    "director": row[4],
                    "length": row[5],
                    "genre": row[6],
                    "access_group": row[7],
                    "cost_to_buy": row[8]
                })
            
            conn.close()
            return self._format_response(True, shows, f"Retrieved {len(shows)} {access_group} shows")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving shows: {e}")
    
    def get_available_genres(self) -> str:
        """Get all available genres"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT Genre FROM SHOWS ORDER BY Genre")
            genres = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return self._format_response(True, genres, f"Retrieved {len(genres)} genres")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving genres: {e}")
    
    def get_available_ratings(self) -> str:
        """Get all available ratings"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT Rating FROM SHOWS ORDER BY Rating")
            ratings = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return self._format_response(True, ratings, f"Retrieved {len(ratings)} ratings")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving ratings: {e}")
    
    def get_user_info(self, user_id: int) -> str:
        """Get user information"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID, Username, Email, Subscription_Level, Total_Spent, Favourite_Genre, Shows, Marketing_Opt_In
                FROM CUSTOMERS
                WHERE User_ID = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user = {
                    "user_id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "subscription_level": row[3],
                    "total_spent": row[4],
                    "favourite_genre": row[5],
                    "shows": row[6] or "",
                    "marketing_opt_in": bool(row[7])
                }
                return self._format_response(True, user, "User found")
            else:
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving user: {e}")
    
    def update_subscription(self, user_id: int, subscription_level: str) -> str:
        """Update user subscription level with pricing"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get current subscription
            cursor.execute("SELECT Subscription_Level, Total_Spent FROM CUSTOMERS WHERE User_ID = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return self._format_response(False, message="User not found")
            
            current_level, current_spent = result
            charge = 0.00
            
            # Calculate charge: Basic->Premium = $80, Premium->Basic = free
            if current_level == "Basic" and subscription_level == "Premium":
                charge = 80.00
            
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Subscription_Level = ?, Total_Spent = Total_Spent + ?
                WHERE User_ID = ?
            """, (subscription_level, charge, user_id))
            
            conn.commit()
            conn.close()
            
            # Update statistics asynchronously
            self._update_statistics_async()
            
            return self._format_response(True, {"charged": charge}, "Subscription updated successfully")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating subscription: {e}")
    
    def update_marketing_opt_in(self, user_id: int, marketing_opt_in: bool) -> str:
        """Update user marketing opt-in preference"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Marketing_Opt_In = ?
                WHERE User_ID = ?
            """, (marketing_opt_in, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                
                # Update statistics asynchronously
                self._update_statistics_async()
                
                return self._format_response(True, message="Marketing preference updated successfully")
            else:
                conn.close()
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating marketing preference: {e}")
    
    def add_show_to_user(self, user_id: int, show_id: int) -> str:
        """Add show to user's shows collection"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get user's current shows and subscription level
            cursor.execute("""
                SELECT Shows, Subscription_Level FROM CUSTOMERS WHERE User_ID = ?
            """, (user_id,))
            
            user_result = cursor.fetchone()
            if not user_result:
                conn.close()
                return self._format_response(False, message="User not found")
            
            current_shows, subscription_level = user_result
            
            # Get show details
            cursor.execute("SELECT Access_Group, Cost_To_Buy FROM SHOWS WHERE Show_ID = ?", (show_id,))
            show_result = cursor.fetchone()
            
            if not show_result:
                conn.close()
                return self._format_response(False, message="Show not found")
            
            access_group, cost_to_buy = show_result
            
            # Parse current shows
            if current_shows:
                show_ids = [int(x.strip()) for x in current_shows.split(',') if x.strip()]
            else:
                show_ids = []
            
            # Check if user already has this show
            if show_id in show_ids:
                conn.close()
                return self._format_response(False, message="Show already added to your collection")
            
            # Add show to user's collection
            show_ids.append(show_id)
            new_shows = ','.join(map(str, show_ids))
            
            # Calculate cost
            cost = 0.0
            if access_group == "Premium" and subscription_level == "Basic":
                cost = cost_to_buy or 0.0
            
            # Update user's shows and total spent
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Shows = ?, Total_Spent = Total_Spent + ?
                WHERE User_ID = ?
            """, (new_shows, cost, user_id))
            
            # Create buy record if there's a cost
            if cost > 0:
                buy_date = date.today()
                cursor.execute("""
                    INSERT INTO BUYS (User_ID, Show_ID, Buy_Date, Cost)
                    VALUES (?, ?, ?, ?)
                """, (user_id, show_id, buy_date, cost))
            
            conn.commit()
            conn.close()
            
            # Update statistics asynchronously
            self._update_statistics_async()
            
            return self._format_response(True, message="Show added successfully")
            
        except Exception as e:
            return self._format_response(False, message=f"Error adding show: {e}")
    
    def remove_show_from_user(self, user_id: int, show_id: int) -> str:
        """Remove show from user's collection"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get user's current shows
            cursor.execute("SELECT Shows FROM CUSTOMERS WHERE User_ID = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return self._format_response(False, message="User not found")
            
            current_shows = result[0]
            if not current_shows:
                conn.close()
                return self._format_response(False, message="No shows to remove")
            
            # Parse current shows
            show_ids = [int(x.strip()) for x in current_shows.split(',') if x.strip()]
            
            if show_id not in show_ids:
                conn.close()
                return self._format_response(False, message="Show not in your collection")
            
            # Remove show
            show_ids.remove(show_id)
            new_shows = ','.join(map(str, show_ids)) if show_ids else ''
            
            # Update user's shows
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Shows = ?
                WHERE User_ID = ?
            """, (new_shows, user_id))
            
            conn.commit()
            conn.close()
            
            # Update statistics asynchronously
            self._update_statistics_async()
            
            return self._format_response(True, message="Show removed successfully")
            
        except Exception as e:
            return self._format_response(False, message=f"Error removing show: {e}")
    
    def get_user_shows(self, user_id: int) -> str:
        """Get user's shows from their collection"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get user's shows
            cursor.execute("SELECT Shows FROM CUSTOMERS WHERE User_ID = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                conn.close()
                return self._format_response(True, [], "No shows found")
            
            show_ids = [int(x.strip()) for x in result[0].split(',') if x.strip()]
            
            if not show_ids:
                conn.close()
                return self._format_response(True, [], "No shows found")
            
            # Get show details
            placeholders = ','.join(['?' for _ in show_ids])
            cursor.execute(f"""
                SELECT s.Show_ID, s.Name, s.Release_Date, s.Rating, s.Director, 
                       s.Length, s.Genre, s.Access_Group, s.Cost_To_Buy
                FROM SHOWS s
                WHERE s.Show_ID IN ({placeholders})
                ORDER BY s.Name
            """, show_ids)
            
            shows = []
            for row in cursor.fetchall():
                shows.append({
                    "show_id": row[0],
                    "show_name": row[1],
                    "release_date": row[2],
                    "rating": row[3],
                    "director": row[4],
                    "length": row[5],
                    "genre": row[6],
                    "access_group": row[7],
                    "cost_to_buy": row[8]
                })
            
            conn.close()
            return self._format_response(True, shows, f"Retrieved {len(shows)} shows")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving user shows: {e}")
    
    def get_all_users(self) -> str:
        """Get all users (admin only)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID, Username, Email, Subscription_Level, Total_Spent, Favourite_Genre, Marketing_Opt_In
                FROM CUSTOMERS
                ORDER BY Username
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    "user_id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "subscription_level": row[3],
                    "total_spent": row[4],
                    "favourite_genre": row[5],
                    "marketing_opt_in": bool(row[6])
                })
            
            conn.close()
            return self._format_response(True, users, f"Retrieved {len(users)} users")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving users: {e}")
    
    def get_statistics(self) -> str:
        """Get system statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Date, Total_Shows_Bought, Total_Subscriptions, Total_Users, Last_Updated
                FROM STATISTICS
                ORDER BY Date DESC
                LIMIT 1
            """)
            
            stats_row = cursor.fetchone()
            
            cursor.execute("""
                SELECT Date, Total_Revenue_Buys, Total_Revenue_Subscriptions, 
                       Total_Combined_Revenue, Last_Updated
                FROM FINANCIALS
                ORDER BY Date DESC
                LIMIT 1
            """)
            
            finance_row = cursor.fetchone()
            conn.close()
            
            data = {
                "statistics": {
                    "date": stats_row[0] if stats_row else None,
                    "total_shows_bought": stats_row[1] if stats_row else 0,
                    "total_subscriptions": stats_row[2] if stats_row else 0,
                    "total_users": stats_row[3] if stats_row else 0,
                    "last_updated": stats_row[4] if stats_row else None
                },
                "financials": {
                    "date": finance_row[0] if finance_row else None,
                    "total_revenue_buys": finance_row[1] if finance_row else 0.00,
                    "total_revenue_subscriptions": finance_row[2] if finance_row else 0.00,
                    "total_combined_revenue": finance_row[3] if finance_row else 0.00,
                    "last_updated": finance_row[4] if finance_row else None
                }
            }
            
            return self._format_response(True, data, "Statistics retrieved")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving statistics: {e}")

    def get_finances(self) -> str:
        """Get financial data"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Date, Total_Revenue_Buys, Total_Revenue_Subscriptions, 
                       Total_Combined_Revenue, Last_Updated
                FROM FINANCIALS
                ORDER BY Date DESC
            """)
            
            finances = []
            for row in cursor.fetchall():
                finances.append({
                    "date": row[0],
                    "total_revenue_buys": row[1],
                    "total_revenue_subscriptions": row[2],
                    "total_combined_revenue": row[3],
                    "last_updated": row[4]
                })
            
            conn.close()
            return self._format_response(True, finances, f"Retrieved {len(finances)} financial records")
        
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving finances: {e}")

    def delete_user(self, user_id: int) -> str:
        """Delete user account"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete user's buys first
            cursor.execute("DELETE FROM BUYS WHERE User_ID = ?", (user_id,))
            
            # Delete user account
            cursor.execute("DELETE FROM CUSTOMERS WHERE User_ID = ?", (user_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                
                # Update statistics asynchronously
                self._update_statistics_async()
                
                return self._format_response(True, message="User account deleted successfully")
            else:
                conn.close()
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error deleting user: {e}")
    
    def change_password(self, user_id: int, new_password: str) -> str:
        """Change user password"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            salt = self._generate_salt()
            password_hash = self._hash_password(new_password, salt)
            
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Password_Hash = ?, Salt = ?
                WHERE User_ID = ?
            """, (password_hash, salt, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return self._format_response(True, message="Password changed successfully")
            else:
                conn.close()
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error changing password: {e}")
    
    def add_show(self, name: str, release_date: str, rating: str, director: str, 
                 length: int, genre: str, access_group: str, cost_to_buy: float) -> str:
        """Add new show to catalogue"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO SHOWS (Name, Release_Date, Rating, Director, Length, 
                                 Genre, Access_Group, Cost_To_Buy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, release_date, rating, director, length, genre, access_group, cost_to_buy))
            
            show_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Update statistics asynchronously
            self._update_statistics_async()
            
            return self._format_response(True, {"show_id": show_id}, "Show added successfully")
            
        except Exception as e:
            return self._format_response(False, message=f"Error adding show: {e}")
    
    def update_show_access(self, show_id: int, access_group: str) -> str:
        """Update show access group"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE SHOWS 
                SET Access_Group = ?
                WHERE Show_ID = ?
            """, (access_group, show_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return self._format_response(True, message="Show access group updated successfully")
            else:
                conn.close()
                return self._format_response(False, message="Show not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating show access: {e}")
    
    def update_show_cost(self, show_id: int, cost_to_buy: float) -> str:
        """Update show purchase cost"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE SHOWS 
                SET Cost_To_Buy = ?
                WHERE Show_ID = ?
            """, (cost_to_buy, show_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return self._format_response(True, message="Show purchase cost updated successfully")
            else:
                conn.close()
                return self._format_response(False, message="Show not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating show cost: {e}")
    
    def get_all_buys(self) -> str:
        """Get all current buys (admin only)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT b.Buy_ID, b.User_ID, c.Username, b.Show_ID, s.Name,
                       b.Buy_Date, b.Cost
                FROM BUYS b
                JOIN CUSTOMERS c ON b.User_ID = c.User_ID
                JOIN SHOWS s ON b.Show_ID = s.Show_ID
                ORDER BY b.Buy_Date DESC
            """)
            
            buys = []
            for row in cursor.fetchall():
                buys.append({
                    "buy_id": row[0],
                    "user_id": row[1],
                    "username": row[2],
                    "show_id": row[3],
                    "show_name": row[4],
                    "buy_date": row[5],
                    "cost": row[6]
                })
            
            conn.close()
            return self._format_response(True, buys, f"Retrieved {len(buys)} buys")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving buys: {e}")
    
    def search_shows_by_genre(self, genre: str) -> str:
        """Search shows by genre"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Show_ID, Name, Release_Date, Rating, Director, Length, 
                       Genre, Access_Group, Cost_To_Buy
                FROM SHOWS
                WHERE Genre LIKE ?
                ORDER BY Name
            """, (f"%{genre}%",))
            
            shows = []
            for row in cursor.fetchall():
                shows.append({
                    "show_id": row[0],
                    "name": row[1],
                    "release_date": row[2],
                    "rating": row[3],
                    "director": row[4],
                    "length": row[5],
                    "genre": row[6],
                    "access_group": row[7],
                    "cost_to_buy": row[8]
                })
            
            conn.close()
            return self._format_response(True, shows, f"Found {len(shows)} shows in genre: {genre}")
            
        except Exception as e:
            return self._format_response(False, message=f"Error searching shows: {e}")
    
    def update_user_favourite_genre(self, user_id: int, favourite_genre: str) -> str:
        """Update user's favourite genre"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Favourite_Genre = ?
                WHERE User_ID = ?
            """, (favourite_genre, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                
                # Update statistics asynchronously
                self._update_statistics_async()
                
                return self._format_response(True, message="Favourite genre updated successfully")
            else:
                conn.close()
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating favourite genre: {e}")

def main():
    parser = argparse.ArgumentParser(description="EasyFlix API")
    parser.add_argument('--command', required=True, help='API command to execute')
    parser.add_argument('--username', help='Username for authentication')
    parser.add_argument('--password', help='Password for authentication')
    parser.add_argument('--email', help='Email for user creation')
    parser.add_argument('--user_id', type=int, help='User ID')
    parser.add_argument('--show_id', type=int, help='Show ID')
    parser.add_argument('--access_group', help='Access group (Basic/Premium)')
    parser.add_argument('--subscription_level', help='Subscription level')
    parser.add_argument('--db_path', default='easyflix.db', help='Database path')
    parser.add_argument('--new_password', help='New password for password change')
    parser.add_argument('--name', help='Show name')
    parser.add_argument('--release_date', help='Show release date')
    parser.add_argument('--rating', help='Show rating')
    parser.add_argument('--director', help='Show director')
    parser.add_argument('--length', type=int, help='Show length in minutes')
    parser.add_argument('--genre', help='Show genre')
    parser.add_argument('--cost_to_buy', type=float, help='Show purchase cost')
    parser.add_argument('--buy_id', type=int, help='Buy ID')
    parser.add_argument('--favourite_genre', help='User favourite genre')
    parser.add_argument('--marketing_opt_in', action='store_true', help='Marketing opt-in flag')
    parser.add_argument('--year', type=int, help='Release year for search')
        
    args = parser.parse_args()
    
    try:
        api = EFAPI_Commands(args.db_path)
        
        # Get the method from the API class
        method = getattr(api, args.command, None)
        if not method:
            print(api._format_response(False, message=f"Unknown command: {args.command}"))
            return
        
        # Build kwargs based on command requirements
        kwargs = {}
        
        # Map arguments to parameters
        if args.username:
            kwargs['username'] = args.username
        if args.password:
            kwargs['password'] = args.password
        if args.email:
            kwargs['email'] = args.email
        if args.user_id:
            kwargs['user_id'] = args.user_id
        if args.show_id:
            kwargs['show_id'] = args.show_id
        if args.access_group:
            kwargs['access_group'] = args.access_group
        if args.subscription_level:
            kwargs['subscription_level'] = args.subscription_level
        if args.new_password:
            kwargs['new_password'] = args.new_password
        if args.name:
            kwargs['name'] = args.name
        if args.release_date:
            kwargs['release_date'] = args.release_date
        if args.rating:
            kwargs['rating'] = args.rating
        if args.director:
            kwargs['director'] = args.director
        if args.length:
            kwargs['length'] = args.length
        if args.genre:
            kwargs['genre'] = args.genre
        if args.cost_to_buy:
            kwargs['cost_to_buy'] = args.cost_to_buy
        if args.buy_id:
            kwargs['buy_id'] = args.buy_id
        if args.favourite_genre:
            kwargs['favourite_genre'] = args.favourite_genre
        if args.marketing_opt_in:
            kwargs['marketing_opt_in'] = args.marketing_opt_in
        if args.year:
            kwargs['year'] = args.year
        
        # Call the method with appropriate arguments
        result = method(**kwargs)
        print(result)
        
    except TypeError as e:
        print(EFAPI_Commands(args.db_path)._format_response(False, message=f"Invalid arguments for command {args.command}: {e}"))
    except EFAPIError as e:
        print(EFAPI_Commands(args.db_path)._format_response(False, message=str(e)))
    except Exception as e:
        print(EFAPI_Commands(args.db_path)._format_response(False, message=f"Unexpected error: {e}"))

if __name__ == "__main__":
    main()
