from typing import Tuple

from telegram import Update
from telegram.ext import Updater, CommandHandler

TOKEN = '1081971757:AAF9THRcvkp7IPty2AkOYPIanaWEzL3FDJ0'


def print_group_id(update: Update, context):
	"""Usage: /id"""
	group_id = update.message.chat.id
	update.message.reply_text(group_id)


def select_group(update: Update, context):
	"""Usage: /select group_id"""
	key = update.message.from_user.id
	value = int(update.message.text.partition(' ')[2])
	
	# Store new value
	context.bot_data[key] = value
	reply = f'Group \'{value}\' has been selected.'
	update.message.reply_text(reply)


def add_ingredient(update: Update, context):
	"""Usage: /add value"""
	# Generate ID based on user and selected chat
	if update.message.from_user.id in context.bot_data.keys():
		# get selected chat_id
		chat_id = context.bot_data[update.message.from_user.id]
		# key has to be a combination of user_id and chat_id so that a single user can be in multiple groups
		key = (update.message.from_user.id, chat_id)
		value = update.message.text.partition(' ')[2]
		
		# Grab previous value if it exists
		previous = context.bot_data[key] if key in context.bot_data.keys() else None
		
		# Store new value
		context.bot_data[key] = value
		if previous:
			reply = f'Ingredient \'{previous}\' has been replaced with \'{value}\' in group {chat_id}.'
		else:
			reply = f'Ingredient \'{value}\' has been saved to group {chat_id}.'
	else:
		reply = 'No chat has been selected yet.\n' \
				'Please select a chat with \'/select [chat_id]\' first.'
	update.message.reply_text(reply)


def delete(update: Update, context):
	"""Usage: /del"""
	if update.message.from_user.id in context.bot_data.keys():
		# get selected chat_id
		chat_id = context.bot_data[update.message.from_user.id]
		# key has to be a combination of user_id and chat_id so that a single user can be in multiple groups
		key = (update.message.from_user.id, chat_id)
		
		# Store previous value if it exists
		previous = context.bot_data[key] if key in context.bot_data.keys() else None
		
		if previous:
			del context.bot_data[key]
			reply = f'Ingredient \'{previous}\' has deleted from group {chat_id}.'
		else:
			reply = f'No ingredient has been submitted to group {chat_id}.'
	
	else:
		reply = 'No chat has been selected yet.\n' \
				'Please select a chat with \'/select [chat_id]\' first.'
	update.message.reply_text(reply)


def get(update: Update, context):
	"""Usage: /get"""
	this_chats_ingredients = []
	for key in context.bot_data.keys():
		# only add this group's ingredients
		if isinstance(key, Tuple) and key[1] == update.message.chat.id:
			this_chats_ingredients.append(f'{context.bot_data[key]}\n')
	missing = update.message.chat.get_members_count() - len(this_chats_ingredients) - 1  # the bot counts itself
	if missing == 0:
		msg = ''
		for ingredient in this_chats_ingredients:
			msg += ingredient
		update.message.reply_text(msg[:-1])
	elif missing == 1:
		update.message.reply_text('One person hasn\'t added his/her ingredient yet.\n')
	else:
		update.message.reply_text(f'{missing} people haven\'t added their ingredient yet.\n')


def print_help_msg(update: Update, context):
	"""Usage: /help"""
	msg = '/add [ingredient] - Adds an ingredient to the chat selected with \'/select [chat_id]\'' \
		  f'(This chats ID is {update.message.chat.id}), please use in private chat only!.\n' \
		  '/get - Sends a list of all the selected ingredients if all group members have selected an ingredient.\n' \
		  '/help - Prints this message.\n' \
		  '/id - Prints the ID of the current chat.\n' \
		  '/select [group_id] - Selects the given group to add ingredients to.'
	update.message.reply_text(msg)


if __name__ == '__main__':
	updater = Updater(TOKEN, use_context=True)
	dp = updater.dispatcher
	
	dp.add_handler(CommandHandler('add', add_ingredient))
	dp.add_handler(CommandHandler('del', delete))
	dp.add_handler(CommandHandler('get', get))
	dp.add_handler(CommandHandler('help', print_help_msg))
	dp.add_handler(CommandHandler('id', print_group_id))
	dp.add_handler(CommandHandler('select', select_group))
	dp.add_handler(CommandHandler('start', print_help_msg))
	
	updater.start_polling()
	updater.idle()
