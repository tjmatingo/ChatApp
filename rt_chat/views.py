from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import ChatMessageChatForm

@login_required
def chat_view(request, chatroom_name='public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name="school-gc")
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatMessageChatForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if request.htmx:            # htmx only refreshes the messages not the entire page
        form = ChatMessageChatForm(request.POST)
        if form.is_valid:
            msg = form.save(commit=False) # false because we need to attach author
            msg.author = request.user
            msg.group = chat_group 
            msg.save()
            context = {
                'msg': msg,
                'user': request.user
            }
            return render(request, 'rt_chat/partials/chat_message_p.html', context)

    context = {
        "chat_msgs": chat_messages, 
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
    }
    
    return render(request, 'rt_chat/chat.html', context)


@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')

    other_user = User.objects.get(username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom
                break

            else: 
                chatroom = ChatGroup.objects.create(is_private = True)
                chatroom.members.add(other_user, request.user)
        
    else: 
        chatroom = ChatGroup.objects.create(is_private = True)
        chatroom.members.add(other_user, request.user)


    return redirect('chatroom', chatroom.group_name )
        
