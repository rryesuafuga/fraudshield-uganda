"""
Feature Engineering for Fraud Detection
Creates features from raw loan data for ML models
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional
from datetime import datetime


class FeatureEngineer:
    """
    Creates features from raw loan data for machine learning models.
    Features capture patterns related to borrowers, officers, timing, and relationships.
    """
    
    def __init__(self):
        self.fitted = False
        self.officer_stats = None
        self.branch_stats = None
        self.product_stats = None
    
    def create_features(self, data: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Create feature matrix from loan data
        
        Parameters:
        -----------
        data : pd.DataFrame
            Raw loan data
        fit : bool
            Whether to fit statistics (True for training, False for inference)
            
        Returns:
        --------
        pd.DataFrame
            Feature matrix aligned with input data
        """
        features = pd.DataFrame(index=data.index)
        
        # 1. Amount Features
        features = self._add_amount_features(data, features)
        
        # 2. Officer Features
        features = self._add_officer_features(data, features, fit)
        
        # 3. Temporal Features
        features = self._add_temporal_features(data, features)
        
        # 4. Network/Relationship Features
        features = self._add_network_features(data, features)
        
        # 5. Geographic Features
        features = self._add_geographic_features(data, features)
        
        # 6. Branch Features
        features = self._add_branch_features(data, features, fit)
        
        # 7. Borrower Features
        features = self._add_borrower_features(data, features)
        
        # Fill NaN values
        features = features.fillna(0)
        
        self.fitted = True
        
        return features
    
    def _add_amount_features(self, data: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Amount-related features"""
        if 'amount' not in data.columns:
            return features
        
        # Basic amount statistics
        features['amount'] = data['amount']
        features['amount_log'] = np.log1p(data['amount'])
        
        # Amount relative to product average
        if 'product_id' in data.columns:
            product_avg = data.groupby('product_id')['amount'].transform('mean')
            features['amount_vs_product_avg'] = data['amount'] / (product_avg + 1)
        
        # Amount relative to overall average
        overall_avg = data['amount'].mean()
        features['amount_vs_avg'] = data['amount'] / (overall_avg + 1)
        
        # Amount percentile
        features['amount_percentile'] = data['amount'].rank(pct=True)
        
        # Is amount a round number (often suspicious)
        features['is_round_amount'] = (data['amount'] % 100000 == 0).astype(int)
        
        return features
    
    def _add_officer_features(self, data: pd.DataFrame, features: pd.DataFrame, 
                              fit: bool = True) -> pd.DataFrame:
        """Officer-related features"""
        if 'officer_id' not in data.columns:
            return features
        
        # Calculate officer statistics
        if fit or self.officer_stats is None:
            self.officer_stats = data.groupby('officer_id').agg({
                'loan_id': 'count',
                'amount': ['sum', 'mean', 'std']
            })
            self.officer_stats.columns = ['officer_loan_count', 'officer_total_amount',
                                          'officer_avg_amount', 'officer_amount_std']
            self.officer_stats = self.officer_stats.fillna(0)
        
        # Merge officer stats
        officer_features = data[['officer_id']].merge(
            self.officer_stats, left_on='officer_id', right_index=True, how='left'
        )
        
        features['officer_loan_count'] = officer_features['officer_loan_count'].values
        features['officer_avg_amount'] = officer_features['officer_avg_amount'].values
        
        # Officer volume z-score
        if len(self.officer_stats) > 2:
            volume_mean = self.officer_stats['officer_loan_count'].mean()
            volume_std = self.officer_stats['officer_loan_count'].std()
            if volume_std > 0:
                features['officer_volume_z'] = (features['officer_loan_count'] - volume_mean) / volume_std
            else:
                features['officer_volume_z'] = 0
        else:
            features['officer_volume_z'] = 0
        
        # Officer approval rate (if status available)
        if 'status' in data.columns:
            officer_approval = data.groupby('officer_id').apply(
                lambda x: (x['status'] != 'rejected').mean() if len(x) > 0 else 0.5
            )
            features['officer_approval_rate'] = data['officer_id'].map(officer_approval).values
        
        return features
    
    def _add_temporal_features(self, data: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Time-related features"""
        # Use created_at or disbursement_date
        date_col = 'created_at' if 'created_at' in data.columns else 'disbursement_date'
        
        if date_col not in data.columns:
            return features
        
        dates = pd.to_datetime(data[date_col], errors='coerce')
        
        # Hour of day
        features['hour'] = dates.dt.hour.fillna(12)
        
        # Is after hours (before 6am or after 10pm)
        features['is_after_hours'] = ((features['hour'] < 6) | (features['hour'] >= 22)).astype(int)
        
        # Day of week
        features['day_of_week'] = dates.dt.dayofweek.fillna(0)
        
        # Is weekend
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        
        # Month
        features['month'] = dates.dt.month.fillna(1)
        
        # Is month end (last 3 days)
        features['is_month_end'] = (dates.dt.day > 27).astype(int)
        
        # Days since start of year
        year_start = pd.Timestamp(dates.min().year, 1, 1) if dates.notna().any() else pd.Timestamp.now()
        features['days_since_year_start'] = (dates - year_start).dt.days.fillna(0)
        
        return features
    
    def _add_network_features(self, data: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Network/relationship features"""
        # Shared phone numbers
        if 'phone_number' in data.columns:
            phone_counts = data.groupby('phone_number')['borrower_id'].transform('nunique')
            features['shared_phone_count'] = phone_counts.values
            features['has_shared_phone'] = (features['shared_phone_count'] > 1).astype(int)
        
        # Shared guarantors
        if 'guarantor_name' in data.columns:
            guarantor_counts = data.groupby('guarantor_name')['loan_id'].transform('count')
            features['shared_guarantor_count'] = guarantor_counts.values
            features['has_shared_guarantor'] = (features['shared_guarantor_count'] > 2).astype(int)
        
        # Shared national ID
        if 'national_id' in data.columns:
            id_counts = data.groupby('national_id')['loan_id'].transform('count')
            features['national_id_loan_count'] = id_counts.values
        
        return features
    
    def _add_geographic_features(self, data: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Geographic features"""
        if 'latitude' not in data.columns or 'longitude' not in data.columns:
            return features
        
        # Round coordinates for clustering
        data_copy = data.copy()
        data_copy['geo_cluster'] = (
            data_copy['latitude'].round(3).astype(str) + '_' + 
            data_copy['longitude'].round(3).astype(str)
        )
        
        # Loans in same geographic cluster
        cluster_counts = data_copy.groupby('geo_cluster')['loan_id'].transform('count')
        features['geographic_density'] = cluster_counts.values
        
        # Geographic cluster by officer
        if 'officer_id' in data.columns:
            officer_geo = data_copy.groupby(['officer_id', 'geo_cluster'])['loan_id'].transform('count')
            features['officer_geo_concentration'] = officer_geo.values
        
        return features
    
    def _add_branch_features(self, data: pd.DataFrame, features: pd.DataFrame,
                             fit: bool = True) -> pd.DataFrame:
        """Branch-related features"""
        if 'branch_id' not in data.columns:
            return features
        
        # Calculate branch statistics
        if fit or self.branch_stats is None:
            self.branch_stats = data.groupby('branch_id').agg({
                'loan_id': 'count',
                'amount': ['sum', 'mean']
            })
            self.branch_stats.columns = ['branch_loan_count', 'branch_total_amount', 'branch_avg_amount']
        
        # Merge branch stats
        branch_features = data[['branch_id']].merge(
            self.branch_stats, left_on='branch_id', right_index=True, how='left'
        )
        
        features['branch_loan_count'] = branch_features['branch_loan_count'].values
        features['branch_avg_amount'] = branch_features['branch_avg_amount'].values
        
        # Amount vs branch average
        if 'amount' in data.columns:
            features['amount_vs_branch_avg'] = data['amount'] / (features['branch_avg_amount'] + 1)
        
        return features
    
    def _add_borrower_features(self, data: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Borrower-related features"""
        if 'borrower_id' not in data.columns:
            return features
        
        # Multiple loans per borrower
        borrower_loan_count = data.groupby('borrower_id')['loan_id'].transform('count')
        features['borrower_loan_count'] = borrower_loan_count.values
        features['has_multiple_loans'] = (features['borrower_loan_count'] > 1).astype(int)
        
        # Total exposure per borrower
        if 'amount' in data.columns:
            borrower_exposure = data.groupby('borrower_id')['amount'].transform('sum')
            features['borrower_total_exposure'] = borrower_exposure.values
        
        # Borrower across multiple branches
        if 'branch_id' in data.columns:
            borrower_branches = data.groupby('borrower_id')['branch_id'].transform('nunique')
            features['borrower_branch_count'] = borrower_branches.values
            features['multi_branch_borrower'] = (features['borrower_branch_count'] > 1).astype(int)
        
        # Borrower across multiple officers
        if 'officer_id' in data.columns:
            borrower_officers = data.groupby('borrower_id')['officer_id'].transform('nunique')
            features['borrower_officer_count'] = borrower_officers.values
        
        return features
    
    def get_feature_names(self) -> list:
        """Return list of all feature names that may be created"""
        return [
            # Amount features
            'amount', 'amount_log', 'amount_vs_product_avg', 'amount_vs_avg',
            'amount_percentile', 'is_round_amount',
            # Officer features
            'officer_loan_count', 'officer_avg_amount', 'officer_volume_z',
            'officer_approval_rate',
            # Temporal features
            'hour', 'is_after_hours', 'day_of_week', 'is_weekend', 'month',
            'is_month_end', 'days_since_year_start',
            # Network features
            'shared_phone_count', 'has_shared_phone', 'shared_guarantor_count',
            'has_shared_guarantor', 'national_id_loan_count',
            # Geographic features
            'geographic_density', 'officer_geo_concentration',
            # Branch features
            'branch_loan_count', 'branch_avg_amount', 'amount_vs_branch_avg',
            # Borrower features
            'borrower_loan_count', 'has_multiple_loans', 'borrower_total_exposure',
            'borrower_branch_count', 'multi_branch_borrower', 'borrower_officer_count'
        ]


if __name__ == "__main__":
    # Test feature engineering
    from app.services.data_generator import generate_sample_data
    
    data = generate_sample_data(1000, 0.05)
    print(f"Generated {len(data)} loans")
    
    fe = FeatureEngineer()
    features = fe.create_features(data)
    
    print(f"\nCreated {len(features.columns)} features:")
    print(features.columns.tolist())
    
    print(f"\nFeature summary:")
    print(features.describe())
    
    # Check correlation with fraud
    if 'is_fraud' in data.columns:
        print("\nCorrelation with fraud:")
        correlations = features.apply(lambda x: x.corr(data['is_fraud']))
        top_corr = correlations.abs().sort_values(ascending=False).head(10)
        for feat, corr in top_corr.items():
            print(f"  {feat}: {correlations[feat]:.3f}")
