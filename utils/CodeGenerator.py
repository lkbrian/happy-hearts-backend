import random
import string


class CodeGenerator:
    def __init__(self, existing_codes=None):
        # Initialize the set of used codes with existing codes if provided
        self.used_codes = set(existing_codes) if existing_codes else set()

    def generate_unique_code(self):
        characters = string.ascii_uppercase + string.digits
        attempt_count = 0
        while True:
            attempt_count += 1
            code = "".join(random.choices(characters, k=6))
            if code in self.used_codes:
                print(f"Repeated code detected: {code} (Attempt #{attempt_count})")
            else:
                self.used_codes.add(code)
                return code




