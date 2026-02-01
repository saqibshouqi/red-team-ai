"""
Database models for experiments
"""
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class ExperimentStatusEnum(str, enum.Enum):
    """Experiment status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Experiment(Base):
    """Experiment table"""
    __tablename__ = "experiments"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ExperimentStatusEnum), default=ExperimentStatusEnum.PENDING)
    
    # Configuration (stored as JSON)
    config = Column(JSON)
    
    # Results
    conversation = Column(JSON, nullable=True)
    scores = Column(JSON, nullable=True)
    
    # Timing
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation_turns = relationship("ConversationTurnModel", back_populates="experiment", cascade="all, delete-orphan")
    score = relationship("Score", back_populates="experiment", uselist=False, cascade="all, delete-orphan")


class ConversationTurnModel(Base):
    """Conversation turn table"""
    __tablename__ = "conversation_turns"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    experiment_id = Column(String, ForeignKey("experiments.id"), index=True)
    turn_number = Column(Integer)
    interrogator_message = Column(Text)
    target_response = Column(Text)
    interrogator_strategy = Column(String)
    response_time_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    experiment = relationship("Experiment", back_populates="conversation_turns")


class Score(Base):
    """Scores table"""
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    experiment_id = Column(String, ForeignKey("experiments.id"), unique=True, index=True)
    
    # Scores
    role_fidelity_score = Column(Float)
    drift_index = Column(Float)
    ethical_deviation_score = Column(Float)
    consistency_score = Column(Float)
    overall_score = Column(Float)
    
    # Analysis
    detailed_analysis = Column(Text, nullable=True)
    turn_by_turn_scores = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    experiment = relationship("Experiment", back_populates="score")