import librosa 
import numpy as np
from scipy.stats import linregress
from models import analytics
from constants import MAJOR_SCALES
import db

class Functions:
    @staticmethod
    def intonation(scale, sample):
        scale_notes = MAJOR_SCALES.get(scale)
        y, sr = sample
        
        f, flag, prob = librosa.pyin(
            y,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7")
        )

        note_names = librosa.hz_to_note(f)
        notes = [note_names[:-1] if note != "nan" else "none" for note in note_names]
        onset_frames = librosa.onset.onset_detect(y, sr)
        
        score = 0
        results = []

        for i in range(7):
            note_index = onset_frames[i]
            note = notes[note_index]
            if note != "none" and note == scale_notes[i]:
                score += 1
            else:
                results.append({"played": note, "correct": scale_notes[i]})
        
        results.insert(0,{"score": score})
        return results

    @staticmethod
    def detached_evenness(scale, sample):
        scale_notes = MAJOR_SCALES.get(scale)
        onset_diffs = Functions.get_diffs(scale, sample)
        mean = np.mean(onset_diffs)
        std = np.std(onset_diffs, ddof=1)
        cv = 100 * (std / mean)
        z_scores = (onset_diffs - mean) / std 

        total_evenness = ""

        if cv < 3:
            total_evenness = "very even"
        elif cv < 5:
            total_evenness = "even"
        else:
            total_evenness = "practice more"

        result = {"total_evenness": total_evenness, "uneven_notes": []}

        for i in range(6):
            if abs(z_scores[i]) > 1.5:
                result.get("uneven_notes").append(f"{scale_notes[i]} - {scale_notes[i + 1]}")
        
        return cv # separate z scores into different function
    
    @staticmethod
    def tempo_eveness(sample):
        onset_diffs = Functions.get_diffs(sample) #two octave scale
        mean_bpm = 60 / onset_diffs

        block_bpm = []
        num_of_blocks = len(onset_diffs) // 4
        remainder = onset_diffs[num_of_blocks * 4:].mean()

        for i in range(num_of_blocks):
            block_bpm.append(60 / onset_diffs[i * 4: (1 + i) * 4].mean())

        if remainder:
            block_bpm.append(60 / remainder)
        
        slope, intercept, r, p, se = linregress(range(len(block_bpm)), block_bpm)

        return slope, r, mean_bpm

    @staticmethod
    def get_diffs(sample):
        y, sr = sample
        onset_frames = librosa.onset.onset_detect(y, sr)
        onset_times = librosa.frames_to_time(onset_frames)
        onset_diffs = np.diff(onset_times)

        return onset_diffs
    
    @staticmethod
    def run(filepath, scale):
        y, sr = librosa.load(filepath)
        sample = y, sr

        res_intonation = Functions.intonation(sample, scale)[0].get("score")
        res_tempo_evenness = Functions.tempo_eveness(sample)
        slope, r, mean_bpm = res_tempo_evenness
        res_detached_evenness = Functions.detached_evenness(sample, scale)

        return analytics(intonation=res_intonation, 
                         cv_evenness=res_detached_evenness, 
                         tempo_slope=slope, 
                         tempo_r=r,
                         mean_tempo=mean_bpm)
    
    @staticmethod
    def scale_trends(scale: str):
        records = db.get_scale(scale)
        return Functions.find_trends(records)
    
    @staticmethod
    def all_trends():
        records = db.get_all()
        return Functions.find_trends(records)
        
    @staticmethod
    def find_trends(records):
        if len(records) < 2:
            return {"error": "must have at least 2 records"}
        
        x = np.arange(len(records))
        fields = ["intonation", "cv_evenness", "tempo_slope", "tempo_r", "mean_tempo"]
        trends = {}

        for field in fields:
            y = np.array([getattr(record, field) for record in records])
            model = linregress(x,y)

            trends[field] = {
                "slope": model.slope,
                "r": model.rvalue,
                "p": model.pvalue
            }
        
        return trends
        


        






















