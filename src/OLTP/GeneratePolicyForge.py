import yaml
from random import randint, randrange, choices
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from faker import Faker

all_tables = {
    'transaction': [['transaction_id', 'policy_id', 'transaction_type_key', 'transaction_state_key', 'sequence', 'effective', 'expiration', 'modified']],
    'policy': [['policy_id', 'party_association_id', 'policy_number', 'channel', 'inception', 'brand', 'line_of_business', 'modified']],
    'party': [['party_id', 'given_name', 'surname', 'role', 'modified'],]
}

id_counters = {
    'transaction': 1,
    'policy': 1,
    'party': 1,
}

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
days_to_simulate = 1


def simulate_system(tables, counters):
    days_to_present = abs((system_go_live_date - current_datetime)).days
    days_scope = [system_go_live_date + timedelta(days=x) for x in range(0, days_to_present + 1)]

    for i, day in enumerate(days_scope):

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

        #todo update to reflect all transaction types
        tracker['All']['required'] = tracker['New Business']['required']

        transaction_types = ['New Business', 'Endorsement', 'Cancellation']
        transaction_timestamp = None

        while True:
            if transaction_timestamp is None:
                transaction_timestamp = day + timedelta(seconds=randint(0, 10800))
            else:
                transaction_timestamp = transaction_timestamp + timedelta(seconds=randint(5, 15))
            if tracker['All']['created'] >= tracker['All']['required']:
                print('leave')
                print(tracker['All']['required'])
                print(tracker['All']['created'])
                break

            choice = choices(transaction_types, weights=[randrange(10, 30), randrange(10, 30), randrange(10, 30)])[0]

            if tracker[choice]['created'] >= tracker[choice]['required']:
                continue

            if choice == 'New Business':
                policy_number = policy_id_start + counters['transaction']
                inception = datetime.combine(transaction_timestamp, time.min)
                expiry = datetime.combine(transaction_timestamp, time.min) + relativedelta(years=1),
                record = [counters['transaction'],
                                       policy_number,
                                       'NEW',
                                       'COM',
                                       1,
                                       inception,
                                       expiry,
                                       transaction_timestamp]
                active_policies.add(policy_id_start + counters['transaction'])
                tables['transaction'].append(record)
                counters['transaction'] += 1

                party_record = generate_customer_party_record(counters, transaction_timestamp)
                tables['party'].append(party_record)

                record = generate_policy_record(counters, party_record[0], policy_number, inception, transaction_timestamp)
                tables['policy'].append(record)

                tracker['All']['created'] += 1

        if i >= days_to_simulate:
            break
    return tables
        # todo renewals... as many of these occur as needed, processed in batch after all of these, exc. canc. Track renewals by date


def generate_policy_record(counters, party_id, policy_number, inception, transaction_timestamp):
    #todo make line of business dynamic based on risk/cover
    record = [counters['policy'], party_id, policy_number, 'Online', inception, 'Western Alliance', 'Home', transaction_timestamp]
    counters['policy'] += 1
    return record


def generate_customer_party_record(counters, transaction_timestamp):
    names = fake.name().split(' ')
    record = [counters['party'], names[0], names[1], 'CUSTOMER', transaction_timestamp]
    counters['party'] += 1
    return record


def generate_go_live_users(tables, counters):
    go_live_users = [system_user,] + starting_staff_ids
    for uid in go_live_users:
        if uid == system_user:
            party_record = [counters['party'], 'SYSTEM', 'USER', 'BATCH', system_go_live_date]
        else:
            first_name, surname = fake.name().split(' ')
            party_record = [counters['party'], first_name, surname, 'STAFF', system_go_live_date]
        counters['party'] += 1
        tables['party'].append(party_record)
    return all_tables, id_counters


def generate_type_tables(tables):
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

    return tables


if __name__ == '__main__':
    all_tables, id_counters = generate_go_live_users(all_tables, id_counters)
    all_tables = generate_type_tables(all_tables)
    all_tables = simulate_system(all_tables, id_counters)
