import os

import yaml
from random import randint, randrange, choices, uniform
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from faker import Faker
import csv
from os import path
from pkg_resources import resource_filename

#todo as time allows - calculate premium as proportion of term e.g for endorsements
#todo make inception/expiry non overlapping?


fake = Faker('en_AU')
Faker.seed(451)

current_datetime = datetime.now()

system_go_live_date = datetime(2006, 3, 25, 6, 0, 0)
system_user = 1
starting_staff_ids = [x for x in range(2, 22)]

num_active_policies = 0
policy_id_start = 1000000
track_party_occupancy = dict()
track_active_policies = dict()
track_renewals = dict()

new_business_min_transactions = 0
new_business_max_transactions = 50
days_to_simulate = 800
endorsement_cancellation_start_on_day = 5


def simulate_system(tables, counters, customer_party_occupancy_data, active_policies, num_active_policies, track_renewals):
    days_to_present = abs((system_go_live_date - current_datetime)).days
    days_scope = [system_go_live_date + timedelta(days=x) for x in range(0, days_to_present + 1)]

    for i, day in enumerate(days_scope):
        if i == days_to_simulate:
            return tables

        endorsement_min_transactions = int(num_active_policies * 0.01)
        endorsement_max_transactions = int(num_active_policies * 0.02)
        cancellations_min_transactions = int(num_active_policies * 0.00)
        cancellations_max_transactions = int(num_active_policies * 0.01)

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

        if i + 1 >= endorsement_cancellation_start_on_day:
            sum_required = tracker['New Business']['required'] + tracker['Endorsement']['required'] + tracker['Cancellation']['required']
            tracker['All']['required'] = sum_required
            transaction_types = ['New Business', 'Endorsement', 'Cancellation']
            tran_choice_weights = [randrange(10, 30), randrange(10, 30), randrange(10, 30)]
        else:
            tracker['All']['required'] = tracker['New Business']['required']
            transaction_types = ['New Business',]
            tran_choice_weights = [100,]

        transaction_timestamp = None
        coverage_type_keys = [x[1] for x in tables['coverage_type']]
        property_type_keys = [x[1] for x in tables['property_type']]
        wall_material_type_keys = [x[1] for x in tables['wall_material_type']]
        roof_material_type_keys = [x[1] for x in tables['roof_material_type']]
        occupancy_type_keys = [x[1] for x in tables['property_occupation_type']]
        address_type_keys = ['MAI', 'RIS']

        while True:
            if transaction_timestamp is None:
                transaction_timestamp = day + timedelta(seconds=randint(0, 10800))
            else:
                transaction_timestamp = transaction_timestamp + timedelta(seconds=randint(5, 15))

            if tracker['All']['created'] >= tracker['All']['required']:
                tomorrow = (transaction_timestamp + relativedelta(days=1)).date()

                try:
                    policies_renewing_tomorrow = track_renewals[tomorrow]
                except KeyError:
                    break

                for policy_id, renewal_datetime in policies_renewing_tomorrow.items():
                    policy_table_ids_structure = active_policies[policy_id]
                    current_transaction = tables['transaction'][policy_table_ids_structure['transaction']]
                    next_sequence = current_transaction[4] + 1
                    inception = datetime.combine(renewal_datetime, time.min)
                    expiry = renewal_datetime + relativedelta(years=1)
                    record = generate_transaction_record(counters, policy_id, 'REN', 'COM', next_sequence, inception, expiry, transaction_timestamp)
                    tables['transaction'].append(record)
                    active_policies[policy_id]['transaction'] = record[0]
                    update_premium_record = tables['premium_detail'][chosen_policy_table_ids_structure['premium_detail']]
                    update_premium_record[1] = record[0]
                    old_base_premium = update_premium_record[2]
                    new_base_premium = round(uniform(old_base_premium, old_base_premium * 1.03), 2)
                    update_premium_record[2] = new_base_premium
                    new_gross_premium = new_base_premium * (1 + update_premium_record[3]) * (1 + update_premium_record[4])
                    update_premium_record[5] = round(new_gross_premium, 2)
                    update_premium_record[-1] = transaction_timestamp

                    try:
                        track_renewals[expiry.date()]
                    except KeyError:
                        track_renewals[expiry.date()] = dict()

                    track_renewals[expiry.date()][tables['policy'][policy_id][0]] = record[6]
                break

            choice = choices(transaction_types, weights=tran_choice_weights)[0]
            if tracker[choice]['created'] >= tracker[choice]['required']:
                continue

            if choice == 'New Business':
                chance_existing_party_new_policy = 50
                roll_existing_party_new_policy = uniform(0.00, 100)
                is_existing_party_new_policy = (lambda x, y: True if x < y and len(customer_party_occupancy_data) > 0 else False)(roll_existing_party_new_policy, chance_existing_party_new_policy)
                occ_property_cover_weights = [50, 0, 50]
                occ_combined_cover_weights = [10, 0, 90]
                occ_contents_cover_weights = [33, 33, 33]
                policy_number = policy_id_start + counters['transaction']
                inception = datetime.combine(transaction_timestamp, time.min)
                expiry = datetime.combine(transaction_timestamp, time.min) + relativedelta(years=1)
                record = generate_transaction_record(counters, counters['policy'], 'NEW', 'COM', 1, inception, expiry, transaction_timestamp)
                tables['transaction'].append(record)

                if is_existing_party_new_policy:
                    existing_party_id = choices([x for x in customer_party_occupancy_data.keys()])[0]
                    policy_record = generate_policy_record(counters, policy_number, inception, transaction_timestamp)
                    tables['policy'].append(policy_record)
                    if customer_party_occupancy_data[existing_party_id]['insured_ppor']:
                        occ_property_cover_weights = [10, 90, 0]
                        occ_combined_cover_weights = [10, 90, 0]
                    party_policy_record = generate_party_policy_record(counters, policy_record[0], existing_party_id, transaction_timestamp)
                else:
                    party_record = generate_customer_party_record(counters, transaction_timestamp)
                    tables['party'].append(party_record)
                    mailing_address_record = generate_address_record(counters, 'MAI', transaction_timestamp)
                    tables['address'].append(mailing_address_record)
                    contact_record = generate_contact_record(counters, party_record[0], mailing_address_record[0], transaction_timestamp)
                    tables['contact'].append(contact_record)
                    policy_record = generate_policy_record(counters, policy_number, inception, transaction_timestamp)
                    tables['policy'].append(policy_record)
                    party_policy_record = generate_party_policy_record(counters, policy_record[0], party_record[0], transaction_timestamp)

                tables['party_policy_association'].append(party_policy_record)

                chance_combined = randint(1, 100)
                wall_type = choices(wall_material_type_keys)[0]
                roof_type = choices(roof_material_type_keys)[0]
                prop_type = choices(property_type_keys)[0]

                if chance_combined <= 40:
                    home_coverage_record = generate_coverage_record(counters, coverage_type_keys[0], counters['transaction'], transaction_timestamp)
                    tables['coverage'].append(home_coverage_record)
                    occ_type = choices(occupancy_type_keys, weights=occ_combined_cover_weights)[0]  # Renter will not buy combined
                    occupancy_record = generate_occupancy_record(counters, occ_type, transaction_timestamp)
                    property_record = generate_property_record(counters, home_coverage_record[0], prop_type, roof_type, wall_type, occupancy_record[0], randint(1950, 2005), round(randint(500000, 3000000), -4), transaction_timestamp)
                    contents_coverage_record = generate_coverage_record(counters, coverage_type_keys[1], counters['transaction'], transaction_timestamp)
                    tables['coverage'].append(contents_coverage_record)
                    contents_record = generate_contents_record(counters, contents_coverage_record[0], transaction_timestamp)
                    total_sum_insured = property_record[-2] + contents_record[-2]
                    premium_record = generate_premium_detail(counters, record[0], total_sum_insured, transaction_timestamp)
                    tables['contents'].append(contents_record)
                else:
                    choice = choices(coverage_type_keys, weights=[10, 90])[0]
                    coverage_record = generate_coverage_record(counters, choice, counters['transaction'], transaction_timestamp)
                    tables['coverage'].append(coverage_record)
                    if coverage_record[2] == 'CON':
                        occ_type = choices(occupancy_type_keys, weights=occ_contents_cover_weights)[0]
                        occupancy_record = generate_occupancy_record(counters, occ_type, transaction_timestamp)
                        contents_record = generate_contents_record(counters, coverage_record[0], transaction_timestamp)
                        tables['contents'].append(contents_record)
                        property_record = generate_property_record(counters, coverage_record[0], prop_type, roof_type, wall_type, occupancy_record[0], randint(1950, 2005), 0, transaction_timestamp)
                        premium_record = generate_premium_detail(counters, record[0], contents_record[-2], transaction_timestamp)
                    else:
                        occ_type = choices(occupancy_type_keys, weights=occ_property_cover_weights)[0]  # Renter will not buy property insurance for residence they are inhabiting
                        occupancy_record = generate_occupancy_record(counters, occ_type, transaction_timestamp)
                        property_record = generate_property_record(counters, coverage_record[0], prop_type, roof_type, wall_type, occupancy_record[0], randint(1950, 2005), round(randint(500000, 3000000), -4), transaction_timestamp)
                        premium_record = generate_premium_detail(counters, record[0], property_record[-2], transaction_timestamp)
                tables['occupancy'].append(occupancy_record)
                tables['property'].append(property_record)
                tables['premium_detail'].append(premium_record)

                try:
                    customer_party_occupancy_data[party_record[0]]
                except KeyError:
                    customer_party_occupancy_data[party_record[0]] = {'insured_ppor': False}

                if occupancy_record[1] == 'OWN':
                    customer_party_occupancy_data[party_record[0]] = {'insured_ppor': True}

                chance_mailing_address = randint(1, 100)

                if chance_mailing_address <= 90:
                    mail_data = mailing_address_record[2:-2]
                    risk_address_record = generate_address_record(counters, 'RIS', transaction_timestamp, address_data=mail_data)
                else:
                    risk_address_record = generate_address_record(counters, 'RIS', transaction_timestamp)

                tables['address'].append(risk_address_record)

                tracker['All']['created'] += 1
                tracker['New Business']['created'] += 1
                active_policies[policy_record[0]] = {
                    'mailing_address': mailing_address_record[0],
                    'risk_address': risk_address_record[0],
                    'transaction': record[0],
                    'premium_detail': premium_record[0],
                }

                try:
                    track_renewals[record[5].date() + relativedelta(years=1)]
                except KeyError:
                    track_renewals[record[5].date() + relativedelta(years=1)] = dict()

                track_renewals[record[5].date() + relativedelta(years=1)][policy_record[0]] = record[6]

                num_active_policies += 1

            if choice == 'Endorsement':
                # Choose whether this is a risk address and forces re-rate or just mailing address and hence no re-rate
                address_type = choices(address_type_keys, weights=[80,20])

                # Update transaction
                policy_ids = [x for x in active_policies.keys()]
                chosen_policy_id = choices(policy_ids)[0]
                chosen_policy_table_ids_structure = active_policies[chosen_policy_id]
                current_transaction = tables['transaction'][chosen_policy_table_ids_structure['transaction']]
                next_sequence = current_transaction[4] + 1
                inception = datetime.combine(transaction_timestamp, time.min)
                expiry = current_transaction[6]
                record = generate_transaction_record(counters, chosen_policy_id, 'END', 'COM', next_sequence, inception, expiry, transaction_timestamp)
                tables['transaction'].append(record)
                current_transaction[6] = inception
                current_transaction[-1] = transaction_timestamp
                active_policies[chosen_policy_id]['transaction'] = record[0]

                # Get new information
                address_line, structured_address = fake.address().split('\n')
                suburb, state, postcode = [x.strip() for x in structured_address.split(',')]

                if address_type == 'MAI':
                    update_address_record = tables['address'][chosen_policy_table_ids_structure['mailing_address']]
                else:
                    update_address_record = tables['address'][chosen_policy_table_ids_structure['risk_address']]
                    update_premium_record = tables['premium_detail'][chosen_policy_table_ids_structure['premium_detail']]
                    update_premium_record[1] = record[0]
                    old_base_premium = update_premium_record[2]
                    new_base_premium = round(uniform(old_base_premium * .75, old_base_premium * 1.25), 2)
                    update_premium_record[2] = new_base_premium
                    new_gross_premium = new_base_premium * (1 + update_premium_record[3]) * (1 + update_premium_record[4])
                    update_premium_record[5] = round(new_gross_premium, 2)
                    update_premium_record[-1] = transaction_timestamp

                update_address_record[2] = address_line
                update_address_record[3] = suburb
                update_address_record[4] = postcode
                update_address_record[5] = state
                update_address_record[-1] = transaction_timestamp
                tracker['All']['created'] += 1
                tracker['Endorsement']['created'] += 1

                try:
                    track_renewals[expiry.date()]
                except KeyError:
                    track_renewals[expiry.date()] = dict()

                track_renewals[expiry.date()][tables['policy'][chosen_policy_id][0]] = record[6]

            if choice == 'Cancellation':
                # Update transaction
                policy_ids = [x for x in active_policies.keys()]
                chosen_policy_id = choices(policy_ids)[0]
                chosen_policy_table_ids_structure = active_policies[chosen_policy_id]
                current_transaction = tables['transaction'][chosen_policy_table_ids_structure['transaction']]
                next_sequence = current_transaction[4] + 1
                inception = datetime.combine(transaction_timestamp, time.min)
                expiry = inception
                record = generate_transaction_record(counters, chosen_policy_id, 'CAN', 'COM', next_sequence, inception, expiry, transaction_timestamp)
                tables['transaction'].append(record)

                current_transaction_expiry = current_transaction[6]
                del track_renewals[current_transaction_expiry.date()][tables['policy'][chosen_policy_id][0]]

                current_transaction[6] = inception
                current_transaction[-1] = transaction_timestamp
                del active_policies[chosen_policy_id]
                num_active_policies -= 1

                tracker['All']['created'] += 1
                tracker['Cancellation']['created'] += 1

    return tables
        # todo renewals... as many of these occur as needed, processed in batch after all of these, exc. canc. Track renewals by date


def generate_party_policy_record(counters, policy_id, party_id, transaction_timestamp):
    record = [counters['party_policy_association'], policy_id, party_id, transaction_timestamp]
    counters['party_policy_association'] += 1
    return record


def generate_premium_detail(counters, transaction_id, sum_insured, transaction_timestamp):
    base_premium = round(sum_insured * uniform(0.03, 0.032), 2)
    gst = 0.10
    stamp_duty = 0.08
    gross_premium = base_premium * (1 + gst) * (1 + stamp_duty)
    record = [counters['premium_detail'], transaction_id,  base_premium, gst, stamp_duty, round(gross_premium, 2), round(randint(0, 3000), -2), transaction_timestamp]
    counters['premium_detail'] += 1
    return record


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


def generate_policy_record(counters, policy_number, inception, transaction_timestamp):
    #todo make line of business dynamic based on risk/cover
    record = [counters['policy'], policy_number, 'Online', inception, 'Western Alliance', 'Property', transaction_timestamp]
    counters['policy'] += 1
    return record


def generate_customer_party_record(counters, transaction_timestamp):
    names = fake.name().split(' ')
    record = [counters['party'], names[0], names[1], 'CUSTOMER', transaction_timestamp]
    counters['party'] += 1
    return record


def generate_transaction_record(counters, policy_id, t_type_key, t_state_key, seq, effective, expiration, transaction_timestamp):
    record = [counters['transaction'], policy_id, t_type_key, t_state_key, seq, effective, expiration, transaction_timestamp]
    counters['transaction'] += 1
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
    return tables, counters


def generate_type_tables(tables):
    filepath = resource_filename(__name__, 'type_tables.yml')
    #filepath = 'type_tables.yml'
    with open(filepath, 'r') as file:
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


def generate_data():
    all_tables = {
        'transaction': [
            ['transaction_id', 'policy_id', 'transaction_type_key', 'transaction_state_key', 'sequence', 'effective',
             'expiration', 'modified']],
        'policy': [['policy_id', 'policy_number', 'channel', 'inception', 'brand', 'line_of_business', 'modified']],
        'party': [['party_id', 'given_name', 'surname', 'role', 'modified'], ],
        'coverage': [['coverage_id', 'coverage_type_key', 'transaction_id', 'modified']],
        'property': [['property_id', 'coverage_id', 'property_type_key', 'roof_material_key', 'wall_material_key',
                      'occupancy_id', 'year_of_construction', 'sum_insured', 'modified']],
        'occupancy': [['occupancy_id', 'occupancy_type_key', 'rental_amount', 'modified']],
        'contents': [['contents_id', 'coverage_id', 'sum_insured', 'modified']],
        'address': [
            ['address_id', 'address_key', 'address_line', 'suburb', 'postcode', 'state', 'country', 'modified']],
        'contact': [['contact_id', 'party_id', 'address_id', 'contact_preference', 'modified']],
        'premium_detail': [
            ['premium_detail_id', 'transaction_id', 'base_annual_premium', 'gst', 'stamp_duty', 'gross_annual_premium',
             'excess', 'modified']],
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

    all_tables, id_counters = generate_go_live_users(all_tables, id_counters)
    all_tables = generate_type_tables(all_tables)
    all_tables = simulate_system(all_tables, id_counters, track_party_occupancy, track_active_policies, num_active_policies, track_renewals)

    output_folder = path.join(os.path.abspath(os.getcwd()), 'output')

    if not path.exists(output_folder):
        os.mkdir(output_folder)

    for table_name, content in all_tables.items():
        with open(f'{path.join(output_folder, table_name)}.csv', 'w', newline='\n') as f:
            writer = csv.writer(f)
            for row in content:
                writer.writerow(row)
