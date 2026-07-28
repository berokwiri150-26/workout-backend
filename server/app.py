from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError

from models import db, Workout, Exercise, WorkoutExercise
from schemas import (
    WorkoutSchema, ExerciseSchema, WorkoutExerciseSchema,
    WorkoutWithExercisesSchema
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# Schema instances
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()
workout_with_exercises_schema = WorkoutWithExercisesSchema()

# Define Routes here
class WorkoutsResource(Resource):
    def get(self):
        """Get all workouts"""
        workouts = Workout.query.all()
        return make_response(workouts_schema.dump(workouts), 200)
    
    def post(self):
        """Create a new workout"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('date'):
                return make_response({"error": "Date is required"}, 400)
            if not data.get('duration_minutes'):
                return make_response({"error": "Duration minutes is required"}, 400)
            
            new_workout = Workout(
                date=data['date'],
                duration_minutes=data['duration_minutes'],
                notes=data.get('notes', '')
            )
            
            db.session.add(new_workout)
            db.session.commit()
            
            return make_response(workout_schema.dump(new_workout), 201)
        
        except IntegrityError as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

class WorkoutResource(Resource):
    def get(self, id):
        """Get a single workout with its exercises"""
        workout = Workout.query.get(id)
        if not workout:
            return make_response({"error": "Workout not found"}, 404)
        
        # Include reps/sets/duration data from WorkoutExercises
        return make_response(workout_with_exercises_schema.dump(workout), 200)
    
    def delete(self, id):
        """Delete a workout and its associated WorkoutExercises"""
        workout = Workout.query.get(id)
        if not workout:
            return make_response({"error": "Workout not found"}, 404)
        
        try:
            # Delete associated WorkoutExercises
            WorkoutExercise.query.filter_by(workout_id=id).delete()
            db.session.delete(workout)
            db.session.commit()
            
            return make_response({"message": "Workout deleted successfully"}, 200)
        
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

class ExercisesResource(Resource):
    def get(self):
        """Get all exercises"""
        exercises = Exercise.query.all()
        return make_response(exercises_schema.dump(exercises), 200)
    
    def post(self):
        """Create a new exercise"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('name'):
                return make_response({"error": "Name is required"}, 400)
            if not data.get('category'):
                return make_response({"error": "Category is required"}, 400)
            
            new_exercise = Exercise(
                name=data['name'],
                category=data['category'],
                equipment_needed=data.get('equipment_needed', False)
            )
            
            db.session.add(new_exercise)
            db.session.commit()
            
            return make_response(exercise_schema.dump(new_exercise), 201)
        
        except IntegrityError as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

class ExerciseResource(Resource):
    def get(self, id):
        """Get a single exercise with its workouts"""
        exercise = Exercise.query.get(id)
        if not exercise:
            return make_response({"error": "Exercise not found"}, 404)
        
        return make_response(exercise_schema.dump(exercise), 200)
    
    def delete(self, id):
        """Delete an exercise and its associated WorkoutExercises"""
        exercise = Exercise.query.get(id)
        if not exercise:
            return make_response({"error": "Exercise not found"}, 404)
        
        try:
            # Delete associated WorkoutExercises
            WorkoutExercise.query.filter_by(exercise_id=id).delete()
            db.session.delete(exercise)
            db.session.commit()
            
            return make_response({"message": "Exercise deleted successfully"}, 200)
        
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

class WorkoutExerciseResource(Resource):
    def post(self, workout_id, exercise_id):
        """Add an exercise to a workout with reps/sets/duration"""
        # Verify workout and exercise exist
        workout = Workout.query.get(workout_id)
        if not workout:
            return make_response({"error": "Workout not found"}, 404)
        
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return make_response({"error": "Exercise not found"}, 404)
        
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('reps') and not data.get('duration_seconds'):
                return make_response({"error": "Either reps or duration_seconds is required"}, 400)
            
            # Check if relationship already exists
            existing = WorkoutExercise.query.filter_by(
                workout_id=workout_id,
                exercise_id=exercise_id
            ).first()
            
            if existing:
                return make_response({"error": "This exercise is already added to the workout"}, 400)
            
            workout_exercise = WorkoutExercise(
                workout_id=workout_id,
                exercise_id=exercise_id,
                reps=data.get('reps'),
                sets=data.get('sets', 1),
                duration_seconds=data.get('duration_seconds')
            )
            
            db.session.add(workout_exercise)
            db.session.commit()
            
            return make_response(workout_exercise_schema.dump(workout_exercise), 201)
        
        except IntegrityError as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

# Register resources
api.add_resource(WorkoutsResource, '/workouts')
api.add_resource(WorkoutResource, '/workouts/<int:id>')
api.add_resource(ExercisesResource, '/exercises')
api.add_resource(ExerciseResource, '/exercises/<int:id>')
api.add_resource(WorkoutExerciseResource, '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises')

if __name__ == '__main__':
    app.run(port=5555, debug=True)