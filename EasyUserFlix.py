#!/usr/bin/env python3
"""
EasyFlixUser - Enhanced user interface for EasyFlix streaming service
"""

import subprocess
import json
import sys
import os
import asyncio
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Input, Label, Select, Static, Header, Footer, LoadingIndicator, Checkbox
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.reactive import reactive
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

class ConfirmDeleteModal(ModalScreen):
    """Modal for confirming account deletion"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Delete Account", classes="modal_title"),
            Static("Are you sure you want to delete your account?", classes="modal_text"),
            Static("This action cannot be undone.", classes="modal_text warning"),
            Horizontal(
                Button("Delete Account", id="confirm_delete", variant="error"),
                Button("Cancel", id="cancel_delete", variant="default"),
                classes="modal_buttons"
            ),
            classes="modal_container"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_delete":
            self.dismiss(True)
        else:
            self.dismiss(False)

class RentConfirmModal(ModalScreen):
    """Modal for confirming premium show rental"""
    
    def __init__(self, show_name: str, cost: float, show_id: int):
        super().__init__()
        self.show_name = show_name
        self.cost = cost
        self.show_id = show_id
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Rent Premium Show", classes="modal_title"),
            Static(f"Show: {self.show_name}", classes="modal_text"),
            Static(f"Cost: ${self.cost:.2f}", classes="modal_text"),
            Static("Would you like to rent this premium show?", classes="modal_text"),
            Horizontal(
                Button("Rent Show", id="confirm_rent", variant="primary"),
                Button("Cancel", id="cancel_rent", variant="default"),
                classes="modal_buttons"
            ),
            classes="modal_container"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_rent":
            self.dismiss({"action": "rent", "show_id": self.show_id})
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
            classes="main_container"
        )
        yield Footer()

    @work(exclusive=True)
    async def authenticate_user(self, username: str, password: str):
        """Authenticate user asynchronously"""
        result = await asyncio.to_thread(
            self.app.call_api, "authenticate_user", 
            username=username, password=password
        )
        
        self.app.pop_screen()  # Remove loading screen
        
        if result and result.get("success"):
            user_data = result.get("data", {})
            self.app.current_user = user_data
            self.app.pop_screen()
            self.app.push_screen(MainScreen())
        else:
            self.notify("Login failed: " + result.get("message", "Unknown error"), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            username = self.query_one("#username", Input).value
            password = self.query_one("#password", Input).value
            
            if username and password:
                loading = LoadingScreen("Authenticating...")
                self.app.push_screen(loading)
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
                Select([("Basic", "Basic"), ("Premium", "Premium")], id="subscription"),
                Checkbox("Receive marketing emails", id="marketing_opt_in"),
                Horizontal(
                    Button("Create Account", id="submit", variant="primary"),
                    Button("Back", id="back", variant="default"),
                    classes="button_row"
                ),
                classes="form_container"
            ),
            classes="main_container"
        )
        yield Footer()

    @work(exclusive=True)
    async def create_user_account(self, username: str, email: str, password: str, subscription: str, marketing_opt_in: bool):
        """Create user account asynchronously"""
        result = await asyncio.to_thread(
            self.app.call_api, "create_user",
            username=username, email=email, password=password, 
            subscription_level=subscription, marketing_opt_in=str(marketing_opt_in).lower()
        )
        
        self.app.pop_screen()  # Remove loading screen
        
        if result and result.get("success"):
            self.notify("Account created successfully! Please log in.", severity="information")
            self.app.pop_screen()
        else:
            self.notify("Account creation failed: " + result.get("message", "Unknown error"), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            username = self.query_one("#username", Input).value
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            subscription = self.query_one("#subscription", Select).value
            marketing_opt_in = self.query_one("#marketing_opt_in", Checkbox).value
            
            if all([username, email, password, subscription]):
                loading = LoadingScreen("Creating account...")
                self.app.push_screen(loading)
                self.create_user_account(username, email, password, subscription, marketing_opt_in)
            else:
                self.notify("Please fill in all fields", severity="warning")
        elif event.button.id == "back":
            self.app.pop_screen()

class MainScreen(Screen):
    """Main application screen with optimized loading"""
    
    current_view = reactive("shows")
    current_page = reactive(1)
    current_sort = reactive("name")
    current_order = reactive("ASC")
    current_genre = reactive("all")
    shows_cache = reactive({})
    visible_shows = reactive([])
    
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
        self.load_shows()

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
        elif event.button.id == "change_password":
            self.app.push_screen(ChangePasswordScreen())
        elif event.button.id == "change_subscription":
            self.app.push_screen(ChangeSubscriptionScreen())
        elif event.button.id == "delete_account":
            self.handle_delete_account()
        elif event.button.id == "update_marketing":
            self.app.push_screen(MarketingPreferenceScreen())
        elif event.button.id == "load_more":
            self.load_more_shows()
        elif event.button.id and event.button.id.startswith("genre_"):
            genre = event.button.id.replace("genre_", "")
            self.current_genre = genre
            self.current_page = 1
            self.load_shows()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "sort_select":
            self.current_sort = event.value
            self.current_page = 1
            self.load_shows()
        elif event.select.id == "order_select":
            self.current_order = event.value
            self.current_page = 1
            self.load_shows()

    def update_sidebar_buttons(self, active_button_id: str):
        """Update sidebar button styles"""
        button_ids = ["shows_btn", "my_shows_btn", "account_btn"]
        for btn_id in button_ids:
            button = self.query_one(f"#{btn_id}", Button)
            if btn_id == active_button_id:
                button.variant = "primary"
            else:
                button.variant = "default"

    @work(exclusive=True)
    async def handle_show_action_async(self, show_id: int, button: Button):
        """Handle show action asynchronously with button-specific loading"""
        original_text = button.label
        button.label = "Adding..."
        button.disabled = True
        
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(
            self.app.call_api, "add_show_to_user", 
            user_id=user_id, show_id=show_id
        )
        
        if result and result.get("success"):
            button.label = "Added ✓"
            button.variant = "default"
            button.add_class("disabled_button")
            
            # Update user info
            user_info_result = await asyncio.to_thread(
                self.app.call_api, "get_user_info", user_id=user_id
            )
            if user_info_result and user_info_result.get("success"):
                self.app.current_user.update(user_info_result.get("data", {}))
            
            self.notify("Show added successfully!", severity="information")
        else:
            button.label = original_text
            button.disabled = False
            self.notify("Failed to add show: " + result.get("message", "Unknown error"), severity="error")

    def handle_show_action(self, show_id: int) -> None:
        """Handle show action (add or rent)"""
        button = self.query_one(f"#add_show_{show_id}", Button)
        
        # Check if this requires rental confirmation
        if "premium_button" in button.classes:
            # Get show data from cache for modal
            show = None
            for cached_shows in self.shows_cache.values():
                show = next((s for s in cached_shows.get("shows", []) if s["show_id"] == show_id), None)
                if show:
                    break
            
            def handle_modal_result(result):
                if result and result.get("action") == "rent":
                    self.handle_show_action_async(show_id, button)
            
            if show:
                self.app.push_screen(
                    RentConfirmModal(show["name"], show.get("cost_to_rent", 0), show_id),
                    handle_modal_result
                )
        else:
            self.handle_show_action_async(show_id, button)

    @work(exclusive=True)
    async def load_shows_async(self, append: bool = False):
        """Load shows asynchronously with caching and virtual scrolling"""
        content = self.query_one("#content_area")
        
        if not append:
            content.remove_children()
            content.mount(LoadingIndicator())
        
        # Create cache key
        cache_key = f"{self.current_sort}_{self.current_order}_{self.current_genre}_{self.current_page}"
        
        # Check cache first
        if cache_key not in self.shows_cache:
            result = await asyncio.to_thread(
                self.app.call_api, "get_shows_paginated",
                page=self.current_page, limit=20,
                sort_by=self.current_sort, sort_order=self.current_order,
                genre=self.current_genre if self.current_genre != "all" else ""
            )
            
            if result and result.get("success"):
                self.shows_cache[cache_key] = result.get("data", {})
            else:
                if not append:
                    content.remove_children()
                    content.mount(Static("Error loading shows", classes="error_message"))
                return
        
        data = self.shows_cache[cache_key]
        shows = data.get("shows", [])
        pagination = data.get("pagination", {})
        
        if not append:
            content.remove_children()
            
            # Load genres for filter (cache these too)
            if not hasattr(self, '_genres_cache'):
                genres_result = await asyncio.to_thread(self.app.call_api, "get_genres")
                self._genres_cache = genres_result.get("data", []) if genres_result and genres_result.get("success") else []
            
            # Create header with controls
            controls = Container(
                Horizontal(
                    Static("Sort by:", classes="filter_label"),
                    Select([
                        ("name", "Name"),
                        ("rating", "Rating"),
                        ("release_date", "Release Date"),
                        ("genre", "Genre"),
                        ("length", "Length")
                    ], value=self.current_sort, id="sort_select"),
                    Select([
                        ("ASC", "Ascending"),
                        ("DESC", "Descending")
                    ], value=self.current_order, id="order_select"),
                    classes="sort_controls"
                ),
                ScrollableContainer(
                    Button("All", id="genre_all", variant="primary" if self.current_genre == "all" else "default", classes="genre_button"),
                    *[Button(genre, id=f"genre_{genre}", variant="primary" if self.current_genre == genre else "default", classes="genre_button") for genre in self._genres_cache],
                    classes="genre_filter"
                ),
                classes="controls_container"
            )
            
            content.mount(Static("Available Shows", classes="content_title"))
            content.mount(controls)
            content.mount(Container(id="shows_container", classes="shows_grid"))
        
        # Get user's shows for comparison
        user_shows = self.app.current_user.get("shows", "").split(",") if self.app.current_user.get("shows") else []
        user_show_ids = [int(x.strip()) for x in user_shows if x.strip()]
        
        shows_container = content.query_one("#shows_container")
        
        if shows:
            for show in shows:
                shows_container.mount(self.create_show_card(show, show["show_id"] in user_show_ids))
            
            # Add load more button if there are more pages
            if pagination.get("has_next"):
                if content.query("#load_more"):
                    content.query_one("#load_more").remove()
                content.mount(Button("Load More", id="load_more", variant="primary", classes="load_more_button"))
        elif not append and not shows:
            content.mount(Static("No shows available", classes="empty_message"))

    def load_shows(self) -> None:
        """Load shows from beginning"""
        self.current_page = 1
        self.load_shows_async(append=False)

    def load_more_shows(self) -> None:
        """Load next page of shows"""
        self.current_page += 1
        self.load_shows_async(append=True)

    @work(exclusive=True)
    async def load_my_shows_async(self):
        """Load user's shows asynchronously"""
        content = self.query_one("#content_area")
        content.remove_children()
        content.mount(LoadingIndicator())
        
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(self.app.call_api, "get_user_shows", user_id=user_id)
        content.remove_children()
        
        content.mount(Static("My Shows", classes="content_title"))
        
        if result and result.get("success"):
            shows = result.get("data", [])
            if shows:
                content.mount(ScrollableContainer(
                    *[self.create_my_show_card(show) for show in shows],
                    classes="shows_grid"
                ))
            else:
                content.mount(Static("No shows found", classes="empty_message"))
        else:
            content.mount(Static("Error loading shows", classes="error_message"))

    def load_my_shows(self) -> None:
        """Load and display user's shows"""
        self.load_my_shows_async()

    def load_account(self) -> None:
        """Load and display account information"""
        content = self.query_one("#content_area")
        content.remove_children()
        
        user = self.app.current_user
        
        content.mount(Static("Account Information", classes="content_title"))
        content.mount(Container(
            Static(f"Username: {user.get('username', 'N/A')}", classes="info_item"),
            Static(f"Email: {user.get('email', 'N/A')}", classes="info_item"),
            Static(f"Subscription: {user.get('subscription_level', 'N/A')}", classes="info_item"),
            Static(f"Total Spent: ${user.get('total_spent', 0):.2f}", classes="info_item"),
            Static(f"Favourite Genre: {user.get('favourite_genre', 'Not set')}", classes="info_item"),
            Static(f"Marketing Emails: {'Yes' if user.get('marketing_opt_in', False) else 'No'}", classes="info_item"),
            Horizontal(
                Button("Change Password", id="change_password", variant="default"),
                Button("Change Subscription", id="change_subscription", variant="primary"),
                classes="button_row"
            ),
            Horizontal(
                Button("Update Marketing", id="update_marketing", variant="default"),
                Button("Delete Account", id="delete_account", variant="error"),
                classes="button_row"
            ),
            classes="account_info"
        ))

    @work(exclusive=True)
    async def handle_delete_account_async(self):
        """Delete account asynchronously"""
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(self.app.call_api, "delete_user_account", user_id=user_id)
        
        self.app.pop_screen()  # Remove loading screen
        
        if result and result.get("success"):
            self.notify("Account deleted successfully", severity="information")
            self.app.current_user = None
            self.app.pop_screen()  # Return to login
        else:
            self.notify("Failed to delete account: " + result.get("message", "Unknown error"), severity="error")

    def handle_delete_account(self):
        """Handle account deletion with confirmation"""
        def handle_confirm(confirmed):
            if confirmed:
                loading = LoadingScreen("Deleting account...")
                self.app.push_screen(loading)
                self.handle_delete_account_async()
        
        self.app.push_screen(ConfirmDeleteModal(), handle_confirm)

    def create_show_card(self, show: Dict, already_owned: bool = False) -> Container:
        """Create a show card widget"""
        is_premium = show.get("access_group") == "Premium"
        user_subscription = self.app.current_user.get("subscription_level", "Basic")
        
        if already_owned:
            button_text = "Added ✓"
            button_variant = "default"
            button_classes = "disabled_button"
            button_disabled = True
        elif is_premium and user_subscription == "Basic":
            button_text = f"Rent (${show.get('cost_to_rent', 0):.2f})"
            button_variant = "warning"
            button_classes = "premium_button"
            button_disabled = False
        elif user_subscription == "Premium":
            button_text = "Add to My Shows (Free)"
            button_variant = "success"
            button_classes = "premium_included"
            button_disabled = False
        else:
            button_text = "Add to My Shows"
            button_variant = "primary"
            button_classes = "basic_button"
            button_disabled = False
        
        button = Button(
            button_text,
            id=f"add_show_{show.get('show_id')}",
            variant=button_variant,
            classes=button_classes,
            disabled=button_disabled
        )
        
        return Container(
            Static(show.get("name", "Unknown"), classes="show_title"),
            Static(f"Genre: {show.get('genre', 'N/A')}", classes="show_info"),
            Static(f"Rating: {show.get('rating', 'N/A')}/10", classes="show_info"),
            Static(f"Director: {show.get('director', 'N/A')}", classes="show_info"),
            Static(f"Length: {show.get('length', 'N/A')} min", classes="show_info"),
            Static(f"Release: {show.get('release_date', 'N/A')}", classes="show_info"),
            button,
            classes="show_card premium_card" if is_premium else "show_card basic_card"
        )

    def create_my_show_card(self, show: Dict) -> Container:
        """Create a show card for user's collection"""
        return Container(
            Static(show.get("show_name", "Unknown"), classes="show_title"),
            Static(f"Genre: {show.get('genre', 'N/A')}", classes="show_info"),
            Static(f"Rating: {show.get('rating', 'N/A')}/10", classes="show_info"),
            Static(f"Director: {show.get('director', 'N/A')}", classes="show_info"),
            Static(f"Length: {show.get('length', 'N/A')} min", classes="show_info"),
            Static(f"Release: {show.get('release_date', 'N/A')}", classes="show_info"),
            Static("✓ In Your Collection", classes="owned_status"),
            classes="show_card owned_card"
        )

class MarketingPreferenceScreen(Screen):
    """Marketing preference screen"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Marketing Preferences", classes="title"),
            Container(
                Label("Email Marketing:"),
                Checkbox("Receive marketing emails", 
                        value=self.app.current_user.get("marketing_opt_in", False), 
                        id="marketing_checkbox"),
                Horizontal(
                    Button("Update", id="submit", variant="primary"),
                    Button("Cancel", id="cancel", variant="default"),
                    classes="button_row"
                ),
                classes="form_container"
            ),
            classes="main_container"
        )
        yield Footer()

    @work(exclusive=True)
    async def update_marketing_async(self, opt_in: bool):
        """Update marketing preference asynchronously"""
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(
            self.app.call_api, "update_marketing_opt_in", 
            user_id=user_id, opt_in=str(opt_in).lower()
        )
        
        self.app.pop_screen()  # Remove loading screen
        
        if result and result.get("success"):
            self.app.current_user["marketing_opt_in"] = opt_in
            self.notify("Marketing preference updated successfully!", severity="information")
            self.app.pop_screen()
        else:
            self.notify("Failed to update preference: " + result.get("message", "Unknown error"), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            opt_in = self.query_one("#marketing_checkbox", Checkbox).value
            loading = LoadingScreen("Updating preferences...")
            self.app.push_screen(loading)
            self.update_marketing_async(opt_in)
        elif event.button.id == "cancel":
            self.app.pop_screen()

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
            classes="main_container"
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
        
        self.app.pop_screen()  # Remove loading screen
        
        if result and result.get("success"):
            self.notify("Password changed successfully!", severity="information")
            self.app.pop_screen()
        else:
            self.notify("Failed to change password: " + result.get("message", "Unknown error"), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            new_password = self.query_one("#new_password", Input).value
            confirm_password = self.query_one("#confirm_password", Input).value
            
            if new_password and confirm_password:
                if new_password == confirm_password:
                    loading = LoadingScreen("Changing password...")
                    self.app.push_screen(loading)
                    self.change_password_async(new_password)
                else:
                    self.notify("Passwords do not match", severity="warning")
            else:
                self.notify("Please fill in both fields", severity="warning")
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
                Select([("Basic", "Basic"), ("Premium", "Premium")], id="subscription"),
                Horizontal(
                    Button("Update Subscription", id="submit", variant="primary"),
                    Button("Cancel", id="cancel", variant="default"),
                    classes="button_row"
                ),
                classes="form_container"
            ),
            classes="main_container"
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
        
        self.app.pop_screen()  # Remove loading screen
        
        if result and result.get("success"):
            self.app.current_user["subscription_level"] = subscription
            
            user_info_result = await asyncio.to_thread(
                self.app.call_api, "get_user_info", user_id=user_id
            )
            if user_info_result and user_info_result.get("success"):
                self.app.current_user.update(user_info_result.get("data", {}))
            
            self.notify("Subscription updated successfully!", severity="information")
            self.app.pop_screen()
        else:
            self.notify("Failed to update subscription: " + result.get("message", "Unknown error"), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            subscription = self.query_one("#subscription", Select).value
            
            if subscription:
                loading = LoadingScreen("Updating subscription...")
                self.app.push_screen(loading)
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
        width: 80%;
        height: auto;
        min-height: 60%;
        background: #404040;
        border: solid #FF8C00;
        padding: 4;
    }
    
    .button_container {
        align: center middle;
        height: auto;
        margin: 2;
    }
    
    .main_container {
        align: center middle;
        width: 60%;
        height: 70%;
        background: #404040;
        border: solid #FF8C00;
    }
    
    .form_container {
        padding: 2;
        height: auto;
    }
    
    .button_row {
        margin-top: 2;
        height: auto;
    }
    
    Input {
        margin: 1;
        background: #2F2F2F;
        border: solid #696969;
    }
    
    Input:focus {
        border: solid #FF8C00;
    }
    
    Label {
        margin: 1 0 0 1;
        color: white;
    }
    
    Select {
        margin: 1;
        background: #2F2F2F;
        border: solid #696969;
        width: auto;
        min-width: 15;
    }
    
    Checkbox {
        margin: 1;
    }
    
    .current_sub {
        margin: 1;
        color: #FF8C00;
        text-style: bold;
    }
    
    .main_layout {
        height: 100%;
    }
    
    .sidebar {
        width: 20%;
        background: #404040;
        padding: 1;
        border-right: solid #FF8C00;
        align: center top;
    }
    
    .sidebar_button {
        width: 90%;
        margin: 1;
        height: 3;
    }
    
    .sidebar_button:hover {
        background: #FF8C00;
        color: #000000;
        border: solid #FFD700;
        text-style: bold;
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
    }
    
    .controls_container {
        background: #404040;
        border: solid #696969;
        margin: 1;
        padding: 1;
    }
    
    .sort_controls {
        height: auto;
        align: left middle;
    }
    
    .filter_label {
        color: #FF8C00;
        margin-right: 1;
    }
    
    .genre_filter {
        height: 4;
        margin-top: 1;
    }
    
    .genre_button {
        margin: 0 1 0 0;
        height: 2;
        min-width: 8;
    }
    
    .genre_button:hover {
        background: #FF8C00;
        color: #000000;
        text-style: bold;
    }
    
    .shows_grid {
        height: 100%;
    }
    
    .show_card {
        background: #404040;
        border: solid #696969;
        margin: 1;
        padding: 1;
        height: auto;
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
    }
    
    .basic_button:hover {
        background: #FFB84D;
        border: solid #FFD700;
        text-style: bold;
    }
    
    .premium_button {
        background: #FFD700;
        color: black;
        margin-top: 1;
    }
    
    .premium_button:hover {
        background: #FFF700;
        border: solid #FF8C00;
        text-style: bold;
    }
    
    .premium_included {
        background: #32CD32;
        margin-top: 1;
    }
    
    .premium_included:hover {
        background: #90EE90;
        border: solid #228B22;
        text-style: bold;
    }
    
    .disabled_button {
        background: #696969;
        color: #A0A0A0;
        margin-top: 1;
    }
    
    .load_more_button {
        width: 100%;
        margin: 2;
        background: #FF8C00;
    }
    
    .load_more_button:hover {
        background: #FFB84D;
        text-style: bold;
    }
    
    .account_info {
        padding: 2;
        background: #404040;
        border: solid #FF8C00;
        margin: 2;
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
        width: 50%;
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
    
    .modal_container {
        background: #404040;
        border: solid #FF8C00;
        width: 50%;
        height: auto;
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
    
    .warning {
        color: #FF6B6B;
        text-style: bold;
    }
    
    .modal_buttons {
        margin-top: 2;
        height: auto;
        align: center middle;
    }
    
    Button {
        margin: 1;
    }
    
    Button:hover {
        text-style: bold;
        border: solid #FF8C00;
    }
    
    Button.-primary {
        background: #FF8C00;
        color: white;
    }
    
    Button.-primary:hover {
        background: #FFB84D;
        border: solid #FFD700;
    }
    
    Button.-success {
        background: #32CD32;
        color: white;
    }
    
    Button.-success:hover {
        background: #90EE90;
        border: solid #228B22;
    }
    
    Button.-warning {
        background: #FFD700;
        color: black;
    }
    
    Button.-warning:hover {
        background: #FFF700;
        border: solid #FF8C00;
    }
    
    Button.-error {
        background: #DC143C;
        color: white;
    }
    
    Button.-error:hover {
        background: #FF6B6B;
        border: solid #FF0000;
    }
    
    Button.-default {
        background: #696969;
        color: white;
    }
    
    Button.-default:hover {
        background: #A9A9A9;
        border: solid #DCDCDC;
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
