import telebot
from telebot import types
from settings import TOKEN
import random
import uuid
import shortuuid

class User:
	registry = []

	def __init__(self, tg_id):
		self.tg_id = tg_id
		self.buisnes = []
		self.registry.append(self)

	def get_user(tg_id):
		for user in User.registry:
			if user.tg_id == tg_id:
				return user

	def user_is_know(tg_id):
		for user in User.registry:
			if user.tg_id == tg_id:
				return True
		return False

	def get_delo_by_text(self, delo_text):
		for delo in self.buisnes:
			if delo.text == delo_text:
				return delo

	def get_delo_by_id(self, delo_id):
		for delo in self.buisnes:
			if delo.delo_id == delo_id:
				return delo

	def get_delo_by_statys(self, status):
		dela = []
		for delo in self.buisnes:
			if delo.status == status:
				dela.append(delo)
		return dela




class Delo:
	STATUS_DELETE = 0
	STATUS_ACTIVE = 1
	STATUS_COMPLETED = 2

	def __init__(self, text):
		self.text = text
		self.delo_id = shortuuid.ShortUUID().random(length=5) # google random number/ random uuid
		self.status = self.STATUS_ACTIVE
		print(self.delo_id)



bot = telebot.TeleBot(TOKEN)

def get_keyboard():
	keyboard = types.ReplyKeyboardMarkup(True)
	keyboard.row('Добавить дело', 'Посмотреть дела', 'Назад')
	return keyboard

def start_keyboard():
	keyboard = telebot.types.ReplyKeyboardMarkup(True)
	keyboard.row('Мои дела', 'Помощь')
	return keyboard


@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id, 'Привет! Я твой личный бот-помощник, если хочешь узнать все про мой функционал, воспользуйся командой /help или кнопкой "Помощь" на клавиатуре', reply_markup=start_keyboard())

@bot.message_handler(commands=['help'])
def help_message(message):
	bot.send_message(message.chat.id, 'Пока что, я могу только записать твои дела')

@bot.message_handler(content_types=['text'])
def message_text(message):
	user = User.get_user(message.chat.id)
	if user is None:
		user = User(message.chat.id)
	if message.text == 'Мои дела':
		bot.send_message(message.chat.id, 'Здесь вы можете посмотреть или запланировать дела', reply_markup=get_keyboard())
	elif message.text == 'Назад':
		bot.send_message(message.chat.id, 'Хорошо', reply_markup= start_keyboard())
	elif message.text == 'Помощь':
		bot.send_message(message.chat.id, 'Пока что я могу записывать только твои дела. Если у тебя пропала клавиатура, напиши /start\nДалее воспользуйся кнопками на клавиатуре')
	elif message.text == 'Добавить дело':
		keyboard = types.ReplyKeyboardMarkup(True)
		keyboard.row('Отмена')
		delo = bot.send_message(message.chat.id, 'Напишите дело, которое вы хотите добавить:', reply_markup=keyboard)
		bot.register_next_step_handler(delo, buisnes)
	elif message.text == 'Посмотреть дела':
		keyboard = telebot.types.ReplyKeyboardMarkup(True)
		keyboard.row('Выполненные', 'Текущие', 'Назад')
		bot.send_message(message.chat.id, 'Выберите нужный раздел:', reply_markup = keyboard)
	elif message.text == 'Текущие':
		dela = user.get_delo_by_statys(Delo.STATUS_ACTIVE)
		keyboard = telebot.types.ReplyKeyboardMarkup(True)
		for itm in dela:
			keyboard.row(itm.text)
		keyboard.row('Назад')
		bot.send_message(message.chat.id, 'Выберите дело', reply_markup=keyboard)
	elif message.text in[delo.text for delo in user.buisnes]:
		delo = user.get_delo_by_text(message.text)
		deluga = types.InlineKeyboardMarkup(row_width=2)
		deluga.add(types. InlineKeyboardButton(text='Выполнить', callback_data=f'completed_{delo.delo_id}'))
		deluga.add(types.InlineKeyboardButton(text='Удалить', callback_data=f'delete_{delo.delo_id}'))
		bot.send_message(message.chat.id, message.text, reply_markup=deluga)
	elif message.text == 'Выполненные':
		dela = user.get_delo_by_statys(Delo.STATUS_COMPLETED)
		text = ''
		for d in dela:
			text += d.text + '\n'
		bot.send_message(message.chat.id, text)

@bot.callback_query_handler(func=lambda call: True)
def callback_key(call):
	user = User.get_user(call.message.chat.id)
	if user is None:
		user = User(call.message.chat.id)

	if 'completed_' in call.data:
		bot.answer_callback_query(call.id, 'Задание выполнено!')
		delo_id = call.data.replace('completed_', '')
		delo = user.get_delo_by_id(delo_id)
		delo.status = delo.STATUS_COMPLETED
	if 'delete_' in call.data:
		bot.answer_callback_query(call.id, 'Задание удалено.')
		delo_id = call.data.replace('delete_', '')
		delo = user.get_delo_by_id(delo_id)
		delo.status = delo.STATUS_DELETE



def buisnes(message):
	user = User.get_user(message.chat.id)
	if user is None:
		user = User(message.chat.id)

	if message.text == 'Отмена':
		bot.send_message(message.chat.id, 'Хорошо', reply_markup= get_keyboard())
	else:
		delo = Delo(message.text)
		user.buisnes.append(delo)
		delo = bot.send_message(message.chat.id, 'Ваше дело сохранено!', reply_markup=get_keyboard())






bot.polling(none_stop=True, interval=0)
