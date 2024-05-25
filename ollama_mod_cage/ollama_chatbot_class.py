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

from tts_processor_class import tts_processor_class
from directory_manager_class import directory_manager_class
from latex_render_class import latex_render_class
from unsloth_train_class import unsloth_train_class

# from tensorflow.keras.models import load_model
# sentiment_model = load_model('D:\\CodingGit_StorageHDD\\model_git\\emotions_classifier\\emotions_classifier.keras')

class ollama_chatbot_class:
    """ A class for accessing the ollama local serve api via python, and creating new custom agents.
    The ollama_chatbot_class is also used for accessing Speech to Text transcription/Text to Speech Generation methods via a speedy
    low level, command line interface and the Tortoise TTS model.
    """
    def __init__(self, user_input_model_select):
        """ a method for initializing the class
        """
        """ a method for initializing the class
        """
        # User Input
        self.user_input_model_select = user_input_model_select
        # Connect api
        self.url = "http://localhost:11434/api/chat"
        # Setup chat_history
        self.headers = {'Content-Type': 'application/json'}
        self.chat_history = []
        self.llava_history = []
        # Default Agent Voice Reference
        self.voice_name = "Amy_en"
        # Default conversation name
        self.save_name = "default"
        self.load_name = "default"
        self.current_dir = os.getcwd()
        self.parent_dir = os.path.abspath(os.path.join(self.current_dir, os.pardir))
        self.ignored_agents = os.path.join(self.parent_dir, "AgentFiles\\Ignored_Agents\\") 
        self.conversation_library = os.path.join(self.parent_dir, "AgentFiles\\pipeline\\conversation_library")
        self.default_conversation_path = os.path.join(self.parent_dir, f"AgentFiles\\pipeline\\conversation_library\\{self.user_input_model_select}\\{self.save_name}.json")
        self.llava_library = os.path.join(self.parent_dir, "AgentFiles\\pipeline\\llava_library")

        # TODO developer_tools.txt file for custom path library
        self.model_git = 'D:\\CodingGit_StorageHDD\\model_git\\'

        #Initialize tool flags
        self.leap_flag = True # IF TRUE=Turn off audio generation- important setting amos #
        self.listen_flag = True # IF FALSE=SPEECH TO TEXT - important setting amos #
        self.latex_flag = False
        self.llava_flag = False

    def send_prompt(self, user_input_prompt):
        """ a method for prompting the model
            args: user_input_prompt, user_input_model_select, search_google
            returns: none
        """
        self.chat_history.append({"role": "user", "content": user_input_prompt})
        self.screenshot_path = os.path.join(self.llava_library, "screenshot.png")
        # Get the llava response and append it to the chat history only if an image is provided
        if self.llava_flag is True:
            # Load the screenshot and convert it to a base64 string
            with open(f'{self.screenshot_path}', 'rb') as f:
                user_screenshot_raw2 = base64.b64encode(f.read()).decode('utf-8')
                self.user_screenshot_raw = user_screenshot_raw2
            llava_response = self.llava_prompt(user_screenshot_raw2)
            self.chat_history.append({"role": "assistant", "content": f"LLAVA_DATA: {llava_response}"})

        try:
            response = ollama.chat(model=self.user_input_model_select, messages=(self.chat_history), stream=False )
            if isinstance(response, dict) and "message" in response:
                llama_response = response.get("message")
                self.chat_history.append(llama_response)
                return llama_response["content"]
            else:
                return "Error: Response from model is not in the expected format"
        except Exception as e:
            return f"Error: {e}"

    
    def llava_prompt(self, user_screenshot_raw2):
        """ a method for prompting the model
            args: user_input_prompt, user_input_model_select, search_google
            returns: none
        """
        message = {"role": "user", "content": "what objects are in this screen share image?"}
        if user_screenshot_raw2 is not None:
            # Assuming user_input_image is a base64 encoded image
            message["images"] = [user_screenshot_raw2]
        self.llava_history.append(message["content"])

        try:
            response = ollama.chat(model="llava", messages=(self.llava_history), stream=False )
        except Exception as e:
            return f"Error: {e}"

        if "message" in response:
            llama_response = response.get("message")
            self.llava_history.append(llama_response)
            print(f"LLAVA HISTORY: {self.llava_history}")

            # Keep only the last 2 responses in llava_history
            self.llava_history = self.llava_history[-2:]

            return llama_response["content"]
        else:
            return "Error: Response from model is not in the expected format"
        
    def write_model_file_and_run_agent_create_ollama(self, listen_flag):
        """ a method to automatically generate a new agent via commands
            args: listen_flag
            returns: none
        """
        # collect agent data with stt or ttt
        if listen_flag == False:  # listen_flag is False, use speech recognition
            print("Press space bar to record the new agent's agent name.")
            while not keyboard.is_pressed('space'):  # wait for space bar press
                time.sleep(0.1)
            # Now start recording
            try:
                mic_audio = tts_processor_instance.get_audio()
                self.user_create_agent_name = tts_processor_instance.recognize_speech(mic_audio)
                self.user_create_agent_name = tts_processor_instance.file_name_conversation_history_filter(self.user_create_agent_name)
            except sr.UnknownValueError:
                print(OKCYAN + "Google Speech Recognition could not understand audio" + OKCYAN)
            except sr.RequestError as e:
                print(OKCYAN + "Could not request results from Google Speech Recognition service; {0}".format(e) + OKCYAN)

            print("Press space bar to record the new agent's temperature.")
            while not keyboard.is_pressed('space'):  # wait for space bar press
                time.sleep(0.1)
            # Now start recording
            try:
                mic_audio = tts_processor_instance.get_audio()
                user_input_temperature = tts_processor_instance.recognize_speech(mic_audio)
            except sr.UnknownValueError:
                print(OKCYAN + "Google Speech Recognition could not understand audio" + OKCYAN)
            except sr.RequestError as e:
                print(OKCYAN + "Could not request results from Google Speech Recognition service; {0}".format(e) + OKCYAN)

            print("Press space bar to record the new agent's system prompt.")
            while not keyboard.is_pressed('space'):  # wait for space bar press
                time.sleep(0.1)
            # Now start recording
            try:        
                mic_audio = tts_processor_instance.get_audio()
                system_prompt = tts_processor_instance.recognize_speech(mic_audio)
            except sr.UnknownValueError:
                print(OKCYAN + "Google Speech Recognition could not understand audio" + OKCYAN)
            except sr.RequestError as e:
                print(OKCYAN + "Could not request results from Google Speech Recognition service; {0}".format(e) + OKCYAN)

        elif listen_flag == True:  # listen_flag is True, use text input
            self.user_create_agent_name = input(WARNING + "<<< PROVIDE NEW AGENT NAME TO CREATE >>> " + OKBLUE)
            user_input_temperature = input(WARNING + "<<< PROVIDE NEW AGENT TEMPERATURE (0.1 - 5.0) >>> " + OKBLUE)
            system_prompt = input(WHITE + "<<< PROVIDE SYSTEM PROMPT >>> " + OKBLUE)

        model_create_dir = os.path.join(self.ignored_agents, f"{self.user_create_agent_name}")
        model_create_file = os.path.join(self.ignored_agents, f"{self.user_create_agent_name}\\modelfile")

        try:
            # Create the new directory
            os.makedirs(model_create_dir, exist_ok=True)
            # Get current model template data
            self.current_model_template()
            # Create the text file
            with open(model_create_file, 'w') as f:
                f.write(f"FROM {self.user_input_model_select}\n")
                f.write(f"#temperature higher -> creative, lower -> coherent\n")
                f.write(f"PARAMETER temperature {user_input_temperature}\n")
                f.write(f"\n#Set the system prompt\n")
                f.write(f"SYSTEM \"\"\"\n{system_prompt}\n\"\"\"\n")
                f.write(f"TEMPLATE \"\"\"\n{self.template}\n\"\"\"\n")

            # Execute create_agent_cmd
            self.create_agent_cmd(self.user_create_agent_name, 'create_agent_automation_ollama.cmd')
            return
        except Exception as e:
            return f"Error creating directory or text file: {str(e)}"

    def write_model_file_and_run_agent_create_gguf(self, listen_flag, model_git):
            """ a method to automatically generate a new agent via commands
                args: none
                returns: none
            """
            self.model_git = model_git
            # collect agent data with stt or ttt
            if listen_flag == False:  # listen_flag is False, use speech recognition
                print("Press space bar to record the new agent's agent name.")
                while not keyboard.is_pressed('space'):  # wait for space bar press
                    time.sleep(0.1)
                # Now start recording
                try:
                    mic_audio = tts_processor_instance.get_audio()
                    self.user_create_agent_name = tts_processor_instance.recognize_speech(mic_audio)
                    self.user_create_agent_name = tts_processor_instance.file_name_conversation_history_filter(self.user_create_agent_name)
                except sr.UnknownValueError:
                    print(OKCYAN + "Google Speech Recognition could not understand audio" + OKCYAN)
                except sr.RequestError as e:
                    print(OKCYAN + "Could not request results from Google Speech Recognition service; {0}".format(e) + OKCYAN)

                print("Press space bar to record the new agent's temperature.")
                while not keyboard.is_pressed('space'):  # wait for space bar press
                    time.sleep(0.1)
                # Now start recording
                try:
                    mic_audio = tts_processor_instance.get_audio()
                    user_input_temperature = tts_processor_instance.recognize_speech(mic_audio)
                except sr.UnknownValueError:
                    print(OKCYAN + "Google Speech Recognition could not understand audio" + OKCYAN)
                except sr.RequestError as e:
                    print(OKCYAN + "Could not request results from Google Speech Recognition service; {0}".format(e) + OKCYAN)

                print("Press space bar to record the new agent's system prompt.")
                while not keyboard.is_pressed('space'):  # wait for space bar press
                    time.sleep(0.1)
                # Now start recording
                try:        
                    mic_audio = tts_processor_instance.get_audio()
                    system_prompt = tts_processor_instance.recognize_speech(mic_audio)
                except sr.UnknownValueError:
                    print(OKCYAN + "Google Speech Recognition could not understand audio" + OKCYAN)
                except sr.RequestError as e:
                    print(OKCYAN + "Could not request results from Google Speech Recognition service; {0}".format(e) + OKCYAN)

            elif listen_flag == True:  # listen_flag is True, use text input
                self.converted_gguf_model_name = input(WARNING + "<<< PROVIDE SAFETENSOR CONVERTED GGUF NAME (without .gguf) >>> " + OKBLUE)
                self.user_create_agent_name = input(WARNING + "<<< PROVIDE NEW AGENT NAME TO CREATE >>> " + OKBLUE)
                user_input_temperature = input(WARNING + "<<< PROVIDE NEW AGENT TEMPERATURE (0.1 - 5.0) >>> " + OKBLUE)
                system_prompt = input(WHITE + "<<< PROVIDE SYSTEM PROMPT >>> " + OKBLUE)

            model_create_dir = os.path.join(self.ignored_agents, f"{self.user_create_agent_name}")
            model_create_file = os.path.join(self.ignored_agents, f"{self.user_create_agent_name}\\modelfile")
            self.gguf_path_part = os.path.join(self.model_git, "converted")
            self.gguf_path = os.path.join(self.gguf_path_part, f"{self.converted_gguf_model_name}.gguf")
            print(f"model_git: {model_git}")
            try:
                # Create the new directory
                os.makedirs(model_create_dir, exist_ok=True)

                # Copy gguf to IgnoredAgents dir
                self.copy_gguf_to_ignored_agents()

                # Create the text file
                with open(model_create_file, 'w') as f:
                    f.write(f"FROM ./{self.converted_gguf_model_name}.gguf\n")
                    f.write(f"#temperature higher -> creative, lower -> coherent\n")
                    f.write(f"PARAMETER temperature {user_input_temperature}\n")
                    f.write(f"\n#Set the system prompt\n")
                    f.write(f"SYSTEM \"\"\"\n{system_prompt}\n\"\"\"\n")
                
                # Execute create_agent_cmd
                self.create_agent_cmd(self.user_create_agent_name, "create_agent_automation_gguf.cmd")
                return
            except Exception as e:
                return f"Error creating directory or text file: {str(e)}"

    def copy_gguf_to_ignored_agents(self):
        """ a method to setup the gguf before gguf to ollama create """
        self.create_ollama_model_dir = os.path.join(self.ignored_agents, self.user_create_agent_name)
        print(self.create_ollama_model_dir)
        print(self.gguf_path)
        print(self.create_ollama_model_dir)
        # Copy the file from self.gguf_path to create_ollama_model_dir
        shutil.copy(self.gguf_path, self.create_ollama_model_dir)
        return
    
    def command_auto_select_list_generate(self):
        """ a method to generate a command list to be executed by the function call model
        """
        return

    def command_function_call_model(self):
        """ a method to call the command list produced by command_auto_select_list_generate
        """
        return
    
    def swap(self):
        """ a method to call when swapping models
        """
        self.chat_history = []
        self.user_input_model_select = input(HEADER + "<<< PROVIDE AGENT NAME TO SWAP >>> " + OKBLUE)
        print(f"Model changed to {self.user_input_model_select}")
        return
    
    def voice_swap(self):
        """ a method to call when swapping voices
        """
        # Search for the name after 'forward slash voice swap'
        print(f"Agent voice swapped to {self.voice_name}")
        print(GREEN + f"<<< USER >>> " + OKGREEN)
        return

    def save_to_json(self):
        """ a method for saving the current agent conversation history
            Args: filename
            Returns: none
        """
        file_save_path_dir = os.path.join(self.conversation_library, f"{self.user_input_model_select}")
        file_save_path_str = os.path.join(file_save_path_dir, f"{self.save_name}.json")
        directory_manager_class.create_directory_if_not_exists(file_save_path_dir)
        
        print(f"file path 1:{file_save_path_dir} \n")
        print(f"file path 2:{file_save_path_str} \n")
        with open(file_save_path_str, "w") as json_file:
            json.dump(self.chat_history, json_file, indent=2)

    def load_from_json(self):
        """ a method for loading the directed conversation history to the current agent, mis matching
        agents and history may be bizarre
            Args: filename
            Returns: none
        """
        # Check if user_input_model_select contains a slash
        if "/" in self.user_input_model_select:
            user_dir, model_dir = self.user_input_model_select.split("/")
            file_load_path_dir = os.path.join(self.conversation_library, user_dir, model_dir)
        else:
            file_load_path_dir = os.path.join(self.conversation_library, self.user_input_model_select)

        file_load_path_str = os.path.join(file_load_path_dir, f"{self.load_name}.json")
        directory_manager_class.create_directory_if_not_exists(file_load_path_dir)
        print(f"file path 1:{file_load_path_dir} \n")
        print(f"file path 2:{file_load_path_str} \n")
        with open(file_load_path_str, "r") as json_file:
            self.chat_history = json.load(json_file)
    
    def listen(self, flag):
        """ a method for changing the listen flag """
        self.listen_flag = flag
        return
    
    def leap(self, flag):
        """ a method for changing the leap flag """
        self.leap_flag = flag
        return
    
    def speech(self, flag):
        """ a method for changing the speech flags """
        self.listen_flag = flag
        self.leap_flag = flag
        return
    
    def latex(self, flag):
        """ a method for changing the latex flag """
        self.latex_flag = flag
        return
    
    def llava_flow(self, flag):
        """ a method for changing the listen flag """
        self.llava_flag = flag
        return
    
    def auto_commands(self, flag):
        """ a method for auto_command flag """
        self.auto_commands_flag = flag
        return
    
    def quit(self):
        """ a method for quitting the program """
        sys.exit()

    def ollama_show_template(self):
        """ a method for getting the model template """
        modelfile_data = ollama.show(f'{self.user_input_model_select}')
        for key, value in modelfile_data.items():
            if key == 'template':
                self.template = value
        return
    
    def ollama_show_license(self):
        """ a method for showing the model license """
        modelfile_data = ollama.show(f'{self.user_input_model_select}')
        for key, value in modelfile_data.items():
            if key == 'license':
                print(RED + f"<<< {self.user_input_model_select} >>> " + OKBLUE + f"{key}: {value}")
        return

    def ollama_show_modelfile(self):
        """ a method for showing the modelfile """
        modelfile_data = ollama.show(f'{self.user_input_model_select}')
        for key, value in modelfile_data.items():
            if key != 'license':
                print(RED + f"<<< {self.user_input_model_select} >>> " + OKBLUE + f"{key}: {value}")
        return

    def ollama_list(self):
        """ a method for showing the ollama model list """
        ollama_list = ollama.list()
        for model_info in ollama_list.get('models', []):
            model_name = model_info.get('name')
            model = model_info.get('model')
            print(RED + f"<<< {self.user_input_model_select} >>> " + OKBLUE + f"{model_name}" + RED + " <<< ")
        return
    
    def ollama_create(self):
        """ a method for running the ollama create command across the current agent """
        ollama_chatbot_class.write_model_file_and_run_agent_create_ollama(self.listen_flag)
        print(GREEN + f"<<< USER >>> " + OKGREEN)
        return
    
    def safe_tensor_gguf_convert(self, safe_tensor_input_name):
        """ a method for converting safetensors to GGUF
            args: safe_tensor_input_name: str
            returns: None
        """
        # Construct the full path
        full_path = os.path.join(self.current_dir, 'safetensors_to_GGUF.cmd')

        # Define the command to be executed
        cmd = f'call {full_path} {self.model_git} {safe_tensor_input_name}'

        # Call the command
        subprocess.run(cmd, shell=True)
        print(RED + f"CONVERTED: {safe_tensor_input_name}" + OKGREEN)
        print(GREEN + f"<<< USER >>> " + OKGREEN)
        return
    
    def create_agent_cmd(self, user_create_agent_name, cmd_file_name):
        """Executes the create_agent_automation.cmd file with the specified agent name.
            Args: 
            Returns: None
        """
        try:
            # Construct the path to the create_agent_automation.cmd file
            batch_file_path = os.path.join(self.current_dir, cmd_file_name)

            # Call the batch file
            subprocess.run(f"call {batch_file_path} {user_create_agent_name}", shell=True)
        except Exception as e:
            print(f"Error executing create_agent_cmd: {str(e)}")

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
            self.voice_name = tts_processor_instance.file_name_conversation_history_filter(self.voice_name)

        # Search for the name after 'forward slash movie'
        match = re.search(r"(activate movie|/movie) ([^/.]*)", user_input_prompt, flags=re.IGNORECASE)
        if match:
            self.movie_name = match.group(2)
            self.movie_name = tts_processor_instance.file_name_conversation_history_filter(self.movie_name)
        else:
            self.movie_name = None

        # Search for the name after 'activate save'
        match = re.search(r"(activate save|/save) ([^/.]*)", user_input_prompt, flags=re.IGNORECASE)
        if match:
            self.save_name = match.group(2)
            self.save_name = tts_processor_instance.file_name_conversation_history_filter(self.save_name)
            print(f"save_name string: {self.save_name}")
        else:
            self.save_name = None

        # Search for the name after 'activate load'
        match = re.search(r"(activate open|/open) ([^/.]*)", user_input_prompt, flags=re.IGNORECASE)
        if match:
            self.load_name = match.group(2)
            self.load_name = tts_processor_instance.file_name_conversation_history_filter(self.load_name)
            print(f"load_name string: {self.load_name}")
        else:
            self.load_name = None

        # Search for the name after 'forward slash voice swap'
        match = re.search(r"(activate convert tensor|/convert tensor) ([^\s]*)", user_input_prompt, flags=re.IGNORECASE)
        if match:
            self.tensor_name = match.group(2)

        return user_input_prompt 
    
    def command_select(self, command_str):
        """ a method for selecting the command to execute
            Args: command_str
            Returns: command_library[command_str]
        """
        command_library = {
            "/swap": lambda: self.swap(),
            "/voice swap": lambda: self.voice_swap(),
            "/save": lambda: self.save_to_json(),
            "/open": lambda: self.load_from_json(),
            "/convert tensor": lambda: self.safe_tensor_gguf_convert(self.tensor_name),
            "/convert gguf": lambda: self.write_model_file_and_run_agent_create_gguf(self.listen_flag, self.model_git),
            "/listen on": lambda: self.listen(True),
            "/listen off": lambda: self.listen(False),
            "/leap on": lambda: self.leap(True),
            "/leap off": lambda: self.leap(False),
            "/speech on": lambda: self.speech(True),
            "/speech off": lambda: self.speech(False),
            "/latex on": lambda: self.latex(True),
            "/latex off": lambda: self.latex(False),
            "/command auto on": lambda: self.auto_commands(True),
            "/command auto off": lambda: self.auto_commands(False),
            "/quit": lambda: self.quit(),
            "/ollama create": lambda: self.ollama_create(),
            "/ollama show": lambda: self.ollama_show_modelfile(),
            "/ollama template": lambda: self.ollama_show_template(),
            "/ollama license": lambda: self.ollama_show_license(),
            "/ollama list": lambda: self.ollama_list(),
            "/llava flow": lambda: self.llava_flow(True),
            "/llava freeze": lambda: self.llava_flow(False)
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
        
    def get_screenshot(self):
        """ a method for taking a screenshot
            args: none
            returns: none
        """
        # Clear the llava_library directory
        files = glob.glob(os.path.join(self.llava_library, '*'))
        for f in files:
            os.remove(f)

        # Take a screenshot using PyAutoGUI
        user_screen = pyautogui.screenshot()

        # Create a path for the screenshot in the llava_library directory
        self.screenshot_path = os.path.join(self.llava_library, 'screenshot.png')

        # Save the screenshot to the file
        user_screen.save(self.screenshot_path)

        # Add a delay to ensure the screenshot is saved before it is read
        time.sleep(1)  # delay for 1 second
        screen_shot_flag = True
        return screen_shot_flag
    
    # def instancer(self, tts_processor_instance, directory_manager_class, unsloth_train_instance, ollama_chatbot_class, latex_render_instance):
    #     self.tts_processor_instance = tts_processor_instance
    #     self.directory_manager_class = directory_manager_class
    #     self.unsloth_train_instance = unsloth_train_instance
    #     self.ollama_chatbot_class = ollama_chatbot_class
    #     self.latex_render_instance = latex_render_instance
    #     return
    
if __name__ == "__main__":

    """ 
    The main loop for the ollama_chatbot_class, utilizing a state machine for user command injection during command line prompting,
    all commands start with /, and are named logically.
    """
    # Used Colors
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    ORANGE = '\033[38;5;208m'

    # Unused Colors
    DARK_GREY = '\033[90m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\x1B[37m'
    
    screen_shot_flag = False

    # instantiate class calls
    tts_processor_instance = tts_processor_class()
    directory_manager_class = directory_manager_class()
    unsloth_train_instance = unsloth_train_class()

    # select agent name
    ollama_chatbot_class.user_input_model_select = input(HEADER + "<<< PROVIDE AGENT NAME >>> " + OKBLUE)
    # new instance class
    ollama_chatbot_class = ollama_chatbot_class(ollama_chatbot_class.user_input_model_select)
    latex_render_instance = None

    # ollama_chatbot_class.instancer(tts_processor_instance, directory_manager_class, unsloth_train_instance, ollama_chatbot_class, latex_render_instance)

    print(OKCYAN + "Press space bar to record audio:" + OKCYAN)
    print(GREEN + f"<<< USER >>> " + END)
    while True:
        user_input_prompt = ""
        speech_done = False
        cmd_run_flag = False
        if ollama_chatbot_class.listen_flag == True:  # listen_flag is True
            print(OKCYAN + "Please type your selected prompt:" + OKCYAN)
            user_input_prompt = input(GREEN + f"<<< USER >>> " + END)
            speech_done = True
        elif ollama_chatbot_class.listen_flag == False:
            while keyboard.is_pressed('space'):  # user holds down the space bar
                try:
                    # Record audio from microphone
                    print(">>AUDIO SENDING<<")
                    audio = tts_processor_instance.get_audio()
                    print(">>AUDIO RECEIVED<<")
                    # Recognize speech to text from audio
                    user_input_prompt = tts_processor_instance.recognize_speech(audio)
                    print(f">>SPEECH RECOGNIZED<< >> {user_input_prompt} <<")
                    speech_done = True
                except sr.UnknownValueError:
                    print(OKCYAN + "Google Speech Recognition could not understand audio" + OKCYAN)
                except sr.RequestError as e:
                    print(OKCYAN + "Could not request results from Google Speech Recognition service; {0}".format(e) + OKCYAN)

        # Use re.sub to replace "forward slash cmd" with "/cmd"
        user_input_prompt = ollama_chatbot_class.voice_command_select_filter(user_input_prompt)
        cmd_run_flag = ollama_chatbot_class.command_select(user_input_prompt)

        if cmd_run_flag == False and speech_done == True:
            print(YELLOW + f"{user_input_prompt}" + OKCYAN)

            # Get Screenshot
            if ollama_chatbot_class.llava_flag is True:
                screen_shot_flag = ollama_chatbot_class.get_screenshot()

            # Send the prompt to the assistant
            if screen_shot_flag is True:
                response = ollama_chatbot_class.send_prompt(user_input_prompt)
                screen_shot_flag = False
            else:
                response = ollama_chatbot_class.send_prompt(user_input_prompt)
            
            print(ORANGE + f"<<< {ollama_chatbot_class.user_input_model_select} >>> " + END + f"{response}" + ORANGE)

            # Check for latex and add to queue
            if ollama_chatbot_class.latex_flag:
                # Create a new instance
                latex_render_instance = latex_render_class()
                latex_render_instance.add_latex_code(response, ollama_chatbot_class.user_input_model_select)

            # Preprocess for text to speech, add flag for if text to speech enable handle canche otherwise do /leap or smt
            # Clear speech cache and split the response into sentences for next TTS cache
            if ollama_chatbot_class.leap_flag is not None and isinstance(ollama_chatbot_class.leap_flag, bool):
                if ollama_chatbot_class.leap_flag != True:
                    tts_processor_instance.process_tts_responses(response, ollama_chatbot_class.voice_name)
            elif ollama_chatbot_class.leap_flag is None:
                pass
            # Start the mainloop in the main thread
            print(GREEN + f"<<< USER >>> " + END)