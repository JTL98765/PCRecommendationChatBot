@echo off
rasa train
start "" "C:\PCChatBot\pc_chatbot.html"
rasa run --enable-api --cors "*" --connector socketio

