#!/usr/bin/env python3
"""
EasyFlix API (EFAPI.py)
Secure API interface for EasyFlix database operations with encrypted communication
"""

import sqlite3
import argparse
import json
import hashlib
import os
import sys
import base64
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EFAPIError(Exception):
    """Custom exception for EFAPI errors"""
    pass

class EncryptionManager:
    """Handles encryption and decryption of API communications"""
    
    def __init__(self, master_key: str = "EFS3cur3K3y"):
        self.master_key = master_key.encode()
        self.salt = b'EFS3cur3S@lt'
        
    def _derive_key(self) -> bytes:
        """Derive encryption key from master key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data and return base64 encoded string"""
        try:
            key = self._derive_key()
            f = Fernet(key)
            encrypted_data = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise EFAPIError(f"Encryption failed: {e}")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data"""
        try:
            key = self._derive_key()
            f = Fernet(key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise EFAPIError(f"Decryption failed: {e}")

class EFAPI_Commands:
    def __init__(self, db_path: str = "easyflix.db", password: str = "E@syFl1xP@ss"):
        self.db_path = db_path
        self.password = password
        self.encryption = EncryptionManager()
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
        """Format API response as JSON with encryption"""
        response = {
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        json_response = json.dumps(response, indent=2, default=str)
        
        try:
            encrypted_response = self.encryption.encrypt_data(json_response)
            return json.dumps({
                "encrypted": True,
                "data": encrypted_response
            })
        except Exception:
            # Fallback to unencrypted if encryption fails
            return json_response
    
    def _auto_update_statistics(self):
        """Auto update statistics - direct synchronous call"""
        try:
            self._update_statistics_sync()
        except Exception:
            # Silent fail for auto updates
            pass
    
    def _update_statistics_sync(self):
        """Update statistics and financials synchronously using optimized SQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            today = date.today()
            now = datetime.now()
            
            # Get aggregated statistics in one query using GROUP BY
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    SUM(CASE WHEN Subscription_Level = 'Premium' THEN 1 ELSE 0 END) as premium_subs,
                    SUM(CASE WHEN Subscription_Level = 'Basic' THEN 1 ELSE 0 END) as basic_subs,
                    COALESCE(SUM(Total_Spent), 0) as total_spent
                FROM CUSTOMERS
            """)
            
            result = cursor.fetchone()
            total_users, premium_subs, basic_subs, customer_spent = result
            total_subscriptions = premium_subs + basic_subs
            
            # Get total shows bought count
            cursor.execute("SELECT COUNT(*) FROM BUYS")
            total_shows_bought = cursor.fetchone()[0]
            
            # Get total revenue from buys
            cursor.execute("SELECT COALESCE(SUM(Cost), 0) FROM BUYS")
            total_revenue_buys = cursor.fetchone()[0]
            
            # Calculate subscription revenues
            basic_subscription_revenue = basic_subs * 30.0
            premium_subscription_revenue = premium_subs * 80.0
            total_subscription_revenue = basic_subscription_revenue + premium_subscription_revenue
            total_combined_revenue = total_revenue_buys + total_subscription_revenue
            
            # Update or insert statistics
            cursor.execute('SELECT Date FROM STATISTICS WHERE Date = ?', (today,))
            if cursor.fetchone():
                cursor.execute('''
                UPDATE STATISTICS 
                SET Total_Shows_Bought = ?, Total_Subscriptions = ?, Premium_Subscriptions = ?, 
                    Basic_Subscriptions = ?, Total_Users = ?, Last_Updated = ?
                WHERE Date = ?
                ''', (total_shows_bought, total_subscriptions, premium_subs, basic_subs, total_users, now, today))
            else:
                cursor.execute('''
                INSERT INTO STATISTICS 
                (Date, Total_Shows_Bought, Total_Subscriptions, Premium_Subscriptions, Basic_Subscriptions, Total_Users, Last_Updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (today, total_shows_bought, total_subscriptions, premium_subs, basic_subs, total_users, now))
            
            # Update or insert financials
            cursor.execute('SELECT Date FROM FINANCIALS WHERE Date = ?', (today,))
            if cursor.fetchone():
                cursor.execute('''
                UPDATE FINANCIALS 
                SET Total_Revenue_Buys = ?, Total_Revenue_Subscriptions = ?, Premium_Subscription_Revenue = ?,
                    Basic_Subscription_Revenue = ?, Total_Combined_Revenue = ?, Last_Updated = ?
                WHERE Date = ?
                ''', (total_revenue_buys, total_subscription_revenue, premium_subscription_revenue, 
                      basic_subscription_revenue, total_combined_revenue, now, today))
            else:
                cursor.execute('''
                INSERT INTO FINANCIALS 
                (Date, Total_Revenue_Buys, Total_Revenue_Subscriptions, Premium_Subscription_Revenue, 
                 Basic_Subscription_Revenue, Total_Combined_Revenue, Last_Updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (today, total_revenue_buys, total_subscription_revenue, premium_subscription_revenue,
                      basic_subscription_revenue, total_combined_revenue, now))
            
            # Update favourite genres for marketing opted-in users using optimized query
            cursor.execute('''
            SELECT c.User_ID, c.Shows, 
                   GROUP_CONCAT(s.Genre) as genres
            FROM CUSTOMERS c
            LEFT JOIN SHOWS s ON INSTR(',' || c.Shows || ',', ',' || s.Show_ID || ',') > 0
            WHERE c.Marketing_Opt_In = 1 AND c.Shows IS NOT NULL AND c.Shows != ''
            GROUP BY c.User_ID, c.Shows
            ''')
            
            users_with_genres = cursor.fetchall()
            for user_id, shows_str, genres_str in users_with_genres:
                if genres_str:
                    try:
                        # Count genre occurrences
                        genre_counts = {}
                        for genre in genres_str.split(','):
                            if genre and genre.strip():
                                clean_genre = genre.strip()
                                genre_counts[clean_genre] = genre_counts.get(clean_genre, 0) + 1
                        
                        if genre_counts:
                            # Find most common genre
                            favourite_genre = max(genre_counts, key=genre_counts.get)
                            
                            # Update user's favourite genre
                            cursor.execute('''
                            UPDATE CUSTOMERS SET Favourite_Genre = ? WHERE User_ID = ?
                            ''', (favourite_genre, user_id))
                    except (ValueError, TypeError):
                        continue
            
            conn.commit()
            conn.close()
            
            return {
                "total_users": total_users,
                "premium_subs": premium_subs,
                "basic_subs": basic_subs,
                "total_shows_bought": total_shows_bought,
                "total_revenue_buys": total_revenue_buys,
                "total_combined_revenue": total_combined_revenue
            }
            
        except Exception as e:
            raise EFAPIError(f"Error updating statistics: {e}")
    
    def update_statistics(self) -> str:
        """Manual command to update statistics and financials"""
        try:
            result = self._update_statistics_sync()
            return self._format_response(True, result, "Statistics updated successfully")
        except Exception as e:
            return self._format_response(False, message=f"Failed to update statistics: {e}")
    
    def authenticate_admin(self, username: str, password: str) -> str:
        """Authenticate admin credentials using stored database values"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Admin_ID, Password_Hash, Salt, Username, Role
                FROM ADMIN_CREDENTIALS 
                WHERE Username = ?
            """, (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                admin_id, stored_hash, salt, stored_username, role = result
                input_hash = self._hash_password(password, salt)
                
                if input_hash == stored_hash:
                    admin_data = {
                        "admin_id": admin_id,
                        "username": stored_username,
                        "role": role,
                        "access_level": "full"
                    }
                    return self._format_response(True, admin_data, "Admin authentication successful")
                else:
                    return self._format_response(False, message="Invalid admin credentials")
            else:
                return self._format_response(False, message="Admin user not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Admin authentication error: {e}")
    
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
            """, (username, email, password_hash, salt, subscription_level, subscription_cost, int(marketing_opt_in)))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Update statistics immediately
            self._auto_update_statistics()
            
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
        """Get all available genres using GROUP BY"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Genre, COUNT(*) as show_count 
                FROM SHOWS 
                GROUP BY Genre 
                ORDER BY Genre
            """)
            
            genres = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return self._format_response(True, genres, f"Retrieved {len(genres)} genres")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving genres: {e}")
    
    def get_available_ratings(self) -> str:
        """Get all available ratings using GROUP BY"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Rating, COUNT(*) as show_count 
                FROM SHOWS 
                GROUP BY Rating 
                ORDER BY Rating
            """)
            
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
            
            # Update statistics immediately
            self._auto_update_statistics()
            
            return self._format_response(True, {"charged": charge}, "Subscription updated successfully")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating subscription: {e}")
    
    def update_marketing_opt_in(self, user_id: int, marketing_opt_in: bool = False) -> str:
        """Update user marketing opt-in preference"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Marketing_Opt_In = ?
                WHERE User_ID = ?
            """, (int(marketing_opt_in), user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                
                # Update statistics immediately
                self._auto_update_statistics()
                
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
            
            # Update statistics immediately
            self._auto_update_statistics()
            
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
            
            # Update statistics immediately
            self._auto_update_statistics()
            
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
    
    def get_all_users(self, subscription_filter: str = None) -> str:
        """Get all users with optional subscription filtering (admin only)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT User_ID, Username, Email, Subscription_Level, Total_Spent, Favourite_Genre, Marketing_Opt_In
                FROM CUSTOMERS
            """
            params = []
            
            if subscription_filter and subscription_filter in ['Basic', 'Premium']:
                query += " WHERE Subscription_Level = ?"
                params.append(subscription_filter)
            
            query += " ORDER BY Username"
            
            cursor.execute(query, params)
            
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
            filter_msg = f" with {subscription_filter} subscription" if subscription_filter else ""
            return self._format_response(True, users, f"Retrieved {len(users)} users{filter_msg}")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving users: {e}")
    
    def get_users_by_subscription(self, subscription_level: str) -> str:
        """Get users filtered by subscription level using GROUP BY"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID, Username, Email, Subscription_Level, Total_Spent, 
                       Favourite_Genre, Marketing_Opt_In,
                       COUNT(*) OVER (PARTITION BY Subscription_Level) as subscription_count
                FROM CUSTOMERS
                WHERE Subscription_Level = ?
                ORDER BY Username
            """, (subscription_level,))
            
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
            return self._format_response(True, users, f"Retrieved {len(users)} {subscription_level} users")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving users by subscription: {e}")
    
    def get_statistics(self) -> str:
        """Get system statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get latest statistics
            cursor.execute("""
                SELECT Date, Total_Shows_Bought, Total_Subscriptions, Premium_Subscriptions, 
                       Basic_Subscriptions, Total_Users, Last_Updated
                FROM STATISTICS
                ORDER BY Date DESC
                LIMIT 1
            """)
            stats_row = cursor.fetchone()
            
            # Get latest financials
            cursor.execute("""
                SELECT Date, Total_Revenue_Buys, Total_Revenue_Subscriptions, 
                       Premium_Subscription_Revenue, Basic_Subscription_Revenue,
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
                    "premium_subscriptions": stats_row[3] if stats_row else 0,
                    "basic_subscriptions": stats_row[4] if stats_row else 0,
                    "total_users": stats_row[5] if stats_row else 0,
                    "last_updated": stats_row[6] if stats_row else None
                },
                "financials": {
                    "date": finance_row[0] if finance_row else None,
                    "total_revenue_buys": finance_row[1] if finance_row else 0.00,
                    "total_revenue_subscriptions": finance_row[2] if finance_row else 0.00,
                    "premium_subscription_revenue": finance_row[3] if finance_row else 0.00,
                    "basic_subscription_revenue": finance_row[4] if finance_row else 0.00,
                    "total_combined_revenue": finance_row[5] if finance_row else 0.00,
                    "last_updated": finance_row[6] if finance_row else None
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
                       Premium_Subscription_Revenue, Basic_Subscription_Revenue,
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
                    "premium_subscription_revenue": row[3],
                    "basic_subscription_revenue": row[4],
                    "total_combined_revenue": row[5],
                    "last_updated": row[6]
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
                
                # Update statistics immediately
                self._auto_update_statistics()
                
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
            
            # Update statistics immediately
            self._auto_update_statistics()
            
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
                
                # Update statistics immediately
                self._auto_update_statistics()
                
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
                
                # Update statistics immediately
                self._auto_update_statistics()
                
                return self._format_response(True, message="Show purchase cost updated successfully")
            else:
                conn.close()
                return self._format_response(False, message="Show not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating show cost: {e}")
    
    def get_all_buys(self) -> str:
        """Get all current buys using JOIN for better performance (admin only)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT b.Buy_ID, b.User_ID, c.Username, b.Show_ID, s.Name,
                       b.Buy_Date, b.Cost
                FROM BUYS b
                INNER JOIN CUSTOMERS c ON b.User_ID = c.User_ID
                INNER JOIN SHOWS s ON b.Show_ID = s.Show_ID
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
                
                # Update statistics immediately
                self._auto_update_statistics()
                
                return self._format_response(True, message="Favourite genre updated successfully")
            else:
                conn.close()
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating favourite genre: {e}")
    
    def delete_show(self, show_id: int) -> str:
        """Delete show from catalog"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete associated buys first
            cursor.execute("DELETE FROM BUYS WHERE Show_ID = ?", (show_id,))
            
            # Remove show from user collections
            cursor.execute("SELECT User_ID, Shows FROM CUSTOMERS WHERE Shows IS NOT NULL AND Shows != ''")
            users_with_shows = cursor.fetchall()
            
            for user_id, shows_str in users_with_shows:
                if shows_str:
                    show_ids = [int(x.strip()) for x in shows_str.split(',') if x.strip() and x.strip().isdigit()]
                    if show_id in show_ids:
                        show_ids.remove(show_id)
                        new_shows = ','.join(map(str, show_ids)) if show_ids else ''
                        cursor.execute("UPDATE CUSTOMERS SET Shows = ? WHERE User_ID = ?", (new_shows, user_id))
            
            # Delete the show
            cursor.execute("DELETE FROM SHOWS WHERE Show_ID = ?", (show_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                
                # Update statistics immediately
                self._auto_update_statistics()
                
                return self._format_response(True, message="Show deleted successfully")
            else:
                conn.close()
                return self._format_response(False, message="Show not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error deleting show: {e}")

def main():
    parser = argparse.ArgumentParser(description="EasyFlix API with Encrypted Communication")
    parser.add_argument('--command', help='API command to execute')
    parser.add_argument('--username', help='Username for authentication')
    parser.add_argument('--password', help='Password for authentication')
    parser.add_argument('--email', help='Email for user creation')
    parser.add_argument('--user_id', type=int, help='User ID')
    parser.add_argument('--show_id', type=int, help='Show ID')
    parser.add_argument('--access_group', help='Access group (Basic/Premium)')
    parser.add_argument('--subscription_level', help='Subscription level')
    parser.add_argument('--subscription_filter', help='Filter users by subscription level')
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
    parser.add_argument('--marketing_opt_in_true', action='store_true', help='Set marketing opt-in to true')
    parser.add_argument('--marketing_opt_in_false', action='store_true', help='Set marketing opt-in to false')
    parser.add_argument('--year', type=int, help='Release year for search')
    parser.add_argument('--encrypted_data', help='Encrypted request data')
        
    args = parser.parse_args()
    
    try:
        api = EFAPI_Commands(args.db_path)
        
        # Handle encrypted requests
        if args.encrypted_data:
            try:
                decrypted_request = api.encryption.decrypt_data(args.encrypted_data)
                request_data = json.loads(decrypted_request)
                command = request_data.get('command')
                kwargs = request_data.get('parameters', {})
                
                method = getattr(api, command, None)
                if not method:
                    print(api._format_response(False, message=f"Unknown command: {command}"))
                    return
                
                result = method(**kwargs)
                print(result)
                return
                
            except Exception as e:
                print(api._format_response(False, message=f"Error processing encrypted request: {e}"))
                return
        
        # Handle regular command-line requests (for backward compatibility)
        if not args.command:
            print(api._format_response(False, message="No command specified"))
            return
            
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
        if args.subscription_filter:
            kwargs['subscription_filter'] = args.subscription_filter
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
        if args.marketing_opt_in_true:
            kwargs['marketing_opt_in'] = True
        elif args.marketing_opt_in_false:
            kwargs['marketing_opt_in'] = False
        if args.year:
            kwargs['year'] = args.year
        
        # Call the method with appropriate arguments
        result = method(**kwargs)
        print(result)
        
    except TypeError as e:
        error_api = EFAPI_Commands(args.db_path if args.db_path else "easyflix.db")
        print(error_api._format_response(False, message=f"Invalid arguments for command {args.command}: {e}"))
    except EFAPIError as e:
        error_api = EFAPI_Commands(args.db_path if args.db_path else "easyflix.db") 
        print(error_api._format_response(False, message=str(e)))
    except Exception as e:
        error_api = EFAPI_Commands(args.db_path if args.db_path else "easyflix.db")
        print(error_api._format_response(False, message=f"Unexpected error: {e}"))

if __name__ == "__main__":
    main()
