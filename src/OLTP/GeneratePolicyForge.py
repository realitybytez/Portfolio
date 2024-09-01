import yaml
from random import randint, randrange, choices
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from faker import Faker

all_tables = {
    'transaction': [['transaction_id', 'policy_id', 'transaction_type_key', 'transaction_state_key', 'sequence', 'effective', 'expiration', 'modified']],
    'policy': [['policy_id', 'party_association_id', 'policy_number', 'channel', 'inception', 'brand', 'line_of_business', 'modified']],
    'party': [['party_id', 'given_name', 'surname', 'role', 'modified'],],
    'coverage': [['coverage_id', 'coverage_type_key', 'transaction_id', 'sum_insured', 'modified']],
    'property': [['property_id', 'coverage_id', 'property_type_key', 'roof_material_key', 'wall_material_key', 'occupancy_id', 'year_of_construction', 'sum_insured', 'modified']],
    'occupancy': [['occupancy_id', 'occupancy_type_key', 'rental_amount', 'modified']],
    'contents': [['contents_id', 'coverage_id', 'coverage_type_key', 'transaction_id', 'modified']],
    'address': [['address_id', 'address_key', 'address_line', 'suburb', 'postcode', 'state', 'country', 'modified']],
    'contact': [['contact_id', 'party_id', 'address_id', 'contact_preference', 'modified']],
    'premium_detail': [['premium_detail_id', 'annual_premium', 'base_premium', 'gst', 'esl', 'excess', 'modified']],
    'party_policy_association': [['party_policy_id', 'policy_id', 'party_id', 'modified']],
}

id_counters = {
    'transaction': 1,
    'policy': 1,
    'party': 1,
    'coverage': 1,
    'property': 1,
    'occupancy': 1,
    'contents': 1,
    'address': 1,
    'contact': 1,
    'premium_detail': 1,
    'party_policy_association': 1,
}

fake = Faker('en_AU')
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
        if i == days_to_simulate:
            break

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
        coverage_type_keys = [x[1] for x in tables['coverage_type']]
        property_type_keys = [x[1] for x in tables['property_type']]
        wall_material_type_keys = [x[1] for x in tables['wall_material_type']]
        roof_material_type_keys = [x[1] for x in tables['roof_material_type']]
        occupancy_type_keys = [x[1] for x in tables['property_occupation']]

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

                party_record = generate_customer_party_record(counters, transaction_timestamp)
                tables['party'].append(party_record)

                mailing_address_record = generate_address_record(counters, 'MAI', transaction_timestamp)
                tables['address'].append(mailing_address_record)

                contact_record = generate_contact_record(counters, party_record[0], mailing_address_record[0], transaction_timestamp)
                tables['contact'].append(contact_record)

                policy_record = generate_policy_record(counters, party_record[0], policy_number, inception, transaction_timestamp)
                tables['policy'].append(policy_record)

                chance_combined = randint(1, 100)
                wall_type = choices(wall_material_type_keys)[0]
                roof_type = choices(roof_material_type_keys)[0]
                prop_type = choices(property_type_keys)[0]

                if chance_combined <= 40:
                    home_coverage_record = generate_coverage_record(counters, coverage_type_keys[0], counters['transaction'], transaction_timestamp)
                    tables['coverage'].append(home_coverage_record)
                    occ_type = choices(occupancy_type_keys, weights=[10, 0, 90])[0]  # Renter will not buy combined
                    occupancy_record = generate_occupancy_record(counters, occ_type, transaction_timestamp)
                    property_record = generate_property_record(counters, home_coverage_record[0], prop_type, roof_type, wall_type, occupancy_record[0], randint(1950, 2005), round(randint(500000, 3000000), -4), transaction_timestamp)
                    contents_coverage_record = generate_coverage_record(counters, coverage_type_keys[1], counters['transaction'], transaction_timestamp)
                    tables['coverage'].append(contents_coverage_record)
                    contents_record = generate_contents_record(counters, contents_coverage_record[0], transaction_timestamp)
                    tables['contents'].append(contents_record)
                else:
                    choice = choices(coverage_type_keys, weights=[10, 90])[0]
                    coverage_record = generate_coverage_record(counters, choice, counters['transaction'], transaction_timestamp)
                    tables['coverage'].append(coverage_record)
                    if coverage_record[2] == 'CON':
                        occ_type = choices(occupancy_type_keys, weights=[33, 33, 33])[0]
                        occupancy_record = generate_occupancy_record(counters, occ_type, transaction_timestamp)
                        contents_record = generate_contents_record(counters, coverage_record[0], transaction_timestamp)
                        tables['contents'].append(contents_record)
                        property_record = generate_property_record(counters, coverage_record[0], prop_type, roof_type, wall_type, occupancy_record[0], randint(1950, 2005), 0, transaction_timestamp)
                    else:
                        occ_type = choices(occupancy_type_keys, weights=[50, 0, 50])[0]  # Renter will not buy property insurance for residence they are inhabiting
                        occupancy_record = generate_occupancy_record(counters, occ_type, transaction_timestamp)
                        property_record = generate_property_record(counters, coverage_record[0], prop_type, roof_type, wall_type, occupancy_record[0], randint(1950, 2005), round(randint(500000, 3000000), -4), transaction_timestamp)
                tables['occupancy'].append(occupancy_record)
                tables['property'].append(property_record)

                chance_mailing_address = randint(1, 100)

                if chance_mailing_address <= 90:
                    mail_data = mailing_address_record[2:-2]
                    risk_address_record = generate_address_record(id_counters, 'RIS', transaction_timestamp, address_data=mail_data)
                else:
                    risk_address_record = generate_address_record(id_counters, 'RIS', transaction_timestamp)

                tables['address'].append(risk_address_record)

                counters['transaction'] += 1
                tracker['All']['created'] += 1
    return tables
        # todo renewals... as many of these occur as needed, processed in batch after all of these, exc. canc. Track renewals by date


def generate_contents_record(counters, coverage_id, transaction_timestamp):
    record = [counters['contents'], coverage_id, round(randrange(50000, 300000), -3), transaction_timestamp]
    counters['contents'] += 1
    return record


def generate_occupancy_record(counters, occ_type, transaction_timestamp):
    rental_amount = 0
    if occ_type == 'TEN':
        rental_amount = randrange(300, 1500)
    record = [counters['occupancy'], occ_type, rental_amount, transaction_timestamp]
    counters['occupancy'] += 1
    return record


def generate_property_record(counters, coverage_id, prop_type_key, roof_key, wall_key, occ_id, construct_year, sum_insured, transaction_timestamp):
    record = [counters['property'], coverage_id, prop_type_key, roof_key, wall_key, occ_id, construct_year, sum_insured, transaction_timestamp]
    counters['property'] += 1
    return record


def generate_contact_record(counters, party_id, address_id, transaction_timestamp):
    record = [counters['contact'], party_id, address_id, 'MAIL', transaction_timestamp]
    counters['contact'] += 1
    return record


def generate_address_record(counters, address_type, transaction_timestamp, address_data=None):
    address_line, structured_address = fake.address().split('\n')
    suburb, state, postcode = [x.strip() for x in structured_address.split(',')]

    if address_data is None:
        record = [counters['address'], address_type, address_line, suburb, postcode, state, 'AU', transaction_timestamp]
    else:
        record = [counters['address'], address_type, address_data[0], address_data[1], address_data[2], address_data[3], 'AU', transaction_timestamp]

    counters['address'] += 1
    return record

def generate_coverage_record(counters, cover, transaction_id, transaction_timestamp):
    record = [counters['coverage'], cover, transaction_id, transaction_timestamp]
    counters['coverage'] += 1
    return record


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
