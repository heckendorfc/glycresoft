import numpy as np

from .base import ScoringFeatureBase, epsilon


def total_intensity(peaks):
    return sum(p.intensity for p in peaks)


class ChromatogramSpacingFitter(ScoringFeatureBase):
    feature_type = "spacing_fit"

    def __init__(self, chromatogram):
        self.chromatogram = chromatogram
        self.rt_deltas = []
        self.intensity_deltas = []
        self.score = None

        if len(chromatogram) < 3:
            self.score = 1.0
        else:
            self.fit()

    def fit(self):
        times, intensities = self.chromatogram.as_arrays()
        last_rt = times[0]
        last_int = intensities[0]

        for rt, inten in zip(times[1:], intensities[1:]):
            d_rt = rt - last_rt
            self.rt_deltas.append(d_rt)
            self.intensity_deltas.append(abs(last_int - inten))
            last_rt = rt
            last_int = inten

        self.rt_deltas = np.array(self.rt_deltas, dtype=np.float16)
        self.intensity_deltas = np.array(self.intensity_deltas, dtype=np.float32) + 1

        self.score = np.average(self.rt_deltas, weights=self.intensity_deltas)

    def __repr__(self):
        return "ChromatogramSpacingFitter(%s, %0.4f)" % (self.chromatogram, self.score)

    @classmethod
    def score(cls, chromatogram, *args, **kwargs):
        return max(1 - cls(chromatogram).score * 2, epsilon)
