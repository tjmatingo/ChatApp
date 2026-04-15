from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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


    # only verified users join chat rooms
    '''   
    if chat_group.groupchat_name:
        if request.uuser not in chat_group.members.all():
            if request.user.emailaddress_set.filter(verified=True).exists():
                chat_group.members.add(request.user)
            else:
                messages.warning(request, 'You need to verify your email to join the chat!')
                return redirect('profile-settings')
    '''
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

@login_required
def chatroom_edit_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    form = ChatroomEditForm(instance=chat_group)

    if request.method == "POST":
        form = ChatroomEditForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()

            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.members.remove(member)

            return redirect('chatroom', chatroom_name)

    context = {
        'form': form,
        'chat_group': chat_group
    }
    
    return render(request, 'rt_chat/chatroom_edit.html', context)


@login_required
def chatroom_delete(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.user != chat_group.admin:
        raise Http404()

    if request.method == 'POST':
        chat_group.delete()
        messages.success(request, 'Chatroom PURGED!!')
        return redirect('home')

    context = {
        'chat_group': chat_group
    }
    
    return render(request, 'rt_chat/chatroom_delete.html', context)

@login_required
def chatroom_leave(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.user not in chat_group.members.all():
        raise Http404()
    
    if request.method == 'POST':
        chat_group.members.remove(request.user)
        messages.success(request, f'You left the group{chat_group.groupchat_name}!')
        return redirect('home')
    
    return redirect('chatroom', chatroom_name=chatroom_name) 


def chat_file_upload(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    # checking for htmx request with file attached to the request
    if request.htmx and request.FILES:
        file = request.FILES['file']
        message = GroupMessage.objects.create(
            file = file,
            author = request.user,
            group = chat_group,
        )

        channel_layer = get_channel_layer()

        event = {
            'type': 'message_handler',
            'message_id': message.id, 
        }

        async_to_sync(channel_layer.group_send)(
            chatroom_name, event
        )
    return HttpResponse()