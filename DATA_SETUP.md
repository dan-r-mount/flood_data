# Dataset Setup Guide

This guide helps you set up the large dataset files needed for the flood risk assessment tool.

## 📥 Required Data Files

### 1. Flood Risk Areas (FRA) Shapefile
**Size**: ~14MB  
**Status**: ✅ Required for basic functionality

**Google Drive Link**: [Download FRA Dataset](https://drive.google.com/drive/folders/YOUR_FOLDER_ID)

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
3. Verify setup by running: `python flood_checker_integrated.py --postcode "E1 6AN"`

### 2. Enhanced Datasets (Optional)

These will improve accuracy when available:

**Surface Water Grids**
- **Status**: Available for download
- **Source**: [Environment Agency Surface Water Data](https://www.data.gov.uk/dataset/bad20199-6d39-4aad-8564-26a46778fd94)
- **Setup**: Extract to `flood_datasets/surface_water/`

**Rivers/Sea Data**  
- **Status**: DEFRA request submitted - pending access
- **Setup**: Will extract to `flood_datasets/rivers_sea/` when available

## 🔧 Verification

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

## 📊 File Structure

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

## 🚨 Troubleshooting

**"Error loading FRA data"**
- Ensure all 5 shapefile components are present
- Check file permissions (should be readable)
- Verify files aren't corrupted by checking file sizes

**Large file warnings in Git**
- The .gitignore is set up to exclude these files
- They should only be stored on Google Drive
- Never commit .shp files to GitHub

**Performance issues**  
- FRA shapefile is 14MB - normal load time is 1-2 seconds
- If consistently slow, check available memory
- Consider closing other applications during assessment 