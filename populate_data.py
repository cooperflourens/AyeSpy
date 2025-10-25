#!/usr/bin/env python3
"""
Data Population Script for AyeSpy
Populates the system with initial data from Congress.gov and GovInfo APIs
"""

import os
import sys
import logging
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_manager
from database.migrations import initialize_database
from api.api_manager import APIManager
from services.embedding_service import EmbeddingService

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
console = Console()


def main():
    """Main data population function."""
    console.print(Panel(
        Text("🚀 AyeSpy Data Population", style="bold blue"),
        title="Starting Data Population",
        border_style="blue"
    ))
    
    try:
        # Initialize database
        console.print("[yellow]Initializing database...[/yellow]")
        initialize_database()
        
        # Get database manager
        db_manager = get_db_manager()
        
        # Initialize API manager
        console.print("[yellow]Initializing API manager...[/yellow]")
        api_manager = APIManager()
        
        # Initialize embedding service
        console.print("[yellow]Loading embedding model...[/yellow]")
        embedding_service = EmbeddingService()
        
        console.print("[blue]🚀 Starting comprehensive data synchronization for current Congress...[/blue]")
        
        try:
            # Use the comprehensive sync method
            results = api_manager.sync_current_congress_data()
            
            # Display results
            console.print("\n[green]✅ Data synchronization completed![/green]")
            console.print("\n[blue]📊 Sync Results:[/blue]")
            
            for category, stats in results.items():
                added = stats.get('added', 0)
                updated = stats.get('updated', 0)
                errors = stats.get('errors', 0)
                
                if added > 0 or updated > 0:
                    console.print(f"  {category.title()}: +{added} added, {updated} updated, {errors} errors")
                else:
                    console.print(f"  {category.title()}: {errors} errors")
                    
        except Exception as e:
            console.print(f"[red]❌ Data synchronization failed: {e}[/red]")
            logger.error(f"Data synchronization failed: {e}")
            return False
        
        # Show summary
        console.print("\n" + "="*60)
        console.print("[bold green]🎉 Data Population Complete![/bold green]")
        console.print("="*60)
        
        # Display data counts
        with db_manager.get_session() as session:
            from database.models import Representative, Committee, Bill, Hearing, Vote
            
            rep_count = session.query(Representative).count()
            committee_count = session.query(Committee).count()
            bill_count = session.query(Bill).count()
            hearing_count = session.query(Hearing).count()
            vote_count = session.query(Vote).count()
            
            console.print(f"📊 [blue]Representatives:[/blue] {rep_count}")
            console.print(f"🏛️ [blue]Committees:[/blue] {committee_count}")
            console.print(f"📜 [blue]Bills:[/blue] {bill_count}")
            console.print(f"🎤 [blue]Hearings:[/blue] {hearing_count}")
            console.print(f"🗳️ [blue]Votes:[/blue] {vote_count}")
        
        console.print("\n[green]✅ AyeSpy is now populated with initial data![/green]")
        console.print("[yellow]You can now run the main application and start searching and tracking.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Data population failed: {e}[/red]")
        logger.error(f"Data population failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 