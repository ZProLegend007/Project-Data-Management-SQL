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
    
    def authenticate_user(self, username: str, password: str) -> str:
        """Authenticate user credentials"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID, Password_Hash, Salt FROM CUSTOMERS 
                WHERE Username = ?
            """, (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, stored_hash, salt = result
                input_hash = self._hash_password(password, salt)
                
                if input_hash == stored_hash:
                    return self._format_response(True, {"user_id": user_id}, "Authentication successful")
                else:
                    return self._format_response(False, message="Invalid credentials")
            else:
                return self._format_response(False, message="User not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Authentication error: {e}")
    
    def create_user(self, username: str, email: str, password: str, subscription_level: str) -> str:
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
            
            cursor.execute("""
                INSERT INTO CUSTOMERS (Username, Email, Password_Hash, Salt, Subscription_Level, Total_Spent, Favourite_Genre)
                VALUES (?, ?, ?, ?, ?, 0.00, '')
            """, (username, email, password_hash, salt, subscription_level))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return self._format_response(True, {"user_id": user_id}, "User created successfully")
            
        except Exception as e:
            return self._format_response(False, message=f"User creation error: {e}")
    
    def get_all_shows(self) -> str:
        """Get all shows from database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Show_ID, Name, Release_Date, Rating, Director, Length, 
                       Genre, Access_Group, Cost_To_Rent
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
                    "cost_to_rent": row[8]
                })
            
            conn.close()
            return self._format_response(True, shows, f"Retrieved {len(shows)} shows")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving shows: {e}")
    
    def get_shows_by_access(self, access_group: str) -> str:
        """Get shows by access group (Basic/Premium)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Show_ID, Name, Release_Date, Rating, Director, Length, 
                       Genre, Access_Group, Cost_To_Rent
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
                    "cost_to_rent": row[8]
                })
            
            conn.close()
            return self._format_response(True, shows, f"Retrieved {len(shows)} {access_group} shows")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving shows: {e}")
    
    def get_user_info(self, user_id: int) -> str:
        """Get user information"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT User_ID, Username, Email, Subscription_Level, Total_Spent, Favourite_Genre
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
                    "favourite_genre": row[5]
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
    
    def create_rental(self, user_id: int, show_id: int) -> str:
        """Create new rental"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT Cost_To_Rent FROM SHOWS WHERE Show_ID = ?", (show_id,))
            show_result = cursor.fetchone()
            
            if not show_result:
                conn.close()
                return self._format_response(False, message="Show not found")
            
            cost = show_result[0] or 0.00
            rental_date = date.today()
            
            cursor.execute("""
                INSERT INTO RENTALS (User_ID, Show_ID, Rental_Date, Expired, Cost)
                VALUES (?, ?, ?, 0, ?)
            """, (user_id, show_id, rental_date, cost))
            
            rental_id = cursor.lastrowid
            
            cursor.execute("""
                UPDATE CUSTOMERS 
                SET Total_Spent = Total_Spent + ?
                WHERE User_ID = ?
            """, (cost, user_id))
            
            conn.commit()
            conn.close()
            
            return self._format_response(True, {"rental_id": rental_id}, "Rental created successfully")
            
        except Exception as e:
            return self._format_response(False, message=f"Error creating rental: {e}")
    
    def get_user_rentals(self, user_id: int) -> str:
        """Get user's rental history"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.Rental_ID, r.Show_ID, s.Name, r.Rental_Date, 
                       r.Return_Date, r.Expired, r.Cost
                FROM RENTALS r
                JOIN SHOWS s ON r.Show_ID = s.Show_ID
                WHERE r.User_ID = ?
                ORDER BY r.Rental_Date DESC
            """, (user_id,))
            
            rentals = []
            for row in cursor.fetchall():
                rentals.append({
                    "rental_id": row[0],
                    "show_id": row[1],
                    "show_name": row[2],
                    "rental_date": row[3],
                    "return_date": row[4],
                    "expired": bool(row[5]),
                    "cost": row[6]
                })
            
            conn.close()
            return self._format_response(True, rentals, f"Retrieved {len(rentals)} rentals")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving rentals: {e}")
    
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
    
    def get_statistics(self) -> str:
        """Get system statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Date, Total_Shows_Rented, Total_Subscriptions, Total_Users, Last_Updated
                FROM STATISTICS
                ORDER BY Date DESC
                LIMIT 1
            """)
            
            stats_row = cursor.fetchone()
            
            cursor.execute("""
                SELECT Date, Total_Revenue_Rent, Total_Revenue_Subscriptions, 
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
                    "total_shows_rented": stats_row[1] if stats_row else 0,
                    "total_subscriptions": stats_row[2] if stats_row else 0,
                    "total_users": stats_row[3] if stats_row else 0,
                    "last_updated": stats_row[4] if stats_row else None
                },
                "financials": {
                    "date": finance_row[0] if finance_row else None,
                    "total_revenue_rent": finance_row[1] if finance_row else 0.00,
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
                SELECT Date, Total_Revenue_Rent, Total_Revenue_Subscriptions, 
                       Total_Combined_Revenue, Last_Updated
                FROM FINANCIALS
                ORDER BY Date DESC
            """)
            
            finances = []
            for row in cursor.fetchall():
                finances.append({
                    "date": row[0],
                    "total_revenue_rent": row[1],
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
            
            # Delete user's rentals first
            cursor.execute("DELETE FROM RENTALS WHERE User_ID = ?", (user_id,))
            
            # Delete user account
            cursor.execute("DELETE FROM CUSTOMERS WHERE User_ID = ?", (user_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
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
    
    def add_show(self, name: str, release_date: str, rating: float, director: str, 
                 length: int, genre: str, access_group: str, cost_to_rent: float) -> str:
        """Add new show to catalogue"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO SHOWS (Name, Release_Date, Rating, Director, Length, 
                                 Genre, Access_Group, Cost_To_Rent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, release_date, rating, director, length, genre, access_group, cost_to_rent))
            
            show_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
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
    
    def update_show_cost(self, show_id: int, cost_to_rent: float) -> str:
        """Update show rental cost"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE SHOWS 
                SET Cost_To_Rent = ?
                WHERE Show_ID = ?
            """, (cost_to_rent, show_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return self._format_response(True, message="Show rental cost updated successfully")
            else:
                conn.close()
                return self._format_response(False, message="Show not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error updating show cost: {e}")
    
    def get_all_rentals(self) -> str:
        """Get all current rentals (admin only)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.Rental_ID, r.User_ID, c.Username, r.Show_ID, s.Name,
                       r.Rental_Date, r.Return_Date, r.Expired, r.Cost
                FROM RENTALS r
                JOIN CUSTOMERS c ON r.User_ID = c.User_ID
                JOIN SHOWS s ON r.Show_ID = s.Show_ID
                ORDER BY r.Rental_Date DESC
            """)
            
            rentals = []
            for row in cursor.fetchall():
                rentals.append({
                    "rental_id": row[0],
                    "user_id": row[1],
                    "username": row[2],
                    "show_id": row[3],
                    "show_name": row[4],
                    "rental_date": row[5],
                    "return_date": row[6],
                    "expired": bool(row[7]),
                    "cost": row[8]
                })
            
            conn.close()
            return self._format_response(True, rentals, f"Retrieved {len(rentals)} rentals")
            
        except Exception as e:
            return self._format_response(False, message=f"Error retrieving rentals: {e}")
    
    def return_rental(self, rental_id: int) -> str:
        """Return a rental"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            return_date = date.today()
            
            cursor.execute("""
                UPDATE RENTALS 
                SET Return_Date = ?, Expired = 1
                WHERE Rental_ID = ?
            """, (return_date, rental_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return self._format_response(True, message="Rental returned successfully")
            else:
                conn.close()
                return self._format_response(False, message="Rental not found")
                
        except Exception as e:
            return self._format_response(False, message=f"Error returning rental: {e}")
    
    def search_shows_by_genre(self, genre: str) -> str:
        """Search shows by genre"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Show_ID, Name, Release_Date, Rating, Director, Length, 
                       Genre, Access_Group, Cost_To_Rent
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
                    "cost_to_rent": row[8]
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
    parser.add_argument('--rating', type=float, help='Show rating')
    parser.add_argument('--director', help='Show director')
    parser.add_argument('--length', type=int, help='Show length in minutes')
    parser.add_argument('--genre', help='Show genre')
    parser.add_argument('--cost_to_rent', type=float, help='Show rental cost')
    parser.add_argument('--rental_id', type=int, help='Rental ID')
    parser.add_argument('--favourite_genre', help='User favourite genre')
        
    args = parser.parse_args()
    
    try:
        api = EFAPI(args.db_path)
        
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
        if args.cost_to_rent:
            kwargs['cost_to_rent'] = args.cost_to_rent
        if args.rental_id:
            kwargs['rental_id'] = args.rental_id
        if args.favourite_genre:
            kwargs['favourite_genre'] = args.favourite_genre
        
        # Call the method with appropriate arguments
        result = method(**kwargs)
        print(result)
        
    except TypeError as e:
        print(EFAPI(args.db_path)._format_response(False, message=f"Invalid arguments for command {args.command}: {e}"))
    except EFAPIError as e:
        print(EFAPI(args.db_path)._format_response(False, message=str(e)))
    except Exception as e:
        print(EFAPI(args.db_path)._format_response(False, message=f"Unexpected error: {e}"))

if __name__ == "__main__":
    main()
