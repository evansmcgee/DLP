import os, zipfile

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error, info
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import UserForm, RegistrationForm, ModuleForm
from .models import User, InviteCode, Modules, UserProfile, ModulesStatus, MessageBoard, Teams, MessageViews
from .helpers import generator


def index(request):
    if request.user.is_authenticated():
        return redirect("/home/")

    else:
        form = UserForm()
        return render(request,"login.html",{'LoginForm':form})


def register(request, invite="0000"):
    if request.method == "POST":
        current_invite = InviteCode.objects.get(invite_code=request.POST['invite'])

        if current_invite.active:
            new_user = User.objects.create_user(request.POST['username'],current_invite.email,request.POST['password'])
            new_profile = UserProfile(user=new_user,
                                      invite_code=request.POST['invite'],
                                      team=current_invite.leader)

            team = Teams(team=current_invite.leader,
                         member=new_user)

            if current_invite.staff:
                new_user.is_staff = True

            new_profile.save()
            new_user.save()
            team.save()

            current_invite.active = False
            current_invite.save()

            info(request,"You have been registered, please login")
            return redirect("/login/")
        else:
            return redirect("/")
    else:
        if request.user.is_authenticated():
            return redirect("/home/")
        else:
            return render(request, "register.html",{'form': RegistrationForm(),'invite':invite})


def userlogin(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                info(request, "Welcome back")
                return redirect("/home/")

            else:
                info(request, "User is not active")
                return redirect("/login/")

        else:
            error(request, "There was an error with your username/password")
            return redirect("/login/")

    else:
        form = UserForm()
        return render(request, "login.html", {'LoginForm': form})


@csrf_exempt
@login_required
def content_mgmt(request):

    if request.method == "POST":
        if request.POST["action"] == "delete":
            Modules.objects.filter(name=request.POST["item"]).delete()
            info(request, "Module Deleted")
            return redirect("/home/")

        elif request.POST["action"] == "publish":
            mod = Modules.objects.get(name=request.POST["item"])

            if mod.published:
                mod.published = False
                info(request, "Module Unpublished")

            else:
                mod.published = True
                info(request, "Module Published")

            mod.save()

            return redirect("/home/")

        elif request.POST["action"] == "upload":

            if request.FILES["module"]:
                uploadedfile = request.FILES["module"]
                module_dir = "modules/"
                ext = uploadedfile.name.split(".")
                storage = generator.id_generator(size=16)
                upload_dir = os.path.join(module_dir,storage,uploadedfile.name)
                fs = FileSystemStorage()
                fs.save(upload_dir, uploadedfile)

                if ext[1:len(ext)][0] == "zip" and os.path.isfile(upload_dir):
                    zip_ref = zipfile.ZipFile(upload_dir,"r")
                    zip_ref.extractall(os.path.join(settings.MEDIA_ROOT,module_dir,storage,'store'))
                    zip_ref.close()

                if not request.POST['name']:
                    module_name = ext[0]

                else:
                    module_name = request.POST['name']

                Modules(name=module_name,
                        description=request.POST['description'],
                        owner=request.user.username,
                        storage=storage,
                        module=uploadedfile.name)

                info(request, "Module Uploaded")
                return redirect("/home/")

    else:
        return redirect("/home/")


@login_required
def home(request):

    modules = Modules.objects.all()
    personal_stats = ModulesStatus.objects.filter(user=request.user.id)
    return render(request, "home.html", {"modules": modules,
                                         "pstats":personal_stats,})


@login_required
def manage(request):

    if request.method == "POST":

        if request.POST.get('staff'):
            staff = True

        else:
            staff = False


        # TODO: move invite code stuff from models
        invite = InviteCode().create_code(leader=request.user,
                                          email=request.POST['email'],
                                          staff=staff)

        # send invite email.
        message = """
            # email/invite not working yet
            Good Day,
            You've been invited to use the Daimlier Learning Platform

            http://localhost:8000/register/%s

            Cheers,
            The DLP Team
            """ % invite

        info(request, message)
        return redirect("/manage")


    total_invites = InviteCode.objects.all()
    pending_invites = total_invites.filter(active=True)
    team_all_invites = total_invites.filter(leader=request.user)
    team_pending_invites = total_invites.filter(active=True, leader=request.user)

    # superusers can see all teams.
    current_team = UserProfile.objects.filter(team=request.user)

    module_all = Modules.objects.filter(published=True)
    module_status = ModulesStatus.objects.all()

    dasstats = []
    for a in module_all:
        if a.published:
            for b in module_status:
                if a.id == b.module_id:
                    dasstats.append({"user_id":b.user_id,"status":b.status,"module":a,"dtg":b.dtg})


    return render(request, "manage.html", {"total_invites":total_invites,
                                           "pending_invites":pending_invites,
                                           "team_pending_invites":team_pending_invites,
                                           "team_all_invites":team_all_invites,
                                           "current_team":current_team,
                                           "module_status":module_status,
                                           "dasstats":dasstats,
                                           "modules":module_all})




@login_required
def module(request, storage=None):

    try:
        current_module = Modules.objects.get(storage=storage)
        if not ModulesStatus.objects.filter(user=request.user,module=current_module):
            ModulesStatus(user=request.user,
                          module=current_module,
                          status="started").save()

        return render(request, "module.html", {"module": current_module})

    except:
        info(request, "There was an error with your request")
        return redirect("/home/")



@login_required
def profile(request):

    if request.method == "POST":
        current_user = User.objects.get(username=request.user.username)
        current_user.email = request.POST['email']
        current_user.first_name = request.POST['firstname']
        current_user.last_name = request.POST['lastname']
        current_user.save()
        info(request, "Profile Updated")
        return redirect('/profile')

    else:
        return render(request, "profile.html")


@login_required
def userlogout(request):

    logout(request)
    return redirect("/home/")


@login_required
def message(request, message_id=None):

    myprofile = UserProfile.objects.get(user=request.user)
    board = MessageBoard.objects.filter(team=myprofile.team, parent=0).order_by("-id")
    board_views = MessageViews.objects.filter(user=request.user)

    if request.method == "POST":

        try:

            MessageBoard(body=request.POST["body"],
                         author=request.user,
                         parent=request.POST["parent"],
                         team=myprofile.team).save()

            info(request,"beta message")
            return redirect("/message/" + request.POST["parent"])
        except:
            MessageBoard(title=request.POST["title"],
                         body=request.POST["body"],
                         author=request.user,
                         parent=0,
                         team=myprofile.team).save()
            info(request, "Message Posted")
            return redirect("/message/")


    if message_id:
        try:
            payload = MessageBoard.objects.get(id=message_id)
            payload_reply = MessageBoard.objects.filter(parent=message_id)
            if not MessageViews.objects.filter(message=payload, user=request.user, data="view"):
                MessageViews(message=payload, user=request.user, data="view").save()
        except:
            info(request, "There was a problem with your request")
            return redirect("/message/")

    else:
        payload=None
        payload_reply=None

    return render(request, "message.html", {"board":board,
                                            "views":board_views,
                                            "payload":payload,
                                            "payload_reply":payload_reply})


