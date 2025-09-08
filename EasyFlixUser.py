#!/usr/bin/env python3
"""
EasyFlixUser - User interface for EasyFlix streaming service
"""

import subprocess
import json
import sys
import os
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, Center, Middle
from textual.widgets import Button, Input, Label, Select, Static, Header, Footer, LoadingIndicator, Checkbox
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.reactive import reactive
from textual import work
from typing import Dict, List, Optional, Any

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

class RentConfirmModal(ModalScreen):
    """Modal for confirming premium show purchase"""
    
    def __init__(self, show_name: str, cost: float, show_id: int):
        super().__init__()
        self.show_name = show_name
        self.cost = cost
        self.show_id = show_id
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Buy Premium Show", classes="modal_title"),
            Static(f"Show: {self.show_name}", classes="modal_text"),
            Static(f"Cost: ${self.cost:.2f}", classes="modal_text"),
            Static("Would you like to buy this premium show?", classes="modal_text"),
            Horizontal(
                Button("Buy Show", id="confirm_rent", variant="primary"),
                Button("Cancel", id="cancel_rent", variant="default"),
                classes="modal_buttons"
            ),
            classes="modal_container_fullscreen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_rent":
            self.dismiss({"action": "rent", "show_id": self.show_id})
        else:
            self.dismiss(None)

class RemoveConfirmModal(ModalScreen):
    """Modal for confirming show removal"""
    
    def __init__(self, show_name: str, show_id: int):
        super().__init__()
        self.show_name = show_name
        self.show_id = show_id
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Remove Show", classes="modal_title"),
            Static(f"Show: {self.show_name}", classes="modal_text"),
            Static("Are you sure you want to remove this show from your collection?", classes="modal_text"),
            Horizontal(
                Button("Remove", id="confirm_remove", variant="error"),
                Button("Cancel", id="cancel_remove", variant="default"),
                classes="modal_buttons"
            ),
            classes="modal_container_fullscreen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_remove":
            self.dismiss({"action": "remove", "show_id": self.show_id})
        else:
            self.dismiss(None)

class LoginScreen(Screen):
    """Login screen for user authentication"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Welcome to EasyFlix", classes="title"),
            Container(
                Button("Login", id="login_btn", variant="primary"),
                Button("Create Account", id="create_btn", variant="success"),
                classes="button_container"
            ),
            classes="login_container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_btn":
            self.app.push_screen(LoginFormScreen())
        elif event.button.id == "create_btn":
            self.app.push_screen(CreateAccountScreen())

class LoginFormScreen(Screen):
    """Login form screen"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Login to EasyFlix", classes="title"),
            Container(
                Label("Username:"),
                Input(placeholder="Enter username", id="username"),
                Label("Password:"),
                Input(placeholder="Enter password", password=True, id="password"),
                Horizontal(
                    Button("Login", id="submit", variant="primary"),
                    Button("Back", id="back", variant="default"),
                    classes="button_row"
                ),
                classes="form_container"
            ),
            classes="main_container_fullscreen"
        )
        yield Footer()

    @work(exclusive=True)
    async def authenticate_user(self, username: str, password: str):
        """Authenticate user asynchronously"""
        result = await asyncio.to_thread(
            self.app.call_api, "authenticate_user", 
            username=username, password=password
        )
        
        if result is not None and result.get("success"):
            user_data = result.get("data", {})
            self.app.current_user = user_data
            self.app.pop_screen()
            self.app.push_screen(MainScreen())
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Login failed: " + error_msg, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            username = self.query_one("#username", Input).value
            password = self.query_one("#password", Input).value
            
            if username and password:
                self.authenticate_user(username, password)
            else:
                self.notify("Please enter both username and password", severity="warning")
        elif event.button.id == "back":
            self.app.pop_screen()

class CreateAccountScreen(Screen):
    """Account creation screen"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create EasyFlix Account", classes="title"),
            Container(
                Label("Username:"),
                Input(placeholder="Enter username", id="username"),
                Label("Email:"),
                Input(placeholder="Enter email", id="email"),
                Label("Password:"),
                Input(placeholder="Enter password", password=True, id="password"),
                Label("Subscription Level:"),
                Select([("Basic - $30", "Basic"), ("Premium - $80", "Premium")], id="subscription"),
                Checkbox("I agree to receive marketing communications", id="marketing_checkbox"),
                Horizontal(
                    Button("Create Account", id="submit", variant="primary"),
                    Button("Back", id="back", variant="default"),
                    classes="button_row"
                ),
                classes="form_container"
            ),
            classes="main_container_fullscreen"
        )
        yield Footer()

    @work(exclusive=True)
    async def create_user_account(self, username: str, email: str, password: str, subscription: str, marketing_opt_in: bool):
        """Create user account asynchronously"""
        result = await asyncio.to_thread(
            self.app.call_api, "create_user",
            username=username, email=email, password=password, 
            subscription_level=subscription, marketing_opt_in=marketing_opt_in
        )
        
        if result is not None and result.get("success"):
            charged = result.get("data", {}).get("charged", 0) if result.get("data") else 0
            self.notify(f"Account created successfully! Charged: ${charged:.2f}. Please log in.", severity="information")
            self.app.pop_screen()
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Account creation failed: " + error_msg, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            username = self.query_one("#username", Input).value
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            subscription = self.query_one("#subscription", Select).value
            marketing_opt_in = self.query_one("#marketing_checkbox", Checkbox).value
            
            if all([username, email, password, subscription]):
                self.create_user_account(username, email, password, subscription, marketing_opt_in)
            else:
                self.notify("Please fill in all fields", severity="warning")
        elif event.button.id == "back":
            self.app.pop_screen()

class MainScreen(Screen):
    """Main application screen"""
    
    current_view = reactive("shows")
    current_search_filters = {}
    shows_cache = []
    genres_cache = []
    ratings_cache = []
    interface_built = False
    search_timer = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Container(
                Static("Menu", classes="menu_title"),
                Button("Browse Shows", id="shows_btn", variant="primary", classes="sidebar_button"),
                Button("My Shows", id="my_shows_btn", variant="default", classes="sidebar_button"),
                Button("Account", id="account_btn", variant="default", classes="sidebar_button"),
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
        self.genres_cache = [
            "Action", "Adventure", "Animation", "Comedy", "Crime", "Drama", 
            "Fantasy", "History", "Romance", "Sci-Fi", "Thriller"
        ]
        self.ratings_cache = [
            "G", "PG", "PG-13", "R", "TV-14", "TV-MA", "TV-PG"
        ]
        
        self.load_genres_and_ratings()
        self.load_shows()

    @work(exclusive=True)
    async def load_genres_and_ratings(self):
        """Load genres and ratings for filters"""
        try:
            genres_result = await asyncio.to_thread(self.app.call_api, "get_available_genres")
            if genres_result is not None and genres_result.get("success"):
                self.genres_cache = genres_result.get("data", self.genres_cache)
            
            ratings_result = await asyncio.to_thread(self.app.call_api, "get_available_ratings")
            if ratings_result is not None and ratings_result.get("success"):
                self.ratings_cache = ratings_result.get("data", self.ratings_cache)
        except Exception as e:
            self.notify(f"Error loading filters: {e}", severity="warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "shows_btn":
            self.current_view = "shows"
            self.update_sidebar_buttons("shows_btn")
            self.load_shows()
        elif event.button.id == "my_shows_btn":
            self.current_view = "my_shows"
            self.update_sidebar_buttons("my_shows_btn")
            self.load_my_shows()
        elif event.button.id == "account_btn":
            self.current_view = "account"
            self.update_sidebar_buttons("account_btn")
            self.load_account()
        elif event.button.id == "logout_btn":
            self.app.current_user = None
            self.app.pop_screen()
        elif event.button.id and event.button.id.startswith("add_show_"):
            show_id = int(event.button.id.replace("add_show_", ""))
            self.handle_show_action(show_id)
        elif event.button.id and event.button.id.startswith("remove_show_"):
            show_id = int(event.button.id.replace("remove_show_", ""))
            self.handle_remove_show(show_id)
        elif event.button.id == "change_password":
            self.app.push_screen(ChangePasswordScreen())
        elif event.button.id == "change_subscription":
            self.app.push_screen(ChangeSubscriptionScreen())
        elif event.button.id == "update_marketing":
            self.app.push_screen(MarketingPreferenceScreen())

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search_text":
            # Cancel previous timer if it exists
            if self.search_timer:
                try:
                    self.search_timer.stop()
                except:
                    pass
            # Set new timer for 0.5 seconds
            self.search_timer = self.set_timer(0.5, self.apply_filters)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id in ["genre_filter", "rating_filter"]:
            self.apply_filters()

    def apply_filters(self):
        """Apply current filters and search"""
        if not self.interface_built or self.current_view != "shows":
            return
            
        try:
            content = self.query_one("#content_area")
            
            self.current_search_filters = {}
            
            # Get search text
            search_input = content.query_one("#search_text", Input)
            search_text = search_input.value.strip()
            if search_text:
                self.current_search_filters["name"] = search_text
            
            # Get genre filter - only add if it's a real value
            genre_select = content.query_one("#genre_filter", Select)
            genre_value = genre_select.value
            if genre_value and genre_value != "All" and genre_value != Select.BLANK:
                self.current_search_filters["genre"] = genre_value
            
            # Get rating filter - only add if it's a real value
            rating_select = content.query_one("#rating_filter", Select)
            rating_value = rating_select.value
            if rating_value and rating_value != "All" and rating_value != Select.BLANK:
                self.current_search_filters["rating"] = rating_value
            
            self.refresh_shows_data()
        except Exception:
            pass

    def update_sidebar_buttons(self, active_button_id: str):
        """Update sidebar button styles"""
        button_ids = ["shows_btn", "my_shows_btn", "account_btn"]
        for btn_id in button_ids:
            button = self.query_one(f"#{btn_id}", Button)
            if btn_id == active_button_id:
                button.variant = "primary"
            else:
                button.variant = "default"

    def handle_show_action(self, show_id: int) -> None:
        """Handle show action (add or purchase)"""
        show = next((s for s in self.shows_cache if s["show_id"] == show_id), None)
        
        if show:
            is_premium = show.get("access_group") == "Premium"
            user_subscription = self.app.current_user.get("subscription_level", "Basic")
            
            if is_premium and user_subscription == "Basic":
                def handle_modal_result(result):
                    if result and result.get("action") == "rent":
                        self.add_show_to_user(show_id)
                
                self.app.push_screen(
                    RentConfirmModal(show["name"], show.get("cost_to_buy", 0), show_id),
                    handle_modal_result
                )
            else:
                self.add_show_to_user(show_id)

    def handle_remove_show(self, show_id: int) -> None:
        """Handle show removal"""
        self.check_user_shows_for_removal(show_id)

    @work(exclusive=True)
    async def check_user_shows_for_removal(self, show_id: int):
        """Check user shows for removal"""
        user_shows_result = await asyncio.to_thread(self.app.call_api, "get_user_shows", user_id=self.app.current_user.get("user_id"))
        if user_shows_result is not None and user_shows_result.get("success"):
            shows = user_shows_result.get("data", [])
            show = next((s for s in shows if s["show_id"] == show_id), None)
            
            if show:
                def handle_modal_result(result):
                    if result and result.get("action") == "remove":
                        self.remove_show_from_user(show_id)
                
                self.app.push_screen(
                    RemoveConfirmModal(show["show_name"], show_id),
                    handle_modal_result
                )

    @work(exclusive=True)
    async def add_show_to_user(self, show_id: int):
        """Add show to user's collection asynchronously"""
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(
            self.app.call_api, "add_show_to_user", 
            user_id=user_id, show_id=show_id
        )
        
        if result is not None and result.get("success"):
            self.notify("Show added successfully!", severity="information")
            user_info_result = await asyncio.to_thread(
                self.app.call_api, "get_user_info", user_id=user_id
            )
            if user_info_result is not None and user_info_result.get("success"):
                self.app.current_user.update(user_info_result.get("data", {}))
            
            if self.current_view == "shows":
                self.refresh_shows_data()
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Failed to add show: " + error_msg, severity="error")

    @work(exclusive=True)
    async def remove_show_from_user(self, show_id: int):
        """Remove show from user's collection asynchronously"""
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(
            self.app.call_api, "remove_show_from_user", 
            user_id=user_id, show_id=show_id
        )
        
        if result is not None and result.get("success"):
            self.notify("Show removed successfully!", severity="information")
            user_info_result = await asyncio.to_thread(
                self.app.call_api, "get_user_info", user_id=user_id
            )
            if user_info_result is not None and user_info_result.get("success"):
                self.app.current_user.update(user_info_result.get("data", {}))
            
            if self.current_view == "my_shows":
                self.load_my_shows()
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Failed to remove show: " + error_msg, severity="error")

    def clear_content_area(self):
        """Safely clear content area"""
        content = self.query_one("#content_area")
        try:
            content.remove_children()
        except Exception:
            pass
        self.interface_built = False

    def build_shows_interface(self):
        """Build the shows interface once"""
        if self.interface_built:
            return
            
        content = self.query_one("#content_area")
        genre_options = [("All", "All")] + [(g, g) for g in self.genres_cache]
        rating_options = [("All", "All")] + [(r, r) for r in self.ratings_cache]
        
        interface_widgets = [
            Static("Available Shows", classes="content_title"),
            Input(placeholder="Search shows...", id="search_text", classes="search_input"),
            Horizontal(
                Select(genre_options, prompt="Genre", id="genre_filter", classes="filter_select"),
                Select(rating_options, prompt="Rating", id="rating_filter", classes="filter_select"),
                classes="filters_row"
            ),
            Container(id="shows_content_area", classes="shows_content")
        ]
        
        for widget in interface_widgets:
            content.mount(widget)
        
        self.interface_built = True

    @work(exclusive=True)
    async def refresh_shows_data(self):
        """Refresh only the shows data without rebuilding interface"""
        if not self.interface_built:
            return
            
        content = self.query_one("#content_area")
        shows_content = content.query_one("#shows_content_area")
        
        # Clear existing children and ensure no duplicate IDs
        shows_content.remove_children()
        
        # Add loading indicator with unique ID using timestamp
        import time
        unique_id = f"shows_loading_{int(time.time() * 1000)}"
        shows_content.mount(LoadingIndicator(id=unique_id))
        
        try:
            if self.current_search_filters:
                result = await asyncio.to_thread(self.app.call_api, "search_shows", **self.current_search_filters)
            else:
                result = await asyncio.to_thread(self.app.call_api, "get_all_shows")
            
            # Remove loading indicator
            try:
                shows_content.query_one(f"#{unique_id}").remove()
            except:
                pass
            
            if result is not None and result.get("success"):
                shows = result.get("data", [])
                self.shows_cache = shows
                user_shows = self.app.current_user.get("shows", "").split(",") if self.app.current_user.get("shows") else []
                user_show_ids = [int(x.strip()) for x in user_shows if x.strip()]
                
                if shows:
                    show_rows = []
                    for i in range(0, len(shows), 3):
                        row_shows = shows[i:i+3]
                        row_cards = []
                        for j, show in enumerate(row_shows):
                            row_cards.append(self.create_show_card(show, show["show_id"] in user_show_ids))
                        
                        show_rows.append(Horizontal(*row_cards, classes="shows_row"))
                    
                    shows_container = Vertical(*show_rows, classes="shows_main_container")
                    shows_content.mount(shows_container)
                else:
                    shows_content.mount(Static("No shows found", classes="empty_message"))
            else:
                error_msg = result.get("message", "Failed to load shows") if result else "API connection failed"
                shows_content.mount(Static(f"Error loading shows: {error_msg}", classes="error_message"))
                
        except Exception as e:
            try:
                shows_content.query_one(f"#{unique_id}").remove()
            except:
                pass
            shows_content.mount(Static(f"Error loading shows: {e}", classes="error_message"))

    def load_shows(self) -> None:
        """Load and display all shows"""
        self.clear_content_area()
        self.build_shows_interface()
        self.refresh_shows_data()

    @work(exclusive=True)
    async def load_my_shows_async(self):
        """Load user's shows asynchronously"""
        self.clear_content_area()
        content = self.query_one("#content_area")
        
        content.mount(Static("My Shows", classes="content_title"))
        content.mount(LoadingIndicator())
        
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(self.app.call_api, "get_user_shows", user_id=user_id)
        
        content.remove_children()
        content.mount(Static("My Shows", classes="content_title"))
        
        if result is not None and result.get("success"):
            shows = result.get("data", [])
            if shows:
                show_rows = []
                for i in range(0, len(shows), 3):
                    row_shows = shows[i:i+3]
                    row_cards = []
                    for j, show in enumerate(row_shows):
                        row_cards.append(self.create_my_show_card(show))
                    
                    show_rows.append(Horizontal(*row_cards, classes="shows_row"))
                
                shows_container = Vertical(*show_rows, classes="shows_main_container")
                content.mount(shows_container)
            else:
                content.mount(Static("No shows found", classes="empty_message"))
        else:
            error_msg = result.get("message", "Failed to load shows") if result else "API connection failed"
            content.mount(Static(f"Error loading shows: {error_msg}", classes="error_message"))

    def load_my_shows(self) -> None:
        """Load and display user's shows"""
        self.load_my_shows_async()

    def load_account(self) -> None:
        """Load and display account information"""
        self.clear_content_area()
        content = self.query_one("#content_area")
        
        user = self.app.current_user
        
        content.mount(Static("Account Information", classes="content_title"))
        content.mount(Container(
            Static(f"Username: {user.get('username', 'N/A')}", classes="info_item"),
            Static(f"Email: {user.get('email', 'N/A')}", classes="info_item"),
            Static(f"Subscription: {user.get('subscription_level', 'N/A')}", classes="info_item"),
            Static(f"Total Spent: ${user.get('total_spent', 0):.2f}", classes="info_item"),
            Static(f"Favourite Genre: {user.get('favourite_genre', 'Not set')}", classes="info_item"),
            Static(f"Marketing Opt-in: {'Yes' if user.get('marketing_opt_in', False) else 'No'}", classes="info_item"),
            Button("Change Password", id="change_password", variant="default"),
            Button("Change Subscription", id="change_subscription", variant="primary"),
            Button("Update Marketing Preference", id="update_marketing", variant="default"),
            classes="account_info"
        ))

    def create_show_card(self, show: Dict, already_owned: bool = False) -> Container:
        """Create a show card widget"""
        is_premium = show.get("access_group") == "Premium"
        user_subscription = self.app.current_user.get("subscription_level", "Basic")
        
        if already_owned:
            button_text = "Already Added"
            button_variant = "default"
            button_classes = "disabled_button"
            button_disabled = True
        elif is_premium and user_subscription == "Basic":
            button_text = f"Buy (${show.get('cost_to_buy', 0):.2f})"
            button_variant = "warning"
            button_classes = "premium_button"
            button_disabled = False
        else:
            button_text = "Add to My Shows"
            button_variant = "primary" if not is_premium else "success"
            button_classes = "basic_button" if not is_premium else "premium_included"
            button_disabled = False
        
        button = Button(
            button_text,
            id=f"add_show_{show.get('show_id')}",
            variant=button_variant,
            classes=button_classes,
            disabled=button_disabled
        )
        
        card_classes = f"show_card {'premium_card' if is_premium else 'basic_card'}"
        
        return Container(
            Static(show.get("name", "Unknown"), classes="show_title"),
            Static(f"Genre: {show.get('genre', 'N/A')}", classes="show_info"),
            Static(f"Rating: {show.get('rating', 'N/A')}", classes="show_info"),
            Static(f"Director: {show.get('director', 'N/A')}", classes="show_info"),
            Static(f"Length: {show.get('length', 'N/A')} min", classes="show_info"),
            Static(f"Release: {show.get('release_date', 'N/A')}", classes="show_info"),
            button,
            classes=card_classes
        )

    def create_my_show_card(self, show: Dict) -> Container:
        """Create a show card for user's collection"""
        return Container(
            Static(show.get("show_name", "Unknown"), classes="show_title"),
            Static(f"Genre: {show.get('genre', 'N/A')}", classes="show_info"),
            Static(f"Rating: {show.get('rating', 'N/A')}", classes="show_info"),
            Static(f"Director: {show.get('director', 'N/A')}", classes="show_info"),
            Static(f"Length: {show.get('length', 'N/A')} min", classes="show_info"),
            Static(f"Release: {show.get('release_date', 'N/A')}", classes="show_info"),
            Static("✓ In Your Collection", classes="owned_status"),
            Button("Remove", id=f"remove_show_{show.get('show_id')}", variant="error", classes="remove_button"),
            classes="show_card owned_card"
        )

class ChangePasswordScreen(Screen):
    """Change password screen"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Change Password", classes="title"),
            Container(
                Label("New Password:"),
                Input(placeholder="Enter new password", password=True, id="new_password"),
                Label("Confirm Password:"),
                Input(placeholder="Confirm new password", password=True, id="confirm_password"),
                Horizontal(
                    Button("Change Password", id="submit", variant="primary"),
                    Button("Cancel", id="cancel", variant="default"),
                    classes="button_row"
                ),
                classes="form_container"
            ),
            classes="main_container_fullscreen"
        )
        yield Footer()

    @work(exclusive=True)
    async def change_password_async(self, new_password: str):
        """Change password asynchronously"""
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(
            self.app.call_api, "change_password", 
            user_id=user_id, new_password=new_password
        )
        
        if result is not None and result.get("success"):
            self.notify("Password changed successfully!", severity="information")
            self.app.pop_screen()
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Failed to change password: " + error_msg, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            new_password = self.query_one("#new_password", Input).value
            confirm_password = self.query_one("#confirm_password", Input).value
            
            if new_password and confirm_password:
                if new_password == confirm_password:
                    self.change_password_async(new_password)
                else:
                    self.notify("Passwords do not match", severity="warning")
            else:
                self.notify("Please fill in both fields", severity="warning")
        elif event.button.id == "cancel":
            self.app.pop_screen()

class MarketingPreferenceScreen(Screen):
    """Marketing preference screen"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Marketing Preferences", classes="title"),
            Container(
                Label("Current Setting:"),
                Static(f"{'Opted In' if self.app.current_user.get('marketing_opt_in', False) else 'Opted Out'}", classes="current_sub"),
                Checkbox("I agree to receive marketing communications", 
                        id="marketing_checkbox", 
                        value=self.app.current_user.get('marketing_opt_in', False)),
                Horizontal(
                    Button("Update Preference", id="submit", variant="primary"),
                    Button("Cancel", id="cancel", variant="default"),
                    classes="button_row"
                ),
                classes="form_container"
            ),
            classes="main_container_fullscreen"
        )
        yield Footer()

    @work(exclusive=True)
    async def update_marketing_preference_async(self, marketing_opt_in: bool):
        """Update marketing preference asynchronously"""
        user_id = self.app.current_user.get("user_id")
        
        result = await asyncio.to_thread(
            self.app.call_api, "update_marketing_opt_in", 
            user_id=user_id, marketing_opt_in=marketing_opt_in
        )
        
        if result is not None and result.get("success"):
            self.app.current_user["marketing_opt_in"] = marketing_opt_in
            self.notify("Marketing preference updated successfully!", severity="information")
            self.app.pop_screen()
            
            main_screen = self.app.screen_stack[-1]
            if hasattr(main_screen, 'load_account') and main_screen.current_view == "account":
                main_screen.load_account()
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Failed to update preference: " + error_msg, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            marketing_opt_in = self.query_one("#marketing_checkbox", Checkbox).value
            self.update_marketing_preference_async(marketing_opt_in)
        elif event.button.id == "cancel":
            self.app.pop_screen()

class ChangeSubscriptionScreen(Screen):
    """Change subscription screen"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Change Subscription", classes="title"),
            Container(
                Label("Current Subscription:"),
                Static(f"{self.app.current_user.get('subscription_level', 'Unknown')}", classes="current_sub"),
                Label("New Subscription Level:"),
                Select([("Basic - $30", "Basic"), ("Premium - $80", "Premium")], id="subscription"),
                Static("Note: Premium to Basic is free, Basic to Premium costs $80", classes="pricing_note"),
                Horizontal(
                    Button("Update Subscription", id="submit", variant="primary"),
                    Button("Cancel", id="cancel", variant="default"),
                    classes="button_row"
                ),
                classes="form_container"
            ),
            classes="main_container_fullscreen"
        )
        yield Footer()

    @work(exclusive=True)
    async def update_subscription_async(self, subscription: str):
        """Update subscription asynchronously"""
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(
            self.app.call_api, "update_subscription", 
            user_id=user_id, subscription_level=subscription
        )
        
        if result is not None and result.get("success"):
            user_info_result = await asyncio.to_thread(
                self.app.call_api, "get_user_info", user_id=user_id
            )
            if user_info_result is not None and user_info_result.get("success"):
                self.app.current_user.update(user_info_result.get("data", {}))
            
            charged = result.get("data", {}).get("charged", 0) if result.get("data") else 0
            if charged > 0:
                self.notify(f"Subscription updated successfully! Charged: ${charged:.2f}", severity="information")
            else:
                self.notify("Subscription updated successfully!", severity="information")
            self.app.pop_screen()
            
            main_screen = self.app.screen_stack[-1]
            if hasattr(main_screen, 'load_account') and main_screen.current_view == "account":
                main_screen.load_account()
        else:
            error_msg = result.get("message", "Unknown error") if result else "API connection failed"
            self.notify("Failed to update subscription: " + error_msg, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            subscription = self.query_one("#subscription", Select).value
            
            if subscription:
                self.update_subscription_async(subscription)
            else:
                self.notify("Please select a subscription level", severity="warning")
        elif event.button.id == "cancel":
            self.app.pop_screen()

class EasyFlixUserApp(App):
    """Main EasyFlix User Application"""
    
    CSS = """
    Screen {
        background: #2F2F2F;
        color: white;
        width: 100%;
        height: 100%;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: #FF8C00;
        margin: 2;
        content-align: center middle;
    }
    
    .content_title {
        text-style: bold;
        color: #FF8C00;
        margin: 1;
        padding: 1;
    }
    
    .login_container {
        align: center middle;
        width: 100%;
        height: 100%;
        background: #404040;
        border: solid #FF8C00;
        padding: 4;
    }
    
    .button_container {
        align: center middle;
        height: auto;
        margin: 2;
    }
    
    .main_container_fullscreen {
        align: center middle;
        width: 100vw;
        height: 100vh;
        background: #404040;
        border: solid #FF8C00;
    }
    
    .form_container {
        padding: 2;
        height: auto;
        width: 100%;
    }
    
    .button_row {
        margin-top: 2;
        height: auto;
        align: center middle;
    }
    
    .pricing_note {
        color: #FFD700;
        margin: 1;
        text-style: italic;
    }
    
    Input {
        margin: 1;
        background: #2F2F2F;
        border: solid #696969;
        width: 100%;
        transition: border 0.3s in_out_cubic;
    }
    
    Input:focus {
        border: solid #FF8C00;
    }
    
    .search_input {
        width: 100%;
        margin: 1 0;
        height: 3;
    }
    
    Label {
        margin: 1 0 0 1;
        color: white;
    }
    
    Select {
        margin: 0 1;
        background: #2F2F2F;
        border: solid #696969;
        width: 1fr;
        transition: border 0.3s in_out_cubic;
    }
    
    Select:focus {
        border: solid #FF8C00;
    }
    
    .filter_select {
        margin: 0 1;
        width: 1fr;
        min-width: 15;
    }
    
    Checkbox {
        margin: 1;
        color: white;
    }
    
    .current_sub {
        margin: 1;
        color: #FF8C00;
        text-style: bold;
    }
    
    .main_layout {
        height: 100%;
        width: 100%;
    }
    
    .sidebar {
        width: 20%;
        background: #404040;
        padding: 1;
        border-right: solid #FF8C00;
        align: center top;
        text-align: center;
        height: 100%;
    }
    
    .sidebar_button {
        width: 100%;
        margin: 1;
        height: 3;
        text-align: center;
        content-align: center middle;
    }
    
    .menu_title {
        text-style: bold;
        color: #FF8C00;
        margin-bottom: 1;
        text-align: center;
    }
    
    .content {
        width: 80%;
        padding: 1;
        height: 100%;
    }
    
    .filters_row {
        width: 100%;
        height: auto;
        margin: 1 0;
    }
    
    .shows_content {
        width: 100%;
        height: 1fr;
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
    
    .show_card {
        background: #404040;
        border: solid #696969;
        margin: 0 1;
        padding: 1;
        height: auto;
        width: 1fr;
    }
    
    .basic_card {
        border-left: solid #FF8C00;
    }
    
    .premium_card {
        border-left: solid #FFD700;
    }
    
    .owned_card {
        border-left: solid #32CD32;
        background: #2F4F2F;
    }
    
    .show_title {
        text-style: bold;
        color: #FF8C00;
        margin-bottom: 1;
    }
    
    .show_info {
        color: white;
        margin: 0 0 0 1;
    }
    
    .owned_status {
        color: #32CD32;
        text-style: bold;
        margin-top: 1;
        text-align: center;
    }
    
    .basic_button {
        background: #FF8C00;
        margin-top: 1;
        height: 3;
    }
    
    .basic_button:hover {
        background: #FFB84D;
    }
    
    .premium_button {
        background: #FFD700;
        color: black;
        margin-top: 1;
        height: 3;
    }
    
    .premium_button:hover {
        background: #FFF700;
    }
    
    .premium_included {
        background: #32CD32;
        margin-top: 1;
        height: 3;
    }
    
    .premium_included:hover {
        background: #90EE90;
    }
    
    .disabled_button {
        background: #696969;
        color: #A0A0A0;
        margin-top: 1;
        height: 3;
    }
    
    .remove_button {
        background: #DC143C;
        margin-top: 1;
        width: 100%;
        height: 3;
    }
    
    .remove_button:hover {
        background: #FF6B6B;
    }
    
    .account_info {
        padding: 2;
        background: #404040;
        border: solid #FF8C00;
        margin: 2;
        width: 100%;
    }
    
    .info_item {
        margin: 1;
        color: white;
    }
    
    .empty_message {
        color: #696969;
        text-align: center;
        margin: 2;
    }
    
    .error_message {
        color: #DC143C;
        text-align: center;
        margin: 2;
    }
    
    .loading_container {
        background: #404040;
        border: solid #FF8C00;
        width: 50vw;
        height: auto;
        align: center middle;
        padding: 2;
    }
    
    .loading_text {
        color: #FF8C00;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    
    .modal_container_fullscreen {
        background: #404040;
        border: solid #FF8C00;
        width: 100vw;
        height: 100vh;
        align: center middle;
        padding: 2;
    }
    
    .modal_title {
        text-style: bold;
        color: #FF8C00;
        text-align: center;
        margin-bottom: 1;
    }
    
    .modal_text {
        color: white;
        text-align: center;
        margin: 1;
    }
    
    .modal_buttons {
        margin-top: 2;
        height: auto;
        align: center middle;
    }
    
    Button {
        margin: 1;
        height: 3;
    }
    
    Button:hover {
        text-style: bold;
    }
    
    Button.-primary {
        background: #FF8C00;
        color: white;
    }
    
    Button.-primary:hover {
        background: #FFB84D;
    }
    
    Button.-success {
        background: #32CD32;
        color: white;
    }
    
    Button.-success:hover {
        background: #90EE90;
    }
    
    Button.-warning {
        background: #FFD700;
        color: black;
    }
    
    Button.-warning:hover {
        background: #FFF700;
    }
    
    Button.-error {
        background: #DC143C;
        color: white;
    }
    
    Button.-error:hover {
        background: #FF6B6B;
    }
    
    Button.-default {
        background: #696969;
        color: white;
    }
    
    Button.-default:hover {
        background: #A9A9A9;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_user: Optional[Dict] = None
    
    def on_mount(self) -> None:
        self.title = "EasyFlix User"
        self.push_screen(LoginScreen())
    
    def call_api(self, command: str, **kwargs) -> Optional[Dict]:
        """Call the EFAPI with the given command and arguments"""
        try:
            if not os.path.exists("EFAPI.py"):
                self.notify("EFAPI.py not found in current directory", severity="error")
                return None
            
            cmd = [sys.executable, "EFAPI.py", "--command", command]
            
            for key, value in kwargs.items():
                if key == 'marketing_opt_in' and isinstance(value, bool):
                    # Handle marketing_opt_in boolean specifically
                    if value:
                        cmd.append("--marketing_opt_in_true")
                    else:
                        cmd.append("--marketing_opt_in_false")
                elif isinstance(value, bool):
                    if value:
                        cmd.append(f"--{key}")
                else:
                    cmd.extend([f"--{key}", str(value)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
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
    app = EasyFlixUserApp()
    app.run()
