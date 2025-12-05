from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Max

from djangolms.courses.models import Course, Enrollment
from .models import ChatRoom, Message, MessageReadReceipt, UserPresence, ChatNotification


@login_required
def chat_home(request):
    """Chat home page showing all available chat rooms"""
    # Get user's courses
    if request.user.role == 'STUDENT':
        enrollments = Enrollment.objects.filter(
            student=request.user,
            status='ENROLLED'
        ).select_related('course')
        user_courses = [e.course for e in enrollments]
    else:
        # Instructors get their teaching courses (published and draft)
        user_courses = list(Course.objects.filter(instructor=request.user))

    # Auto-create chat rooms for courses that don't have them (optimized)
    # Get existing course chat rooms
    existing_rooms = set(
        ChatRoom.objects.filter(
            course__in=user_courses,
            room_type='COURSE'
        ).values_list('course_id', flat=True)
    )

    # Create missing rooms in bulk
    rooms_to_create = []
    for course in user_courses:
        if course.id not in existing_rooms:
            rooms_to_create.append(ChatRoom(
                course=course,
                room_type='COURSE',
                name=f"{course.title} - Chat",
                created_by=request.user,
                is_active=True,
            ))

    if rooms_to_create:
        ChatRoom.objects.bulk_create(rooms_to_create)

    # Get course chat rooms
    course_rooms = ChatRoom.objects.filter(
        course__in=user_courses,
        room_type='COURSE',
        is_active=True
    ).select_related('course')

    # Get direct message and group chat rooms
    dm_rooms = ChatRoom.objects.filter(
        participants=request.user,
        room_type__in=['DIRECT', 'GROUP'],
        is_active=True
    ).distinct()

    # Get unread message counts (optimized to avoid N+1 queries)
    all_rooms = list(course_rooms) + list(dm_rooms)
    room_ids = [room.id for room in all_rooms]

    # Single query to get all unread counts
    unread_data = ChatNotification.objects.filter(
        user=request.user,
        room_id__in=room_ids,
        is_read=False
    ).values('room_id').annotate(count=Count('id'))

    # Convert to dictionary
    unread_counts = {item['room_id']: item['count'] for item in unread_data}

    # Fill in zeros for rooms with no unread messages
    for room_id in room_ids:
        if room_id not in unread_counts:
            unread_counts[room_id] = 0

    context = {
        'course_rooms': course_rooms,
        'dm_rooms': dm_rooms,
        'unread_counts': unread_counts,
        'user_courses': user_courses,
    }

    return render(request, 'chat/chat_home.html', context)


@login_required
def chat_room(request, room_id):
    """Chat room view"""
    room = get_object_or_404(ChatRoom, id=room_id, is_active=True)

    # Check access permissions
    has_access = False

    if room.room_type == 'COURSE':
        # Check if user is enrolled or is the instructor
        if request.user.role == 'INSTRUCTOR' and room.course.instructor == request.user:
            has_access = True
        elif Enrollment.objects.filter(student=request.user, course=room.course, status='ENROLLED').exists():
            has_access = True
    else:
        # For DM and group chats, check if user is a participant
        if room.participants.filter(id=request.user.id).exists():
            has_access = True

    if not has_access:
        messages.error(request, "You don't have access to this chat room.")
        return redirect('chat:chat_home')

    # Get recent messages (last 50)
    messages_list = Message.objects.filter(
        room=room,
        is_deleted=False
    ).select_related('sender', 'reply_to', 'reply_to__sender').order_by('-created_at')[:50]

    # Reverse to show oldest first
    messages_list = list(reversed(messages_list))

    # Mark notifications as read
    ChatNotification.objects.filter(
        user=request.user,
        room=room,
        is_read=False
    ).update(is_read=True)

    # Get online users
    online_users = UserPresence.objects.filter(
        room=room,
        is_online=True
    ).select_related('user')

    context = {
        'room': room,
        'messages': messages_list,
        'online_users': online_users,
    }

    return render(request, 'chat/chat_room.html', context)


@login_required
def create_course_chat_room(request, course_id):
    """Create a chat room for a course"""
    course = get_object_or_404(Course, id=course_id)

    # Only instructors can create course chat rooms
    if course.instructor != request.user:
        messages.error(request, "Only the course instructor can create a chat room.")
        return redirect('courses:course_detail', course_id=course.id)

    # Check if room already exists
    existing_room = ChatRoom.objects.filter(course=course, room_type='COURSE').first()

    if existing_room:
        messages.info(request, "Chat room already exists for this course.")
        return redirect('chat:chat_room', room_id=existing_room.id)

    # Create room
    room = ChatRoom.objects.create(
        name=f"{course.title} - Chat",
        room_type='COURSE',
        course=course,
        created_by=request.user
    )

    messages.success(request, f"Chat room created for {course.title}")
    return redirect('chat:chat_room', room_id=room.id)


@login_required
def create_direct_message(request, user_id):
    """Create or get existing direct message room"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    other_user = get_object_or_404(User, id=user_id)

    if other_user == request.user:
        messages.error(request, "You cannot create a direct message with yourself.")
        return redirect('chat:chat_home')

    # Check if DM already exists
    existing_room = ChatRoom.objects.filter(
        room_type='DIRECT',
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if existing_room:
        return redirect('chat:chat_room', room_id=existing_room.id)

    # Create new DM room
    room = ChatRoom.objects.create(
        name=f"{request.user.username} & {other_user.username}",
        room_type='DIRECT',
        created_by=request.user
    )

    room.participants.add(request.user, other_user)

    return redirect('chat:chat_room', room_id=room.id)


@require_POST
@login_required
def delete_message(request, message_id):
    """Delete a message (soft delete)"""
    message = get_object_or_404(Message, id=message_id)

    # Only sender can delete
    if message.sender != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    message.is_deleted = True
    message.content = "[Message deleted]"
    message.save()

    return JsonResponse({'success': True})


@require_POST
@login_required
def edit_message(request, message_id):
    """Edit a message"""
    message = get_object_or_404(Message, id=message_id)

    # Only sender can edit
    if message.sender != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    new_content = request.POST.get('content', '').strip()

    if not new_content:
        return JsonResponse({'error': 'Content cannot be empty'}, status=400)

    if len(new_content) > 5000:
        return JsonResponse({'error': 'Message too long (maximum 5000 characters)'}, status=400)

    message.content = new_content
    message.is_edited = True
    message.save()

    return JsonResponse({
        'success': True,
        'content': message.content,
        'is_edited': message.is_edited
    })


@login_required
def load_more_messages(request, room_id):
    """Load more messages (pagination)"""
    room = get_object_or_404(ChatRoom, id=room_id)

    # Check access permissions
    has_access = False

    if room.room_type == 'COURSE':
        # Check if user is enrolled or is the instructor
        if request.user.role == 'INSTRUCTOR' and room.course.instructor == request.user:
            has_access = True
        elif Enrollment.objects.filter(student=request.user, course=room.course, status='ENROLLED').exists():
            has_access = True
    else:
        # For DM and group chats, check if user is a participant
        if room.participants.filter(id=request.user.id).exists():
            has_access = True

    if not has_access:
        return JsonResponse({'error': 'Access denied'}, status=403)

    before_id = request.GET.get('before', None)

    messages_query = Message.objects.filter(
        room=room,
        is_deleted=False
    ).select_related('sender', 'reply_to')

    if before_id:
        messages_query = messages_query.filter(id__lt=before_id)

    messages_list = messages_query.order_by('-created_at')[:50]

    # Serialize messages
    messages_data = [{
        'id': msg.id,
        'sender_id': msg.sender.id,
        'sender_name': msg.sender.get_full_name() or msg.sender.username,
        'sender_username': msg.sender.username,
        'content': msg.content,
        'message_type': msg.message_type,
        'reply_to': msg.reply_to.id if msg.reply_to else None,
        'created_at': msg.created_at.isoformat(),
        'is_edited': msg.is_edited,
    } for msg in messages_list]

    return JsonResponse({'messages': messages_data})


@login_required
def notifications_count(request):
    """Get unread chat notifications count"""
    count = ChatNotification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return JsonResponse({'count': count})
