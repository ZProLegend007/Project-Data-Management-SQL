#!/usr/bin/env python3
"""
EasyFlixUser - User interface for EasyFlix streaming service
"""

import subprocess
import json
import sys
import os
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Input, Label, Select, Static, Header, Footer
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.reactive import reactive
from typing import Dict, List, Optional, Any

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            username = self.query_one("#username", Input).value
            password = self.query_one("#password", Input).value
            
            if username and password:
                result = self.app.call_api("authenticate_user", username=username, password=password)
                if result and result.get("success"):
                    user_data = result.get("data", {})
                    self.app.current_user = user_data
                    self.app.push_screen(MainScreen())
                else:
                    self.notify("Login failed: " + result.get("message", "Unknown error"), severity="error")
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            username = self.query_one("#username", Input).value
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            subscription = self.query_one("#subscription", Select).value
            
            if all([username, email, password, subscription]):
                result = self.app.call_api("create_user", 
                                         username=username, 
                                         email=email, 
                                         password=password, 
                                         subscription_level=subscription)
                if result and result.get("success"):
                    self.notify("Account created successfully! Please log in.", severity="information")
                    self.app.pop_screen()
                else:
                    self.notify("Account creation failed: " + result.get("message", "Unknown error"), severity="error")
            else:
                self.notify("Please fill in all fields", severity="warning")
        elif event.button.id == "back":
            self.app.pop_screen()

class MainScreen(Screen):
    """Main application screen"""
    
    current_view = reactive("shows")
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Container(
                Static("Menu", classes="menu_title"),
                Button("Browse Shows", id="shows_btn", variant="primary"),
                Button("My Shows", id="my_shows_btn", variant="default"),
                Button("Account", id="account_btn", variant="default"),
                Button("Logout", id="logout_btn", variant="error"),
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
            self.load_shows()
        elif event.button.id == "my_shows_btn":
            self.current_view = "my_shows"
            self.load_my_shows()
        elif event.button.id == "account_btn":
            self.current_view = "account"
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

    def handle_show_action(self, show_id: int) -> None:
        """Handle show action (add or rent)"""
        # Find the show data
        result = self.app.call_api("get_all_shows")
        if result and result.get("success"):
            shows = result.get("data", [])
            show = next((s for s in shows if s["show_id"] == show_id), None)
            
            if show:
                is_premium = show.get("access_group") == "Premium"
                user_subscription = self.app.current_user.get("subscription_level", "Basic")
                
                if is_premium and user_subscription == "Basic":
                    # Show rental confirmation modal
                    def handle_modal_result(result):
                        if result and result.get("action") == "rent":
                            self.rent_show(show_id)
                    
                    self.app.push_screen(
                        RentConfirmModal(show["name"], show.get("cost_to_rent", 0), show_id),
                        handle_modal_result
                    )
                else:
                    # Direct rental for premium users or basic shows
                    self.rent_show(show_id)

    def load_shows(self) -> None:
        """Load and display all shows"""
        content = self.query_one("#content_area")
        content.remove_children()
        
        result = self.app.call_api("get_all_shows")
        if result and result.get("success"):
            shows = result.get("data", [])
            
            content.mount(Static("Available Shows", classes="content_title"))
            if shows:
                content.mount(ScrollableContainer(
                    *[self.create_show_card(show) for show in shows],
                    classes="shows_grid"
                ))
            else:
                content.mount(Static("No shows available", classes="empty_message"))
        else:
            content.mount(Static("Error loading shows", classes="error_message"))

    def load_my_shows(self) -> None:
        """Load and display user's rented shows"""
        content = self.query_one("#content_area")
        content.remove_children()
        
        user_id = self.app.current_user.get("user_id")
        result = self.app.call_api("get_user_rentals", user_id=user_id)
        
        content.mount(Static("My Shows", classes="content_title"))
        
        if result and result.get("success"):
            rentals = result.get("data", [])
            if rentals:
                content.mount(ScrollableContainer(
                    *[self.create_rental_card(rental) for rental in rentals],
                    classes="shows_grid"
                ))
            else:
                content.mount(Static("No rentals found", classes="empty_message"))
        else:
            content.mount(Static("Error loading rentals", classes="error_message"))

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
            Button("Change Password", id="change_password", variant="default"),
            Button("Change Subscription", id="change_subscription", variant="primary"),
            classes="account_info"
        ))

    def create_show_card(self, show: Dict) -> Container:
        """Create a show card widget"""
        is_premium = show.get("access_group") == "Premium"
        user_subscription = self.app.current_user.get("subscription_level", "Basic")
        
        if is_premium and user_subscription == "Basic":
            button_text = f"Rent (${show.get('cost_to_rent', 0):.2f})"
            button_variant = "warning"
            button_classes = "premium_button"
        else:
            button_text = "Add to My Shows"
            button_variant = "primary" if not is_premium else "success"
            button_classes = "basic_button" if not is_premium else "premium_included"
        
        return Container(
            Static(show.get("name", "Unknown"), classes="show_title"),
            Static(f"Genre: {show.get('genre', 'N/A')}", classes="show_info"),
            Static(f"Rating: {show.get('rating', 'N/A')}/10", classes="show_info"),
            Static(f"Director: {show.get('director', 'N/A')}", classes="show_info"),
            Static(f"Length: {show.get('length', 'N/A')} min", classes="show_info"),
            Static(f"Release: {show.get('release_date', 'N/A')}", classes="show_info"),
            Button(
                button_text,
                id=f"add_show_{show.get('show_id')}",
                variant=button_variant,
                classes=button_classes
            ),
            classes="show_card premium_card" if is_premium else "show_card basic_card"
        )

    def create_rental_card(self, rental: Dict) -> Container:
        """Create a rental card widget"""
        return Container(
            Static(rental.get("show_name", "Unknown"), classes="show_title"),
            Static(f"Rented: {rental.get('rental_date', 'N/A')}", classes="show_info"),
            Static(f"Cost: ${rental.get('cost', 0):.2f}", classes="show_info"),
            Static("Expired" if rental.get("expired") else "Active", 
                  classes="status_expired" if rental.get("expired") else "status_active"),
            classes="rental_card"
        )

    def rent_show(self, show_id: int) -> None:
        """Rent a show"""
        user_id = self.app.current_user.get("user_id")
        result = self.app.call_api("create_rental", user_id=user_id, show_id=show_id)
        
        if result and result.get("success"):
            self.notify("Show added successfully!", severity="information")
            # Update user's total spent
            user_info_result = self.app.call_api("get_user_info", user_id=user_id)
            if user_info_result and user_info_result.get("success"):
                self.app.current_user.update(user_info_result.get("data", {}))
            
            if self.current_view == "shows":
                self.load_shows()
        else:
            self.notify("Failed to add show: " + result.get("message", "Unknown error"), severity="error")

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            new_password = self.query_one("#new_password", Input).value
            confirm_password = self.query_one("#confirm_password", Input).value
            
            if new_password and confirm_password:
                if new_password == confirm_password:
                    user_id = self.app.current_user.get("user_id")
                    result = self.app.call_api("change_password", user_id=user_id, new_password=new_password)
                    
                    if result and result.get("success"):
                        self.notify("Password changed successfully!", severity="information")
                        self.app.pop_screen()
                    else:
                        self.notify("Failed to change password: " + result.get("message", "Unknown error"), severity="error")
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            subscription = self.query_one("#subscription", Select).value
            
            if subscription:
                user_id = self.app.current_user.get("user_id")
                result = self.app.call_api("update_subscription", user_id=user_id, subscription_level=subscription)
                
                if result and result.get("success"):
                    self.app.current_user["subscription_level"] = subscription
                    self.notify("Subscription updated successfully!", severity="information")
                    self.app.pop_screen()
                else:
                    self.notify("Failed to update subscription: " + result.get("message", "Unknown error"), severity="error")
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
    
    .shows_grid {
        height: 100%;
    }
    
    .show_card {
        background: #404040;
        border: solid #696969;
        margin: 1;
        padding: 1;
        height: 100%;
    }
    
    .basic_card {
        border-left: solid #FF8C00;
    }
    
    .premium_card {
        border-left: solid #FFD700;
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
    
    .basic_button {
        background: #FF8C00;
        margin-top: 1;
    }
    
    .premium_button {
        background: #FFD700;
        color: black;
        margin-top: 1;
    }
    
    .premium_included {
        background: #32CD32;
        margin-top: 1;
    }
    
    .rental_card {
        background: #404040;
        border: solid #FF8C00;
        margin: 1;
        padding: 1;
        height: 100%;
    }
    
    .status_active {
        color: #32CD32;
        text-style: bold;
    }
    
    .status_expired {
        color: #DC143C;
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
    
    /* Modal Styles */
    .modal_container {
        background: #404040;
        border: solid #FF8C00;
        width: 100%;
        height: 100%;
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
    
    Button.-primary {
        background: #FF8C00;
        color: white;
    }
    
    Button.-success {
        background: #32CD32;
        color: white;
    }
    
    Button.-warning {
        background: #FFD700;
        color: black;
    }
    
    Button.-error {
        background: #DC143C;
        color: white;
    }
    
    Button.-default {
        background: #696969;
        color: white;
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
            # Check if EFAPI.py exists
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
