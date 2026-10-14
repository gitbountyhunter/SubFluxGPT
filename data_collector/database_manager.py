"""
Database manager for storing bug bounty data.
Handles PostgreSQL operations for programs, reports, domains, etc.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Numeric, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

from data_collector.collectors.base import Report, Program

logger = logging.getLogger(__name__)

Base = declarative_base()


class ProgramModel(Base):
    """SQLAlchemy model for programs table."""
    __tablename__ = 'programs'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)
    program_id = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reports = relationship("ReportModel", back_populates="program")


class ReportModel(Base):
    """SQLAlchemy model for reports table."""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey('programs.id', ondelete='CASCADE'))
    platform_report_id = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    weakness = Column(String(255))
    severity = Column(String(50))
    reporter = Column(String(255))
    bounty_amount = Column(Numeric(10, 2))
    disclosed_at = Column(DateTime)
    url = Column(Text)
    raw_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    program = relationship("ProgramModel", back_populates="reports")


class DomainModel(Base):
    """SQLAlchemy model for domains table."""
    __tablename__ = 'domains'
    
    id = Column(Integer, primary_key=True)
    domain = Column(String(255), unique=True, nullable=False)
    apex_domain = Column(String(255), nullable=False)
    tld = Column(String(50), nullable=False)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    report_count = Column(Integer, default=0)
    is_validated = Column(Boolean, default=False)
    validation_status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SubdomainModel(Base):
    """SQLAlchemy model for subdomains table."""
    __tablename__ = 'subdomains'
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey('domains.id', ondelete='CASCADE'))
    subdomain = Column(String(255), nullable=False)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    report_count = Column(Integer, default=0)
    is_validated = Column(Boolean, default=False)
    validation_status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseManager:
    """Manager for database operations."""
    
    def __init__(self, database_url: str):
        """
        Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        logger.info(f"Initialized DatabaseManager with URL: {database_url}")
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)
        logger.info("Created database tables")
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def upsert_program(self, program: Program) -> ProgramModel:
        """
        Insert or update a program.
        
        Args:
            program: Program object to upsert
            
        Returns:
            ProgramModel object
        """
        session = self.get_session()
        try:
            # Check if program exists
            existing = session.query(ProgramModel).filter_by(
                platform=program.platform,
                program_id=program.program_id
            ).first()
            
            if existing:
                # Update existing
                existing.name = program.name
                existing.url = program.url
                existing.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(existing)
                logger.debug(f"Updated program: {program.platform}/{program.program_id}")
                return existing
            else:
                # Insert new
                new_program = ProgramModel(
                    platform=program.platform,
                    program_id=program.program_id,
                    name=program.name,
                    url=program.url
                )
                session.add(new_program)
                session.commit()
                session.refresh(new_program)
                logger.debug(f"Inserted program: {program.platform}/{program.program_id}")
                return new_program
                
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to upsert program {program.program_id}: {e}")
            raise
        finally:
            session.close()
    
    def upsert_report(self, report: Report) -> Optional[ReportModel]:
        """
        Insert or update a report.
        
        Args:
            report: Report object to upsert
            
        Returns:
            ReportModel object or None if program doesn't exist
        """
        session = self.get_session()
        try:
            # Get or create program
            program = session.query(ProgramModel).filter_by(
                platform=report.platform,
                program_id=report.program_id
            ).first()
            
            if not program:
                # Program doesn't exist, create it
                program = ProgramModel(
                    platform=report.platform,
                    program_id=report.program_id,
                    name=report.program_name
                )
                session.add(program)
                session.flush()
            
            # Check if report exists
            existing = session.query(ReportModel).filter_by(
                platform=report.platform,
                platform_report_id=report.platform_report_id
            ).first()
            
            if existing:
                # Update existing
                existing.title = report.title
                existing.weakness = report.weakness
                existing.severity = report.severity
                existing.reporter = report.reporter
                existing.bounty_amount = report.bounty_amount
                existing.disclosed_at = report.disclosed_at
                existing.url = report.url
                existing.raw_content = report.raw_content
                existing.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(existing)
                logger.debug(f"Updated report: {report.platform_report_id}")
                return existing
            else:
                # Insert new
                new_report = ReportModel(
                    program_id=program.id,
                    platform_report_id=report.platform_report_id,
                    title=report.title,
                    weakness=report.weakness,
                    severity=report.severity,
                    reporter=report.reporter,
                    bounty_amount=report.bounty_amount,
                    disclosed_at=report.disclosed_at,
                    url=report.url,
                    raw_content=report.raw_content
                )
                session.add(new_report)
                session.commit()
                session.refresh(new_report)
                logger.debug(f"Inserted report: {report.platform_report_id}")
                return new_report
                
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to upsert report {report.platform_report_id}: {e}")
            raise
        finally:
            session.close()
    
    def upsert_domain(self, domain: str, apex_domain: str, tld: str) -> DomainModel:
        """
        Insert or update a domain.
        
        Args:
            domain: Domain string
            apex_domain: Apex domain
            tld: Top-level domain
            
        Returns:
            DomainModel object
        """
        session = self.get_session()
        try:
            existing = session.query(DomainModel).filter_by(domain=domain).first()
            
            if existing:
                existing.last_seen_at = datetime.utcnow()
                existing.report_count += 1
                existing.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(existing)
                return existing
            else:
                new_domain = DomainModel(
                    domain=domain,
                    apex_domain=apex_domain,
                    tld=tld
                )
                session.add(new_domain)
                session.commit()
                session.refresh(new_domain)
                return new_domain
                
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to upsert domain {domain}: {e}")
            raise
        finally:
            session.close()
    
    def get_report_count(self, platform: Optional[str] = None) -> int:
        """
        Get count of reports in database.
        
        Args:
            platform: Optional platform filter
            
        Returns:
            Number of reports
        """
        session = self.get_session()
        try:
            query = session.query(ReportModel)
            if platform:
                query = query.join(ProgramModel).filter(ProgramModel.platform == platform)
            return query.count()
        finally:
            session.close()
    
    def get_domain_count(self) -> int:
        """Get count of unique domains in database."""
        session = self.get_session()
        try:
            return session.query(DomainModel).count()
        finally:
            session.close()
    
    def get_reports_for_training(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get reports formatted for training.
        
        Args:
            limit: Maximum number of reports to return
            
        Returns:
            List of report dictionaries
        """
        session = self.get_session()
        try:
            query = session.query(ReportModel).filter(ReportModel.raw_content.isnot(None))
            
            if limit:
                query = query.limit(limit)
            
            reports = query.all()
            
            return [
                {
                    'id': r.id,
                    'platform': r.program.platform,
                    'program_name': r.program.name,
                    'title': r.title,
                    'weakness': r.weakness,
                    'raw_content': r.raw_content
                }
                for r in reports
            ]
        finally:
            session.close()
