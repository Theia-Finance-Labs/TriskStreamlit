import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import csv
import tqdm
import os



# Define the function to geocode unique addresses and save them in a CSV file
def geocode_unique_addresses(df, output_csv='geocoded_addresses.csv',user_agent='my_geocoder_app myemail@example.com', min_delay_seconds=2):
    # Initialize geolocator
    geolocator = Nominatim(user_agent=user_agent)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=min_delay_seconds)
    # Get unique addresses
    unique_addresses = pd.DataFrame(df['address'].unique(), columns=['address'])
    print(f'Found {len(unique_addresses)} unique addresses to geocode.')

    # Check if CSV file exists and read existing addresses to avoid duplicates
    if os.path.exists(output_csv):
        existing_data = pd.read_csv(output_csv)
        geocoded_addresses = existing_data['address'].unique().tolist()
    else:
        geocoded_addresses = []

    # Filter for addresses that haven't been geocoded yet
    new_addresses = unique_addresses[~unique_addresses['address'].isin(geocoded_addresses)]
    print(f'{len(new_addresses)} addresses need geocoding.')

    # Open the CSV file in append mode
    with open(output_csv, mode='a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Write header if the file is new
        if not geocoded_addresses:
            csv_writer.writerow(['address', 'latitude', 'longitude'])
        
        # Apply geocoding and write results to CSV
        for _, row in tqdm.tqdm(new_addresses.iterrows()):
            location = geocode(row['address'])
            if location:
                latitude = location.latitude
                longitude = location.longitude
                csv_writer.writerow([row['address'], latitude, longitude])
                print(f'Geocoded: {row["address"]} -> {latitude}, {longitude}')
            else:
                print(f'Failed to geocode: {row["address"]}')

    print(f'Geocoding completed. Results saved to {output_csv}')
