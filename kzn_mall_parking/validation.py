# validation.py
# input checking functions used by main.py

def get_valid_choice(prompt, valid_options):
    while True:
        choice = input(prompt)
        if choice in valid_options:
            return choice
        print(f'Please enter one of: {", ".join(valid_options)}')


def get_valid_number(prompt, low, high):
    while True:
        text = input(prompt)
        text = text.strip()
        if text.isdigit():
            number = int(text)
            if number >= low and number <= high:
                return number
        print("Please enter a number between " + str(low) + " and " + str(high) + ".")


def validate_entry(spaces_free):
    if spaces_free <= 0:
        return "This mall is full - no bays available."
    return None


def validate_text(text, label, minlen):
    # used for both username and password 
    if len(text) < minlen:
        return f"{label} must be at least {minlen} characters long."
    if "," in text:
        return f"{label} cannot contain a comma."
    return ""


def safe_save_record(filename, line):
    try:
        """use append 'a' so that what's saved isn't ovrritten"""
        with open(filename, 'a') as f:
            f.write(line + '\n')
        return True
    except OSError as e:
        print(f'Could not save the record: {e}')
        return False
