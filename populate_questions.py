import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Lecture, Question, AnswerOption

def populate():
    # Create Lecture
    lecture, created = Lecture.objects.get_or_create(
        title="Lecture 1 – Introduction",
        defaults={'description': "Introduction to Theoretical Computer Science, Course Organization, and Assessment."}
    )
    if created:
        print(f"Created lecture: {lecture}")
    else:
        print(f"Using existing lecture: {lecture}")

    # Questions Data
    questions_data = [
        {
            "page": 3,
            "text": "What is the main focus of Part A of the course?",
            "options": [
                ("Decidability and Logic", True),
                ("Computational Complexity", False),
                ("Algorithm Design", False),
                ("Computer Architecture", False)
            ]
        },
        {
            "page": 3,
            "text": "What is the main focus of Part B of the course?",
            "options": [
                ("Computational Complexity", True),
                ("Formal Languages", False),
                ("First-order Logic", False),
                ("Turing Machines", False)
            ]
        },
        {
            "page": 4,
            "text": "How many lectures are delivered by Prof. Marco Manna (Part A)?",
            "options": [
                ("16", True),
                ("24", False),
                ("12", False),
                ("56", False)
            ]
        },
        {
            "page": 4,
            "text": "What is the minimum attendance required for each module to qualify for the final exam?",
            "options": [
                ("70%", True),
                ("50%", False),
                ("80%", False),
                ("100%", False)
            ]
        },
        {
            "page": 10,
            "text": "How many multiple-choice questions are there in the exam for each module?",
            "options": [
                ("15", True),
                ("10", False),
                ("5", False),
                ("20", False)
            ]
        },
        {
            "page": 11,
            "text": "What is the minimum score required for M_part_x (multiple-choice questions) to pass?",
            "options": [
                ("9", True),
                ("18", False),
                ("15", False),
                ("12", False)
            ]
        },
        {
            "page": 12,
            "text": "Which of the following statements is syntactically correct to define Hany?",
            "options": [
                ("Hany = {<M> | ∃w s.t. M(w) = h}", True),
                ("Hany = {<M,w> | ∃w s.t. M(w) = h}", False),
                ("Hany = {<M> | ∃w s.t. M(w) = }", False),
                ("Hany = {<M> | ∃w and ∃M s.t. M(w) ∈ {y,n,h} }", False)
            ]
        },
        {
            "page": 13,
            "text": "Given (q2,a)→q1 and (q2,b)→q3, what is the yield-in-one-step of (q2, babbaa)?",
            "options": [
                ("(q3, abbaa)", True),
                ("(q3, babbaa)", False),
                ("(q1, babba)", False),
                ("(q2, abbaa)", False)
            ]
        },
        {
            "page": 19,
            "text": "What question does Computability Theory primarily address?",
            "options": [
                ("Is a problem solvable on a computer?", True),
                ("How efficiently can a problem be solved?", False),
                ("How to design the fastest algorithm?", False),
                ("How to secure data?", False)
            ]
        },
        {
            "page": 19,
            "text": "What question does Complexity Theory primarily address?",
            "options": [
                ("How efficiently a solvable problem can be solved?", True),
                ("Is a problem solvable?", False),
                ("Is a problem undecidable?", False),
                ("Can a machine emulate human behavior?", False)
            ]
        },
        {
            "page": 24,
            "text": "What is a key difference between TCS and AI?",
            "options": [
                ("TCS explores the limits of computation; AI mimics human cognitive abilities.", True),
                ("TCS focuses on machine learning; AI focuses on logic.", False),
                ("TCS is about hardware; AI is about software.", False),
                ("There is no difference.", False)
            ]
        }
    ]

    for q_data in questions_data:
        question, created = Question.objects.get_or_create(
            lecture=lecture,
            text=q_data['text'],
            defaults={'page_number': q_data['page']}
        )
        
        if created:
            print(f"Created question: {question} (Page {q_data['page']})")
            # Create options
            for opt_text, is_correct in q_data['options']:
                AnswerOption.objects.create(
                    question=question,
                    text=opt_text,
                    is_correct=is_correct
                )
        else:
            print(f"Question already exists: {question}")

if __name__ == '__main__':
    populate()
