from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *

@login_required
def chat_view(request, chatroom_name='school-gc'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
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

    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)

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
        'chat_group': chat_group

    }
    
    return render(request, 'rt_chat/chat.html', context)



def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')    
    other_user = User.objects.get(username = username)
    my_private_chatrooms = request.user.chat_groups.filter(is_private=True)
    
    if my_private_chatrooms.exists():
        for chatroom in my_private_chatrooms:
            if other_user in chatroom.members.all():
                return redirect('chatroom', chatroom.group_name)
   
    chatroom = ChatGroup.objects.create( is_private = True )
    chatroom.members.add(other_user, request.user)   
    return redirect('chatroom', chatroom.group_name)
        

@login_required
def create_groupchat(request):
    form  = NewGroupForm()

    if request.method == "POST":
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom', new_groupchat.group_name)
    
    context = {
        'form': form
    }
    return render(request, 'rt_chat/create_groupchat.html', context)