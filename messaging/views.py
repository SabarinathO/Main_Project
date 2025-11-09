from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Conversation, Message
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.db.models import Max
from django.db.models import Count
from .tasks import disband_expired_group

@login_required(login_url="/signup/")
def get_or_create_conversation(request, user_id):
    """ Get or create a chat between two users """
    user2 = get_object_or_404(User, id=user_id)
    
    # Ensure only ONE conversation exists between the two users
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=user2).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, user2)
    
    receiver = conversation.participants.exclude(id=request.user.id).first()
    
    messages = conversation.messages.all()
    users = User.objects.all().exclude(id=request.user.id)
    group_chats = Conversation.objects.filter(is_groupchat=True, participants=request.user).order_by("-id")
    now = timezone.now() 
    context = {
        'conversation': conversation,
        'messages': messages,
        'users': users,
        'group_chats': group_chats,
        'receiver': receiver,
        'now': now
    }
    return render(request, "networking/privateChat.html", context)

@login_required
def send_message(request, conversation_id):
    """ Send a new message """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    content = request.POST.get("content")

    if content:
        message = Message.objects.create(conversation=conversation, sender=request.user, content=content)
        return JsonResponse({"message": message.content, "sender": message.sender.username, "timestamp": message.timestamp})

    return JsonResponse({"error": "Message cannot be empty"}, status=400)

def chatInterface(request):
    users = User.objects.all().exclude(id=request.user.id)
    group_chats = Conversation.objects.filter(is_groupchat=True, participants=request.user).order_by("-id")
    return render(request, "networking/chatInterface.html", {"users": users, "group_chats": group_chats})

@login_required
def group_chat(request, group_id):
    """ Fetch an existing group chat or create a new one """
    
    conversation = Conversation.objects.annotate(
            participant_count=Count("participants")
        ).filter(
        id=group_id,
        is_groupchat=True,
        participants=request.user,
        participant_count__gt=1).first() # Ensure at least 2 participants

    if not conversation:
       return redirect("chatInterface")  # Or render a fallback page

    group_name = conversation.groupname

    messages = conversation.messages.all().order_by("timestamp")
    users = User.objects.exclude(id=request.user.id)
    group_chats = Conversation.objects.filter(is_groupchat=True, participants=request.user).order_by("-id")
    member_count = conversation.participants.count()
    members = conversation.participants.all().exclude(id=conversation.creator.id)
    if conversation.expiry_at and conversation.expiry_at < timezone.now():
        # Check if the group has expired
    # only shows popup if extension_pending is True
        conversation.extension_pending = True
        conversation.extension_popup_shown = True  # Avoid repeated popups
        conversation.save()  

    context = {
        'conversation': conversation,
        'messages': messages,
        'users': users,
        'group_name': group_name,
        'group_chats': group_chats,
        'member_count': member_count,
        'members': members,
        'group_creator': conversation.creator,
        'profile_pic': conversation.profile_pic
    }

    return render(request, "networking/groupchat.html", context)

def new_groupChat(request):
    if request.method == "POST":
        group_name = request.POST.get("group_name")
        group_pic = request.FILES.get("group_pic")
        members = request.POST.get("group_members")  # Comma-separated usernames
        timespan_type = request.POST.get("timespan_type")
        timespan_value = request.POST.get("timespan_value")
        
        if not group_name:
            return render(request, "networking/groupChat.html", {"error": "Group name cannot be empty"})

        conversation = Conversation.objects.create(
            is_groupchat=True,
            groupname=group_name,
            creator=request.user,
            timespan_type=timespan_type if timespan_type else "none",
            timespan_value=int(timespan_value) if timespan_value else 1,
        )

        if group_pic:
            conversation.profile_pic = group_pic

        conversation.participants.add(request.user)

        if members:
            member_list = [username.strip() for username in members.split(",")]
            for username in member_list:
                try:
                    user = User.objects.get(username=username)
                    conversation.participants.add(user)
                except User.DoesNotExist:
                    pass

        conversation.save()
        
# Schedule expiration check
    if conversation.timespan_type != "none":
        now = timezone.now()
        if conversation.timespan_type == "hours":
            expiry_time = now + timedelta(hours=conversation.timespan_value)
        elif conversation.timespan_type == "days":
            expiry_time = now + timedelta(days=conversation.timespan_value)
        elif conversation.timespan_type == "months":
            expiry_time = now + timedelta(days=conversation.timespan_value * 30)

        conversation.expiry_at = expiry_time
        conversation.save()

        delay = (expiry_time - now).total_seconds()
        disband_expired_group.apply_async((conversation.id,), countdown=delay)


        members = conversation.participants.all().exclude(id=conversation.creator.id)
        group_chats = Conversation.objects.filter(is_groupchat=True, participants=request.user).order_by("-id")

        context = {
            'conversation': conversation,
            'users': User.objects.all().exclude(id=request.user.id),
            'group_name': group_name,
            'group_chats': group_chats,
            'member_count': conversation.participants.count(),
            'members': members,
            'group_creator': conversation.creator,
            'profile_pic': conversation.profile_pic
        }

        return render(request, "networking/groupChat.html", context)

    return render(request, "networking/ChatInterface.html")

@login_required
def send_group_message(request, conversation_id):
    """ Send a message to the group chat """
    conversation = get_object_or_404(Conversation, id=conversation_id, is_groupchat=True)
    content = request.POST.get("content")

    if content:
        message = Message.objects.create(conversation=conversation, sender=request.user, content=content)
        return JsonResponse({"message": message.content, "sender": message.sender.username, "timestamp": message.timestamp})

    return JsonResponse({"error": "Message cannot be empty"}, status=400)

@login_required(login_url="/signup/")
def profile(request):
    user = request.user
    username = user.username
    return render(request, "networking/profile.html", {"username": username})

@login_required(login_url="/signup/")
def home(request):
    user = request.user
    username = user.username
    return render(request, "networking/home.html", {"username": username})

@csrf_exempt
@login_required
def handle_extension_decision(request, conversation_id):
    """ Handle group extension or deletion after expiry """
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user != conversation.creator:
        return JsonResponse({"error": "Only the admin can perform this action"}, status=403)

    decision = request.POST.get("decision")
    new_type = request.POST.get("new_type")
    new_value = int(request.POST.get("new_value", 0))

    if decision == "extend" and new_type in ["hours", "days", "months"]:
        now = timezone.now()

        if new_type == "hours":
            conversation.expiry_at = now + timedelta(hours=new_value)
        elif new_type == "days":
            conversation.expiry_at = now + timedelta(days=new_value)
        elif new_type == "months":
            conversation.expiry_at = now + timedelta(days=new_value * 30)

        conversation.timespan_type = new_type
        conversation.timespan_value = new_value
        conversation.start_time = timezone.now()
        conversation.extension_pending = False
        conversation.extension_asked_at = None

        conversation.save()

        delay = (conversation.expiry_at - timezone.now()).total_seconds()
        disband_expired_group.apply_async((conversation.id,), countdown=delay)

        return JsonResponse({"status": "extended"})

    elif decision == "decline":
        conversation.participants.clear()  # ← This removes all participants 
        conversation.delete()
        return redirect("chatInterface")
       

    return JsonResponse({"error": "Invalid decision"}, status=400)
