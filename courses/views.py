from django.shortcuts import render, redirect
from courses import models
from courses import forms
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.core.paginator import Paginator

# Отправка сигнала (например, в views.py)
from courses.signals.custom_signals import course_published


@require_GET
def courses(request):
    paginator = Paginator(models.Course.objects.all().order_by("title"), 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "course_list.html", {"page_obj": page_obj})


@require_http_methods(["GET", "POST"])
def create_course(request):
    if request.method == "POST":
        form = forms.CourseForm(request.POST)

        if form.is_valid():
            form.save()

            course_published.send(
                sender=models.Course, course=form.instance, user=request.user
            )

            return redirect("courses")
    else:
        form = forms.CourseForm()
        return render(request, "course_form.html", {"form": form})


@require_GET
def course_details(request, course_id):
    # Course -> parts (CoursePart) -> topics (CourseTopic) -> documents (TopicDocument)
    course = models.Course.objects.prefetch_related("parts__topics__documents").get(
        id=course_id
    )
    return render(request, "course_details.html", {"course": course})


@require_http_methods(["GET", "POST"])
def update_course(request, course_id):
    course = models.Course.objects.get(id=course_id)
    if request.method == "POST":
        form = forms.CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("courses")
    else:
        form = forms.CourseForm(instance=course)
        return render(request, "course_form.html", {"form": form})


@require_POST
def delete_course(request, course_id):
    course = models.Course.objects.get(id=course_id)
    course.delete()
    return redirect("courses")


@require_http_methods(["GET", "POST"])
def create_course_part(request, course_id):
    course = models.Course.objects.get(id=course_id)
    if request.method == "POST":
        form = forms.CoursePartForm(request.POST)
        if form.is_valid():
            course.parts.create(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
            )
            return redirect("course-details", course_id=course_id)
        else:
            return render(
                request, "course_part_form.html", {"form": form, "course_id": course_id}
            )
    else:
        form = forms.CoursePartForm()
        return render(
            request, "course_part_form.html", {"form": form, "course_id": course_id}
        )


@require_http_methods(["GET", "POST"])
def create_course_topic(request, course_id, part_id):
    part = models.CoursePart.objects.get(id=part_id)
    if request.method == "POST":
        form = forms.CourseTopicForm(request.POST)
        if form.is_valid():
            part.topics.create(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
            )
            return redirect("course-details", course_id=course_id)
        else:
            return render(
                request,
                "course_topic_form.html",
                {"form": form, "course_id": course_id, "part_id": part_id},
            )
    else:
        form = forms.CourseTopicForm()
        return render(
            request,
            "course_topic_form.html",
            {"form": form, "course_id": course_id, "part_id": part_id},
        )


@require_http_methods(["GET", "POST"])
def create_topic_document(request, course_id, part_id, topic_id):
    topic = models.CourseTopic.objects.get(id=topic_id)
    if request.method == "POST":
        form = forms.TopicDocumentForm(request.POST, request.FILES)
        # При создании файл обязателен
        if form.is_valid():
            if not form.cleaned_data.get("file"):
                form.add_error("file", "Файл обязателен при создании документа")
                return render(
                    request,
                    "topic_document_form.html",
                    {
                        "form": form,
                        "course_id": course_id,
                        "part_id": part_id,
                        "topic_id": topic_id,
                    },
                )
            topic.documents.create(
                name=form.cleaned_data["name"], file=form.cleaned_data["file"]
            )
            return redirect("course-details", course_id=course_id)
        else:
            return render(
                request,
                "topic_document_form.html",
                {
                    "form": form,
                    "course_id": course_id,
                    "part_id": part_id,
                    "topic_id": topic_id,
                },
            )
    else:
        form = forms.TopicDocumentForm()
        return render(
            request,
            "topic_document_form.html",
            {
                "form": form,
                "course_id": course_id,
                "part_id": part_id,
                "topic_id": topic_id,
            },
        )


# Update и Delete для CoursePart
@require_http_methods(["GET", "POST"])
def update_course_part(request, course_id, part_id):
    part = models.CoursePart.objects.get(id=part_id)
    if request.method == "POST":
        form = forms.CoursePartForm(request.POST)
        if form.is_valid():
            part.title = form.cleaned_data["title"]
            part.description = form.cleaned_data["description"]
            part.save()
            return redirect("course-details", course_id=course_id)
        else:
            return render(
                request,
                "course_part_form.html",
                {
                    "form": form,
                    "course_id": course_id,
                    "part_id": part_id,
                    "is_edit": True,
                },
            )
    else:
        form = forms.CoursePartForm(
            initial={"title": part.title, "description": part.description}
        )
        return render(
            request,
            "course_part_form.html",
            {"form": form, "course_id": course_id, "part_id": part_id, "is_edit": True},
        )


@require_POST
def delete_course_part(request, course_id, part_id):
    part = models.CoursePart.objects.get(id=part_id)
    part.delete()
    return redirect("course-details", course_id=course_id)


# Update и Delete для CourseTopic
@require_http_methods(["GET", "POST"])
def update_course_topic(request, course_id, part_id, topic_id):
    topic = models.CourseTopic.objects.get(id=topic_id)
    if request.method == "POST":
        form = forms.CourseTopicForm(request.POST)
        if form.is_valid():
            topic.title = form.cleaned_data["title"]
            topic.description = form.cleaned_data["description"]
            topic.save()
            return redirect("course-details", course_id=course_id)
        else:
            return render(
                request,
                "course_topic_form.html",
                {
                    "form": form,
                    "course_id": course_id,
                    "part_id": part_id,
                    "topic_id": topic_id,
                    "is_edit": True,
                },
            )
    else:
        form = forms.CourseTopicForm(
            initial={"title": topic.title, "description": topic.description}
        )
        return render(
            request,
            "course_topic_form.html",
            {
                "form": form,
                "course_id": course_id,
                "part_id": part_id,
                "topic_id": topic_id,
                "is_edit": True,
            },
        )


@require_POST
def delete_course_topic(request, course_id, part_id, topic_id):
    topic = models.CourseTopic.objects.get(id=topic_id)
    topic.delete()
    return redirect("course-details", course_id=course_id)


# Update и Delete для TopicDocument
@require_http_methods(["GET", "POST"])
def update_topic_document(request, course_id, part_id, topic_id, document_id):
    document = models.TopicDocument.objects.get(id=document_id)
    if request.method == "POST":
        form = forms.TopicDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document.name = form.cleaned_data["name"]
            if form.cleaned_data.get("file"):
                document.file = form.cleaned_data["file"]
            document.save()
            return redirect("course-details", course_id=course_id)
        else:
            return render(
                request,
                "topic_document_form.html",
                {
                    "form": form,
                    "course_id": course_id,
                    "part_id": part_id,
                    "topic_id": topic_id,
                    "document_id": document_id,
                    "document": document,
                    "is_edit": True,
                },
            )
    else:
        form = forms.TopicDocumentForm(initial={"name": document.name})
        return render(
            request,
            "topic_document_form.html",
            {
                "form": form,
                "course_id": course_id,
                "part_id": part_id,
                "topic_id": topic_id,
                "document_id": document_id,
                "document": document,
                "is_edit": True,
            },
        )


@require_POST
def delete_topic_document(request, course_id, part_id, topic_id, document_id):
    document = models.TopicDocument.objects.get(id=document_id)
    document.delete()
    return redirect("course-details", course_id=course_id)
