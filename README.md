# UK Flood Risk Assessment Tool

A comprehensive CLI tool for assessing flood risk at UK postcodes, designed to replicate functionality similar to the [official government service](https://check-long-term-flood-risk.service.gov.uk/risk#).

## 🎯 What This Tool Does

- **Distance calculations** to nearest flood risk areas (unique feature not in gov.uk service)
- **Risk categorization** using government-style Very Low/Low/Medium/High categories  
- **Multiple flood types**: Surface Water, Rivers & Sea, Reservoirs, Groundwater
- **Live data integration** from Environment Agency APIs
- **Future risk projections** with climate change considerations

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- ~20MB disk space (datasets hosted separately)
- Internet connection for postcode lookup and reservoir API

### Setup
```bash
# Clone this repository
git clone https://github.com/dan-r-mount/flood_data.git
cd flood_data

# Create virtual environment
python3 -m venv flood_env
source flood_env/bin/activate  # On Windows: flood_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Assessment
```bash
# Check flood risk for any UK postcode
python flood_checker_integrated.py --postcode "E1 6AN"

# Example with verbose output
python flood_checker_integrated.py --postcode "HU1 1AA" --verbose
```

### Expected Output
```
🌊 INTEGRATED FLOOD RISK ASSESSMENT
Location: E1 6AN
Coordinates: 533416, 181746 (BNG)
================================================================================

💧 SURFACE WATER FLOOD RISK: HIGH
   Yearly chance of flooding: Greater than 1 in 30 (3.3%)
   Status: You are INSIDE a surface water flood risk area

🌊 RIVERS AND SEA FLOOD RISK: VERY LOW  
   Distance to nearest area: 1016 meters

🏔️  RESERVOIR FLOOD RISK: VERY LOW
   Note: No reservoir flood risk areas found at this location
```

## 📊 Current Implementation Status

### ✅ Fully Working
| Component | Status | Data Source | Coverage |
|-----------|--------|-------------|----------|
| **Surface Water** | ✅ Working | FRA Approximation | England-wide significant areas |
| **Rivers & Sea** | ✅ Working | FRA Approximation | England-wide significant areas |  
| **Reservoirs** | ✅ Working | Live EA API | Major reservoirs |
| **Distance Calculations** | ✅ Working | Spatial Analysis | All flood sources |
| **Risk Scoring** | ✅ Working | Government Categories | 4-band system |

### 🔄 Enhanced Versions Available (Pending Data)
| Component | Enhancement | Status | Impact |
|-----------|-------------|---------|---------|
| **Surface Water** | 50m probability grids | Needs EA dataset | More precise risk scoring |
| **Rivers & Sea** | Detailed flood modeling | DEFRA request submitted | Higher accuracy assessment |
| **Groundwater** | BGS geological data | Requires license | Complete risk picture |

## 📁 Datasets

### Currently Used (Working)
1. **Flood Risk Areas (FRA) Shapefile**
   - **Source**: Environment Agency
   - **Content**: 189 significant flood risk polygons across England
   - **Coverage**: Surface Water and Rivers/Sea risk areas
   - **Size**: ~14MB (hosted on Google Drive - see Data Access section)
   - **Format**: ESRI Shapefile (.shp, .shx, .dbf, .prj, .cst)

2. **Reservoir Flood Risk API**
   - **Source**: Environment Agency WFS Service
   - **Endpoint**: `https://environment.data.gov.uk/geoservices/datasets/db114020-465a-412b-b289-be393d995a75/ogc/features/v1`
   - **Coverage**: Major reservoir failure scenarios
   - **Access**: Live API (no download required)

### Needed for Enhanced Accuracy

3. **Risk of Flooding from Surface Water (RoFSW)**
   - **Source**: Environment Agency
   - **Content**: 50m resolution probability grids
   - **Status**: Available for download
   - **URL**: [data.gov.uk surface water dataset](https://www.data.gov.uk/dataset/bad20199-6d39-4aad-8564-26a46778fd94)
   - **Impact**: Precise surface water risk scoring vs. current FRA approximation

4. **Risk of Flooding from Rivers and Sea (RoFRS)**  
   - **Source**: Environment Agency  
   - **Content**: Detailed rivers/coastal flood modeling
   - **Status**: **DEFRA request submitted** - awaiting access
   - **Impact**: Higher accuracy rivers/sea assessment vs. current FRA approximation

5. **Groundwater Flood Risk**
   - **Source**: British Geological Survey (BGS)
   - **Content**: Geological susceptibility mapping
   - **Status**: Requires commercial license
   - **Impact**: Complete groundwater risk assessment (currently not available)

## 💾 Data Access

### Large Dataset Files
Due to GitHub size limitations, the main FRA shapefile (~14MB) is hosted separately:

**Google Drive**: [Flood Risk Areas Dataset](https://drive.google.com/drive/folders/YOUR_FOLDER_ID)

**Contents**:
- `Flood_Risk_AreasPolygon.shp` - Main shapefile
- `Flood_Risk_AreasPolygon.shx` - Shape index
- `Flood_Risk_AreasPolygon.dbf` - Attribute database  
- `Flood_Risk_AreasPolygon.prj` - Projection information
- `Flood_Risk_AreasPolygon.cst` - Character set information

**Setup Instructions**:
1. Download all files from Google Drive
2. Place in the same directory as `flood_checker_integrated.py`
3. The tool will automatically detect and load the data

## 🔧 Technical Details

### Architecture
```
Postcode Input → Coordinates → Multi-Source Assessment:
├── FRA Shapefile Analysis (Surface Water & Rivers/Sea)
├── Environment Agency API (Reservoirs)  
├── Distance Calculations (All Sources)
└── Risk Categorization (Government Standards)
```

### Risk Assessment Method
- **Distance-based scoring**: Inside area = HIGH, <100m = MEDIUM, <500m = LOW, >500m = VERY LOW
- **Probability estimates**: Based on Environment Agency categories
- **Future projections**: Climate change factor applied to current risk
- **Multiple sources**: All flood types assessed independently

### Performance
- **Assessment time**: 3-7 seconds per postcode
- **API dependency**: Only reservoir data (with fallback)
- **Offline capability**: Surface water and rivers/sea work without internet

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python test_examples.py
```

Tests various postcodes:
- **E1 6AN** (London) - High surface water risk
- **HU1 1AA** (Hull) - High multiple flood risks  
- **EH1 1YZ** (Edinburgh) - Low risk area

## 🤝 For Collaborators

### Getting Started
1. Clone this repo
2. Download FRA dataset from Google Drive (link above)
3. Set up Python environment (see Quick Start)
4. Run test examples to verify setup
5. Try your own postcodes!

### Key Files
- `flood_checker_integrated.py` - Main assessment tool
- `test_examples.py` - Example usage and testing
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

### Making Changes
- The tool is designed to automatically detect new datasets when added
- For rivers/sea: Place shapefiles in `flood_datasets/rivers_sea/`
- For surface water: Place grids in `flood_datasets/surface_water/`
- All coordinate systems should be British National Grid (EPSG:27700)

## 🚨 Known Limitations

1. **Surface Water**: Currently uses FRA approximation, not precise 50m grids
2. **Rivers/Sea**: Currently uses FRA approximation, waiting for DEFRA access
3. **Groundwater**: Not implemented (requires BGS license)
4. **Climate Projections**: Simplified estimates, not full UKCP18 modeling
5. **Geographic Coverage**: England only (could extend to Wales/Scotland with additional data)

## 🎯 Comparison with Gov.UK Service

| Feature | This Tool | Gov.UK Service | Status |
|---------|-----------|---------------|---------|
| Distance to Risk Areas | ✅ Precise measurements | ❌ Not provided | **Better** |
| Reservoir Data | ✅ Live API | ⏳ Static maps | **More current** |
| Surface Water Risk | 🟡 FRA approximation | ✅ Detailed grids | **Good match** |
| Rivers/Sea Risk | 🟡 FRA approximation | ✅ Detailed modeling | **Pending data** |
| Groundwater Risk | ❌ Not available | ✅ Available | **Missing** |

## 📞 Support

### Common Issues

**"Failed to find coordinates for postcode"**
- Check postcode format: "SW1A 1AA" (space before final part)
- Verify postcode exists using [Royal Mail finder](https://www.royalmail.com/find-a-postcode)

**"No rivers/sea shapefile found"**  
- Expected message - system uses FRA data as fallback
- Will automatically upgrade when DEFRA provides RoFRS access

**"API request timed out"**
- Only affects reservoir assessment
- Other flood types continue to work
- Try again later if network conditions improve

### Contact
- **Technical Issues**: Check GitHub Issues
- **Data Access**: DEFRA request status available on request
- **Enhancements**: Pull requests welcome

## 📜 License & Attribution

- **Code**: Open source (specify license)
- **FRA Data**: © Environment Agency, Open Government License
- **API Access**: Environment Agency WFS Service
- **Coordinate Conversion**: postcodes.io (open source)

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Status**: Production ready with enhancement pipeline 