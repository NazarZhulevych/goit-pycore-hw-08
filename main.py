from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # Зберігає об'єкт Name у атрибуті name (успадковано від Field)
    def __init__(self, value):
        super().__init__(value)
        # self.name = value  # для явної відповідності опису

class Phone(Field):
    # Зберігає об'єкт Phone у атрибуті value та реалізує валідацію
    def __init__(self, value):
        if self._validate(value):
            super().__init__(value)
        else:
            raise ValueError("Phone number must contain exactly 10 digits.")

    def _validate(self, value):
        if str(value).isdigit() and len(str(value)) == 10:
            return True
        else:
            return False
        #digits = ''.join(filter(str.isdigit, str(value)))
        #return len(digits) == 10

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self.value = value

    @staticmethod
    def date_to_string(date_obj):
        """Convert a datetime.date object to a string (YYYY.MM.DD)."""
        return date_obj.strftime("%Y.%m.%d")

    @staticmethod
    def find_next_weekday(start_date, weekday=0):
        """Find the next occurrence of a specific weekday (default: Monday)."""
        days_ahead = (weekday - start_date.weekday()) % 7
        days_ahead = days_ahead if days_ahead > 0 else 7
        return start_date + timedelta(days=days_ahead)
    
    @staticmethod
    def adjust_for_weekend(birthday):
        """Move birthdays that fall on weekends to the next Monday."""
        if birthday.weekday() >= 5:  # Saturday (5) or Sunday (6)
            return Birthday.find_next_weekday(birthday, 0)  # Move to next Monday
        return birthday  # Return unchanged if it's a weekday

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def find_phone(self, target_phone):
        for i in self.phones:
         if i.value == target_phone:
          return i 

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Phone number '{phone}' not found.")

    def edit_phone(self, old_phone, new_phone):
        if self.find_phone(old_phone):
            self.add_phone(new_phone)
            self.remove_phone(old_phone)
        else:
            raise ValueError(f"Phone number '{old_phone}' not found.")
    
    def add_birthday(self, birthdate):
        self.birthday = Birthday(birthdate)
       
    # Реалізовано зберігання об'єкта Name в атрибуті name.
    # Реалізовано зберігання списку об'єктів Phone в атрибуті phones.
    # Реалізовано метод для додавання - add_phone .На вхід подається рядок, який містить номер телефона.
    # Реалізовано метод для видалення - remove_phone. На вхід подається рядок, який містить номер телефона.
    # Реалізовано метод для редагування - edit_phone. На вхід подається два аргумента - рядки, які містять старий номер телефона та новий. У разі некоректності вхідних даних метод має завершуватись помилкою ValueError.
    # Реалізовано метод для пошуку об'єктів Phone - find_phone. На вхід подається рядок, який містить номер телефона. Метод має повертати або об’єкт Phone, або None .

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def __str__(self):
        if not self.data:
            return ("Address book is empty.")
        result = []
        for key, record in self.data.items():
            birthday = record.birthday.value if record.birthday else "N/A"
            result.append(f"{key}: {record}. Birthdate: {birthday}")
        return '\n'.join(result)

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name) 
        
    def delete(self, name: str):
        del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday_date.replace(year=today.year)

            # If birthday already passed, consider next year
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            # Adjust for weekend
            congratulation_date = Birthday.adjust_for_weekend(birthday_this_year)
            days_until_birthday = (congratulation_date - today).days

            if 0 <= days_until_birthday <= days:
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": Birthday.date_to_string(congratulation_date)
                })

        return upcoming_birthdays
        """
        Це буде метод, який визначає контакти, у яких день народження припадає вперед на 7 днів включаючи поточний день. 
        Метод має повертати список словників. Кожен словник містить два значення - ім’я з ключем "name", та дата привітання з ключем "birthday”. 
        Не забудьте врахувати перенесення дати на наступний робочий день, якщо день народження припадає на вихідний.
        """
        
    # Має наслідуватись від класу UserDict .
    # Реалізовано метод add_record, який додає запис до self.data. Записи Record у AddressBook зберігаються як значення у словнику. В якості ключів використовується значення Record.name.value.
    # Реалізовано метод find, який знаходить запис за ім'ям. На вхід отримує один аргумент - рядок, якій містить ім’я. Повертає об’єкт Record, або None, якщо запис не знайден.
    # Реалізовано метод delete, який видаляє запис за ім'ям.
    # Реалізовано магічний метод __str__ для красивого виводу об’єкту класу AddressBook .

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if len(args) < 1:
                raise ValueError("Name too short")
            return result
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Input error: Missing required elements."
        except KeyError:
            return "Input error: Key not found."
        except AttributeError as e:
            return "Contact does not exist"
        except Exception as e:
            return f"Unexpected error: {e}"
    return wrapper

@input_error
def parse_input(user_input):
    try:
        parts = user_input.split()
        if not parts:
            return "", []  
        cmd, args = parts[0], parts[1:]  
        return cmd.strip().lower(), args
    except Exception as e:
        return "", []

@input_error
def phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"'{name}' numbers: {', '.join(str(phone.value) for phone in record.phones)}"

@input_error
def change(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    record.edit_phone(old_phone, new_phone)
    return message

@input_error
def add_birthday(args, book: AddressBook):
    name, birthdate = args
    record = book.find(name)
    record.add_birthday(birthdate)
    return f"Birthday for '{name}' added: {birthdate}."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record.birthday is None:
        return f"Contact '{name}' has no birthday set."
    else:
        return f"Birthday for '{name}': {record.birthday.value}."

@input_error
def birthdays(book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    result = []
    for item in upcoming:
        result.append(f"{item['name']}: {item['congratulation_date']}")
    return "\n".join(result)

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

def main():
    book = AddressBook()
    """
    ivan_record = Record("Ivan")
    ivan_record.add_phone("1234567890")
    ivan_record.add_birthday("01.01.1999")
    book.add_record(ivan_record)

    jane_record = Record("jane")
    jane_record.add_phone("9876543210")
    jane_record.add_birthday("01.01.1990")
    book.add_record(jane_record)
    """
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change(args, book))

        elif command == "phone":
            print(phone(args, book))

        elif command == "all":
            print(book)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

"""

john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")

add Ivan 1234567890
add-birthday Ivan 01.01.1999
change Ivan 1234567890 1112223333
add Ivan 1234567890
phone Ivan
add jane 9876543210
add-birthday jane 01.01.1990
show-birthday jane

birthdays

book.add_record(john_record)

jane_record = Record("Jane")
jane_record.add_phone("9876543210")
book.add_record(jane_record)

# Виведення всіх записів у книзі
     
print(book)
#print(john_record)

# Знаходження та редагування телефону для John
john = book.find("John")
john.edit_phone("1234567890", "1112223333")

print(john)

found_phone = john.find_phone("5555555555")
print(f"{john.name}: {found_phone}")

book.delete("Jane")

"""

if __name__ == "__main__":
    main()