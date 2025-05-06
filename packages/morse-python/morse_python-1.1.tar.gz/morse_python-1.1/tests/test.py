from morse_python import *

# Test the morse to text function
morse_code = ".--. .-. .. -. - -.--. .-..-. .... .. .-..-. -.--.-"
print("Morse to Text:", morse_to_text(morse_code))

# Test the text_to_morse function
python_code = 'print("Hello, World!")'
print("Text to Morse:", text_to_morse(python_code))

# Test the execute_morse_code function
morse_code_for_execution = ".--. .-. .. -. - -.--. .-..-. .... .. .-..-. -.--.-"
print("Execute Morse Code output:")
execute_morse_code(morse_code_for_execution)

# Test the play_morse_code function
play_morse_code("... --- ...")