"""
Smart Column Mapping System
Uses pattern matching, fuzzy matching, and ML to automatically detect column types
from CSV/Excel files with various naming conventions.

This allows FraudShield to accept data exports from ANY banking/SACCO system
without requiring a specific format.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter
from difflib import SequenceMatcher
from dataclasses import dataclass


@dataclass
class ColumnMapping:
    """Result of column type detection"""
    original_name: str
    standard_name: str
    confidence: float
    detection_method: str
    sample_values: List[Any]


class SmartColumnMapper:
    """
    Intelligently maps columns from uploaded data to standard FraudShield fields.

    Uses three detection methods:
    1. Fuzzy Name Matching - Match column names to known variations
    2. Pattern Detection - Detect data types from content patterns (phone, date, etc.)
    3. Statistical Analysis - Infer type from data characteristics
    """

    # Standard field names that FraudShield expects
    STANDARD_FIELDS = {
        'loan_id': 'Unique loan identifier',
        'borrower_id': 'Unique borrower/member identifier',
        'borrower_name': 'Full name of borrower',
        'phone': 'Phone number (primary)',
        'national_id': 'National ID or similar identifier',
        'amount': 'Loan amount',
        'loan_date': 'Date loan was issued',
        'disbursement_date': 'Date funds were disbursed',
        'approval_time': 'Time of approval',
        'officer_id': 'Loan officer identifier',
        'officer_name': 'Loan officer name',
        'branch': 'Branch name or code',
        'status': 'Loan status (active/paid/defaulted)',
        'guarantor_name': 'Name of guarantor',
        'guarantor_phone': 'Guarantor phone number',
        'repayment_amount': 'Monthly/scheduled repayment',
        'interest_rate': 'Interest rate',
        'term_months': 'Loan term in months',
        'purpose': 'Loan purpose/product type',
        'address': 'Borrower address',
        'latitude': 'GPS latitude',
        'longitude': 'GPS longitude'
    }

    # Common column name variations for each standard field
    NAME_VARIATIONS = {
        'loan_id': [
            'loan_id', 'loanid', 'loan_no', 'loan_number', 'loan_ref', 'reference',
            'loan_reference', 'contract_id', 'contract_no', 'application_id',
            'disbursement_id', 'txn_id', 'transaction_id', 'id', 'ref_no'
        ],
        'borrower_id': [
            'borrower_id', 'borrowerid', 'member_id', 'memberid', 'client_id',
            'clientid', 'customer_id', 'customerid', 'member_no', 'member_number',
            'client_no', 'account_no', 'account_number', 'sacco_no'
        ],
        'borrower_name': [
            'borrower_name', 'borrowername', 'name', 'full_name', 'fullname',
            'member_name', 'membername', 'client_name', 'clientname',
            'customer_name', 'customername', 'applicant_name', 'applicant'
        ],
        'phone': [
            'phone', 'phone_number', 'phonenumber', 'mobile', 'mobile_number',
            'mobilenumber', 'telephone', 'tel', 'contact', 'contact_number',
            'cell', 'cellphone', 'phone_no', 'tel_no', 'mobile_no'
        ],
        'national_id': [
            'national_id', 'nationalid', 'national_id_no', 'nin', 'id_no',
            'id_number', 'idno', 'national_identification', 'id_card',
            'identification', 'nid', 'govt_id', 'government_id'
        ],
        'amount': [
            'amount', 'loan_amount', 'loanamount', 'principal', 'principal_amount',
            'disbursed_amount', 'disbursement', 'approved_amount', 'requested_amount',
            'credit_amount', 'facility_amount', 'sum', 'total', 'value'
        ],
        'loan_date': [
            'loan_date', 'loandate', 'disbursement_date', 'date_disbursed',
            'issue_date', 'created_date', 'application_date', 'approved_date',
            'date', 'transaction_date', 'txn_date', 'start_date'
        ],
        'disbursement_date': [
            'disbursement_date', 'disbursed_date', 'date_disbursed',
            'payout_date', 'release_date', 'date_released'
        ],
        'approval_time': [
            'approval_time', 'time', 'created_at', 'timestamp', 'datetime',
            'approved_time', 'creation_time', 'entry_time'
        ],
        'officer_id': [
            'officer_id', 'officerid', 'loan_officer_id', 'staff_id', 'staffid',
            'employee_id', 'employeeid', 'user_id', 'userid', 'approved_by',
            'created_by', 'processed_by', 'agent_id', 'agent_code'
        ],
        'officer_name': [
            'officer_name', 'officername', 'loan_officer', 'loanofficer',
            'staff_name', 'staffname', 'approved_by_name', 'agent_name'
        ],
        'branch': [
            'branch', 'branch_name', 'branchname', 'branch_id', 'branchid',
            'branch_code', 'location', 'office', 'center', 'unit'
        ],
        'status': [
            'status', 'loan_status', 'loanstatus', 'state', 'current_status',
            'account_status', 'disbursement_status'
        ],
        'guarantor_name': [
            'guarantor_name', 'guarantorname', 'guarantor', 'witness',
            'reference_name', 'referee_name', 'co_applicant'
        ],
        'guarantor_phone': [
            'guarantor_phone', 'guarantorphone', 'guarantor_mobile',
            'guarantor_contact', 'referee_phone', 'witness_phone'
        ],
        'repayment_amount': [
            'repayment_amount', 'repayment', 'installment', 'monthly_payment',
            'emi', 'periodic_payment', 'payment_amount'
        ],
        'interest_rate': [
            'interest_rate', 'interestrate', 'rate', 'int_rate', 'interest'
        ],
        'term_months': [
            'term_months', 'term', 'tenure', 'loan_term', 'duration',
            'months', 'period', 'repayment_period'
        ],
        'purpose': [
            'purpose', 'loan_purpose', 'product', 'product_type', 'loan_type',
            'facility_type', 'category', 'use_of_funds'
        ],
        'address': [
            'address', 'residential_address', 'home_address', 'location',
            'village', 'parish', 'district', 'region'
        ],
        'latitude': [
            'latitude', 'lat', 'gps_lat', 'y_coordinate', 'geo_lat'
        ],
        'longitude': [
            'longitude', 'lon', 'long', 'lng', 'gps_lon', 'gps_long',
            'x_coordinate', 'geo_lon', 'geo_long'
        ]
    }

    # Regular expressions for detecting data types from content
    PATTERNS = {
        'phone': [
            r'^\+?256\d{9}$',           # Uganda format
            r'^0\d{9}$',                 # Local format
            r'^\+?\d{10,15}$',           # International format
            r'^07\d{8}$',                # Uganda mobile
            r'^256\d{9}$'                # Without plus
        ],
        'national_id': [
            r'^[A-Z]{2}\d{13}[A-Z0-9]$',  # Uganda NIN format
            r'^CF\d{13}[A-Z]$',            # Common Uganda NIN
            r'^CM\d{13}[A-Z]$',
            r'^\d{14}$'                    # Numeric only
        ],
        'date': [
            r'^\d{4}-\d{2}-\d{2}$',       # ISO format
            r'^\d{2}/\d{2}/\d{4}$',       # DD/MM/YYYY
            r'^\d{2}-\d{2}-\d{4}$',       # DD-MM-YYYY
            r'^\d{4}/\d{2}/\d{2}$',       # YYYY/MM/DD
        ],
        'time': [
            r'^\d{2}:\d{2}(:\d{2})?$',    # HH:MM or HH:MM:SS
        ],
        'amount': [
            r'^\d{1,3}(,\d{3})*(\.\d{2})?$',  # Formatted currency
            r'^\d+\.?\d*$',                     # Plain number
        ],
        'email': [
            r'^[\w\.-]+@[\w\.-]+\.\w+$'
        ]
    }

    def __init__(self):
        self.mappings: Dict[str, ColumnMapping] = {}
        self.unmapped_columns: List[str] = []

    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, ColumnMapping]:
        """
        Analyze a DataFrame and return mapping suggestions for each column.

        Parameters:
        -----------
        df : pd.DataFrame
            Input data to analyze

        Returns:
        --------
        Dict[str, ColumnMapping]
            Mapping from original column names to ColumnMapping objects
        """
        self.mappings = {}
        self.unmapped_columns = []

        for col in df.columns:
            mapping = self._analyze_column(df, col)
            if mapping:
                self.mappings[col] = mapping
            else:
                self.unmapped_columns.append(col)

        # Resolve conflicts (multiple columns mapped to same standard field)
        self._resolve_conflicts()

        return self.mappings

    def _analyze_column(self, df: pd.DataFrame, col: str) -> Optional[ColumnMapping]:
        """Analyze a single column and determine its type"""

        # Get sample values (non-null)
        sample = df[col].dropna().head(100).tolist()
        if not sample:
            return None

        # Method 1: Fuzzy name matching (highest priority for clear matches)
        name_match = self._match_by_name(col)
        if name_match and name_match[1] > 0.8:
            return ColumnMapping(
                original_name=col,
                standard_name=name_match[0],
                confidence=name_match[1],
                detection_method='name_matching',
                sample_values=sample[:5]
            )

        # Method 2: Pattern detection from content
        pattern_match = self._match_by_pattern(sample)
        if pattern_match and pattern_match[1] > 0.7:
            return ColumnMapping(
                original_name=col,
                standard_name=pattern_match[0],
                confidence=pattern_match[1],
                detection_method='pattern_detection',
                sample_values=sample[:5]
            )

        # Method 3: Statistical analysis
        stat_match = self._match_by_statistics(df, col, sample)
        if stat_match and stat_match[1] > 0.6:
            return ColumnMapping(
                original_name=col,
                standard_name=stat_match[0],
                confidence=stat_match[1],
                detection_method='statistical_analysis',
                sample_values=sample[:5]
            )

        # Method 4: Name matching with lower threshold
        if name_match and name_match[1] > 0.5:
            return ColumnMapping(
                original_name=col,
                standard_name=name_match[0],
                confidence=name_match[1],
                detection_method='name_matching_low',
                sample_values=sample[:5]
            )

        return None

    def _match_by_name(self, col: str) -> Optional[Tuple[str, float]]:
        """Match column name to standard fields using fuzzy matching"""
        col_clean = col.lower().strip().replace(' ', '_').replace('-', '_')

        best_match = None
        best_score = 0

        for standard_field, variations in self.NAME_VARIATIONS.items():
            for variation in variations:
                # Exact match
                if col_clean == variation:
                    return (standard_field, 1.0)

                # Contains check
                if variation in col_clean or col_clean in variation:
                    score = 0.85
                    if score > best_score:
                        best_score = score
                        best_match = standard_field

                # Fuzzy matching
                similarity = SequenceMatcher(None, col_clean, variation).ratio()
                if similarity > best_score:
                    best_score = similarity
                    best_match = standard_field

        return (best_match, best_score) if best_match else None

    def _match_by_pattern(self, sample: List[Any]) -> Optional[Tuple[str, float]]:
        """Detect column type by analyzing content patterns"""

        # Convert to strings for pattern matching
        str_sample = [str(v) for v in sample if pd.notna(v)]
        if not str_sample:
            return None

        # Check each pattern type
        pattern_scores = {}

        for pattern_type, patterns in self.PATTERNS.items():
            matches = 0
            for value in str_sample:
                value_clean = value.strip()
                for pattern in patterns:
                    if re.match(pattern, value_clean):
                        matches += 1
                        break

            if matches > 0:
                score = matches / len(str_sample)
                pattern_scores[pattern_type] = score

        # Map pattern type to standard field
        pattern_to_field = {
            'phone': 'phone',
            'national_id': 'national_id',
            'date': 'loan_date',
            'time': 'approval_time',
            'amount': 'amount',
            'email': 'email'
        }

        if pattern_scores:
            best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
            if best_pattern[1] > 0.5:
                return (pattern_to_field.get(best_pattern[0]), best_pattern[1])

        return None

    def _match_by_statistics(self, df: pd.DataFrame, col: str,
                             sample: List[Any]) -> Optional[Tuple[str, float]]:
        """Infer column type from statistical characteristics"""

        # Check if numeric
        try:
            numeric_values = pd.to_numeric(df[col].dropna(), errors='coerce')
            numeric_ratio = numeric_values.notna().sum() / len(df[col].dropna())

            if numeric_ratio > 0.9:
                # It's a numeric column
                values = numeric_values.dropna()
                if len(values) == 0:
                    return None

                mean_val = values.mean()
                min_val = values.min()
                max_val = values.max()

                # Amount detection: positive, large values, wide range
                if min_val >= 0 and mean_val > 10000:
                    return ('amount', 0.75)

                # Interest rate: 0-100 range, decimals
                if 0 <= min_val and max_val <= 100:
                    return ('interest_rate', 0.6)

                # Term months: small integers
                if min_val >= 1 and max_val <= 360 and values.dtype == int:
                    return ('term_months', 0.6)

                # Latitude/Longitude ranges
                if -90 <= min_val <= 90 and -90 <= max_val <= 90:
                    # Check if looks like coordinates
                    if values.apply(lambda x: len(str(x).split('.')[-1]) > 4 if '.' in str(x) else False).mean() > 0.5:
                        return ('latitude', 0.65)

                if -180 <= min_val <= 180 and -180 <= max_val <= 180:
                    if values.apply(lambda x: len(str(x).split('.')[-1]) > 4 if '.' in str(x) else False).mean() > 0.5:
                        return ('longitude', 0.65)
        except:
            pass

        # Check if it's a date column
        try:
            date_parsed = pd.to_datetime(df[col], errors='coerce')
            date_ratio = date_parsed.notna().sum() / len(df[col].dropna())
            if date_ratio > 0.8:
                return ('loan_date', 0.7)
        except:
            pass

        # Check for ID patterns (unique values, alphanumeric)
        str_sample = [str(v) for v in sample]
        unique_ratio = len(set(str_sample)) / len(str_sample)

        if unique_ratio > 0.95:
            # Likely an ID column
            avg_len = np.mean([len(s) for s in str_sample])
            if avg_len < 15:
                return ('loan_id', 0.6)
            elif avg_len < 25:
                return ('borrower_id', 0.55)

        # Check for name patterns (title case, spaces, 2-4 words)
        name_pattern = sum(1 for s in str_sample if self._looks_like_name(s)) / len(str_sample)
        if name_pattern > 0.7:
            return ('borrower_name', 0.7)

        # Check for status patterns
        unique_values = set([str(v).lower() for v in sample])
        status_keywords = {'active', 'inactive', 'paid', 'closed', 'pending',
                          'approved', 'rejected', 'defaulted', 'written_off',
                          'disbursed', 'completed', 'overdue'}
        if unique_values & status_keywords:
            return ('status', 0.8)

        return None

    def _looks_like_name(self, value: str) -> bool:
        """Check if a string looks like a person's name"""
        if not isinstance(value, str):
            return False

        # Names typically: 2-4 words, mostly alphabetic, title case
        words = value.strip().split()
        if not (2 <= len(words) <= 4):
            return False

        for word in words:
            if not word.replace('-', '').replace("'", '').isalpha():
                return False

        return True

    def _resolve_conflicts(self):
        """Resolve conflicts where multiple columns map to the same standard field"""

        # Group by standard name
        by_standard: Dict[str, List[Tuple[str, ColumnMapping]]] = {}
        for orig, mapping in self.mappings.items():
            if mapping.standard_name not in by_standard:
                by_standard[mapping.standard_name] = []
            by_standard[mapping.standard_name].append((orig, mapping))

        # For conflicts, keep highest confidence
        for standard_name, candidates in by_standard.items():
            if len(candidates) > 1:
                # Sort by confidence descending
                candidates.sort(key=lambda x: x[1].confidence, reverse=True)

                # Keep the best, move others to unmapped
                best = candidates[0]
                for orig, mapping in candidates[1:]:
                    del self.mappings[orig]
                    self.unmapped_columns.append(orig)

    def apply_mapping(self, df: pd.DataFrame,
                      custom_overrides: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Apply the detected mappings to rename columns.

        Parameters:
        -----------
        df : pd.DataFrame
            Input DataFrame
        custom_overrides : Dict[str, str], optional
            Manual overrides for column mappings {original_name: standard_name}

        Returns:
        --------
        pd.DataFrame
            DataFrame with standardized column names
        """
        # Start with detected mappings
        rename_map = {m.original_name: m.standard_name for m in self.mappings.values()}

        # Apply custom overrides
        if custom_overrides:
            rename_map.update(custom_overrides)

        # Rename columns
        df_renamed = df.rename(columns=rename_map)

        return df_renamed

    def get_mapping_report(self) -> Dict[str, Any]:
        """Generate a report of the column mapping analysis"""

        mapped = []
        for orig, mapping in self.mappings.items():
            mapped.append({
                'original': orig,
                'standard': mapping.standard_name,
                'confidence': round(mapping.confidence * 100, 1),
                'method': mapping.detection_method,
                'samples': mapping.sample_values[:3]
            })

        return {
            'total_columns': len(self.mappings) + len(self.unmapped_columns),
            'mapped_columns': len(self.mappings),
            'unmapped_columns': len(self.unmapped_columns),
            'mappings': sorted(mapped, key=lambda x: x['confidence'], reverse=True),
            'unmapped': self.unmapped_columns,
            'required_fields_found': self._check_required_fields()
        }

    def _check_required_fields(self) -> Dict[str, bool]:
        """Check if minimum required fields are detected"""
        required = ['loan_id', 'borrower_id', 'amount', 'officer_id']
        important = ['phone', 'loan_date', 'borrower_name', 'branch', 'status']

        mapped_standards = {m.standard_name for m in self.mappings.values()}

        return {
            'required': {f: f in mapped_standards for f in required},
            'important': {f: f in mapped_standards for f in important},
            'can_analyze': all(f in mapped_standards for f in ['borrower_id', 'amount'])
        }


def auto_map_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to automatically map columns and return standardized DataFrame.

    Parameters:
    -----------
    df : pd.DataFrame
        Input data with unknown column names

    Returns:
    --------
    Tuple[pd.DataFrame, Dict]
        (Standardized DataFrame, Mapping report)
    """
    mapper = SmartColumnMapper()
    mapper.analyze_dataframe(df)
    df_standard = mapper.apply_mapping(df)
    report = mapper.get_mapping_report()

    return df_standard, report


if __name__ == "__main__":
    # Test with sample data
    import io

    # Simulate a CSV with non-standard column names
    csv_data = """
    ref_no,member_no,full_name,mobile_number,principal_amount,disbursed_date,created_at,staff_id,office,loan_status
    LN001,M001,John Mukasa,0772123456,2500000,2024-01-15,09:30:00,S001,Kampala,active
    LN002,M002,Sarah Nambi,0753456789,1500000,2024-01-16,14:45:00,S002,Entebbe,active
    LN003,M003,Peter Okello,0772123456,3000000,2024-01-17,11:20:00,S001,Kampala,active
    LN004,M004,Grace Auma,+256701234567,2000000,2024-01-18,16:00:00,S003,Jinja,paid
    LN005,M005,James Ssempala,0782999888,4500000,2024-01-19,08:15:00,S001,Kampala,active
    """

    df = pd.read_csv(io.StringIO(csv_data.strip()))
    print("Original columns:", df.columns.tolist())

    # Auto-map columns
    df_standard, report = auto_map_columns(df)

    print("\n=== Column Mapping Report ===")
    print(f"Total: {report['total_columns']}, Mapped: {report['mapped_columns']}, Unmapped: {report['unmapped_columns']}")

    print("\nMappings:")
    for m in report['mappings']:
        print(f"  {m['original']:<20} -> {m['standard']:<20} ({m['confidence']}% by {m['method']})")

    print("\nUnmapped:", report['unmapped'])
    print("\nRequired fields found:", report['required_fields_found'])

    print("\nStandardized columns:", df_standard.columns.tolist())
