# Data Generation Analysis

## Overview

This document analyzes the data generation logic in the Sparkov Data Generation project, focusing on how transaction data is generated, what distributions are used, and how the various configuration files interact.

## Key Components

### 1. Data Sources

- **Merchants**: Stored in `data/merchants.csv` with pipe-delimited format
- **Customer Profiles**: JSON files in the `profiles/` directory
- **Fraud Profiles**: Corresponding JSON files with `fraud_` prefix

### 2. Main Scripts

- **datagen.py**: Main orchestration script
- **datagen_customer.py**: Generates customer demographic data
- **datagen_transaction.py**: Generates transaction data based on customer profiles
- **static_merchant_generator.py**: Creates merchant data for different categories

## Data Generation Logic

### Customer Generation

Customers are generated with demographic attributes including:
- Age
- Gender
- Location (urban/rural)
- Home address coordinates

Each customer is assigned a profile based on their demographic attributes as defined in `main_config.json`.

### Transaction Generation

Transactions are generated using a sophisticated model with several key components:

1. **Profile-Based Generation**:
   - Each customer is assigned a profile (e.g., `adults_50up_male_urban.json`)
   - Profiles define transaction patterns for that demographic group
   - Separate fraud profiles exist for generating fraudulent transactions

2. **Temporal Distributions**:
   - **Day of Week Weighting**: Different days have different transaction probabilities
     - Example: Weekends typically have higher weights (150-175) than weekdays (80-100)
   - **Seasonal Patterns**: 
     - Holiday periods (Nov 30-Dec 31) have higher weights (200)
     - Post-holiday periods (Jan 1-Feb 28) have lower weights (75)
     - Summer periods (May 24-Sep 1) have moderate weights (125)
   - **Time of Day**: Transactions are split between AM/PM with profile-specific weights

3. **Category Distributions**:
   - Each profile defines weights for different merchant categories
   - Categories include: gas_transport, grocery, shopping, entertainment, etc.
   - Higher weights mean more transactions in that category

4. **Amount Distributions**:
   - Transaction amounts follow normal distributions
   - Each category has a specific mean and standard deviation
   - Example: `"shopping_net": {"mean": 1000, "stdev": 100}`

5. **Geographical Distribution**:
   - Transactions occur within a radius of the customer's home location
   - Regular transactions: ~70 miles (1 decimal degree) radius
   - Travel transactions: Larger radius based on `travel_max_dist` parameter
   - Merchant locations are generated using uniform distribution within the radius

6. **Fraud Generation**:
   - Fraud probability is set at ~1% (fraud_flag < 99)
   - Fraud transactions use different amount distributions
   - Fraud typically occurs in concentrated time periods (1-7 days)
   - Fraud profiles have different category preferences and amount distributions

## Statistical Distributions Used

1. **Normal Distribution**:
   - Used for transaction amounts
   - Parameters: mean and standard deviation specific to each category and profile
   - Implementation: Not explicitly shown but likely using numpy or random module

2. **Uniform Distribution**:
   - Used for merchant location generation
   - Used for selecting random dates within intervals
   - Implementation: `fake.coordinate(center=float(cust_lat), radius=rad)`

3. **Weighted Random Selection**:
   - Used for selecting transaction categories based on weights
   - Used for day-of-week and seasonal patterns
   - Implementation: Custom logic in the Profile class

4. **Bernoulli Distribution** (implicit):
   - Used for fraud flag generation (random.randint(0,100) < 99)
   - Used for travel decisions based on travel_pct

## Profile Configuration Details

Profiles contain several key parameters:

1. **Transaction Frequency**:
   ```json
   "avg_transactions_per_day": {
       "min": 7,
       "max": 12
   }
   ```

2. **Temporal Patterns**:
   ```json
   "date_wt": {
       "day_of_week": {
           "monday": 80,
           "friday": 125,
           "saturday": 150
       },
       "time_of_year": {
           "holidays": {"start_date": "11-30", "end_date": "12-31", "weight": 200}
       }
   }
   ```

3. **Category Weights and Amounts**:
   ```json
   "categories_wt": {
       "food_dining": 100,
       "health_fitness": 100
   },
   "categories_amt": {
       "shopping_net": {"mean": 1000, "stdev": 100},
       "food_dining": {"mean": 120, "stdev": 12}
   }
   ```

4. **Travel Parameters**:
   ```json
   "travel_pct": 20,
   "travel_max_dist": 600
   ```

## Fraud vs. Normal Transaction Patterns

Comparing fraud and normal profiles reveals key differences:

1. **Amount Differences**:
   - Fraud transactions typically have higher amounts
   - Example: Normal shopping_pos mean=$50, fraud shopping_pos mean=$800-950

2. **Category Focus**:
   - Fraud focuses on high-value categories (shopping_net, misc_net)
   - Normal transactions are more evenly distributed

3. **Temporal Concentration**:
   - Fraud occurs in short bursts (1-7 days)
   - Normal transactions follow regular patterns throughout the date range

## Parallelization Strategy

The data generation is parallelized by:
1. Chunking the customer list
2. Processing each chunk independently
3. Creating separate output files per chunk and profile
4. This explains why empty files can occur when no customers in a chunk match a profile

## Conclusion

The data generation system uses a sophisticated combination of statistical distributions and weighted parameters to create realistic transaction patterns. The profile-based approach allows for demographic-specific behavior modeling, while the separate fraud profiles enable the generation of anomalous transactions for fraud detection testing.

The system's strength lies in its configurability through the profile JSON files, allowing users to adjust parameters to create different data scenarios without changing the core code.