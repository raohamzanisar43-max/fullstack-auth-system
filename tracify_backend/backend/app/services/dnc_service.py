"""
DNC scrubbing service for Tracerfy Backend
"""

import json
import csv
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import UploadFile, HTTPException

from app.models.dnc import DncScrubJob, DncScrubResult, DncRecord, DncScrubStatus
from app.models.user import User
from app.schemas.dnc import DncScrubCreate, DncScrubUpdate
from app.core.exceptions import ValidationError, NotFoundError
from app.core.config import settings


class DncService:
    def __init__(self, db: Session):
        self.db = db

    def create_dnc_scrub(self, user_id: int, scrub_data: DncScrubCreate, file: UploadFile) -> DncScrubJob:
        """Create a new DNC scrub job with file upload"""
        
        # Validate file
        if not file.filename:
            raise ValidationError("No file provided")
        
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            raise ValidationError("Only CSV and Excel files are supported")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, "dnc", unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
        except Exception as e:
            raise ValidationError(f"Failed to save file: {str(e)}")
        
        # Count records in file
        try:
            record_count = self._count_records_in_file(file_path)
        except Exception as e:
            # Clean up file if counting fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValidationError(f"Failed to process file: {str(e)}")
        
        # Calculate credits needed (1 credit per record)
        credits_needed = record_count
        
        # TODO: Check user's credit balance
        # credit_service = CreditService(self.db)
        # credit_service.deduct_credits(user_id, credits_needed)
        
        # Create DNC scrub job
        dnc_scrub = DncScrubJob(
            user_id=user_id,
            name=scrub_data.name,
            status=DncScrubStatus.PENDING,
            total_records=record_count,
            credits_used=credits_needed,
            file_path=file_path
        )
        
        self.db.add(dnc_scrub)
        self.db.commit()
        self.db.refresh(dnc_scrub)
        
        # TODO: Start background processing
        # self._start_dnc_processing(dnc_scrub.id)
        
        return dnc_scrub

    def get_user_dnc_scrubs(self, user_id: int, skip: int = 0, limit: int = 50) -> List[DncScrubJob]:
        """Get user's DNC scrub jobs"""
        return (
            self.db.query(DncScrubJob)
            .filter(DncScrubJob.user_id == user_id)
            .order_by(desc(DncScrubJob.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_dnc_scrub(self, scrub_id: int, user_id: int) -> DncScrubJob:
        """Get specific DNC scrub job"""
        dnc_scrub = (
            self.db.query(DncScrubJob)
            .filter(DncScrubJob.id == scrub_id, DncScrubJob.user_id == user_id)
            .first()
        )
        
        if not dnc_scrub:
            raise NotFoundError("DNC scrub job not found")
        
        return dnc_scrub

    def update_dnc_scrub(self, scrub_id: int, user_id: int, update_data: DncScrubUpdate) -> DncScrubJob:
        """Update DNC scrub job"""
        dnc_scrub = self.get_dnc_scrub(scrub_id, user_id)
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(dnc_scrub, field, value)
        
        dnc_scrub.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(dnc_scrub)
        
        return dnc_scrub

    def delete_dnc_scrub(self, scrub_id: int, user_id: int) -> bool:
        """Delete DNC scrub job"""
        dnc_scrub = self.get_dnc_scrub(scrub_id, user_id)
        
        # Clean up files
        if dnc_scrub.file_path and os.path.exists(dnc_scrub.file_path):
            os.remove(dnc_scrub.file_path)
        
        if dnc_scrub.result_file_path and os.path.exists(dnc_scrub.result_file_path):
            os.remove(dnc_scrub.result_file_path)
        
        self.db.delete(dnc_scrub)
        self.db.commit()
        
        return True

    def get_dnc_scrub_results(self, scrub_id: int, user_id: int) -> List[DncScrubResult]:
        """Get DNC scrub job results"""
        dnc_scrub = self.get_dnc_scrub(scrub_id, user_id)
        
        return (
            self.db.query(DncScrubResult)
            .filter(DncScrubResult.scrub_job_id == scrub_id)
            .order_by(DncScrubResult.created_at)
            .all()
        )

    def download_dnc_results(self, scrub_id: int, user_id: int) -> str:
        """Generate and return path to results file"""
        dnc_scrub = self.get_dnc_scrub(scrub_id, user_id)
        
        if dnc_scrub.status != DncScrubStatus.COMPLETED:
            raise ValidationError("DNC scrub job is not completed")
        
        if not dnc_scrub.result_file_path:
            # Generate results file
            result_file_path = self._generate_results_file(dnc_scrub)
            dnc_scrub.result_file_path = result_file_path
            self.db.commit()
        
        return dnc_scrub.result_file_path

    def check_phone_numbers(self, phone_numbers: List[str]) -> Dict[str, Any]:
        """Check if phone numbers are on DNC lists"""
        
        results = []
        
        for phone_number in phone_numbers:
            # Normalize phone number
            normalized_phone = self._normalize_phone_number(phone_number)
            
            # Check against DNC database
            dnc_record = (
                self.db.query(DncRecord)
                .filter(DncRecord.phone_number == normalized_phone)
                .first()
            )
            
            is_dnc = dnc_record.is_dnc if dnc_record else False
            
            results.append({
                "input_phone": phone_number,
                "normalized_phone": normalized_phone,
                "is_dnc": is_dnc,
                "dnc_type": dnc_record.dnc_type if dnc_record else None,
                "dnc_source": dnc_record.dnc_source if dnc_record else None
            })
        
        return {
            "results": results,
            "total_checked": len(phone_numbers),
            "dnc_count": sum(1 for r in results if r["is_dnc"]),
            "clean_count": sum(1 for r in results if not r["is_dnc"])
        }

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get DNC registry statistics"""
        
        # Get counts from database
        federal_count = (
            self.db.query(DncRecord)
            .filter(DncRecord.dnc_type == "federal")
            .count()
        )
        
        state_count = (
            self.db.query(DncRecord)
            .filter(DncRecord.dnc_type == "state")
            .count()
        )
        
        dma_count = (
            self.db.query(DncRecord)
            .filter(DncRecord.dnc_type == "dma")
            .count()
        )
        
        tcpa_count = (
            self.db.query(DncRecord)
            .filter(DncRecord.dnc_type == "tcpa_litigator")
            .count()
        )
        
        total_count = (
            self.db.query(DncRecord)
            .filter(DncRecord.is_dnc == True)
            .count()
        )
        
        return {
            "federal_dnc_count": federal_count,
            "state_dnc_count": state_count,
            "dma_count": dma_count,
            "tcpa_litigator_count": tcpa_count,
            "total_records": total_count,
            "last_updated": datetime.utcnow()
        }

    def _count_records_in_file(self, file_path: str) -> int:
        """Count records in uploaded file"""
        if file_path.endswith('.csv'):
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                return sum(1 for row in reader) - 1  # Subtract header row
        else:
            # TODO: Implement Excel file counting
            raise ValidationError("Excel file support not yet implemented")

    def _generate_results_file(self, dnc_scrub: DncScrubJob) -> str:
        """Generate results file for completed DNC scrub job"""
        results = self.get_dnc_scrub_results(dnc_scrub.id, dnc_scrub.user_id)
        
        # Generate unique filename
        unique_filename = f"dnc_results_{dnc_scrub.id}_{uuid.uuid4()}.csv"
        result_file_path = os.path.join(settings.UPLOAD_DIR, "results", unique_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        
        # Generate CSV file
        with open(result_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'input_phone', 'normalized_phone', 'is_dnc', 'dnc_type', 
                'dnc_source', 'first_seen_date', 'last_seen_date', 'status', 'error_message'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                input_data = json.loads(result.input_record)
                output_data = json.loads(result.output_record) if result.output_record else {}
                
                writer.writerow({
                    'input_phone': input_data.get('phone', ''),
                    'normalized_phone': output_data.get('normalized_phone', ''),
                    'is_dnc': output_data.get('is_dnc', ''),
                    'dnc_type': output_data.get('dnc_type', ''),
                    'dnc_source': output_data.get('dnc_source', ''),
                    'first_seen_date': output_data.get('first_seen_date', ''),
                    'last_seen_date': output_data.get('last_seen_date', ''),
                    'status': result.status,
                    'error_message': result.error_message or ''
                })
        
        return result_file_path

    def _normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number to standard format"""
        # Remove all non-numeric characters
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Remove leading 1 if it's a US number
        if len(digits_only) == 11 and digits_only.startswith('1'):
            digits_only = digits_only[1:]
        
        # Return 10-digit number
        return digits_only[-10:] if len(digits_only) >= 10 else digits_only

    def _start_dnc_processing(self, scrub_id: int):
        """Start background processing for DNC scrub job"""
        # TODO: Implement background processing with Celery or similar
        pass

    def _check_single_phone(self, phone_number: str) -> Dict[str, Any]:
        """Check a single phone number against DNC lists"""
        normalized_phone = self._normalize_phone_number(phone_number)
        
        # Check against DNC database
        dnc_record = (
            self.db.query(DncRecord)
            .filter(DncRecord.phone_number == normalized_phone)
            .first()
        )
        
        is_dnc = dnc_record.is_dnc if dnc_record else False
        
        return {
            "input_phone": phone_number,
            "normalized_phone": normalized_phone,
            "is_dnc": is_dnc,
            "dnc_type": dnc_record.dnc_type if dnc_record else None,
            "dnc_source": dnc_record.dnc_source if dnc_record else None,
            "first_seen_date": dnc_record.first_seen_date.isoformat() if dnc_record and dnc_record.first_seen_date else None,
            "last_seen_date": dnc_record.last_seen_date.isoformat() if dnc_record and dnc_record.last_seen_date else None
        }
