from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import ChatMessageChatForm

@login_required
def chat_view(request):
    chat_group = get_object_or_404(ChatGroup, group_name="School GC")
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatMessageChatForm()

    if request.htmx:            # htmx only refreshes the messages not the entire page
        form = ChatMessageChatForm(request.POST)
        if form.is_valid:
            msg = form.save(commit=False) # false because we need to attach author
            msg.author = request.user
            msg.group = chat_group 
            msg.save()
            context = {
                'message': msg,
                'user': request.user
            }
            return render(request, 'rt_chat/partials/chat_message_p.html', context)

    
    return render(request, 'rt_chat/chat.html', {"chat_msgs": chat_messages, 'form': form})