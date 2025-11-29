
content = """{% extends 'quiz/base.html' %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="badge bg-secondary">{{ mode }}</span>
            <span class="text-muted">Domanda {{ index }} di {{ total }}</span>
        </div>

        <div class="card mb-4">
            <div class="card-body p-4 p-md-5">
                <h3 class="card-title mb-4">{{ question.text }}</h3>
                
                <form method="post" id="quiz-form">
                    {% csrf_token %}
                    <input type="hidden" name="action" id="action-input" value="answer">
                    
                    <div class="d-grid gap-3 mb-4">
                        {% for option in options %}
                        <button type="submit" 
                                name="option" 
                                value="{{ option.id }}" 
                                class="option-btn 
                                    {% if feedback %}
                                        {% if option.id == correct_option_id %}option-correct{% endif %}
                                        {% if option.id == selected_option_id and not is_correct %}option-wrong{% endif %}
                                    {% endif %}"
                                {% if feedback %}disabled{% endif %}>
                            {{ option.text }}
                        </button>
                        {% endfor %}
                    </div>
                </form>

                {% if feedback %}
                <div class="alert {% if is_correct %}alert-success{% else %}alert-danger{% endif %} mb-4 text-center fw-bold">
                    {% if is_correct %}
                        Corretto!
                    {% else %}
                        Risposta Errata
                    {% endif %}
                </div>
                {% endif %}

                <div class="d-flex justify-content-between mt-4">
                    <form method="post" class="d-inline">
                        {% csrf_token %}
                        <input type="hidden" name="action" value="prev">
                        <button type="submit" class="btn btn-outline-light" {% if index == 1 %}disabled{% endif %}>&larr; Indietro</button>
                    </form>

                    <form method="post" class="d-inline">
                        {% csrf_token %}
                        <input type="hidden" name="action" value="finish">
                        <button type="submit" class="btn btn-danger">Termina Test</button>
                    </form>

                    <form method="post" class="d-inline">
                        {% csrf_token %}
                        <input type="hidden" name="action" value="next">
                        <button type="submit" class="btn btn-primary" {% if not feedback %}disabled{% endif %}>Avanti &rarr;</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

with open('quiz/templates/quiz/quiz_question.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("File written successfully")
