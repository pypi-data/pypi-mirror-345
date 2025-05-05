from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize
import nltk
import os
from typing import List, Union
nltk.download('punkt_tab', quiet=True)

def calculate_bleu(candidate_doc: str, reference_doc: str, smoothing_method: str = None) -> float:
    """
    Calculates the BLEU score comparing the candidate documentation against a reference.

    :param candidate_doc: Generated documentation text.
    :param reference_doc: Reference documentation text.
    :param smoothing_method: Smoothing method to use. Options: 'method0','method1', 'method2', 'method3', 
                            'method4', 'method5', 'method6', 'method7', or None for no smoothing.
    :return: The BLEU score as a float.
    """
    candidate_tokens = word_tokenize(candidate_doc)
    reference_tokens = word_tokenize(reference_doc)
    
    if smoothing_method:
        smoothing_function = SmoothingFunction()
        smoothing_methods = {
            'method0': smoothing_function.method0,
            'method1': smoothing_function.method1,
            'method2': smoothing_function.method2,
            'method3': smoothing_function.method3,
            'method4': smoothing_function.method4,
            'method5': smoothing_function.method5,
            'method6': smoothing_function.method6,
            'method7': smoothing_function.method7
        }
        
        if smoothing_method in smoothing_methods:
            score = sentence_bleu([reference_tokens], candidate_tokens, 
                                 smoothing_function=smoothing_methods[smoothing_method])
        else:
            raise ValueError(f"Invalid smoothing method: {smoothing_method}. " 
                           f"Choose from: {', '.join(smoothing_methods.keys())}")
    else:
        score = sentence_bleu([reference_tokens], candidate_tokens)
    
    return score

def calculate_bleu_multi_reference(candidate_doc: str, reference_docs: List[str], smoothing_method: str = None) -> float:
    """
    Calculates the BLEU score comparing the candidate documentation against multiple references.

    :param candidate_doc: Generated documentation text.
    :param reference_docs: List of reference documentation texts.
    :param smoothing_method: Smoothing method to use. Options: 'method0','method1', 'method2', 'method3', 
                            'method4', 'method5', 'method6', 'method7', or None for no smoothing.
    :return: The BLEU score as a float.
    """
    if not reference_docs:
        raise ValueError("At least one reference document must be provided")
    
    candidate_tokens = word_tokenize(candidate_doc)
    reference_tokens_list = [word_tokenize(ref_doc) for ref_doc in reference_docs]
    
    if smoothing_method:
        smoothing_function = SmoothingFunction()
        smoothing_methods = {
            'method0': smoothing_function.method0,
            'method1': smoothing_function.method1,
            'method2': smoothing_function.method2,
            'method3': smoothing_function.method3,
            'method4': smoothing_function.method4,
            'method5': smoothing_function.method5,
            'method6': smoothing_function.method6,
            'method7': smoothing_function.method7
        }
        
        if smoothing_method in smoothing_methods:
            score = sentence_bleu(reference_tokens_list, candidate_tokens, 
                                 smoothing_function=smoothing_methods[smoothing_method])
        else:
            raise ValueError(f"Invalid smoothing method: {smoothing_method}. " 
                           f"Choose from: {', '.join(smoothing_methods.keys())}")
    else:
        score = sentence_bleu(reference_tokens_list, candidate_tokens)
    
    return score

def calculate_bleu_from_files(candidate_file: str, reference_files: Union[str, List[str]], smoothing_method: str = None) -> float:
    """
    Calculates the BLEU score by comparing the candidate file against one or more reference files.

    :param candidate_file: Path to the candidate documentation file.
    :param reference_files: Path to a single reference file or a list of paths to reference files.
    :param smoothing_method: Smoothing method to use. Options: 'method0', 'method1', 'method2', 'method3', 
                            'method4', 'method5', 'method6', 'method7', or None for no smoothing.
    :return: The BLEU score as a float.
    """
    # Read candidate file
    with open(candidate_file, 'r', encoding='utf-8') as f:
        candidate_doc = f.read()
    
    # Handle both single file and multiple files
    if isinstance(reference_files, str):
        with open(reference_files, 'r', encoding='utf-8') as f:
            reference_doc = f.read()
        return calculate_bleu(candidate_doc, reference_doc, smoothing_method)
    else:
        reference_docs = []
        for ref_file in reference_files:
            with open(ref_file, 'r', encoding='utf-8') as f:
                reference_docs.append(f.read())
        return calculate_bleu_multi_reference(candidate_doc, reference_docs, smoothing_method)
