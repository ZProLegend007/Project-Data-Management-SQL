#!/usr/bin/env python3
"""
EasyFlix API (EFAPI.py)
Enhanced secure API interface for EasyFlix database operations
"""

import sqlite3
import argparse
import json
import hashlib
import os
import sys
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
    
    def authenticate_user(self, username: str, password: str) -> str:
        """Authenticate user credentials"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID, Password_Hash, Salt, Username, Email, Subscription_Level, 
                       Total_Spent, Favourite_Genre, Shows, Marketing_Opt_In
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
    
    def create_user(self, username: str, email: str, password: str, subscription_level: str, marketing_opt_in: str = "false") -> str:
        """Create new user account"""
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
            marketing_bool = marketing_opt_in.lower() == "true"
            
            cursor.execute("""
                INSERT INTO CUSTOMERS (Username, Email, Password_Hash, Salt, Subscription_Level, 
                                     Total_Spent, Favourite_Genre, Shows, Marketing_Opt_In)
                VALUES (?, ?, ?, ?, ?, 0.00, '', '', ?)
            """, (username, email, password_hash, salt, subscription_level, marketing_bool))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return self._format_response(True, {"user_id": user_id}, "User created successfully")
            
        except Exception as e:
            return self._format_response(False, message=f"User creation error: {e}")
    
    def get_shows_paginated(self, page: int = 1, limit: int = 20, sort_by: str = "name", 
                           sort_order: str = "ASC", genre: str = "", access_group: str = "") -> str:
        """Get paginated shows with sorting and filtering"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            offset = (page - 1) * limit
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if genre and genre.lower() != "all":
                where_conditions.append("Genre = ?")
                params.append(genre)
            
            if access_group and access_group.lower() != "all":
                where_conditions.append("Access_Group = ?")
                params.append(access_group)
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Valid sort columns
            valid_sorts = {
                "name": "Name",
                "rating": "Rating",
                "release_date": "Release_Date",
                "genre": "Genre",
                "length": "Length"
            }
            
            sort_column = valid_sorts.get(sort_by.lower(), "Name")
            order = "DESC" if sort_order.upper() == "DESC" else "ASC"
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM SHOWS{where_clause}", params)
            total_count = cursor.fetchone()[0]
            
            # Get paginated results
            cursor.execute(f"""
                SELECT Show_ID, Name, Release_Date, Rating, Director, Length, 
                       Genre, Access_Group, Cost_To_Rent
                FROM SHOWS{where_clause}
                ORDER BY {sort_column} {order}
                LIMIT ? OFFSET ?
            """, params + [limit, offset])
            
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
                    "cost_to_rent": row[8]
                })
            
            conn.close()
            
            result = {
                "shows": shows,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_count": total_count,
                    "total_pages": (total_count + limit - 1) // limit,
                    "has_next": page * limit < total_count,
                    "has_prev": page > 1
                }
            }
            
            return self._format_response(True, result, f"Retrieved {len(shows)} shows")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving shows: {e}")
    
    def get_all_shows(self) -> str:
        """Get all shows (for backward compatibility)"""
        return self.get_shows_paginated(page=1, limit=1000)
    
    def get_genres(self) -> str:
        """Get all unique genres"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT Genre FROM SHOWS ORDER BY Genre")
            genres = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return self._format_response(True, genres, f"Retrieved {len(genres)} genres")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving genres: {e}")
    
    def get_user_info(self, user_id: int) -> str:
        """Get user information"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID, Username, Email, Subscription_Level, Total_Spent, 
                       Favourite_Genre, Shows, Marketing_Opt_In
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
        """Update user subscription level"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Subscription_Level = ?
                WHERE User_ID = ?
            """, (subscription_level, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return self._format_response(True, message="Subscription updated successfully")
            else:
                conn.close()
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating subscription: {e}")
    
    def update_marketing_opt_in(self, user_id: int, opt_in: str) -> str:
        """Update user marketing opt-in preference"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            opt_in_bool = opt_in.lower() == "true"
            
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Marketing_Opt_In = ?
                WHERE User_ID = ?
            """, (opt_in_bool, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return self._format_response(True, message="Marketing preference updated successfully")
            else:
                conn.close()
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating marketing preference: {e}")
    
    def delete_user_account(self, user_id: int) -> str:
        """Delete user account and all associated data"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete user's rentals first
            cursor.execute("DELETE FROM RENTALS WHERE User_ID = ?", (user_id,))
            
            # Delete user account
            cursor.execute("DELETE FROM CUSTOMERS WHERE User_ID = ?", (user_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return self._format_response(True, message="Account deleted successfully")
            else:
                conn.close()
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error deleting account: {e}")
    
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
            cursor.execute("SELECT Access_Group, Cost_To_Rent FROM SHOWS WHERE Show_ID = ?", (show_id,))
            show_result = cursor.fetchone()
            
            if not show_result:
                conn.close()
                return self._format_response(False, message="Show not found")
            
            access_group, cost_to_rent = show_result
            
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
                cost = cost_to_rent or 0.0
            
            # Update user's shows and total spent
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Shows = ?, Total_Spent = Total_Spent + ?
                WHERE User_ID = ?
            """, (new_shows, cost, user_id))
            
            # Create rental record if there's a cost
            if cost > 0:
                rental_date = date.today()
                cursor.execute("""
                    INSERT INTO RENTALS (User_ID, Show_ID, Rental_Date, Expired, Cost)
                    VALUES (?, ?, ?, 0, ?)
                """, (user_id, show_id, rental_date, cost))
            
            conn.commit()
            conn.close()
            
            return self._format_response(True, message="Show added successfully")
            
        except Exception as e:
            return self._format_response(False, message=f"Error adding show: {e}")
    
    def create_rental(self, user_id: int, show_id: int) -> str:
        """Create new rental - redirects to add_show_to_user"""
        return self.add_show_to_user(user_id, show_id)
    
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
                       s.Length, s.Genre, s.Access_Group, s.Cost_To_Rent
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
                    "cost_to_rent": row[8]
                })
            
            conn.close()
            return self._format_response(True, shows, f"Retrieved {len(shows)} shows")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving user shows: {e}")
    
    def get_user_rentals(self, user_id: int) -> str:
        """Get user's rental history - redirects to get_user_shows"""
        return self.get_user_shows(user_id)
    
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
    
    # Additional methods for admin functionality
    def get_all_users(self) -> str:
        """Get all users (admin only)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID, Username, Email, Subscription_Level, Total_Spent, Favourite_Genre
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
                    "favourite_genre": row[5]
                })
            
            conn.close()
            return self._format_response(True, users, f"Retrieved {len(users)} users")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving users: {e}")

def main():
    parser = argparse.ArgumentParser(description="EasyFlix API")
    parser.add_argument('--command', required=True, help='API command to execute')
    parser.add_argument('--username', help='Username for authentication')
    parser.add_argument('--password', help='Password for authentication')
    parser.add_argument('--email', help='Email for user creation')
    parser.add_argument('--user_id', type=int, help='User ID')
    parser.add_argument('--show_id', type=int, help='Show ID')
    parser.add_argument('--subscription_level', help='Subscription level')
    parser.add_argument('--marketing_opt_in', help='Marketing opt-in (true/false)')
    parser.add_argument('--opt_in', help='Opt-in preference (true/false)')
    parser.add_argument('--db_path', default='easyflix.db', help='Database path')
    parser.add_argument('--new_password', help='New password for password change')
    parser.add_argument('--page', type=int, default=1, help='Page number for pagination')
    parser.add_argument('--limit', type=int, default=20, help='Items per page')
    parser.add_argument('--sort_by', default='name', help='Sort by field')
    parser.add_argument('--sort_order', default='ASC', help='Sort order (ASC/DESC)')
    parser.add_argument('--genre', help='Filter by genre')
    parser.add_argument('--access_group', help='Filter by access group')
        
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
        if args.subscription_level:
            kwargs['subscription_level'] = args.subscription_level
        if args.marketing_opt_in:
            kwargs['marketing_opt_in'] = args.marketing_opt_in
        if args.opt_in:
            kwargs['opt_in'] = args.opt_in
        if args.new_password:
            kwargs['new_password'] = args.new_password
        if args.page:
            kwargs['page'] = args.page
        if args.limit:
            kwargs['limit'] = args.limit
        if args.sort_by:
            kwargs['sort_by'] = args.sort_by
        if args.sort_order:
            kwargs['sort_order'] = args.sort_order
        if args.genre:
            kwargs['genre'] = args.genre
        if args.access_group:
            kwargs['access_group'] = args.access_group
        
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
