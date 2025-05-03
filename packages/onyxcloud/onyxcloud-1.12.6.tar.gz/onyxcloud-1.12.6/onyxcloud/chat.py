"""
Fleet Assistant Chat Interface
This module implements a chat interface for interacting with a language translation model.
It provides real-time translation capabilities between human input and an alien language system (obviously the challenge not actual aliens, well we dont think so anyways...).
"""
import sys
import torch
import os
import colorama
import traceback
from colorama import Fore, Style
from importlib.resources import files
from .Utils import *

class ModelExecutor:
    """
    Handles the loading and execution of the language translation model.
    
    Attributes:
        device (torch.device): The device where the model will run (CPU/GPU)
        model: The loaded translation model
        tokenizer: Tokenizer for processing input text
        debug (bool): Flag to enable debug printing
    """

    def __init__(self, debug=False):
        """
        Initialize the ModelExecutor.

        Args:
            model_path (str): Path to the model file
            debug (bool): Enable debug mode if True
        """
        # Ensure paths are setup correctly
        package_model_path = files("onyxcloud").joinpath("model/model")
        self.model_path = str(package_model_path)
        print(Fore.BLUE + Style.BRIGHT + f"\n🔧 Initiating Quantum Core Stabilizer..." + Style.RESET_ALL)
        self.device = get_device()
        self.load_model(self.model_path)
        self.debug = debug

    def debug_print(self, *args, **kwargs):
        """
        Print debug information if debug mode is enabled.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        if self.debug:
            print(*args, **kwargs)

    def load_model(self, model_path):
        """
        Load the model and tokenizer from the specified path.

        Args:
            model_path (str): Path to the model checkpoint

        Raises:
            Exception: If model loading fails
        """
        print(Fore.BLUE + Style.BRIGHT + f"💠 Neural Translation Matrix: Alignment in progress..." + Style.RESET_ALL)
        try: 
            PrepareModel(model_path).stabilize()
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
        try:
            print(Fore.BLUE + Style.BRIGHT + f"🌌 Interstellar Signal Decryptor: Spooling up temporal harmonics..." + Style.RESET_ALL)
            checkpoint = torch.load(model_path, weights_only=False, map_location=torch.device('cpu'))
            self.model = checkpoint['model'].to(self.device)
            self.tokenizer = checkpoint['tokenizer']
            self.model.eval()
            print(Fore.GREEN + Style.BRIGHT + f"\n✅ Hyperwave Neural Decoder online.\n" + Style.RESET_ALL)
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def generate_response(self, prompt, max_length=50, temperature=0.4, top_k=1):
        """
        Generate a response for the given prompt using the loaded model.

        Returns:
            str: Generated response text
        """
        generator = Generator(self.model, self.tokenizer)
        generated_text = generator.generate(
            max_tokens_to_generate=max_length,
            prompt=prompt,
            temperature=temperature,
            sampling_strategy="top_k",
            top_k=top_k,
            padding_token=self.tokenizer.character_to_token('<pad>')
        )
        output = generated_text.replace('<pad>', '').replace(prompt, '')
        return output


def chat(max_length=50, temperature=0.4, top_k=1):
    """
    Main function that runs the chat interface.
    Handles user input and model responses in an interactive loop.
    """
    ModelUpdate()
    colorama.init(autoreset=True, convert=True)
    executor = ModelExecutor()
    # Display welcome messages
    print(Fore.YELLOW + "-" * 50 + Style.RESET_ALL)
    print(Fore.CYAN + Style.BRIGHT + "🚀 Welcome aboard, Inspector!")
    print(Fore.CYAN + Style.BRIGHT + "\n🤖 I am NOMI, your Neural Operations & Multilingual Interface\n   here to bridge communication with the OnyxCloud fleet.")    
    print(Fore.YELLOW + Style.BRIGHT + "\n⚠️  Advisory: Subspace linguistic algorithms are in preliminary phases.\n   Translations are severely hindered due to alien signal complexity!" + Style.RESET_ALL)
    print(Fore.MAGENTA + "\nType 'exit' to exit the chat at any time." + Style.RESET_ALL)
    print(Fore.YELLOW + "-" * 50 + Style.RESET_ALL)

    # Main chat loop
    while True:
        try:
            user_input = input(Fore.LIGHTBLUE_EX + Style.BRIGHT + "\nYou: " + Style.RESET_ALL)
            exit_prompts = ['quit', 'bye', 'exit']

            if user_input.strip().lower() in exit_prompts:
                print(Fore.GREEN + "\n🔚 Disengaging neural link. Safe travels!" + Style.RESET_ALL)
                break
            p_val = plot(user_input)
            if p_val:
                response = p_val
            else:
                response = executor.generate_response(user_input, max_length, temperature, top_k)
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"\nBot: {response}" + Style.RESET_ALL)

        except KeyboardInterrupt:
            print(Fore.RED + "\n\n⚠️  Signal Interrupted!" + Style.RESET_ALL)
            break
        except Exception as e:
            print(Fore.GREEN + Style.BRIGHT + "\nBot: ...Hmmmm you seemm to be mre advanced than I thout!" + Style.RESET_ALL)
