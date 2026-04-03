"""
DNC Registry Integration
Handles Federal DNC, State DNC, DMA, and TCPA Litigator database scrubbing
"""

import asyncio
import aiohttp
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime, timedelta
import logging

from app.core.config import settings
from app.core.exceptions import DNCServiceError


logger = logging.getLogger(__name__)


class DNCRegistry:
    """DNC Registry service integration"""
    
    def __init__(self):
        self.federal_dnc_url = settings.FEDERAL_DNC_API_URL
        self.state_dnc_url = settings.STATE_DNC_API_URL
        self.dma_url = settings.DMA_API_URL
        self.tcpa_url = settings.TCPA_LITIGATOR_API_URL
        self.api_keys = {
            'federal': settings.FEDERAL_DNC_API_KEY,
            'state': settings.STATE_DNC_API_KEY,
            'dma': settings.DMA_API_KEY,
            'tcpa': settings.TCPA_API_KEY
        }
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def scrub_phone_numbers(
        self,
        phone_numbers: List[str],
        scrub_federal: bool = True,
        scrub_state: bool = True,
        scrub_dma: bool = True,
        scrub_tcpa: bool = True
    ) -> Dict[str, Dict[str, bool]]:
        """
        Scrub phone numbers against DNC registries
        
        Returns:
            {
                "phone_number": {
                    "federal_dnc": bool,
                    "state_dnc": bool,
                    "dma": bool,
                    "tcpa_litigator": bool,
                    "clean": bool
                }
            }
        """
        results = {}
        
        # Process in batches to avoid rate limits
        batch_size = 100
        for i in range(0, len(phone_numbers), batch_size):
            batch = phone_numbers[i:i + batch_size]
            batch_results = await self._scrub_batch(
                batch, scrub_federal, scrub_state, scrub_dma, scrub_tcpa
            )
            results.update(batch_results)
            
            # Small delay between batches
            if i + batch_size < len(phone_numbers):
                await asyncio.sleep(0.1)
        
        return results
    
    async def _scrub_batch(
        self,
        phone_numbers: List[str],
        scrub_federal: bool,
        scrub_state: bool,
        scrub_dma: bool,
        scrub_tcpa: bool
    ) -> Dict[str, Dict[str, bool]]:
        """Scrub a batch of phone numbers"""
        results = {}
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = []
            
            for phone in phone_numbers:
                # Normalize phone number (remove formatting)
                normalized_phone = self._normalize_phone(phone)
                
                task = self._scrub_single_phone(
                    session, normalized_phone, scrub_federal, scrub_state, scrub_dma, scrub_tcpa
                )
                tasks.append((normalized_phone, task))
            
            # Execute all tasks concurrently
            for phone, task in tasks:
                try:
                    result = await task
                    results[phone] = result
                except Exception as e:
                    logger.error(f"Failed to scrub phone {phone}: {str(e)}")
                    results[phone] = {
                        "federal_dnc": False,
                        "state_dnc": False,
                        "dma": False,
                        "tcpa_litigator": False,
                        "clean": True,
                        "error": str(e)
                    }
        
        return results
    
    async def _scrub_single_phone(
        self,
        session: aiohttp.ClientSession,
        phone: str,
        scrub_federal: bool,
        scrub_state: bool,
        scrub_dma: bool,
        scrub_tcpa: bool
    ) -> Dict[str, bool]:
        """Scrub a single phone number against all registries"""
        result = {
            "federal_dnc": False,
            "state_dnc": False,
            "dma": False,
            "tcpa_litigator": False
        }
        
        # Run all checks concurrently
        tasks = []
        
        if scrub_federal and self.api_keys.get('federal'):
            tasks.append(self._check_federal_dnc(session, phone))
        
        if scrub_state and self.api_keys.get('state'):
            tasks.append(self._check_state_dnc(session, phone))
        
        if scrub_dma and self.api_keys.get('dma'):
            tasks.append(self._check_dma(session, phone))
        
        if scrub_tcpa and self.api_keys.get('tcpa'):
            tasks.append(self._check_tcpa_litigator(session, phone))
        
        # Execute checks
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results back
        for i, check_result in enumerate(check_results):
            if isinstance(check_result, Exception):
                logger.error(f"DNC check failed for {phone}: {str(check_result)}")
                continue
            
            if scrub_federal and self.api_keys.get('federal') and i == 0:
                result["federal_dnc"] = check_result
            elif scrub_state and self.api_keys.get('state') and i == 1:
                result["state_dnc"] = check_result
            elif scrub_dma and self.api_keys.get('dma') and i == 2:
                result["dma"] = check_result
            elif scrub_tcpa and self.api_keys.get('tcpa') and i == 3:
                result["tcpa_litigator"] = check_result
        
        # Determine if number is clean
        result["clean"] = not any([
            result["federal_dnc"],
            result["state_dnc"],
            result["dma"],
            result["tcpa_litigator"]
        ])
        
        return result
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to 10-digit format"""
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Remove country code if present
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        
        return digits
    
    async def _check_federal_dnc(self, session: aiohttp.ClientSession, phone: str) -> bool:
        """Check Federal DNC registry"""
        try:
            headers = {"Authorization": f"Bearer {self.api_keys['federal']}"}
            params = {"phone": phone}
            
            async with session.get(
                self.federal_dnc_url,
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("in_dnc", False)
                else:
                    raise DNCServiceError(f"Federal DNC API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Federal DNC check failed: {str(e)}")
            return False
    
    async def _check_state_dnc(self, session: aiohttp.ClientSession, phone: str) -> bool:
        """Check State DNC registry"""
        try:
            headers = {"Authorization": f"Bearer {self.api_keys['state']}"}
            params = {"phone": phone}
            
            async with session.get(
                self.state_dnc_url,
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("in_dnc", False)
                else:
                    raise DNCServiceError(f"State DNC API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"State DNC check failed: {str(e)}")
            return False
    
    async def _check_dma(self, session: aiohttp.ClientSession, phone: str) -> bool:
        """Check DMA registry"""
        try:
            headers = {"Authorization": f"Bearer {self.api_keys['dma']}"}
            params = {"phone": phone}
            
            async with session.get(
                self.dma_url,
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("in_dma", False)
                else:
                    raise DNCServiceError(f"DMA API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"DMA check failed: {str(e)}")
            return False
    
    async def _check_tcpa_litigator(self, session: aiohttp.ClientSession, phone: str) -> bool:
        """Check TCPA Litigator database"""
        try:
            headers = {"Authorization": f"Bearer {self.api_keys['tcpa']}"}
            params = {"phone": phone}
            
            async with session.get(
                self.tcpa_url,
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("is_litigator", False)
                else:
                    raise DNCServiceError(f"TCPA Litigator API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"TCPA Litigator check failed: {str(e)}")
            return False
    
    async def get_dnc_stats(self, date_range: int = 30) -> Dict[str, Any]:
        """Get DNC registry statistics"""
        # This would typically call admin APIs for each service
        # For now, return mock data
        return {
            "federal_dnc": {
                "total_numbers": 250000000,
                "last_updated": datetime.now().isoformat()
            },
            "state_dnc": {
                "total_numbers": 50000000,
                "states_covered": 50,
                "last_updated": datetime.now().isoformat()
            },
            "dma": {
                "total_numbers": 75000000,
                "last_updated": datetime.now().isoformat()
            },
            "tcpa_litigator": {
                "total_numbers": 150000,
                "last_updated": datetime.now().isoformat()
            }
        }


# Singleton instance
dnc_registry = DNCRegistry() if all([
    hasattr(settings, 'FEDERAL_DNC_API_URL'),
    hasattr(settings, 'STATE_DNC_API_URL'),
    hasattr(settings, 'DMA_API_URL'),
    hasattr(settings, 'TCPA_LITIGATOR_API_URL')
]) else None


class DNCScrubResult:
    """DNC scrub result processing"""
    
    @staticmethod
    def generate_summary(results: Dict[str, Dict[str, bool]]) -> Dict[str, Any]:
        """Generate summary of DNC scrub results"""
        total = len(results)
        federal_dnc_count = sum(1 for r in results.values() if r.get("federal_dnc"))
        state_dnc_count = sum(1 for r in results.values() if r.get("state_dnc"))
        dma_count = sum(1 for r in results.values() if r.get("dma"))
        tcpa_count = sum(1 for r in results.values() if r.get("tcpa_litigator"))
        clean_count = sum(1 for r in results.values() if r.get("clean"))
        
        return {
            "total_processed": total,
            "federal_dnc_violations": federal_dnc_count,
            "state_dnc_violations": state_dnc_count,
            "dma_violations": dma_count,
            "tcpa_litigator_violations": tcpa_count,
            "clean_numbers": clean_count,
            "violation_rate": round((total - clean_count) / total * 100, 2) if total > 0 else 0,
            "compliance_rate": round(clean_count / total * 100, 2) if total > 0 else 0
        }
    
    @staticmethod
    def filter_clean_numbers(results: Dict[str, Dict[str, bool]]) -> List[str]:
        """Get list of clean phone numbers"""
        return [phone for phone, result in results.items() if result.get("clean")]
    
    @staticmethod
    def filter_violations(results: Dict[str, Dict[str, bool]]) -> Dict[str, List[str]]:
        """Get violations grouped by type"""
        violations = {
            "federal_dnc": [],
            "state_dnc": [],
            "dma": [],
            "tcpa_litigator": []
        }
        
        for phone, result in results.items():
            for violation_type in violations.keys():
                if result.get(violation_type):
                    violations[violation_type].append(phone)
        
        return violations
