#!/usr/bin/env python3
"""
AyeSpy - Congressional Transparency Platform
Main terminal application for searching transcripts, tracking bills, and viewing voting history.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_manager
from database.migrations import initialize_database, check_database_health
from api.api_manager import APIManager
from services.embedding_service import EmbeddingService
from services.search_service import SearchService
from services.bill_tracking_service import BillTrackingService

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ayespy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Rich console for beautiful terminal output
console = Console()


class AyeSpyTerminal:
    """Main terminal application for AyeSpy."""
    
    def __init__(self):
        """Initialize the terminal application."""
        self.console = console
        self.db_manager = None
        self.api_manager = None
        self.embedding_service = None
        self.search_service = None
        self.bill_tracking_service = None
        
        # Application state
        self.current_congress = None
        self.is_initialized = False
    
    def run(self):
        """Run the main application loop."""
        try:
            self._show_welcome()
            
            if not self._initialize_system():
                self.console.print("[red]Failed to initialize system. Exiting.[/red]")
                return
            
            self._main_menu()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Application interrupted by user.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/red]")
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self._cleanup()
    
    def _show_welcome(self):
        """Display welcome message and application information."""
        welcome_text = Text()
        welcome_text.append("🏛️  ", style="bold blue")
        welcome_text.append("AyeSpy - Congressional Transparency Platform", style="bold white")
        welcome_text.append("\n\n", style="white")
        welcome_text.append("Discover what your politicians really think, in their own words.\n", style="white")
        welcome_text.append("Search transcripts, track bills, and analyze voting patterns.\n", style="white")
        welcome_text.append("\n", style="white")
        welcome_text.append("Built for transparency and democratic accountability.", style="italic white")
        
        panel = Panel(
            welcome_text,
            title="Welcome to AyeSpy",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def _initialize_system(self) -> bool:
        """Initialize the system components."""
        self.console.print("[yellow]Initializing AyeSpy system...[/yellow]")
        
        try:
            # Initialize database
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Initializing database...", total=None)
                
                # Check if database exists and is healthy
                is_healthy, message = check_database_health()
                
                if not is_healthy:
                    progress.update(task, description="Creating database tables...")
                    success, message = initialize_database()
                    if not success:
                        self.console.print(f"[red]Database initialization failed: {message}[/red]")
                        return False
                
                progress.update(task, description="Database ready!")
            
            # Get database manager
            self.db_manager = get_db_manager()
            
            # Initialize API manager
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            )
            with progress:
                task = progress.add_task("Initializing API connections...", total=None)
                
                self.api_manager = APIManager()
                self.current_congress = self.api_manager.current_congress
                
                progress.update(task, description="API connections ready!")
            
            # Initialize services
            with progress:
                task = progress.add_task("Loading AI services...", total=None)
                
                self.embedding_service = EmbeddingService()
                self.search_service = SearchService(self.embedding_service, self.db_manager)
                self.bill_tracking_service = BillTrackingService(self.db_manager)
                
                progress.update(task, description="AI services ready!")
            
            self.is_initialized = True
            self.console.print("[green]✅ System initialized successfully![/green]")
            self.console.print(f"[blue]Current Congress: {self.current_congress}th[/blue]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]System initialization failed: {e}[/red]")
            logger.error(f"System initialization failed: {e}")
            return False
    
    def _main_menu(self):
        """Display and handle the main menu."""
        while True:
            self.console.print()
            self.console.print("=" * 60)
            self.console.print("[bold blue]MAIN MENU[/bold blue]")
            self.console.print("=" * 60)
            self.console.print()
            
            options = [
                "1. 🔍 Search Transcripts",
                "2. 📋 Track Bills",
                "3. 🗳️  View Voting History",
                "4. 📊 View Recent Updates",
                "5. 🔄 Sync Data",
                "6. ⚙️  System Status",
                "7. ❓ Help",
                "8. 🚪 Exit"
            ]
            
            for option in options:
                self.console.print(f"  {option}")
            
            self.console.print()
            
            choice = Prompt.ask(
                "Select an option",
                choices=["1", "2", "3", "4", "5", "6", "7", "8"],
                default="1"
            )
            
            if choice == "1":
                self._search_transcripts_menu()
            elif choice == "2":
                self._track_bills_menu()
            elif choice == "3":
                self._voting_history_menu()
            elif choice == "4":
                self._recent_updates_menu()
            elif choice == "5":
                self._sync_data_menu()
            elif choice == "6":
                self._system_status_menu()
            elif choice == "7":
                self._help_menu()
            elif choice == "8":
                if Confirm.ask("Are you sure you want to exit?"):
                    break
    
    def _search_transcripts_menu(self):
        """Handle transcript search functionality."""
        self.console.print()
        self.console.print("[bold blue]TRANSCRIPT SEARCH[/bold blue]")
        self.console.print("-" * 40)
        
        # Get search query
        query = Prompt.ask("Enter your search query")
        if not query.strip():
            self.console.print("[yellow]No query entered. Returning to main menu.[/yellow]")
            return
        
        # Get search filters
        representative = Prompt.ask("Filter by representative (optional, press Enter to skip)")
        if not representative.strip():
            representative = None
        
        committee = Prompt.ask("Filter by committee (optional, press Enter to skip)")
        if not committee.strip():
            committee = None
        
        max_results = Prompt.ask(
            "Maximum results",
            choices=["10", "20", "50", "100"],
            default="20"
        )
        
        # Perform search
        self.console.print()
        self.console.print("[yellow]Searching transcripts...[/yellow]")
        
        try:
            results = self.search_service.search_transcripts(
                query=query,
                representative=representative,
                committee=committee,
                max_results=int(max_results)
            )
            
            if not results:
                self.console.print("[yellow]No results found.[/yellow]")
                return
            
            # Display results
            self._display_search_results(results)
            
        except Exception as e:
            self.console.print(f"[red]Search failed: {e}[/red]")
            logger.error(f"Transcript search failed: {e}")
    
    def _display_search_results(self, results: List[Dict]):
        """Display search results in a formatted table."""
        table = Table(title="Search Results")
        table.add_column("Speaker", style="cyan")
        table.add_column("Committee", style="green")
        table.add_column("Date", style="yellow")
        table.add_column("Quote", style="white", width=60)
        table.add_column("Similarity", style="magenta")
        
        for result in results:
            table.add_row(
                result.get('speaker_name', 'Unknown'),
                result.get('committee_name', 'Unknown'),
                result.get('hearing_date', 'Unknown'),
                result.get('text', '')[:100] + "..." if len(result.get('text', '')) > 100 else result.get('text', ''),
                f"{result.get('similarity', 0):.3f}"
            )
        
        self.console.print(table)
        
        # Ask if user wants to see full quote
        if Confirm.ask("View full quote for a specific result?"):
            try:
                choice = Prompt.ask("Enter result number", default="1")
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(results):
                    result = results[choice_idx]
                    self.console.print()
                    self.console.print(Panel(
                        result.get('text', ''),
                        title=f"Full Quote - {result.get('speaker_name', 'Unknown')}",
                        border_style="blue"
                    ))
                else:
                    self.console.print("[red]Invalid result number.[/red]")
            except ValueError:
                self.console.print("[red]Invalid input.[/red]")
    
    def _track_bills_menu(self):
        """Handle bill tracking functionality."""
        self.console.print()
        self.console.print("[bold blue]BILL TRACKING[/bold blue]")
        self.console.print("-" * 40)
        
        options = [
            "1. 🔍 Search Bills",
            "2. 📋 List All Bills",
            "3. 📊 View Bill Status",
            "4. 📈 Bill Lifecycle",
            "5. 🔙 Back to Main Menu"
        ]
        
        for option in options:
            self.console.print(f"  {option}")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="1")
        
        if choice == "1":
            self._search_bills()
        elif choice == "2":
            self._list_all_bills()
        elif choice == "3":
            self._view_bill_status()
        elif choice == "4":
            self._view_bill_lifecycle()
    
    def _search_bills(self):
        """Search for bills."""
        query = Prompt.ask("Enter bill search query")
        if not query.strip():
            return
        
        try:
            bills = self.bill_tracking_service.search_bills(query)
            self._display_bills(bills)
        except Exception as e:
            self.console.print(f"[red]Bill search failed: {e}[/red]")
    
    def _list_all_bills(self):
        """List all available bills with pagination."""
        self.console.print()
        self.console.print("[bold blue]LISTING ALL BILLS[/bold blue]")
        self.console.print("-" * 40)
        
        # Get pagination preferences
        page_size = Prompt.ask(
            "Bills per page",
            choices=["10", "20", "50", "100"],
            default="20"
        )
        page_size = int(page_size)
        
        try:
            # Get total count first
            total_bills = self.bill_tracking_service.get_total_bill_count()
            self.console.print(f"[blue]Total bills available: {total_bills}[/blue]")
            
            if total_bills == 0:
                self.console.print("[yellow]No bills found in the database.[/yellow]")
                return
            
            page = 1
            while True:
                self.console.print(f"\n[bold]Page {page}[/bold]")
                
                # Get bills for current page
                bills = self.bill_tracking_service.get_bills_paginated(page=page, page_size=page_size)
                
                if not bills:
                    self.console.print("[yellow]No more bills to display.[/yellow]")
                    break
                
                # Display bills
                self._display_bills(bills)
                
                # Navigation options
                self.console.print()
                nav_options = []
                if page > 1:
                    nav_options.append("p - Previous page")
                if len(bills) == page_size:  # If we got a full page, there might be more
                    nav_options.append("n - Next page")
                nav_options.append("q - Back to menu")
                
                for option in nav_options:
                    self.console.print(f"  {option}")
                
                choice = Prompt.ask("Navigation", choices=["p", "n", "q"], default="q")
                
                if choice == "p" and page > 1:
                    page -= 1
                elif choice == "n" and len(bills) == page_size:
                    page += 1
                else:
                    break
                    
        except Exception as e:
            self.console.print(f"[red]Failed to list bills: {e}[/red]")
            logger.error(f"Failed to list bills: {e}")
    
    def _view_bill_status(self):
        """View status of a specific bill."""
        bill_id = Prompt.ask("Enter bill ID or number (e.g., HR1234)")
        if not bill_id.strip():
            return
        
        try:
            bill = self.bill_tracking_service.get_bill(bill_id)
            if bill:
                self._display_bill_details(bill)
            else:
                self.console.print("[yellow]Bill not found.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Failed to get bill: {e}[/red]")
    
    def _view_bill_lifecycle(self):
        """View the lifecycle of a bill."""
        bill_id = Prompt.ask("Enter bill ID or number")
        if not bill_id.strip():
            return
        
        try:
            lifecycle = self.bill_tracking_service.get_bill_lifecycle(bill_id)
            if lifecycle:
                self._display_bill_lifecycle(lifecycle)
            else:
                self.console.print("[yellow]Bill lifecycle not found.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Failed to get bill lifecycle: {e}[/red]")
    
    def _display_bills(self, bills: List[Dict]):
        """Display bills in a table."""
        if not bills:
            self.console.print("[yellow]No bills found.[/yellow]")
            return
        
        table = Table(title="Bill Search Results")
        table.add_column("Bill ID", style="cyan")
        table.add_column("Title", style="white", width=50)
        table.add_column("Status", style="green")
        table.add_column("Introduced", style="yellow")
        table.add_column("Sponsor", style="magenta")
        
        for bill in bills:
            table.add_row(
                f"{bill.get('bill_type', '')}{bill.get('bill_number', '')}",
                bill.get('title', '')[:50] + "..." if len(bill.get('title', '')) > 50 else bill.get('title', ''),
                bill.get('current_status', 'Unknown'),
                bill.get('introduced_date', 'Unknown'),
                bill.get('sponsor_name', 'Unknown')
            )
        
        self.console.print(table)
    
    def _display_bill_details(self, bill: Dict):
        """Display detailed bill information."""
        panel = Panel(
            f"Title: {bill.get('title', 'Unknown')}\n"
            f"Status: {bill.get('current_status', 'Unknown')}\n"
            f"Introduced: {bill.get('introduced_date', 'Unknown')}\n"
            f"Sponsor: {bill.get('sponsor_name', 'Unknown')}\n"
            f"Summary: {bill.get('summary', 'No summary available')}",
            title=f"Bill Details - {bill.get('bill_type', '')}{bill.get('bill_number', '')}",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _display_bill_lifecycle(self, lifecycle: Dict):
        """Display bill lifecycle information."""
        self.console.print()
        self.console.print("[bold blue]Bill Lifecycle[/bold blue]")
        self.console.print("-" * 40)
        
        for status in lifecycle.get('statuses', []):
            self.console.print(f"📅 {status.get('date', 'Unknown')}")
            self.console.print(f"   {status.get('status', 'Unknown')}")
            if status.get('description'):
                self.console.print(f"   📝 {status.get('description')}")
            self.console.print()
    
    def _voting_history_menu(self):
        """Handle voting history functionality."""
        self.console.print()
        self.console.print("[bold blue]VOTING HISTORY[/bold blue]")
        self.console.print("-" * 40)
        
        options = [
            "1. 👤 Representative Voting Record",
            "2. 🗳️  Bill Vote Results",
            "3. 📊 Party Voting Patterns",
            "4. 🔙 Back to Main Menu"
        ]
        
        for option in options:
            self.console.print(f"  {option}")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "1":
            self._representative_voting_record()
        elif choice == "2":
            self._bill_vote_results()
        elif choice == "3":
            self._party_voting_patterns()
    
    def _representative_voting_record(self):
        """View voting record for a specific representative."""
        name = Prompt.ask("Enter representative name")
        if not name.strip():
            return
        
        try:
            # This would be implemented in the voting service
            self.console.print("[yellow]Voting record functionality coming soon...[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Failed to get voting record: {e}[/red]")
    
    def _bill_vote_results(self):
        """View vote results for a specific bill."""
        bill_id = Prompt.ask("Enter bill ID or number")
        if not bill_id.strip():
            return
        
        try:
            # This would be implemented in the voting service
            self.console.print("[yellow]Bill vote results functionality coming soon...[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Failed to get vote results: {e}[/red]")
    
    def _party_voting_patterns(self):
        """View voting patterns by party."""
        try:
            # This would be implemented in the voting service
            self.console.print("[yellow]Party voting patterns functionality coming soon...[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Failed to get voting patterns: {e}[/red]")
    
    def _recent_updates_menu(self):
        """Display recent updates."""
        self.console.print()
        self.console.print("[bold blue]RECENT UPDATES[/bold blue]")
        self.console.print("-" * 40)
        
        try:
            recent_updates = self.api_manager.get_recent_updates(hours=24)
            
            if not any(recent_updates.values()):
                self.console.print("[yellow]No recent updates found.[/yellow]")
                return
            
            # Display recent bills
            if recent_updates.get('bills'):
                self.console.print("[bold green]Recent Bills:[/bold green]")
                for bill in recent_updates['bills'][:5]:
                    self.console.print(f"  📋 {bill.title[:60]}...")
                self.console.print()
            
            # Display recent hearings
            if recent_updates.get('hearings'):
                self.console.print("[bold blue]Recent Hearings:[/bold blue]")
                for hearing in recent_updates['hearings'][:5]:
                    self.console.print(f"  🏛️  {hearing.title[:60]}...")
                self.console.print()
            
            # Display recent votes
            if recent_updates.get('votes'):
                self.console.print("[bold magenta]Recent Votes:[/bold magenta]")
                for vote in recent_updates['votes'][:5]:
                    self.console.print(f"  🗳️  Vote on {vote.bill.title[:50]}...")
                self.console.print()
                
        except Exception as e:
            self.console.print(f"[red]Failed to get recent updates: {e}[/red]")
    
    def _sync_data_menu(self):
        """Handle data synchronization."""
        self.console.print()
        self.console.print("[bold blue]DATA SYNCHRONIZATION[/bold blue]")
        self.console.print("-" * 40)
        
        options = [
            "1. 🔄 Full Sync (All Data)",
            "2. 📊 Bills Only",
            "3. 🏛️  Hearings Only",
            "4. 📝 Transcripts Only",
            "5. 🗳️  Votes Only",
            "6. 🔙 Back to Main Menu"
        ]
        
        for option in options:
            self.console.print(f"  {option}")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6"], default="1")
        
        if choice == "1":
            self._perform_full_sync()
        elif choice == "2":
            self._sync_bills_only()
        elif choice == "3":
            self._sync_hearings_only()
        elif choice == "4":
            self._sync_transcripts_only()
        elif choice == "5":
            self._sync_votes_only()
    
    def _perform_full_sync(self):
        """Perform full data synchronization."""
        if not Confirm.ask("This will sync all data and may take a while. Continue?"):
            return
        
        self.console.print("[yellow]Starting full data synchronization...[/yellow]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Syncing data...", total=None)
                
                results = self.api_manager.sync_current_congress_data()
                
                progress.update(task, description="Sync completed!")
            
            # Display results
            self._display_sync_results(results)
            
        except Exception as e:
            self.console.print(f"[red]Data synchronization failed: {e}[/red]")
            logger.error(f"Data synchronization failed: {e}")
    
    def _sync_bills_only(self):
        """Sync bills only."""
        self.console.print("[yellow]Bill-only sync not yet implemented.[/yellow]")
    
    def _sync_hearings_only(self):
        """Sync hearings only."""
        self.console.print("[yellow]Hearing-only sync not yet implemented.[/yellow]")
    
    def _sync_transcripts_only(self):
        """Sync transcripts only."""
        self.console.print("[yellow]Transcript-only sync not yet implemented.[/yellow]")
    
    def _sync_votes_only(self):
        """Sync votes only."""
        self.console.print("[yellow]Vote-only sync not yet implemented.[/yellow]")
    
    def _display_sync_results(self, results: Dict):
        """Display synchronization results."""
        table = Table(title="Sync Results")
        table.add_column("Data Type", style="cyan")
        table.add_column("Added", style="green")
        table.add_column("Updated", style="yellow")
        table.add_column("Errors", style="red")
        
        for data_type, result in results.items():
            table.add_row(
                data_type.title(),
                str(result.get('added', 0)),
                str(result.get('updated', 0)),
                str(result.get('errors', 0))
            )
        
        self.console.print(table)
    
    def _system_status_menu(self):
        """Display system status."""
        self.console.print()
        self.console.print("[bold blue]SYSTEM STATUS[/bold blue]")
        self.console.print("-" * 40)
        
        try:
            # Database status
            is_healthy, message = check_database_health()
            db_status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
            self.console.print(f"Database: {db_status}")
            if not is_healthy:
                self.console.print(f"  Error: {message}")
            
            # API status
            congress_status = "✅ Connected" if self.api_manager else "❌ Not Connected"
            self.console.print(f"Congress.gov API: {congress_status}")
            
            govinfo_status = "✅ Connected" if self.api_manager else "❌ Not Connected"
            self.console.print(f"GovInfo API: {govinfo_status}")
            
            # AI services status
            embedding_status = "✅ Loaded" if self.embedding_service else "❌ Not Loaded"
            self.console.print(f"Embedding Service: {embedding_status}")
            
            if self.embedding_service:
                model_info = self.embedding_service.get_model_info()
                self.console.print(f"  Model: {model_info.get('model_name', 'Unknown')}")
                self.console.print(f"  Dimension: {model_info.get('embedding_dimension', 'Unknown')}")
            
            # Current Congress
            self.console.print(f"Current Congress: {self.current_congress}th")
            
        except Exception as e:
            self.console.print(f"[red]Failed to get system status: {e}[/red]")
    
    def _help_menu(self):
        """Display help information."""
        help_text = """
        [bold blue]AyeSpy Help[/bold blue]
        
        [bold]Transcript Search:[/bold]
        • Search congressional transcripts by concept or keywords
        • Filter by representative, committee, or date
        • Results show speaker, context, and similarity score
        
        [bold]Bill Tracking:[/bold]
        • Track bills from introduction through final passage
        • View bill status, sponsor, and summary
        • See complete bill lifecycle with status changes
        
        [bold]Voting History:[/bold]
        • View representative voting records
        • Analyze bill vote results
        • Examine party voting patterns
        
        [bold]Data Sync:[/bold]
        • Automatically update data from congressional APIs
        • Sync bills, hearings, transcripts, and votes
        • Keep data current and accurate
        
        [bold]Tips:[/bold]
        • Use natural language for transcript searches
        • Check system status if experiencing issues
        • Data sync may take several minutes
        """
        
        panel = Panel(help_text, title="Help", border_style="blue")
        self.console.print(panel)
        
        Prompt.ask("Press Enter to continue")
    
    def _cleanup(self):
        """Clean up resources before exit."""
        try:
            if self.db_manager:
                self.db_manager.close()
            self.console.print("[green]Goodbye![/green]")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


def main():
    """Main entry point."""
    app = AyeSpyTerminal()
    app.run()


if __name__ == "__main__":
    main() 