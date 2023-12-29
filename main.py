import video2signal
import telebot
from predictions_generator import Predictions_Generator
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Need to take tg bot TOKEN
bot = telebot.TeleBot('TOKEN')
# Credentials file from firebase
cred = credentials.Certificate("credential file")
# db url
firebase_admin = firebase_admin.initialize_app(cred,
                                               {"databaseURL": "url"})

ref = db.reference('/')
# Initializing xgboost classifier
generator = Predictions_Generator('xgb_model.json')
# For saving video
video_id = 0

# String that shows when /start command is activated
start_message = ""
# String that shows when /advice command is activated
advice_message = ""

# /start command
@bot.message_handler(commands=['start'])
def start_message(message):

    bot.send_message(message.from_user.id, text=start_message)

# /advice command
@bot.message_handler(commands=['advice'])
def advice_message(message):

    bot.send_message(message.from_user.id, text=advice_message)

# /stats command
@bot.message_handler(commands=['stats'])
def statistics(message):
    id = str(message.from_user.id)
    only_stress = dict()
    all_cases = dict()
    percentage = dict()
    keys = set()
    for i in ref.get():
        components = i.split('_')
        if components[0] == 'tag' and components[1] != 'all' and id == components[1]:
            only_stress[components[-1]] = int(db.reference(i).get())
            keys.add(components[-1])
        elif components[0] == 'tag' and components[1] == 'all' and id == components[2]:
            all_cases[components[-1]] = int(db.reference(i).get())
            keys.add(components[-1])
    for i in keys:
        percentage[i] = only_stress[i]/all_cases[i]*100
    msg = 'Вот ваша статистика:\n'
    for i in keys:
        msg+=i+' -  количество стрессовых ситуаций: '+str(only_stress[i])+', Общее количество: '+str(all_cases[i])+', Частота стрессовых ситуаций: '+str(percentage[i])+'%\n'
    bot.send_message(message.from_user.id, text=msg)


# Analyzing video function
@bot.message_handler(content_types=['video','video_note'])
def analyze_stress(message):
    global video_id
    if message.content_type == 'video':
        video = bot.get_file(message.video.file_id)
    else:
        video = bot.get_file(message.video_note.file_id)
    video_name = str(video_id)
    video_id += 1
    video_path = video.file_path
    video_name += '.'+video_path.split('.')[-1]
    print(video_path)
    video_as_file = bot.download_file(video_path)
    bot.send_message(message.from_user.id, text='Обработка в процессе. Генерирую результат.')
    with open("videos/" + video_name, "wb") as videofile:
        videofile.write(video_as_file)
    response = generator.generate_prediction(
        video2signal.get_metrics(video2signal.convert_to_signal("videos/" + video_name)))
    if response == 0:
        message_text = "В данный момент вы спокойны. Так держать!"
    else:
        message_text = "Судя по вашим результатам, вы испытываете стресс. Советую сделать перерыв и выполнить дыхательные упражнения, чтобы снизить уровень стресса."
    bot.send_message(message.from_user.id, text=message_text)
    ref.update({str(message.from_user.id)+'_last':response})
    ref.update({str(message.from_user.id)+'_wait_for_resp':True})
    bot.send_message(message.from_user.id, text="Не могли бы вы написать одним или несколькими словами последние события? Например (работа, болезнь, отдых)")
    try:
        os.remove("videos/" + video_name)
    except:
        pass

# Marking results with tag
@bot.message_handler(content_types=['text'])
def write_tag(message):
    result = db.reference(str(message.from_user.id)+'_wait_for_resp').get()
    print(result)
    message_text = ''
    for i in message.text:
        if 'a' <= i.lower() <= 'z' or 'а' <= i.lower() <= 'я':
            message_text += i
    if result:
        r = db.reference('tag_'+str(message.from_user.id)+'_'+message_text+'/')
        if r.get() is not None:
            print(r.get())
            ref.update({'tag_'+str(message.from_user.id)+'_'+message_text:r.get()+db.reference(str(message.from_user.id)+'_last').get()})
            ref.update({'tag_all_'+str(message.from_user.id)+'_'+message_text:db.reference('tag_all_'+str(message.from_user.id)+'_'+message_text+'/').get()+1})
        else:
            ref.update({'tag_'+str(message.from_user.id)+'_'+message_text:db.reference(str(message.from_user.id)+'_last').get()})
            ref.update({'tag_all_'+str(message.from_user.id)+'_'+message_text:1})

        ref.update({str(message.from_user.id) + '_wait_for_resp': False})
        bot.send_message(message.from_user.id,
                         text="Ответ записан")


if __name__ == '__main__':
    file = open('start_message.txt','r', encoding = 'utf-8')
    start_message = file.read()
    file.close()
    file = open('advice_message.txt','r', encoding = 'utf-8')
    advice_message = file.read()
    file.close()
    bot.polling(none_stop=True, interval=0)

