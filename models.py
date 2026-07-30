# models.py
from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="owner")  # owner | admin | worker
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    farms = db.relationship("Farm", backref="owner", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Farm(db.Model):
    __tablename__ = "farms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200))
    size_acres = db.Column(db.Float)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    crops = db.relationship("Crop", backref="farm", lazy=True, cascade="all, delete-orphan")
    livestock = db.relationship("Livestock", backref="farm", lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship("Expense", backref="farm", lazy=True, cascade="all, delete-orphan")
    income_records = db.relationship("Income", backref="farm", lazy=True, cascade="all, delete-orphan")
    inventory_items = db.relationship("Inventory", backref="farm", lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="farm", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        """Convert farm object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "size_acres": self.size_acres,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Crop(db.Model):
    __tablename__ = "crops"

    STAGES = ("planted", "growing", "flowering", "harvesting", "harvested")

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80))
    stage = db.Column(db.String(20), default="planted")
    planting_date = db.Column(db.Date)
    expected_harvest_date = db.Column(db.Date)
    actual_harvest_date = db.Column(db.Date)
    yield_amount = db.Column(db.Float)
    yield_unit = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert crop object to dictionary"""
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "name": self.name,
            "category": self.category,
            "stage": self.stage,
            "planting_date": self.planting_date.isoformat() if self.planting_date else None,
            "expected_harvest_date": self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            "actual_harvest_date": self.actual_harvest_date.isoformat() if self.actual_harvest_date else None,
            "yield_amount": self.yield_amount,
            "yield_unit": self.yield_unit,
            "notes": self.notes,
        }


class Livestock(db.Model):
    __tablename__ = "livestock"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)
    tag_number = db.Column(db.String(50))
    animal_type = db.Column(db.String(80), nullable=False)  # e.g. cattle, goat, poultry
    breed = db.Column(db.String(80))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    status = db.Column(db.String(20), default="active")  # active | sold | deceased
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    health_records = db.relationship(
        "HealthRecord", backref="animal", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert livestock object to dictionary"""
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "tag_number": self.tag_number,
            "animal_type": self.animal_type,
            "breed": self.breed,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender,
            "status": self.status,
            "notes": self.notes,
        }


class HealthRecord(db.Model):
    __tablename__ = "health_records"

    id = db.Column(db.Integer, primary_key=True)
    livestock_id = db.Column(db.Integer, db.ForeignKey("livestock.id"), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)  # vaccination | checkup | treatment
    description = db.Column(db.String(255))
    date_administered = db.Column(db.Date, nullable=False)
    next_due_date = db.Column(db.Date)
    veterinarian = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert health record object to dictionary"""
        return {
            "id": self.id,
            "livestock_id": self.livestock_id,
            "record_type": self.record_type,
            "description": self.description,
            "date_administered": self.date_administered.isoformat() if self.date_administered else None,
            "next_due_date": self.next_due_date.isoformat() if self.next_due_date else None,
            "veterinarian": self.veterinarian,
            "notes": self.notes,
        }


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)
    category = db.Column(db.String(80), nullable=False)  # seeds, fertilizer, labor, veterinary...
    description = db.Column(db.String(255))
    amount = db.Column(db.Float, nullable=False)
    date_incurred = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert expense object to dictionary"""
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "category": self.category,
            "description": self.description,
            "amount": self.amount,
            "date_incurred": self.date_incurred.isoformat() if self.date_incurred else None,
        }


class Income(db.Model):
    __tablename__ = "income"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)
    source = db.Column(db.String(80), nullable=False)  # crop_sale | livestock_sale | other
    description = db.Column(db.String(255))
    amount = db.Column(db.Float, nullable=False)
    date_received = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert income object to dictionary"""
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "source": self.source,
            "description": self.description,
            "amount": self.amount,
            "date_received": self.date_received.isoformat() if self.date_received else None,
        }


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)
    item_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80))  # seeds, fertilizer, feed, tools
    quantity = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20))
    reorder_level = db.Column(db.Float, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert inventory object to dictionary"""
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "item_name": self.item_name,
            "category": self.category,
            "quantity": self.quantity,
            "unit": self.unit,
            "reorder_level": self.reorder_level,
            "low_stock": (self.quantity or 0) <= (self.reorder_level or 0),
        }


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="pending")  # pending | in_progress | completed
    priority = db.Column(db.String(10), default="medium")  # low | medium | high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert task object to dictionary"""
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "priority": self.priority,
        }