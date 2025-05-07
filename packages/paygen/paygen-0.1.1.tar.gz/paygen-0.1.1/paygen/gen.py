import json
import numpy as np
from faker import Faker


def text_payloads(num_samples: int, min_size: int = 100, max_size: int = 1000000) -> list[bytes]:
    """Generate a list of text payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated text payloads as bytes
    """
    fake = Faker()
    payloads = []
    
    # Generate power law distribution of sizes
    alpha = 2.0  # Typical power law exponent for text data
    sizes = np.random.power(alpha, size=num_samples)
    # Scale sizes to our desired range
    sizes = min_size + (max_size - min_size) * sizes
    
    for size in sizes:
        text = ""
        current_size = 0
        while current_size < size:
            text += fake.paragraph() + "\n"
            current_size = len(text.encode('utf-8'))
        payloads.append(text.encode('utf-8'))
        
    return payloads


def binary_payloads(num_samples: int, min_size: int = 100, max_size: int = 1000000) -> list[bytes]:
    """Generate a list of binary payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated binary payloads
    """
    fake = Faker()
    payloads = []
    
    # Generate power law distribution of sizes
    alpha = 2.0  # Typical power law exponent for binary data
    sizes = np.random.power(alpha, size=num_samples)
    # Scale sizes to our desired range
    sizes = min_size + (max_size - min_size) * sizes
    
    for size in sizes:
        data = b""
        current_size = 0
        while current_size < size:
            data += fake.binary(length=min(1024, size - current_size))
            current_size = len(data)
        payloads.append(data)
        
    return payloads


def json_payloads(num_samples: int, min_size: int = 100, max_size: int = 1000000) -> list[bytes]:
    """Generate a list of JSON payloads following a power law distribution.
    
    Args:
        num_samples: Number of payloads to generate
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes
        
    Returns:
        List of generated JSON payloads as bytes
    """
    fake = Faker()
    payloads = []
    
    # Generate power law distribution of sizes
    alpha = 2.0  # Typical power law exponent for JSON data
    sizes = np.random.power(alpha, size=num_samples)
    # Scale sizes to our desired range
    sizes = min_size + (max_size - min_size) * sizes

    def generate_nested_value(depth=0):
        if depth > 3 or fake.boolean(chance_of_getting_true=30):
            choices = [
                lambda: fake.word(),
                lambda: fake.random_number(),
                lambda: fake.boolean(),
                lambda: None,
                lambda: [fake.word() for _ in range(fake.random_int(min=1, max=5))],
            ]
            return fake.random_element(choices)()
        
        nested = {}
        for _ in range(fake.random_int(min=1, max=5)):
            nested[fake.word()] = generate_nested_value(depth + 1)
        return nested

    for size in sizes:
        json_data = {}
        current_size = 0
        while current_size < size:
            key = fake.word()
            json_data[key] = generate_nested_value()
            current_size = len(json.dumps(json_data).encode('utf-8'))
        payloads.append(json.dumps(json_data).encode('utf-8'))
        
    return payloads