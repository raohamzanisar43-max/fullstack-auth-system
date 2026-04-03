"""
Trace job service for Tracerfy Backend
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

from app.models.trace import TraceJob, TraceResult, ManualSearch, TraceJobStatus, TraceType
from app.models.user import User
from app.schemas.trace import TraceJobCreate, TraceJobUpdate, ManualSearchCreate
from app.core.exceptions import ValidationError, NotFoundError
from app.core.config import settings


class TraceService:
    def __init__(self, db: Session):
        self.db = db

    def create_trace_job(self, user_id: int, job_data: TraceJobCreate, file: UploadFile) -> TraceJob:
        """Create a new trace job with file upload"""
        
        # Validate file
        if not file.filename:
            raise ValidationError("No file provided")
        
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            raise ValidationError("Only CSV and Excel files are supported")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, "traces", unique_filename)
        
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
        
        # Create trace job
        trace_job = TraceJob(
            user_id=user_id,
            name=job_data.name,
            type=job_data.type,
            status=TraceJobStatus.PENDING,
            total_records=record_count,
            file_path=file_path
        )
        
        self.db.add(trace_job)
        self.db.commit()
        self.db.refresh(trace_job)
        
        # TODO: Start background processing
        # self._start_trace_processing(trace_job.id)
        
        return trace_job

    def get_user_trace_jobs(self, user_id: int, skip: int = 0, limit: int = 50) -> List[TraceJob]:
        """Get user's trace jobs"""
        return (
            self.db.query(TraceJob)
            .filter(TraceJob.user_id == user_id)
            .order_by(desc(TraceJob.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_trace_job(self, job_id: int, user_id: int) -> TraceJob:
        """Get specific trace job"""
        trace_job = (
            self.db.query(TraceJob)
            .filter(TraceJob.id == job_id, TraceJob.user_id == user_id)
            .first()
        )
        
        if not trace_job:
            raise NotFoundError("Trace job not found")
        
        return trace_job

    def update_trace_job(self, job_id: int, user_id: int, update_data: TraceJobUpdate) -> TraceJob:
        """Update trace job"""
        trace_job = self.get_trace_job(job_id, user_id)
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(trace_job, field, value)
        
        trace_job.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(trace_job)
        
        return trace_job

    def delete_trace_job(self, job_id: int, user_id: int) -> bool:
        """Delete trace job"""
        trace_job = self.get_trace_job(job_id, user_id)
        
        # Clean up files
        if trace_job.file_path and os.path.exists(trace_job.file_path):
            os.remove(trace_job.file_path)
        
        if trace_job.result_file_path and os.path.exists(trace_job.result_file_path):
            os.remove(trace_job.result_file_path)
        
        self.db.delete(trace_job)
        self.db.commit()
        
        return True

    def get_trace_job_results(self, job_id: int, user_id: int) -> List[TraceResult]:
        """Get trace job results"""
        trace_job = self.get_trace_job(job_id, user_id)
        
        return (
            self.db.query(TraceResult)
            .filter(TraceResult.trace_job_id == job_id)
            .order_by(TraceResult.created_at)
            .all()
        )

    def download_trace_results(self, job_id: int, user_id: int) -> str:
        """Generate and return path to results file"""
        trace_job = self.get_trace_job(job_id, user_id)
        
        if trace_job.status != TraceJobStatus.COMPLETED:
            raise ValidationError("Trace job is not completed")
        
        if not trace_job.result_file_path:
            # Generate results file
            result_file_path = self._generate_results_file(trace_job)
            trace_job.result_file_path = result_file_path
            self.db.commit()
        
        return trace_job.result_file_path

    def create_manual_search(self, user_id: int, search_data: ManualSearchCreate) -> ManualSearch:
        """Create a manual search"""
        
        # Calculate credits needed
        credits_needed = 3 if search_data.search_type == "enhanced" else 1
        
        # TODO: Check user's credit balance
        # credit_service = CreditService(self.db)
        # credit_service.deduct_credits(user_id, credits_needed)
        
        manual_search = ManualSearch(
            user_id=user_id,
            search_type=search_data.search_type,
            search_query=search_data.search_query,
            credits_used=credits_needed,
            status=TraceJobStatus.PENDING
        )
        
        self.db.add(manual_search)
        self.db.commit()
        self.db.refresh(manual_search)
        
        # TODO: Start background processing
        # self._start_manual_search_processing(manual_search.id)
        
        return manual_search

    def get_user_manual_searches(self, user_id: int, skip: int = 0, limit: int = 50) -> List[ManualSearch]:
        """Get user's manual searches"""
        return (
            self.db.query(ManualSearch)
            .filter(ManualSearch.user_id == user_id)
            .order_by(desc(ManualSearch.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_manual_search(self, search_id: int, user_id: int) -> ManualSearch:
        """Get specific manual search"""
        manual_search = (
            self.db.query(ManualSearch)
            .filter(ManualSearch.id == search_id, ManualSearch.user_id == user_id)
            .first()
        )
        
        if not manual_search:
            raise NotFoundError("Manual search not found")
        
        return manual_search

    def _count_records_in_file(self, file_path: str) -> int:
        """Count records in uploaded file"""
        if file_path.endswith('.csv'):
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                return sum(1 for row in reader) - 1  # Subtract header row
        else:
            # TODO: Implement Excel file counting
            raise ValidationError("Excel file support not yet implemented")

    def _generate_results_file(self, trace_job: TraceJob) -> str:
        """Generate results file for completed trace job"""
        results = self.get_trace_job_results(trace_job.id, trace_job.user_id)
        
        # Generate unique filename
        unique_filename = f"trace_results_{trace_job.id}_{uuid.uuid4()}.csv"
        result_file_path = os.path.join(settings.UPLOAD_DIR, "results", unique_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        
        # Generate CSV file
        with open(result_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'input_address', 'input_city', 'input_state', 'input_zip',
                'owner_name', 'owner_address', 'owner_city', 'owner_state', 'owner_zip',
                'phone_numbers', 'email_addresses', 'property_value', 'status', 'error_message'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                input_data = json.loads(result.input_record)
                output_data = json.loads(result.output_record) if result.output_record else {}
                
                writer.writerow({
                    'input_address': input_data.get('address', ''),
                    'input_city': input_data.get('city', ''),
                    'input_state': input_data.get('state', ''),
                    'input_zip': input_data.get('zip', ''),
                    'owner_name': output_data.get('owner_name', ''),
                    'owner_address': output_data.get('owner_address', ''),
                    'owner_city': output_data.get('owner_city', ''),
                    'owner_state': output_data.get('owner_state', ''),
                    'owner_zip': output_data.get('owner_zip', ''),
                    'phone_numbers': ';'.join(output_data.get('phone_numbers', [])),
                    'email_addresses': ';'.join(output_data.get('email_addresses', [])),
                    'property_value': output_data.get('property_value', ''),
                    'status': result.status,
                    'error_message': result.error_message or ''
                })
        
        return result_file_path

    def _start_trace_processing(self, job_id: int):
        """Start background processing for trace job"""
        # TODO: Implement background processing with Celery or similar
        pass

    def _start_manual_search_processing(self, search_id: int):
        """Start background processing for manual search"""
        # TODO: Implement background processing with Celery or similar
        pass
