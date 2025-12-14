# Data Source Integration Guide

This guide explains how to integrate Sentinel with your alliance's intel data sources.

## Overview

Sentinel uses a simple interface (`DataSource`) to retrieve character data. You need to implement this interface to connect Sentinel to your data source (database views, internal APIs, etc.).

## The DataSource Interface

All data sources must implement the `DataSource` abstract base class defined in `sentinel/data_sources/base.py`.

### Required Methods

```python
from sentinel.data_sources.base import DataSource

class MyCustomDataSource(DataSource):
    def __init__(self, connection_string):
        # Initialize your connection
        self.conn = create_connection(connection_string)
    
    def get_character_info(self, character_id: int) -> Optional[CharacterInfo]:
        """Get basic character information."""
        # Query your database/API
        # Return CharacterInfo object or None
        pass
    
    def get_corporation_history(self, character_id: int) -> List[CorporationHistory]:
        """Get character's corporation employment history."""
        pass
    
    def get_transactions(self, character_id: int, limit: Optional[int] = None) -> List[Transaction]:
        """Get character's transaction history."""
        pass
    
    def get_contracts(self, character_id: int, limit: Optional[int] = None) -> List[Contract]:
        """Get character's contract history."""
        pass
    
    def get_contacts(self, character_id: int) -> List[Contact]:
        """Get character's known contacts/associates."""
        pass
    
    def get_alliance_info(self, alliance_id: int) -> Optional[AllianceInfo]:
        """Get alliance information."""
        pass
    
    def search_characters_by_pattern(self, pattern: str) -> List[CharacterInfo]:
        """Search for characters matching a pattern (for alt detection)."""
        pass
```

## Example: PostgreSQL Data Source

Here's a complete example of implementing a data source that reads from PostgreSQL:

```python
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from sentinel.data_sources.base import DataSource
from sentinel.models.data_models import *

class PostgreSQLDataSource(DataSource):
    """Data source that reads from PostgreSQL database."""
    
    def __init__(self, connection_string: str):
        """
        Initialize PostgreSQL connection.
        
        Args:
            connection_string: PostgreSQL connection string
                e.g., "host=localhost dbname=intel user=readonly password=xxx"
        """
        self.conn = psycopg2.connect(connection_string)
    
    def get_character_info(self, character_id: int) -> Optional[CharacterInfo]:
        """Get basic character information."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    character_id,
                    character_name,
                    corporation_id,
                    corporation_name,
                    alliance_id,
                    alliance_name,
                    security_status
                FROM character_info_view
                WHERE character_id = %s
            """, (character_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return CharacterInfo(**row)
    
    def get_corporation_history(self, character_id: int) -> List[CorporationHistory]:
        """Get character's corporation employment history."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    corporation_id,
                    corporation_name,
                    start_date,
                    end_date,
                    is_deleted
                FROM corporation_history_view
                WHERE character_id = %s
                ORDER BY start_date DESC
            """, (character_id,))
            
            rows = cur.fetchall()
            return [CorporationHistory(**row) for row in rows]
    
    def get_transactions(self, character_id: int, limit: Optional[int] = None) -> List[Transaction]:
        """Get character's transaction history."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT 
                    transaction_id,
                    date,
                    client_id,
                    amount,
                    description,
                    is_personal,
                    journal_ref_type
                FROM transactions_view
                WHERE character_id = %s
                ORDER BY date DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cur.execute(query, (character_id,))
            rows = cur.fetchall()
            return [Transaction(**row) for row in rows]
    
    # ... implement other methods similarly
```

## Example: REST API Data Source

Here's an example using an internal REST API:

```python
import requests
from typing import List, Optional
from sentinel.data_sources.base import DataSource
from sentinel.models.data_models import *

class APIDataSource(DataSource):
    """Data source that reads from a REST API."""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the API (e.g., "https://intel.alliance.com/api")
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def get_character_info(self, character_id: int) -> Optional[CharacterInfo]:
        """Get basic character information."""
        try:
            response = self.session.get(
                f"{self.base_url}/characters/{character_id}"
            )
            response.raise_for_status()
            data = response.json()
            return CharacterInfo(**data)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def get_corporation_history(self, character_id: int) -> List[CorporationHistory]:
        """Get character's corporation employment history."""
        response = self.session.get(
            f"{self.base_url}/characters/{character_id}/corporations"
        )
        response.raise_for_status()
        data = response.json()
        return [CorporationHistory(**item) for item in data]
    
    # ... implement other methods similarly
```

## Data Requirements

### Minimum Required Data

For basic analysis, you need:
- Character basic info (name, current corp, alliance)
- Corporation history

### Recommended Data

For comprehensive analysis:
- Transaction/wallet journal history (ISK transfers)
- Contract history
- Known contacts/associates

### Optional Data

For enhanced analysis:
- Alliance information (hostile/friendly status)
- Character age/creation date
- Additional metadata

## Testing Your Integration

Use the provided mock data source as a reference:

```python
from sentinel import SentinelAnalyzer
from my_data_source import MyCustomDataSource

# Initialize your data source
data_source = MyCustomDataSource(connection_string="...")

# Create analyzer
analyzer = SentinelAnalyzer(data_source)

# Test with a known character
result = analyzer.analyze_character(12345)

if result:
    print(f"Risk Score: {result.overall_risk_score}")
    print(f"Flags: {len(result.hard_flags)} hard, {len(result.soft_flags)} soft")
else:
    print("Character not found")
```

## Performance Considerations

1. **Implement caching** if your data source is slow
2. **Use connection pooling** for database connections
3. **Consider limiting** transaction/contract history (e.g., last 6 months)
4. **Index your database** on character_id fields for fast lookups

## Security Notes

1. **Read-only access**: Use read-only database credentials
2. **No ESI tokens**: Sentinel should NEVER handle ESI tokens directly
3. **API keys**: Store API keys securely (environment variables, secrets manager)
4. **Data privacy**: Ensure compliance with your alliance's data policies
