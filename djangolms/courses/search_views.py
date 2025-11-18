"""
Global search views for courses, assignments, quizzes, and materials.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from djangolms.courses.models import Course, Material
from djangolms.assignments.models import Assignment, Quiz


@login_required
def global_search(request):
    """
    Global search across courses, assignments, quizzes, and materials.
    """
    query = request.GET.get('q', '').strip()
    results = {
        'courses': [],
        'assignments': [],
        'quizzes': [],
        'materials': [],
    }

    if query:
        # Search courses
        results['courses'] = Course.objects.filter(
            Q(title__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query),
            status=Course.Status.PUBLISHED
        ).select_related('instructor')[:10]

        # Search assignments (only from enrolled courses for students)
        assignments = Assignment.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).select_related('course')

        # Filter based on user role
        if request.user.is_student:
            # Only show assignments from enrolled courses
            enrolled_courses = request.user.enrollments.filter(
                status='ENROLLED'
            ).values_list('course_id', flat=True)
            assignments = assignments.filter(course_id__in=enrolled_courses)
        elif request.user.is_instructor:
            # Show assignments from courses they teach
            assignments = assignments.filter(course__instructor=request.user)

        results['assignments'] = assignments[:10]

        # Search quizzes
        quizzes = Quiz.objects.filter(
            Q(assignment__title__icontains=query) |
            Q(assignment__description__icontains=query)
        ).select_related('assignment__course')

        # Apply same filtering as assignments
        if request.user.is_student:
            enrolled_courses = request.user.enrollments.filter(
                status='ENROLLED'
            ).values_list('course_id', flat=True)
            quizzes = quizzes.filter(assignment__course_id__in=enrolled_courses)
        elif request.user.is_instructor:
            quizzes = quizzes.filter(assignment__course__instructor=request.user)

        results['quizzes'] = quizzes[:10]

        # Search materials
        materials = Material.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).select_related('module__course')

        # Filter based on enrollment
        if request.user.is_student:
            enrolled_courses = request.user.enrollments.filter(
                status='ENROLLED'
            ).values_list('course_id', flat=True)
            materials = materials.filter(module__course_id__in=enrolled_courses)
        elif request.user.is_instructor:
            materials = materials.filter(module__course__instructor=request.user)

        results['materials'] = materials[:10]

    # Calculate total results
    total_results = sum(len(v) for v in results.values())

    context = {
        'query': query,
        'results': results,
        'total_results': total_results,
    }

    return render(request, 'search/results.html', context)


@login_required
def search_courses(request):
    """
    Dedicated course search with advanced filtering.
    """
    query = request.GET.get('q', '').strip()
    instructor = request.GET.get('instructor', '')
    status = request.GET.get('status', '')

    courses = Course.objects.filter(status=Course.Status.PUBLISHED).select_related('instructor')

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query)
        )

    if instructor:
        courses = courses.filter(instructor__username__icontains=instructor)

    context = {
        'query': query,
        'courses': courses,
        'instructor': instructor,
    }

    return render(request, 'search/courses.html', context)


@login_required
def search_quizzes(request):
    """
    Dedicated quiz search.
    """
    query = request.GET.get('q', '').strip()
    course_code = request.GET.get('course', '')

    quizzes = Quiz.objects.select_related('assignment__course').all()

    # Filter based on user role
    if request.user.is_student:
        enrolled_courses = request.user.enrollments.filter(
            status='ENROLLED'
        ).values_list('course_id', flat=True)
        quizzes = quizzes.filter(assignment__course_id__in=enrolled_courses)
    elif request.user.is_instructor:
        quizzes = quizzes.filter(assignment__course__instructor=request.user)

    if query:
        quizzes = quizzes.filter(
            Q(assignment__title__icontains=query) |
            Q(assignment__description__icontains=query)
        )

    if course_code:
        quizzes = quizzes.filter(assignment__course__code__icontains=course_code)

    context = {
        'query': query,
        'quizzes': quizzes,
        'course_code': course_code,
    }

    return render(request, 'search/quizzes.html', context)
