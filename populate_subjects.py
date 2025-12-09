import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Subject, Lecture

def populate_subjects():
    # Create default subject
    general_subject, created = Subject.objects.get_or_create(
        name="Generale",
        defaults={
            'description': 'Materia predefinita per le lezioni esistenti.',
            'color': '#3B82F6'
        }
    )
    
    if created:
        print(f"Created default subject: {general_subject.name}")
    else:
        print(f"Subject {general_subject.name} already exists")

    # Assign all lectures without a subject to this default subject
    lectures = Lecture.objects.filter(subject__isnull=True)
    count = lectures.count()
    
    if count > 0:
        lectures.update(subject=general_subject)
        print(f"Updated {count} lectures to belong to '{general_subject.name}'")
    else:
        print("No lectures found needing update.")

if __name__ == '__main__':
    populate_subjects()
