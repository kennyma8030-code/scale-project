import librosa 
import numpy as np
from scipy.stats import linregress
from models import analytics
from constants import MAJOR_SCALES
import db

class Functions:
    @staticmethod
    def intonation(scale, sample):
        scale_notes = [note[0] for note in MAJOR_SCALES.get(scale)]
        print(scale_notes)
        y, sr = sample
        
        f, flag, prob = librosa.pyin(
            y,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7")
        )

        onset_frames = librosa.onset.onset_detect(
            y=y, 
            sr=sr,
            delta=0.1,
            wait=20,           
            pre_avg=5,         
            post_avg=5,       
            pre_max=5,          
            post_max=5,                
            backtrack=False)

        notes = []
        
        for frame in onset_frames:
            start = max(0, frame)
            end = min(len(f), frame + 10)  
            
            freqs = f[start:end]
            freqs = freqs[~np.isnan(freqs)]  
            
            if len(freqs) > 0:
                avg_freq = np.median(freqs)
                notes.append(librosa.hz_to_note(avg_freq))
            else:
                notes.append(None)
        notes = [note[0] for note in notes]
       
        print(notes)

        filtered_notes = [notes[0]]
        for note in notes[1:]:
            if note != filtered_notes[-1]:
                filtered_notes.append(note)

        score = 0
        results = []

        for i in range(7):
            note = filtered_notes[i]
            if note is not None and note[0] == scale_notes[i]:
                score += 1
            else:
                results.append({"played": note, "correct": scale_notes[i]})
        
        results.insert(0,{"score": score})
        return results

    @staticmethod
    def detached_evenness(scale, sample):
        scale_notes = MAJOR_SCALES.get(scale)
        onset_diffs = Functions.get_diffs(sample)
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
        mean_bpm = (60 / onset_diffs).mean()

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
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames)
        onset_diffs = np.diff(onset_times)

        return onset_diffs
    
    @staticmethod
    def run(file, scale):
        y, sr = librosa.load(file.file)
        sample = y, sr

        res_intonation = Functions.intonation(scale, sample)
        res_tempo_evenness = Functions.tempo_eveness(sample)
        slope, r, mean_bpm = res_tempo_evenness
        res_detached_evenness = Functions.detached_evenness(scale, sample)

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
        


        






















