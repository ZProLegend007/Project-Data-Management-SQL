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
from textual.worker import work
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

class SearchModal(ModalScreen):
    """Modal for advanced search functionality"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Advanced Search", classes="modal_title"),
            Container(
                Label("Genre:"),
                Input(placeholder="Enter genre (e.g., Action, Comedy)", id="search_genre"),
                Label("Rating:"),
                Input(placeholder="Enter rating (e.g., PG-13, R)", id="search_rating"),
                Label("Year:"),
                Input(placeholder="Enter year (e.g., 2023)", id="search_year"),
                Horizontal(
                    Button("Search", id="perform_search", variant="primary"),
                    Button("Clear", id="clear_search", variant="default"),
                    Button("Cancel", id="cancel_search", variant="default"),
                    classes="modal_buttons"
                ),
                classes="search_form"
            ),
            classes="modal_container"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "perform_search":
            genre = self.query_one("#search_genre", Input).value.strip()
            rating = self.query_one("#search_rating", Input).value.strip()
            year_str = self.query_one("#search_year", Input).value.strip()
            
            year = None
            if year_str:
                try:
                    year = int(year_str)
                except ValueError:
                    pass
            
            self.dismiss({
                "action": "search",
                "genre": genre if genre else None,
                "rating": rating if rating else None,
                "year": year
            })
        elif event.button.id == "clear_search":
            self.dismiss({"action": "clear"})
        else:
            self.dismiss(None)

class RentConfirmModal(ModalScreen):
    """Modal for confirming premium show rental"""
    
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
            classes="modal_container"
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
            classes="modal_container"
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
                self.app.pop_screen()
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
            classes="main_container"
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
        if result and result.get("success"):
            charged = result.get("data", {}).get("charged", 0)
            self.notify(f"Account created successfully! Charged: ${charged:.2f}. Please log in.", severity="information")
            self.app.pop_screen()
        else:
            self.notify("Account creation failed: " + result.get("message", "Unknown error"), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            username = self.query_one("#username", Input).value
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            subscription = self.query_one("#subscription", Select).value
            marketing_opt_in = self.query_one("#marketing_checkbox", Checkbox).value
            
            if all([username, email, password, subscription]):
                loading = LoadingScreen("Creating account...")
                self.app.push_screen(loading)
                self.create_user_account(username, email, password, subscription, marketing_opt_in)
                self.app.pop_screen()
            else:
                self.notify("Please fill in all fields", severity="warning")
        elif event.button.id == "back":
            self.app.pop_screen()

class MainScreen(Screen):
    """Main application screen"""
    
    current_view = reactive("shows")
    current_search_filters = {}
    
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
        elif event.button.id == "search_shows":
            self.app.push_screen(SearchModal(), self.handle_search_result)
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

    def handle_search_result(self, result):
        """Handle search modal result"""
        if result:
            if result.get("action") == "search":
                self.current_search_filters = {k: v for k, v in result.items() if k != "action" and v is not None}
                self.load_shows()
            elif result.get("action") == "clear":
                self.current_search_filters = {}
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
    async def handle_show_action_async(self, show_id: int):
        """Handle show action asynchronously"""
        if self.current_search_filters:
            shows_result = await asyncio.to_thread(self.app.call_api, "search_shows", **self.current_search_filters)
        else:
            shows_result = await asyncio.to_thread(self.app.call_api, "get_all_shows")
            
        if shows_result and shows_result.get("success"):
            shows = shows_result.get("data", [])
            show = next((s for s in shows if s["show_id"] == show_id), None)
            
            if show:
                is_premium = show.get("access_group") == "Premium"
                user_subscription = self.app.current_user.get("subscription_level", "Basic")
                
                if is_premium and user_subscription == "Basic":
                    def handle_modal_result(result):
                        if result and result.get("action") == "rent":
                            self.add_show_to_user(show_id)
                    
                    self.app.push_screen(
                        RentConfirmModal(show["name"], show.get("cost_to_rent", 0), show_id),
                        handle_modal_result
                    )
                else:
                    self.add_show_to_user(show_id)

    def handle_show_action(self, show_id: int) -> None:
        """Handle show action (add or rent)"""
        self.handle_show_action_async(show_id)

    @work(exclusive=True)
    async def handle_remove_show_async(self, show_id: int):
        """Handle show removal asynchronously"""
        user_shows_result = await asyncio.to_thread(self.app.call_api, "get_user_shows", user_id=self.app.current_user.get("user_id"))
        if user_shows_result and user_shows_result.get("success"):
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

    def handle_remove_show(self, show_id: int) -> None:
        """Handle show removal"""
        self.handle_remove_show_async(show_id)

    @work(exclusive=True)
    async def add_show_to_user(self, show_id: int):
        """Add show to user's collection asynchronously"""
        loading = LoadingScreen("Adding show...")
        self.app.push_screen(loading)
        
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(
            self.app.call_api, "add_show_to_user", 
            user_id=user_id, show_id=show_id
        )
        
        self.app.pop_screen()
        
        if result and result.get("success"):
            self.notify("Show added successfully!", severity="information")
            user_info_result = await asyncio.to_thread(
                self.app.call_api, "get_user_info", user_id=user_id
            )
            if user_info_result and user_info_result.get("success"):
                self.app.current_user.update(user_info_result.get("data", {}))
            
            if self.current_view == "shows":
                self.load_shows()
        else:
            self.notify("Failed to add show: " + result.get("message", "Unknown error"), severity="error")

    @work(exclusive=True)
    async def remove_show_from_user(self, show_id: int):
        """Remove show from user's collection asynchronously"""
        loading = LoadingScreen("Removing show...")
        self.app.push_screen(loading)
        
        user_id = self.app.current_user.get("user_id")
        result = await asyncio.to_thread(
            self.app.call_api, "remove_show_from_user", 
            user_id=user_id, show_id=show_id
        )
        
        self.app.pop_screen()
        
        if result and result.get("success"):
            self.notify("Show removed successfully!", severity="information")
            user_info_result = await asyncio.to_thread(
                self.app.call_api, "get_user_info", user_id=user_id
            )
            if user_info_result and user_info_result.get("success"):
                self.app.current_user.update(user_info_result.get("data", {}))
            
            if self.current_view == "my_shows":
                self.load_my_shows()
        else:
            self.notify("Failed to remove show: " + result.get("message", "Unknown error"), severity="error")

    @work(exclusive=True)
    async def load_shows_async(self):
        """Load shows asynchronously"""
        content = self.query_one("#content_area")
        content.remove_children()
        content.mount(LoadingIndicator())
        
        if self.current_search_filters:
            result = await asyncio.to_thread(self.app.call_api, "search_shows", **self.current_search_filters)
        else:
            result = await asyncio.to_thread(self.app.call_api, "get_all_shows")
            
        content.remove_children()
        
        if result and result.get("success"):
            shows = result.get("data", [])
            user_shows = self.app.current_user.get("shows", "").split(",") if self.app.current_user.get("shows") else []
            user_show_ids = [int(x.strip()) for x in user_shows if x.strip()]
            
            title = "Search Results" if self.current_search_filters else "Available Shows"
            content.mount(Static(title, classes="content_title"))
            content.mount(Button("Advanced Search", id="search_shows", variant="warning", classes="search_button"))
            
            if shows:
                content.mount(ScrollableContainer(
                    *[self.create_show_card(show, show["show_id"] in user_show_ids) for show in shows],
                    classes="shows_grid"
                ))
            else:
                content.mount(Static("No shows found", classes="empty_message"))
        else:
            content.mount(Static("Error loading shows", classes="error_message"))

    def load_shows(self) -> None:
        """Load and display all shows"""
        self.load_shows_async()

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
            button_text = f"Buy (${show.get('cost_to_rent', 0):.2f})"
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
            Static(f"Rating: {show.get('rating', 'N/A')}", classes="show_info"),
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
                    self.app.pop_screen()
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
            classes="main_container"
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
        
        if result and result.get("success"):
            self.app.current_user["marketing_opt_in"] = marketing_opt_in
            self.notify("Marketing preference updated successfully!", severity="information")
            self.app.pop_screen()
            
            # Reload account page
            main_screen = self.app.screen_stack[-1]
            if hasattr(main_screen, 'load_account') and main_screen.current_view == "account":
                main_screen.load_account()
        else:
            self.notify("Failed to update preference: " + result.get("message", "Unknown error"), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            marketing_opt_in = self.query_one("#marketing_checkbox", Checkbox).value
            loading = LoadingScreen("Updating preference...")
            self.app.push_screen(loading)
            self.update_marketing_preference_async(marketing_opt_in)
            self.app.pop_screen()
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
        
        if result and result.get("success"):
            # Update user data immediately
            user_info_result = await asyncio.to_thread(
                self.app.call_api, "get_user_info", user_id=user_id
            )
            if user_info_result and user_info_result.get("success"):
                self.app.current_user.update(user_info_result.get("data", {}))
            
            charged = result.get("data", {}).get("charged", 0)
            if charged > 0:
                self.notify(f"Subscription updated successfully! Charged: ${charged:.2f}", severity="information")
            else:
                self.notify("Subscription updated successfully!", severity="information")
            self.app.pop_screen()
            
            # Force reload of the account view if it's currently displayed
            main_screen = self.app.screen_stack[-1]
            if hasattr(main_screen, 'load_account') and main_screen.current_view == "account":
                main_screen.load_account()
        else:
            self.notify("Failed to update subscription: " + result.get("message", "Unknown error"), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            subscription = self.query_one("#subscription", Select).value
            
            if subscription:
                loading = LoadingScreen("Updating subscription...")
                self.app.push_screen(loading)
                self.update_subscription_async(subscription)
                self.app.pop_screen()
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
    
    .main_container {
        align: center middle;
        width: 100%;
        height: 100%;
        background: #404040;
        border: solid #FF8C00;
    }
    
    .form_container {
        padding: 2;
        height: auto;
        width: 100%;
    }
    
    .search_form {
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
        width: 100%;
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
        width: 90%;
        margin: 1;
        height: 3;
        text-align: center;
        content-align: center middle;
    }
    
    .sidebar_button:hover {
        background: #FF8C00;
        color: #000000;
        border: solid #FFD700;
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
    
    .search_button {
        margin: 1;
        width: auto;
    }
    
    .shows_grid {
        height: 100%;
        width: 100%;
    }
    
    .show_card {
        background: #404040;
        border: solid #696969;
        margin: 1;
        padding: 1;
        height: auto;
        width: 100%;
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
    }
    
    .premium_button {
        background: #FFD700;
        color: black;
        margin-top: 1;
    }
    
    .premium_button:hover {
        background: #FFF700;
        border: solid #FF8C00;
    }
    
    .premium_included {
        background: #32CD32;
        margin-top: 1;
    }
    
    .premium_included:hover {
        background: #90EE90;
        border: solid #228B22;
    }
    
    .disabled_button {
        background: #696969;
        color: #A0A0A0;
        margin-top: 1;
    }
    
    .remove_button {
        background: #DC143C;
        margin-top: 1;
        width: 100%;
    }
    
    .remove_button:hover {
        background: #FF6B6B;
        border: solid #FF0000;
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
        width: 60%;
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
        background: #555555;
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
                if isinstance(value, bool):
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
