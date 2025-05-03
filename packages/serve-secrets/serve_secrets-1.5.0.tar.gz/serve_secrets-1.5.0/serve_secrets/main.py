import keyring
import pyperclip

def store_api_key(service_name, api_key):
    """Store an API key in the system's password manager."""
    keyring.set_password(service_name, "api_key", api_key)
    print(f"API key for {service_name} stored successfully.")

def get_api_key(service_name):
    """Retrieve an API key from the system's password manager."""
    api_key = keyring.get_password(service_name, "api_key")
    if api_key:
        print(f"Retrieved API key for {service_name}: {api_key}")
    else:
        print(f"No API key found for {service_name}.")
    return api_key

def copy_to_clipboard(service_name):
    """Copy the API key to the clipboard."""
    api_key = keyring.get_password(service_name, "api_key")
    if api_key:
        pyperclip.copy(api_key)
        print(f"API key for {service_name} copied to clipboard.")
    else:
        print(f"No API key found for {service_name}.")

def interactive_mode():
    """Run the CLI in interactive mode."""
    print("Welcome to Serve-Secrets Interactive Mode!")
    print("What would you like to do?")
    print("1. Store an API key")
    print("2. Retrieve an API key")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        service_name = input("Enter the service name: ").strip()
        api_key = input("Enter the API key: ").strip()
        store_api_key(service_name, api_key)
    elif choice == "2":
        service_name = input("Enter the service name: ").strip()
        get_api_key(service_name)
    else:
        print("Invalid choice. Exiting interactive mode.")

def main():
    """Entry point for the CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Store and retrieve API keys using the system's password manager.")
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Subparser for storing API keys
    store_parser = subparsers.add_parser("store", help="Store an API key.")
    store_parser.add_argument("service_name", help="The name of the service.")
    store_parser.add_argument("api_key", help="The API key to store.")

    # Subparser for retrieving API keys
    get_parser = subparsers.add_parser("get", help="Retrieve an API key.")
    get_parser.add_argument("service_name", help="The name of the service.")

    parser.add_argument("--cp", metavar="service_name", help="Copy an API key to the clipboard.")

    # Add an interactive mode option
    parser.add_argument("--st", action="store_true", help="Run in interactive mode.")

    args = parser.parse_args()

    if args.st:
        interactive_mode()
    elif args.command == "store":
        store_api_key(args.service_name, args.api_key)
    elif args.command == "get":
        get_api_key(args.service_name)
    elif args.cp:
        copy_to_clipboard(args.cp)
    else:
        parser.print_help()

# Keep the __main__ block for direct execution
if __name__ == "__main__":
    main()