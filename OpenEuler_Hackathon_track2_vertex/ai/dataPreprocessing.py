import pandas as pd
import numpy as np

def convert_monitoring_data(input_csv, output_csv='blocksector_format.csv'):
    """
    Convert OpenEuler monitoring data to blocksector format.
    Handles small byte values that would round to 0.
    
    Parameters:
    - input_csv: Path to the OpenEuler monitoring CSV file
    - output_csv: Path for the output CSV file
    """
    
    # Read the input CSV
    df = pd.read_csv(input_csv)
    
    print(f"Input file loaded: {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")
    
    # Initialize output data structure
    output_data = []
    
    # Block size in bytes (Pintos standard)
    BLOCK_SIZE = 512
    
    # Check if we need to use ceiling instead of floor
    sample_reads = df['disk_read'].head(100)
    sample_writes = df['disk_write'].head(100)
    avg_read = sample_reads[sample_reads > 0].mean() if (sample_reads > 0).any() else 0
    avg_write = sample_writes[sample_writes > 0].mean() if (sample_writes > 0).any() else 0
    
    # If average values are small, use ceiling to avoid all zeros
    use_ceiling = (avg_read < BLOCK_SIZE * 2) or (avg_write < BLOCK_SIZE * 2)
    
    if use_ceiling:
        print(f"⚠ Detected small byte values (avg_read={avg_read:.2f}, avg_write={avg_write:.2f})")
        print(f"  Using CEILING division to preserve small requests")
        conversion_func = lambda x: int(np.ceil(x / BLOCK_SIZE)) if x > 0 else 0
    else:
        print(f"✓ Normal byte values detected (avg_read={avg_read:.2f}, avg_write={avg_write:.2f})")
        print(f"  Using FLOOR division (standard behavior)")
        conversion_func = lambda x: int(x / BLOCK_SIZE)
    
    print("\nFirst few input values:")
    print(df[['disk_read', 'disk_write']].head(10))
    
    # Process each row
    for idx, row in df.iterrows():
        disk_read = row['disk_read']
        disk_write = row['disk_write']
        
        # Convert bytes to block sectors
        blocksector_read = conversion_func(disk_read)
        blocksector_write = conversion_func(disk_write)
        
        # Determine boot/exec status
        boot_exec = 1 if idx == 0 else 0  # 1 for boot, 0 for exec
        
        # Add read operation
        output_data.append({
            'blocksector': blocksector_read,
            'read/write': 1,  # 1 for read
            'boot/exec': boot_exec
        })
        
        # Add write operation
        output_data.append({
            'blocksector': blocksector_write,
            'read/write': 0,  # 0 for write
            'boot/exec': boot_exec
        })
    
    # Create output DataFrame
    output_df = pd.DataFrame(output_data)
    
    # Statistics
    zero_count = (output_df['blocksector'] == 0).sum()
    nonzero_count = (output_df['blocksector'] > 0).sum()
    unique_values = output_df['blocksector'].nunique()
    
    print(f"\n{'='*60}")
    print("CONVERSION RESULTS")
    print(f"{'='*60}")
    print(f"Total records created: {len(output_df)}")
    print(f"  - Zero blocksectors: {zero_count} ({zero_count/len(output_df)*100:.1f}%)")
    print(f"  - Non-zero blocksectors: {nonzero_count} ({nonzero_count/len(output_df)*100:.1f}%)")
    print(f"  - Unique blocksector values: {unique_values}")
    print(f"  - Max blocksector value: {output_df['blocksector'].max()}")
    
    print("\nFirst 20 rows of output:")
    print(output_df.head(20))
    
    # Warning if too many zeros
    if zero_count / len(output_df) > 0.9:
        print(f"\n⚠ WARNING: {zero_count/len(output_df)*100:.1f}% of blocksectors are 0!")
        print("  This means most disk I/O values are < 512 bytes.")
        print("  The Cache may consider this dataset too small.")
        print("\n  SOLUTIONS:")
        print("  1. Use a smaller BLOCK_SIZE (try 256, 128, or 64)")
        print("  2. Aggregate multiple rows together")
        print("  3. Use the cumulative version (see below)")
    
    # Save to CSV
    output_df.to_csv(output_csv, index=False)
    print(f"\n✓ Output saved to: {output_csv}")
    
    return output_df


def convert_with_smaller_blocksize(input_csv, output_csv='blocksector_format.csv', block_size=128):
    """
    Convert with a custom (smaller) block size to handle small byte values.
    """
    
    df = pd.read_csv(input_csv)
    print(f"Using custom BLOCK_SIZE={block_size} bytes")
    
    output_data = []
    
    for idx, row in df.iterrows():
        disk_read = row['disk_read']
        disk_write = row['disk_write']
        
        # Use ceiling for any non-zero value
        blocksector_read = int(np.ceil(disk_read / block_size)) if disk_read > 0 else 0
        blocksector_write = int(np.ceil(disk_write / block_size)) if disk_write > 0 else 0
        
        boot_exec = 1 if idx == 0 else 0
        
        output_data.append({
            'blocksector': blocksector_read,
            'read/write': 1,
            'boot/exec': boot_exec
        })
        
        output_data.append({
            'blocksector': blocksector_write,
            'read/write': 0,
            'boot/exec': boot_exec
        })
    
    output_df = pd.DataFrame(output_data)
    output_df.to_csv(output_csv, index=False)
    
    nonzero = (output_df['blocksector'] > 0).sum()
    print(f"Created {len(output_df)} records with {nonzero} non-zero blocksectors")
    print(f"Output saved to: {output_csv}")
    
    return output_df


def convert_with_cumulative_sectors(input_csv, output_csv='blocksector_format.csv'):
    """
    Alternative: Use cumulative block sectors instead of per-request values.
    This ensures growing sector numbers even with small individual I/O.
    """
    
    df = pd.read_csv(input_csv)
    output_data = []
    BLOCK_SIZE = 256
    
    # Calculate cumulative sectors
    df['cumulative_read_sectors'] = (df['disk_read'].cumsum() / BLOCK_SIZE).astype(int)
    df['cumulative_write_sectors'] = (df['disk_write'].cumsum() / BLOCK_SIZE).astype(int)
    
    print("Using CUMULATIVE sector addressing")
    print(f"  Final read sector: {df['cumulative_read_sectors'].iloc[-1]}")
    print(f"  Final write sector: {df['cumulative_write_sectors'].iloc[-1]}")
    
    for idx, row in df.iterrows():
        boot_exec = 1 if idx == 0 else 0
        
        # Use cumulative sector numbers
        output_data.append({
            'blocksector': int(row['cumulative_read_sectors']),
            'read/write': 1,
            'boot/exec': boot_exec
        })
        
        output_data.append({
            'blocksector': int(row['cumulative_write_sectors']),
            'read/write': 0,
            'boot/exec': boot_exec
        })
    
    output_df = pd.DataFrame(output_data)
    output_df.to_csv(output_csv, index=False)
    
    unique = output_df['blocksector'].nunique()
    print(f"Created {len(output_df)} records with {unique} unique sector addresses")
    print(f"Output saved to: {output_csv}")
    
    return output_df


# Usage example:
if __name__ == "__main__":
    input_file = 'metrics (3).csv'
    
    print("="*60)
    print("METHOD 1: Smart conversion (auto-detects small values)")
    print("="*60)
    df1 = convert_monitoring_data(input_file, 'blocksector_format.csv')
    
    # If you get too many zeros, try these alternatives:
    
    # print("\n" + "="*60)
    # print("METHOD 2: Smaller block size (128 bytes)")
    # print("="*60)
    # df2 = convert_with_smaller_blocksize(input_file, 'blocksector_format_128.csv', block_size=128)
    
    # print("\n" + "="*60)
    # print("METHOD 3: Cumulative sector addressing")
    # print("="*60)
    # df3 = convert_with_cumulative_sectors(input_file, 'blocksector_format_cumulative.csv')