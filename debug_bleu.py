import os
import sys
import re
import sacrebleu

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

root = "."
en_raw = os.path.join(root, 'data/raw/english_texts.txt')
ar_raw = os.path.join(root, 'data/raw/arabic_texts.txt')

with open(en_raw, 'r', encoding='utf-8') as f:
    en_blocks = [t.strip() for t in re.split(r'\n\s*\n', f.read()) if t.strip()]
with open(ar_raw, 'r', encoding='utf-8') as f:
    ar_blocks = [t.strip() for t in re.split(r'\n\s*\n', f.read()) if t.strip()]

print(f"EN blocks: {len(en_blocks)}")
print(f"AR blocks: {len(ar_blocks)}")

if len(en_blocks) > 0 and len(ar_blocks) > 0:
    print("\n--- Alignment Check ---")
    print(f"EN 1: {en_blocks[0][:50]}...")
    print(f"AR 1: {ar_blocks[0][:50]}...")

    # Test BLEU with self-reference
    score = sacrebleu.corpus_bleu([ar_blocks[0]], [[ar_blocks[0]]], tokenize='intl').score
    print(f"\nSelf-BLEU (AR): {score}")
