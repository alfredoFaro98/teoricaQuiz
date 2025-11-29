from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F
from django.contrib import messages
from .models import Lecture, Question, AnswerOption
from .forms import LectureForm, QuestionForm, QuestionImportForm
import random
import json

def home(request):
    lectures = Lecture.objects.all()
    # Annotate with question count if needed, or just do it in template
    lecture_data = []
    for lecture in lectures:
        lecture_data.append({
            'lecture': lecture,
            'question_count': lecture.questions.count()
        })
    return render(request, 'quiz/home.html', {'lectures': lecture_data})

# --- CRUD Views ---

def lecture_list(request):
    lectures = Lecture.objects.all()
    return render(request, 'quiz/lecture_list.html', {'lectures': lectures})

def lecture_detail(request, lecture_id):
    lecture = get_object_or_404(Lecture, pk=lecture_id)
    questions = lecture.questions.all()
    return render(request, 'quiz/lecture_detail.html', {'lecture': lecture, 'questions': questions})

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
                    question_text = item.get('question_text')
                    options = item.get('options')
                    correct_index = item.get('correct_index')
                    nature = item.get('nature', 'Teorica') # Default to Teorica if not provided
                    
                    if not all([lecture_title, question_text, options]) or correct_index is None:
                        continue # Skip invalid items or raise error
                        
                    if len(options) != 4:
                        continue
                        
                    # Create/Get Lecture
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
