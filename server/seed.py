#!/usr/bin/env python3

from app import app
from models import db, Workout, Exercise, WorkoutExercise
from datetime import date, timedelta
from random import randint, choice

def seed_database():
    """Seed the database with sample data"""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.session.query(WorkoutExercise).delete()
        db.session.query(Workout).delete()
        db.session.query(Exercise).delete()
        db.session.commit()
        
        # Create exercises
        print("Creating exercises...")
        exercises = [
            Exercise(name="Push-ups", category="strength", equipment_needed=False),
            Exercise(name="Squats", category="strength", equipment_needed=False),
            Exercise(name="Running", category="cardio", equipment_needed=False),
            Exercise(name="Plank", category="strength", equipment_needed=False),
            Exercise(name="Yoga", category="flexibility", equipment_needed=False),
            Exercise(name="Dumbbell Curls", category="strength", equipment_needed=True),
            Exercise(name="Cycling", category="cardio", equipment_needed=True),
            Exercise(name="Stretching", category="flexibility", equipment_needed=False),
            Exercise(name="Balance Board", category="balance", equipment_needed=True),
            Exercise(name="Jumping Jacks", category="cardio", equipment_needed=False),
        ]
        
        for exercise in exercises:
            db.session.add(exercise)
        db.session.commit()
        
        # Create workouts
        print("Creating workouts...")
        workouts = [
            Workout(date=date.today() - timedelta(days=randint(0, 30)), 
                   duration_minutes=randint(20, 90),
                   notes="Great workout!"),
            Workout(date=date.today() - timedelta(days=randint(0, 30)), 
                   duration_minutes=randint(15, 60),
                   notes="Focused on upper body"),
            Workout(date=date.today() - timedelta(days=randint(0, 30)), 
                   duration_minutes=randint(30, 120),
                   notes="Full body session"),
            Workout(date=date.today() - timedelta(days=randint(0, 30)), 
                   duration_minutes=randint(25, 45),
                   notes="Quick cardio workout"),
            Workout(date=date.today() - timedelta(days=randint(0, 30)), 
                   duration_minutes=randint(45, 90),
                   notes="Strength training day"),
        ]
        
        for workout in workouts:
            db.session.add(workout)
        db.session.commit()
        
        # Create WorkoutExercise associations
        print("Creating workout-exercise associations...")
        for workout in workouts:
            # Each workout gets 2-5 exercises
            num_exercises = randint(2, 5)
            selected_exercises = choice([exercises, exercises[:5], exercises[3:8], exercises[2:7]])
            
            for exercise in selected_exercises[:num_exercises]:
                # Randomly decide if it's reps-based or duration-based
                is_reps_based = choice([True, False])
                
                if is_reps_based:
                    workout_exercise = WorkoutExercise(
                        workout=workout,
                        exercise=exercise,
                        reps=randint(8, 20),
                        sets=randint(3, 5),
                        duration_seconds=None
                    )
                else:
                    workout_exercise = WorkoutExercise(
                        workout=workout,
                        exercise=exercise,
                        reps=None,
                        sets=1,
                        duration_seconds=randint(30, 300)  # 30 seconds to 5 minutes
                    )
                
                db.session.add(workout_exercise)
        
        db.session.commit()
        print("Database seeded successfully!")
        
        # Verify relationships
        print("\nVerifying relationships:")
        print(f"Total workouts: {Workout.query.count()}")
        print(f"Total exercises: {Exercise.query.count()}")
        print(f"Total workout-exercise associations: {WorkoutExercise.query.count()}")
        
        # Test validations
        print("\nTesting validations...")
        try:
            invalid_workout = Workout(date=date.today() + timedelta(days=1), duration_minutes=-5)
            db.session.add(invalid_workout)
            db.session.commit()
        except Exception as e:
            print(f"✓ Validation caught: {e}")
            db.session.rollback()
        
        try:
            invalid_exercise = Exercise(name="A", category="invalid")
            db.session.add(invalid_exercise)
            db.session.commit()
        except Exception as e:
            print(f"✓ Validation caught: {e}")
            db.session.rollback()
        
        print("\nSeeding complete!")

if __name__ == '__main__':
    seed_database()