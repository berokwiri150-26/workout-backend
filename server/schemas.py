from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import Workout, Exercise, WorkoutExercise

class WorkoutExerciseSchema(SQLAlchemyAutoSchema):
    """Schema for WorkoutExercise model"""
    class Meta:
        model = WorkoutExercise
        include_fk = True
        load_instance = True
    
    # Schema validations
    @validates('reps')
    def validate_reps(self, value):
        """Validate reps is positive if provided"""
        if value is not None and value <= 0:
            raise ValidationError("Reps must be positive")
        return value
    
    @validates('sets')
    def validate_sets(self, value):
        """Validate sets is between 1 and 100"""
        if value is not None and (value < 1 or value > 100):
            raise ValidationError("Sets must be between 1 and 100")
        return value
    
    @validates('duration_seconds')
    def validate_duration(self, value):
        """Validate duration_seconds is positive if provided"""
        if value is not None and value <= 0:
            raise ValidationError("Duration seconds must be positive")
        return value

class ExerciseSchema(SQLAlchemyAutoSchema):
    """Schema for Exercise model"""
    class Meta:
        model = Exercise
        include_fk = True
        load_instance = True
    
    workouts = fields.Nested('WorkoutSchema', many=True, exclude=('exercises',))
    
    # Schema validations
    @validates('name')
    def validate_name(self, value):
        """Validate name length and content"""
        if not value or not value.strip():
            raise ValidationError("Exercise name cannot be empty")
        if len(value) < 3:
            raise ValidationError("Exercise name must be at least 3 characters long")
        if len(value) > 100:
            raise ValidationError("Exercise name cannot exceed 100 characters")
        return value
    
    @validates('category')
    def validate_category(self, value):
        """Validate category is valid"""
        valid_categories = ['cardio', 'strength', 'flexibility', 'balance']
        if value not in valid_categories:
            raise ValidationError(f"Category must be one of: {', '.join(valid_categories)}")
        return value

class WorkoutSchema(SQLAlchemyAutoSchema):
    """Schema for Workout model"""
    class Meta:
        model = Workout
        include_fk = True
        load_instance = True
    
    exercises = fields.Nested(ExerciseSchema, many=True, exclude=('workouts',))
    
    # Schema validations
    @validates('duration_minutes')
    def validate_duration(self, value):
        """Validate duration is between 1 and 1440 minutes"""
        if value < 1:
            raise ValidationError("Duration must be at least 1 minute")
        if value > 1440:
            raise ValidationError("Duration cannot exceed 1440 minutes (24 hours)")
        return value
    
    @validates('date')
    def validate_date(self, value):
        """Validate date is not in the future"""
        from datetime import datetime
        if value and value > datetime.now().date():
            raise ValidationError("Workout date cannot be in the future")
        return value

class WorkoutWithExercisesSchema(WorkoutSchema):
    """Schema for Workout with detailed exercise information"""
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True)
    
    class Meta(WorkoutSchema.Meta):
        fields = ('id', 'date', 'duration_minutes', 'notes', 'workout_exercises')