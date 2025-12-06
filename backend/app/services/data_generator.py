"""
Sample Data Generator for FraudShield Demo
Generates realistic microfinance loan data with embedded fraud patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# Ugandan names for realistic data
FIRST_NAMES = [
    'John', 'Mary', 'Peter', 'Grace', 'David', 'Sarah', 'James', 'Agnes',
    'Robert', 'Florence', 'Joseph', 'Catherine', 'Charles', 'Dorothy', 'Francis',
    'Harriet', 'George', 'Irene', 'Henry', 'Jane', 'Isaac', 'Juliet', 'Kenneth',
    'Lillian', 'Martin', 'Naomi', 'Patrick', 'Olivia', 'Richard', 'Patience',
    'Samuel', 'Rose', 'Timothy', 'Susan', 'Vincent', 'Teddy', 'William', 'Winnie'
]

LAST_NAMES = [
    'Mukasa', 'Nakato', 'Ssemakula', 'Nambi', 'Okello', 'Akello', 'Wasswa', 'Babirye',
    'Kato', 'Nalongo', 'Mugisha', 'Asiimwe', 'Tumusiime', 'Byamugisha', 'Mbabazi',
    'Nankya', 'Kabanda', 'Namutebi', 'Lule', 'Nansubuga', 'Kizza', 'Nabukeera',
    'Mutesa', 'Namatovu', 'Ssebaggala', 'Nakimera', 'Lubega', 'Nabukera'
]

BRANCHES = [
    {'id': 'BR001', 'name': 'Kampala Central', 'lat': 0.3163, 'lon': 32.5822},
    {'id': 'BR002', 'name': 'Entebbe', 'lat': 0.0512, 'lon': 32.4637},
    {'id': 'BR003', 'name': 'Jinja', 'lat': 0.4244, 'lon': 33.2041},
    {'id': 'BR004', 'name': 'Mbarara', 'lat': -0.6067, 'lon': 30.6545},
    {'id': 'BR005', 'name': 'Gulu', 'lat': 2.7746, 'lon': 32.2990},
    {'id': 'BR006', 'name': 'Mbale', 'lat': 1.0647, 'lon': 34.1797}
]

OFFICERS = [
    {'id': 'OFF001', 'name': 'K. Mutesa', 'branch': 'BR001'},
    {'id': 'OFF002', 'name': 'J. Nakato', 'branch': 'BR002'},
    {'id': 'OFF003', 'name': 'P. Okello', 'branch': 'BR003'},
    {'id': 'OFF004', 'name': 'S. Nambi', 'branch': 'BR001'},
    {'id': 'OFF005', 'name': 'D. Wasswa', 'branch': 'BR004'},
    {'id': 'OFF006', 'name': 'R. Kizza', 'branch': 'BR005'},
    {'id': 'OFF007', 'name': 'M. Lubega', 'branch': 'BR006'},
    {'id': 'OFF008', 'name': 'T. Ssebaggala', 'branch': 'BR002'}
]

LOAN_PRODUCTS = [
    {'id': 'PROD001', 'name': 'Agricultural Loan', 'min': 500000, 'max': 5000000},
    {'id': 'PROD002', 'name': 'Business Loan', 'min': 1000000, 'max': 20000000},
    {'id': 'PROD003', 'name': 'Emergency Loan', 'min': 100000, 'max': 2000000},
    {'id': 'PROD004', 'name': 'Education Loan', 'min': 500000, 'max': 10000000},
    {'id': 'PROD005', 'name': 'Housing Loan', 'min': 5000000, 'max': 50000000}
]


def generate_phone_number() -> str:
    """Generate Ugandan phone number"""
    prefixes = ['0700', '0701', '0702', '0703', '0704', '0705', '0772', '0782', '0752', '0762']
    return random.choice(prefixes) + ''.join(random.choices('0123456789', k=6))


def generate_national_id() -> str:
    """Generate Ugandan National ID format"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices('0123456789', k=12))
    return f"CM{letters}{numbers}"


def generate_address(branch: dict, is_clustered: bool = False, cluster_base: tuple = None) -> dict:
    """Generate address with optional geographic clustering for fraud simulation"""
    if is_clustered and cluster_base:
        # Clustered loans within ~300m of base
        lat = cluster_base[0] + np.random.uniform(-0.003, 0.003)
        lon = cluster_base[1] + np.random.uniform(-0.003, 0.003)
    else:
        # Normal distribution around branch
        lat = branch['lat'] + np.random.uniform(-0.05, 0.05)
        lon = branch['lon'] + np.random.uniform(-0.05, 0.05)
    
    villages = ['Kyanja', 'Ntinda', 'Bukoto', 'Kamwokya', 'Nakawa', 'Kira', 'Bunga', 'Makindye']
    
    return {
        'village': random.choice(villages),
        'district': branch['name'].split()[0],
        'latitude': round(lat, 6),
        'longitude': round(lon, 6)
    }


def generate_sample_data(num_loans: int = 1000, fraud_rate: float = 0.05) -> pd.DataFrame:
    """
    Generate sample loan dataset with realistic fraud patterns
    
    Parameters:
    -----------
    num_loans : int
        Number of loans to generate
    fraud_rate : float
        Approximate percentage of fraudulent loans (0-1)
    
    Returns:
    --------
    pd.DataFrame
        Generated loan data with fraud indicators
    """
    
    loans = []
    
    # Calculate fraud counts
    num_fraud = int(num_loans * fraud_rate)
    num_normal = num_loans - num_fraud
    
    # Track used identifiers for fraud patterns
    used_phones = {}
    used_addresses = {}
    collusion_clusters = []
    
    # Generate fraud patterns
    # Pattern 1: Ghost loans (same phone for multiple "borrowers")
    ghost_phone_count = num_fraud // 4
    ghost_phones = [generate_phone_number() for _ in range(ghost_phone_count // 3 + 1)]
    
    # Pattern 2: Collusion rings (geographic clustering + same guarantor)
    collusion_count = num_fraud // 4
    collusion_officer = random.choice(OFFICERS[:2])  # First officers are "bad"
    collusion_branch = next(b for b in BRANCHES if b['id'] == collusion_officer['branch'])
    collusion_base = (collusion_branch['lat'], collusion_branch['lon'])
    collusion_guarantor = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    
    # Pattern 3: Unusual approval patterns (high volume for one officer)
    unusual_approval_count = num_fraud // 4
    
    # Pattern 4: After-hours transactions
    after_hours_count = num_fraud // 4
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 1)
    
    loan_id = 0
    
    # Generate ghost loans
    for i in range(ghost_phone_count):
        loan_id += 1
        phone = random.choice(ghost_phones)
        officer = random.choice(OFFICERS[:2])
        branch = next(b for b in BRANCHES if b['id'] == officer['branch'])
        product = random.choice(LOAN_PRODUCTS)
        
        address = generate_address(branch)
        
        loans.append({
            'loan_id': f'L{loan_id:06d}',
            'borrower_id': f'B{loan_id:06d}',
            'borrower_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'national_id': generate_national_id(),
            'phone_number': phone,  # Reused phone = ghost loan indicator
            'address_village': address['village'],
            'address_district': address['district'],
            'latitude': address['latitude'],
            'longitude': address['longitude'],
            'amount': random.randint(product['min'], product['max']),
            'product_id': product['id'],
            'product_name': product['name'],
            'officer_id': officer['id'],
            'officer_name': officer['name'],
            'branch_id': branch['id'],
            'branch_name': branch['name'],
            'disbursement_date': start_date + timedelta(days=random.randint(0, 334)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'status': random.choice(['active', 'active', 'active', 'defaulted']),
            'guarantor_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'guarantor_phone': generate_phone_number(),
            'is_fraud': True,
            'fraud_type': 'ghost_loan'
        })
    
    # Generate collusion ring loans
    for i in range(collusion_count):
        loan_id += 1
        branch = collusion_branch
        officer = collusion_officer
        product = random.choice(LOAN_PRODUCTS)
        
        address = generate_address(branch, is_clustered=True, cluster_base=collusion_base)
        
        loans.append({
            'loan_id': f'L{loan_id:06d}',
            'borrower_id': f'B{loan_id:06d}',
            'borrower_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'national_id': generate_national_id(),
            'phone_number': generate_phone_number(),
            'address_village': address['village'],
            'address_district': address['district'],
            'latitude': address['latitude'],
            'longitude': address['longitude'],
            'amount': random.randint(product['min'], product['max']),
            'product_id': product['id'],
            'product_name': product['name'],
            'officer_id': officer['id'],
            'officer_name': officer['name'],
            'branch_id': branch['id'],
            'branch_name': branch['name'],
            'disbursement_date': start_date + timedelta(days=random.randint(0, 334)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'status': random.choice(['active', 'active', 'defaulted']),
            'guarantor_name': collusion_guarantor,  # Same guarantor = collusion indicator
            'guarantor_phone': generate_phone_number(),
            'is_fraud': True,
            'fraud_type': 'collusion'
        })
    
    # Generate after-hours loans
    for i in range(after_hours_count):
        loan_id += 1
        officer = random.choice(OFFICERS)
        branch = next(b for b in BRANCHES if b['id'] == officer['branch'])
        product = random.choice(LOAN_PRODUCTS)
        address = generate_address(branch)
        
        # After hours timestamp
        base_date = start_date + timedelta(days=random.randint(0, 334))
        if random.random() > 0.5:
            hour = random.randint(22, 23)
        else:
            hour = random.randint(0, 5)
        timestamp = base_date.replace(hour=hour, minute=random.randint(0, 59))
        
        loans.append({
            'loan_id': f'L{loan_id:06d}',
            'borrower_id': f'B{loan_id:06d}',
            'borrower_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'national_id': generate_national_id(),
            'phone_number': generate_phone_number(),
            'address_village': address['village'],
            'address_district': address['district'],
            'latitude': address['latitude'],
            'longitude': address['longitude'],
            'amount': random.randint(product['min'], product['max']),
            'product_id': product['id'],
            'product_name': product['name'],
            'officer_id': officer['id'],
            'officer_name': officer['name'],
            'branch_id': branch['id'],
            'branch_name': branch['name'],
            'disbursement_date': base_date,
            'created_at': timestamp,  # After hours
            'status': 'active',
            'guarantor_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'guarantor_phone': generate_phone_number(),
            'is_fraud': True,
            'fraud_type': 'after_hours'
        })
    
    # Generate remaining fraud (unusual patterns)
    remaining_fraud = num_fraud - ghost_phone_count - collusion_count - after_hours_count
    for i in range(remaining_fraud):
        loan_id += 1
        officer = OFFICERS[0]  # Concentrate on one officer
        branch = next(b for b in BRANCHES if b['id'] == officer['branch'])
        product = LOAN_PRODUCTS[1]  # Higher value product
        address = generate_address(branch)
        
        loans.append({
            'loan_id': f'L{loan_id:06d}',
            'borrower_id': f'B{loan_id:06d}',
            'borrower_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'national_id': generate_national_id(),
            'phone_number': generate_phone_number(),
            'address_village': address['village'],
            'address_district': address['district'],
            'latitude': address['latitude'],
            'longitude': address['longitude'],
            'amount': random.randint(product['max'] // 2, product['max']),  # Higher amounts
            'product_id': product['id'],
            'product_name': product['name'],
            'officer_id': officer['id'],
            'officer_name': officer['name'],
            'branch_id': branch['id'],
            'branch_name': branch['name'],
            'disbursement_date': start_date + timedelta(days=random.randint(0, 334)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'status': 'active',
            'guarantor_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'guarantor_phone': generate_phone_number(),
            'is_fraud': True,
            'fraud_type': 'unusual_pattern'
        })
    
    # Generate normal loans
    for i in range(num_normal):
        loan_id += 1
        officer = random.choice(OFFICERS)
        branch = next(b for b in BRANCHES if b['id'] == officer['branch'])
        product = random.choice(LOAN_PRODUCTS)
        address = generate_address(branch)
        
        # Normal business hours
        base_date = start_date + timedelta(days=random.randint(0, 334))
        hour = random.randint(8, 17)
        timestamp = base_date.replace(hour=hour, minute=random.randint(0, 59))
        
        loans.append({
            'loan_id': f'L{loan_id:06d}',
            'borrower_id': f'B{loan_id:06d}',
            'borrower_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'national_id': generate_national_id(),
            'phone_number': generate_phone_number(),
            'address_village': address['village'],
            'address_district': address['district'],
            'latitude': address['latitude'],
            'longitude': address['longitude'],
            'amount': random.randint(product['min'], product['max']),
            'product_id': product['id'],
            'product_name': product['name'],
            'officer_id': officer['id'],
            'officer_name': officer['name'],
            'branch_id': branch['id'],
            'branch_name': branch['name'],
            'disbursement_date': base_date,
            'created_at': timestamp,
            'status': random.choice(['active', 'active', 'active', 'completed', 'defaulted']),
            'guarantor_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'guarantor_phone': generate_phone_number(),
            'is_fraud': False,
            'fraud_type': None
        })
    
    # Shuffle and return
    df = pd.DataFrame(loans)
    df = df.sample(frac=1).reset_index(drop=True)
    
    return df


if __name__ == "__main__":
    # Test generation
    data = generate_sample_data(1000, 0.05)
    print(f"Generated {len(data)} loans")
    print(f"Fraud rate: {data['is_fraud'].mean():.2%}")
    print(f"\nFraud types:")
    print(data[data['is_fraud']]['fraud_type'].value_counts())
    print(f"\nSample data:")
    print(data.head())
