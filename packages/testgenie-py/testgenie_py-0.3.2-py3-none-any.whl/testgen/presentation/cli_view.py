class CLIView:
    def __init__(self):
        "pass"

    def display_message(self, message: str):
        print(f"[INFO] {message}")

    def display_error(self, error: str):
        print(f"[ERROR] {error}")

    def prompt_input(self, prompt: str) -> str:
        return input(f"{prompt}:> ")