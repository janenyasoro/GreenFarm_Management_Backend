# Import Flask tools for creating API routes and handling requests/responses
from flask import Blueprint, request, jsonify
# Import JWT decorator to protect routes that require authentication
from flask_jwt_extended import jwt_required

# Import database instance for interacting with the database
from extensions import db
# Import the Livestock model which represents the animals table in database
from models import Livestock
# Import helper functions for farm context and date parsing
from routes.helpers import get_current_farm, parse_date

# Create a Blueprint for livestock routes
# This groups all livestock-related endpoints together
# All routes will be prefixed with /api/livestock
livestock_bp = Blueprint("livestock", __name__, url_prefix="/api/livestock")


@livestock_bp.get("")  # This handles GET requests to /api/livestock
@jwt_required()        # This route requires a valid JWT token (user must be logged in)
def list_livestock():
    """Get a list of all livestock belonging to the current user's farm"""
    
    # Get the farm associated with the currently logged-in user
    # This uses the JWT token to identify the user
    farm = get_current_farm()
    
    # If user has no farm, return an empty list instead of error
    if not farm:
        return jsonify([])
    
    # Query the database for all animals belonging to this farm
    # Sort them with newest first (descending order by created_at)
    animals = Livestock.query.filter_by(farm_id=farm.id).order_by(Livestock.created_at.desc()).all()
    
    # Convert each animal object to a dictionary (using the to_dict() method from the model)
    # and return as JSON response
    return jsonify([a.to_dict() for a in animals])


@livestock_bp.post("")  # This handles POST requests to /api/livestock
@jwt_required()         # User must be logged in to create livestock
def create_livestock():
    """Add a new animal to the current user's farm"""
    
    # Get the user's farm
    farm = get_current_farm()
    
    # If user has no farm, they can't add livestock
    if not farm:
        return jsonify({"error": "No farm found for this user"}), 404

    # Get JSON data from the request body (what the client sent)
    # If no data, use an empty dictionary
    data = request.get_json() or {}
    
    # Validate that animal_type is provided (required field)
    if not data.get("animal_type"):
        return jsonify({"error": "animal_type is required"}), 400

    # Create a new Livestock object with the provided data
    # The parse_date() helper handles converting string dates to date objects
    animal = Livestock(
        farm_id=farm.id,                    # Link this animal to the user's farm
        tag_number=data.get("tag_number"),  # Optional: unique identifier tag
        animal_type=data["animal_type"],    # Required: e.g., "cow", "pig", "sheep"
        breed=data.get("breed"),            # Optional: breed name
        birth_date=parse_date(data.get("birth_date")),  # Optional: convert string to date
        gender=data.get("gender"),          # Optional: "male" or "female"
        status=data.get("status", "active"), # Default to "active" if not provided
        notes=data.get("notes"),            # Optional: any additional notes
    )
    
    # Add the new animal to the database session (staging for saving)
    db.session.add(animal)
    # Commit the transaction to save to the database
    db.session.commit()
    
    # Return the created animal data with 201 Created status
    return jsonify(animal.to_dict()), 201