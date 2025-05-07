from s_aes.core import s_aes_encrypt, s_aes_decrypt

def main():
    while True:
        choice = input("\nChoose mode:\n1. Encrypt\n2. Decrypt\n3. Exit\nChoice: ")
        if choice == '3':
            break
            
        if choice not in ['1', '2']:
            print("Invalid choice. Try again.")
            continue

        key_input = input("Enter 16-bit binary key: ")
        if len(key_input) != 16 or not all(bit in '01' for bit in key_input):
            print("Invalid key. Must be 16 binary bits.")
            continue

        text_input = input("Enter 16-bit binary text: ")
        if len(text_input) != 16 or not all(bit in '01' for bit in text_input):
            print("Invalid text. Must be 16 binary bits.")
            continue

        if choice == '1':
            result = s_aes_encrypt(text_input, key_input)
            print(f"Encrypted result: {result}")
        else:
            result = s_aes_decrypt(text_input, key_input)
            print(f"Decrypted result: {result}")

if __name__ == "__main__":
    main()