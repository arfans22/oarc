""" ollama_chatbot_class.py

    ollama_agent_roll_cage, is a command line interface for STT, & TTS commands with local LLMS.
    It is an easy to install add on for the ollama application.
    
        This software was designed by Leo Borcherding with the intent of creating an easy to use
    ai interface for anyone, through Speech to Text and Text to Speech.
        
        With ollama_agent_roll_cage we can provide hands free access to LLM data. 
    This has a host of applications and I want to bring this software to users 
    suffering from blindness/vision loss, and children suffering from austism spectrum 
    disorder as way for learning and expanding communication and speech. 
    
        The C3PO ai is a great imaginary friend! I could envision myself 
    talking to him all day telling me stories about a land far far away! 
    This makes learning fun and accessible! Children would be directly 
    rewarded for better speech as the ai responds to subtle differences 
    in language ultimately educating them without them realizing it.

    Development for this software was started on: 4/20/2024 
    By: Leo Borcherding
        on github @ 
            leoleojames1/ollama_agent_roll_cage

"""
import os
import sys
import subprocess
import json
import re
import keyboard
import time
import speech_recognition as sr
import ollama
import shutil
import threading
import pyautogui
import glob
from PIL import Image
import base64

from Public_Chatbot_Base_Wand.flags import flag_manager
from Public_Chatbot_Base_Wand.ollama_add_on_library import ollama_commands
from Public_Chatbot_Base_Wand.speech_to_speech import tts_processor_class
from Public_Chatbot_Base_Wand.directory_manager import directory_manager_class
from Public_Chatbot_Base_Wand.latex_render import latex_render_class
from Public_Chatbot_Base_Wand.data_set_manipulator import data_set_constructor
from Public_Chatbot_Base_Wand.write_modelfile import model_write_class
from Public_Chatbot_Base_Wand.chat_history import json_chat_history
from Public_Chatbot_Base_Wand.read_write_symbol_collector import read_write_symbol_collector

# from tensorflow.keras.models import load_model
# sentiment_model = load_model('D:\\CodingGit_StorageHDD\\model_git\\emotions_classifier\\emotions_classifier.keras')

# -------------------------------------------------------------------------------------------------
class ollama_chatbot_base:
    """ A class for accessing the ollama local serve api via python, and creating new custom agents.
    The ollama_chatbot_class is also used for accessing Speech to Text transcription/Text to Speech Generation methods via a speedy
    low level, command line interface and the Tortoise TTS model.
    """

    # -------------------------------------------------------------------------------------------------
    def __init__(self, ):
        """ a method for initializing the class """
        # Connect api
        self.url = "http://localhost:11434/api/chat"
        # Setup chat_history
        self.headers = {'Content-Type': 'application/json'}
        self.chat_history = []
        self.llava_history = []
        # Default Agent Voice Reference
        self.voice_name = "C3PO"
        # Default conversation name
        self.save_name = "default"
        self.load_name = "default"

        #TODO ADD FILE PATH COLLECTOR, MANAGER, PARSER & a developer_tools.txt to house said paths.
        self.current_dir = os.getcwd()
        self.parent_dir = os.path.abspath(os.path.join(self.current_dir, os.pardir))
        self.ignored_agents = os.path.join(self.parent_dir, "AgentFiles\\Ignored_Agents\\") 
        self.conversation_library = os.path.join(self.parent_dir, "AgentFiles\\pipeline\\conversation_library")
        self.default_conversation_path = os.path.join(self.parent_dir, f"AgentFiles\\pipeline\\conversation_library\\{self.user_input_model_select}\\{self.save_name}.json")
        self.llava_library = os.path.join(self.parent_dir, "AgentFiles\\pipeline\\llava_library")

        # TODO developer_tools.txt file for custom path library
        self.model_git = 'D:\\CodingGit_StorageHDD\\model_git\\'

        #Initialize tool flags
        self.leap_flag = True # TODO TURN OFF FOR MINECRAFT
        self.listen_flag = False # TODO TURN ON FOR MINECRAFT
        self.latex_flag = False
        self.llava_flag = False # TODO TURN ON FOR MINECRAFT
        self.chunk_flag = False
        self.auto_speech_flag = False #TODO KEEP OFF BY DEFAULT FOR MINECRAFT, TURN ON TO START
        self.splice_flag = False
        self.colors = ollama_commands.get_colors()

    # -------------------------------------------------------------------------------------------------
    def instance_tts_processor(self):
        if not hasattr(self, 'tts_processor_instance') or self.tts_processor_instance is None:
            self.tts_processor_instance = tts_processor_class()
        return self.tts_processor_instance
    
    # -------------------------------------------------------------------------------------------------
    def instance_latex_render(self):
        if not hasattr(self, 'latex_render_instance') or self.latex_render_instance is None:
            self.latex_render_instance = latex_render_class()
        return self.latex_render_instance
    
    # -------------------------------------------------------------------------------------------------
    def select_model(self, user_input_model_select):
        self.user_input_model_select = user_input_model_select
        return user_input_model_select

    # -------------------------------------------------------------------------------------------------
    def voice_command_select_filter(self, user_input_prompt):
        """ a method for managing the voice command selection
            Args: user_input_prompt
            Returns: user_input_prompt
        """ 
        user_input_prompt = re.sub(r"activate swap", "/swap", user_input_prompt, flags=re.IGNORECASE)
        user_input_prompt = re.sub(r"activate quit", "/quit", user_input_prompt, flags=re.IGNORECASE)
        user_input_prompt = re.sub(r"activate create", "/create", user_input_prompt, flags=re.IGNORECASE)

        user_input_prompt = re.sub(r"activate listen on", "/listen on", user_input_prompt, flags=re.IGNORECASE)
        user_input_prompt = re.sub(r"activate listen on", "/listen off", user_input_prompt, flags=re.IGNORECASE)

        user_input_prompt = re.sub(r"activate speech on", "/speech on", user_input_prompt, flags=re.IGNORECASE)
        user_input_prompt = re.sub(r"activate speech off", "/speech off", user_input_prompt, flags=re.IGNORECASE)

        user_input_prompt = re.sub(r"activate leap on", "/leap on", user_input_prompt, flags=re.IGNORECASE)
        user_input_prompt = re.sub(r"activate leap off", "/leap off", user_input_prompt, flags=re.IGNORECASE)

        user_input_prompt = re.sub(r"activate latex on", "/latex on", user_input_prompt, flags=re.IGNORECASE)
        user_input_prompt = re.sub(r"activate latex off", "/latex off", user_input_prompt, flags=re.IGNORECASE)

        user_input_prompt = re.sub(r"activate show model", "/show model", user_input_prompt, flags=re.IGNORECASE)

        # Search for the name after 'forward slash voice swap'
        match = re.search(r"(activate voice swap|/voice swap) ([^/.]*)", user_input_prompt, flags=re.IGNORECASE)
        if match:
            self.voice_name = match.group(2)
            self.voice_name = self.tts_processor_instance.file_name_conversation_history_filter(self.voice_name)

        # Search for the name after 'forward slash movie'
        match = re.search(r"(activate movie|/movie) ([^/.]*)", user_input_prompt, flags=re.IGNORECASE)
        if match:
            self.movie_name = match.group(2)
            self.movie_name = self.tts_processor_instance.file_name_conversation_history_filter(self.movie_name)
        else:
            self.movie_name = None

        # Search for the name after 'activate save'
        match = re.search(r"(activate save as|/save as) ([^/.]*)", user_input_prompt, flags=re.IGNORECASE)
        if match:
            self.save_name = match.group(2)
            self.save_name = self.tts_processor_instance.file_name_conversation_history_filter(self.save_name)
            print(f"save_name string: {self.save_name}")
        else:
            self.save_name = None

        # Search for the name after 'activate load'
        match = re.search(r"(activate load as|/load as) ([^/.]*)", user_input_prompt, flags=re.IGNORECASE)
        if match:
            self.load_name = match.group(2)
            self.load_name = self.tts_processor_instance.file_name_conversation_history_filter(self.load_name)
            print(f"load_name string: {self.load_name}")
        else:
            self.load_name = None

        # Search for the name after 'forward slash voice swap'
        match = re.search(r"(activate convert tensor|/convert tensor) ([^\s]*)", user_input_prompt, flags=re.IGNORECASE)
        if match:
            self.tensor_name = match.group(2)

        return user_input_prompt 
    
    # -------------------------------------------------------------------------------------------------
    def command_select(self, command_str):
        """ a method for selecting the command to execute
            Args: command_str
            Returns: command_library[command_str]
        """
        command_library = {
            "/swap": lambda: self.ollama_command_instance.swap(),
            "/voice swap": lambda: self.tts_processor_instance.voice_swap(),
            "/save as": lambda: self.ollama_chatbot_base_instance.save_to_json(),
            "/load as": lambda: self.ollama_chatbot_base_instance.load_from_json(),
            "/write modelfile": lambda: self.model_write_class_instance.write_model_file(),
            "/convert tensor": lambda: self.model_write_class_instance.safe_tensor_gguf_convert(self.tensor_name),
            "/convert gguf": lambda: self.model_write_class_instance.write_model_file_and_run_agent_create_gguf(self.listen_flag, self.model_git),
            "/listen on": lambda: self.flag_manager_instance.listen(True, self.ollama_chatbot_base_instance),
            "/listen off": lambda: self.flag_manager_instance.listen(False, self.ollama_chatbot_base_instance),
            "/leap on": lambda: self.flag_manager_instance.leap(True, self.ollama_chatbot_base_instance),
            "/leap off": lambda: self.flag_manager_instance.leap(False, self.ollama_chatbot_base_instance),
            "/speech on": lambda: self.flag_manager_instance.speech(True, self.ollama_chatbot_base_instance),
            "/speech off": lambda: self.flag_manager_instance.speech(False, self.ollama_chatbot_base_instance),
            "/latex on": lambda: self.flag_manager_instance.latex(True, self.ollama_chatbot_base_instance),
            "/latex off": lambda: self.flag_manager_instance.latex(False, self.ollama_chatbot_base_instance),
            "/command auto on": lambda: self.flag_manager_instance.auto_commands(True, self.ollama_chatbot_base_instance),
            "/command auto off": lambda: self.flag_manager_instance.auto_commands(False, self.ollama_chatbot_base_instance),
            "/llava flow": lambda: self.flag_manager_instance.llava_flow(True),
            "/llava freeze": lambda: self.flag_manager_instance.llava_flow(False),
            "/auto on": lambda: self.flag_manager_instance.auto_speech_set(True),
            "/auto off": lambda: self.flag_manager_instance.auto_speech_set(False),
            "/quit": lambda: self.ollama_command_instance.quit(),
            "/ollama create": lambda: self.ollama_command_instance.ollama_create(self.ollama_chatbot_base_instance),
            "/ollama show": lambda: self.ollama_command_instance.ollama_show_modelfile(self.ollama_chatbot_base_instance),
            "/ollama template": lambda: self.ollama_command_instance.ollama_show_template(self, self.ollama_chatbot_base_instance),
            "/ollama license": lambda: self.ollama_command_instance.ollama_show_license(self.ollama_chatbot_base_instance),
            "/ollama list": lambda: self.ollama_command_instance.ollama_list(self.ollama_chatbot_base_instance),
            "/splice video": lambda: self.data_set_video_process_instance.generate_image_data(),
            "/developer new" : lambda: self.read_write_symbol_collector_instance.developer_tools_generate()
        }

        # Find the command in the command string
        command = next((cmd for cmd in command_library.keys() if command_str.startswith(cmd)), None)

        # If a command is found, split it from the arguments
        if command:
            args = command_str[len(command):].strip()
        else:
            args = None

        # Check if the command is in the library, if not return None
        if command in command_library:
            command_library[command]()
            cmd_run_flag = True
            return cmd_run_flag
        else:
            cmd_run_flag = False
            return cmd_run_flag

    # -------------------------------------------------------------------------------------------------
    def main(self):
        """ a method for managing the current chatbot instance loop
        """
            
        self.flag_manager_instance = flag_manager
        self.ollama_command_instance = ollama_commands
        self.chat_history_instance = json_chat_history
        self.model_write_class_instance = model_write_class
        self.read_write_symbol_collector_instance = read_write_symbol_collector
        self.latex_render_instance = None
        self.data_set_video_process_instance = None
        self.tts_processor_instance = None

        colors = ollama_commands.get_colors()
        screen_shot_flag = False

        # new instance class
        self.ollama_chatbot_base_instance = ollama_chatbot_base
        self.data_set_video_process_instance = data_set_constructor()

        # select agent name
        self.ollama_chatbot_base_instance.user_input_model_select = input(colors["HEADER"] + "<<< PROVIDE AGENT NAME >>> " + colors["OKBLUE"])


        print(colors["OKCYAN"] + "Press space bar to record audio:" + colors["OKCYAN"])
        print(colors["GREEN"] + f"<<< USER >>> " + colors["END"])
        # keyboard.add_hotkey('ctrl+a+d', print, args=('triggered', 'begin speech'))
        # keyboard.add_hotkey('ctrl+a+d', print, args=('triggered', 'begin speech'))

        # def chunk_speach(value):
        #     ollama_chatbot_class.chunk_flag = value
        #     print(f"CHUNK FLAG STATE: {ollama_chatbot_class.listen_flag}")

        keyboard.add_hotkey('ctrl+a+d', self.ollama_chatbot_base_instance.auto_speech_set, args=(True,))
        keyboard.add_hotkey('ctrl+s+w', self.ollama_chatbot_base_instance.chunk_speech, args=(True,))

        while True:
            user_input_prompt = ""
            speech_done = False
            cmd_run_flag = False
            
            # print(f"WHILE LOOP WAY TOP LISTEN: {ollama_chatbot_class.listen_flag}")
            # print(f"WHILE LOOP WAY TOP AUTO: {ollama_chatbot_class.auto_speech_flag}")
            # print(f"WHILE LOOP WAY TOP CHUNK: {ollama_chatbot_class.chunk_flag}")

            if self.ollama_chatbot_base_instance.listen_flag | self.ollama_chatbot_base_instance.auto_speech_flag is True:
                self.tts_processor_instance = self.ollama_chatbot_base_instance.instance_tts_processor()
                # print(f"ENTER IF LISTEN TRUE LISTEN: {ollama_chatbot_class.listen_flag}") 
                # print(f"ENTER IF LISTEN TRUE AUTO: {ollama_chatbot_class.auto_speech_flag}") 
                # print(f"ENTER IF LISTEN TRUE CHUNK: {ollama_chatbot_class.chunk_flag}")
                while self.ollama_chatbot_base_instance.auto_speech_flag is True:  # user holds down the space bar
                    try:
                        # Record audio from microphone
                        audio = self.tts_processor_instance.get_audio(self.ollama_chatbot_base_instance)

                        if self.ollama_chatbot_base_instance.listen_flag is True:
                            # Recognize speech to text from audio
                            user_input_prompt = self.tts_processor_instance.recognize_speech(audio)
                            print(f">>SPEECH RECOGNIZED<< >> {user_input_prompt} <<")
                            speech_done = True
                            self.ollama_chatbot_base_instance.chunk_flag = False
                            print(f"CHUNK FLAG STATE: {self.ollama_chatbot_base_instance.chunk_flag}")
                            self.ollama_chatbot_base_instance.auto_speech_flag = False

                    except sr.UnknownValueError:
                        print(colors["OKCYAN"] + "Google Speech Recognition could not understand audio" + colors["OKCYAN"])
                    except sr.RequestError as e:
                        print(colors["OKCYAN"] + "Could not request results from Google Speech Recognition service; {0}".format(e) + colors["OKCYAN"])
            elif self.ollama_chatbot_base_instance.listen_flag is False:
                print(colors["OKCYAN"] + "Please type your selected prompt:" + colors["OKCYAN"])
                user_input_prompt = input(colors["GREEN"] + f"<<< USER >>> " + colors["END"])
                speech_done = True

            # Use re.sub to replace "forward slash cmd" with "/cmd"
            # print(f"MID ELIF LISTEN: {ollama_chatbot_class.listen_flag}")
            # print(f"MID ELIF AUTO: {ollama_chatbot_class.auto_speech_flag}")
            # print(f"MID ELIF CHUNK: {ollama_chatbot_class.chunk_flag}")

            user_input_prompt = self.ollama_chatbot_base_instance.voice_command_select_filter(user_input_prompt)
            cmd_run_flag = self.ollama_chatbot_base_instance.command_select(user_input_prompt, self.flag_manager_instance, self.ollama_chatbot_base_instance)
            
            # get screenshot
            if self.ollama_chatbot_base_instance.llava_flag is True:
                screen_shot_flag = self.ollama_chatbot_base_instance.get_screenshot()
            # splice videos
            if self.ollama_chatbot_base_instance.splice_flag == True:
                self.data_set_video_process_instance.generate_image_data()

            if cmd_run_flag == False and speech_done == True:
                print(colors["YELLOW"] + f"{user_input_prompt}" + colors["OKCYAN"])

                # Send the prompt to the assistant
                if screen_shot_flag is True:
                    response = self.ollama_chatbot_base_instance.send_prompt(user_input_prompt)
                    screen_shot_flag = False
                else:
                    response = self.ollama_chatbot_base_instance.send_prompt(user_input_prompt)
                
                print(colors["RED"] + f"<<< {self.ollama_chatbot_base_instance.user_input_model_select} >>> " + colors["RED"] + f"{response}" + colors["RED"])

                # Check for latex and add to queue
                if self.ollama_chatbot_base_instance.latex_flag:
                    # Create a new instance
                    latex_render_instance = latex_render_class()
                    latex_render_instance.add_latex_code(response, self.ollama_chatbot_base_instance.user_input_model_select)

                # Preprocess for text to speech, add flag for if text to speech enable handle canche otherwise do /leap or smt
                # Clear speech cache and split the response into sentences for next TTS cache
                if self.ollama_chatbot_base_instance.leap_flag is not None and isinstance(self.ollama_chatbot_base_instance.leap_flag, bool):
                    if self.ollama_chatbot_base_instance.leap_flag != True:
                        self.tts_processor_instance.process_tts_responses(response, self.ollama_chatbot_base_instance.voice_name)
                elif self.ollama_chatbot_base_instance.leap_flag is None:
                    pass
                # Start the mainloop in the main thread
                print(colors["GREEN"] + f"<<< USER >>> " + colors["END"])