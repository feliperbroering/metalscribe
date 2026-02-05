import sys
import time
import logging
from pathlib import Path
from difflib import SequenceMatcher

# Add src to path
sys.path.append(str(Path.cwd() / "src"))

from metalscribe.core.audio import convert_to_wav_16k
from metalscribe.core.whisper import run_transcription
from metalscribe.utils.logging import setup_logging

# Setup
FILES = [
    "test_output/Nm4/nm4.m4a",
]

MODELS = [
    "large-v3",
    "large-v3-q5_0",
    "large-v3-turbo"
]

EVAL_DIR = Path(".models_eval")
EVAL_DIR.mkdir(exist_ok=True)

setup_logging(verbose=True)
logger = logging.getLogger("eval")

def read_text(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

report_lines = []
report_lines.append("# Relatório de Avaliação de Modelos Whisper")
report_lines.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("")

for file_str in FILES:
    input_path = Path(file_str)
    if not input_path.exists():
        logger.error(f"File not found: {input_path}")
        continue
    
    file_id = input_path.stem
    logger.info(f"Processing {file_id}...")
    
    # 1. Convert/Truncate
    wav_path = EVAL_DIR / f"{file_id}_15m.wav"
    if not wav_path.exists():
        logger.info(f"Converting {file_id} to 15m WAV...")
        convert_to_wav_16k(input_path, wav_path, limit_minutes=15.0)
    else:
        logger.info(f"WAV already exists: {wav_path}")
    
    # 2. Transcribe with each model
    results = {} # model -> {time, text_path, rtf}
    
    for model in MODELS:
        logger.info(f"Transcribing {file_id} with {model}...")
        
        # We want the output txt. run_transcription uses output_base to generate .txt
        output_base = EVAL_DIR / f"{file_id}_{model}"
        expected_txt = Path(f"{output_base}.txt")
        
        start_t = time.time()
        
        # Check if already processed to save time (optional, but good for retries)
        if not expected_txt.exists():
             run_transcription(
                wav_path, 
                model_name=model, 
                language="pt", 
                output_base=output_base
            )
        else:
             logger.info(f"Output already exists for {model}")
        
        duration = time.time() - start_t
        # If cached, duration is ~0, so we can't calculate RTF correctly from this run
        # For the purpose of the report, we only get accurate RTF if we run it.
        # But for now let's assume we run it or report 0.
        
        rtf = duration / 900.0 
        
        results[model] = {
            "time": duration,
            "rtf": rtf,
            "path": expected_txt
        }
        
    # 3. Compare
    ref_model = "large-v3"
    if ref_model not in results or not results[ref_model]["path"].exists():
        logger.error(f"Reference model {ref_model} failed for {file_id}")
        continue
        
    ref_text = read_text(results[ref_model]["path"])
    ref_len = len(ref_text)
    
    report_lines.append(f"## Arquivo: {file_id}")
    report_lines.append(f"**Referência ({ref_model}):** {ref_len} caracteres")
    report_lines.append("")
    report_lines.append("| Modelo | Tempo (s) | RTF | Similaridade | Diferença Chars | Notas |")
    report_lines.append("|---|---|---|---|---|---|")
    
    for model in MODELS:
        res = results[model]
        cand_text = read_text(res["path"])
        cand_len = len(cand_text)
        
        sim = similarity(ref_text, cand_text)
        diff_len = cand_len - ref_len
        
        # Hallucination heuristic: Repetition or huge length diff
        notes = ""
        if abs(diff_len) > ref_len * 0.2:
            notes += "⚠️ Tamanho muito diferente "
        if sim < 0.9 and model != ref_model:
            notes += "⚠️ Baixa similaridade "
        if model == ref_model:
            notes = "Referência"
            
        report_lines.append(f"| {model} | {res['time']:.2f} | {res['rtf']:.3f} | {sim:.4f} | {diff_len} | {notes} |")
    
    report_lines.append("")

# Write report
report_path = EVAL_DIR / "evaluation_report.md"
report_path.write_text("\n".join(report_lines), encoding="utf-8")
logger.info(f"Report generated at {report_path}")
print(f"Report generated at {report_path}")
