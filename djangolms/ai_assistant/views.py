from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from djangolms.assignments.models import Assignment, Submission
from djangolms.courses.models import Course, Enrollment
from .services import ai_service
from .models import AIInteraction, AIGradingSuggestion, StudentAnalytics, QuizAssistanceSession


# ===== Student AI Assistance Views =====

@login_required
def quiz_assistant(request, assignment_id):
    """AI quiz assistant for students"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    # Check if student is enrolled
    if not Enrollment.objects.filter(student=request.user, course=course, status='ENROLLED').exists():
        messages.error(request, "You must be enrolled in this course.")
        return redirect('courses:course_detail', course_id=course.id)

    # Get or create quiz session
    session, created = QuizAssistanceSession.objects.get_or_create(
        student=request.user,
        assignment=assignment,
        session_end__isnull=True,
        defaults={'hints_requested': 0, 'explanations_requested': 0}
    )

    # Get recent interactions for this assignment
    recent_interactions = AIInteraction.objects.filter(
        user=request.user,
        assignment=assignment,
        interaction_type__in=['QUIZ_HINT', 'QUIZ_EXPLANATION', 'ANSWER_REVIEW', 'CONCEPT_HELP']
    )[:10]

    context = {
        'assignment': assignment,
        'course': course,
        'session': session,
        'recent_interactions': recent_interactions,
    }

    return render(request, 'ai_assistant/quiz_assistant.html', context)


@require_POST
@login_required
def get_hint(request, assignment_id):
    """AJAX endpoint to get a hint for a quiz question"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    question_text = request.POST.get('question', '')
    student_context = request.POST.get('context', '')

    if not question_text:
        return JsonResponse({'error': 'Question text is required'}, status=400)

    hint = ai_service.get_quiz_hint(request.user, assignment, question_text, student_context)

    # Update session
    session = QuizAssistanceSession.objects.filter(
        student=request.user,
        assignment=assignment,
        session_end__isnull=True
    ).first()

    if session:
        session.hints_requested += 1
        session.save()

    return JsonResponse({'hint': hint})


@require_POST
@login_required
def explain_concept(request, assignment_id):
    """AJAX endpoint to explain a concept"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    concept = request.POST.get('concept', '')
    question = request.POST.get('question', '')

    if not concept:
        return JsonResponse({'error': 'Concept is required'}, status=400)

    explanation = ai_service.explain_concept(request.user, assignment, concept, question)

    # Update session
    session = QuizAssistanceSession.objects.filter(
        student=request.user,
        assignment=assignment,
        session_end__isnull=True
    ).first()

    if session:
        session.explanations_requested += 1
        session.save()

    return JsonResponse({'explanation': explanation})


@require_POST
@login_required
def review_answer(request, assignment_id):
    """AJAX endpoint to review an answer before submission"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    question = request.POST.get('question', '')
    answer = request.POST.get('answer', '')

    if not question or not answer:
        return JsonResponse({'error': 'Question and answer are required'}, status=400)

    review = ai_service.review_answer(request.user, assignment, question, answer)

    return JsonResponse({'review': review})


@login_required
def study_recommendations(request, submission_id):
    """Get personalized study recommendations"""
    submission = get_object_or_404(Submission, id=submission_id, student=request.user)

    recommendations = ai_service.get_study_recommendations(
        request.user,
        submission.assignment,
        submission
    )

    context = {
        'submission': submission,
        'assignment': submission.assignment,
        'recommendations': recommendations,
    }

    return render(request, 'ai_assistant/study_recommendations.html', context)


# ===== Teacher AI Assistance Views =====

@login_required
def teacher_dashboard(request):
    """AI assistant dashboard for teachers"""
    if request.user.role != 'INSTRUCTOR':
        messages.error(request, "This feature is only available for instructors.")
        return redirect('courses:my_courses')

    # Get instructor's courses
    courses = Course.objects.filter(instructor=request.user, status='PUBLISHED')

    # Get recent AI interactions
    recent_interactions = AIInteraction.objects.filter(
        Q(course__instructor=request.user) | Q(user=request.user)
    )[:20]

    context = {
        'courses': courses,
        'recent_interactions': recent_interactions,
    }

    return render(request, 'ai_assistant/teacher_dashboard.html', context)


@login_required
def grading_assistant(request, course_id):
    """AI grading assistant for instructors"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    # Get ungraded submissions
    ungraded_submissions = Submission.objects.filter(
        assignment__course=course,
        graded=False
    ).select_related('student', 'assignment').order_by('submitted_at')

    # Get submissions with AI suggestions
    suggested_submissions = Submission.objects.filter(
        assignment__course=course,
        ai_suggestion__isnull=False,
        graded=False
    ).select_related('student', 'assignment', 'ai_suggestion')

    context = {
        'course': course,
        'ungraded_submissions': ungraded_submissions,
        'suggested_submissions': suggested_submissions,
    }

    return render(request, 'ai_assistant/grading_assistant.html', context)


@require_POST
@login_required
def generate_grading_suggestion(request, submission_id):
    """Generate AI grading suggestion for a submission"""
    submission = get_object_or_404(Submission, id=submission_id)

    # Check if user is the instructor
    if submission.assignment.course.instructor != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    suggestion = ai_service.generate_grading_suggestion(submission)

    if suggestion:
        return JsonResponse({
            'success': True,
            'suggested_score': float(suggestion.suggested_score),
            'confidence': float(suggestion.confidence_score),
            'feedback': suggestion.feedback,
            'strengths': suggestion.strengths,
            'improvements': suggestion.areas_for_improvement,
            'requires_review': suggestion.requires_human_review,
            'flagged_reason': suggestion.flagged_reason,
        })
    else:
        return JsonResponse({'error': 'Failed to generate suggestion'}, status=500)


@require_POST
@login_required
def accept_grading_suggestion(request, submission_id):
    """Accept AI grading suggestion and apply it"""
    submission = get_object_or_404(Submission, id=submission_id)

    # Check if user is the instructor
    if submission.assignment.course.instructor != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    try:
        suggestion = submission.ai_suggestion

        # Apply the suggestion
        submission.score = suggestion.suggested_score
        submission.feedback = suggestion.feedback
        submission.graded = True
        submission.graded_by = request.user
        from django.utils import timezone
        submission.graded_at = timezone.now()
        submission.save()

        # Mark suggestion as accepted
        suggestion.accepted = True
        suggestion.reviewed_by = request.user
        suggestion.reviewed_at = timezone.now()
        suggestion.save()

        messages.success(request, f"Grade applied: {submission.score}/{submission.assignment.total_points}")
        return JsonResponse({'success': True})

    except AIGradingSuggestion.DoesNotExist:
        return JsonResponse({'error': 'No AI suggestion found'}, status=404)


@login_required
def student_analytics_view(request, course_id):
    """View analytics for all students in a course"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    # Get all enrolled students
    enrollments = Enrollment.objects.filter(
        course=course,
        status='ENROLLED'
    ).select_related('student')

    # Get or generate analytics for each student
    analytics_list = []
    for enrollment in enrollments:
        analytics = StudentAnalytics.objects.filter(
            student=enrollment.student,
            course=course
        ).first()

        if not analytics:
            # Generate analytics if doesn't exist
            analytics = ai_service.analyze_student_performance(enrollment.student, course)

        if analytics:
            analytics_list.append({
                'student': enrollment.student,
                'analytics': analytics
            })

    # Sort by risk level
    risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    analytics_list.sort(key=lambda x: risk_order.get(x['analytics'].risk_level, 4))

    context = {
        'course': course,
        'analytics_list': analytics_list,
    }

    return render(request, 'ai_assistant/student_analytics.html', context)


@login_required
def student_detail_analytics(request, course_id, student_id):
    """Detailed analytics for a specific student"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    student = get_object_or_404(User, id=student_id)

    # Check enrollment
    if not Enrollment.objects.filter(student=student, course=course).exists():
        messages.error(request, "Student is not enrolled in this course.")
        return redirect('ai_assistant:student_analytics', course_id=course_id)

    # Get or generate analytics
    analytics = StudentAnalytics.objects.filter(student=student, course=course).first()

    if not analytics:
        analytics = ai_service.analyze_student_performance(student, course)

    # Get all submissions
    submissions = Submission.objects.filter(
        student=student,
        assignment__course=course
    ).select_related('assignment').order_by('-submitted_at')

    context = {
        'course': course,
        'student': student,
        'analytics': analytics,
        'submissions': submissions,
    }

    return render(request, 'ai_assistant/student_detail_analytics.html', context)


@require_POST
@login_required
def refresh_analytics(request, course_id, student_id):
    """Refresh analytics for a student"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    student = get_object_or_404(User, id=student_id)

    analytics = ai_service.analyze_student_performance(student, course)

    if analytics:
        messages.success(request, f"Analytics refreshed for {student.get_full_name() or student.username}")
    else:
        messages.warning(request, "Could not generate analytics. Student may not have any graded submissions.")

    return redirect('ai_assistant:student_detail_analytics', course_id=course_id, student_id=student_id)
