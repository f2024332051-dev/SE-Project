"""
ARENA - Online Gaming Tournament Management System
A complete single-file implementation based on SRS requirements
Uses tkinter for GUI (built-in Python library)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import json
import os
from enum import Enum


class UserRole(Enum):
    OPERATOR = "Operator"
    LEAGUE_OWNER = "League Owner"
    PLAYER = "Player"
    SPECTATOR = "Spectator"
    ADVERTISER = "Advertiser"


class TournamentStatus(Enum):
    ANNOUNCED = "Announced"
    OPEN_FOR_REGISTRATION = "Open for Registration"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


class MatchStatus(Enum):
    SCHEDULED = "Scheduled"
    LIVE = "Live"
    COMPLETED = "Completed"


class ArenaSystem:
    """Main system class for ARENA Tournament Management"""
    
    def __init__(self):
        self.data_file = "arena_data.json"
        self.users = {}
        self.leagues = {}
        self.tournaments = {}
        self.matches = {}
        self.advertisements = {}
        self.current_user = None
        self.load_data()
        
        # Initialize with default operator account
        if "admin" not in self.users:
            self.users["admin"] = {
                "username": "admin",
                "password": "admin123",
                "name": "System Administrator",
                "email": "admin@arena.com",
                "role": UserRole.OPERATOR.value,
                "approved": True
            }
    
    def save_data(self):
        """Save all data to JSON file"""
        data = {
            "users": self.users,
            "leagues": self.leagues,
            "tournaments": self.tournaments,
            "matches": self.matches,
            "advertisements": self.advertisements
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.users = data.get("users", {})
                    self.leagues = data.get("leagues", {})
                    self.tournaments = data.get("tournaments", {})
                    self.matches = data.get("matches", {})
                    self.advertisements = data.get("advertisements", {})
            except:
                pass
    
    def register_user(self, username, password, name, email, role):
        """Register a new user"""
        if username in self.users:
            return False, "Username already exists"
        self.users[username] = {
            "username": username,
            "password": password,
            "name": name,
            "email": email,
            "role": role,
            "approved": False if role != UserRole.SPECTATOR.value else True,
            "registered_date": datetime.now().isoformat()
        }
        self.save_data()
        return True, "Registration successful. Account pending approval."
    
    def login(self, username, password):
        """Authenticate user"""
        if username not in self.users:
            return False, "User not found"
        user = self.users[username]
        if user["password"] != password:
            return False, "Invalid password"
        if not user.get("approved", False):
            return False, "Account not approved yet"
        self.current_user = user
        return True, "Login successful"
    
    def create_league(self, name, game_type, description):
        """Create a new league (League Owner only)"""
        league_id = f"LEAGUE_{len(self.leagues) + 1}"
        self.leagues[league_id] = {
            "league_id": league_id,
            "name": name,
            "game_type": game_type,
            "description": description,
            "owner": self.current_user["username"],
            "created_date": datetime.now().isoformat(),
            "tournaments": []
        }
        self.save_data()
        return league_id
    
    def create_tournament(self, league_id, name, start_date, max_players, prize_pool):
        """Create a tournament in a league"""
        tournament_id = f"TOUR_{len(self.tournaments) + 1}"
        self.tournaments[tournament_id] = {
            "tournament_id": tournament_id,
            "league_id": league_id,
            "name": name,
            "start_date": start_date,
            "max_players": max_players,
            "prize_pool": prize_pool,
            "status": TournamentStatus.ANNOUNCED.value,
            "participants": [],
            "matches": [],
            "winner": None,
            "created_by": self.current_user["username"],
            "created_date": datetime.now().isoformat()
        }
        if league_id in self.leagues:
            self.leagues[league_id]["tournaments"].append(tournament_id)
        self.save_data()
        return tournament_id
    
    def apply_for_tournament(self, tournament_id):
        """Player applies for tournament"""
        if tournament_id not in self.tournaments:
            return False, "Tournament not found"
        tournament = self.tournaments[tournament_id]
        username = self.current_user["username"]
        
        if username in tournament["participants"]:
            return False, "Already registered for this tournament"
        if len(tournament["participants"]) >= tournament["max_players"]:
            return False, "Tournament is full"
        
        tournament["participants"].append(username)
        tournament["status"] = TournamentStatus.OPEN_FOR_REGISTRATION.value
        self.save_data()
        return True, "Application submitted successfully"
    
    def start_tournament(self, tournament_id):
        """Kick-off tournament and create matches"""
        if tournament_id not in self.tournaments:
            return False, "Tournament not found"
        tournament = self.tournaments[tournament_id]
        
        if len(tournament["participants"]) < 2:
            return False, "Need at least 2 participants"
        
        tournament["status"] = TournamentStatus.IN_PROGRESS.value
        # Create matches (simple bracket)
        participants = tournament["participants"]
        match_num = 1
        for i in range(0, len(participants) - 1, 2):
            match_id = f"{tournament_id}_MATCH_{match_num}"
            self.matches[match_id] = {
                "match_id": match_id,
                "tournament_id": tournament_id,
                "player1": participants[i],
                "player2": participants[i + 1] if i + 1 < len(participants) else "BYE",
                "status": MatchStatus.SCHEDULED.value,
                "winner": None,
                "score": "",
                "created_date": datetime.now().isoformat()
            }
            tournament["matches"].append(match_id)
            match_num += 1
        self.save_data()
        return True, "Tournament started successfully"
    
    def record_match_result(self, match_id, winner, score):
        """Record match result"""
        if match_id not in self.matches:
            return False, "Match not found"
        match = self.matches[match_id]
        match["status"] = MatchStatus.COMPLETED.value
        match["winner"] = winner
        match["score"] = score
        match["completed_date"] = datetime.now().isoformat()
        
        # Update tournament
        tournament = self.tournaments[match["tournament_id"]]
        completed_matches = sum(1 for m in tournament["matches"] 
                               if self.matches.get(m, {}).get("status") == MatchStatus.COMPLETED.value)
        
        if completed_matches == len(tournament["matches"]):
            # Tournament completed - determine winner
            winners = [self.matches[m].get("winner") for m in tournament["matches"] 
                      if self.matches[m].get("winner")]
            if winners:
                tournament["winner"] = winners[0]
                tournament["status"] = TournamentStatus.COMPLETED.value
        
        self.save_data()
        return True, "Match result recorded"
    
    def create_advertisement(self, title, content, cost):
        """Create advertisement"""
        ad_id = f"AD_{len(self.advertisements) + 1}"
        self.advertisements[ad_id] = {
            "ad_id": ad_id,
            "title": title,
            "content": content,
            "cost": cost,
            "advertiser": self.current_user["username"],
            "created_date": datetime.now().isoformat(),
            "active": True
        }
        self.save_data()
        return ad_id


class ArenaGUI:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ARENA - Online Gaming Tournament Management System")
        self.root.geometry("1000x700")
        self.system = ArenaSystem()
        self.show_login_screen()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login screen"""
        self.clear_window()
        
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", pady=20)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="ARENA", font=("Arial", 32, "bold"), 
                bg="#2c3e50", fg="white").pack()
        tk.Label(title_frame, text="Tournament Management System", 
                font=("Arial", 14), bg="#2c3e50", fg="#ecf0f1").pack()
        
        # Login Form
        login_frame = tk.Frame(self.root, pady=50)
        login_frame.pack(expand=True)
        
        tk.Label(login_frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, pady=10, sticky=tk.E)
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=25)
        self.username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(login_frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, pady=10, sticky=tk.E)
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        btn_frame = tk.Frame(login_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Login", command=self.handle_login, 
                 font=("Arial", 12), bg="#3498db", fg="white", width=12, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Register", command=self.show_register_screen, 
                 font=("Arial", 12), bg="#95a5a6", fg="white", width=12, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Default credentials hint
        hint_frame = tk.Frame(self.root, bg="#ecf0f1")
        hint_frame.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(hint_frame, text="Default Operator: admin / admin123", 
                font=("Arial", 10), bg="#ecf0f1", fg="#7f8c8d").pack(pady=5)
    
    def show_register_screen(self):
        """Display registration screen"""
        self.clear_window()
        
        tk.Label(self.root, text="Register New User", font=("Arial", 20, "bold")).pack(pady=20)
        
        register_frame = tk.Frame(self.root, pady=30)
        register_frame.pack(expand=True)
        
        fields = [
            ("Username:", "username"),
            ("Password:", "password"),
            ("Full Name:", "name"),
            ("Email:", "email")
        ]
        
        self.register_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(register_frame, text=label, font=("Arial", 12)).grid(row=i, column=0, pady=10, sticky=tk.E)
            entry = tk.Entry(register_frame, font=("Arial", 12), width=30)
            entry.grid(row=i, column=1, pady=10, padx=10)
            self.register_entries[key] = entry
            if key == "password":
                entry.config(show="*")
        
        tk.Label(register_frame, text="Role:", font=("Arial", 12)).grid(row=4, column=0, pady=10, sticky=tk.E)
        self.role_var = tk.StringVar(value=UserRole.PLAYER.value)
        role_combo = ttk.Combobox(register_frame, textvariable=self.role_var, 
                                  values=[r.value for r in UserRole if r != UserRole.OPERATOR],
                                  state="readonly", width=27)
        role_combo.grid(row=4, column=1, pady=10, padx=10)
        
        btn_frame = tk.Frame(register_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Register", command=self.handle_register, 
                 font=("Arial", 12), bg="#27ae60", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Back to Login", command=self.show_login_screen, 
                 font=("Arial", 12), bg="#95a5a6", fg="white", width=12).pack(side=tk.LEFT, padx=5)
    
    def handle_register(self):
        """Handle user registration"""
        username = self.register_entries["username"].get()
        password = self.register_entries["password"].get()
        name = self.register_entries["name"].get()
        email = self.register_entries["email"].get()
        role = self.role_var.get()
        
        if not all([username, password, name, email]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        success, message = self.system.register_user(username, password, name, email, role)
        if success:
            messagebox.showinfo("Success", message)
            self.show_login_screen()
        else:
            messagebox.showerror("Error", message)
    
    def handle_login(self):
        """Handle user login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        success, message = self.system.login(username, password)
        if success:
            self.show_main_dashboard()
        else:
            messagebox.showerror("Error", message)
    
    def show_main_dashboard(self):
        """Show main dashboard based on user role"""
        role = self.system.current_user["role"]
        
        if role == UserRole.OPERATOR.value:
            self.show_operator_dashboard()
        elif role == UserRole.LEAGUE_OWNER.value:
            self.show_league_owner_dashboard()
        elif role == UserRole.PLAYER.value:
            self.show_player_dashboard()
        elif role == UserRole.SPECTATOR.value:
            self.show_spectator_dashboard()
        elif role == UserRole.ADVERTISER.value:
            self.show_advertiser_dashboard()
    
    def create_nav_bar(self, parent):
        """Create navigation bar"""
        nav_frame = tk.Frame(parent, bg="#34495e", pady=10)
        nav_frame.pack(fill=tk.X)
        
        user_info = tk.Label(nav_frame, 
                            text=f"Logged in as: {self.system.current_user['name']} ({self.system.current_user['role']})",
                            bg="#34495e", fg="white", font=("Arial", 11))
        user_info.pack(side=tk.LEFT, padx=10)
        
        tk.Button(nav_frame, text="Logout", command=self.show_login_screen,
                 bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=10)
        
        return nav_frame
    
    def show_operator_dashboard(self):
        """Operator dashboard"""
        self.clear_window()
        self.create_nav_bar(self.root)
        
        tk.Label(self.root, text="Operator Dashboard", font=("Arial", 24, "bold")).pack(pady=20)
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # User Management Tab
        user_frame = tk.Frame(notebook)
        notebook.add(user_frame, text="User Management")
        
        tk.Label(user_frame, text="Pending User Approvals", font=("Arial", 16, "bold")).pack(pady=10)
        
        tree = ttk.Treeview(user_frame, columns=("Username", "Name", "Email", "Role", "Status"), show="headings", height=15)
        tree.heading("Username", text="Username")
        tree.heading("Name", text="Name")
        tree.heading("Email", text="Email")
        tree.heading("Role", text="Role")
        tree.heading("Status", text="Status")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for username, user in self.system.users.items():
            status = "Approved" if user.get("approved") else "Pending"
            tree.insert("", tk.END, values=(username, user["name"], user["email"], user["role"], status))
        
        btn_frame = tk.Frame(user_frame)
        btn_frame.pack(pady=10)
        
        def approve_user():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a user")
                return
            item = tree.item(selection[0])
            username = item["values"][0]
            self.system.users[username]["approved"] = True
            self.system.save_data()
            messagebox.showinfo("Success", f"User {username} approved")
            self.show_operator_dashboard()
        
        tk.Button(btn_frame, text="Approve Selected User", command=approve_user,
                 bg="#27ae60", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        
        # System Overview Tab
        overview_frame = tk.Frame(notebook)
        notebook.add(overview_frame, text="System Overview")
        
        stats_text = scrolledtext.ScrolledText(overview_frame, height=20, font=("Arial", 11))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        stats = f"""
SYSTEM STATISTICS
==================

Total Users: {len(self.system.users)}
Total Leagues: {len(self.system.leagues)}
Total Tournaments: {len(self.system.tournaments)}
Total Matches: {len(self.system.matches)}
Total Advertisements: {len(self.system.advertisements)}

Active Tournaments: {sum(1 for t in self.system.tournaments.values() 
                        if t['status'] in [TournamentStatus.IN_PROGRESS.value, 
                                         TournamentStatus.OPEN_FOR_REGISTRATION.value])}

Completed Tournaments: {sum(1 for t in self.system.tournaments.values() 
                           if t['status'] == TournamentStatus.COMPLETED.value)}
        """
        stats_text.insert(tk.END, stats)
        stats_text.config(state=tk.DISABLED)
    
    def show_league_owner_dashboard(self):
        """League Owner dashboard"""
        self.clear_window()
        self.create_nav_bar(self.root)
        
        tk.Label(self.root, text="League Owner Dashboard", font=("Arial", 24, "bold")).pack(pady=20)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create League Tab
        create_league_frame = tk.Frame(notebook)
        notebook.add(create_league_frame, text="Create League")
        
        tk.Label(create_league_frame, text="Create New League", font=("Arial", 16, "bold")).pack(pady=10)
        
        form_frame = tk.Frame(create_league_frame)
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="League Name:", font=("Arial", 12)).grid(row=0, column=0, pady=10, sticky=tk.E)
        league_name_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        league_name_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Game Type:", font=("Arial", 12)).grid(row=1, column=0, pady=10, sticky=tk.E)
        game_type_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        game_type_entry.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Description:", font=("Arial", 12)).grid(row=2, column=0, pady=10, sticky=tk.E)
        description_entry = tk.Text(form_frame, font=("Arial", 12), width=30, height=5)
        description_entry.grid(row=2, column=1, pady=10, padx=10)
        
        def create_league():
            name = league_name_entry.get()
            game_type = game_type_entry.get()
            description = description_entry.get("1.0", tk.END).strip()
            
            if not all([name, game_type, description]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            league_id = self.system.create_league(name, game_type, description)
            messagebox.showinfo("Success", f"League created successfully! ID: {league_id}")
            self.show_league_owner_dashboard()
        
        tk.Button(form_frame, text="Create League", command=create_league,
                 bg="#3498db", fg="white", font=("Arial", 11)).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Manage Tournaments Tab
        tournament_frame = tk.Frame(notebook)
        notebook.add(tournament_frame, text="Manage Tournaments")
        
        # Create Tournament Section
        create_tour_frame = tk.LabelFrame(tournament_frame, text="Create Tournament", font=("Arial", 12, "bold"))
        create_tour_frame.pack(fill=tk.X, padx=10, pady=10)
        
        inner_frame = tk.Frame(create_tour_frame)
        inner_frame.pack(pady=10)
        
        tk.Label(inner_frame, text="Select League:").grid(row=0, column=0, pady=5, padx=5)
        league_var = tk.StringVar()
        league_combo = ttk.Combobox(inner_frame, textvariable=league_var, 
                                    values=list(self.system.leagues.keys()), width=20)
        league_combo.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(inner_frame, text="Tournament Name:").grid(row=1, column=0, pady=5, padx=5)
        tour_name_entry = tk.Entry(inner_frame, width=22)
        tour_name_entry.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(inner_frame, text="Start Date (YYYY-MM-DD):").grid(row=2, column=0, pady=5, padx=5)
        start_date_entry = tk.Entry(inner_frame, width=22)
        start_date_entry.grid(row=2, column=1, pady=5, padx=5)
        start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(inner_frame, text="Max Players:").grid(row=3, column=0, pady=5, padx=5)
        max_players_entry = tk.Entry(inner_frame, width=22)
        max_players_entry.grid(row=3, column=1, pady=5, padx=5)
        
        tk.Label(inner_frame, text="Prize Pool:").grid(row=4, column=0, pady=5, padx=5)
        prize_entry = tk.Entry(inner_frame, width=22)
        prize_entry.grid(row=4, column=1, pady=5, padx=5)
        
        def create_tournament():
            league_id = league_var.get()
            name = tour_name_entry.get()
            start_date = start_date_entry.get()
            try:
                max_players = int(max_players_entry.get())
                prize_pool = prize_entry.get()
            except:
                messagebox.showerror("Error", "Invalid input")
                return
            
            if not all([league_id, name, start_date]):
                messagebox.showerror("Error", "All fields required")
                return
            
            tour_id = self.system.create_tournament(league_id, name, start_date, max_players, prize_pool)
            messagebox.showinfo("Success", f"Tournament created! ID: {tour_id}")
            self.show_league_owner_dashboard()
        
        tk.Button(inner_frame, text="Create Tournament", command=create_tournament,
                 bg="#27ae60", fg="white").grid(row=5, column=0, columnspan=2, pady=10)
        
        # View Tournaments Section
        view_frame = tk.LabelFrame(tournament_frame, text="My Tournaments", font=("Arial", 12, "bold"))
        view_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tour_tree = ttk.Treeview(view_frame, columns=("ID", "Name", "League", "Status", "Participants"), 
                                show="headings", height=10)
        tour_tree.heading("ID", text="Tournament ID")
        tour_tree.heading("Name", text="Name")
        tour_tree.heading("League", text="League")
        tour_tree.heading("Status", text="Status")
        tour_tree.heading("Participants", text="Participants")
        tour_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for tour_id, tournament in self.system.tournaments.items():
            if tournament["created_by"] == self.system.current_user["username"]:
                league_name = self.system.leagues.get(tournament["league_id"], {}).get("name", "N/A")
                participants = f"{len(tournament['participants'])}/{tournament['max_players']}"
                tour_tree.insert("", tk.END, values=(
                    tour_id, tournament["name"], league_name, 
                    tournament["status"], participants
                ))
        
        def start_selected_tournament():
            selection = tour_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Select a tournament")
                return
            item = tour_tree.item(selection[0])
            tour_id = item["values"][0]
            success, msg = self.system.start_tournament(tour_id)
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)
            self.show_league_owner_dashboard()
        
        tk.Button(view_frame, text="Start Selected Tournament", command=start_selected_tournament,
                 bg="#e67e22", fg="white").pack(pady=5)
    
    def show_player_dashboard(self):
        """Player dashboard"""
        self.clear_window()
        self.create_nav_bar(self.root)
        
        tk.Label(self.root, text="Player Dashboard", font=("Arial", 24, "bold")).pack(pady=20)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Browse Tournaments Tab
        browse_frame = tk.Frame(notebook)
        notebook.add(browse_frame, text="Browse Tournaments")
        
        tk.Label(browse_frame, text="Available Tournaments", font=("Arial", 16, "bold")).pack(pady=10)
        
        tour_tree = ttk.Treeview(browse_frame, columns=("ID", "Name", "League", "Status", "Spots"), 
                                show="headings", height=15)
        tour_tree.heading("ID", text="Tournament ID")
        tour_tree.heading("Name", text="Name")
        tour_tree.heading("League", text="League")
        tour_tree.heading("Status", text="Status")
        tour_tree.heading("Spots", text="Available Spots")
        tour_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        username = self.system.current_user["username"]
        for tour_id, tournament in self.system.tournaments.items():
            if tournament["status"] in [TournamentStatus.ANNOUNCED.value, 
                                       TournamentStatus.OPEN_FOR_REGISTRATION.value]:
                league_name = self.system.leagues.get(tournament["league_id"], {}).get("name", "N/A")
                available = tournament["max_players"] - len(tournament["participants"])
                is_registered = username in tournament["participants"]
                
                if not is_registered:
                    tour_tree.insert("", tk.END, values=(
                        tour_id, tournament["name"], league_name,
                        tournament["status"], f"{available} spots left"
                    ))
        
        def apply_to_tournament():
            selection = tour_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Select a tournament")
                return
            item = tour_tree.item(selection[0])
            tour_id = item["values"][0]
            success, msg = self.system.apply_for_tournament(tour_id)
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)
            self.show_player_dashboard()
        
        tk.Button(browse_frame, text="Apply for Selected Tournament", command=apply_to_tournament,
                 bg="#3498db", fg="white", font=("Arial", 11)).pack(pady=10)
        
        # My Tournaments Tab
        my_tour_frame = tk.Frame(notebook)
        notebook.add(my_tour_frame, text="My Tournaments")
        
        tk.Label(my_tour_frame, text="My Registered Tournaments", font=("Arial", 16, "bold")).pack(pady=10)
        
        my_tour_tree = ttk.Treeview(my_tour_frame, columns=("ID", "Name", "Status"), 
                                    show="headings", height=15)
        my_tour_tree.heading("ID", text="Tournament ID")
        my_tour_tree.heading("Name", text="Name")
        my_tour_tree.heading("Status", text="Status")
        my_tour_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for tour_id, tournament in self.system.tournaments.items():
            if username in tournament["participants"]:
                my_tour_tree.insert("", tk.END, values=(
                    tour_id, tournament["name"], tournament["status"]
                ))
        
        # View Matches Tab
        matches_frame = tk.Frame(notebook)
        notebook.add(matches_frame, text="My Matches")
        
        tk.Label(matches_frame, text="My Matches", font=("Arial", 16, "bold")).pack(pady=10)
        
        matches_tree = ttk.Treeview(matches_frame, columns=("Match ID", "Tournament", "Opponent", "Status", "Result"), 
                                   show="headings", height=15)
        matches_tree.heading("Match ID", text="Match ID")
        matches_tree.heading("Tournament", text="Tournament")
        matches_tree.heading("Opponent", text="Opponent")
        matches_tree.heading("Status", text="Status")
        matches_tree.heading("Result", text="Result")
        matches_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for match_id, match in self.system.matches.items():
            if match["player1"] == username or match["player2"] == username:
                opponent = match["player2"] if match["player1"] == username else match["player1"]
                tournament = self.system.tournaments.get(match["tournament_id"], {}).get("name", "N/A")
                result = match.get("winner", "Pending")
                matches_tree.insert("", tk.END, values=(
                    match_id, tournament, opponent, match["status"], result
                ))
    
    def show_spectator_dashboard(self):
        """Spectator dashboard"""
        self.clear_window()
        self.create_nav_bar(self.root)
        
        tk.Label(self.root, text="Spectator Dashboard", font=("Arial", 24, "bold")).pack(pady=20)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Live Matches Tab
        live_frame = tk.Frame(notebook)
        notebook.add(live_frame, text="Live Matches")
        
        tk.Label(live_frame, text="Currently Live Matches", font=("Arial", 16, "bold")).pack(pady=10)
        
        live_tree = ttk.Treeview(live_frame, columns=("Match ID", "Tournament", "Player 1", "Player 2", "Status"), 
                                show="headings", height=15)
        live_tree.heading("Match ID", text="Match ID")
        live_tree.heading("Tournament", text="Tournament")
        live_tree.heading("Player 1", text="Player 1")
        live_tree.heading("Player 2", text="Player 2")
        live_tree.heading("Status", text="Status")
        live_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for match_id, match in self.system.matches.items():
            if match["status"] == MatchStatus.LIVE.value:
                tournament = self.system.tournaments.get(match["tournament_id"], {}).get("name", "N/A")
                live_tree.insert("", tk.END, values=(
                    match_id, tournament, match["player1"], match["player2"], match["status"]
                ))
        
        # Tournament History Tab
        history_frame = tk.Frame(notebook)
        notebook.add(history_frame, text="Tournament History")
        
        tk.Label(history_frame, text="Completed Tournaments", font=("Arial", 16, "bold")).pack(pady=10)
        
        history_tree = ttk.Treeview(history_frame, columns=("ID", "Name", "League", "Winner", "Status"), 
                                   show="headings", height=15)
        history_tree.heading("ID", text="Tournament ID")
        history_tree.heading("Name", text="Name")
        history_tree.heading("League", text="League")
        history_tree.heading("Winner", text="Winner")
        history_tree.heading("Status", text="Status")
        history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for tour_id, tournament in self.system.tournaments.items():
            if tournament["status"] in [TournamentStatus.COMPLETED.value, TournamentStatus.ARCHIVED.value]:
                league_name = self.system.leagues.get(tournament["league_id"], {}).get("name", "N/A")
                winner = tournament.get("winner", "N/A")
                history_tree.insert("", tk.END, values=(
                    tour_id, tournament["name"], league_name, winner, tournament["status"]
                ))
        
        # Player Statistics Tab
        stats_frame = tk.Frame(notebook)
        notebook.add(stats_frame, text="Player Statistics")
        
        tk.Label(stats_frame, text="Player Statistics", font=("Arial", 16, "bold")).pack(pady=10)
        
        stats_text = scrolledtext.ScrolledText(stats_frame, height=20, font=("Arial", 11))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Calculate statistics
        player_stats = {}
        for match in self.system.matches.values():
            for player in [match["player1"], match["player2"]]:
                if player != "BYE" and player not in player_stats:
                    player_stats[player] = {"wins": 0, "matches": 0}
                if player != "BYE":
                    player_stats[player]["matches"] += 1
                    if match.get("winner") == player:
                        player_stats[player]["wins"] += 1
        
        stats_display = "PLAYER STATISTICS\n" + "="*50 + "\n\n"
        for player, stats in sorted(player_stats.items(), 
                                   key=lambda x: x[1]["wins"], reverse=True):
            win_rate = (stats["wins"] / stats["matches"] * 100) if stats["matches"] > 0 else 0
            stats_display += f"{player}:\n"
            stats_display += f"  Matches: {stats['matches']}\n"
            stats_display += f"  Wins: {stats['wins']}\n"
            stats_display += f"  Win Rate: {win_rate:.1f}%\n\n"
        
        stats_text.insert(tk.END, stats_display)
        stats_text.config(state=tk.DISABLED)
    
    def show_advertiser_dashboard(self):
        """Advertiser dashboard"""
        self.clear_window()
        self.create_nav_bar(self.root)
        
        tk.Label(self.root, text="Advertiser Dashboard", font=("Arial", 24, "bold")).pack(pady=20)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Advertisement Tab
        create_ad_frame = tk.Frame(notebook)
        notebook.add(create_ad_frame, text="Create Advertisement")
        
        tk.Label(create_ad_frame, text="Create New Advertisement", font=("Arial", 16, "bold")).pack(pady=10)
        
        form_frame = tk.Frame(create_ad_frame)
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Title:", font=("Arial", 12)).grid(row=0, column=0, pady=10, sticky=tk.E)
        title_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        title_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Content:", font=("Arial", 12)).grid(row=1, column=0, pady=10, sticky=tk.E)
        content_entry = tk.Text(form_frame, font=("Arial", 12), width=30, height=5)
        content_entry.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Cost ($):", font=("Arial", 12)).grid(row=2, column=0, pady=10, sticky=tk.E)
        cost_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        cost_entry.grid(row=2, column=1, pady=10, padx=10)
        
        def create_ad():
            title = title_entry.get()
            content = content_entry.get("1.0", tk.END).strip()
            try:
                cost = float(cost_entry.get())
            except:
                messagebox.showerror("Error", "Invalid cost")
                return
            
            if not all([title, content]):
                messagebox.showerror("Error", "All fields required")
                return
            
            ad_id = self.system.create_advertisement(title, content, cost)
            messagebox.showinfo("Success", f"Advertisement created! ID: {ad_id}")
            self.show_advertiser_dashboard()
        
        tk.Button(form_frame, text="Create Advertisement", command=create_ad,
                 bg="#3498db", fg="white", font=("Arial", 11)).grid(row=3, column=0, columnspan=2, pady=20)
        
        # My Advertisements Tab
        my_ads_frame = tk.Frame(notebook)
        notebook.add(my_ads_frame, text="My Advertisements")
        
        tk.Label(my_ads_frame, text="My Advertisements", font=("Arial", 16, "bold")).pack(pady=10)
        
        ads_tree = ttk.Treeview(my_ads_frame, columns=("ID", "Title", "Cost", "Status"), 
                               show="headings", height=15)
        ads_tree.heading("ID", text="Ad ID")
        ads_tree.heading("Title", text="Title")
        ads_tree.heading("Cost", text="Cost")
        ads_tree.heading("Status", text="Status")
        ads_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        username = self.system.current_user["username"]
        total_cost = 0
        for ad_id, ad in self.system.advertisements.items():
            if ad["advertiser"] == username:
                status = "Active" if ad.get("active") else "Inactive"
                ads_tree.insert("", tk.END, values=(
                    ad_id, ad["title"], f"${ad['cost']}", status
                ))
                if ad.get("active"):
                    total_cost += ad["cost"]
        
        tk.Label(my_ads_frame, text=f"Total Billing: ${total_cost:.2f}", 
                font=("Arial", 12, "bold"), fg="#e74c3c").pack(pady=10)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ArenaGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
