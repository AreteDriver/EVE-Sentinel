"""Alt relationship detection analyzer."""

from typing import List, Set
from collections import defaultdict
from sentinel.models.data_models import CharacterInfo, Transaction, Contact
from sentinel.models.analysis_result import AltRelationship


class AltDetector:
    """Detects potential alt character relationships."""
    
    def analyze(
        self,
        character_info: CharacterInfo,
        transactions: List[Transaction],
        contacts: List[Contact],
        search_function
    ) -> List[AltRelationship]:
        """
        Analyze potential alt relationships.
        
        Args:
            character_info: The character being analyzed
            transactions: Transaction history
            contacts: Known contacts
            search_function: Function to search for similar character names
            
        Returns:
            List of potential alt relationships with probability scores
        """
        potential_alts = {}
        
        # Check for similar character names
        similar_names = search_function(character_info.character_name[:5])
        for similar_char in similar_names:
            if similar_char.character_id == character_info.character_id:
                continue
                
            evidence = []
            shared_behaviors = []
            
            # Name similarity
            if self._names_similar(character_info.character_name, similar_char.character_name):
                evidence.append(f"Similar name pattern to {similar_char.character_name}")
                shared_behaviors.append("naming_pattern")
            
            if similar_char.character_id not in potential_alts:
                potential_alts[similar_char.character_id] = {
                    'char': similar_char,
                    'evidence': evidence,
                    'behaviors': shared_behaviors,
                    'score': 0.0
                }
        
        # Analyze transaction patterns
        transaction_contacts = defaultdict(int)
        transaction_amounts = defaultdict(float)
        
        for txn in transactions:
            transaction_contacts[txn.client_id] += 1
            transaction_amounts[txn.client_id] += abs(txn.amount)
        
        # Frequent ISK transfers can indicate alts
        for client_id, count in transaction_contacts.items():
            if count >= 5:  # Threshold for frequent transactions
                avg_amount = transaction_amounts[client_id] / count
                
                if client_id not in potential_alts:
                    potential_alts[client_id] = {
                        'char': None,  # Would need to look up
                        'evidence': [],
                        'behaviors': [],
                        'score': 0.0
                    }
                
                potential_alts[client_id]['evidence'].append(
                    f"Frequent ISK transfers ({count} transactions, avg {avg_amount:,.0f} ISK)"
                )
                potential_alts[client_id]['behaviors'].append("frequent_isk_transfers")
                potential_alts[client_id]['score'] += 0.3
        
        # Convert to AltRelationship objects
        results = []
        for char_id, data in potential_alts.items():
            if not data['evidence']:
                continue
                
            # Calculate probability based on evidence
            probability = min(len(data['evidence']) * 0.2 + data['score'], 0.95)
            
            char_name = data['char'].character_name if data['char'] else f"Character {char_id}"
            
            results.append(AltRelationship(
                character_id=char_id,
                character_name=char_name,
                probability=probability,
                evidence=data['evidence'],
                shared_behaviors=data['behaviors']
            ))
        
        # Sort by probability descending
        results.sort(key=lambda x: x.probability, reverse=True)
        return results
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two character names follow similar patterns."""
        # Simple heuristic: check if names share significant prefix/suffix
        if len(name1) < 3 or len(name2) < 3:
            return False
            
        # Check prefix (first 3+ chars)
        if name1[:3].lower() == name2[:3].lower() and len(name1) > 3:
            return True
            
        # Check suffix (last 3+ chars)
        if len(name1) >= 3 and len(name2) >= 3:
            if name1[-3:].lower() == name2[-3:].lower():
                return True
        
        return False
