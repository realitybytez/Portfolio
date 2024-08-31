import yaml
from random import randint, randrange, choices
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from faker import Faker

tables = dict()
fake = Faker()
Faker.seed(451)

current_datetime = datetime.now()

system_go_live_date = datetime(2006, 3, 25, 6, 0, 0)
system_user = 1
starting_staff_ids = [x for x in range(2, 22)]

active_policies = set()
num_active_policies = 0
policy_id_start = 1000000

new_business_min_transactions = 0
new_business_max_transactions = 50
endorsement_min_transactions = int(num_active_policies * 0.01)
endorsement_max_transactions = int(num_active_policies * 0.05)
cancellations_min_transactions = int(num_active_policies * 0.00)
cancellations_max_transactions = int(num_active_policies * 0.01)


def simulate_system():
    days_to_present = abs((system_go_live_date - current_datetime)).days
    days_scope = [system_go_live_date + timedelta(days=x) for x in range(0, days_to_present + 1)]
    next_transaction_id = 1

    for day in days_scope:
        tracker = {'New Business':
                {
                    'created': 0,
                    'required': randint(new_business_min_transactions, new_business_max_transactions),
                },
            'Endorsement':
                {
                    'created': 0,
                    'required': randint(endorsement_min_transactions, endorsement_max_transactions)
                },
            'Cancellation':
                {
                    'created': 0,
                    'required': randint(cancellations_min_transactions, cancellations_max_transactions)
                },
                'All':
                {
                    'created': 0,
                    'required': 0
                }
        }

        #transaction_types = ['New Business', 'Endorsement', 'Cancellation']
        transaction_types = ['New Business', 'Endorsement', 'Cancellation']
        transaction_timestamp = None

        if transaction_timestamp is None:
            transaction_timestamp = system_go_live_date + timedelta(seconds=randint(0, 10800))
        else:
            transaction_timestamp = transaction_timestamp + timedelta(seconds=randint(5,15))

        while True:
            if tracker['All']['created'] > tracker['All']['required']:
                break

            choice = choices(transaction_types, weights=[randrange(10, 30), randrange(10, 30), randrange(10, 30)])[0]

            if tracker[choice]['created'] > tracker[choice]['required']:
                continue

            if choice == 'New Business':
                record = [next_transaction_id,
                                       policy_id_start + next_transaction_id,
                                       'NEW',
                                       'COM',
                                       1,
                                       datetime.combine(transaction_timestamp, time.min),
                                       datetime.combine(transaction_timestamp, time.min) + relativedelta(years=1),
                                       transaction_timestamp]
                active_policies.add(policy_id_start + next_transaction_id)

                next_transaction_id += 1
                print(record)


        # todo renewals... as many of these occur as needed, processed in batch after all of these, exc. canc. Track renewals by date

def generate_go_live_users():
    party_table = [['party_id', 'given_name', 'surname', 'role', 'modified']]
    go_live_users = [system_user,] + starting_staff_ids
    for uid in go_live_users:
        if uid == system_user:
            party_record = [uid, 'SYSTEM', 'USER', 'BATCH', system_go_live_date]
        else:
            first_name, surname = fake.name().split(' ')
            party_record = [uid, first_name, surname, 'STAFF', system_go_live_date]
        party_table.append(party_record)
    tables['party'] = party_table


def generate_type_tables():
    with open('type_tables.yml', 'r') as file:
        data = yaml.safe_load(file)

        for table in data:
            new_table = []
            id_counter = 0
            for key, value in data[table].items():
                id_counter += 1
                row = [id_counter, key, value, current_datetime]
                new_table.append(row)
                tables[table] = new_table


if __name__ == '__main__':
    generate_go_live_users()
    generate_type_tables()
    simulate_system()
