# main.py - run this file to start the system
# handles all the menus, calls out to file_handler/pricing/validation for the rest

from datetime import datetime

import file_handler
import pricing
import validation
import random

TIME_FORMAT = "%Y-%m-%d %H:%M"


def main():

    file_handler.setup_files()
    print("=" * 50)
    print("   KwaZulu-Natal Mall Parking Management System")
    print("=" * 50)

    while True:

        # main menu loop, keeps going until they pick exit
        print("\nMAIN MENU")
        print("1. Log in")
        print("2. Register as a new driver")
        print("3. Exit program")
        choice = validation.get_valid_number("Enter your choice (1-3): ", 1, 3)

        if choice == 3:
            print("Thank you for using the system. Goodbye!")
            break

        if choice == 1:
            user = login()
        else:
            user = register_customer()

        if user is not None:
            role = user[file_handler.USER_ROLE]
            print(f"Login successful. Welcome, {user[file_handler.USER_NAME]} ({role}).")
            open_role_menu(user)


""""Fetches the current time and formats it as a string in the expected format."""
def now_text():
    return datetime.now().strftime(TIME_FORMAT)


def minutes_between(start_text, end_text):
    start = datetime.strptime(start_text, TIME_FORMAT)
    end = datetime.strptime(end_text, TIME_FORMAT)
    seconds = (end - start).total_seconds()
    return int(seconds // 60)



def ask_new_password():
    while True:
        password = input("Choose a password: ").strip()
        error = validation.validate_text(password, "Password", 4)
        if error != "":
            print("Error: " + error)
            continue
        again = input("Type the password again: ")
        if again == password:
            return password
        print("Error: the two passwords do not match. Please try again.")


def ask_new_username():

    while True:
        username = input("Choose a username: ").strip()
        error = validation.validate_text(username, "Username", 3)
        if error == "" and file_handler.find_user(username) is not None:
            error = "That username is already taken. Please choose another one."
        if error == "":
            return username

        print("Error: " + error)


def register_customer():
    print("\n--- Register a new driver account ---")
    username = ask_new_username()
    password = ask_new_password()


    file_handler.add_user(username, password, "customer")
    print(f"Success: account '{username}' has been created.")
    return file_handler.find_user(username)


def login():
    print("\n--- Log in ---")
    attempts = 3
    while attempts > 0:
        username = input("Username: ").strip()
        password = input("Password: ")
        user = file_handler.find_user(username)
        if user is None:
            error = "no account exists with that username"
        elif user[file_handler.USER_PASS] != password:
            error = "that password is incorrect"
        else:
            return user
        attempts = attempts - 1
        if attempts > 0:
            print(f"Error: {error}. {attempts} attempt(s) left.")
    print("Error: too many failed attempts. Returning to the main menu.")
    return None


def calculate_fee(mall_id, minutes):

    mall = file_handler.find_mall(mall_id)
    pricing_type = mall[file_handler.MALL_PRICING]
    return pricing.calculate_fee(pricing_type, minutes)



def register_entry(username, mall_id):

    free = file_handler.spaces_free(mall_id)
    if validation.validate_entry(free) is not None:
        return False
    file_handler.save_new_record(username, mall_id, now_text())
    return True


def register_exit(username, mall_id):

    # works out how long they were parked for, doesn't touch the fee -
    # that part happens back in the menu
    record = file_handler.get_active_record(username, mall_id)
    if record is None:
        return None
    exit_time = now_text()
    minutes = minutes_between(record[file_handler.REC_IN], exit_time)
    return record, exit_time, minutes



def entry_exit_menu(username, mall_id):

    # recalculates free bays every loop so it stays up to date

    while True:
        mall = file_handler.find_mall(mall_id)
        capacity = int(mall[file_handler.MALL_CAPACITY])
        free = file_handler.spaces_free(mall_id)

        print(f"\n-- {mall[file_handler.MALL_NAME]} --")
        print(f"{free} / {capacity} bays free")

        # print(mall)  # was using this to debug the capacity stuff earlier
        print("1. Register entry")
        print("2. Register exit")
        print("3. Back to main menu")
        choice = input("Choose an option: ")

        if choice == "1":
            if register_entry(username, mall_id):
                print("Entry recorded. Enjoy your  shopping!")
            else:
                print("Error:  this mall is full - no bays available right now.")
        elif choice == "2":
            result = register_exit(username, mall_id)
            if result is None:
                print("Error: we have no record of your vehicle entering this mall.")
            else:
                # menu works out the fee itself and then tells file_handler

                # to close off the record - register_exit just did the timing part

                record, exit_time, minutes = result
                fee = calculate_fee(mall_id, minutes)
                file_handler.close_record(record[file_handler.REC_ID], exit_time, fee)
                pricing_type = mall[file_handler.MALL_PRICING]

                print("Exit recorded.")
                print(f"Parking duration: {minutes} minute(s)")
                print(f"Pricing type: {pricing_type}")
                print(f"Amount due: R{fee:.2f}")
                print("Please pay from the main menu before you leave.")
        elif choice == "3":
            break
        else:
            print("Please enter 1, 2 or 3.")


def parking_status(username, mall_id):

    return file_handler.get_active_record(username, mall_id)

def view_fee(username, mall_id):

    unpaid = file_handler.get_unpaid_records(username, mall_id)
    if len(unpaid) == 0:
        return None
    return unpaid[0]


def make_payment(username, mall_id):

    record = view_fee(username, mall_id)
    if record is None:
        return None
    amount = float(record[file_handler.REC_FEE])
    print("Processing payment...")
    file_handler.save_payment(record[file_handler.REC_ID], amount, now_text())
    return amount

def payment_menu(username, mall_id):

    # shows the amount + pricing type before asking them to confirm, like

    # the brief said to
    record = view_fee(username, mall_id)
    if record is None:
        print("You have no outstanding parking charges at this mall.")
        return

    mall = file_handler.find_mall(mall_id)
    print(f"\nOutstanding charge: R{float(record[file_handler.REC_FEE]):.2f} "
          f"(pricing type: {mall[file_handler.MALL_PRICING]})")
    print(f"For your visit on {record[file_handler.REC_IN]}")
    answer = validation.get_valid_choice("Confirm payment? (y/n): ", ["y", "n"])
    # print("answer was:", answer)

    if answer == "y":
        amount = make_payment(username, mall_id)
        print("Payment confirmed: R" + str(round(amount, 2)) + " paid. Thank you!")
    else:
        print("Payment cancelled.")


def view_history(username):
    records = file_handler.get_records_for_user(username)
    payments = file_handler.get_payments_for_user(username)

    print("\n--- Your parking history ---")
    if len(records) == 0:
        print("No parking history yet.")
    for record in records:
        exit_text = record[file_handler.REC_OUT]
        if exit_text == '':
            exit_text = "still parked"
        print(f"Record {record[file_handler.REC_ID]} | "
              f"{file_handler.mall_name(record[file_handler.REC_MALL])} | "
              f"In: {record[file_handler.REC_IN]} | Out: {exit_text} | "
              f"Fee: R{float(record[file_handler.REC_FEE]):.2f}")

    print("\n--- Your payment history ---")
    if len(payments) == 0:

        print("No payments yet.")
    for payment in payments:
        print(f"Payment {payment[file_handler.PAY_ID]} | "
              f"Record {payment[file_handler.PAY_RECORD]} | "
              f"R{float(payment[file_handler.PAY_AMOUNT]):.2f} | "
              f"Paid at: {payment[file_handler.PAY_TIME]}")


def mall_status_line(mall):
    capacity = int(mall[file_handler.MALL_CAPACITY])
    free = file_handler.spaces_free(mall[file_handler.MALL_ID])
    taken = capacity - free  # can use this agian later
    line = f"{mall[file_handler.MALL_NAME]}: {free} / {capacity} bays free"

    if free <= 0:
        line = line + "  ** FULL **"
    return line



def select_mall():
    malls = file_handler.get_malls()
    print("\n--- Choose a mall ---")
    number = 1
    for mall in malls:
        print(f"{number}. {mall_status_line(mall)}")
        number = number + 1
    choice = validation.get_valid_number(f"Enter your choice (1-{len(malls)}): ", 1, len(malls))
    return malls[choice - 1][file_handler.MALL_ID]


def customer_menu(username):

    mall_id = None
    while True:
        if mall_id is None:
            active_mall = "No mall selected"
        else:
            active_mall = file_handler.mall_name(mall_id)

        print(f"\n[CUSTOMER: {username}]"
               f"Active mall: {active_mall}")
        print("1. Select a mall")
        print("2. Register vehicle entry / exit")
        print("3. Check my current parking status")
        print("4. View outstanding charges and pay")
        print("5. View my parking and payment history")
        print("6. Log out")

        choice = validation.get_valid_number("Enter your choice (1-6): ", 1, 6)

        if choice == 6:
            print()
            print("You have been logged out. Goodbye!")
            return
        if choice == 1:
            mall_id = select_mall()
            print(f"Confirmed: your active mall is now {file_handler.mall_name(mall_id)}.")
        elif choice == 5:
            view_history(username)
        else:

            # options 2-4 all need a mall picked first, so ask if they haven't

            if mall_id is None:
                print("You have not chosen a mall yet - let's pick one first.")
                mall_id = select_mall()
                print(f"Confirmed: your active mall is now {file_handler.mall_name(mall_id)}.")
            if choice == 2:
                entry_exit_menu(username, mall_id)
            elif choice == 3:
                record = parking_status(username, mall_id)
                if record is None:
                    print("You have no vehicle parked at this mall right now.")
                else:
                    minutes = minutes_between(record[file_handler.REC_IN], now_text())
                    print(f"Your vehicle entered at {record[file_handler.REC_IN]} "
                          f"({minutes} minute(s) ago) and is still parked.")
            elif choice == 4:
                payment_menu(username, mall_id)



def show_parked_vehicles(mall_id):

    parked = []
    for record in file_handler.get_records_for_mall(mall_id):
        if record[file_handler.REC_OUT] == "":
            parked.append(record)

    print(f"\n--- Vehicles currently parked at {file_handler.mall_name(mall_id)} ---")
    if len(parked) == 0:
        print("No vehicles are parked here right now.")
    for record in parked:
        minutes = minutes_between(record[file_handler.REC_IN], now_text())
        print(f"Record {record[file_handler.REC_ID]} | "
              f"Driver: {record[file_handler.REC_USER]} | "
              f"Entered: {record[file_handler.REC_IN]} | "
              f"Parked for: {minutes} minute(s)")


def show_capacity(mall_id):
    mall = file_handler.find_mall(mall_id)
    capacity = int(mall[file_handler.MALL_CAPACITY])
    parked = file_handler.count_parked(mall_id)
    free = capacity - parked
    percent = parked / capacity * 100
    print(f"\n--- Parking capacity: {mall[file_handler.MALL_NAME]} ---")
    print(f"{free} / {capacity} bays free ({percent:.0f}% full)")
    print(f"Pricing type: {mall[file_handler.MALL_PRICING]}")


def mall_report(mall_id):

    # only counts finished visits (exit time filled in), not cars still parked
    completed = []
    for record in file_handler.get_records_for_mall(mall_id):
        if record[file_handler.REC_OUT] != "":
            completed.append(record)

    total_vehicles = len(completed)
    total_revenue = 0.0
    total_minutes = 0
    for record in completed:
        total_revenue = total_revenue + float(record[file_handler.REC_FEE])
        total_minutes = total_minutes + minutes_between(
            record[file_handler.REC_IN], record[file_handler.REC_OUT])

    if total_vehicles > 0:
        average_minutes = total_minutes / total_vehicles
    else:
        average_minutes = 0
    return total_vehicles, total_revenue, average_minutes



def admin_menu(username, mall_id):
    # admin only ever sees their own mall

    while True:
        print(f"\n[ADMIN: {username}]  Mall: {file_handler.mall_name(mall_id)}")
        print("1. View vehicles currently parked")
        print("2. Monitor parking capacity")
        print("3. View mall report (vehicles, revenue, average duration)")
        print("4. Log out")
        choice = validation.get_valid_number("Enter your choice (1-4): ", 1, 4)

        if choice == 1:
            show_parked_vehicles(mall_id)
        elif choice == 2:
            show_capacity(mall_id)
        elif choice == 3:
            total_vehicles, total_revenue, average_minutes = mall_report(mall_id)
            print(f"\n--- Report for {file_handler.mall_name(mall_id)} ---")
            print(f"Total vehicles parked: {total_vehicles}")
            print(f"Total revenue: R{total_revenue:.2f}")
            print(f"Average parking duration: {average_minutes:.0f} minute(s)")
        else:
            print("You have been logged out. Goodbye!")
            return


def show_comparison_report():
    print("\n--- Comparative report: all malls ---")
    total_revenue = 0.0
    for mall in file_handler.get_malls():
        mall_id = mall[file_handler.MALL_ID]
        total_vehicles, revenue, average_minutes = mall_report(mall_id)
        print(f"{mall[file_handler.MALL_NAME]} ({mall[file_handler.MALL_PRICING]}): "
              f"{total_vehicles} vehicle(s), R{revenue:.2f} revenue, "
              f"{average_minutes:.0f} minute(s) average")
        total_revenue = total_revenue + revenue

    print(f"\nTotal revenue across all malls: R{total_revenue:.2f}")



def owner_menu(username):
    # owner isn't locked to one mall like the admin is,they can check any of the malls

    while True:
        print(f"\n[OWNER: {username}]  Access: all malls")
        print("1. Comparative report across all malls")
        print("2. View one mall in detail")
        print("3. Log out")
        choice = validation.get_valid_number("Enter your choice (1-3): ", 1, 3)

        if choice == 1:
            show_comparison_report()
        elif choice == 2:
            mall_id = select_mall()
            show_capacity(mall_id)
            show_parked_vehicles(mall_id)
            total_vehicles, total_revenue, average_minutes = mall_report(mall_id)
            print(f"\nMall report: {file_handler.mall_name(mall_id)}")
            print("Total revenue: R" + str(round(total_revenue, 2)))
            print(f"Total vehicles parked: {total_vehicles}")
            print(f"Average parking duration: {average_minutes:.0f} minute(s)")
        else:
            print("You have been logged out. Goodbye!")
            return


def open_role_menu(user):
    role = user[file_handler.USER_ROLE]
    if role == "customer":
        customer_menu(user[file_handler.USER_NAME])
    else:
        if role == "admin":
            admin_menu(user[file_handler.USER_NAME], user[file_handler.USER_MALL])
        else:
            if role == "owner":
                owner_menu(user[file_handler.USER_NAME])


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nProgram closed. Your data has been saved.")
