from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *


@login_required
def chat_view(request):
    chat_group = get_object_or_404(ChatGroup, group_name="School-GC")
    chat_msgs = ChatGroup.chat_msgs.all()[:30]
    return render(request, 'rt_chat/chat.html', {"chat_msgs": chat_msgs})