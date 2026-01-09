"""
ARENA - System Core Logic
Contains the main ArenaSystem class that handles all business logic
for tournament management, user management, and data persistence
"""

from datetime import datetime
import json
import os
from enums import UserRole, TournamentStatus, MatchStatus


class ArenaSystem:
    """Main system class for ARENA Tournament Management"""
    
    def __init__(self):
        """Initialize the system with data file and default admin account"""
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
    
    # ==================== DATA PERSISTENCE ====================
    
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
    
    # ==================== USER MANAGEMENT ====================
    
    def register_user(self, username, password, name, email, role):
        """
        Register a new user
        
        Args:
            username: User's username
            password: User's password
            name: User's full name
            email: User's email address
            role: User's role (UserRole enum value)
            
        Returns:
            Tuple (success: bool, message: str)
        """
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
        """
        Authenticate user with credentials
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Tuple (success: bool, message: str)
        """
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        if user["password"] != password:
            return False, "Invalid password"
        
        if not user.get("approved", False):
            return False, "Account not approved yet"
        
        self.current_user = user
        return True, "Login successful"
    
    # ==================== LEAGUE MANAGEMENT ====================
    
    def create_league(self, name, game_type, description):
        """
        Create a new league
        
        Args:
            name: League name
            game_type: Type of game
            description: League description
            
        Returns:
            league_id: The newly created league ID
        """
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
    
    # ==================== TOURNAMENT MANAGEMENT ====================
    
    def create_tournament(self, league_id, name, start_date, max_players, prize_pool):
        """
        Create a tournament in a league
        
        Args:
            league_id: ID of the league
            name: Tournament name
            start_date: Start date (YYYY-MM-DD format)
            max_players: Maximum number of players
            prize_pool: Prize pool amount
            
        Returns:
            tournament_id: The newly created tournament ID
        """
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
        """
        Player applies for tournament
        
        Args:
            tournament_id: ID of the tournament
            
        Returns:
            Tuple (success: bool, message: str)
        """
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
        """
        Kick-off tournament and create matches
        
        Args:
            tournament_id: ID of the tournament
            
        Returns:
            Tuple (success: bool, message: str)
        """
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
    
    # ==================== MATCH MANAGEMENT ====================
    
    def record_match_result(self, match_id, winner, score):
        """
        Record match result
        
        Args:
            match_id: ID of the match
            winner: Username of the winner
            score: Match score
            
        Returns:
            Tuple (success: bool, message: str)
        """
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
    
    # ==================== ADVERTISEMENT MANAGEMENT ====================
    
    def create_advertisement(self, title, content, cost):
        """
        Create advertisement
        
        Args:
            title: Advertisement title
            content: Advertisement content
            cost: Cost of the advertisement
            
        Returns:
            ad_id: The newly created advertisement ID
        """
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
