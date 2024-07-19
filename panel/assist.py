import uuid
import copy
from django.utils import timezone
import jdatetime
from PIL import ImageFont, Image, ImageDraw
from django.conf import settings

def generate_uid():
	return str(uuid.uuid4()).split("-")[0]

def get_time():
  now = jdatetime.datetime.utcnow()
  time_zone = jdatetime.timedelta(hours=3, minutes=30)
  now = now + time_zone
  # return now
  return now.isoformat()

def get_date2():
	now = jdatetime.datetime.utcnow()
	time_zone = jdatetime.timedelta(hours=3, minutes=30)
	now = now + time_zone

	return f"{now.year}/{now.month}/{now.day}"


def edit_keyboard(data, target_callback_data, new_text):
	array = data
	for inner_list in array:
		for item in inner_list:
			if item["callback_data"] == target_callback_data:
				item.update({"text": new_text})
	return array



def get_filename_with_date(base_filename, extension):
  """
  Combines a base filename with the current date in YYYY-MM-DD format.

  Args:
      base_filename (str): The base name of the file (without extension).
      extension (str): The file extension (e.g., ".txt", ".csv").

  Returns:
      str: The combined filename with date (e.g., "report_2024-07-18.txt").
  """

  # Get today's date in YYYY-MM-DD format
  today_str = timezone.now().timestamp()

  # Combine filename, date, and extension
  filename_with_date = f"{base_filename}_{today_str}{extension}"

  return filename_with_date



def generate_ticket(name, date, ticket):
	number = {'1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹', '0': '۰'}
	shamsi_date = jdatetime.datetime.fromgregorian(datetime=date)
	date = shamsi_date.strftime('%Y/%m/%d %H:%M')
	for i in number:
		if i in date:
			date = date.replace(i, number[i])
	font_dir = settings.BASE_DIR / 'panel' / 'fonts'
	english_font = ImageFont.truetype(font_dir/"Fonarto.ttf", 80)
	english_font2 = ImageFont.truetype(font_dir/"Fonarto.ttf", 120)
	persian_font = ImageFont.truetype(font_dir/"Estedad.ttf", 80)
	image = Image.open(settings.BASE_DIR / 'panel' /"ticket.jpg")

	draw = ImageDraw.Draw(image)
	draw.text((1080, 660), name, (109, 129, 58), font=english_font)
	draw.text((620, 400), ticket, (109, 129, 58), font=english_font2)

	draw.text((255, 645), date, (109, 129, 58), font=persian_font)

	draw = ImageDraw.Draw(image)
	path = get_filename_with_date(ticket, '.png')
	path = f"media/img/tickets/" + path
	image.save(path)

	return path


import jdatetime
from datetime import datetime

def convert_date(date):
    if date:
        # Convert to Shamsi date
        shamsi_date = jdatetime.datetime.fromgregorian(datetime=date)
        # Update the field in the dictionary
        return shamsi_date.strftime('%Y-%m-%d %H:%M')
def timeValidation(start_time, end_time):
    """
    Checks if the current Jalali datetime (adjusted for a specific time zone)
    falls within the provided start and end times (inclusive) for a lottery registration period.

    Args:
        start_time (datetime.datetime): Start time of the lottery registration period.
        end_time (datetime.datetime): End time of the lottery registration period.

    Returns:
        tuple: (bool, str)
            - bool: True if current time is within the registration period, False otherwise.
            - str: Message indicating the validation status and current time information.
    """

    try:

        start_time = convert_date(start_time)
        end_time = convert_date(end_time)
        print(start_time, end_time)
        start_time = jdatetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_time = jdatetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")

        # Get current UTC time and apply time zone offset
        now = jdatetime.datetime.utcnow()
        time_zone = jdatetime.timedelta(hours=3, minutes=30)  # Adjust for your local time zone
        current_time = now + time_zone

        # Check conditions and generate messages
        if start_time > current_time:
            msg = "زمان ثبت نام در قرعه کشی هنوز شروع نشده."
            return False, msg
        elif end_time < current_time:
            msg = "زمان ثبت نام در قرعه کشی به پایان رسیده."
            return False, msg
        else:
            msg = "زمان ثبت نام در قرعه کشی فرا رسیده."
            return True, msg

    except TypeError as e:
        # Handle TypeError specifically
        error_msg = f"Invalid data types for start_time and end_time: {e}"
        print(error_msg)
        return False, ""

    except Exception as e:  # Catch other exceptions more generally
        # Handle other exceptions generically
        error_msg = f"An error occurred during time validation: {e}"
        print(error_msg)
        return False, ""
