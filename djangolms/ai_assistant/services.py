"""
AI Service Layer for Django LMS
Handles all AI API interactions using Anthropic's Claude API
"""
import os
import time
from anthropic import Anthropic
from django.conf import settings
from .models import AIInteraction


class AIAssistantService:
    """Service class for AI assistant functionality"""

    def __init__(self):
        # Get API key from environment or settings
        self.api_key = os.getenv('ANTHROPIC_API_KEY', getattr(settings, 'ANTHROPIC_API_KEY', None))
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
            self.model = getattr(settings, 'AI_MODEL', 'claude-3-5-sonnet-20241022')
        else:
            self.client = None
            self.model = None

    def _call_claude(self, system_prompt, user_message, max_tokens=4096):
        """Internal method to call Claude API"""
        if not self.client:
            return {
                'response': "AI service is not configured. Please set ANTHROPIC_API_KEY in your environment.",
                'tokens': 0,
                'time_ms': 0
            }

        start_time = time.time()

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            response_text = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens
            time_ms = int((time.time() - start_time) * 1000)

            return {
                'response': response_text,
                'tokens': tokens_used,
                'time_ms': time_ms
            }
        except Exception as e:
            return {
                'response': f"Error calling AI service: {str(e)}",
                'tokens': 0,
                'time_ms': int((time.time() - start_time) * 1000)
            }

    def _log_interaction(self, user, interaction_type, user_input, ai_response,
                        tokens, time_ms, course=None, assignment=None, submission=None):
        """Log AI interaction for analytics"""
        AIInteraction.objects.create(
            user=user,
            interaction_type=interaction_type,
            user_input=user_input,
            ai_response=ai_response,
            model_used=self.model or 'not_configured',
            tokens_used=tokens,
            response_time_ms=time_ms,
            course=course,
            assignment=assignment,
            submission=submission
        )

    # ===== Student Assistance Methods =====

    def get_quiz_hint(self, user, assignment, question_text, student_context=""):
        """Provide a hint for a quiz question without giving away the answer"""
        system_prompt = """You are an educational AI assistant helping students with quizzes.
Your goal is to provide helpful hints that guide students toward understanding, NOT to give direct answers.
Be encouraging and supportive. Keep hints concise and actionable."""

        user_message = f"""Assignment: {assignment.title}
Question: {question_text}

{f"Student's context: {student_context}" if student_context else ""}

Please provide a helpful hint that guides the student toward the answer without directly giving it away."""

        result = self._call_claude(system_prompt, user_message, max_tokens=500)

        self._log_interaction(
            user=user,
            interaction_type='QUIZ_HINT',
            user_input=question_text,
            ai_response=result['response'],
            tokens=result['tokens'],
            time_ms=result['time_ms'],
            assignment=assignment,
            course=assignment.course
        )

        return result['response']

    def explain_concept(self, user, assignment, concept, student_question=""):
        """Explain a concept related to the assignment"""
        system_prompt = """You are an expert educator. Explain concepts clearly and concisely.
Use examples and analogies when helpful. Tailor explanations to student needs.
Break down complex topics into understandable parts."""

        user_message = f"""Assignment: {assignment.title}
Assignment Description: {assignment.description}

Concept to explain: {concept}
{f"Student's specific question: {student_question}" if student_question else ""}

Please provide a clear, educational explanation of this concept."""

        result = self._call_claude(system_prompt, user_message, max_tokens=1000)

        self._log_interaction(
            user=user,
            interaction_type='CONCEPT_HELP',
            user_input=f"{concept} | {student_question}",
            ai_response=result['response'],
            tokens=result['tokens'],
            time_ms=result['time_ms'],
            assignment=assignment,
            course=assignment.course
        )

        return result['response']

    def review_answer(self, user, assignment, question, student_answer):
        """Review a student's answer before submission and provide feedback"""
        system_prompt = """You are an educational AI providing constructive feedback on student answers.
Be encouraging but honest. Point out strengths and areas for improvement.
Don't give the correct answer directly, but guide students to improve their response.
If the answer is completely wrong, gently redirect them."""

        user_message = f"""Assignment: {assignment.title}
Question: {question}
Student's Answer: {student_answer}

Please review this answer and provide constructive feedback. Help the student understand if they're on the right track."""

        result = self._call_claude(system_prompt, user_message, max_tokens=800)

        self._log_interaction(
            user=user,
            interaction_type='ANSWER_REVIEW',
            user_input=f"Q: {question}\nA: {student_answer}",
            ai_response=result['response'],
            tokens=result['tokens'],
            time_ms=result['time_ms'],
            assignment=assignment,
            course=assignment.course
        )

        return result['response']

    def get_study_recommendations(self, user, assignment, submission=None):
        """Provide personalized study recommendations based on submission"""
        system_prompt = """You are an educational advisor providing study recommendations.
Based on a student's work, suggest specific topics to review and study strategies.
Be specific and actionable."""

        submission_text = submission.submission_text if submission else "No submission yet"
        score_text = f"Score: {submission.score}/{assignment.total_points}" if submission and submission.score else ""

        user_message = f"""Assignment: {assignment.title}
Assignment Type: {assignment.get_assignment_type_display()}
{score_text}

Student's submission:
{submission_text}

Based on this work, what specific topics should the student review? Provide actionable study recommendations."""

        result = self._call_claude(system_prompt, user_message, max_tokens=800)

        self._log_interaction(
            user=user,
            interaction_type='CONCEPT_HELP',
            user_input=f"Study recommendations for {assignment.title}",
            ai_response=result['response'],
            tokens=result['tokens'],
            time_ms=result['time_ms'],
            assignment=assignment,
            submission=submission,
            course=assignment.course
        )

        return result['response']

    # ===== Teacher Assistance Methods =====

    def generate_grading_suggestion(self, submission):
        """Generate AI grading suggestion for a submission"""
        from .models import AIGradingSuggestion

        assignment = submission.assignment
        system_prompt = f"""You are an expert grading assistant for educators.
Evaluate student submissions fairly and consistently.
Provide specific, constructive feedback that helps students learn.

Assignment Details:
- Title: {assignment.title}
- Type: {assignment.get_assignment_type_display()}
- Total Points: {assignment.total_points}
- Description: {assignment.description}

Grading Criteria:
- Accuracy and correctness
- Completeness
- Clarity of expression
- Understanding of concepts

Respond in this exact JSON format:
{{
  "suggested_score": <number between 0 and {assignment.total_points}>,
  "confidence": <number between 0 and 100>,
  "feedback": "<detailed feedback string>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": ["<area 1>", "<area 2>"],
  "requires_review": <true/false>,
  "review_reason": "<reason if flagged>"
}}"""

        user_message = f"""Student: {submission.student.get_full_name() or submission.student.username}

Submission Text:
{submission.submission_text or '[No text provided]'}

{f"Attached File: {submission.submission_file.name}" if submission.submission_file else ""}

Please evaluate this submission and provide a grading suggestion."""

        result = self._call_claude(system_prompt, user_message, max_tokens=2000)

        # Parse the response (in production, use proper JSON parsing with error handling)
        import json
        try:
            suggestion_data = json.loads(result['response'])

            # Create or update grading suggestion
            ai_suggestion, created = AIGradingSuggestion.objects.update_or_create(
                submission=submission,
                defaults={
                    'suggested_score': suggestion_data.get('suggested_score', 0),
                    'confidence_score': suggestion_data.get('confidence', 0),
                    'feedback': suggestion_data.get('feedback', ''),
                    'strengths': suggestion_data.get('strengths', []),
                    'areas_for_improvement': suggestion_data.get('improvements', []),
                    'requires_human_review': suggestion_data.get('requires_review', False),
                    'flagged_reason': suggestion_data.get('review_reason', ''),
                }
            )

            # Log interaction
            self._log_interaction(
                user=submission.assignment.course.instructor,
                interaction_type='GRADING_ASSIST',
                user_input=f"Grade request: {submission.assignment.title} - {submission.student.username}",
                ai_response=result['response'],
                tokens=result['tokens'],
                time_ms=result['time_ms'],
                assignment=assignment,
                submission=submission,
                course=assignment.course
            )

            return ai_suggestion

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return None

    def generate_bulk_feedback(self, submissions):
        """Generate feedback for multiple submissions efficiently"""
        results = []
        for submission in submissions:
            if not submission.graded:
                suggestion = self.generate_grading_suggestion(submission)
                results.append(suggestion)
        return results

    def analyze_student_performance(self, student, course):
        """Analyze a student's performance in a course"""
        from .models import StudentAnalytics
        from djangolms.assignments.models import Submission
        from djangolms.grades.models import CourseGrade

        # Get all submissions for this student in this course
        submissions = Submission.objects.filter(
            student=student,
            assignment__course=course,
            graded=True
        ).select_related('assignment')

        if not submissions.exists():
            return None

        # Build performance summary
        total_points_earned = sum(s.score or 0 for s in submissions)
        total_points_possible = sum(s.assignment.total_points for s in submissions)
        percentage = (total_points_earned / total_points_possible * 100) if total_points_possible > 0 else 0

        submission_details = "\n".join([
            f"- {s.assignment.title} ({s.assignment.get_assignment_type_display()}): "
            f"{s.score}/{s.assignment.total_points} ({(s.score/s.assignment.total_points*100):.1f}%)"
            for s in submissions
        ])

        system_prompt = """You are an educational data analyst helping instructors identify students who need support.
Analyze student performance data and provide actionable insights.
Identify learning gaps, strengths, and recommend specific interventions.

Respond in this JSON format:
{
  "predicted_grade": "<letter grade>",
  "risk_level": "<LOW/MEDIUM/HIGH/CRITICAL>",
  "engagement_score": <0-100>,
  "participation_trend": "<IMPROVING/STABLE/DECLINING>",
  "learning_gaps": ["<gap 1>", "<gap 2>"],
  "strengths": ["<strength 1>", "<strength 2>"],
  "recommendations": ["<recommendation 1>", "<recommendation 2>"],
  "summary": "<2-3 sentence summary>"
}"""

        user_message = f"""Student: {student.get_full_name() or student.username}
Course: {course.title}

Performance Summary:
- Overall Score: {percentage:.1f}% ({total_points_earned}/{total_points_possible} points)
- Assignments Completed: {submissions.count()}

Assignment Breakdown:
{submission_details}

Please analyze this student's performance and provide insights for the instructor."""

        result = self._call_claude(system_prompt, user_message, max_tokens=2000)

        # Parse and save analytics
        import json
        try:
            analytics_data = json.loads(result['response'])

            analytics, created = StudentAnalytics.objects.update_or_create(
                student=student,
                course=course,
                defaults={
                    'predicted_grade': analytics_data.get('predicted_grade', ''),
                    'risk_level': analytics_data.get('risk_level', 'LOW'),
                    'engagement_score': analytics_data.get('engagement_score', 0),
                    'participation_trend': analytics_data.get('participation_trend', 'STABLE'),
                    'learning_gaps': analytics_data.get('learning_gaps', []),
                    'strengths': analytics_data.get('strengths', []),
                    'recommendations': analytics_data.get('recommendations', []),
                    'summary': analytics_data.get('summary', ''),
                    'analyzed_assignments_count': submissions.count(),
                }
            )

            # Log interaction
            self._log_interaction(
                user=course.instructor,
                interaction_type='STUDENT_ANALYTICS',
                user_input=f"Analyze {student.username} in {course.title}",
                ai_response=result['response'],
                tokens=result['tokens'],
                time_ms=result['time_ms'],
                course=course
            )

            return analytics

        except json.JSONDecodeError:
            return None

    def identify_struggling_students(self, course):
        """Identify students who are struggling in a course"""
        from djangolms.courses.models import Enrollment

        enrolled_students = Enrollment.objects.filter(
            course=course,
            status='ENROLLED'
        ).select_related('student')

        struggling_students = []

        for enrollment in enrolled_students:
            analytics = self.analyze_student_performance(enrollment.student, course)
            if analytics and analytics.risk_level in ['HIGH', 'CRITICAL']:
                struggling_students.append({
                    'student': enrollment.student,
                    'analytics': analytics
                })

        return struggling_students


# Create a singleton instance
ai_service = AIAssistantService()
