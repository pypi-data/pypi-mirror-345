def pass_(prompt_text):
    """
    Returns a prompt text string. When used with input(), it will
    capture the user's input but display asterisks (*) instead.
    
    Usage:
        from rescore09 import pass_
        password = input(pass_("Enter your password: "))
        
    Args:
        prompt_text (str): The text prompt to display to the user
        
    Returns:
        str: The prompt text
    """
    # Hook into standard input
    import builtins
    original_input = builtins.input
    
    def masked_input(prompt):
        """Custom input function that masks characters with asterisks"""
        import sys
        import os
        
        print(prompt, end='', flush=True)
        password = ''
        
        if os.name == 'nt':  # Windows
            import msvcrt
            while True:
                char = msvcrt.getch()
                if char in (b'\r', b'\n'):  # Enter key
                    print()
                    break
                elif char == b'\b':  # Backspace
                    if password:
                        password = password[:-1]
                        sys.stdout.write('\b \b')  # Erase the last asterisk
                        sys.stdout.flush()
                elif char and char.decode('utf-8', errors='ignore').isprintable():
                    password += char.decode('utf-8', errors='ignore')
                    sys.stdout.write('*')  # Show asterisk
                    sys.stdout.flush()
        
        # Restore original input function
        builtins.input = original_input
        return password
    
    # Replace input with our masked version
    builtins.input = masked_input
    
    return prompt_text