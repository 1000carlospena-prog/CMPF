from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max
from django.contrib.auth.models import User

from .models import Conversation, Message
from config.grados import DEV_GRADO
from apps.usuarios.models import GRADO_NIVEL


def _display_name(user, viewer=None):
    if viewer and viewer.id == user.id:
        return user.profile.nombre_real or user.username
    if user.profile.grado == DEV_GRADO:
        return 'Anónimo'
    if user.profile.grado == 'v1':
        return 'Desarrollador'
    if user.profile.grado == 'v2':
        return 'Moderador'
    return user.profile.nombre_real or user.username


def _grados_visibles_chat(grado):
    nivel = GRADO_NIVEL.get(grado, 4)
    return [g for g, n in GRADO_NIVEL.items() if n >= nivel]


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
            'other_display': _display_name(other, request.user),
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

    conv.messages.filter(~Q(sender=request.user), read=False).update(read=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(conversation=conv, sender=request.user, content=content)
        return redirect('chat:conversation', conversation_id=conv.id)

    messages_qs = conv.messages.all()

    sidebar_convos = []
    for c in request.user.conversations.annotate(last_created=Max('messages__created')).order_by('-last_created'):
        o = c.participants.exclude(id=request.user.id).first()
        sidebar_convos.append({
            'conversation': c,
            'other': o,
            'other_display': _display_name(o, request.user),
        })

    return render(request, 'chat/conversation.html', {
        'conversation': conv,
        'other': other,
        'other_display': _display_name(other, request.user),
        'messages': messages_qs,
        'sidebar_convos': sidebar_convos,
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

    grados_ok = _grados_visibles_chat(request.user.profile.grado)
    users = users.filter(profile__grado__in=grados_ok)

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
        'display_name': _display_name,
    })
