from django import forms

from courses import models


class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = ["title", "description"]
        widgets = (
            {
                "description": forms.Textarea(attrs={"rows": 3}),
            },
        )
        labels = {"title": "Название курса", "description": "Описание"}
        help_texts = {"description": "Введите описание курса"}


class CoursePartForm(forms.Form):
    title = forms.CharField(max_length=255, label="Название части")
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), required=False, label="Описание"
    )


class CourseTopicForm(forms.Form):
    title = forms.CharField(max_length=255, label="Название темы")
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), required=False, label="Описание"
    )


class TopicDocumentForm(forms.Form):
    name = forms.CharField(max_length=255, label="Название документа")
    file = forms.FileField(
        label="Файл",
        required=False,
        help_text="Оставьте пустым, если не хотите изменять файл",
    )
