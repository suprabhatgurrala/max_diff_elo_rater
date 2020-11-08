import os

import pandas as pd


ELO_RATINGS_FILE = "elo_ratings.csv"


class MaxDiffRater:

    def __init__(self, elo_ratings=None, k_factor=32):
        if elo_ratings is None:
            if os.path.isfile(ELO_RATINGS_FILE):
                self.load_elo_ratings()
            else:
                self.initialize_items()
        else:
            self.elo_ratings = elo_ratings
        self.k_factor = k_factor
        
    def initialize_items(self):
        self.elo_ratings = pd.read_csv("items.csv", names=["items"])
        self.elo_ratings["elo"] = 1500
        self.elo_ratings["matches"] = 0
        self.store_elo_ratings()

    def store_elo_ratings(self):
        self.elo_ratings.to_csv("elo_ratings.csv", index_label="id")

    def load_elo_ratings(self):
        self.elo_ratings = pd.read_csv("elo_ratings.csv", index_col="id")

    def update_elo(self, winner, loser):
        print(f"Updating elo for {winner} over {loser}")
        if winner == loser:
            return
        
        a = self.elo_ratings.loc[winner]["elo"]
        b = self.elo_ratings.loc[loser]["elo"]
        
        expected = 1 / (1 + 10**((b - a) / 400))
        
        rating_change = self.k_factor * (1 - expected)
        
        self.elo_ratings.at[winner, "elo"] += rating_change
        self.elo_ratings.at[loser, "elo"] -= rating_change
        
        self.elo_ratings.at[winner, "matches"] += 1
        self.elo_ratings.at[loser, "matches"] += 1
    
    def submit_results(self, sample_ids, best, worst):
        best = int(best)
        worst = int(worst)
        for i in sample_ids:
            if i != best:
                self.update_elo(best, i)
            if (i != worst) and (i != best):
                self.update_elo(i, worst)
        
        self.store_elo_ratings()

    def get_sample(self, bucket_size=5):
        i = 1
        least_sample = self.elo_ratings.nsmallest(i, "matches", keep="all")

        while least_sample.shape[0] < bucket_size:
            i += 1
            least_sample = self.elo_ratings.nsmallest(i, "matches", keep="all")
        
        if least_sample.shape[0] > bucket_size:
            least_sample = least_sample.sample(bucket_size)
        
        return least_sample
