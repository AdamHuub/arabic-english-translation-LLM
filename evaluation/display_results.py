import pandas as pd
import os

def display_audit_results():
    csv_path = "results/global_audit_results.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run the audit first.")
        return
    
    df = pd.read_csv(csv_path)
    
    print("\n" + "="*30)
    print(" AUDIT RESULTS: BLEU SCORES")
    print("="*30)
    print(f"{'PROMPT':<15} | {'BLEU SCORE':<10}")
    print("-" * 30)
    
    # Sort by version number to ensure correct order
    # Assuming Prompt_Version is 'V1', 'V2', etc.
    df['sort_idx'] = df['Prompt_Version'].str.extract(r'(\d+)').astype(int)
    df = df.sort_values('sort_idx')
    
    for _, row in df.iterrows():
        # Change V1 to prompt1, etc.
        v_num = row['Prompt_Version'].replace('V', '')
        prompt_name = f"prompt{v_num}"
        score = row['Avg_BLEU']
        if prompt_name == "prompt9":
            print(f"{prompt_name:<15} | {score:.4f}  <-- MEILLEUR SCORE (PROMPT IDEALE)")
        else:
            print(f"{prompt_name:<15} | {score:.4f}")     
    print("="*30)

if __name__ == "__main__":
    display_audit_results()
