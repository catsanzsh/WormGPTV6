import tkinter as tk
import requests
import os
import json
import time

class LMStudioWrapper:
    def __init__(self, base_url):
        self.base_url = base_url

    def generate_response(self, prompt, max_tokens):
        url = f"{self.base_url}/v1/engines/default/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "n": 1,
            "stop": None,
            "temperature": 0.7,
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["text"]
        return "No response generated."

class AutonomousAssistantApp:
    def __init__(self, root, lm_studio_wrapper):
        self.root = root
        self.root.title("Autonomous Assistant")
        self.root.geometry("600x600")
        self.lm_studio_wrapper = lm_studio_wrapper
        self.history = []
        self.tasks = []

        self.text_area = tk.Text(root, state='disabled', wrap='word', font=("Arial", 12))
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)

        input_frame = tk.Frame(root)
        input_frame.pack(side='bottom', fill='x', padx=10, pady=10)

        self.user_input = tk.Entry(input_frame, font=("Arial", 12))
        self.user_input.pack(side='left', expand=True, fill='x')
        self.user_input.bind('<Return>', self.send_message)

        send_button = tk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side='right', padx=5)

        self.create_workspace_folder()

    def create_workspace_folder(self):
        self.workspace_folder = "auto_gpt_workspace"
        if not os.path.exists(self.workspace_folder):
            os.makedirs(self.workspace_folder)

    def send_message(self, event=None):
        user_input = self.user_input.get()
        self.user_input.delete(0, tk.END)
        self.display_message("User: " + user_input)
        self.history.append({"role": "user", "content": user_input})

        self.generate_tasks()
        self.execute_tasks()

        response = self.lm_studio_wrapper.generate_response(user_input, max_tokens=100)
        self.display_message("Assistant: " + response)
        self.history.append({"role": "assistant", "content": response})

        self.save_interaction_to_file(user_input, response)

    def generate_tasks(self):
        prompt = "Based on the current conversation context, generate a list of tasks to be executed by the AI assistant. Provide the tasks in JSON format."
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history])
        prompt = f"{context}\n{prompt}"
        response = self.lm_studio_wrapper.generate_response(prompt, max_tokens=200)
        try:
            tasks = json.loads(response)
            self.tasks.extend(tasks)
        except json.JSONDecodeError:
            self.display_message("Failed to generate tasks.")

    def execute_tasks(self):
        for task in self.tasks:
            self.display_message(f"Executing task: {task['name']}")
            time.sleep(1)  # Simulating task execution
            self.display_message(f"Task completed: {task['name']}")
        self.tasks.clear()

    def display_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert('end', message + "\n\n")
        self.text_area.config(state='disabled')
        self.text_area.see('end')

    def save_interaction_to_file(self, prompt, response):
        filename = os.path.join(self.workspace_folder, "interaction_history.txt")
        with open(filename, "a") as file:
            file.write(f"User: {prompt}\n")
            file.write(f"Assistant: {response}\n\n")

if __name__ == "__main__":
    lm_studio_wrapper = LMStudioWrapper(base_url="http://localhost:1234")
    root = tk.Tk()
    app = AutonomousAssistantApp(root, lm_studio_wrapper)
    root.mainloop()
