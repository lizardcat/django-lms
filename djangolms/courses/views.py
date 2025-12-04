from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Course, Enrollment
from .forms import CourseForm


def course_list(request):
    """
    Display list of all published courses.
    """
    courses = Course.objects.filter(status='PUBLISHED').select_related('instructor')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'courses': courses,
        'search_query': search_query,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, course_id):
    """
    Display course details.
    Instructors can see their own courses regardless of status.
    Students and anonymous users can only see published courses.
    """
    # Allow instructors to see their own courses regardless of status
    if request.user.is_authenticated and request.user.is_instructor:
        course = get_object_or_404(Course, id=course_id)
        # Check if user is the course instructor
        if course.instructor != request.user:
            # Not the instructor, so apply published filter
            course = get_object_or_404(Course, id=course_id, status='PUBLISHED')
    else:
        # Students and anonymous users can only see published courses
        course = get_object_or_404(Course, id=course_id, status='PUBLISHED')

    is_enrolled = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status='ENROLLED'
        ).exists()

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def course_create(request):
    """
    Create a new course (instructors only).
    """
    if not request.user.is_instructor:
        messages.error(request, 'Only instructors can create courses.')
        return redirect('course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm()

    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Create'})


@login_required
def course_edit(request, course_id):
    """
    Edit an existing course (course instructor only).
    """
    course = get_object_or_404(Course, id=course_id)

    if course.instructor != request.user:
        messages.error(request, 'You can only edit your own courses.')
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" updated successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Edit', 'course': course})


@login_required
def course_enroll(request, course_id):
    """
    Enroll in a course (students only).
    """
    if not request.user.is_student:
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('course_detail', course_id=course_id)

    course = get_object_or_404(Course, id=course_id, status='PUBLISHED')

    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course, status='ENROLLED').exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('course_detail', course_id=course.id)

    # Check if course is full
    if course.is_full:
        messages.error(request, 'This course is full.')
        return redirect('course_detail', course_id=course.id)

    # Create enrollment
    Enrollment.objects.create(student=request.user, course=course)
    messages.success(request, f'Successfully enrolled in "{course.title}"!')
    return redirect('course_detail', course_id=course.id)


@login_required
def course_unenroll(request, course_id):
    """
    Unenroll from a course.
    """
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course, status='ENROLLED')

    enrollment.status = 'DROPPED'
    enrollment.save()
    messages.info(request, f'You have unenrolled from "{course.title}".')
    return redirect('course_list')


@login_required
def my_courses(request):
    """
    Display user's courses (enrolled courses for students, teaching courses for instructors).
    """
    if request.user.is_student:
        enrollments = Enrollment.objects.filter(
            student=request.user,
            status='ENROLLED'
        ).select_related('course', 'course__instructor')
        context = {
            'enrollments': enrollments,
            'user_type': 'student'
        }
    elif request.user.is_instructor:
        courses = Course.objects.filter(instructor=request.user).prefetch_related('enrollments')
        context = {
            'courses': courses,
            'user_type': 'instructor'
        }
    else:
        context = {'user_type': 'other'}

    return render(request, 'courses/my_courses.html', context)
