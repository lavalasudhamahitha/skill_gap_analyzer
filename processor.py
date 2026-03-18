import sys
import os
import random
import argparse
from sympy import sympify, symbols, lambdify
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine

def process_music(input_path, output_path, formula_str=None, formulas_file=None):
    try:
        print(f"Processing version: 2.0")
        
        # 1. Collect Formulas
        formulas = []
        if formula_str:
            formulas.append(formula_str)
        
        if formulas_file and os.path.exists(formulas_file):
            with open(formulas_file, 'r', encoding='utf-8') as f:
                if formulas_file.endswith('.json'):
                    import json
                    data = json.load(f)
                    if isinstance(data, list):
                        formulas.extend(data)
                    elif isinstance(data, dict) and 'formulas' in data:
                        formulas.extend(data['formulas'])
                else:
                    # Assume text file, one formula per line
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                    formulas.extend(lines)
        
        if not formulas:
            print("No formulas provided. Using default sin(x).")
            formulas.append("sin(x)")

        print(f"Loaded formulas: {formulas}")
        
        # Parse all formulas
        x = symbols('x')
        parsed_funcs = []
        for f_str in formulas:
            try:
                expr = sympify(f_str)
                f = lambdify(x, expr, 'numpy')
                parsed_funcs.append(f)
            except Exception as e:
                print(f"Error parsing formula '{f_str}': {e}")

        if not parsed_funcs:
            print("Fatal Error: No valid formulas could be parsed.", file=sys.stderr)
            sys.exit(1)

        # 2. Try to load original audio
        base_audio = None
        try:
            # Attempt to load the original tune
            original_tune = AudioSegment.from_file(input_path)
            # Limit to first 30 seconds for performance
            if len(original_tune) > 30000:
                original_tune = original_tune[:30000]
            
            base_audio = original_tune.apply_gain(-6) 
            print(f"Successfully loaded original tune: {input_path} ({len(original_tune)}ms)")
        except Exception as pydub_err:
            is_mp3 = input_path.lower().endswith('.mp3')
            msg = f"Skipping original tune load: {pydub_err}"
            if is_mp3:
                msg += " (Notice: Loading MP3 requires 'ffmpeg' installed on the server. Try using a .wav file instead.)"
            print(msg)
            base_audio = AudioSegment.silent(duration=5000, frame_rate=44100)

        # 3. Generate Formula Melody
        duration_ms = len(base_audio)
        melody = AudioSegment.silent(duration=duration_ms, frame_rate=44100)
        
        print(f"Generating formula melody for {duration_ms}ms with {len(parsed_funcs)} formulas...")
        # Spread formulas across the duration
        num_steps = max(1, duration_ms // 500)
        
        for i in range(num_steps):
            # Select formula based on step (or cycling through them)
            f_idx = i % len(parsed_funcs)
            f = parsed_funcs[f_idx]
            
            try:
                raw_val = f(i)
                if isinstance(raw_val, np.ndarray):
                    val = float(raw_val.item()) if raw_val.size == 1 else float(raw_val[0])
                else:
                    val = float(raw_val)

                if not np.isfinite(val):
                    continue

                # Map to a reasonable frequency range (200Hz to 1200Hz)
                freq = 200 + (abs(val) % 1000) 
                
                tone = Sine(freq).to_audio_segment(duration=400).fade_in(50).fade_out(50)
                melody = melody.overlay(tone.apply_gain(-3), position=i*500)
            except Exception:
                continue
                
        # 4. Mix them together
        final_audio = base_audio.overlay(melody)
        
        print(f"Exporting to {output_path}...")
        final_audio.export(output_path, format="wav")
        print(f"Done! Exported {len(final_audio)}ms to {output_path}")
                
    except Exception as e:
        print(f"Fatal Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process music with formulas.")
    parser.add_argument("input", help="Path to input audio file")
    parser.add_argument("output", help="Path to output wav file")
    parser.add_argument("--formula", help="A single mathematical formula string")
    parser.add_argument("--file", help="Path to a file containing formulas")
    
    args = parser.parse_args()
    
    process_music(args.input, args.output, args.formula, args.file)
