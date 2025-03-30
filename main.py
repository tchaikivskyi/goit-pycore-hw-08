import pickle 
from datetime import datetime, timedelta

class Record:
    def __init__(self, name):
        self.name = name
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if phone is None:
            raise ValueError("Phone is required field.")
        self.phones.append(phone)

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        if old_phone not in self.phones:
            raise ValueError("Phone number not found.")
        if new_phone is None:
            raise ValueError("Phone is required field.")
        index = self.phones.index(old_phone)
        self.phones[index] = new_phone

    def add_birthday(self, birthday):
        try:
            datetime.strptime(birthday, '%d.%m.%Y')
            self.birthday = birthday
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        phones = '; '.join(self.phones)
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones}{birthday}"

class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if not record.birthday:
                continue
                
            birthday_date = datetime.strptime(record.birthday, "%d.%m.%Y").date()
            birthday_this_year = birthday_date.replace(year=today.year)
            
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            
            delta_days = (birthday_this_year - today).days
            if 0 <= delta_days <= 7:
                if birthday_this_year.weekday() in [5, 6]:
                    birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
                
                upcoming_birthdays.append({
                    "name": record.name,
                    "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")
                })
        
        return upcoming_birthdays

    @staticmethod
    def input_error(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyError:
                return "Contact not found."
            except ValueError as e:
                return str(e) if str(e) else "Invalid input. Please follow the command format."
            except IndexError:
                return "Invalid input. Make sure to provide the correct number of arguments."
            except AttributeError:
                return "Contact doesn't have this attribute."
        return inner
    
    @staticmethod
    def load_from_file(filename="addressbook.pkl"):
        print('load_from_file')
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()
        
    def save_to_file(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @input_error
    def add_contact(self, args):
        if len(args) < 2:
            raise ValueError("Provide name and at least one phone number.")
        name, phone, *_ = args
        record = self.find(name)
        message = "Contact updated."
        if record is None:
            record = Record(name)
            self.add_record(record)
            message = "Contact added."
        if phone:
            record.add_phone(phone)
        return message

    @input_error
    def change_contact(self, args):
        if len(args) != 3:
            raise ValueError("Provide name, old phone, and new phone.")
        name, old_phone, new_phone = args
        record = self.find(name)
        if record:
            record.edit_phone(old_phone, new_phone)
            return "Contact updated."
        else:
            raise KeyError

    @input_error
    def show_phone(self, args):
        if len(args) != 1:
            raise ValueError("Provide name.")
        name = args[0]
        record = self.find(name)
        if record:
            return f"{name}: {', '.join(record.phones)}"
        else:
            raise KeyError

    @input_error
    def show_all(self):
        if not self.data:
            return "No contacts saved."
        return "\n".join(str(record) for record in self.data.values())

    @input_error
    def add_birthday(self, args):
        if len(args) != 2:
            raise ValueError("Provide name and birthday in DD.MM.YYYY format.")
        name, birthday = args
        record = self.find(name)
        if record:
            record.add_birthday(birthday)
            return "Birthday added."
        else:
            raise KeyError

    @input_error
    def show_birthday(self, args):
        if len(args) != 1:
            raise ValueError("Provide name.")
        name = args[0]
        record = self.find(name)
        if record and record.birthday:
            return f"{name} birthday is: {record.birthday}"
        elif record:
            return f"{name} doesn't have a birthday set."
        else:
            raise KeyError

    @input_error
    def get_birthdays(self):
        upcoming = self.get_upcoming_birthdays()
        if not upcoming:
            return "No upcoming birthdays in the next week."
        return "\n".join(
            f"{entry['name']}: congratulate on {entry['congratulation_date']}"
            for entry in upcoming
        )

def parse_input(user_input):
    if not user_input.strip():
        return None, []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def main():
    book = AddressBook.load_from_file()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue
        
        command, args = parse_input(user_input)
        if command is None:
            continue
        
        if command in ["close", "exit"]:
            book.save_to_file()
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(book.add_contact(args))
        elif command == "change":
            print(book.change_contact(args))
        elif command == "phone":
            print(book.show_phone(args))
        elif command == "all":
            print(book.show_all())
        elif command == "add-birthday":
            print(book.add_birthday(args))
        elif command == "show-birthday":
            print(book.show_birthday(args))
        elif command == "birthdays":
            print(book.get_birthdays())
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()