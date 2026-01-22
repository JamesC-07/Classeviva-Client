# Classeviva Client

A comprehensive client application for accessing Classeviva (Spaggiari) school data, available in both Flutter for Android and a Python/Kivy implementation for desktop.

## Overview

This project provides unofficial clients for the Classeviva platform used by many Italian schools. It allows students to view their grades, absences, and academic statistics in a modern, user-friendly interface.

## Technologies & Frameworks

### Flutter Implementation
![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![Dart](https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white)

### Python/Kivy Implementation
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Kivy](https://img.shields.io/badge/Kivy-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Features

### Core Functionality
- Secure login with credential persistence
- Automatic re-authentication on app launch
- Grade viewing with detailed breakdowns
- Absence tracking and monitoring
- Quarterly and overall grade averages
- Subject-specific statistics
- Responsive design for mobile and tablet devices

### Grade Management
- View all grades with dates and descriptions
- Color-coded grades (green for passing, red for failing, blue for non-counting)
- Quarterly breakdown (Q1 and Q2)
- Subject-specific averages
- Grade distribution histograms
- Expandable grade cards with full details
- Warning indicators for subjects with insufficient grades

### Absence Tracking
- Total absences, late arrivals, and early departures
- Justification status for each absence
- Absence limit monitoring (25% threshold)
- Progress bars showing:
  - School year completion percentage
  - Absence usage against limit
- Remaining absence count
- Detailed absence history

### Statistics
- Overall grade average
- Per-subject averages
- Quarterly comparisons
- Grade distribution analysis
- Visual bar charts and histograms
- Responsive statistics display

## Installation
You can install the latest version on the release page: https://github.com/JamesC-07/Classeviva-Client/releases/tag/v.1.1.0

## Usage

### First Launch

1. Launch the application
2. Enter your Classeviva credentials:
   - Username (format: S1234567C)
   - Password
3. Click "Accedi" (Login)
4. Credentials are saved for automatic login

## API Integration

Both implementations use the Classeviva REST API: https://github.com/Lioydiano/Classeviva
A list of the official endpoints can be found here: https://github.com/michelangelomo/Classeviva-Official-Endpoints

## Calculations & Algorithms

### Grade Averages
- Excludes blue (non-counting) grades
- Calculated per quarter and overall
- Weighted equally (simple arithmetic mean)

### Absence Limit
- Based on 25% of total school days (approximately 200 days)
- Maximum allowed absences: ~50 days
- Excludes weekends, holidays, and break periods:
  - Christmas break (December 23 - January 6)
  - Easter break (approximately April 10-17)

## Known Limitations

- Absence day calculations are approximate and may not match official school counts
- Some grade types may not display correctly if format is non-standard
- API rate limiting may affect data loading on slow connections
- Does not allow email sign-in

## Troubleshooting

### App does not launch
- Ensure you are not on a iOS device
- Check if your internet connection is on

### Login Failed
- Verify username format (usually starts with 'S' followed by numbers and a letter)
- Ensure internet connection is active
- Try logging in via the official Classeviva website to verify credentials

### Data Not Loading
- Check internet connection
- Restart the application
- Clear app data and re-login

## Disclaimer

This is an unofficial client and is not affiliated with, endorsed by, or connected to Gruppo Spaggiari Parma or the Classeviva platform.

### Version 1.0.0
- Python/Kivy implementation
- Grade viewing and statistics
- Absence tracking
- Responsive design
- Secure credential storage
- Quarterly grade breakdowns
- Subject detail views

### Version 1.1.0
- Flutter implementation
