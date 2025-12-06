"""
Rule-Based Detection Engine
Statistical pattern recognition and anomaly detection without ML training
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict, Any
from datetime import datetime
import networkx as nx
from collections import defaultdict
import uuid


class RuleBasedDetector:
    """
    Rule-based fraud detection engine that works immediately without training.
    Uses statistical analysis and predefined patterns to identify anomalies.
    """
    
    def __init__(self):
        self.thresholds = {
            'z_score_threshold': 2.0,          # Standard deviations for outlier
            'approval_rate_threshold': 0.90,    # 90% approval rate is suspicious
            'volume_multiplier': 2.0,           # 2x average volume is suspicious
            'geographic_cluster_radius': 0.005, # ~500m in degrees
            'min_cluster_size': 3,              # Minimum loans to form suspicious cluster
            'shared_phone_threshold': 2,        # Same phone used by 2+ borrowers
            'shared_guarantor_threshold': 3,    # Same guarantor for 3+ loans
            'after_hours_start': 22,            # 10 PM
            'after_hours_end': 6,               # 6 AM
        }
    
    def detect_all(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Run all rule-based detection methods
        
        Parameters:
        -----------
        data : pd.DataFrame
            Loan data to analyze
            
        Returns:
        --------
        List[Dict]
            List of fraud alerts
        """
        alerts = []
        
        # 1. Ghost Loan Detection (shared identifiers)
        alerts.extend(self.detect_ghost_loans(data))
        
        # 2. Officer Anomaly Detection
        alerts.extend(self.detect_officer_anomalies(data))
        
        # 3. Geographic Clustering (Collusion)
        alerts.extend(self.detect_geographic_clusters(data))
        
        # 4. Timing Anomalies
        alerts.extend(self.detect_timing_anomalies(data))
        
        # 5. Shared Guarantor Networks
        alerts.extend(self.detect_shared_guarantors(data))
        
        # 6. Loan Stacking
        alerts.extend(self.detect_loan_stacking(data))
        
        return alerts
    
    def detect_ghost_loans(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect potential ghost loans by identifying shared phone numbers
        across different borrowers
        """
        alerts = []
        
        # Group by phone number
        phone_groups = data.groupby('phone_number').agg({
            'borrower_id': 'nunique',
            'loan_id': 'count',
            'amount': 'sum',
            'officer_id': lambda x: x.mode().iloc[0] if len(x) > 0 else None,
            'borrower_name': lambda x: list(x.unique())
        }).reset_index()
        
        # Find suspicious patterns
        suspicious = phone_groups[
            phone_groups['borrower_id'] >= self.thresholds['shared_phone_threshold']
        ]
        
        for _, row in suspicious.iterrows():
            affected_loans = data[data['phone_number'] == row['phone_number']]['loan_id'].tolist()
            
            alerts.append({
                'id': str(uuid.uuid4()),
                'type': 'ghost_loan',
                'severity': 'high',
                'title': 'Potential Ghost Loans Detected',
                'description': f"Phone number {row['phone_number']} is linked to {row['borrower_id']} different borrowers",
                'amount_at_risk': float(row['amount']),
                'detection_method': 'rule',
                'officer_id': row['officer_id'],
                'affected_loans': affected_loans,
                'evidence': {
                    'phone_number': row['phone_number'],
                    'borrower_count': int(row['borrower_id']),
                    'loan_count': int(row['loan_id']),
                    'borrower_names': row['borrower_name'][:5]  # First 5 names
                },
                'created_at': datetime.now().isoformat()
            })
        
        return alerts
    
    def detect_officer_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect officers with unusual approval patterns using z-score analysis
        """
        alerts = []
        
        # Calculate officer statistics
        officer_stats = data.groupby('officer_id').agg({
            'loan_id': 'count',
            'amount': ['sum', 'mean'],
            'officer_name': 'first',
            'branch_name': 'first'
        }).reset_index()
        
        officer_stats.columns = ['officer_id', 'loan_count', 'total_amount', 
                                  'avg_amount', 'officer_name', 'branch_name']
        
        # Calculate z-scores for volume
        if len(officer_stats) > 2:
            officer_stats['volume_z'] = stats.zscore(officer_stats['loan_count'])
            officer_stats['amount_z'] = stats.zscore(officer_stats['avg_amount'])
            
            # Find outliers
            outliers = officer_stats[
                (officer_stats['volume_z'].abs() > self.thresholds['z_score_threshold']) |
                (officer_stats['amount_z'].abs() > self.thresholds['z_score_threshold'])
            ]
            
            for _, row in outliers.iterrows():
                severity = 'high' if row['volume_z'] > 2.5 else 'medium'
                
                affected_loans = data[data['officer_id'] == row['officer_id']]['loan_id'].tolist()
                
                alerts.append({
                    'id': str(uuid.uuid4()),
                    'type': 'unusual_approval',
                    'severity': severity,
                    'title': 'Unusual Officer Activity Pattern',
                    'description': f"Officer {row['officer_name']} has {row['loan_count']} loans " +
                                   f"({row['volume_z']:.1f} std from average)",
                    'amount_at_risk': float(row['total_amount'] * 0.1),  # Estimate 10% at risk
                    'detection_method': 'rule',
                    'officer_id': row['officer_id'],
                    'affected_loans': affected_loans[:20],  # First 20
                    'evidence': {
                        'officer_name': row['officer_name'],
                        'branch': row['branch_name'],
                        'loan_count': int(row['loan_count']),
                        'volume_z_score': float(row['volume_z']),
                        'avg_amount': float(row['avg_amount']),
                        'total_amount': float(row['total_amount'])
                    },
                    'created_at': datetime.now().isoformat()
                })
        
        return alerts
    
    def detect_geographic_clusters(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect suspicious geographic clustering of loans
        """
        alerts = []
        
        # Ensure we have geographic data
        if 'latitude' not in data.columns or 'longitude' not in data.columns:
            return alerts
        
        # Filter valid coordinates
        valid_data = data.dropna(subset=['latitude', 'longitude'])
        
        if len(valid_data) < self.thresholds['min_cluster_size']:
            return alerts
        
        # Simple clustering by rounding coordinates
        valid_data = valid_data.copy()
        valid_data['geo_cluster'] = (
            valid_data['latitude'].round(3).astype(str) + '_' + 
            valid_data['longitude'].round(3).astype(str)
        )
        
        # Analyze clusters by officer
        for officer_id in valid_data['officer_id'].unique():
            officer_data = valid_data[valid_data['officer_id'] == officer_id]
            cluster_counts = officer_data['geo_cluster'].value_counts()
            
            suspicious_clusters = cluster_counts[
                cluster_counts >= self.thresholds['min_cluster_size']
            ]
            
            for cluster_id, count in suspicious_clusters.items():
                cluster_loans = officer_data[officer_data['geo_cluster'] == cluster_id]
                total_amount = cluster_loans['amount'].sum()
                
                # Calculate cluster center
                center_lat = cluster_loans['latitude'].mean()
                center_lon = cluster_loans['longitude'].mean()
                
                affected_loans = cluster_loans['loan_id'].tolist()
                
                alerts.append({
                    'id': str(uuid.uuid4()),
                    'type': 'collusion_ring',
                    'severity': 'high' if count >= 5 else 'medium',
                    'title': 'Geographic Cluster Detected',
                    'description': f"{count} loans clustered within ~500m radius for Officer {officer_id}",
                    'amount_at_risk': float(total_amount),
                    'detection_method': 'rule',
                    'officer_id': officer_id,
                    'affected_loans': affected_loans,
                    'evidence': {
                        'cluster_size': int(count),
                        'center_latitude': float(center_lat),
                        'center_longitude': float(center_lon),
                        'officer_id': officer_id,
                        'borrowers': cluster_loans['borrower_name'].tolist()[:5]
                    },
                    'created_at': datetime.now().isoformat()
                })
        
        return alerts
    
    def detect_timing_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect transactions processed outside business hours
        """
        alerts = []
        
        if 'created_at' not in data.columns:
            return alerts
        
        # Convert to datetime if needed
        data = data.copy()
        data['created_at'] = pd.to_datetime(data['created_at'])
        data['hour'] = data['created_at'].dt.hour
        
        # Find after-hours transactions
        after_hours = data[
            (data['hour'] >= self.thresholds['after_hours_start']) |
            (data['hour'] < self.thresholds['after_hours_end'])
        ]
        
        if len(after_hours) > 0:
            # Group by officer
            officer_groups = after_hours.groupby('officer_id').agg({
                'loan_id': 'count',
                'amount': 'sum',
                'officer_name': 'first'
            }).reset_index()
            
            for _, row in officer_groups.iterrows():
                affected_loans = after_hours[
                    after_hours['officer_id'] == row['officer_id']
                ]['loan_id'].tolist()
                
                alerts.append({
                    'id': str(uuid.uuid4()),
                    'type': 'timing_anomaly',
                    'severity': 'low' if row['loan_id'] < 5 else 'medium',
                    'title': 'After-Hours Transaction Activity',
                    'description': f"{row['loan_id']} loans processed outside business hours by {row['officer_name']}",
                    'amount_at_risk': float(row['amount'] * 0.05),  # 5% estimated risk
                    'detection_method': 'rule',
                    'officer_id': row['officer_id'],
                    'affected_loans': affected_loans,
                    'evidence': {
                        'after_hours_count': int(row['loan_id']),
                        'total_amount': float(row['amount']),
                        'hours': list(after_hours[after_hours['officer_id'] == row['officer_id']]['hour'].unique())
                    },
                    'created_at': datetime.now().isoformat()
                })
        
        return alerts
    
    def detect_shared_guarantors(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect suspicious networks of shared guarantors
        """
        alerts = []
        
        if 'guarantor_name' not in data.columns:
            return alerts
        
        # Group by guarantor
        guarantor_groups = data.groupby('guarantor_name').agg({
            'loan_id': 'count',
            'borrower_id': 'nunique',
            'amount': 'sum',
            'officer_id': lambda x: list(x.unique())
        }).reset_index()
        
        # Find suspicious patterns
        suspicious = guarantor_groups[
            guarantor_groups['loan_id'] >= self.thresholds['shared_guarantor_threshold']
        ]
        
        for _, row in suspicious.iterrows():
            affected_loans = data[
                data['guarantor_name'] == row['guarantor_name']
            ]['loan_id'].tolist()
            
            # Determine primary officer
            primary_officer = row['officer_id'][0] if row['officer_id'] else None
            
            alerts.append({
                'id': str(uuid.uuid4()),
                'type': 'shared_guarantor',
                'severity': 'medium' if row['loan_id'] < 5 else 'high',
                'title': 'Shared Guarantor Network',
                'description': f"Guarantor '{row['guarantor_name']}' linked to {row['loan_id']} loans across {row['borrower_id']} borrowers",
                'amount_at_risk': float(row['amount'] * 0.2),
                'detection_method': 'rule',
                'officer_id': primary_officer,
                'affected_loans': affected_loans,
                'evidence': {
                    'guarantor_name': row['guarantor_name'],
                    'loan_count': int(row['loan_id']),
                    'borrower_count': int(row['borrower_id']),
                    'officers_involved': row['officer_id']
                },
                'created_at': datetime.now().isoformat()
            })
        
        return alerts
    
    def detect_loan_stacking(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect borrowers with multiple active loans (loan stacking)
        """
        alerts = []
        
        # Filter active loans
        active_loans = data[data['status'] == 'active']
        
        # Group by borrower
        borrower_groups = active_loans.groupby('borrower_id').agg({
            'loan_id': 'count',
            'amount': 'sum',
            'borrower_name': 'first',
            'officer_id': lambda x: list(x.unique()),
            'branch_name': lambda x: list(x.unique())
        }).reset_index()
        
        # Find borrowers with multiple active loans
        stacking = borrower_groups[borrower_groups['loan_id'] >= 2]
        
        for _, row in stacking.iterrows():
            affected_loans = active_loans[
                active_loans['borrower_id'] == row['borrower_id']
            ]['loan_id'].tolist()
            
            # Higher severity if across multiple branches
            multi_branch = len(row['branch_name']) > 1
            
            alerts.append({
                'id': str(uuid.uuid4()),
                'type': 'loan_stacking',
                'severity': 'high' if multi_branch else 'medium',
                'title': 'Loan Stacking Detected',
                'description': f"Borrower {row['borrower_name']} has {row['loan_id']} active loans" +
                               (f" across {len(row['branch_name'])} branches" if multi_branch else ""),
                'amount_at_risk': float(row['amount']),
                'detection_method': 'rule',
                'officer_id': row['officer_id'][0] if row['officer_id'] else None,
                'affected_loans': affected_loans,
                'evidence': {
                    'borrower_name': row['borrower_name'],
                    'loan_count': int(row['loan_id']),
                    'total_exposure': float(row['amount']),
                    'branches': row['branch_name'],
                    'officers': row['officer_id']
                },
                'created_at': datetime.now().isoformat()
            })
        
        return alerts
    
    def build_relationship_network(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Build a network graph of relationships for visualization
        """
        nodes = []
        links = []
        node_ids = set()
        
        # Add officer nodes
        for officer_id in data['officer_id'].unique():
            officer_data = data[data['officer_id'] == officer_id].iloc[0]
            loan_count = len(data[data['officer_id'] == officer_id])
            
            nodes.append({
                'id': officer_id,
                'name': officer_data.get('officer_name', officer_id),
                'type': 'officer',
                'risk': 'high' if loan_count > 50 else 'low',
                'loan_count': loan_count
            })
            node_ids.add(officer_id)
        
        # Add borrower nodes (sample to avoid too many)
        sampled_borrowers = data.sample(min(50, len(data)))
        
        for _, row in sampled_borrowers.iterrows():
            if row['borrower_id'] not in node_ids:
                # Determine risk based on fraud indicators
                risk = 'low'
                if row.get('is_fraud', False):
                    risk = 'high'
                elif data[data['phone_number'] == row['phone_number']]['borrower_id'].nunique() > 1:
                    risk = 'medium'
                
                nodes.append({
                    'id': row['borrower_id'],
                    'name': row.get('borrower_name', row['borrower_id']),
                    'type': 'borrower',
                    'risk': risk,
                    'amount': float(row['amount'])
                })
                node_ids.add(row['borrower_id'])
                
                # Link to officer
                links.append({
                    'source': row['officer_id'],
                    'target': row['borrower_id'],
                    'type': 'approved',
                    'suspicious': risk == 'high'
                })
        
        # Find and add shared phone connections
        phone_groups = data.groupby('phone_number')['borrower_id'].apply(list)
        for phone, borrowers in phone_groups.items():
            if len(borrowers) > 1:
                for i, b1 in enumerate(borrowers[:5]):  # Limit connections
                    for b2 in borrowers[i+1:5]:
                        if b1 in node_ids and b2 in node_ids:
                            links.append({
                                'source': b1,
                                'target': b2,
                                'type': 'shared_phone',
                                'suspicious': True
                            })
        
        # Find shared guarantor connections
        if 'guarantor_name' in data.columns:
            guarantor_groups = data.groupby('guarantor_name')['borrower_id'].apply(list)
            for guarantor, borrowers in guarantor_groups.items():
                if len(borrowers) >= 3:
                    # Add guarantor node
                    guarantor_id = f"G_{hash(guarantor) % 10000:04d}"
                    if guarantor_id not in node_ids:
                        nodes.append({
                            'id': guarantor_id,
                            'name': guarantor[:20],
                            'type': 'guarantor',
                            'risk': 'high'
                        })
                        node_ids.add(guarantor_id)
                        
                        # Link to borrowers
                        for b in borrowers[:5]:
                            if b in node_ids:
                                links.append({
                                    'source': guarantor_id,
                                    'target': b,
                                    'type': 'guarantor',
                                    'suspicious': True
                                })
        
        return {
            'nodes': nodes,
            'links': links,
            'suspicious_clusters': self._find_clusters(nodes, links)
        }
    
    def _find_clusters(self, nodes: List, links: List) -> List[Dict]:
        """Find connected components that may be suspicious"""
        G = nx.Graph()
        
        for node in nodes:
            G.add_node(node['id'], **node)
        
        for link in links:
            if link.get('suspicious', False):
                G.add_edge(link['source'], link['target'])
        
        clusters = []
        for i, component in enumerate(nx.connected_components(G)):
            if len(component) >= 3:
                cluster_nodes = [n for n in nodes if n['id'] in component]
                high_risk = sum(1 for n in cluster_nodes if n.get('risk') == 'high')
                
                clusters.append({
                    'id': f'cluster_{i}',
                    'size': len(component),
                    'node_ids': list(component),
                    'high_risk_count': high_risk,
                    'risk_level': 'high' if high_risk > 2 else 'medium'
                })
        
        return sorted(clusters, key=lambda x: x['high_risk_count'], reverse=True)


if __name__ == "__main__":
    # Test with sample data
    from app.services.data_generator import generate_sample_data
    
    data = generate_sample_data(1000, 0.05)
    detector = RuleBasedDetector()
    
    alerts = detector.detect_all(data)
    
    print(f"Total alerts: {len(alerts)}")
    print("\nBy type:")
    from collections import Counter
    types = Counter(a['type'] for a in alerts)
    for t, c in types.items():
        print(f"  {t}: {c}")
    
    print("\nSample alert:")
    if alerts:
        import json
        print(json.dumps(alerts[0], indent=2, default=str))
