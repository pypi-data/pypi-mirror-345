import re
import uuid
import random
import string


class Id:
    """
    Id class to represent a unique identifier for a particle.

    """

    @staticmethod
    def uuid(length: int = 8) -> str:
        """
        Generate a UUID string of the specified length.

        """
        return str(uuid.uuid4())[:length]

    @staticmethod
    def random(
        length: int = 8,
        include_letters=True,
        include_numbers=False,
        include_upper=False,
        include_lower=True,
    ) -> str:
        """
        Generate a random string of the specified length.

        """
        if include_letters:
            if include_upper and include_lower:
                alphabet = string.ascii_letters
            elif include_upper:
                alphabet = string.ascii_uppercase
            elif include_lower:
                alphabet = string.ascii_lowercase
            else:
                alphabet = ""
        else:
            alphabet = ""

        if include_numbers:
            alphabet += string.digits

        return "".join(random.choice(alphabet) for _ in range(length))
