"""
Health Records API Routes
This module handles all health record-related operations for livestock management.
Health records track medical treatments, vaccinations, checkups, and other health events for animals.
"""

# Import Flask tools for creating API routes and handling requests/responses
from flask import Blueprint, request, jsonify
# Import JWT decorator to protect routes that require authentication
from flask_jwt_extended import jwt_required

# Import database instance for interacting with the database
from extensions import db
# Import models for database tables: HealthRecord (medical records) and Livestock (animals)
from models import HealthRecord, Livestock
# Import helper functions for farm context and date parsing
from routes.helpers import get_current_farm, parse_date

# Create a Blueprint for health records routes
# This groups all health record-related endpoints together
# All routes will be prefixed with /api
health_bp = Blueprint("health_records", __name__, url_prefix="/api")


def _verify_animal_ownership(livestock_id):
    """
    Helper function to check if the current user owns a specific animal.
    
    This is a security check - it ensures users can only access health records
    for animals that belong to their farm. This prevents users from viewing
    or modifying data for animals they don't own.
    
    Parameters:
        livestock_id (int): The ID of the animal to check
        
    Returns:
        Livestock object if the animal exists and belongs to the user's farm
        None if the animal doesn't exist or user has no farm
        
    Note:
        The underscore (_) at the start of the function name indicates this is
        a private helper function meant only for internal use within this file.
    """
    # Get the current user's farm using the JWT token
    # The JWT token contains the user's identity, and get_current_farm()
    # looks up which farm belongs to that user
    farm = get_current_farm()
    
    # If user has no farm, they can't own any animals
    # This can happen if the user hasn't set up their farm profile yet
    if not farm:
        return None
    
    # Try to find the animal by ID and verify it belongs to the user's farm
    # filter_by() checks both conditions: the ID matches AND the farm_id matches
    # .first() returns the first matching record or None if no match found
    return Livestock.query.filter_by(id=livestock_id, farm_id=farm.id).first()


@health_bp.get("/livestock/<int:livestock_id>/health-records")
# This handles GET requests to URLs like: /api/livestock/5/health-records
# The <int:livestock_id> in the URL captures the animal ID as an integer
@jwt_required()  # User must be logged in (valid JWT token required)
def list_health_records(livestock_id):
    """
    Get all health records for a specific animal.
    
    This endpoint retrieves the complete medical history for a single animal,
    including all vaccinations, treatments, checkups, and other health events.
    
    URL example: GET /api/livestock/5/health-records
    
    Parameters:
        livestock_id (int): The ID of the animal (extracted from the URL)
        
    Returns:
        JSON response with:
        - 200 OK: List of health records (empty list if none exist)
        - 404 Not Found: If animal doesn't exist or doesn't belong to user
    """
    
    # First, verify the user owns this animal (security check)
    # This prevents users from accessing records for animals on other farms
    animal = _verify_animal_ownership(livestock_id)
    
    # If the animal doesn't exist or doesn't belong to the user, return 404 error
    # This is standard REST API practice - we don't reveal if the animal exists
    # or just doesn't belong to the user for security reasons
    if not animal:
        return jsonify({"error": "Livestock not found"}), 404
    
    # Query the database for all health records belonging to this animal
    # filter_by(livestock_id=animal.id) finds all records for this specific animal
    # order_by(...desc()) sorts with most recent first (newest dates at the top)
    records = HealthRecord.query.filter_by(livestock_id=animal.id).order_by(
        HealthRecord.date_administered.desc()
    ).all()  # .all() executes the query and returns all matching records as a list
    
    # Convert each record object to a dictionary using the model's to_dict() method
    # This transforms the database objects into JSON-serializable format
    # Return the list as a JSON response (empty list if no records found)
    return jsonify([r.to_dict() for r in records])


@health_bp.post("/livestock/<int:livestock_id>/health-records")
# This handles POST requests to URLs like: /api/livestock/5/health-records
@jwt_required()  # User must be logged in
def create_health_record(livestock_id):
    """
    Create a new health record for a specific animal.
    
    This endpoint adds a new health event (vaccination, treatment, etc.)
    to an animal's medical history.
    
    URL example: POST /api/livestock/5/health-records
    
    Expected JSON in request body:
    {
        "record_type": "vaccination",          # Required: Type of health event
        "date_administered": "2026-07-30",     # Required: Date in YYYY-MM-DD format
        "notes": "Annual rabies vaccination",  # Optional: Additional details
        "administered_by": "Dr. Smith"         # Optional: Who performed the procedure
    }
    
    Parameters:
        livestock_id (int): The ID of the animal (extracted from the URL)
        
    Returns:
        JSON response with:
        - 201 Created: Successfully created record with the record data
        - 400 Bad Request: Missing required fields
        - 404 Not Found: If animal doesn't exist or doesn't belong to user
        - 500 Internal Server Error: Database or other server error
    """
    
    try:
        # Verify the user owns this animal (security check)
        animal = _verify_animal_ownership(livestock_id)
        
        # If the animal doesn't exist or doesn't belong to the user, return 404 error
        if not animal:
            return jsonify({"error": "Livestock not found"}), 404

        # Get JSON data from the request body
        # request.get_json() parses the incoming JSON data
        # If no data is sent, use an empty dictionary to avoid errors
        data = request.get_json() or {}
        
        # Validate that required fields are provided
        # Both record_type and date_administered must be present
        # .get() returns None if the key doesn't exist, so we check for falsy values
        if not data.get("record_type"):
            return jsonify({"error": "record_type is required"}), 400
            
        if not data.get("date_administered"):
            return jsonify({"error": "date_administered is required"}), 400

        # Create a new HealthRecord object with the provided data
        # This doesn't save to the database yet - it just creates the Python object
        record = HealthRecord(
            livestock_id=animal.id,  # Link this record to the specific animal
            record_type=data.get("record_type"),  # e.g., "vaccination", "treatment", "checkup"
            date_administered=parse_date(data.get("date_administered")),  # Convert string to date object
            notes=data.get("notes"),  # Optional: any additional notes about the procedure
            administered_by=data.get("administered_by")  # Optional: who performed the procedure
        )
        
        # Add the new record to the database session
        # This stages the record for saving - it's in memory but not yet in the database
        db.session.add(record)
        
        # Commit the transaction to actually save the record to the database
        # This makes the change permanent - the record is now stored in the database
        db.session.commit()
        
        # Return the created record data to the client with a 201 Created status
        # 201 is the standard HTTP status code for successful creation
        # We use record.to_dict() to convert the database object to JSON format
        return jsonify(record.to_dict()), 201
        
    except Exception as e:
        # If ANY error occurs during the process, rollback the session
        # This undoes any changes made during this request (like the db.session.add)
        # This prevents partial data from being saved if something goes wrong
        db.session.rollback()
        
        # Return an error message with 500 Internal Server Error status
        # str(e) converts the exception to a readable error message
        # This helps with debugging but in production you might want to log the error instead
        return jsonify({"error": f"Failed to create health record: {str(e)}"}), 500


@health_bp.get("/livestock/<int:livestock_id>/health-records/latest")
# This handles GET requests to get only the most recent health record
@jwt_required()
def get_latest_health_record(livestock_id):
    """
    Get the most recent health record for a specific animal.
    
    This is a convenience endpoint to quickly check the latest health event
    without having to fetch all records.
    
    URL example: GET /api/livestock/5/health-records/latest
    
    Parameters:
        livestock_id (int): The ID of the animal
        
    Returns:
        JSON response with:
        - 200 OK: The most recent health record
        - 404 Not Found: If animal doesn't exist or has no records
    """
    
    try:
        # Verify the user owns this animal
        animal = _verify_animal_ownership(livestock_id)
        if not animal:
            return jsonify({"error": "Livestock not found"}), 404
        
        # Get the most recent record for this animal
        # .first() returns only the first record (newest due to desc() ordering)
        latest_record = HealthRecord.query.filter_by(
            livestock_id=animal.id
        ).order_by(
            HealthRecord.date_administered.desc()
        ).first()
        
        # If no records exist, return a helpful message
        if not latest_record:
            return jsonify({"message": "No health records found for this animal"}), 404
        
        # Return the latest record
        return jsonify(latest_record.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve latest record: {str(e)}"}), 500


@health_bp.delete("/health-records/<int:record_id>")
# This handles DELETE requests to URLs like: /api/health-records/12
@jwt_required()
def delete_health_record(record_id):
    """
    Delete a specific health record.
    
    This permanently removes a health record from the database.
    Users can only delete records for animals they own.
    
    URL example: DELETE /api/health-records/12
    
    Parameters:
        record_id (int): The ID of the health record to delete
        
    Returns:
        JSON response with:
        - 200 OK: Successfully deleted
        - 404 Not Found: If record doesn't exist or user doesn't own it
        - 500 Internal Server Error: If deletion fails
    """
    
    try:
        # First, find the record in the database
        record = HealthRecord.query.get(record_id)
        
        # If record doesn't exist, return 404
        if not record:
            return jsonify({"error": "Health record not found"}), 404
        
        # Verify the user owns the animal this record belongs to
        # This prevents users from deleting records for animals they don't own
        animal = _verify_animal_ownership(record.livestock_id)
        if not animal:
            return jsonify({"error": "You don't have permission to delete this record"}), 404
        
        # Delete the record from the session
        db.session.delete(record)
        
        # Commit the deletion to the database
        db.session.commit()
        
        # Return success message
        return jsonify({"message": "Health record deleted successfully"}), 200
        
    except Exception as e:
        # Rollback if something goes wrong
        db.session.rollback()
        return jsonify({"error": f"Failed to delete health record: {str(e)}"}), 500


@health_bp.put("/health-records/<int:record_id>")
# This handles PUT requests to update a record: /api/health-records/12
@jwt_required()
def update_health_record(record_id):
    """
    Update an existing health record.
    
    This allows updating any field of an existing health record.
    Users can only update records for animals they own.
    
    URL example: PUT /api/health-records/12
    
    Expected JSON in request body (all fields optional):
    {
        "record_type": "vaccination",
        "date_administered": "2026-07-30",
        "notes": "Updated notes",
        "administered_by": "Dr. Jones"
    }
    
    Parameters:
        record_id (int): The ID of the health record to update
        
    Returns:
        JSON response with:
        - 200 OK: Successfully updated with the updated record data
        - 404 Not Found: If record doesn't exist or user doesn't own it
        - 400 Bad Request: If invalid data is provided
        - 500 Internal Server Error: If update fails
    """
    
    try:
        # Find the record in the database
        record = HealthRecord.query.get(record_id)
        
        # If record doesn't exist, return 404
        if not record:
            return jsonify({"error": "Health record not found"}), 404
        
        # Verify the user owns the animal this record belongs to
        animal = _verify_animal_ownership(record.livestock_id)
        if not animal:
            return jsonify({"error": "You don't have permission to update this record"}), 404
        
        # Get the update data from the request
        data = request.get_json() or {}
        
        # Update only the fields that were provided
        # We check if each field exists in the data, and if so, update it
        if "record_type" in data:
            record.record_type = data["record_type"]
            
        if "date_administered" in data:
            # Parse the date string to a date object
            date = parse_date(data["date_administered"])
            if date:  # Only update if parsing was successful
                record.date_administered = date
            else:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
                
        if "notes" in data:
            record.notes = data["notes"]
            
        if "administered_by" in data:
            record.administered_by = data["administered_by"]
        
        # Commit the changes to the database
        db.session.commit()
        
        # Return the updated record
        return jsonify(record.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update health record: {str(e)}"}), 500