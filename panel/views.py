from django.shortcuts import render
from panel.models import *
from django.http import JsonResponse
import json
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.files.storage import default_storage
from monogram.methods import sendMessage, sendPhoto
from monogram.types import InputFile
from monogram.text import INIsection, Bold
import jdatetime
from panel.assist import generate_ticket, get_time

def convert_date(date):
    if date:
        # Convert to Shamsi date
        shamsi_date = jdatetime.datetime.fromgregorian(datetime=date)
        time_zone = jdatetime.timedelta(hours=3, minutes=30)
        shamsi_date = shamsi_date + time_zone
        # Update the field in the dictionary
        return shamsi_date.strftime('%H:%M %Y/%m/%d')
    else:
        current_datetime = jdatetime.datetime.now()
        return current_datetime.strftime('%H:%M %Y/%m/%d')


def generate_response(data=None, message='successful', error=None, status_code=200):
  """
  Generates a dictionary representing a response object.

  Args:
      data (dict, optional): Data to include in the response. Defaults to None.
      message (str, optional): Message to include in the response. Defaults to None.
      error (str, optional): Error message to include in the response. Defaults to None.
      status_code (int, optional): HTTP status code for the response. Defaults to 200.

  Returns:
      dict: A dictionary representing the response structure.
  """

  response = {'status_code': status_code}

  if data:
    response['data'] = data
  if message:
    response['message'] = message
  if error:
    response['error'] = error

  return response

# Create your views here.
def home(request):
    return render(request, 'index.html')

def ProfileView(request):
    return render(request, 'Profile.html')

def MessagesView(request):
    return render(request, 'Messages.html')

def WinningView(request):
    return render(request, 'Winning.html')

def SettingsView(request):
    return render(request, 'Settings.html')


def get_users(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()  # Get all Profile objects
        profile_list = []
        for profile in profiles:
            # Create a dictionary for each profile
            profile_dict = {
                'id': profile.id,
                'profile': {'name': profile.full_name, 'username': profile.username},
                'fullName': profile.enter_name,
                'userId': profile.enter_id,
                'picture': profile.picture.url if profile.picture else None,  # Handle potential missing picture
            }
            profile_list.append(profile_dict)

        return JsonResponse(generate_response(data=profile_list))

@csrf_exempt
def load_profile_based_on_id(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    if profile_id:
      try:
        # Get the profile by ID
        profile = Profile.objects.filter(id=profile_id)
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=list(profile.values())))
      except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))


def recordChangesOfProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    enter_id = request.GET.get('enter_id')
    enter_name = request.GET.get('enter_name')
    referral_code = request.GET.get('referral_code')

    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)
        # Update the profile object with new values
        profile.referral_code = referral_code
        profile.enter_name = enter_name
        profile.enter_id = enter_id

        # Save the updated profile
        profile.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def loadProfileFriends(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)
        friends = profile.friends.all()
        profile_list = []
        for profile in friends:
            # Create a dictionary for each profile
            profile_dict = {
                "enter_id": profile.enter_id,
                "enter_name": profile.enter_name,
                "full_name": profile.full_name,
                "id": profile.id,
                "login_code": profile.login_code,
                "picture": profile.picture.url if profile.picture else None,
                "referral_code": profile.referral_code,
                "user_id": profile.user_id,
                "username": profile.username,
            }
            profile_list.append(profile_dict)

        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=profile_list))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def loadMessagesyHistoryOfProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        messages = Messages.objects.filter(sender=profile_id)
        message_data = []
        for message in messages:
            print(message.sender_picture.url)
            sender_profile = message.sender
            message_data.append({
                'id': message.id,
                'message': message.message,
                'answer': message.answer,
                'sender_picture': message.sender_picture.url if message.sender_picture else None,
                'answer_picture': message.answer_picture.url if message.answer_picture else None,
                'sender_profile': {
                    'enter_name': sender_profile.enter_name,
                    'enter_id': sender_profile.enter_id,
                }
            })
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=message_data))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def loadMessagesyHistory(request):
    # Get the profile by ID
    messages = Messages.objects.prefetch_related('sender').all()
    message_data = []
    for message in messages:
        # print(message.answer_picture)
        sender_profile = message.sender
        message_data.append({
            'id': message.id,
            'message': message.message,
            'answer': message.answer,
            'sender_picture': message.sender_picture.url if message.sender_picture else None,
            'answer_picture': message.answer_picture.url if message.answer_picture else None,
            'sender_profile': {
                'enter_name': sender_profile.enter_name,
                'enter_id': sender_profile.enter_id,
            }
        })
    # Return profile data as a dictionary
    return JsonResponse(generate_response(message='successful', data=message_data))

def deleteMessage(request):
    # Access ID from POST data
    message_id = request.GET.get('id')
    try:
        # Get the profile by ID
        message = Messages.objects.get(id=message_id)
        message.delete() # Delete the retrieved profile
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='message deleted successfully'))
    except Messages.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='message not found', status_code=404))

def closeMessage(request):
    # Access ID from POST data
    message_id = request.GET.get('id')
    try:
        # Get the profile by ID
        message = Messages.objects.get(id=message_id)
        message.status = 'CLOSED'
        message.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='message closed successfully'))
    except Messages.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='message not found', status_code=404))

def deleteProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)
        profile.delete() # Delete the retrieved profile
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='Profile deleted successfully'))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def modalHandlerLotteryProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)

        lotteries = profile.lottery_entries.all()
        data = []
        for lottery in list(lotteries.values()):
            l = Lottery.objects.get(pk=lottery['id'])
            lottery['game'] = l.game.name if l.game else ''
            friends = l.friends.all()
            lottery['friends'] = [{'id': f['id'], 'enter_name': f['enter_name']} for f in friends.values()]
            lottery['register_date'] = convert_date(lottery['register_date'])
            lottery['payment_picture'] = l.payment_picture.url if l.payment_picture else None,
            # print(lottery['register_date'])
            data.append(lottery)
        # print(data)
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=data))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def modalHandlerLotteryWinningProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)

        lotteries = profile.lottery_entries.all()
        lotteries = lotteries.filter(winning=True)

        data = []
        for lottery in list(lotteries.values()):
            l = Lottery.objects.get(pk=lottery['id'])
            friends = l.friends.all()
            lottery['friends'] = [{'id': f['id'], 'enter_name': f['enter_name']} for f in friends.values()]
            lottery['game'] = l.game.name if l.game else ''
            lottery['payment_picture'] = l.payment_picture.url if l.payment_picture else None,
            lottery['register_date'] = convert_date(lottery['register_date'])
            data.append(lottery)
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=data))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def modalHandlerLotteryWinning(request):
    winning_lotteries = Lottery.objects.select_related('profile').filter(winning=True)  # Adjust filter criteria as needed

    # Prepare data for rendering (optional)
    lottery_data = []
    for lottery in winning_lotteries:
        lottery_data.append({
            'id': lottery.id,
            'profile_id': lottery.profile.id,
            'register_date': convert_date(lottery.register_date),
            'game': lottery.game.name if lottery.game else '',
            'ticket': lottery.ticket,
            'payment_status': lottery.payment_status,
            'friends': [{'id': f['id'], 'enter_name': f['enter_name']} for f in lottery.friends.values()],
            'enter_name': lottery.profile.enter_name,
            'enter_id': lottery.profile.enter_id,
        })
    # Return profile data as a dictionary
    return JsonResponse(generate_response(message='successful', data=lottery_data))


def sortLotteryBasedOnHighest(request):
    action = request.GET.get('action')
    # Filter for winning records (winning=True)
    winning_lotteries = Lottery.objects.filter(winning=True)

    # Count the number of wins for each profile
    profile_counts = winning_lotteries.values('profile', action).annotate(count=Count(action)).order_by('-count')
    lottery_data = []
    for profile_count in profile_counts:
        profile_id = profile_count['profile']
        count = profile_count['count']

        # Get lottery entries for the current profile
        lottery_entries = Lottery.objects.filter(profile_id=profile_id, winning=True)

        # Loop through lottery entries and build the data dictionary
        for lottery in lottery_entries:

            lottery_data.append({
                'id': lottery.id,
                'register_date': convert_date(lottery.register_date),
                'game': lottery.game.name,  # Assuming 'game' has a related field with 'name'
                'ticket': lottery.ticket,
                'payment_status': lottery.payment_status,
                'price': lottery.price,
                'number_in_cart': lottery.number_in_cart,
                'friends': [{'id': f.id, 'enter_name': f.enter_name} for f in lottery.friends.all()],
                # Access all friends
                'enter_name': lottery.profile.enter_name,
                'enter_id': lottery.profile.enter_id,
            })

    # print(winning_lotteries.values('profile'))
    return JsonResponse(generate_response(message='successful', data=lottery_data))



def addAdmin(request):
    # Access ID from POST data
    name = request.GET.get('name')
    id = request.GET.get('id')
    try:
        # Get the profile by ID
        admin = Admins()
        admin.name = name
        admin.user_id = id
        admin.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def getAdmins(request):
    try:
        # Get the profile by ID
        admin = Admins.objects.all()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=list(admin.values())))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def removeAdmin(request):
    id = request.GET.get('id')
    try:
        admin = Admins.objects.get(id=id)
        admin.delete()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def addGame(request):
    # Access ID from POST data
    name = request.GET.get('name')
    try:
        # Get the profile by ID
        game = Games()
        game.name = name
        game.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def getGames(request):
    try:
        # Get the profile by ID
        game = Games.objects.all()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=list(game.values())))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def removeGame(request):
    id = request.GET.get('id')
    try:
        game = Games.objects.get(id=id)
        game.delete()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Games.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))



def setCard(request):
    # Access ID from POST data
    card_name = request.GET.get('card_name')
    card_number = request.GET.get('card_number')
    price = request.GET.get('price')
    try:
        # Get the profile by ID
        seting = Setting()
        seting.card_name = card_name
        seting.card_number = card_number
        seting.price = price
        seting.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def updateCard(request):
    # Access ID from POST data
    card_name = request.GET.get('card_name')
    card_number = request.GET.get('card_number')
    price = request.GET.get('price')
    try:
        # Get the profile by ID
        seting = Setting.objects.get(id=1)
        seting.card_name = card_name
        seting.card_number = card_number
        seting.price = price
        seting.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def getSettings(request):
    try:
        # Get the profile by ID
        setting = Setting.objects.all()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=list(setting.values())))
    except Setting.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))



def updateChannelSettings(request):
    channel = request.GET.get('channel')
    link = request.GET.get('link')
    try:
        # Get the profile by ID
        setting = Setting.objects.get(id=1)
        # Update the fields with new values (replace with your desired values)
        setting.channel = channel
        setting.link = link

        # Save the updated setting object
        setting.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Setting.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))


def send_message(request):
    message_id = request.GET.get('message_id')
    message = request.GET.get('message')

    try:
        msg = Messages.objects.get(id=message_id)
        try:
            profile = Profile.objects.get(id=msg.sender_id)
            user_id = profile.user_id
            pm1 = INIsection(Bold('پیام شما'), msg.message)
            pm2 = INIsection(Bold("جواب ادمین"), message)
            text = pm1 + '\n' + pm2
            sendMessage(chat_id=user_id, text=text)
            msg.answer = message
            msg.save()
            return JsonResponse(generate_response(message='successful'))
        except Profile.DoesNotExist:
            return JsonResponse(generate_response(error='error in sending message'))
    except Messages.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))


def sendTicket(request):
    lottery_id = request.GET.get('lottery_id')
    try:
        lottery = Lottery.objects.get(id=lottery_id)
        user_id = lottery.profile.user_id
        friendList = []
        friends = lottery.friends.all()
        for friend in friends:
            friendList.append(friend.enter_name)
        text = '✅ در خواست شما با موفقیت تایید شد.\nاطلاعات بلیط شما:'
        game = f' فعالیت انتخاب شده: {lottery.game.name}'
        friendList = INIsection("دوستان", friendList)
        text = text +'\n'+ game+'\n'+friendList
        name = lottery.profile.enter_name
        date = lottery.register_date
        ticket = lottery.ticket
        path_file = generate_ticket(name, date, ticket)
        sendPhoto(chat_id=user_id, photo=InputFile(path_file), caption=text)
        lottery.payment_status = "PAID"
        lottery.status = "Registered"
        lottery.ticket_picture = path_file[len("media/"):]
        lottery.save()
        return JsonResponse(generate_response(message='successful'))
    except Profile.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))


@csrf_exempt
def sendMessageWithImage(request):
    message_id = request.GET.get('message_id')
    message = request.GET.get('message')
    if request.method == 'POST':
        uploaded_image = request.FILES['image']
        path_file1 = 'img/uploads/' + uploaded_image.name
        default_storage.save(path_file1, uploaded_image)
        path_file = 'media/img/uploads/' + uploaded_image.name
        try:
            msg = Messages.objects.get(id=message_id)
            try:
                profile = Profile.objects.get(id=msg.sender_id)
                user_id = profile.user_id
                pm1 = INIsection('پیام شما', msg.message)
                pm2 = INIsection("جواب ادمین", message)
                text = pm1 + '\n' + pm2
                sendPhoto(chat_id=user_id, photo=InputFile(path_file), caption=text)
                msg.answer = message
                msg.answer_picture = path_file1
                msg.save()
                return JsonResponse(generate_response(message='successful'))
            except Profile.DoesNotExist:
                return JsonResponse(generate_response(error='error in sending message'))
        except Messages.DoesNotExist:
            return JsonResponse(generate_response(error='error in sending message'))

        # Return success response (optional)
        return JsonResponse({'message': 'Image uploaded successfully!'})
    else:
        return JsonResponse({'error': 'Invalid request method'})

def selectToWin(request):
    lottery_id = request.GET.get('lottery_id')
    try:
        lottery = Lottery.objects.get(id=lottery_id)
        lottery.winning = True
        lottery.save()
        return JsonResponse(generate_response(message='successful'))
    except Lottery.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))

def sendMessageToWinner(request):
    message_id = request.GET.get('message_id')
    message = request.GET.get('message')

    try:
        profile = Profile.objects.get(id=message_id)
        user_id = profile.user_id
        text = INIsection(Bold("پیام ادمین"), message)
        sendMessage(chat_id=user_id, text=text)
        return JsonResponse(generate_response(message='successful'))
    except Profile.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))


@csrf_exempt
def sendMessageWithImageToWinner(request):
    message_id = request.GET.get('message_id')
    message = request.GET.get('message')
    if request.method == 'POST':
        # Access uploaded image from request.FILES
        uploaded_image = request.FILES['image']
        path_file1 = 'img/uploads/' + uploaded_image.name
        default_storage.save(path_file1, uploaded_image)
        path_file = 'media/img/uploads/' + uploaded_image.name
        try:
            profile = Profile.objects.get(id=message_id)
            user_id = profile.user_id
            text = INIsection("پیام ادمین", message)
            sendPhoto(chat_id=user_id, photo=InputFile(path_file), caption=text)
            return JsonResponse(generate_response(message='successful'))
        except Profile.DoesNotExist:
            return JsonResponse(generate_response(error='error in sending message'))
    else:
        return JsonResponse({'error': 'Invalid request method'})


def setDate(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    lottery = request.GET.get('lottery')
    try:
        setting = Setting.objects.get(id=1)
        setting.start_time = start
        setting.end_time = end
        setting.lottery_time = lottery
        setting.save()
        return JsonResponse(generate_response(message='successful'))
    except Profile.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))



from django.http import JsonResponse
import pandas as pd
from django.utils import timezone
from django.http import FileResponse
import os

def generateExcel(request):
    setting = Setting.objects.get(id=1)
    start_time = setting.start_time
    end_time = setting.end_time

    lotteries = Lottery.objects.filter(register_date__range=(start_time, end_time), status='Registered', payment_status='PAID')
    data = []
    for lottery in lotteries:
        data.append({
            'نام کاربری': lottery.profile.enter_id,
            'نام و نام خانوادکی': lottery.profile.enter_name,
        })
    # Creating DataFrames
    df = pd.DataFrame(data)
    # Generate a timestamp
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')

    # Create a filename with the timestamp
    filename = f'lottery_{timestamp}.xlsx'
    path_dir = 'media/excel'
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    # Writing the DataFrame to an Excel file
    df.to_excel(os.path.join(path_dir, filename), index=False, engine='openpyxl')
    # Open the file in binary mode
    file = open(os.path.join(path_dir, filename), 'rb')

    # Create a FileResponse object
    response = FileResponse(file)

    # Set the Content-Disposition header to signal the browser to download the file
    response['Content-Disposition'] = f'{filename}'

    return response


def endLottery(request):
    registered_lotteries = Lottery.objects.exclude(status='Unregistered')
    for lottery in registered_lotteries:
        lottery.status = 'Unregistered'
        lottery.save()

    return JsonResponse(generate_response(message='successful'))
