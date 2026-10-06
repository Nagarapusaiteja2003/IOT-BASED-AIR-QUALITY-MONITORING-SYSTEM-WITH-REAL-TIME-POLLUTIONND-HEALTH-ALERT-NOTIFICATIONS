"""
IoT-Based Air Quality Monitoring System
With Real-Time Pollution Analysis and Health Alert Notifications
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10

class AirQualitySensor:
    """Simulates IoT air quality monitoring sensors"""
    
    def __init__(self, sensor_id, location, sensor_type='PM2.5'):
        self.sensor_id = sensor_id
        self.location = location  # residential, industrial, urban, school
        self.sensor_type = sensor_type  # PM2.5, PM10, CO, CO2, Temp, Humidity
        self.current_reading = 0.0
        self.measurement_history = []
        self.sensor_status = 'normal'
        self.calibration_needed = False
        
    def read_pollutant(self, base_level, traffic_factor=0, industrial_factor=0, weather_factor=0):
        """
        Read air quality measurement with realistic sensor characteristics
        base_level: baseline pollution level
        traffic_factor: traffic intensity (0-1)
        industrial_factor: industrial activity (0-1)
        weather_factor: weather condition modifier (0-1)
        Returns: measured_value (float)
        """
        # Simulate sensor noise
        noise = np.random.normal(0, base_level * 0.05)
        
        # Calculate affected reading based on various factors
        affected_reading = base_level + (traffic_factor * base_level * 0.8) + \
                          (industrial_factor * base_level * 1.2) + \
                          (weather_factor * base_level * 0.3) + noise
        affected_reading = max(0, affected_reading)
        
        self.current_reading = affected_reading
        
        self.measurement_history.append({
            'timestamp': datetime.now(),
            'value': affected_reading,
            'sensor_id': self.sensor_id,
            'location': self.location,
            'sensor_type': self.sensor_type
        })
        
        return affected_reading


class AQICalculator:
    """Calculates Air Quality Index based on pollutant levels"""
    
    # AQI breakpoints for different pollutants
    PM25_BREAKPOINTS = {
        'good': (0, 12),
        'moderate': (12.1, 35.4),
        'unhealthy_sensitive': (35.5, 55.4),
        'unhealthy': (55.5, 150.4),
        'very_unhealthy': (150.5, 250.4),
        'hazardous': (250.5, 500)
    }
    
    PM10_BREAKPOINTS = {
        'good': (0, 54),
        'moderate': (55, 154),
        'unhealthy_sensitive': (155, 254),
        'unhealthy': (255, 354),
        'very_unhealthy': (355, 424),
        'hazardous': (425, 604)
    }
    
    CO_BREAKPOINTS = {
        'good': (0, 4.4),
        'moderate': (4.5, 9.4),
        'unhealthy_sensitive': (9.5, 12.4),
        'unhealthy': (12.5, 15.4),
        'very_unhealthy': (15.5, 30.4),
        'hazardous': (30.5, 50)
    }
    
    AQI_SCALE = {
        'good': (0, 50),
        'moderate': (51, 100),
        'unhealthy_sensitive': (101, 150),
        'unhealthy': (151, 200),
        'very_unhealthy': (201, 300),
        'hazardous': (301, 500)
    }
    
    @staticmethod
    def calculate_aqi(pm25, pm10, co):
        """Calculate overall AQI from multiple pollutants"""
        aqi_values = []
        
        # Calculate individual AQI values
        aqi_pm25 = AQICalculator._calculate_individual_aqi(pm25, AQICalculator.PM25_BREAKPOINTS)
        aqi_pm10 = AQICalculator._calculate_individual_aqi(pm10, AQICalculator.PM10_BREAKPOINTS)
        aqi_co = AQICalculator._calculate_individual_aqi(co, AQICalculator.CO_BREAKPOINTS)
        
        aqi_values = [aqi_pm25, aqi_pm10, aqi_co]
        
        # Overall AQI is the maximum of individual AQI values
        overall_aqi = max(aqi_values)
        
        return overall_aqi
    
    @staticmethod
    def _calculate_individual_aqi(concentration, breakpoints):
        """Calculate individual AQI for a pollutant"""
        for category, (low, high) in breakpoints.items():
            if low <= concentration <= high:
                # Linear interpolation
                aqi_low, aqi_high = AQICalculator.AQI_SCALE[category]
                aqi = ((aqi_high - aqi_low) / (high - low)) * (concentration - low) + aqi_low
                return aqi
        
        # If concentration exceeds all breakpoints
        return 500
    
    @staticmethod
    def get_aqi_category(aqi_value):
        """Get AQI category based on AQI value"""
        for category, (low, high) in AQICalculator.AQI_SCALE.items():
            if low <= aqi_value <= high:
                return category
        return 'hazardous'


class HealthAlertSystem:
    """Manages health alerts based on air quality levels"""
    
    HEALTH_THRESHOLDS = {
        'good': {'aqi': 50, 'pm25': 12, 'message': 'Air quality is good. Enjoy outdoor activities.'},
        'moderate': {'aqi': 100, 'pm25': 35.4, 'message': 'Air quality is acceptable. Sensitive groups should limit outdoor activities.'},
        'unhealthy_sensitive': {'aqi': 150, 'pm25': 55.4, 'message': 'Unhealthy for sensitive groups. Limit outdoor activities.'},
        'unhealthy': {'aqi': 200, 'pm25': 150.4, 'message': 'Unhealthy. Everyone should limit outdoor activities.'},
        'very_unhealthy': {'aqi': 300, 'pm25': 250.4, 'message': 'Very unhealthy. Avoid outdoor activities.'},
        'hazardous': {'aqi': 500, 'pm25': 500, 'message': 'Hazardous. Stay indoors and use air purifiers.'}
    }
    
    def __init__(self):
        self.alerts = []
        self.alert_history = []
        
    def evaluate_air_quality(self, location, aqi_value, pm25, current_time):
        """Evaluate air quality and generate health alerts"""
        alert_info = None
        category = AQICalculator.get_aqi_category(aqi_value)
        
        if aqi_value > 150:  # Unhealthy or worse
            severity = 'critical' if aqi_value > 200 else 'high'
            alert_info = {
                'timestamp': current_time,
                'location': location,
                'aqi': aqi_value,
                'pm25': pm25,
                'category': category,
                'severity': severity,
                'message': self.HEALTH_THRESHOLDS[category]['message']
            }
            
            self.alerts.append(alert_info)
            self.alert_history.append(alert_info)
        
        return alert_info


class MonitoringLocation:
    """Represents a monitoring location with multiple sensors"""
    
    def __init__(self, location_id, location_name, location_type='urban'):
        self.location_id = location_id
        self.location_name = location_name
        self.location_type = location_type  # residential, industrial, urban, school
        self.sensors = {}
        self.alert_system = HealthAlertSystem()
        self.current_aqi = 0.0
        self.aqi_category = 'good'
        self.health_alerts = []
        self.total_alerts = 0
        
    def add_sensor(self, sensor_id, sensor_type):
        """Add a sensor to the location"""
        self.sensors[sensor_id] = AirQualitySensor(sensor_id, self.location_name, sensor_type)
    
    def evaluate_location_quality(self, current_time):
        """Evaluate overall air quality at the location"""
        # Get readings from sensors
        pm25_reading = 0
        pm10_reading = 0
        co_reading = 0
        
        for sensor_id, sensor in self.sensors.items():
            if sensor.sensor_type == 'PM2.5':
                pm25_reading = sensor.current_reading
            elif sensor.sensor_type == 'PM10':
                pm10_reading = sensor.current_reading
            elif sensor.sensor_type == 'CO':
                co_reading = sensor.current_reading
        
        # Calculate AQI
        self.current_aqi = AQICalculator.calculate_aqi(pm25_reading, pm10_reading, co_reading)
        self.aqi_category = AQICalculator.get_aqi_category(self.current_aqi)
        
        # Check for health alerts
        alert = self.alert_system.evaluate_air_quality(self.location_name, self.current_aqi, pm25_reading, current_time)
        if alert:
            self.health_alerts.append(alert)
            self.total_alerts += 1


class AirQualityMonitoringSystem:
    """Main system managing air quality monitoring"""
    
    def __init__(self, system_name='Air Quality Monitoring System'):
        self.system_name = system_name
        self.locations = {}
        self.system_status = 'operational'
        self.daily_statistics = []
        self.all_alerts = []
        self.monitoring_data = []
        
    def add_location(self, location_id, location_name, location_type='urban'):
        """Add a monitoring location to the system"""
        self.locations[location_id] = MonitoringLocation(location_id, location_name, location_type)
        
    def simulate_monitoring_day(self, date=None, num_intervals=96):
        """
        Simulate a full day of air quality monitoring with 15-minute intervals
        """
        if date is None:
            date = datetime.now().date()
        
        daily_data = []
        total_alerts = 0
        critical_alerts = 0
        
        for interval in range(num_intervals):
            quarter_hour = (interval * 15) / 60
            hour = int(quarter_hour)
            minutes = int((quarter_hour % 1) * 60)
            
            current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=quarter_hour)
            
            for location_id, location in self.locations.items():
                # Generate realistic pollution patterns based on time of day
                traffic_factor = self._generate_traffic_factor(hour)
                industrial_factor = self._generate_industrial_factor(location.location_type, hour)
                weather_factor = self._generate_weather_factor(hour)
                
                # Process each sensor for the location
                for sensor_id, sensor in location.sensors.items():
                    base_level = self._get_base_level(sensor.sensor_type, location.location_type)
                    measured_value = sensor.read_pollutant(base_level, traffic_factor, industrial_factor, weather_factor)
                
                # Evaluate location quality
                location.evaluate_location_quality(current_time)
                
                # Count alerts
                if location.health_alerts and location.health_alerts[-1]['timestamp'] == current_time:
                    total_alerts += 1
                    if location.health_alerts[-1]['severity'] == 'critical':
                        critical_alerts += 1
                    self.all_alerts.append(location.health_alerts[-1])
                
                daily_data.append({
                    'date': date,
                    'time': f"{hour:02d}:{minutes:02d}",
                    'hour': hour,
                    'location_id': location_id,
                    'location_name': location.location_name,
                    'location_type': location.location_type,
                    'aqi': location.current_aqi,
                    'aqi_category': location.aqi_category,
                    'has_alert': len(location.health_alerts) > 0,
                    'total_alerts': location.total_alerts
                })
        
        self.daily_statistics.append({
            'date': date,
            'total_alerts': total_alerts,
            'critical_alerts': critical_alerts,
            'num_locations': len(self.locations),
            'system_status': self.system_status
        })
        
        return pd.DataFrame(daily_data)
    
    def _generate_traffic_factor(self, hour):
        """Generate realistic traffic patterns"""
        if 7 <= hour < 9:  # Morning rush
            return np.random.uniform(0.7, 0.95)
        elif 17 <= hour < 19:  # Evening rush
            return np.random.uniform(0.6, 0.9)
        elif 6 <= hour < 22:  # Day time
            return np.random.uniform(0.3, 0.6)
        else:  # Night time
            return np.random.uniform(0.05, 0.2)
    
    def _generate_industrial_factor(self, location_type, hour):
        """Generate industrial activity patterns"""
        if location_type == 'industrial':
            if 6 <= hour < 18:  # Working hours
                return np.random.uniform(0.5, 0.9)
            else:
                return np.random.uniform(0.1, 0.3)
        else:
            return np.random.uniform(0, 0.2)
    
    def _generate_weather_factor(self, hour):
        """Generate weather condition modifiers"""
        return np.random.uniform(0, 1)
    
    def _get_base_level(self, sensor_type, location_type):
        """Get baseline pollution level for sensor type and location"""
        base_levels = {
            'PM2.5': {'residential': 15, 'industrial': 40, 'urban': 25, 'school': 12},
            'PM10': {'residential': 30, 'industrial': 80, 'urban': 50, 'school': 25},
            'CO': {'residential': 2, 'industrial': 8, 'urban': 4, 'school': 1.5}
        }
        
        if sensor_type in base_levels:
            return base_levels[sensor_type].get(location_type, 20)
        return 20
    
    def get_system_report(self):
        """Generate comprehensive system report"""
        report = {
            'system_name': self.system_name,
            'total_locations': len(self.locations),
            'total_alerts': len(self.all_alerts),
            'critical_alerts': len([a for a in self.all_alerts if a['severity'] == 'critical']),
            'simulation_days': len(self.daily_statistics),
            'system_status': self.system_status,
            'avg_daily_alerts': np.mean([stat['total_alerts'] for stat in self.daily_statistics]) if self.daily_statistics else 0
        }
        return report


def generate_visualizations(system, daily_data):
    """Generate comprehensive visualizations for the report"""
    
    # 1. AQI Analysis by Location
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('IoT-Based Air Quality Monitoring System - AQI Analysis', 
                 fontsize=16, fontweight='bold')
    
    # Average AQI by hour
    aqi_by_hour = daily_data.groupby('hour')['aqi'].mean()
    axes[0, 0].plot(aqi_by_hour.index, aqi_by_hour.values, marker='o', linewidth=2, 
                    markersize=6, color='#E74C3C', label='Average AQI')
    axes[0, 0].axhline(y=50, color='green', linestyle='--', linewidth=2, label='Good (50)')
    axes[0, 0].axhline(y=100, color='yellow', linestyle='--', linewidth=2, label='Moderate (100)')
    axes[0, 0].axhline(y=150, color='orange', linestyle='--', linewidth=2, label='Unhealthy (150)')
    axes[0, 0].fill_between(aqi_by_hour.index, aqi_by_hour.values, alpha=0.3, color='#E74C3C')
    axes[0, 0].set_title('Average AQI by Hour', fontweight='bold')
    axes[0, 0].set_ylabel('AQI Value')
    axes[0, 0].set_xlabel('Hour of Day')
    axes[0, 0].legend(fontsize=9)
    axes[0, 0].grid(True, alpha=0.3)
    
    # AQI category distribution
    category_counts = daily_data['aqi_category'].value_counts()
    colors_map = {'good': '#2ECC71', 'moderate': '#F39C12', 'unhealthy_sensitive': '#E67E22', 
                  'unhealthy': '#E74C3C', 'very_unhealthy': '#8B0000', 'hazardous': '#000000'}
    colors = [colors_map.get(cat, 'gray') for cat in category_counts.index]
    
    axes[0, 1].bar(category_counts.index, category_counts.values, color=colors, edgecolor='black')
    axes[0, 1].set_title('AQI Category Distribution', fontweight='bold')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_xlabel('AQI Category')
    axes[0, 1].tick_params(axis='x', rotation=45)
    for i, v in enumerate(category_counts.values):
        axes[0, 1].text(i, v + 20, str(v), ha='center', fontweight='bold')
    
    # Alerts by location
    alerts_by_location = daily_data.groupby('location_name')['total_alerts'].sum()
    axes[1, 0].barh(alerts_by_location.index, alerts_by_location.values, color='#E74C3C', 
                    edgecolor='black', alpha=0.7)
    axes[1, 0].set_title('Total Alerts by Location', fontweight='bold')
    axes[1, 0].set_xlabel('Number of Alerts')
    for i, v in enumerate(alerts_by_location.values):
        axes[1, 0].text(v + 5, i, str(int(v)), va='center', fontweight='bold')
    
    # AQI by location
    aqi_by_location = daily_data.groupby('location_name')['aqi'].mean()
    axes[1, 1].bar(aqi_by_location.index, aqi_by_location.values, color='#3498DB', 
                   edgecolor='black', alpha=0.7)
    axes[1, 1].axhline(y=100, color='orange', linestyle='--', linewidth=2, label='Moderate Threshold')
    axes[1, 1].set_title('Average AQI by Location', fontweight='bold')
    axes[1, 1].set_ylabel('Average AQI')
    axes[1, 1].set_xlabel('Location')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].legend()
    for i, v in enumerate(aqi_by_location.values):
        axes[1, 1].text(i, v + 2, f'{v:.1f}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/air_quality_project/fig_aqi_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_aqi_analysis.png")
    plt.close()
    
    # 2. Health Alert Analysis
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Health Alert Analysis and Pollution Trends', fontsize=16, fontweight='bold')
    
    # Alerts by hour
    alerts_by_hour = daily_data.groupby('hour')['has_alert'].sum()
    axes[0, 0].bar(alerts_by_hour.index, alerts_by_hour.values, color='#E74C3C', edgecolor='black', alpha=0.7)
    axes[0, 0].set_title('Health Alerts by Hour', fontweight='bold')
    axes[0, 0].set_ylabel('Number of Alerts')
    axes[0, 0].set_xlabel('Hour of Day')
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # Locations with highest AQI
    location_max_aqi = daily_data.groupby('location_name')['aqi'].max()
    axes[0, 1].barh(location_max_aqi.index, location_max_aqi.values, color='#E67E22', edgecolor='black')
    axes[0, 1].set_title('Peak AQI by Location', fontweight='bold')
    axes[0, 1].set_xlabel('Maximum AQI')
    for i, v in enumerate(location_max_aqi.values):
        axes[0, 1].text(v + 2, i, f'{v:.1f}', va='center', fontweight='bold')
    
    # AQI distribution
    axes[1, 0].hist(daily_data['aqi'], bins=30, color='#3498DB', edgecolor='black', alpha=0.7)
    axes[1, 0].axvline(x=100, color='orange', linestyle='--', linewidth=2, label='Moderate (100)')
    axes[1, 0].axvline(x=150, color='red', linestyle='--', linewidth=2, label='Unhealthy (150)')
    axes[1, 0].set_title('AQI Distribution', fontweight='bold')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_xlabel('AQI Value')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Time series AQI
    hourly_aqi = daily_data.groupby('hour')['aqi'].mean()
    axes[1, 1].plot(hourly_aqi.index, hourly_aqi.values, marker='s', linewidth=2.5, 
                    markersize=7, color='#9B59B6', label='Average AQI')
    axes[1, 1].fill_between(hourly_aqi.index, hourly_aqi.values, alpha=0.3, color='#9B59B6')
    axes[1, 1].set_title('AQI Trend Throughout the Day', fontweight='bold')
    axes[1, 1].set_ylabel('AQI Value')
    axes[1, 1].set_xlabel('Hour of Day')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/air_quality_project/fig_alert_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_alert_analysis.png")
    plt.close()
    
    # 3. System Architecture Diagram
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    ax.text(0.5, 0.95, 'IoT-Based Air Quality Monitoring System Architecture', 
            ha='center', fontsize=16, fontweight='bold', transform=ax.transAxes)
    
    components = [
        ('PM2.5\nSensor', 0.15, 0.75),
        ('PM10\nSensor', 0.5, 0.75),
        ('CO\nSensor', 0.85, 0.75),
        ('IoT\nCommunication\nModule', 0.5, 0.55),
        ('Cloud\nServer', 0.15, 0.35),
        ('AQI\nCalculator', 0.5, 0.35),
        ('Health Alert\nSystem', 0.85, 0.35),
    ]
    
    for label, x, y in components:
        bbox = dict(boxstyle='round,pad=0.6', facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold',
                transform=ax.transAxes, bbox=bbox)
    
    connections = [
        ((0.25, 0.75), (0.4, 0.75)),
        ((0.6, 0.75), (0.75, 0.75)),
        ((0.5, 0.65), (0.5, 0.60)),
        ((0.25, 0.65), (0.25, 0.60)),
        ((0.75, 0.65), (0.75, 0.60)),
    ]
    
    for start, end in connections:
        ax.annotate('', xy=end, xytext=start, transform=ax.transAxes,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    features_text = 'Key Features:\n• Real-time Air Quality Monitoring\n• Multi-pollutant Detection\n• Automated Health Alerts\n• AQI Calculation\n• Cloud-based Dashboard'
    ax.text(0.5, 0.15, features_text, ha='center', va='top', fontsize=10,
            transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='lightyellow', 
            edgecolor='black', linewidth=1.5))
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/air_quality_project/fig_system_architecture.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_system_architecture.png")
    plt.close()
    
    # 4. Daily Performance
    fig, ax = plt.subplots(figsize=(12, 6))
    
    daily_stats = pd.DataFrame(system.daily_statistics)
    
    x = np.arange(len(daily_stats))
    width = 0.35
    
    ax.bar(x - width/2, daily_stats['total_alerts'], width, label='Total Alerts', 
           color='#F39C12', edgecolor='black')
    ax2 = ax.twinx()
    ax2.bar(x + width/2, daily_stats['critical_alerts'], width, label='Critical Alerts', 
            color='#E74C3C', alpha=0.7, edgecolor='black')
    
    ax.set_xlabel('Day', fontweight='bold')
    ax.set_ylabel('Total Alerts', fontweight='bold', color='#F39C12')
    ax2.set_ylabel('Critical Alerts', fontweight='bold', color='#E74C3C')
    ax.set_title('Daily System Performance and Alert Trends', fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Day {i+1}" for i in range(len(daily_stats))])
    ax.grid(True, alpha=0.3, axis='y')
    
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/air_quality_project/fig_daily_performance.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_daily_performance.png")
    plt.close()
    
    # 5. Location Heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    
    location_activity = daily_data.pivot_table(values='aqi', index='location_name', 
                                              columns='hour', aggfunc='mean', fill_value=0)
    
    sns.heatmap(location_activity, cmap='RdYlGn_r', annot=True, fmt='.0f', cbar_kws={'label': 'AQI'},
                ax=ax, linewidths=0.5, linecolor='gray', vmin=0, vmax=200)
    ax.set_title('Air Quality Index Heatmap - AQI by Location and Hour', fontweight='bold', fontsize=14)
    ax.set_xlabel('Hour of Day', fontweight='bold')
    ax.set_ylabel('Location Name', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/air_quality_project/fig_aqi_heatmap.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_aqi_heatmap.png")
    plt.close()


def main():
    """Main execution function"""
    print("=" * 70)
    print("IOT-BASED AIR QUALITY MONITORING SYSTEM SIMULATION")
    print("=" * 70)
    
    # Initialize system
    system = AirQualityMonitoringSystem("Air Quality Monitoring System")
    
    # Add monitoring locations
    locations_config = {
        'LOC-001': {'name': 'Residential Area A', 'type': 'residential'},
        'LOC-002': {'name': 'Industrial Zone B', 'type': 'industrial'},
        'LOC-003': {'name': 'Urban Center C', 'type': 'urban'},
        'LOC-004': {'name': 'School Campus D', 'type': 'school'},
        'LOC-005': {'name': 'Commercial Hub E', 'type': 'urban'},
    }
    
    for location_id, config in locations_config.items():
        system.add_location(location_id, config['name'], config['type'])
        location = system.locations[location_id]
        
        # Add sensors to each location
        location.add_sensor(f"{location_id}-PM25", 'PM2.5')
        location.add_sensor(f"{location_id}-PM10", 'PM10')
        location.add_sensor(f"{location_id}-CO", 'CO')
    
    print(f"\nSystem initialized with {len(locations_config)} monitoring locations:")
    for location_id, config in locations_config.items():
        print(f"  - {location_id}: {config['name']} ({config['type']})")
    
    # Simulate 7 days
    print("\nSimulating 7 days of air quality monitoring...")
    all_data = []
    
    for day in range(7):
        simulation_date = datetime.now().date() - timedelta(days=6-day)
        daily_data = system.simulate_monitoring_day(simulation_date)
        all_data.append(daily_data)
        
        daily_stats = system.daily_statistics[-1]
        print(f"Day {day+1}: Alerts={daily_stats['total_alerts']}, "
              f"Critical={daily_stats['critical_alerts']}")
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    generate_visualizations(system, combined_data)
    
    # Generate report data
    report = system.get_system_report()
    
    print("\n" + "=" * 70)
    print("SYSTEM REPORT")
    print("=" * 70)
    print(f"System Name: {report['system_name']}")
    print(f"Total Locations Monitored: {report['total_locations']}")
    print(f"Total Alerts Generated: {report['total_alerts']}")
    print(f"Critical Alerts: {report['critical_alerts']}")
    print(f"Average Daily Alerts: {report['avg_daily_alerts']:.1f}")
    print(f"System Status: {report['system_status']}")
    print(f"Simulation Period: {report['simulation_days']} days")
    print("=" * 70)
    
    # Save data to CSV
    combined_data.to_csv('/home/ubuntu/air_quality_project/monitoring_data.csv', index=False)
    print("\nMonitoring data saved to: monitoring_data.csv")
    
    # Save report to JSON
    report_json = {
        'system_report': report,
        'locations': list(locations_config.keys()),
        'simulation_date': datetime.now().isoformat(),
        'daily_statistics': system.daily_statistics,
        'total_alerts': len(system.all_alerts)
    }
    
    with open('/home/ubuntu/air_quality_project/system_report.json', 'w') as f:
        json.dump(report_json, f, indent=2, default=str)
    
    print("System report saved to: system_report.json")
    
    return system, combined_data


if __name__ == "__main__":
    system, data = main()
