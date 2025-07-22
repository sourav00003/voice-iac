from modules.mode_1.voice_handler import get_voice_confirmation


def get_confirmation_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        print(f"{prompt} [Attempt {attempt + 1}/{max_retries}]")
        response = get_voice_confirmation()
        if "yes" in response:
            return True
        elif "no" in response:
            return False
        else:
            print("Invalid response. Please say 'yes' or 'no'.")
    return False  # After all retries