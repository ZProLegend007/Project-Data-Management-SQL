#!/usr/bin/env python3
"""
EasyFlixAdmin - Administrator interface for EasyFlix streaming service with encrypted communication
"""

import subprocess
import json
import sys
import os
import asyncio
import base64
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, Center, Middle
from textual.widgets import Button, Input, Label, Select, Static, Header, Footer, LoadingIndicator, Checkbox, DataTable
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.reactive import reactive
from textual import work
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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
            raise Exception(f"Encryption failed: {e}")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data"""
        try:
            key = self._derive_key()
            f = Fernet(key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise Exception(f"Decryption failed: {e}")

class LoadingScreen(ModalScreen):
    """Loading screen modal"""
    
    def __init__(self, message: str = "Loading..."):
        super().__init__()
        self.message = message
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.message, classes="loading_text"),
            LoadingIndicator(),
            classes="loading_container"
        )

class DeleteConfirmModal(ModalScreen):
    """Modal for confirming user deletion"""
    
    def __init__(self, username: str, user_id: int):
        super().__init__()
        self.username = username
        self.user_id = user_id
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Delete User Account", classes="modal_title"),
            Static(f"Username: {self.username}", classes="modal_text"),
            Static("Are you sure you want to permanently delete this user account?", classes="modal_text"),
            Static("This action cannot be undone!", classes="modal_warning"),
            Horizontal(
                Button("Delete", id="confirm_delete", variant="error"),
                Button("Cancel", id="cancel_delete", variant="default"),
                classes="modal_buttons"
            ),
            classes="modal_container_fullscreen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_delete":
            self.dismiss({"action": "delete", "user_id": self.user_id})
        else:
            self.dismiss(None)

class DeleteShowConfirmModal(ModalScreen):
    """Modal for confirming show deletion"""
    
    def __init__(self, show_name: str, show_id: int):
        super().__init__()
        self.show_name = show_name
        self.show_id = show_id
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Delete Show", classes="modal_title"),
            Static(f"Show: {self.show_name}", classes="modal_text"),
            Static("Are you sure you want to permanently delete this show?", classes="modal_text"),
            Static("This action cannot be undone!", classes="modal_warning"),
            Horizontal(
                Button("Delete", id="confirm_delete_show", variant="error"),
                Button("Cancel", id="cancel_delete_show", variant="default"),
                classes="modal_buttons"
            ),
            classes="modal_container_fullscreen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_delete_show":
            self.dismiss({"action": "delete", "show_id": self.show_id})
        else:
            self.dismiss(None)

class UserManagementModal(ModalScreen):
    """Modal for managing user account"""
    
    def __init__(self, user: Dict):
        super().__init__()
        self.user = user
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Manage User: {self.user.get('username', 'Unknown')}", classes="modal_title"),
            Horizontal(
                Container(
                    Label("Current Information:"),
                    Static(f"Email: {self.user.get('email', 'N/A')}", classes="user_info_text"),
                    Static(f"Subscription: {self.user.get('subscription_level', 'N/A')}", classes="user_info_text"),
                    Static(f"Total Spent: ${self.user.get('total_spent', 0):.2f}", classes="user_info_text"),
                    Static(f"Favorite Genre: {self.user.get('favourite_genre', 'Not set')}", classes="user_info_text"),
                    Static(f"Marketing Opt-in: {'Yes' if self.user.get('marketing_opt_in', False) else 'No'}", classes="user_info_text"),
                    classes="user_info_column"
                ),
                Container(
                    Label("Management Actions:"),
                    Label("New Password:"),
                    Input(placeholder="Enter new password", password=True, id="new_password"),
                    Label("New Subscription Level:"),
                    Select([("Basic", "Basic"), ("Premium", "Premium")], 
                          value=self.user.get("subscription_level", "Basic"), id="subscription_select"),
                    classes="user_management_column"
                ),
                classes="user_management_layout"
            ),
            Horizontal(
                Button("Update User", id="update_user", variant="primary"),
                Button("Delete User", id="delete_user", variant="error"),
                Button("Cancel", id="cancel_manage", variant="default"),
                classes="modal_buttons"
            ),
            classes="modal_container_fullscreen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "update_user":
            new_password = self.query_one("#new_password", Input).value
            subscription = self.query_one("#subscription_select", Select).value
            
            self.dismiss({
                "action": "update",
                "user_id": self.user.get("user_id"),
                "new_password": new_password if new_password else None,
                "subscription_level": subscription
            })
        elif event.button.id == "delete_user":
            self.dismiss({
                "action": "delete",
                "user_id": self.user.get("user_id")
            })
        else:
            self.dismiss(None)

class AddShowModal(ModalScreen):
    """Modal for adding a new show"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Add New Show", classes="modal_title"),
            Horizontal(
                Container(
                    Label("Name:"),
                    Input(placeholder="Enter show name", id="show_name"),
                    Label("Director:"),
                    Input(placeholder="Enter director name", id="director"),
                    Label("Genre:"),
                    Select([
                        ("Action", "Action"), ("Adventure", "Adventure"), ("Animation", "Animation"),
                        ("Comedy", "Comedy"), ("Crime", "Crime"), ("Drama", "Drama"),
                        ("Fantasy", "Fantasy"), ("History", "History"), ("Romance", "Romance"),
                        ("Sci-Fi", "Sci-Fi"), ("Thriller", "Thriller")
                    ], id="genre_select"),
                    Label("Rating:"),
                    Select([("G", "G"), ("PG", "PG"), ("PG-13", "PG-13"), ("R", "R"), ("TV-14", "TV-14"), ("TV-MA", "TV-MA"), ("TV-PG", "TV-PG")], id="rating_select"),
                    classes="add_show_left_column"
                ),
                Container(
                    Label("Release Date (YYYY-MM-DD):"),
                    Input(placeholder="2024-01-01", id="release_date"),
                    Label("Length (minutes):"),
                    Input(placeholder="120", id="length"),
                    Label("Access Group:"),
                    Select([("Basic", "Basic"), ("Premium", "Premium")], id="access_group_select"),
                    Container(
                        Label("Cost to Buy:"),
                        Input(placeholder="0.00", id="cost_to_buy"),
                        id="cost_container",
                        classes="cost_container hidden"
                    ),
                    classes="add_show_right_column"
                ),
                classes="add_show_layout"
            ),
            Horizontal(
                Button("Add Show", id="add_show", variant="primary"),
                Button("Cancel", id="cancel_add", variant="default"),
                classes="modal_buttons"
            ),
            classes="modal_container_fullscreen"
        )
    
    def on_mount(self) -> None:
        access_select = self.query_one("#access_group_select", Select)
        access_select.watch(lambda: self.toggle_cost_visibility())
    
    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "access_group_select":
            self.toggle_cost_visibility()
    
    def toggle_cost_visibility(self) -> None:
        try:
            access_group = self.query_one("#access_group_select", Select).value
            cost_container = self.query_one("#cost_container")
            
            if access_group == "Premium":
                cost_container.remove_class("hidden")
            else:
                cost_container.add_class("hidden")
        except Exception:
            pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_show":
            name = self.query_one("#show_name", Input).value
            release_date = self.query_one("#release_date", Input).value
            rating = self.query_one("#rating_select", Select).value
            director = self.query_one("#director", Input).value
            length = self.query_one("#length", Input).value
            genre = self.query_one("#genre_select", Select).value
            access_group = self.query_one("#access_group_select", Select).value
            
            if all([name, release_date, rating, director, length, genre, access_group]):
                try:
                    length_int = int(length)
                    
                    if access_group == "Basic":
                        cost_float = 0.0
                    else:
                        cost_to_buy = self.query_one("#cost_to_buy", Input).value
                        cost_float = float(cost_to_buy) if cost_to_buy else 0.0
                    
                    self.dismiss({
                        "action": "add",
                        "name": name,
                        "release_date": release_date,
                        "rating": rating,
                        "director": director,
                        "length": length_int,
                        "genre": genre,
                        "access_group": access_group,
                        "cost_to_buy": cost_float
                    })
                except ValueError:
                    self.app.notify("Please enter valid numbers for length and cost", severity="error")
            else:
                self.app.notify("Please fill in all required fields", severity="warning")
        else:
            self.dismiss(None)

class EditShowModal(ModalScreen):
    """Modal for editing show access and cost"""
    
    def __init__(self, show: Dict):
        super().__init__()
        self.show = show
    
    def compose(self) -> ComposeResult:
        cost_value = self.show.get("cost_to_buy", 0.0)
        cost_str = str(cost_value) if cost_value is not None else "0.0"
        
        yield Container(
            Static(f"Edit Show: {self.show.get('name', 'Unknown')}", classes="modal_title"),
            Container(
                Label("Access Group:"),
                Select([("Basic", "Basic"), ("Premium", "Premium")], 
                      value=self.show.get("access_group", "Basic"), id="access_group_select"),
                Label("Cost to Buy:"),
                Input(placeholder="0.00", value=cost_str, id="cost_to_buy"),
                Horizontal(
                    Button("Update Show", id="update_show", variant="primary"),
                    Button("Delete Show", id="delete_show", variant="error"),
                    Button("Cancel", id="cancel_edit", variant="default"),
                    classes="modal_buttons"
                ),
                classes="edit_show_form"
            ),
            classes="modal_container_fullscreen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "update_show":
            access_group = self.query_one("#access_group_select", Select).value
            cost_to_buy = self.query_one("#cost_to_buy", Input).value
            
            try:
                if access_group == "Basic":
                    cost_float = 0.0
                else:
                    cost_float = float(cost_to_buy) if cost_to_buy else 0.0
                
                self.dismiss({
                    "action": "update",
                    "show_id": self.show.get("show_id"),
                    "access_group": access_group,
                    "cost_to_buy": cost_float
                })
            except ValueError:
                self.app.notify("Please enter a valid cost", severity="error")
        elif event.button.id == "delete_show":
            self.dismiss({
                "action": "delete",
                "show_id": self.show.get("show_id"),
                "show_name": self.show.get("name", "Unknown")
            })
        else:
            self.dismiss(None)

class LoginScreen(Screen):
    """Login screen for admin authentication"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("EasyFlix Admin Portal", classes="title"),
            Container(
                Label("Admin Username:"),
                Input(placeholder="Enter admin username", id="username"),
                Label("Admin Password:"),
                Input(placeholder="Enter admin password", password=True, id="password"),
                Button("Login", id="login_btn", variant="primary"),
                classes="login_form"
            ),
            classes="login_container"
        )
        yield Footer()

    @work(exclusive=True)
    async def authenticate_admin(self, username: str, password: str):
        """Authenticate admin asynchronously"""
        result = await asyncio.to_thread(
            self.app.call_api, "authenticate_admin", 
            username=username, password=password
        )
        
        if result is not None and result.get("success"):
            admin_data = result.get("data", {})
            self.app.current_admin = admin_data
            self.app.pop_screen()
            self.app.push_screen(MainScreen())
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Login failed: " + error_msg, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_btn":
            username = self.query_one("#username", Input).value
            password = self.query_one("#password", Input).value
            
            if username and password:
                self.authenticate_admin(username, password)
            else:
                self.notify("Please enter both username and password", severity="warning")

class MainScreen(Screen):
    """Main admin application screen"""
    
    current_view = reactive("dashboard")
    users_cache = []
    shows_cache = []
    buys_cache = []
    statistics_cache = {}
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Container(
                Static("Admin Menu", classes="menu_title"),
                Button("Dashboard", id="dashboard_btn", variant="primary", classes="sidebar_button"),
                Button("User Management", id="users_btn", variant="default", classes="sidebar_button"),
                Button("Content Management", id="content_btn", variant="default", classes="sidebar_button"),
                Button("Financial Reports", id="financials_btn", variant="default", classes="sidebar_button"),
                Button("System Statistics", id="statistics_btn", variant="default", classes="sidebar_button"),
                Button("Purchase History", id="buys_btn", variant="default", classes="sidebar_button"),
                Button("Logout", id="logout_btn", variant="error", classes="sidebar_button"),
                classes="sidebar"
            ),
            Container(
                id="content_area",
                classes="content"
            ),
            classes="main_layout"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.load_dashboard()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "dashboard_btn":
            self.current_view = "dashboard"
            self.update_sidebar_buttons("dashboard_btn")
            self.load_dashboard()
        elif event.button.id == "users_btn":
            self.current_view = "users"
            self.update_sidebar_buttons("users_btn")
            self.load_users()
        elif event.button.id == "content_btn":
            self.current_view = "content"
            self.update_sidebar_buttons("content_btn")
            self.load_content()
        elif event.button.id == "financials_btn":
            self.current_view = "financials"
            self.update_sidebar_buttons("financials_btn")
            self.load_financials()
        elif event.button.id == "statistics_btn":
            self.current_view = "statistics"
            self.update_sidebar_buttons("statistics_btn")
            self.load_statistics()
        elif event.button.id == "buys_btn":
            self.current_view = "buys"
            self.update_sidebar_buttons("buys_btn")
            self.load_buys()
        elif event.button.id == "logout_btn":
            self.app.current_admin = None
            self.app.switch_screen(LoginScreen())
        elif event.button.id and event.button.id.startswith("manage_user_"):
            user_id = int(event.button.id.replace("manage_user_", ""))
            self.handle_manage_user(user_id)
        elif event.button.id == "add_show_btn":
            self.handle_add_show()
        elif event.button.id and event.button.id.startswith("edit_show_"):
            show_id = int(event.button.id.replace("edit_show_", ""))
            self.handle_edit_show(show_id)

    def update_sidebar_buttons(self, active_button_id: str):
        """Update sidebar button styles"""
        button_ids = ["dashboard_btn", "users_btn", "content_btn", "financials_btn", "statistics_btn", "buys_btn"]
        for btn_id in button_ids:
            button = self.query_one(f"#{btn_id}", Button)
            if btn_id == active_button_id:
                button.variant = "primary"
            else:
                button.variant = "default"

    def clear_content_area(self):
        """Safely clear content area"""
        content = self.query_one("#content_area")
        try:
            content.remove_children()
        except Exception:
            pass

    @work(exclusive=True)
    async def load_dashboard_async(self):
        """Load dashboard data asynchronously"""
        self.clear_content_area()
        content = self.query_one("#content_area")
        
        content.mount(Static("Admin Dashboard", classes="content_title"))
        content.mount(LoadingIndicator())
        
        stats_result = await asyncio.to_thread(self.app.call_api, "get_statistics")
        
        try:
            content.query_one(LoadingIndicator).remove()
        except:
            pass
        
        if stats_result is not None and stats_result.get("success"):
            data = stats_result.get("data", {})
            stats = data.get("statistics", {})
            financials = data.get("financials", {})
            
            dashboard_widgets = [
                Container(
                    Static("System Overview", classes="section_title"),
                    Static(f"Total Users: {stats.get('total_users', 0)}", classes="stat_item"),
                    Static(f"Premium Subscribers: {stats.get('premium_subscriptions', 0)}", classes="stat_item"),
                    Static(f"Basic Subscribers: {stats.get('basic_subscriptions', 0)}", classes="stat_item"),
                    Static(f"Total Shows Purchased: {stats.get('total_shows_bought', 0)}", classes="stat_item"),
                    classes="dashboard_section"
                ),
                Container(
                    Static("Financial Summary", classes="section_title"),
                    Static(f"Total Revenue: ${financials.get('total_combined_revenue', 0):.2f}", classes="stat_item"),
                    Static(f"Subscription Revenue: ${financials.get('total_revenue_subscriptions', 0):.2f}", classes="stat_item"),
                    Static(f"Purchase Revenue: ${financials.get('total_revenue_buys', 0):.2f}", classes="stat_item"),
                    Static(f"Last Updated: {stats.get('last_updated', 'N/A')}", classes="stat_item"),
                    classes="dashboard_section"
                )
            ]
            
            for widget in dashboard_widgets:
                content.mount(widget)
        else:
            content.mount(Static("Error loading dashboard data", classes="error_message"))

    def load_dashboard(self) -> None:
        self.load_dashboard_async()

    @work(exclusive=True)
    async def load_users_async(self):
        """Load users data asynchronously"""
        self.clear_content_area()
        content = self.query_one("#content_area")
        
        content.mount(Static("User Management", classes="content_title"))
        content.mount(LoadingIndicator())
        
        result = await asyncio.to_thread(self.app.call_api, "get_all_users")
        
        content.remove_children()
        content.mount(Static("User Management", classes="content_title"))
        
        if result is not None and result.get("success"):
            users = result.get("data", [])
            self.users_cache = users
            
            if users:
                for user in users:
                    user_widget = Container(
                        Static(f"User: {user.get('username', '')}", classes="user_title"),
                        Static(f"Email: {user.get('email', '')}", classes="user_info"),
                        Static(f"Subscription: {user.get('subscription_level', '')}", classes="user_info"),
                        Static(f"Total Spent: ${user.get('total_spent', 0):.2f}", classes="user_info"),
                        Static(f"Favorite Genre: {user.get('favourite_genre', 'Not set')}", classes="user_info"),
                        Static(f"Marketing Opt-in: {'Yes' if user.get('marketing_opt_in', False) else 'No'}", classes="user_info"),
                        Button(f"Manage User", id=f"manage_user_{user.get('user_id')}", variant="primary", classes="manage_button"),
                        classes="user_card"
                    )
                    content.mount(user_widget)
            else:
                content.mount(Static("No users found", classes="empty_message"))
        else:
            content.mount(Static("Error loading users", classes="error_message"))

    def load_users(self) -> None:
        self.load_users_async()

    def handle_manage_user(self, user_id: int) -> None:
        """Handle user management"""
        user = next((u for u in self.users_cache if u["user_id"] == user_id), None)
        if user:
            def handle_modal_result(result):
                if result:
                    if result.get("action") == "delete":
                        self.delete_user(user_id)
                    elif result.get("action") == "update":
                        self.update_user(result)
            
            self.app.push_screen(
                UserManagementModal(user),
                handle_modal_result
            )

    @work(exclusive=True)
    async def update_user(self, update_data: Dict):
        """Update user asynchronously"""
        user_id = update_data["user_id"]
        
        if update_data.get("new_password"):
            password_result = await asyncio.to_thread(
                self.app.call_api, "change_password", 
                user_id=user_id, new_password=update_data["new_password"]
            )
            if not (password_result and password_result.get("success")):
                self.notify("Failed to update password", severity="error")
                return
        
        subscription_result = await asyncio.to_thread(
            self.app.call_api, "update_subscription", 
            user_id=user_id, subscription_level=update_data["subscription_level"]
        )
        
        if subscription_result and subscription_result.get("success"):
            self.notify("User updated successfully!", severity="information")
            self.load_users()
        else:
            self.notify("Failed to update user", severity="error")

    @work(exclusive=True)
    async def delete_user(self, user_id: int):
        """Delete user asynchronously"""
        result = await asyncio.to_thread(self.app.call_api, "delete_user", user_id=user_id)
        
        if result is not None and result.get("success"):
            self.notify("User deleted successfully!", severity="information")
            self.load_users()
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Failed to delete user: " + error_msg, severity="error")

    @work(exclusive=True)
    async def load_content_async(self):
        """Load content management asynchronously"""
        self.clear_content_area()
        content = self.query_one("#content_area")
        
        content.mount(Static("Content Management", classes="content_title"))
        content.mount(Button("Add New Show", id="add_show_btn", variant="success"))
        content.mount(LoadingIndicator())
        
        result = await asyncio.to_thread(self.app.call_api, "get_all_shows")
        
        try:
            content.query_one(LoadingIndicator).remove()
        except:
            pass
        
        if result is not None and result.get("success"):
            shows = result.get("data", [])
            self.shows_cache = shows
            
            if shows:
                show_rows = []
                for i in range(0, len(shows), 3):
                    row_shows = shows[i:i+3]
                    row_cards = []
                    for show in row_shows:
                        row_cards.append(self.create_admin_show_card(show))
                    
                    show_rows.append(Horizontal(*row_cards, classes="shows_row"))
                
                shows_container = Vertical(*show_rows, classes="shows_main_container")
                content.mount(shows_container)
            else:
                content.mount(Static("No shows found", classes="empty_message"))
        else:
            content.mount(Static("Error loading shows", classes="error_message"))

    def create_admin_show_card(self, show: Dict) -> Container:
        """Create an admin show card widget"""
        cost_to_buy = show.get('cost_to_buy')
        cost_display = f"${cost_to_buy:.2f}" if cost_to_buy is not None else "Free"
        
        return Container(
            Static(show.get("name", "Unknown"), classes="show_title"),
            Static(f"Genre: {show.get('genre', 'N/A')}", classes="show_info"),
            Static(f"Rating: {show.get('rating', 'N/A')}", classes="show_info"),
            Static(f"Director: {show.get('director', 'N/A')}", classes="show_info"),
            Static(f"Length: {show.get('length', 'N/A')} min", classes="show_info"),
            Static(f"Release: {show.get('release_date', 'N/A')}", classes="show_info"),
            Static(f"Access: {show.get('access_group', '')}", classes="show_info"),
            Static(f"Cost: {cost_display}", classes="show_info"),
            Button("Edit", id=f"edit_show_{show.get('show_id')}", variant="warning", classes="edit_button"),
            classes="admin_show_card"
        )

    def load_content(self) -> None:
        self.load_content_async()

    def handle_add_show(self) -> None:
        """Handle adding a new show"""
        def handle_modal_result(result):
            if result and result.get("action") == "add":
                self.add_show(result)
        
        self.app.push_screen(AddShowModal(), handle_modal_result)

    @work(exclusive=True)
    async def add_show(self, show_data: Dict):
        """Add show asynchronously"""
        result = await asyncio.to_thread(
            self.app.call_api, "add_show",
            name=show_data["name"],
            release_date=show_data["release_date"],
            rating=show_data["rating"],
            director=show_data["director"],
            length=show_data["length"],
            genre=show_data["genre"],
            access_group=show_data["access_group"],
            cost_to_buy=show_data["cost_to_buy"]
        )
        
        if result is not None and result.get("success"):
            self.notify("Show added successfully!", severity="information")
            self.load_content()
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Failed to add show: " + error_msg, severity="error")

    def handle_edit_show(self, show_id: int) -> None:
        """Handle editing a show"""
        show = next((s for s in self.shows_cache if s["show_id"] == show_id), None)
        if show:
            def handle_modal_result(result):
                if result:
                    if result.get("action") == "update":
                        self.update_show(result)
                    elif result.get("action") == "delete":
                        self.confirm_delete_show(result["show_id"], result["show_name"])
            
            self.app.push_screen(EditShowModal(show), handle_modal_result)

    def confirm_delete_show(self, show_id: int, show_name: str) -> None:
        """Confirm show deletion"""
        def handle_delete_result(result):
            if result and result.get("action") == "delete":
                self.delete_show(show_id)
        
        self.app.push_screen(
            DeleteShowConfirmModal(show_name, show_id),
            handle_delete_result
        )

    @work(exclusive=True)
    async def delete_show(self, show_id: int):
        """Delete show asynchronously"""
        result = await asyncio.to_thread(self.app.call_api, "delete_show", show_id=show_id)
        
        if result is not None and result.get("success"):
            self.notify("Show deleted successfully!", severity="information")
            self.load_content()
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Failed to delete show: " + error_msg, severity="error")

    @work(exclusive=True)
    async def update_show(self, show_data: Dict):
        """Update show asynchronously"""
        access_result = await asyncio.to_thread(
            self.app.call_api, "update_show_access",
            show_id=show_data["show_id"],
            access_group=show_data["access_group"]
        )
        
        cost_result = await asyncio.to_thread(
            self.app.call_api, "update_show_cost",
            show_id=show_data["show_id"],
            cost_to_buy=show_data["cost_to_buy"]
        )
        
        if (access_result is not None and access_result.get("success") and 
            cost_result is not None and cost_result.get("success")):
            self.notify("Show updated successfully!", severity="information")
            self.load_content()
        else:
            self.notify("Failed to update show", severity="error")

    @work(exclusive=True)
    async def load_financials_async(self):
        """Load financial data asynchronously"""
        self.clear_content_area()
        content = self.query_one("#content_area")
        
        content.mount(Static("Financial Reports", classes="content_title"))
        content.mount(LoadingIndicator())
        
        result = await asyncio.to_thread(self.app.call_api, "get_finances")
        
        try:
            content.query_one(LoadingIndicator).remove()
        except:
            pass
        
        if result is not None and result.get("success"):
            finances = result.get("data", [])
            
            if finances:
                for finance in finances:
                    finance_widget = Container(
                        Static(f"Date: {finance.get('date', '')}", classes="finance_title"),
                        Static(f"Total Revenue: ${finance.get('total_combined_revenue', 0):.2f}", classes="finance_info"),
                        Static(f"Subscription Revenue: ${finance.get('total_revenue_subscriptions', 0):.2f}", classes="finance_info"),
                        Static(f"Purchase Revenue: ${finance.get('total_revenue_buys', 0):.2f}", classes="finance_info"),
                        Static(f"Premium Subscriptions: ${finance.get('premium_subscription_revenue', 0):.2f}", classes="finance_info"),
                        Static(f"Basic Subscriptions: ${finance.get('basic_subscription_revenue', 0):.2f}", classes="finance_info"),
                        classes="finance_card"
                    )
                    content.mount(finance_widget)
            else:
                content.mount(Static("No financial data found", classes="empty_message"))
        else:
            content.mount(Static("Error loading financial data", classes="error_message"))

    def load_financials(self) -> None:
        self.load_financials_async()

    @work(exclusive=True)
    async def load_statistics_async(self):
        """Load statistics asynchronously"""
        self.clear_content_area()
        content = self.query_one("#content_area")
        
        content.mount(Static("System Statistics", classes="content_title"))
        content.mount(LoadingIndicator())
        
        result = await asyncio.to_thread(self.app.call_api, "get_statistics")
        
        try:
            content.query_one(LoadingIndicator).remove()
        except:
            pass
        
        if result is not None and result.get("success"):
            data = result.get("data", {})
            stats = data.get("statistics", {})
            
            stats_widget = Container(
                Static("Current System Statistics", classes="section_title"),
                Static(f"Date: {stats.get('date', 'N/A')}", classes="stat_item"),
                Static(f"Total Users: {stats.get('total_users', 0)}", classes="stat_item"),
                Static(f"Total Subscriptions: {stats.get('total_subscriptions', 0)}", classes="stat_item"),
                Static(f"Premium Subscriptions: {stats.get('premium_subscriptions', 0)}", classes="stat_item"),
                Static(f"Basic Subscriptions: {stats.get('basic_subscriptions', 0)}", classes="stat_item"),
                Static(f"Total Shows Purchased: {stats.get('total_shows_bought', 0)}", classes="stat_item"),
                Static(f"Last Updated: {stats.get('last_updated', 'N/A')}", classes="stat_item"),
                classes="statistics_section"
            )
            content.mount(stats_widget)
        else:
            content.mount(Static("Error loading statistics", classes="error_message"))

    def load_statistics(self) -> None:
        self.load_statistics_async()

    @work(exclusive=True)
    async def load_buys_async(self):
        """Load purchase history asynchronously"""
        self.clear_content_area()
        content = self.query_one("#content_area")
        
        content.mount(Static("Purchase History", classes="content_title"))
        content.mount(LoadingIndicator())
        
        result = await asyncio.to_thread(self.app.call_api, "get_all_buys")
        
        content.remove_children()
        content.mount(Static("Purchase History", classes="content_title"))
        
        if result is not None and result.get("success"):
            buys = result.get("data", [])
            self.buys_cache = buys
            
            if buys:
                buy_rows = []
                for i in range(0, len(buys), 2):
                    row_buys = buys[i:i+2]
                    row_cards = []
                    for buy in row_buys:
                        buy_widget = Container(
                            Static(f"Purchase ID: {buy.get('buy_id', '')}", classes="buy_title"),
                            Static(f"User: {buy.get('username', '')} (ID: {buy.get('user_id', '')})", classes="buy_info"),
                            Static(f"Show: {buy.get('show_name', '')} (ID: {buy.get('show_id', '')})", classes="buy_info"),
                            Static(f"Date: {buy.get('buy_date', '')}", classes="buy_info"),
                            Static(f"Cost: ${buy.get('cost', 0):.2f}", classes="buy_info"),
                            classes="buy_card_two_column"
                        )
                        row_cards.append(buy_widget)
                    
                    buy_rows.append(Horizontal(*row_cards, classes="buy_row"))
                
                buys_container = Vertical(*buy_rows, classes="buys_main_container")
                content.mount(buys_container)
            else:
                content.mount(Static("No purchases found", classes="empty_message"))
        else:
            content.mount(Static("Error loading purchase history", classes="error_message"))

    def load_buys(self) -> None:
        self.load_buys_async()

class EasyFlixAdminApp(App):
    """Main EasyFlix Admin Application"""
    
    CSS = """
    Screen {
        background: #1a1a2e;
        color: white;
        width: 100%;
        height: 100%;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: #e94560;
        margin: 2;
        content-align: center middle;
    }
    
    .content_title {
        text-style: bold;
        color: #e94560;
        margin: 1;
        padding: 1;
    }
    
    .section_title {
        text-style: bold;
        color: #f39c12;
        margin-bottom: 1;
    }
    
    .login_container {
        align: center middle;
        width: 100%;
        height: 100%;
        background: #16213e;
        border: solid #e94560;
        padding: 4;
    }
    
    .login_form {
        padding: 2;
        height: auto;
        width: 100%;
    }
    
    .main_layout {
        height: 100%;
        width: 100%;
    }
    
    .sidebar {
        width: 20%;
        background: #16213e;
        padding: 1;
        border-right: solid #e94560;
        align: center top;
        text-align: center;
        height: 100%;
    }
    
    .sidebar_button {
        width: 90%;
        margin: 1;
        height: 3;
        text-align: center;
        content-align: center middle;
    }
    
    .sidebar_button:hover {
        background: #e94560;
        color: #ffffff;
    }
    
    .menu_title {
        text-style: bold;
        color: #e94560;
        margin-bottom: 1;
        text-align: center;
    }
    
    .content {
        width: 80%;
        padding: 1;
        height: 100%;
        overflow-y: auto;
    }
    
    .refresh_button {
        margin: 1 0;
        width: 35;
    }
    
    .dashboard_section {
        background: #16213e;
        border: solid #e94560;
        margin: 1;
        padding: 2;
    }
    
    .stat_item {
        color: white;
        margin: 0 0 0 1;
    }
    
    .user_card {
        background: #16213e;
        border: solid #3498db;
        margin: 1;
        padding: 2;
        height: auto;
        min-height: 12;
    }
    
    .user_title {
        text-style: bold;
        color: #3498db;
        margin-bottom: 1;
    }
    
    .user_info {
        color: white;
        margin: 0 0 0 1;
    }
    
    .shows_main_container {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }
    
    .shows_row {
        width: 100%;
        height: auto;
        margin: 1 0;
    }
    
    .admin_show_card {
        background: #16213e;
        border: solid #f39c12;
        margin: 0 1;
        padding: 1;
        height: auto;
        width: 1fr;
    }
    
    .show_title {
        text-style: bold;
        color: #f39c12;
        margin-bottom: 1;
    }
    
    .show_info {
        color: white;
        margin: 0 0 0 1;
    }
    
    .finance_card {
        background: #16213e;
        border: solid #27ae60;
        margin: 1;
        padding: 2;
    }
    
    .finance_title {
        text-style: bold;
        color: #27ae60;
        margin-bottom: 1;
    }
    
    .finance_info {
        color: white;
        margin: 0 0 0 1;
    }
    
    .buys_main_container {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }
    
    .buy_row {
        width: 100%;
        height: auto;
        margin: 1 0;
    }
    
    .buy_card_two_column {
        background: #16213e;
        border: solid #9b59b6;
        margin: 0 1;
        padding: 2;
        height: 12;
        min-height: 12;
        width: 1fr;
    }
    
    .buy_title {
        text-style: bold;
        color: #9b59b6;
        margin-bottom: 1;
    }
    
    .buy_info {
        color: white;
        margin: 0 0 0 1;
    }
    
    .statistics_section {
        background: #16213e;
        border: solid #e74c3c;
        margin: 1;
        padding: 2;
    }
    
    .manage_button {
        background: #3498db;
        margin-top: 1;
        width: 25;
        height: 3;
    }
    
    .manage_button:hover {
        background: #5DADE2;
    }
    
    .edit_button {
        background: #f39c12;
        margin-top: 1;
        width: 100%;
        height: 3;
    }
    
    .edit_button:hover {
        background: #F7DC6F;
    }
    
    .action_button {
        margin: 1;
        height: 3;
    }
    
    .cost_container {
        margin: 1 0;
    }
    
    .hidden {
        display: none;
    }
    
    .loading_container {
        background: #16213e;
        border: solid #e94560;
        width: 50vw;
        height: auto;
        align: center middle;
        padding: 2;
    }
    
    .loading_text {
        color: #e94560;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    
    .modal_container_fullscreen {
        background: #16213e;
        border: solid #e94560;
        width: 100vw;
        height: 100vh;
        align: center middle;
        padding: 2;
    }
    
    .modal_title {
        text-style: bold;
        color: #e94560;
        text-align: center;
        margin-bottom: 1;
    }
    
    .modal_text {
        color: white;
        text-align: center;
        margin: 1;
    }
    
    .modal_warning {
        color: #e74c3c;
        text-align: center;
        margin: 1;
        text-style: bold;
    }
    
    .modal_buttons {
        margin-top: 2;
        height: auto;
        align: center middle;
    }
    
    .add_show_layout {
        width: 100%;
        height: auto;
        margin: 1;
    }
    
    .add_show_left_column {
        width: 50%;
        padding: 1;
        height: auto;
    }
    
    .add_show_right_column {
        width: 50%;
        padding: 1;
        height: auto;
    }
    
    .user_management_layout {
        width: 100%;
        height: auto;
        margin: 1;
    }
    
    .user_info_column {
        width: 50%;
        padding: 1;
        height: auto;
    }
    
    .user_management_column {
        width: 50%;
        padding: 1;
        height: auto;
    }
    
    .user_info_text {
        color: white;
        margin: 1 0 0 1;
    }
    
    .edit_show_form {
        padding: 2;
        height: auto;
        width: 100%;
    }
    
    .empty_message {
        color: #95a5a6;
        text-align: center;
        margin: 2;
    }
    
    .error_message {
        color: #e74c3c;
        text-align: center;
        margin: 2;
    }
    
    Input {
        margin: 1;
        background: #1a1a2e;
        border: solid #95a5a6;
        width: 100%;
    }
    
    Input:focus {
        border: solid #e94560;
    }
    
    Label {
        margin: 1 0 0 1;
        color: white;
    }
    
    Select {
        margin: 1;
        background: #1a1a2e;
        border: solid #95a5a6;
        width: 100%;
    }
    
    Checkbox {
        margin: 1;
        color: white;
    }
    
    Button {
        margin: 1;
        height: 3;
    }
    
    Button:hover {
        text-style: bold;
    }
    
    Button.-primary {
        background: #e94560;
        color: white;
    }
    
    Button.-primary:hover {
        background: #c0392b;
    }
    
    Button.-success {
        background: #27ae60;
        color: white;
    }
    
    Button.-success:hover {
        background: #2ecc71;
    }
    
    Button.-warning {
        background: #f39c12;
        color: black;
    }
    
    Button.-warning:hover {
        background: #e67e22;
    }
    
    Button.-error {
        background: #e74c3c;
        color: white;
    }
    
    Button.-error:hover {
        background: #c0392b;
    }
    
    Button.-default {
        background: #95a5a6;
        color: white;
    }
    
    Button.-default:hover {
        background: #7f8c8d;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_admin: Optional[Dict] = None
        self.encryption = EncryptionManager()
    
    def on_mount(self) -> None:
        self.title = "EasyFlix Admin"
        self.push_screen(LoginScreen())
    
    def call_api(self, command: str, **kwargs) -> Optional[Dict]:
        """Call the EFAPI with encrypted communication"""
        try:
            if not os.path.exists("EFAPI.py"):
                self.notify("EFAPI.py not found in current directory", severity="error")
                return None
            
            # Prepare encrypted request
            request_data = {
                "command": command,
                "parameters": kwargs
            }
            
            encrypted_request = self.encryption.encrypt_data(json.dumps(request_data))
            
            cmd = [sys.executable, "EFAPI.py", "--encrypted_data", encrypted_request]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    
                    # Check if response is encrypted
                    if response.get("encrypted"):
                        decrypted_data = self.encryption.decrypt_data(response["data"])
                        return json.loads(decrypted_data)
                    else:
                        return response
                        
                except json.JSONDecodeError:
                    self.notify("Invalid JSON response from API", severity="error")
                    return None
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown API error"
                self.notify(f"API Error: {error_msg}", severity="error")
                return None
                
        except subprocess.TimeoutExpired:
            self.notify("API call timed out", severity="error")
            return None
        except Exception as e:
            self.notify(f"Error calling API: {e}", severity="error")
            return None

if __name__ == "__main__":
    app = EasyFlixAdminApp()
    app.run()
