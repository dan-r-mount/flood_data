# Dataset Setup Guide

This guide helps you set up the large dataset files needed for the flood risk assessment tool. Some datasets have been requested from DEFRA, placeholder folders have been created. 

## Required Data Files

### 1. Flood Risk Areas (FRA) Shapefile
**Size**: ~14MB  
**Status**: ✅ Required for basic functionality

**Google Drive Link**: [Download FRA Dataset](https://drive.google.com/drive/folders/1SMldMWv6_s7J6p_up8iFxWOtWa2YlDro)

**Files to Download**:
```
Flood_Risk_AreasPolygon.shp    # Main shapefile (14MB)
Flood_Risk_AreasPolygon.shx    # Shape index
Flood_Risk_AreasPolygon.dbf    # Attributes (143KB)  
Flood_Risk_AreasPolygon.prj    # Projection info
Flood_Risk_AreasPolygon.cst    # Character set
```

**Installation**:
1. Download all 5 files from Google Drive
2. Place them in the same directory as `flood_checker_integrated.py`
3. Verify setup by running: `python flood_checker_integrated.py --postcode "SW2 4BN"`

### 2. Enhanced Datasets 

These will improve accuracy when available:

**Rivers/Sea Data**  
- **Status**: DEFRA request submitted DSP3-7259 opened on 28/07 - pending access

**Rivers/Sea Data Climate Change**

- **Status**: DEFRA request submitted DSP3-7260 opened on 28/07 - pending access

**Surface Water Grids**
- **Status**: Included within DSP3-7259 request above



## Verification

After setup, run this test:

```bash
python flood_checker_integrated.py --postcode "E1 6AN"
```

**Expected output**:
```
Loading flood risk data sources...
✅ Loaded 189 Flood Risk Areas
⚠️  No rivers/sea shapefile found - using FRA data only for rivers/sea
```

If you see "❌ Error loading FRA data", check that all 5 files are in the correct location.

## File Structure

Your directory should look like:
```
flood_data/
├── flood_checker_integrated.py
├── test_examples.py  
├── requirements.txt
├── README.md
├── Flood_Risk_AreasPolygon.shp    # From Google Drive
├── Flood_Risk_AreasPolygon.shx    # From Google Drive
├── Flood_Risk_AreasPolygon.dbf    # From Google Drive
├── Flood_Risk_AreasPolygon.prj    # From Google Drive
├── Flood_Risk_AreasPolygon.cst    # From Google Drive
└── flood_datasets/                 # Optional enhanced data
    ├── surface_water/
    └── rivers_sea/
```

## Troubleshooting

**Large file available in google drive*
- The .gitignore is set up to exclude these files
- They should only be stored on Google Drive
