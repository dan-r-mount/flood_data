#!/usr/bin/env python3
"""
Integrated Flood Risk Checker
Combines FRA shapefile data, Environment Agency reservoir API, and rivers/sea datasets.
"""

import argparse
import sys
import geopandas as gpd
import requests
import json
from shapely.geometry import Point
from typing import Optional, Dict, List, Tuple
import pandas as pd
from urllib.parse import unquote


class IntegratedFloodRiskChecker:
    """Integrated flood risk checker using multiple data sources."""
    
    def __init__(self, 
                 fra_shapefile_path: str = "Flood_Risk_AreasPolygon.shp",
                 datasets_dir: str = "flood_datasets"):
        """Initialize the integrated flood risk checker."""
        self.fra_shapefile_path = fra_shapefile_path
        self.datasets_dir = datasets_dir
        self.fra_data = None
        self.rivers_sea_data = None
        
        # Reservoir API configuration from example_api.json
        self.reservoir_api_base = "https://environment.data.gov.uk/geoservices/datasets/db114020-465a-412b-b289-be393d995a75/ogc/features/v1"
        
        self._load_data_sources()
    
    def _load_data_sources(self) -> None:
        """Load all available data sources."""
        print("Loading flood risk data sources...")
        
        # Load FRA data (existing)
        try:
            self.fra_data = gpd.read_file(self.fra_shapefile_path)
            print(f"✅ Loaded {len(self.fra_data)} Flood Risk Areas")
            
            if self.fra_data.crs.to_epsg() != 27700:
                self.fra_data = self.fra_data.to_crs(epsg=27700)
        except Exception as e:
            print(f"❌ Error loading FRA data: {e}")
        
        # Try to load rivers/sea data if available
        try:
            rivers_sea_path = f"{self.datasets_dir}/rivers_sea"
            # Look for shapefiles in the rivers_sea directory
            import glob
            shp_files = glob.glob(f"{rivers_sea_path}/*.shp")
            if shp_files:
                self.rivers_sea_data = gpd.read_file(shp_files[0])
                print(f"✅ Loaded rivers/sea data: {len(self.rivers_sea_data)} features")
                if self.rivers_sea_data.crs.to_epsg() != 27700:
                    self.rivers_sea_data = self.rivers_sea_data.to_crs(epsg=27700)
            else:
                print("⚠️  No rivers/sea shapefile found - using FRA data only for rivers/sea")
        except Exception as e:
            print(f"⚠️  Rivers/sea data not available: {e}")
    
    def postcode_to_coordinates(self, postcode: str) -> Optional[tuple]:
        """Convert postcode to British National Grid coordinates."""
        try:
            postcode = postcode.strip().upper().replace(" ", "")
            url = f"https://api.postcodes.io/postcodes/{postcode}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 200:
                    result = data['result']
                    easting = result['eastings']
                    northing = result['northings']
                    return (easting, northing)
            
            print(f"Failed to find coordinates for postcode: {postcode}")
            return None
            
        except Exception as e:
            print(f"Error converting postcode to coordinates: {e}")
            return None
    
    def check_reservoir_risk_api(self, coordinates: tuple) -> Dict:
        """Check reservoir flood risk using Environment Agency API."""
        if not coordinates:
            return {"risk_level": "UNKNOWN", "reason": "No coordinates provided"}
        
        try:
            easting, northing = coordinates
            
            # Query the reservoir API for features at this location
            # Using bbox query around the point (±100m buffer)
            buffer = 100
            bbox = f"{easting-buffer},{northing-buffer},{easting+buffer},{northing+buffer}"
            
            collections_url = f"{self.reservoir_api_base}/collections"
            print(f"Querying reservoir API...")
            
            # First, get available collections
            response = requests.get(f"{collections_url}?f=json", timeout=15)
            
            if response.status_code == 200:
                collections_data = response.json()
                
                if 'collections' in collections_data:
                    # Look for reservoir flood extent collections
                    reservoir_collections = []
                    for collection in collections_data['collections']:
                        if 'reservoir' in collection.get('title', '').lower() or \
                           'flood' in collection.get('title', '').lower():
                            reservoir_collections.append(collection)
                    
                    if reservoir_collections:
                        # Query the first relevant collection
                        collection_id = reservoir_collections[0]['id']
                        features_url = f"{collections_url}/{collection_id}/items"
                        
                        # Query with bbox
                        params = {
                            'f': 'json',
                            'bbox': bbox,
                            'limit': 10
                        }
                        
                        features_response = requests.get(features_url, params=params, timeout=15)
                        
                        if features_response.status_code == 200:
                            features_data = features_response.json()
                            
                            if 'features' in features_data and len(features_data['features']) > 0:
                                # Check if point intersects with any reservoir flood areas
                                point = Point(easting, northing)
                                
                                reservoir_areas = []
                                for feature in features_data['features']:
                                    properties = feature.get('properties', {})
                                    reservoir_areas.append({
                                        'name': properties.get('reservoir_name', 'Unknown Reservoir'),
                                        'type': properties.get('flood_type', 'Reservoir Failure'),
                                        'scenario': properties.get('scenario', 'Worst Case')
                                    })
                                
                                if reservoir_areas:
                                    return {
                                        "risk_level": "MEDIUM",
                                        "areas_count": len(reservoir_areas),
                                        "reservoirs": reservoir_areas,
                                        "note": "You are within a reservoir flood risk area"
                                    }
                
                return {
                    "risk_level": "VERY LOW", 
                    "areas_count": 0,
                    "note": "No reservoir flood risk areas found at this location"
                }
            else:
                return {
                    "risk_level": "DATA UNAVAILABLE",
                    "reason": f"API returned status {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "risk_level": "DATA UNAVAILABLE",
                "reason": "API request timed out"
            }
        except Exception as e:
            return {
                "risk_level": "DATA UNAVAILABLE", 
                "reason": f"API error: {str(e)}"
            }
    
    def calculate_distance_to_flood_areas(self, coordinates: tuple, data_source: gpd.GeoDataFrame) -> List[Dict]:
        """Calculate distance from coordinates to flood risk areas in a dataset."""
        if not coordinates or data_source is None or data_source.empty:
            return []
            
        easting, northing = coordinates
        point = Point(easting, northing)
        
        results = []
        
        for _, area in data_source.iterrows():
            is_inside = area.geometry.contains(point)
            
            if is_inside:
                distance = 0.0
                risk_status = "INSIDE"
            else:
                distance = point.distance(area.geometry)
                risk_status = "OUTSIDE"
            
            # Handle different data structures
            area_info = {
                'distance_meters': round(distance, 2),
                'risk_status': risk_status,
                'geometry': area.geometry
            }
            
            # Try to extract common fields (different datasets have different schemas)
            if 'fra_id' in area:
                area_info.update({
                    'id': area['fra_id'],
                    'name': area['fra_name'],
                    'source': area['flood_sour'],
                    'cycle': area.get('frr_cycle', 'Unknown')
                })
            elif 'prob_4band' in area:  # Rivers/Sea probability data
                area_info.update({
                    'id': f"Rivers_Sea_{len(results)}",
                    'name': f"Rivers and Sea Risk Area",
                    'source': 'Rivers and Sea',
                    'probability': area['prob_4band']
                })
            else:
                # Generic fallback
                area_info.update({
                    'id': f"Area_{len(results)}",
                    'name': "Flood Risk Area",
                    'source': 'Unknown',
                    'cycle': 'Unknown'
                })
            
            results.append(area_info)
        
        # Sort by distance
        results.sort(key=lambda x: x['distance_meters'])
        return results
    
    def assess_comprehensive_flood_risk(self, coordinates: tuple) -> Dict:
        """Provide comprehensive flood risk assessment using all available sources."""
        if not coordinates:
            return {}
        
        print(f"Assessing flood risk at coordinates: {coordinates[0]:.0f}, {coordinates[1]:.0f}")
        
        assessment = {
            'coordinates': coordinates,
            'surface_water': {'risk_level': 'DATA NOT AVAILABLE', 'note': 'Surface water data not yet integrated'},
            'rivers_and_sea': {'risk_level': 'DATA NOT AVAILABLE', 'note': 'Processing...'},
            'reservoirs': {'risk_level': 'DATA NOT AVAILABLE', 'note': 'Checking API...'},
            'groundwater': {'risk_level': 'DATA NOT AVAILABLE', 'note': 'Requires BGS data'},
            'nearest_areas': []
        }
        
        # Assess using FRA data (covers both surface water and rivers/sea)
        if self.fra_data is not None:
            all_fra_areas = self.calculate_distance_to_flood_areas(coordinates, self.fra_data)
            
            # Separate by flood source
            surface_areas = [a for a in all_fra_areas if 'Surface Water' in str(a.get('source', ''))]
            rivers_areas = [a for a in all_fra_areas if 'Rivers' in str(a.get('source', '')) or 'Sea' in str(a.get('source', ''))]
            
            # Assess surface water
            if surface_areas:
                closest_sw = surface_areas[0]
                sw_risk = self._categorize_risk_from_distance(closest_sw['distance_meters'], closest_sw['risk_status'] == 'INSIDE')
                assessment['surface_water'] = {
                    'risk_level': sw_risk,
                    'yearly_chance_current': self._get_yearly_chance_estimate(sw_risk),
                    'yearly_chance_2040s': self._project_future_risk(self._get_yearly_chance_estimate(sw_risk)),
                    'closest_distance': closest_sw['distance_meters'],
                    'areas_count': len(surface_areas)
                }
            else:
                assessment['surface_water'] = {
                    'risk_level': 'VERY LOW',
                    'yearly_chance_current': 'Less than 1 in 1000 (0.1%)',
                    'yearly_chance_2040s': 'Less than 1 in 1000 (0.1%) - may increase slightly',
                    'closest_distance': None,
                    'areas_count': 0
                }
            
            # Assess rivers and sea
            if rivers_areas:
                closest_rs = rivers_areas[0]
                rs_risk = self._categorize_risk_from_distance(closest_rs['distance_meters'], closest_rs['risk_status'] == 'INSIDE')
                assessment['rivers_and_sea'] = {
                    'risk_level': rs_risk,
                    'yearly_chance_current': self._get_yearly_chance_estimate(rs_risk),
                    'yearly_chance_2040s': self._project_future_risk(self._get_yearly_chance_estimate(rs_risk)),
                    'closest_distance': closest_rs['distance_meters'],
                    'areas_count': len(rivers_areas)
                }
            else:
                assessment['rivers_and_sea'] = {
                    'risk_level': 'VERY LOW',
                    'yearly_chance_current': 'Less than 1 in 1000 (0.1%)',
                    'yearly_chance_2040s': 'Less than 1 in 1000 (0.1%) - may increase slightly',
                    'closest_distance': None,
                    'areas_count': 0
                }
            
            assessment['nearest_areas'] = all_fra_areas[:5]
        
        # Check reservoir risk via API
        print("Checking reservoir flood risk via Environment Agency API...")
        reservoir_result = self.check_reservoir_risk_api(coordinates)
        assessment['reservoirs'] = reservoir_result
        
        return assessment
    
    def _categorize_risk_from_distance(self, distance_meters: float, is_inside: bool) -> str:
        """Categorize flood risk based on distance."""
        if is_inside:
            return "HIGH"
        elif distance_meters <= 100:
            return "MEDIUM"
        elif distance_meters <= 500:
            return "LOW"
        else:
            return "VERY LOW"
    
    def _get_yearly_chance_estimate(self, risk_level: str) -> str:
        """Estimate yearly flooding chance based on risk level."""
        risk_mapping = {
            'HIGH': 'Greater than 1 in 30 (3.3%)',
            'MEDIUM': 'Between 1 in 100 and 1 in 30 (1% to 3.3%)',
            'LOW': 'Between 1 in 1000 and 1 in 100 (0.1% to 1%)',
            'VERY LOW': 'Less than 1 in 1000 (0.1%)'
        }
        return risk_mapping.get(risk_level, 'Unknown')
    
    def _project_future_risk(self, current_risk: str) -> str:
        """Project future flood risk with climate change."""
        if 'Greater than 1 in 30' in current_risk:
            return 'Greater than 1 in 30 (3.3%) - increasing trend expected'
        elif 'Between 1 in 100 and 1 in 30' in current_risk:
            return 'Between 1 in 75 and 1 in 30 (1.3% to 3.3%) - higher due to climate change'
        else:
            return current_risk + ' - may increase slightly due to climate change'
    
    def format_comprehensive_results(self, assessment: Dict, location: str) -> None:
        """Format and display comprehensive flood risk results."""
        if not assessment:
            print("No assessment data available")
            return
            
        print(f"\n🌊 INTEGRATED FLOOD RISK ASSESSMENT")
        print(f"Location: {location}")
        print(f"Coordinates: {assessment['coordinates'][0]:.0f}, {assessment['coordinates'][1]:.0f} (BNG)")
        print("=" * 80)
        
        # Surface Water Risk
        sw = assessment['surface_water']
        print(f"\n💧 SURFACE WATER FLOOD RISK: {sw['risk_level']}")
        if 'yearly_chance_current' in sw:
            print(f"   Yearly chance of flooding: {sw['yearly_chance_current']}")
            print(f"   Yearly chance between 2040-2060: {sw['yearly_chance_2040s']}")
            if sw.get('closest_distance') is not None:
                if sw['closest_distance'] == 0:
                    print(f"   Status: You are INSIDE a surface water flood risk area")
                else:
                    print(f"   Distance to nearest area: {sw['closest_distance']:.0f} meters")
            print(f"   Areas identified: {sw['areas_count']}")
        else:
            print(f"   Note: {sw.get('note', 'No additional information')}")
        
        # Rivers and Sea Risk  
        rs = assessment['rivers_and_sea']
        print(f"\n🌊 RIVERS AND SEA FLOOD RISK: {rs['risk_level']}")
        if 'yearly_chance_current' in rs:
            print(f"   Yearly chance of flooding: {rs['yearly_chance_current']}")
            print(f"   Yearly chance between 2040-2069: {rs['yearly_chance_2040s']}")
            if rs.get('closest_distance') is not None:
                if rs['closest_distance'] == 0:
                    print(f"   Status: You are INSIDE a rivers/sea flood risk area")
                else:
                    print(f"   Distance to nearest area: {rs['closest_distance']:.0f} meters")
            print(f"   Areas identified: {rs['areas_count']}")
        else:
            print(f"   Note: {rs.get('note', 'No additional information')}")
        
        # Reservoir Risk
        res = assessment['reservoirs']
        print(f"\n🏔️  RESERVOIR FLOOD RISK: {res['risk_level']}")
        if res.get('areas_count', 0) > 0:
            print(f"   Reservoirs identified: {res['areas_count']}")
            if 'reservoirs' in res:
                for i, reservoir in enumerate(res['reservoirs'][:3], 1):
                    print(f"   {i}. {reservoir['name']} - {reservoir['type']}")
        print(f"   Note: {res.get('note', res.get('reason', 'No additional information'))}")
        
        # Groundwater Risk
        gw = assessment['groundwater']
        print(f"\n🏔️  GROUNDWATER FLOOD RISK: {gw['risk_level']}")
        print(f"   Note: {gw.get('note', 'No additional information')}")
        
        # Nearest Areas Detail
        if assessment.get('nearest_areas'):
            print(f"\n📍 NEAREST FLOOD RISK AREAS")
            for i, area in enumerate(assessment['nearest_areas'], 1):
                status_emoji = "🔴" if area['risk_status'] == 'INSIDE' else "🟡"
                name = area.get('name', 'Unknown Area')
                source = area.get('source', 'Unknown Source')
                distance = area['distance_meters']
                print(f"   {i}. {status_emoji} {name}")
                print(f"      Source: {source}")
                print(f"      Distance: {distance:.0f}m ({area['risk_status']})")
                if 'id' in area:
                    print(f"      ID: {area['id']}")
                print()


def main():
    """Main CLI entry point for integrated flood risk assessment."""
    parser = argparse.ArgumentParser(
        description="Integrated Flood Risk Assessment - FRA data + Reservoir API + Rivers/Sea framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python flood_checker_integrated.py --postcode "E1 6AN"
  python flood_checker_integrated.py --postcode "HU1 1AA" --verbose
        """
    )
    
    parser.add_argument('--postcode', '-p', required=True, help='UK postcode to check')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Show verbose output including API calls')
    parser.add_argument('--fra-shapefile', 
                       default='Flood_Risk_AreasPolygon.shp',
                       help='Path to FRA shapefile')
    parser.add_argument('--datasets-dir',
                       default='flood_datasets',
                       help='Path to additional datasets directory')
    
    args = parser.parse_args()
    
    # Initialize integrated checker
    checker = IntegratedFloodRiskChecker(args.fra_shapefile, args.datasets_dir)
    
    # Get coordinates
    coordinates = checker.postcode_to_coordinates(args.postcode)
    
    if coordinates:
        # Comprehensive assessment
        assessment = checker.assess_comprehensive_flood_risk(coordinates)
        checker.format_comprehensive_results(assessment, args.postcode)
    else:
        print("Could not determine coordinates for the given postcode")
        sys.exit(1)


if __name__ == "__main__":
    main() 