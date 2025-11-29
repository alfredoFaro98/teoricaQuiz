from django import forms
from .models import Lecture, Question, AnswerOption

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class QuestionForm(forms.ModelForm):
    option_1 = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Option 1'}))
    option_2 = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Option 2'}))
    option_3 = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Option 3'}))
    option_4 = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Option 4'}))
    
    correct_option = forms.ChoiceField(
        choices=[('1', 'Option 1'), ('2', 'Option 2'), ('3', 'Option 3'), ('4', 'Option 4')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Correct Option"
    )

    class Meta:
        model = Question
        fields = ['lecture', 'text', 'nature']
        widgets = {
            'lecture': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nature': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            options = self.instance.options.all()
            if len(options) >= 4:
                self.fields['option_1'].initial = options[0].text
                self.fields['option_2'].initial = options[1].text
                self.fields['option_3'].initial = options[2].text
                self.fields['option_4'].initial = options[3].text
                
                for i, option in enumerate(options):
                    if option.is_correct:
                        self.fields['correct_option'].initial = str(i + 1)
                        break

    def save(self, commit=True):
        question = super().save(commit=commit)
        
        opt_texts = [
            self.cleaned_data['option_1'],
            self.cleaned_data['option_2'],
            self.cleaned_data['option_3'],
            self.cleaned_data['option_4']
        ]
        correct_idx = int(self.cleaned_data['correct_option']) - 1

        if self.instance.pk:
            # Update existing options
            options = list(question.options.all())
            # If for some reason we don't have 4, we might need to handle it, but assuming constraints hold:
            if len(options) < 4:
                # Delete and recreate if inconsistent
                question.options.all().delete()
                options = []
            
            if not options:
                for i, text in enumerate(opt_texts):
                    AnswerOption.objects.create(
                        question=question,
                        text=text,
                        is_correct=(i == correct_idx)
                    )
            else:
                for i, option in enumerate(options):
                    if i < 4:
                        option.text = opt_texts[i]
                        option.is_correct = (i == correct_idx)
                        option.save()
        else:
            # Create new options
            # We need to save question first if commit=False, but here we assume commit=True or handle it in view
            # If commit=False, we can't save related objects yet. 
            # For simplicity, we assume commit=True or the view handles saving the question first.
            if commit:
                for i, text in enumerate(opt_texts):
                    AnswerOption.objects.create(
                        question=question,
                        text=text,
                        is_correct=(i == correct_idx)
                    )
        
        return question

class QuestionImportForm(forms.Form):
    json_data = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Paste JSON here...'}),
        label="JSON Data",
        help_text="Incolla qui il JSON con le domande."
    )
