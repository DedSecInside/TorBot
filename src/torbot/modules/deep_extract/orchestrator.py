"""
Deep Content Extraction Orchestrator

This module coordinates all extractors and provides a unified interface
for deep content analysis.
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime

from .base import ExtractionResult
from .credentials_extractor import CredentialsExtractor
from .pii_extractor import PIIExtractor
from .crypto_extractor import CryptoExtractor
from .hidden_services_extractor import HiddenServicesExtractor
from .threat_indicators_extractor import ThreatIndicatorsExtractor
from .marketplace_extractor import MarketplaceExtractor
from .communication_extractor import CommunicationExtractor
from .breach_detector import BreachDetector
from .linguistic_analyzer import LinguisticAnalyzer


class DeepExtractor:
    """
    Orchestrates all deep content extraction modules
    """
    
    def __init__(self):
        """Initialize all extractors"""
        self.extractors = {
            'credentials': CredentialsExtractor(),
            'pii': PIIExtractor(),
            'cryptocurrency': CryptoExtractor(),
            'hidden_services': HiddenServicesExtractor(),
            'threat_indicators': ThreatIndicatorsExtractor(),
            'marketplace': MarketplaceExtractor(),
            'communication': CommunicationExtractor(),
            'data_breach': BreachDetector(),
            'linguistic_analysis': LinguisticAnalyzer()
        }
        
        self.all_results: List[ExtractionResult] = []
        self.logger = logging.getLogger(__name__)
    
    def extract_all(self, text: str, url: str = "") -> Dict[str, List[ExtractionResult]]:
        """
        Run all extractors on the given text
        
        Args:
            text: The text content to analyze
            url: The source URL (optional)
            
        Returns:
            Dictionary mapping extractor names to their results
        """
        results_by_category = {}
        
        self.logger.info(f"Starting deep extraction for URL: {url}")
        
        for name, extractor in self.extractors.items():
            try:
                self.logger.debug(f"Running {name} extractor...")
                extractor_results = extractor.extract(text, url)
                results_by_category[name] = extractor_results
                self.all_results.extend(extractor_results)
                
                if extractor_results:
                    self.logger.info(
                        f"{name}: Found {len(extractor_results)} items"
                    )
            except Exception as e:
                self.logger.error(f"Error in {name} extractor: {str(e)}")
                results_by_category[name] = []
        
        return results_by_category
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all extraction results
        
        Returns:
            Dictionary containing summary statistics
        """
        summary = {
            'total_findings': len(self.all_results),
            'by_category': {},
            'by_risk_level': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'high_confidence_findings': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Count by category
        for result in self.all_results:
            category = result.category
            if category not in summary['by_category']:
                summary['by_category'][category] = 0
            summary['by_category'][category] += 1
            
            # Count by risk level
            risk_level = result.risk_level
            if risk_level in summary['by_risk_level']:
                summary['by_risk_level'][risk_level] += 1
            
            # Count high confidence findings
            if result.confidence >= 0.8:
                summary['high_confidence_findings'] += 1
        
        return summary
    
    def get_critical_findings(self, min_confidence: float = 0.7) -> List[ExtractionResult]:
        """
        Get critical risk findings above a confidence threshold
        
        Args:
            min_confidence: Minimum confidence threshold (0.0 to 1.0)
            
        Returns:
            List of critical findings
        """
        return [
            result for result in self.all_results
            if result.risk_level == 'critical' and result.confidence >= min_confidence
        ]
    
    def export_to_json(self, filepath: str, include_summary: bool = True) -> None:
        """
        Export all results to a JSON file
        
        Args:
            filepath: Path to output JSON file
            include_summary: Whether to include summary statistics
        """
        try:
            export_data = {
                'extraction_results': [
                    result.to_dict() for result in self.all_results
                ]
            }
            
            if include_summary:
                export_data['summary'] = self.get_summary()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(self.all_results)} findings to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            raise
    
    def export_to_text(self, filepath: str) -> None:
        """
        Export results to a human-readable text file
        
        Args:
            filepath: Path to output text file
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("TORBOT DEEP EXTRACTION INTELLIGENCE REPORT\n")
                f.write("="*80 + "\n\n")
                
                # Write summary
                summary = self.get_summary()
                f.write("SUMMARY\n")
                f.write("-"*80 + "\n")
                f.write(f"Total Findings: {summary['total_findings']}\n")
                f.write(f"High Confidence Findings: {summary['high_confidence_findings']}\n")
                # f.write   f"\nFindings by Risk Level:\n")
                for risk, count in summary['by_risk_level'].items():
                    f.write(f"  {risk.upper()}: {count}\n")
                # f.write(f"\nFindings by Category:\n")
                
                for category, count in summary['by_category'].items():
                    f.write(f"  {category}: {count}\n")
                f.write("\n\n")
                
                # Write detailed findings
                f.write("DETAILED FINDINGS\n")
                f.write("=" * 80 + "\n\n")
                
                # Group by category
                by_category = {}
                for result in self.all_results:
                    if result.category not in by_category:
                        by_category[result.category] = []
                    by_category[result.category].append(result)
                
                # Write each category
                for category, results in sorted(by_category.items()):
                    f.write(f"\n{category.upper()}\n")
                    f.write("-" * 80 + "\n")
                    
                    for i, result in enumerate(results, 1):
                        f.write(f"\n[{i}] {result.data.get('type', 'unknown')}\n")
                        f.write(f"    Risk Level: {result.risk_level.upper()}\n")
                        f.write(f"    Confidence: {result.confidence:.2f}\n")
                        f.write(f"    Location: {result.location}\n")
                        
                        # Write data
                        f.write("    Data:\n")
                        for key, value in result.data.items():
                            if key != 'type' and value is not None:
                                # Truncate long values
                                str_value = str(value)
                                if len(str_value) > 100:
                                    str_value = str_value[:100] + "..."
                                f.write(f"      {key}: {str_value}\n")
                        
                        # Write context if available
                        if result.context:
                            f.write(f"    Context: {result.context}\n")
                        
                        f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")
            
            self.logger.info(f"Exported report to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to text: {str(e)}")
            raise
    
    def print_summary(self) -> None:
        """Print a summary of findings to console"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("DEEP EXTRACTION SUMMARY")
        print("="*60)
        print(f"\nTotal Findings: {summary['total_findings']}")
        print(f"High Confidence Findings (>80%): {summary['high_confidence_findings']}")
        
        print("\nFindings by Risk Level:")
        for risk in ['critical', 'high', 'medium', 'low']:
            count = summary['by_risk_level'][risk]
            if count > 0:
                print(f"  {risk.upper():12} {count:4d}")
        
        print("\nFindings by Category:")
        for category, count in sorted(summary['by_category'].items()):
            print(f"  {category:25} {count:4d}")
        
        print("\n" + "="*60 + "\n")
    
    def get_results_by_category(self, category: str) -> List[ExtractionResult]:
        """
        Get all results for a specific category
        
        Args:
            category: Category name
            
        Returns:
            List of results for that category
        """
        return [r for r in self.all_results if r.category == category]
    
    def get_results_by_risk_level(self, risk_level: str) -> List[ExtractionResult]:
        """
        Get all results for a specific risk level
        
        Args:
            risk_level: Risk level (critical, high, medium, low)
            
        Returns:
            List of results for that risk level
        """
        return [r for r in self.all_results if r.risk_level == risk_level]
    
    def clear_results(self) -> None:
        """Clear all stored results"""
        self.all_results.clear()
        for extractor in self.extractors.values():
            extractor.results.clear()

