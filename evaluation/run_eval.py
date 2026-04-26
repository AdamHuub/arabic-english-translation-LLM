import sys
import os
import pandas as pd
import time

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from translation.gemini_api import _translator as translator
import translation.prompts as prompts
from evaluation.bleu_score import TranslationEvaluator

def run_global_audit():
    evaluator = TranslationEvaluator()
    
    # Comprehensive evaluation dataset
    data = [
        {"arabic": "يعتبر الذكاء الاصطناعي من أهم تقنيات العصر الحديث.", "reference": "Artificial intelligence is considered one of the most important technologies of the modern era.", "category": "Scientific"},
        {"arabic": "تعد الخلايا الجذعية ثورة في الطب التجديدي.", "reference": "Stem cells represent a revolution in regenerative medicine.", "category": "Medical"},
        {"arabic": "كانت النجوم تتلألأ في السماء كأنها جواهر منثورة.", "reference": "The stars were twinkling in the sky like scattered jewels.", "category": "Creative"},
        {"arabic": "الحياة رواية جميلة عليك قراءتها حتى النهاية.", "reference": "Life is a beautiful novel that you must read until the end.", "category": "Poetic"},
        {"arabic": "يؤدي التغير المناخي إلى ارتفاع مستويات البحار والمحيطات.", "reference": "Climate change leads to rising sea and ocean levels.", "category": "Environment"},
        {"arabic": "العدل أساس الملك والظلم مؤذن بخراب العمران.", "reference": "Justice is the foundation of the state, and injustice signals the ruin of civilization.", "category": "Legal/Formal"},
        {"arabic": "كيف حالك اليوم؟ أتمنى أن تكون بخير.", "reference": "How are you today? I hope you are doing well.", "category": "General"},
        {"arabic": "تتطلب هذه الوظيفة مهارات عالية في البرمجة والتحليل.", "reference": "This job requires high skills in programming and analysis.", "category": "Professional"},
        {"arabic": "الصمت في حرم الجمال جمال.", "reference": "Silence in the presence of beauty is beauty itself.", "category": "Aesthetic"},
        {"arabic": "سجلت البورصة ارتفاعا ملحوظا في تداولات اليوم.", "reference": "The stock exchange recorded a significant increase in today's trading.", "category": "Economic"}
    ]
    
    num_prompts = 10
    all_prompt_results = []
    
    print(f"Starting Global Audit of {num_prompts} Refined Prompt Variants...")
    print(f"Using Provider: {translator.provider.upper()}")
    
    for p_idx in range(num_prompts):
        version_label = f"V{p_idx + 1}"
        print(f"\nEvaluating Prompt Variant {version_label}...")
        variant_results = []
        
        for i, item in enumerate(data):
            try:
                # Use the refined high-level translate_text function
                # This automatically handles the system/user split and cleaning
                translation = translator.translate_text(
                    item['arabic'], 
                    "Arabic", 
                    "English", 
                    mode=version_label
                )
                
                score = evaluator.evaluate_sentence(item['reference'], translation)
                
                variant_results.append({
                    "prompt_v": version_label,
                    "category": item['category'],
                    "score": score,
                    "translation": translation,
                    "reference": item['reference']
                })
                print(f"  [{item['category']}] BLEU: {score:.4f}")
                time.sleep(1) # Avoid rate limits
            except Exception as e:
                print(f"  Error on item {i}: {e}")
        
        if variant_results:
            avg_score = sum(r['score'] for r in variant_results) / len(variant_results)
            all_prompt_results.append({
                "prompt_v": version_label,
                "avg_bleu": avg_score,
                "details": variant_results
            })

    # Find Best Prompt
    if all_prompt_results:
        best_p = max(all_prompt_results, key=lambda x: x['avg_bleu'])
        
        print("\n" + "="*60)
        print("REFINED GLOBAL AUDIT SUMMARY (WITH OUTPUT CLEANING)")
        print("="*60)
        for res in all_prompt_results:
            print(f"Prompt {res['prompt_v']}: Average BLEU = {res['avg_bleu']:.4f}")
        print("="*60)
        print(f"WINNING PROMPT: {best_p['prompt_v']} with score {best_p['avg_bleu']:.4f}")
        print("="*60)
        
        # Save summary
        summary_data = [{"Prompt_Version": r['prompt_v'], "Avg_BLEU": r['avg_bleu']} for r in all_prompt_results]
        pd.DataFrame(summary_data).to_csv("results/global_audit_results.csv", index=False)
        
        # Save detailed report
        detailed_list = []
        for r in all_prompt_results:
            for d in r['details']:
                detailed_list.append(d)
        pd.DataFrame(detailed_list).to_csv("results/global_audit_detailed.csv", index=False)
        print(f"Results saved to results/global_audit_results.csv")
        
    else:
        print("Audit failed to collect results.")

if __name__ == "__main__":
    run_global_audit()
