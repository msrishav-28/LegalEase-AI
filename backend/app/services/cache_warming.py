"""Cache warming service for preloading frequently accessed data."""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from app.core.cache import cache_manager
from app.config import get_settings

logger = logging.getLogger(__name__)


class CacheWarmingService:
    """Service for warming cache with frequently accessed data."""
    
    def __init__(self):
        """Initialize cache warming service."""
        self.settings = get_settings()
        self.is_warming = False
        self.last_warming_time: Optional[datetime] = None
        self.warming_stats: Dict[str, Any] = {}
    
    async def warm_all_caches(self) -> Dict[str, Any]:
        """Warm all cache categories."""
        if self.is_warming:
            logger.warning("Cache warming already in progress")
            return {"status": "already_running"}
        
        self.is_warming = True
        start_time = datetime.utcnow()
        
        try:
            logger.info("Starting comprehensive cache warming...")
            
            results = {}
            
            # Warm jurisdiction-specific caches
            jurisdiction_results = await self._warm_jurisdiction_caches()
            results["jurisdictions"] = jurisdiction_results
            
            # Warm frequently accessed data
            frequent_data_results = await cache_manager.warm_frequently_accessed_data()
            results["frequent_data"] = frequent_data_results
            
            # Warm legal reference data
            legal_refs_results = await self._warm_legal_references()
            results["legal_references"] = legal_refs_results
            
            # Warm analysis templates
            template_results = await self._warm_analysis_templates()
            results["templates"] = template_results
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.last_warming_time = end_time
            self.warming_stats = {
                "last_run": end_time.isoformat(),
                "duration_seconds": duration,
                "results": results
            }
            
            logger.info(f"Cache warming completed in {duration:.2f} seconds")
            
            return {
                "status": "completed",
                "duration_seconds": duration,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
        finally:
            self.is_warming = False
    
    async def _warm_jurisdiction_caches(self) -> Dict[str, Any]:
        """Warm jurisdiction-specific caches."""
        jurisdictions = ["IN", "US"]
        document_types = ["contract", "agreement", "mou", "nda"]
        analysis_types = ["comprehensive", "risk_analysis", "compliance_check"]
        
        results = {}
        
        for jurisdiction in jurisdictions:
            try:
                result = await cache_manager.warm_jurisdiction_cache(
                    jurisdiction, document_types, analysis_types
                )
                results[jurisdiction] = result
                
                # Add small delay to prevent overwhelming Redis
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to warm {jurisdiction} jurisdiction cache: {e}")
                results[jurisdiction] = {"error": str(e)}
        
        return results
    
    async def _warm_legal_references(self) -> Dict[str, Any]:
        """Warm legal reference data cache."""
        try:
            references = {
                # Indian legal references
                "indian_contract_act_sections": await self._get_indian_contract_act_sections(),
                "indian_companies_act_sections": await self._get_indian_companies_act_sections(),
                "gst_rates": await self._get_gst_rates(),
                "stamp_duty_rates": await self._get_stamp_duty_rates(),
                
                # US legal references
                "ucc_articles": await self._get_ucc_articles(),
                "federal_regulations": await self._get_federal_regulations(),
                "state_law_variations": await self._get_state_law_variations(),
                "securities_regulations": await self._get_securities_regulations()
            }
            
            cached_count = 0
            failed_count = 0
            
            for ref_type, ref_data in references.items():
                cache_key = f"legal_reference:{ref_type}"
                success = await cache_manager.set(cache_key, ref_data, ttl=604800)  # 7 days
                if success:
                    cached_count += 1
                else:
                    failed_count += 1
            
            return {
                "cached": cached_count,
                "failed": failed_count,
                "total_references": len(references)
            }
            
        except Exception as e:
            logger.error(f"Failed to warm legal references: {e}")
            return {"error": str(e)}
    
    async def _warm_analysis_templates(self) -> Dict[str, Any]:
        """Warm analysis templates cache."""
        try:
            templates = {
                "executive_summary_template": {
                    "structure": ["overview", "key_findings", "recommendations"],
                    "max_length": 500,
                    "jurisdiction_specific": True
                },
                "risk_analysis_template": {
                    "categories": ["legal", "financial", "operational", "compliance"],
                    "severity_levels": ["low", "medium", "high", "critical"],
                    "jurisdiction_specific": True
                },
                "compliance_checklist_template": {
                    "indian_requirements": ["stamp_duty", "registration", "gst", "fema"],
                    "us_requirements": ["securities", "antitrust", "privacy", "state_law"],
                    "cross_border": ["tax_treaty", "enforcement", "dispute_resolution"]
                }
            }
            
            cached_count = 0
            
            for template_name, template_data in templates.items():
                cache_key = f"analysis_template:{template_name}"
                success = await cache_manager.set(cache_key, template_data, ttl=86400)  # 24 hours
                if success:
                    cached_count += 1
            
            return {"cached": cached_count, "total_templates": len(templates)}
            
        except Exception as e:
            logger.error(f"Failed to warm analysis templates: {e}")
            return {"error": str(e)}
    
    async def _get_indian_contract_act_sections(self) -> Dict[str, str]:
        """Get Indian Contract Act sections for caching."""
        return {
            "section_10": "What agreements are contracts",
            "section_23": "What consideration and objects are lawful",
            "section_73": "Compensation for loss or damage caused by breach of contract",
            "section_74": "Compensation for breach of contract where penalty stipulated for"
        }
    
    async def _get_indian_companies_act_sections(self) -> Dict[str, str]:
        """Get Indian Companies Act sections for caching."""
        return {
            "section_2": "Definitions",
            "section_180": "Powers of Board",
            "section_188": "Related party transactions",
            "section_297": "Loans to directors"
        }
    
    async def _get_gst_rates(self) -> Dict[str, float]:
        """Get GST rates for caching."""
        return {
            "standard": 18.0,
            "reduced": 5.0,
            "zero": 0.0,
            "exempt": 0.0
        }
    
    async def _get_stamp_duty_rates(self) -> Dict[str, Dict[str, float]]:
        """Get stamp duty rates by state for caching."""
        return {
            "Maharashtra": {"agreement": 0.1, "conveyance": 5.0},
            "Delhi": {"agreement": 0.05, "conveyance": 6.0},
            "Karnataka": {"agreement": 0.1, "conveyance": 5.0},
            "Tamil Nadu": {"agreement": 0.1, "conveyance": 7.0}
        }
    
    async def _get_ucc_articles(self) -> Dict[str, str]:
        """Get UCC articles for caching."""
        return {
            "article_1": "General Provisions",
            "article_2": "Sales",
            "article_3": "Negotiable Instruments",
            "article_9": "Secured Transactions"
        }
    
    async def _get_federal_regulations(self) -> Dict[str, str]:
        """Get federal regulations for caching."""
        return {
            "securities_act_1933": "Securities registration and disclosure",
            "securities_exchange_act_1934": "Securities trading and market regulation",
            "investment_company_act_1940": "Investment company regulation",
            "sarbanes_oxley_act": "Corporate accountability and transparency"
        }
    
    async def _get_state_law_variations(self) -> Dict[str, Dict[str, str]]:
        """Get state law variations for caching."""
        return {
            "California": {
                "privacy": "CCPA - California Consumer Privacy Act",
                "employment": "At-will employment with exceptions"
            },
            "New York": {
                "securities": "Martin Act - Blue sky laws",
                "employment": "At-will employment"
            },
            "Delaware": {
                "corporate": "Delaware General Corporation Law",
                "courts": "Court of Chancery for corporate disputes"
            }
        }
    
    async def _get_securities_regulations(self) -> Dict[str, str]:
        """Get securities regulations for caching."""
        return {
            "rule_10b5": "Employment of manipulative and deceptive practices",
            "rule_144": "Selling restricted and control securities",
            "regulation_d": "Rules governing the limited offer and sale of securities",
            "regulation_s": "Rules governing offers and sales made outside the United States"
        }
    
    async def warm_document_specific_cache(
        self,
        document_id: str,
        document_type: str,
        jurisdiction: str
    ) -> Dict[str, Any]:
        """Warm cache for a specific document context."""
        try:
            # Cache document-specific templates and references
            cache_keys = []
            
            # Document type specific templates
            template_key = f"document_template:{document_type}:{jurisdiction}"
            template_data = await self._get_document_template(document_type, jurisdiction)
            success = await cache_manager.set(template_key, template_data, ttl=3600)
            if success:
                cache_keys.append(template_key)
            
            # Jurisdiction-specific compliance requirements
            compliance_key = f"compliance_requirements:{jurisdiction}:{document_type}"
            compliance_data = await self._get_compliance_requirements(jurisdiction, document_type)
            success = await cache_manager.set(compliance_key, compliance_data, ttl=3600)
            if success:
                cache_keys.append(compliance_key)
            
            return {
                "document_id": document_id,
                "cached_keys": len(cache_keys),
                "keys": cache_keys
            }
            
        except Exception as e:
            logger.error(f"Failed to warm document-specific cache: {e}")
            return {"error": str(e)}
    
    async def _get_document_template(self, document_type: str, jurisdiction: str) -> Dict[str, Any]:
        """Get document-specific template data."""
        templates = {
            "contract": {
                "required_sections": ["parties", "consideration", "terms", "termination"],
                "optional_sections": ["warranties", "indemnification", "dispute_resolution"]
            },
            "agreement": {
                "required_sections": ["parties", "purpose", "obligations", "duration"],
                "optional_sections": ["confidentiality", "intellectual_property"]
            },
            "nda": {
                "required_sections": ["parties", "confidential_information", "obligations", "term"],
                "optional_sections": ["exceptions", "remedies"]
            }
        }
        
        base_template = templates.get(document_type, {})
        
        # Add jurisdiction-specific requirements
        if jurisdiction == "IN":
            base_template["jurisdiction_requirements"] = ["stamp_duty", "registration"]
        elif jurisdiction == "US":
            base_template["jurisdiction_requirements"] = ["governing_law", "jurisdiction_clause"]
        
        return base_template
    
    async def _get_compliance_requirements(self, jurisdiction: str, document_type: str) -> List[str]:
        """Get compliance requirements for jurisdiction and document type."""
        requirements = []
        
        if jurisdiction == "IN":
            requirements.extend([
                "Stamp duty payment",
                "Registration if required",
                "GST implications assessment"
            ])
            
            if document_type == "contract":
                requirements.extend([
                    "Indian Contract Act compliance",
                    "Specific Relief Act provisions"
                ])
        
        elif jurisdiction == "US":
            requirements.extend([
                "Governing law clause",
                "Jurisdiction and venue clause",
                "State law compliance"
            ])
            
            if document_type == "contract":
                requirements.extend([
                    "UCC applicability check",
                    "Federal regulations compliance"
                ])
        
        return requirements
    
    async def get_warming_status(self) -> Dict[str, Any]:
        """Get current cache warming status."""
        return {
            "is_warming": self.is_warming,
            "last_warming_time": self.last_warming_time.isoformat() if self.last_warming_time else None,
            "warming_stats": self.warming_stats
        }
    
    async def schedule_periodic_warming(self, interval_hours: int = 24):
        """Schedule periodic cache warming."""
        logger.info(f"Scheduling cache warming every {interval_hours} hours")
        
        while True:
            try:
                await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
                logger.info("Starting scheduled cache warming...")
                await self.warm_all_caches()
                
            except Exception as e:
                logger.error(f"Scheduled cache warming failed: {e}")


# Global cache warming service instance
cache_warming_service = CacheWarmingService()