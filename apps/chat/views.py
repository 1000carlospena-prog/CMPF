from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max
from django.contrib.auth.models import User

from .models import Conversation, Message


@login_required
def inbox(request):
    conversations = request.user.conversations.annotate(
        last_created=Max('messages__created')
    ).order_by('-last_created')

    ctx = []
    for c in conversations:
        other = c.participants.exclude(id=request.user.id).first()
        last = c.last_message
        unread = c.messages.filter(~Q(sender=request.user), read=False).count()
        ctx.append({
            'conversation': c,
            'other': other,
            'last_message': last,
            'unread': unread,
        })

    return render(request, 'chat/inbox.html', {
        'conversations': ctx,
    })


@login_required
def conversation_detail(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    other = conv.participants.exclude(id=request.user.id).first()

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(conversation=conv, sender=request.user, content=content)
        return redirect('chat:conversation', conversation_id=conv.id)

    conv.messages.filter(~Q(sender=request.user), read=False).update(read=True)

    messages_qs = conv.messages.all()
    return render(request, 'chat/conversation.html', {
        'conversation': conv,
        'other': other,
        'messages': messages_qs,
    })


@login_required
def start_conversation(request, user_id):
    other = get_object_or_404(User, id=user_id)
    if other == request.user:
        messages.error(request, 'No puedes chatear contigo mismo.')
        return redirect('chat:inbox')

    conv = Conversation.objects.filter(participants=request.user).filter(participants=other).first()
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, other)

    return redirect('chat:conversation', conversation_id=conv.id)


@login_required
def search_users(request):
    q = request.GET.get('q', '').strip()
    grado = request.GET.get('grado', '')
    users = User.objects.exclude(id=request.user.id).select_related('profile')

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(profile__nombre_real__icontains=q)
        )
    if grado:
        users = users.filter(profile__grado=grado)

    users = users.order_by('username')

    return render(request, 'chat/search_users.html', {
        'users': users,
        'q': q,
        'grado': grado,
    })
