"""
Database models for GreenHarvest Farm Management System.
Converted from Django models to Flask-SQLAlchemy models.
"""
from datetime import datetime
from extensions import db, bcrypt


class User(db.Model):
    """
    Custom User model for GreenHarvest Farm Management System.
    Converted from Django AbstractUser to Flask-SQLAlchemy model.
    """
    __tablename__ = 'users'

    # Role choices
    class Role:
        ADMIN = 'admin'
        OWNER = 'owner'
        WORKER = 'worker'

    ROLES = [
        (Role.ADMIN, 'Admin'),
        (Role.OWNER, 'Farm Owner'),
        (Role.WORKER, 'Farm Worker'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(20), default=Role.OWNER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_staff = db.Column(db.Boolean, default=False, nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    farms = db.relationship('Farm', backref='owner', lazy=True)
    # Note: Other relationships are through farms, not direct

    def set_password(self, password):
        """Set the user's password using bcrypt hashing."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def is_admin(self):
        """Check if user is an admin."""
        return self.role == self.Role.ADMIN

    def is_owner(self):
        """Check if user is a farm owner."""
        return self.role == self.Role.OWNER

    def is_worker(self):
        """Check if user is a farm worker."""
        return self.role == self.Role.WORKER

    def to_dict(self, include_sensitive=False):
        """Convert user object to dictionary for JSON serialization."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'profile_image': self.profile_image,
            'role': self.role,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'date_joined': self.date_joined.isoformat() + 'Z' if self.date_joined else None,
            'last_login': self.last_login.isoformat() + 'Z' if self.last_login else None,
        }
        return data

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Farm(db.Model):
    """Farm model for farm management."""
    __tablename__ = 'farms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships removed - these were causing foreign key issues

    def to_dict(self):
        """Convert farm object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


class Livestock(db.Model):
    """Livestock model for animal tracking."""
    __tablename__ = 'livestock'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    tag_number = db.Column(db.String(50), nullable=True)
    animal_type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    health_records = db.relationship('HealthRecord', backref='livestock', lazy=True)

    def to_dict(self):
        """Convert livestock object to dictionary."""
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'tag_number': self.tag_number,
            'animal_type': self.animal_type,
            'breed': self.breed,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'gender': self.gender,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


class Expense(db.Model):
    """Expense model for tracking farm expenses."""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date_incurred = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships removed - these were causing foreign key issues

    def to_dict(self):
        """Convert expense object to dictionary."""
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'category': self.category,
            'description': self.description,
            'amount': float(self.amount),
            'date_incurred': self.date_incurred.isoformat() if self.date_incurred else None,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


class Income(db.Model):
    """Income model for tracking farm income."""
    __tablename__ = 'income'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date_received = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships removed - these were causing foreign key issues

    def to_dict(self):
        """Convert income object to dictionary."""
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'source': self.source,
            'description': self.description,
            'amount': float(self.amount),
            'date_received': self.date_received.isoformat() if self.date_received else None,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


class Inventory(db.Model):
    """Inventory model for tracking farm inventory items."""
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    unit = db.Column(db.String(20), nullable=True)
    reorder_level = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships removed - these were causing foreign key issues

    def to_dict(self):
        """Convert inventory object to dictionary."""
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'item_name': self.item_name,
            'category': self.category,
            'quantity': self.quantity,
            'unit': self.unit,
            'reorder_level': self.reorder_level,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


class HealthRecord(db.Model):
    """Health record model for tracking animal health events."""
    __tablename__ = 'health_records'

    id = db.Column(db.Integer, primary_key=True)
    livestock_id = db.Column(db.Integer, db.ForeignKey('livestock.id'), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)
    date_administered = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    administered_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships removed - these were causing foreign key issues

    def to_dict(self):
        """Convert health record object to dictionary."""
        return {
            'id': self.id,
            'livestock_id': self.livestock_id,
            'record_type': self.record_type,
            'date_administered': self.date_administered.isoformat() if self.date_administered else None,
            'notes': self.notes,
            'administered_by': self.administered_by,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }
