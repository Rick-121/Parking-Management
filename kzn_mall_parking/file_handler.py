# file_handler.py
# reads and writes the four txt files - the rest of the program never
# opens a file directly, it goes through here

# users.txt = username,password,role (admins have a 4th field, their mall id)
# malls.txt = mall_id,name,capacity,pricing_type
# parking_records.txt = record_id,username,mall_id,entry_time,exit_time,fee
# payments.txt = payment_id,record_id,amount,paid_at

import os
from validation import safe_save_record

USERS_FILE = "users.txt"
MALLS_FILE = "malls.txt"
RECORDS_FILE = "parking_records.txt"
PAYMENTS_FILE = "payments.txt"

USER_NAME, USER_PASS, USER_ROLE, USER_MALL = 0, 1, 2, 3

MALL_ID = 0
MALL_NAME = 1
MALL_CAPACITY = 2
MALL_PRICING = 3

REC_ID, REC_USER, REC_MALL, REC_IN, REC_OUT, REC_FEE = 0, 1, 2, 3, 4, 5
PAY_ID, PAY_RECORD, PAY_AMOUNT, PAY_TIME = 0, 1, 2, 3




def read_lines(filename):
    rows = []
    if not os.path.exists(filename):
        return rows
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                rows.append(line.split(","))
    return rows


def rewrite_file(filename, rows):
    try:
        with open(filename, "w") as f:
            for row in rows:
                f.write(",".join(row) + "\n")
        return True
    except OSError as e:
        print(f"Could not update the file: {e}")
        return False


STARTER_MALLS = [
    ["GATEWAY", "Gateway Theatre of Shopping", "250", "flat"],
    ["PAVILION", "Pavilion Shopping Centre", "180", "hourly"],
    ["LALUCIA", "La Lucia Mall", "150", "hourly_capped"],
]

# no menu for making admin/owner accounts so these get added automatically
STARTER_USERS = [
    ["owner", "owner123", "owner"],
    ["admin_gateway", "admin123", "admin", "GATEWAY"],
    ["admin_pavilion", "admin123", "admin", "PAVILION"],
    ["admin_lalucia", "admin123", "admin", "LALUCIA"],
]

def setup_files():
    # creates the starting files if they're not already there
    if not os.path.exists(MALLS_FILE):
        with open(MALLS_FILE, "w") as f:
            for mall in STARTER_MALLS:
                f.write(",".join(mall) + "\n")

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            for user in STARTER_USERS:
                f.write(",".join(user) + "\n")


def find_user(username):
    for user in read_lines(USERS_FILE):
        if user[USER_NAME] == username:
            return user
    return None


def add_user(username, password, role):
    line = f"{username},{password},{role}"
    result = safe_save_record(USERS_FILE, line)
    return result


def get_malls():
    return read_lines(MALLS_FILE)


def find_mall(mall_id):
    for mall in get_malls():
        if mall[MALL_ID] == mall_id:
            return mall
    return None


def mall_name(mall_id):
    mall = find_mall(mall_id)
    if mall is None:
        return "Unknown mall"
    return mall[MALL_NAME]




'''find a better way to do this'''
def get_next_id(filename, id_column):
    rows = read_lines(filename)
    if len(rows) == 0:
        return "1"
    highest = 0
    for row in rows:
        row_id = int(row[id_column])
        if row_id > highest:
            highest = row_id
    return str(highest + 1)


def save_new_record(username, mall_id, entry_time):
    record_id = get_next_id(RECORDS_FILE, REC_ID)
    line = f"{record_id},{username},{mall_id},{entry_time},,0.00"
    safe_save_record(RECORDS_FILE, line)
    return record_id


def get_active_record(username, mall_id):
    for record in read_lines(RECORDS_FILE):
        if (record[REC_USER] == username and record[REC_MALL] == mall_id
                and record[REC_OUT] == ""):
            return record
    return None



def close_record(record_id, exit_time, fee):
    # this is the one spot where I rewrite the whole file instead of
    # appending, because I'm changing a line that's already there
    rows = read_lines(RECORDS_FILE)
    for row in rows:
        if row[REC_ID] == record_id:
            row[REC_OUT] = exit_time
            row[REC_FEE] = f"{fee:.2f}"
    return rewrite_file(RECORDS_FILE, rows)


def count_parked(m_id):
    total = 0
    for r in read_lines(RECORDS_FILE):
        if r[REC_MALL] == m_id and r[REC_OUT] == "":
            total = total + 1
    return total


def spaces_free(mall_id):
    mall = find_mall(mall_id)
    capacity = int(mall[MALL_CAPACITY])
    return capacity - count_parked(mall_id)

def get_records_for_mall(mall_id):
    # TODO: this is basically the same as get_records_for_user, could
    # probably combine them but this works for now
    found = []
    for record in read_lines(RECORDS_FILE):
        if record[REC_MALL] == mall_id:
            found.append(record)
    return found


def get_records_for_user(username):
    found = []
    for record in read_lines(RECORDS_FILE):
        if record[REC_USER] == username:
            found.append(record)
    return found

"""find a way to neaten this
"""
def get_unpaid_records(username, mall_id):
    paid_record_ids = []
    for payment in read_lines(PAYMENTS_FILE):
        paid_record_ids.append(payment[PAY_RECORD])

    unpaid = []
    for record in get_records_for_user(username):
        if record[REC_OUT] != "" and record[REC_MALL] == mall_id and record[REC_ID] not in paid_record_ids:
            unpaid.append(record)
    return unpaid


def save_payment(record_id, amount, paid_at):
    payment_id = get_next_id(PAYMENTS_FILE, PAY_ID)
    line = f"{payment_id},{record_id},{amount:.2f},{paid_at}"
    safe_save_record(PAYMENTS_FILE, line)
    return payment_id


def get_payments_for_user(username):
    record_ids = []
    for record in get_records_for_user(username):
        record_ids.append(record[REC_ID])

    found = []
    for payment in read_lines(PAYMENTS_FILE):
        if payment[PAY_RECORD] in record_ids:
            found.append(payment)
    return found
