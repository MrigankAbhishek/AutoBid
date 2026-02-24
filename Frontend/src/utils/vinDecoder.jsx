// src/components/vinDecoder.js

export const decodeIndianVIN = (vin) => {
    // 1. Basic Validation
    if (!vin) return { valid: false, error: "Empty VIN" };
    if (vin.length !== 17) return { valid: false, error: "VIN must be 17 characters" };
  
    const cleanVin = vin.toUpperCase();
  
    // 2. WMI Map (World Manufacturer Identifier - First 3 Chars)
    // Detailed map covering Indian plants and common imports
    const wmiMap = {
        // --- MASS MARKET (INDIAN MANUFACTURED) ---
        'MA3': 'Maruti Suzuki',
        'MBJ': 'Maruti Suzuki', 
        'MAL': 'Hyundai',
        'MNA': 'Hyundai',
        'MAT': 'Tata Motors',
        'MA1': 'Mahindra',
        'MC2': 'Honda',          
        'MAK': 'Honda',          
        'ME4': 'Toyota',
        'MZB': 'Kia',
        'MEX': 'Volkswagen / Skoda', 
        'MEE': 'Renault',
        'MDH': 'Nissan',
        'MFA': 'MG Motor',
        'MAJ': 'Ford',
        'MA6': 'Chevrolet',
        'MCA': 'Jeep / Fiat',    
        'MA8': 'Force Motors',
        'MC1': 'Citroen',
        'MCB': 'Isuzu',

        // --- LUXURY & IMPORTS ---
        'MHL': 'Mercedes-Benz',
        'WDB': 'Mercedes-Benz',
        'WDD': 'Mercedes-Benz',
        'WBA': 'BMW',
        'WBS': 'BMW',
        'WAU': 'Audi',
        'TRU': 'Audi',
        'SAJ': 'Jaguar',
        'SAL': 'Land Rover',
        'YV1': 'Volvo',
        'WVW': 'Volkswagen',
        'TMB': 'Skoda',
        'JHM': 'Honda',
        'JT1': 'Toyota',
        'KL1': 'Chevrolet',

        // --- LEGACY ---
        'MH3': 'Hindustan Motors', 
        'MP3': 'Premier',          
    };
  
    // 3. Year Map (10th Character) - Standard ISO 3779
    const yearMap = {
      'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014, 'F': 2015, 
      'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019, 'L': 2020, 'M': 2021, 
      'N': 2022, 'P': 2023, 'R': 2024, 'S': 2025, 'T': 2026, 'V': 2027, 
      'W': 2028, 'X': 2029,
      '1': 2001, '2': 2002, '3': 2003, '4': 2004, '5': 2005, 
      '6': 2006, '7': 2007, '8': 2008, '9': 2009
    };
  
    // 4. Decode Logic
    const wmi = cleanVin.substring(0, 3);
    const yearChar = cleanVin.charAt(9); // 10th character is the year code
  
    const manufacturer = wmiMap[wmi] || "Unknown Manufacturer";
    const year = yearMap[yearChar] || "Unknown Year";
  
    // 5. Return Result Object
    return {
      valid: true,
      manufacturer: manufacturer,
      year: year,
      originalVin: cleanVin
    };
};