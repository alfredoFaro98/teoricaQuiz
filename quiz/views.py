from django.shortcuts import render, get_object_or_404, redirect
import django.http
from django.db.models import F, Sum, ExpressionWrapper, FloatField
from django.contrib import messages
from .models import Lecture, Question, AnswerOption, Subject
from .forms import LectureForm, QuestionForm, QuestionImportForm, SubjectForm
import random
import json

def home(request):
    subjects = Subject.objects.all()
    return render(request, 'quiz/subject_list.html', {'subjects': subjects})

def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    lectures = subject.lectures.all()
    return render(request, 'quiz/lecture_list.html', {'lectures': lectures, 'subject': subject})

def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SubjectForm()
    return render(request, 'quiz/subject_form.html', {'form': form, 'title': 'Nuova Materia'})

def subject_update(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'quiz/subject_form.html', {'form': form, 'title': 'Modifica Materia', 'subject': subject})

def subject_delete(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == 'POST':
        subject.delete()
        return redirect('home')
    return render(request, 'quiz/subject_confirm_delete.html', {'subject': subject})

# --- CRUD Views ---

def lecture_list(request):
    lectures = Lecture.objects.all()
    return render(request, 'quiz/lecture_list.html', {'lectures': lectures})

def lecture_detail(request, lecture_id):
    lecture = get_object_or_404(Lecture, pk=lecture_id)
    questions = lecture.questions.all()
    
    # Calculate stats for this lecture
    stats = questions.aggregate(
        answered=Sum('times_answered'),
        correct=Sum('times_correct'),
        wrong=Sum('times_wrong')
    )
    
    answered = stats['answered'] or 0
    correct = stats['correct'] or 0
    wrong = stats['wrong'] or 0
    
    accuracy = 0
    if answered > 0:
        accuracy = (correct / answered) * 100
        
    lecture_stats = {
        'answered': answered,
        'correct': correct,
        'wrong': wrong,
        'accuracy': round(accuracy, 1)
    }
    
    return render(request, 'quiz/lecture_detail.html', {
        'lecture': lecture, 
        'questions': questions,
        'stats': lecture_stats
    })

def lecture_create(request):
    if request.method == 'POST':
        form = LectureForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lecture_list')
    else:
        form = LectureForm()
    return render(request, 'quiz/lecture_form.html', {'form': form, 'title': 'Nuova Lezione'})

def lecture_update(request, lecture_id):
    lecture = get_object_or_404(Lecture, pk=lecture_id)
    if request.method == 'POST':
        form = LectureForm(request.POST, instance=lecture)
        if form.is_valid():
            form.save()
            return redirect('lecture_list')
    else:
        form = LectureForm(instance=lecture)
    
    questions = lecture.questions.all()
    return render(request, 'quiz/lecture_form.html', {
        'form': form, 
        'title': 'Modifica Lezione',
        'questions': questions,
        'lecture': lecture
    })

def lecture_delete(request, lecture_id):
    lecture = get_object_or_404(Lecture, pk=lecture_id)
    if request.method == 'POST':
        lecture.delete()
        return redirect('lecture_list')
    return render(request, 'quiz/lecture_confirm_delete.html', {'lecture': lecture})

def api_lectures(request):
    subject_id = request.GET.get('subject')
    lectures = Lecture.objects.all()
    if subject_id:
        lectures = lectures.filter(subject_id=subject_id)
    
    data = [{'id': l.id, 'title': l.title} for l in lectures]
    return django.http.JsonResponse({'lectures': data})

def question_create(request, lecture_id=None):
    initial = {}
    if lecture_id:
        lecture = get_object_or_404(Lecture, pk=lecture_id)
        initial['lecture'] = lecture
        
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            return redirect('lecture_detail', lecture_id=question.lecture.id)
    else:
        form = QuestionForm(initial=initial)
    return render(request, 'quiz/question_form.html', {'form': form, 'title': 'Nuova Domanda'})

def question_update(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            return redirect('lecture_detail', lecture_id=question.lecture.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'quiz/question_form.html', {'form': form, 'title': 'Modifica Domanda'})


def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    lecture_id = question.lecture.id
    if request.method == 'POST':
        question.delete()
        return redirect('lecture_detail', lecture_id=lecture_id)
    return render(request, 'quiz/question_confirm_delete.html', {'question': question})

# --- Quiz Logic ---

def quiz_start_total(request):
    questions = list(Question.objects.values_list('id', flat=True))
    random.shuffle(questions)
    request.session['quiz_question_ids'] = questions
    request.session['quiz_index'] = 0
    request.session['quiz_stats'] = {'correct': 0, 'wrong': 0, 'total': 0}
    request.session['quiz_mode'] = 'Totale'
    return redirect('quiz_question')

def quiz_start_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    questions = list(Question.objects.filter(lecture__subject=subject).values_list('id', flat=True))
    random.shuffle(questions)
    request.session['quiz_question_ids'] = questions
    request.session['quiz_index'] = 0
    request.session['quiz_stats'] = {'correct': 0, 'wrong': 0, 'total': 0}
    request.session['quiz_mode'] = f"Materia: {subject.name}"
    return redirect('quiz_question')

def quiz_start_lecture(request, lecture_id):
    questions = list(Question.objects.filter(lecture_id=lecture_id).values_list('id', flat=True))
    random.shuffle(questions)
    request.session['quiz_question_ids'] = questions
    request.session['quiz_index'] = 0
    request.session['quiz_stats'] = {'correct': 0, 'wrong': 0, 'total': 0}
    lecture = get_object_or_404(Lecture, pk=lecture_id)
    request.session['quiz_mode'] = f"Lezione: {lecture.title}"
    return redirect('quiz_question')

def quiz_question(request):
    question_ids = request.session.get('quiz_question_ids', [])
    index = request.session.get('quiz_index', 0)
    
    if not question_ids or index >= len(question_ids):
        return redirect('quiz_summary')
        
    question_id = question_ids[index]
    question = get_object_or_404(Question, pk=question_id)
    
    # Handle option shuffling persistence
    current_q_id_in_session = request.session.get('quiz_current_question_id')
    saved_order = request.session.get('quiz_option_order')
    
    options = list(question.options.all())
    
    if current_q_id_in_session != question.id or not saved_order:
        # New question or no order saved: shuffle and save
        random.shuffle(options)
        request.session['quiz_current_question_id'] = question.id
        request.session['quiz_option_order'] = [opt.id for opt in options]
    else:
        # Same question: restore order
        # Create a map for O(1) lookup or just sort based on index in saved_order
        # Filter out any options that might have been deleted (though unlikely in this flow)
        options_map = {opt.id: opt for opt in options}
        ordered_options = []
        for opt_id in saved_order:
            if opt_id in options_map:
                ordered_options.append(options_map[opt_id])
        options = ordered_options
    
    context = {
        'question': question,
        'options': options,
        'index': index + 1,
        'total': len(question_ids),
        'mode': request.session.get('quiz_mode', 'Quiz'),
        'feedback': False
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'answer':
            selected_option_id = request.POST.get('option')
            if selected_option_id:
                selected_option = AnswerOption.objects.get(pk=selected_option_id)
                is_correct = selected_option.is_correct
                
                # Update DB stats
                Question.objects.filter(pk=question.id).update(times_answered=F('times_answered') + 1)
                if is_correct:
                    Question.objects.filter(pk=question.id).update(times_correct=F('times_correct') + 1)
                else:
                    Question.objects.filter(pk=question.id).update(times_wrong=F('times_wrong') + 1)
                
                # Update Session stats
                stats = request.session.get('quiz_stats', {'correct': 0, 'wrong': 0, 'total': 0})
                stats['total'] += 1
                if is_correct:
                    stats['correct'] += 1
                else:
                    stats['wrong'] += 1
                request.session['quiz_stats'] = stats
                
                context['feedback'] = True
                context['selected_option_id'] = int(selected_option_id)
                context['is_correct'] = is_correct
                # We need to pass the correct option id to highlight it
                correct_option = question.options.filter(is_correct=True).first()
                context['correct_option_id'] = correct_option.id if correct_option else None
                
                return render(request, 'quiz/quiz_question.html', context)
                
        elif action == 'next':
            request.session['quiz_index'] = index + 1
            return redirect('quiz_question')
            
        elif action == 'prev':
            if index > 0:
                request.session['quiz_index'] = index - 1
            return redirect('quiz_question')
            
        elif action == 'finish':
            return redirect('quiz_summary')

    return render(request, 'quiz/quiz_question.html', context)

def question_import(request):
    if request.method == 'POST':
        form = QuestionImportForm(request.POST)
        if form.is_valid():
            json_text = form.cleaned_data['json_data']
            try:
                data = json.loads(json_text)
                questions_list = data.get('questions', [])
                
                if not isinstance(questions_list, list):
                    raise ValueError("Il campo 'questions' deve essere una lista.")
                
                count = 0
                for item in questions_list:
                    lecture_title = item.get('lecture_title')
                    subject_name = item.get('subject') # Optional subject name
                    question_text = item.get('question_text')
                    options = item.get('options')
                    correct_index = item.get('correct_index')
                    nature = item.get('nature', 'Teorica') # Default to Teorica if not provided
                    
                    if not all([lecture_title, question_text, options]) or correct_index is None:
                        continue # Skip invalid items or raise error
                        
                    if len(options) != 4:
                        continue
                        
                    # Handle Subject
                    subject = None
                    if subject_name:
                        subject, _ = Subject.objects.get_or_create(name=subject_name)

                    # Create/Get Lecture
                    # If subject is provided, we try to find/create lecture with that subject
                    if subject:
                        lecture, _ = Lecture.objects.get_or_create(title=lecture_title, defaults={'subject': subject})
                        if lecture.subject != subject:
                           # If lecture existed but had different subject, should we update? 
                           # For now, let's just ensure if it was None we set it.
                           if not lecture.subject:
                               lecture.subject = subject
                               lecture.save()
                    else:
                        lecture, _ = Lecture.objects.get_or_create(title=lecture_title)
                    
                    # Create Question
                    question = Question.objects.create(
                        lecture=lecture, 
                        text=question_text,
                        nature=nature
                    )
                    
                    # Create Options
                    for i, opt_text in enumerate(options):
                        AnswerOption.objects.create(
                            question=question,
                            text=opt_text,
                            is_correct=(i == correct_index)
                        )
                    count += 1
                
                messages.success(request, f"Importate con successo {count} domande!")
                return redirect('question_import')
                
            except json.JSONDecodeError:
                messages.error(request, "Errore: JSON non valido.")
            except Exception as e:
                messages.error(request, f"Errore durante l'importazione: {str(e)}")
    else:
        form = QuestionImportForm()
    
    return render(request, 'quiz/import_form.html', {'form': form, 'title': 'Importa Domande da JSON'})

def quiz_summary(request):
    stats = request.session.get('quiz_stats', {'correct': 0, 'wrong': 0, 'total': 0})
    percent = 0
    if stats['total'] > 0:
        percent = (stats['correct'] / stats['total']) * 100
    
    return render(request, 'quiz/quiz_summary.html', {'stats': stats, 'percent': percent})

def lecture_export_json(request, lecture_id):
    lecture = get_object_or_404(Lecture, pk=lecture_id)
    questions = lecture.questions.all()
    
    questions_data = []
    for q in questions:
        options = [opt.text for opt in q.options.all()]
        try:
            correct_option = q.options.get(is_correct=True)
            # Find index of correct option in the list of options
            # Note: The order must match. Since we just created the list from .all(), 
            # we need to be careful. Let's do it more robustly.
            options_objs = list(q.options.all())
            options_text = [opt.text for opt in options_objs]
            correct_index = -1
            for i, opt in enumerate(options_objs):
                if opt.is_correct:
                    correct_index = i
                    break
        except AnswerOption.DoesNotExist:
            correct_index = -1 # Should not happen ideally
            
        questions_data.append({
            'lecture_title': lecture.title,
            'question_text': q.text,
            'options': options_text,
            'correct_index': correct_index,
            'nature': q.nature
        })
        
    export_data = {'questions': questions_data}
    
    response = django.http.JsonResponse(export_data, json_dumps_params={'indent': 4})
    response['Content-Disposition'] = f'attachment; filename="lecture_{lecture.id}_questions.json"'
    return response

def stats_global(request):
    # Global Stats
    total_questions = Question.objects.count()
    agg_stats = Question.objects.aggregate(
        total_answered=Sum('times_answered'),
        total_correct=Sum('times_correct'),
        total_wrong=Sum('times_wrong')
    )
    
    # Handle None values if no questions answered yet
    total_answered = agg_stats['total_answered'] or 0
    total_correct = agg_stats['total_correct'] or 0
    total_wrong = agg_stats['total_wrong'] or 0
    
    global_accuracy = 0
    if total_answered > 0:
        global_accuracy = (total_correct / total_answered) * 100

    # Per-Lecture Stats
    lectures = Lecture.objects.annotate(
        l_answered=Sum('questions__times_answered'),
        l_correct=Sum('questions__times_correct')
    ).order_by('title')
    
    lecture_stats = []
    for lec in lectures:
        l_ans = lec.l_answered or 0
        l_corr = lec.l_correct or 0
        accuracy = 0
        if l_ans > 0:
            accuracy = (l_corr / l_ans) * 100
        lecture_stats.append({
            'title': lec.title,
            'accuracy': round(accuracy, 1),
            'answered': l_ans
        })

    # Hardest Questions (min 3 attempts to be significant)
    hardest_questions = Question.objects.filter(times_answered__gte=3).annotate(
        accuracy=ExpressionWrapper(
            F('times_correct') * 100.0 / F('times_answered'),
            output_field=FloatField()
        )
    ).order_by('accuracy')[:5]

    context = {
        'total_questions': total_questions,
        'total_answered': total_answered,
        'total_correct': total_correct,
        'total_wrong': total_wrong,
        'global_accuracy': round(global_accuracy, 1),
        'lecture_stats': lecture_stats,
        'hardest_questions': hardest_questions
    }
    return render(request, 'quiz/stats.html', context)
