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

from app.models.trace import TraceJob, TraceResult, ManualSearch, TraceJobStatus, TraceType, PropertyRecord
from app.models.user import User
from app.schemas.trace import TraceJobCreate, TraceJobUpdate, ManualSearchCreate
from app.core.exceptions import ValidationError, NotFoundError
from app.core.config import settings


class TraceService:
    def __init__(self, db: Session):
        self.db = db

    def create_trace_job(self, user_id: int, job_data: TraceJobCreate, file: UploadFile, column_mapping: Optional[Dict[str, str]] = None) -> TraceJob:
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

        # Parse CSV and count records
        try:
            csv_rows = self._parse_csv_file(file_path)
            record_count = len(csv_rows)
        except Exception as e:
            # Clean up file if parsing fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValidationError(f"Failed to process file: {str(e)}")

        if record_count == 0:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValidationError("CSV file is empty or has no data rows")

        # Create trace job
        trace_job = TraceJob(
            user_id=user_id,
            name=job_data.name,
            type=job_data.type,
            status=TraceJobStatus.PENDING,
            total_records=record_count,
            file_path=file_path,
            column_mapping=json.dumps(column_mapping) if column_mapping else None
        )

        self.db.add(trace_job)
        self.db.commit()
        self.db.refresh(trace_job)

        # Save individual CSV rows to database
        try:
            self._save_csv_rows_to_db(trace_job.id, csv_rows, column_mapping)
        except Exception as e:
            # Clean up job if row saving fails
            self.db.delete(trace_job)
            self.db.commit()
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValidationError(f"Failed to save CSV data: {str(e)}")

        # TODO: Start background processing for actual skip tracing
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

    def _parse_csv_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse CSV file and return list of rows"""
        if not file_path.endswith('.csv'):
            raise ValidationError("Only CSV files are supported")
        
        rows = []
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)
        return rows

    def _save_csv_rows_to_db(self, job_id: int, csv_rows: List[Dict[str, str]], column_mapping: Optional[Dict[str, str]] = None) -> None:
        """Save individual CSV rows to database as trace_results and property_records"""
        for row in csv_rows:
            # Apply column mapping if provided
            mapped_row = row
            if column_mapping:
                mapped_row = {}
                for target_field, source_column in column_mapping.items():
                    mapped_row[target_field] = row.get(source_column, '')
            
            # Create trace result entry
            trace_result = TraceResult(
                trace_job_id=job_id,
                input_record=json.dumps(mapped_row),  # Store mapped row as JSON
                status="pending",
                error_message=None
            )
            self.db.add(trace_result)
            self.db.flush()  # Get trace_result.id without committing

            # Extract and save property data if available
            address = mapped_row.get('address', mapped_row.get('Address', ''))
            city = mapped_row.get('city', mapped_row.get('City', ''))
            state = mapped_row.get('state', mapped_row.get('State', ''))
            zip_code = mapped_row.get('zipCode', mapped_row.get('Zip', mapped_row.get('zip', mapped_row.get('Zip Code', ''))))
            phone_number = mapped_row.get('phoneNumber', mapped_row.get('Phone', mapped_row.get('phone', '')))
            first_name = mapped_row.get('firstName', mapped_row.get('First Name', mapped_row.get('first_name', '')))
            last_name = mapped_row.get('lastName', mapped_row.get('Last Name', mapped_row.get('last_name', '')))
            mailing_address = mapped_row.get('mailingAddress', mapped_row.get('Mailing Address', ''))
            mailing_city = mapped_row.get('mailingCity', mapped_row.get('Mailing City', ''))
            mailing_state = mapped_row.get('mailingState', mapped_row.get('Mailing State', ''))
            
            # Only create property record if we have at least address
            if address or city or state:
                owner_name = f"{first_name} {last_name}".strip() if first_name or last_name else None

                property_record = PropertyRecord(
                    trace_result_id=trace_result.id,
                    property_address=address[:500] if address else '',
                    property_city=city[:100] if city else '',
                    property_state=state[:2] if state else '',
                    property_zip=zip_code[:10] if zip_code else '',
                    owner_name=owner_name[:255] if owner_name else None,
                    owner_address=mailing_address[:500] if mailing_address else None,
                    owner_city=mailing_city[:100] if mailing_city else None,
                    owner_state=mailing_state[:2] if mailing_state else None,
                    owner_zip=zip_code[:10] if zip_code else None
                )
                self.db.add(property_record)

        self.db.commit()

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
        """Generate results file for completed trace job with correct column order"""
        results = self.get_trace_job_results(trace_job.id, trace_job.user_id)
        
        # Generate unique filename
        unique_filename = f"trace_results_{trace_job.id}_{uuid.uuid4()}.csv"
        result_file_path = os.path.join(settings.UPLOAD_DIR, "results", unique_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        
        # Generate CSV file with correct column order: First Name, Last Name, Phone Number, Zip Code, Mailing Address
        with open(result_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'First Name',
                'Last Name',
                'Phone Number',
                'Zip Code',
                'Mailing Address'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                input_data = json.loads(result.input_record)
                output_data = json.loads(result.output_record) if result.output_record else {}
                
                # Extract data from input_record (mapped data)
                first_name = input_data.get('firstName', input_data.get('First Name', ''))
                last_name = input_data.get('lastName', input_data.get('Last Name', ''))
                phone_number = input_data.get('phoneNumber', input_data.get('Phone', ''))
                zip_code = input_data.get('zipCode', input_data.get('Zip Code', input_data.get('Zip', '')))
                mailing_address = input_data.get('mailingAddress', input_data.get('Mailing Address', ''))
                
                # If zip_code is not in mapped data, try to get it from address field
                if not zip_code:
                    # Try to extract zip from address if available
                    import re
                    address = input_data.get('address', input_data.get('Address', ''))
                    if address:
                        zip_match = re.search(r'\b\d{5}(-\d{4})?\b', address)
                        if zip_match:
                            zip_code = zip_match.group()
                
                # If output data exists, prefer it for phone numbers
                if output_data:
                    phone_numbers = output_data.get('phone_numbers', [])
                    if phone_numbers:
                        phone_number = ';'.join(phone_numbers) if isinstance(phone_numbers, list) else phone_numbers
                
                writer.writerow({
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Phone Number': phone_number,
                    'Zip Code': zip_code,
                    'Mailing Address': mailing_address
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
