import yaml
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from faker import Faker

tables = dict()
fake = Faker()
Faker.seed(451)

current_datetime = datetime.now()
number_of_policies = 100000
is_cancelled_weight = 20  # Out of 100

system_go_live_date = datetime(2006, 3, 25, 6, 0, 0)
system_user = 1
starting_staff_ids = [x for x in range(2, 22)]


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

def generate_transactions():
    transaction = [['transaction_id', 'policy_id', 'transaction_type_key', 'transaction_state_key', 'sequence', 'effective', 'expiration', 'modified']]
    transaction_count = 1
    for i in range(number_of_policies):
        policy_inception = fake.date_time_between_dates(datetime_start='-10000d', datetime_end='-180d')
        policy_cancellation = fake.date_time_between_dates(datetime_start=policy_inception, datetime_end='-90d')
        policy_id = i+1000000
        rel_delta = relativedelta(policy_cancellation, policy_inception)
        renewals = 0
        if rel_delta.years >= 1:
            renewals = rel_delta.years

        if not is_policy_cancelled():
            policy_cancellation = None

        new_business_record = [transaction_count, policy_id, 'NEW', 'COM', 1, policy_inception, policy_inception + relativedelta(years=1), policy_inception]
        transaction_count += 1
        transaction.append(new_business_record)

        for r in range(1, renewals + 1):
            renewal_record = [transaction_count, policy_id, 'REN', 'COM', 1+r, policy_inception + relativedelta(years=r), policy_inception + relativedelta(years=r+1), policy_inception + relativedelta(years=1+r)]
            if policy_cancellation and r == renewals:
                renewal_record[6] = policy_cancellation
                renewal_record[-1] = policy_cancellation
            transaction_count += 1
            transaction.append(renewal_record)

        if policy_cancellation is not None:
            cancellation_record = [transaction_count, policy_id, 'CAN', 'COM', 1+renewals+1, policy_cancellation, datetime(2999, 12, 1, 23, 59, 59), policy_cancellation]  # NB + Renewals + Cancellation
            transaction.append(cancellation_record)
            transaction_count += 1


def is_policy_cancelled():
    roll = random.randint(1, 100)
    if roll < is_cancelled_weight:
        return False
    else:
        return True


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
    generate_transactions()
    generate_type_tables()
